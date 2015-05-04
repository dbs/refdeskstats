#!/usr/bin/env python

"""Collect daily reference desk statistics in a database

Display the stats in a useful way with charts and download links"""

from flask import Flask, abort, request, render_template, make_response
from os.path import abspath, dirname
from config import config
import datetime
import psycopg2
import StringIO
import csv

verbose = False

app = Flask(__name__)
app.root_path = abspath(dirname(__file__))

# Table definition
# CREATE TABLE refstats (
#     refdate DATE,
#     refstat TEXT,
#     refcount INTEGER,
#     create_time TIMESTAMP DEFAULT NOW()
# );
# ALTER TABLE refstats ADD PRIMARY KEY (refdate, refstat);

# Table permissions
# GRANT SELECT, INSERT, UPDATE, DELETE ON refstats TO refstats;

# View definition (most recent timestamps)
# CREATE VIEW refview AS WITH x AS (
#    SELECT refstat, refdate, MAX(create_time)
#    AS create_time FROM refstats
#    GROUP BY refstat, refdate)
#    SELECT x.refstat, x.refdate, x.create_time, r.refcount
#    FROM refstats r INNER JOIN x ON (
#       x.create_time = r.create_time AND
#       x.refstat = r.refstat AND
#       x.refdate = r.refdate)
#    ORDER BY refstat;

# View definition (add the day of week to refview)
# CREATE VIEW refview_day_of_week AS
#    SELECT refstat, refdate, EXTRACT(DOW FROM refdate)
#    AS day_of_week, create_time, refcount
#    FROM refview;

def get_db():
    """
    Get a database connection

    With a host attribute in the mix, you could connect to a remote
    database, but then you would have to set up .pgpass or add a
    password parameter, so let's keep it simple.
    """
    try:
        return psycopg2.connect(
            database=config['DB_NAME'],
            user=config['DB_USER']
        )
    except Exception, e:
        print(e)

@app.route(config['URL_BASE'], methods=['GET', 'POST'])
def submit(date=None):
    "Either show the form, or process the form"
    if request.method == 'POST':
        return eat_stat_form()
    else:
        #return show_stat_form()
        if verbose: print('Before queueing data edit.')
        return edit_data(date)

@app.errorhandler(404)
def page_not_found(err):
    "Give a simple 404 error page."
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_broken(err):
    """
    Let people know something went wrong

    This could be a duplicate entry for the same day, or a lost database
    connection, or pretty much anything. Leave it up to the brainiac
    devops person to suss it out.
    """
    return render_template('500.html'), 500

def eat_stat_form():
    "Shove the form data into the database"
    try:
        dbh = get_db()
        cur = dbh.cursor()
        form = request.form
        fdate = form.getlist('refdate')[0]
        for key in form.keys():
            if key == 'refdate':
                continue
            for val in form.getlist(key):
                cur.execute("""INSERT INTO refstats (refdate, refstat, refcount) 
                            VALUES (%s, %s, %s)""", (fdate, key, val))
        dbh.commit()
        dbh.close()
        message = "Your form was successfully submitted."
        return render_template('menu_interface.html', message=message)
    except:
        return abort(500)

#def show_stat_form():
    #"Show the pretty form for the user"
    #return render_template('stat_form.html', today=((datetime.datetime.now() + datetime.timedelta(hours=-2)).date().isoformat()))

def get_stats(date):
    "Get the stats from the database"
    try:
        dbase = get_db()
        cur = dbase.cursor()
        monthdate = str(date) + '%'
        cur.execute(""" 
            SELECT DISTINCT refdate
            FROM refview
            WHERE refdate::text LIKE %s
            ORDER BY refdate desc""",
        (str(monthdate),))
        #cur.execute('SELECT DISTINCT refdate FROM refview ORDER BY refdate desc')
        dates = [dict(refdate=row[0]) for row in cur.fetchall()]
        if dbase.closed:
            return "I was closed!"
        dbase.commit()
        dbase.close()
        return dates
    except Exception, e:
        print(e)

