#!/usr/bin/env python

"""Collect daily reference desk statistics in a database

Display the stats in a useful way with charts and download links"""

from flask import Flask, abort, request, render_template, make_response, g
from flask_babelex import Babel
from os.path import abspath, dirname
from config import config
import sys
import datetime
import psycopg2
import StringIO
import copy
import csv

VERBOSE = True

app = Flask(__name__)
app.root_path = abspath(dirname(__file__))
babel = Babel(app)

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
    except Exception, ex:
        print(ex)

@babel.localeselector
def get_locale():
    return g.current_lang

@app.before_request
def before():
    if request.view_args and 'lang' in request.view_args:
        g.current_lang = request.view_args['lang']
        request.view_args.pop('lang')


@app.route(config['URL_BASE'], methods=['GET', 'POST'])
@app.route(config['URL_BASE'], methods=['GET', 'POST'])
def submit(date=None):
    "Either show the form, or process the form"
    if request.method == 'POST':
        return eat_stat_form()
    else:
        #return show_stat_form()
        if VERBOSE:
            print('Before queueing data edit.')
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
        fdate = form['refdate']
        if VERBOSE:
            print('reached data insertion...')
        for time in config['timelist']:
            for stat in config['helplist']:
                if VERBOSE:
                    print(time, stat)
                val_en = form[time+stat+'_en']
                val_fr = form[time+stat+'_fr']
                cur.execute("""INSERT INTO refdeskstats (refdate, reftime, reftype, refcount_en, refcount_fr) 
                    VALUES (%s, %s, %s, %s, %s)""", (fdate, time, stat, val_en, val_fr))
        dbh.commit()
        dbh.close()
        message = "Your form was successfully submitted."
        return render_template('menu_interface.html', message=message)
    except Exception, ex:
        print(ex)
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
            FROM refstatview
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
    except Exception, ex:
        print(ex)