def get_months():
    "Get the months that have data"
    try:
        dbase = get_db()
        cur = dbase.cursor()
        cur.execute("""SELECT DISTINCT date_part('year',refdate)|| 
                    '-' ||date_part('month',refdate) AS date_piece,
                    (date_part('year',refdate)|| '-' ||date_part('month',refdate)||
                    '-01')::date AS date 
                    FROM refview GROUP BY date_piece
                    ORDER BY date desc""")
        months = []
        for row in cur.fetchall():
            year, month = parse_date(row[1])
            months.append({'month': year + '-' + month})
        #months = [dict(month=row[0]) for row in cur.fetchall()]
        dbase.commit()
        dbase.close()
        # print(months)
        return months
    except Exception, e:
        print(e)

def get_csv(filename):
    "Get the data in CSV format"
    try:
        data = get_db()
        cur = data.cursor()
        #print(cur.mogrify("SELECT refdate, refstat, refcount FROM refstats WHERE refdate = %s", (str(filename),)))
        if str(filename) == 'allstats.csv':
            cur.execute("SELECT refdate, refstat, refcount FROM refview")
        else:
            cur.execute("""SELECT refdate, refstat, refcount
                        FROM refview WHERE refdate=%s""",
                        (str(filename),))
        csvgen = StringIO.StringIO()
        csvfile = csv.writer(csvgen)
        for row in cur.fetchall():
            csvfile.writerow([row[0], row[1], row[2]])
        csv_result = csvgen.getvalue()
        csvgen.close()
        data.commit()
        data.close()
        return csv_result
    except Exception, e:
        print(e)

def get_dataArray(date):
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("""SELECT refdate, refstat, refcount
                    FROM refview WHERE refdate=%s""",
                    (str(date),))
        stack = config['stack'];

        directional = config['directional']
        coll_serv = config['collect/serv']
        referral = config['referral']
        equip = config['equip']
        prin_soft = config['print/software']

        for row in cur.fetchall():
            timeslot, stat = parse_stat(row[1])
            if stat == 'dir':
                directional[config['timecodes'][timeslot]] = row[2]
            elif stat == 'equipment':
                equip[config['timecodes'][timeslot]] = row[2]
            elif stat == 'help':
                coll_serv[config['timecodes'][timeslot]] = row[2]
            elif stat == 'ithelp':
                prin_soft[config['timecodes'][timeslot]] = row[2]
            elif stat == 'referral':
                referral[config['timecodes'][timeslot]] = row[2]

        data.commit()
        data.close()
        for stat_type in [directional, coll_serv, referral, equip, prin_soft]:
            stack.append(stat_type)

        return stack
    except Exception, e:
        print(e)

def get_timeArray(date):
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        #cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate=%s", (str(date),))
        """If we want everyday in the month"""
        if len(str(date)) == 7:
            date_year, date_month = parse_date(str(date))
            cur.execute("""SELECT refstat, sum(refcount)
                        FROM refview
                        WHERE date_part('year',refdate) = %s
                        AND date_part('month',refdate) = %s
                        GROUP BY refstat""",
                        (str(date_year), str(date_month)))
        else:
            cur.execute("""SELECT refstat, refcount, refdate
                        FROM refview WHERE refdate=%s""",
                        (str(date),))

        stack = config['stack']
        times = config['times']

        for row in cur.fetchall():
            timeslot, stat = parse_stat(row[0])
            #print(timeslot, stat, row[1])
            #print(helpcodes[stat])
            if timeslot in config['timecodes']:
                times[config['timecodes'][timeslot]][config['helpcodes'][stat]] = row[1]
            
        data.commit()
        data.close()
        for time in times:
            stack.append(time)
            #print(time)
        #print(stack)
        return stack
    except Exception, e:
        print(e)

def get_weekdayArray(date):
    """Put the data into an array for google charts"""
    try:
        data = get_db()
        cur = data.cursor()
        month = str(date) + '%'
        cur.execute("""
            SELECT refstat, refcount, day_of_week
            FROM refview_day_of_week
            WHERE refdate::text LIKE %s
            ORDER BY day_of_week""", (str(month),))

        stack = config['stack']
        days = config['days']

        for row in cur.fetchall():
            """Get the data for each day of the month and do something useful with it"""
            timeslot, stat = parse_stat(row[0])
            if row[2] >= 0 and row[2] <= 6:
                days[row[2]][config['helpcodes'][stat]] += row[1]

        data.commit()
        data.close()

        for day in days:
            stack.append(day)

        #print(stack)
        return stack


    except Exception, e:
        print(e)