def get_months():
    "Get the months that have data"
    try:
        dbase = get_db()
        cur = dbase.cursor()
        cur.execute("""SELECT DISTINCT date_part('year',refdate)|| 
                    '-' ||date_part('month',refdate) AS date_piece,
                    (date_part('year',refdate)|| '-' ||date_part('month',refdate)||
                    '-01')::date AS date 
                    FROM refstatview GROUP BY date_piece
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
    except Exception, ex:
        print(ex)

def get_csv(filename):
    "Get the data in CSV format"
    try:
        data = get_db()
        cur = data.cursor()
        #print(cur.mogrify("SELECT refdate, refstat, refcount FROM refstats WHERE refdate = %s", (str(filename),)))
        if str(filename) == 'allstats.csv':
            cur.execute("SELECT refdate, reftime, reftype, refcount_en, refcount_fr FROM refstatview")
        else:
            cur.execute("""SELECT refdate, reftime, reftype, refcount_en, refcount_fr
                        FROM refstatview WHERE refdate=%s""",
                        (str(filename),))
        csvgen = StringIO.StringIO()
        csvfile = csv.writer(csvgen)
        for row in cur.fetchall():
            csvfile.writerow([row[0], row[1], row[2], row[3], row[4]])
        csv_result = csvgen.getvalue()
        csvgen.close()
        data.commit()
        data.close()
        return csv_result
    except Exception, ex:
        print(ex)

def get_data_array(date):
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("""SELECT refdate, reftime, reftype, refcount_en,
                       refcount_fr FROM refstatview WHERE refdate=%s""",
                       (str(date),))
        stack = copy.deepcopy(config['stack_a'])
        array = copy.deepcopy(config['array'])

        for row in cur.fetchall():
            timeslot = str(row[1])
            stat = row[2]
            array[config['helpcodes'][stat+'_en']-1][config['timecodes'][timeslot]] = row[3]
            array[config['helpcodes'][stat+'_fr']-1][config['timecodes'][timeslot]] = row[4]

        data.commit()
        data.close()

        for stat_data in array:
            stack.append(stat_data)

        return stack
    except Exception, ex:
        print(ex)

def get_time_array(date):
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        #cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate=%s", (str(date),))
        #"""If we want everyday in the month"""
        if len(str(date)) == 7:
            date_year, date_month = parse_date(str(date))
            if VERBOSE:
                print('viewing:'+ str((date_year,  date_month)))
            cur.execute("""SELECT reftime, reftype,
                        sum(refcount_en), sum(refcount_fr)
                        FROM refstatview
                        WHERE date_part('year',refdate) = %s
                        AND date_part('month',refdate) = %s
                        GROUP BY reftime, reftype""",
                        (str(date_year), str(date_month)))
        else:
            cur.execute("""SELECT reftime, reftype, refcount_en, refcount_fr, refdate
                        FROM refstatview WHERE refdate=%s""",
                        (str(date),))

        stack = copy.deepcopy(config['stack_b'])
        times = copy.deepcopy(config['times'])

        print(times)

        for row in cur.fetchall():
            timeslot = str(row[0])
            stat = row[1]
            #print(helpcodes[stat])
            #if timeslot in config['timelist']:
            times[config['timecodes'][timeslot]-1][config['helpcodes'][stat+'_en']] = row[2]
            times[config['timecodes'][timeslot]-1][config['helpcodes'][stat+'_fr']] = row[3]

        
        print(times)
            
        data.commit()
        data.close()
        for time in times:
            stack.append(time)
            #print(time)
        #print(stack)
        return stack
    except Exception, ex:
        print(ex)

def get_weekday_array(date):
    """Put the data into an array for google charts"""
    try:
        data = get_db()
        cur = data.cursor()
        month = str(date) + '%'
        cur.execute("""
            SELECT reftime, reftype, refcount_en, refcount_fr, day_of_week
            FROM refstatview_day_of_week
            WHERE refdate::text LIKE %s
            ORDER BY day_of_week""", (str(month),))

        stack = copy.deepcopy(config['stack_b'])
        days = copy.deepcopy(config['days'])

        for row in cur.fetchall():
            """Get the data for each day of the month and do something useful with it"""
            timeslot = row[0]
            stat = row[1]
            if row[4] >= 0 and row[4] <= 6:
                days[int(row[4])][config['helpcodes'][stat+'_en']] += row[2]
                days[int(row[4])][config['helpcodes'][stat+'_fr']] += row[3]

        data.commit()
        data.close()

        for day in days:
            stack.append(day)
        #print(stack)
        return stack

    except Exception, ex:
        print(ex)

def parse_date(date):
    "Returns the year and the month separately from the date"

    date_parts = str(date).split('-')
    return date_parts[0], date_parts[1]

def parse_stat(stat):
    "Returns the type of stat and the time slot"

    for s in config['helplist']:
        if VERBOSE: 
            print(stat)
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
            With x AS (SELECT DISTINCT refdate from refstatview
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
    except Exception, ex:
        print(ex)

def get_current_data(date):
    "Pull out the current data for a given day"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("""SELECT reftime, reftype,
                    refcount_en, refcount_fr
                    FROM refstatview WHERE refdate=%s""", 
                    (str(date),))

        stats = {}
        for row in cur.fetchall():
            time = str(row[0])
            stat = row[1]
            stats[time+stat+'_en'] = row[2]
            stats[time+stat+'_fr'] = row[3]

        data.commit()
        data.close()
        #print(stats)
        return stats

    except Exception, ex:
        print(ex)

@app.route(config['URL_BASE'] + 'view/', methods=['GET'])
@app.route(config['URL_BASE'] + 'view/<date>', methods=['GET'])
def show_stats(date=None):
    "Lets try to get all dates with data input"
    try:
        dates = get_stats(date)
        months = get_months()
        if date:
            tarray = get_time_array(date)
            #If the date specified is a full month. len(YYYY-MM) == 7.
            if len(str(date)) == 7:
                wdarray = get_weekday_array(date)
                missing = get_missing(date)
                return render_template('show_mchart.html', dates=dates, \
                    tarray=tarray, date=date, wdarray=wdarray, months=months, \
                    missing=missing \
                )
            else:
                array = get_data_array(date)
                return render_template('show_chart.html', dates=dates, \
                    array=array, tarray=tarray, date=date, months=months \
                )
        else:
            return render_template('show_stats.html', dates=dates, months=months)
    except:
        return abort(500)

#def submit(date=None):
    #"Either show the form, or process the form"
    #if request.method == 'POST':
        #return eat_stat_form()
    #else:
        #return edit_data(date)

@app.route(config['URL_BASE'], methods=['GET','POST'])
@app.route(config['URL_BASE'] + 'edit/<date>', methods=['GET','POST'])
def edit_data(date):
    "Add data to missing days or edit current data"
    if request.method == 'POST':
        return eat_stat_form()
    try:
        if date:
            stats = get_current_data(date)
            #if VERBOSE:
            #    print(date + 'stats:' + stats)
            #if stats:
            if VERBOSE:
                print ('before page render: stats found')
            return render_template('stat_form.html', today=date, stats=stats)
            #else:
                #return render_template('stat_form.html', today=date)
                #return render_template('edit_stat_form.html', today=date, stats=stats)
        else:
            if VERBOSE:
                print ('before page render: no stats')
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            print(date)
            stats = get_current_data(date)
            return render_template('stat_form.html', today=((datetime.datetime.now() + datetime.timedelta(hours=-2)).date().isoformat()), stats=stats)
    except Exception, ex:
        print(ex)
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
    except Exception, ex:
        print(ex)
        return abort(500)

if __name__ == '__main__':
    app.run(debug=True, host=config['HOST'], port=config['PORT'])