def parse_date(date):
    "Returns the year and the month separately from the date"

    date_parts = str(date).split('-')
    return date_parts[0], date_parts[1]

def parse_stat(stat):
    "Returns the type of stat and the time slot"

    for s in ['dir', 'equipment', 'ithelp', 'referral', 'help']:
        pos = stat.find(s)
        if pos > -1:
            return stat[0:pos], s

def get_missing(date):
    "Find the dates that are missing stats"
    try:
        data = get_db()
        cur = data.cursor()
        month = str(date) + '%'
        day = str(date) + '-01'
        cur.execute("""
            With x AS (SELECT DISTINCT refdate from refview
                        WHERE refdate::text LIKE %s),
                 y AS (SELECT generate_series(date %s,
                       date %s + '1 month'::interval - '1 day'::interval,
                       '1 day'::interval) AS missingdate)
            SELECT missingdate::date from y
            WHERE missingdate NOT IN(
            SELECT refdate from x)
        """, (str(month), str(day), str(day)))

        missing = []
        for row in cur.fetchall():
            missing.append({'refdate': row[0]})

        data.commit()
        data.close()

        return missing
    except Exception, e:
        print(e)

def get_current_data(date):
    "Pull out the current data for a given day"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("""SELECT refstat, refcount
                    FROM refview
                    WHERE refdate=%s""",
        (str(date),))

        stats = {}
        for row in cur.fetchall():
            stats[row[0]] = row[1]

        data.commit()
        data.close()
        #print(stats)
        return stats

    except Exception, e:
        print(e)

@app.route(config['URL_BASE'] + 'view/', methods=['GET'])
@app.route(config['URL_BASE'] + 'view/<date>', methods=['GET'])
def show_stats(date=None):
    "Lets try to get all dates with data input"
    try:
        dates = get_stats(date)
        months = get_months()
        if date:
            tarray = get_timeArray(date)
            if len(str(date)) == 7:
                wdarray = get_weekdayArray(date)
                missing = get_missing(date)
                return render_template('show_mchart.html', dates=dates, \
                    tarray=tarray, date=date, wdarray=wdarray, months=months, \
                    missing=missing \
                )
            else:
                array = get_dataArray(date)
                return render_template('show_chart.html', dates=dates, \
                    array=array, tarray=tarray, date=date, months=months \
                )
        else:
            return render_template('show_stats.html', dates=dates, months=months)
    except:
        return abort(500)

@app.route(config['URL_BASE'] + 'edit/<date>', methods=['GET','POST'])
#def submit(date=None):
    #"Either show the form, or process the form"
    #if request.method == 'POST':
        #return eat_stat_form()
    #else:
        #return edit_data(date)

def edit_data(date):
    "Add data to missing days or edit current data"
    if request.method == 'POST':
        return eat_stat_form()
    try:
        if date:
            stats = get_current_data(date)
            #print(date + 'stats:' + stats)
            #if stats:
            if verbose: print ('before page render')
            return render_template('stat_form.html', today=date, stats=stats)
            #else:
                #return render_template('stat_form.html', today=date)
                #return render_template('edit_stat_form.html', today=date, stats=stats)
        else:
            if verbose: print ('before page render')
            return render_template('stat_form.html', today=((datetime.datetime.now() + datetime.timedelta(hours=-2)).date().isoformat()), stats={})
    except:
        return abort(500)

@app.route(config['URL_BASE'] + 'download/')
@app.route(config['URL_BASE'] + 'download/<filename>')
def download_file(filename=None):
    "Downloads a file in CSV format"
    try:
        if filename:
            filename = str(filename)
            csv_data = get_csv(filename)
            csv_file = filename + ".csv"
        else:
            csv_data = get_csv('alldata')
            csv_file = filename
        response = make_response(csv_data)
        response_header = "attachment; fname=" + csv_file
        response.headers["Content-Type"] = 'text/csv'
        response.headers["Content-Disposition"] = response_header
        return response
    except:
        return abort(500)

if __name__ == '__main__':
    app.run(debug=True, host=config['HOST'], port=config['PORT'])
