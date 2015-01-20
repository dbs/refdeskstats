"""Collect daily reference desk statistics in a database

Display the stats in a useful way with charts and download links"""

from flask import Flask, abort, request, render_template, Response, make_response
from os.path import abspath, dirname
import datetime
import psycopg2
import StringIO
import csv

#URL_BASE = '/refdesk-stats/'
URL_BASE = '/'

# Database connection info
DB_NAME = 'refstats'
#DB_HOST = 'localhost'
DB_USER = 'refstats'

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
            database=DB_NAME,
            user=DB_USER
        )
    except Exception, e:
        print(e)

@app.route(URL_BASE, methods=['GET', 'POST'])
def submit():
    "Either show the form, or process the form"
    if request.method == 'POST':
        return eat_stat_form()
    else:
        return show_stat_form()

@app.errorhandler(500)
def page_not_found(err):
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
                cur.execute('INSERT INTO refstats (refdate, refstat, refcount) VALUES (%s, %s, %s)', (fdate, key, val))
        dbh.commit()
        dbh.close()
        message = "Your form was successfully submitted."
        return render_template('menu_interface.html', message=message)
    except:
        return abort(500)

def show_stat_form():
    "Show the pretty form for the user"
    return render_template('stat_form.html', today=((datetime.datetime.now() + datetime.timedelta(hours=-2)).date().isoformat()))

def get_stats():
    "Get the stats from the database"
    try:
        dbase = get_db()
        cur = dbase.cursor()
        cur.execute('SELECT DISTINCT refdate FROM refview ORDER BY refdate desc')
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
        cur.execute("SELECT DISTINCT date_part('year',refdate)|| '-' ||date_part('month',refdate) AS date_piece, (date_part('year',refdate)|| '-' ||date_part('month',refdate)|| '-01')::date AS date FROM refview GROUP BY date_piece ORDER BY date asc")
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
        if str(filename) == 'alldata':
            cur.execute("SELECT refdate, refstat, refcount FROM refview")
        else:
            cur.execute("SELECT refdate, refstat, refcount FROM refview WHERE refdate=%s", (str(filename),))
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
        cur.execute("SELECT refdate, refstat, refcount FROM refview WHERE refdate=%s", (str(date),))
        timecodes = {
            "8to10": 1,
            "10to11": 2,
            "11to12": 3,
            "12to1": 4,
            "1to2": 5,
            "2to3": 6,
            "3to4": 7,
            "4to5": 8,
            "5to6": 9,
            "6to7": 10,
            "7toclose": 11
        }
        stack = [['Timeslot', '8-10AM', '10-11AM', '11AM-12PM', '12-1PM', '1-2PM', '2-3PM', '3-4PM', '4-5PM', '5-6PM', '6-7PM', '7PM-Close', {'role': 'annotation'}]]

        directional = ["Directional", None, None, None, None, None, None, None, None, None, None, None, '']
        coll_serv = ["Help with Collections/Services", None, None, None, None, None, None, None, None, None, None, None, '']
        referral = ["Referral to Librarian", None, None, None, None, None, None, None, None, None, None, None, '']
        equip = ["Equipment", None, None, None, None, None, None, None, None, None, None, None, '']
        prin_soft = ["Help with Printers/Software", None, None, None, None, None, None, None, None, None, None, None, '']

        for row in cur.fetchall():
            timeslot, stat = parse_stat(row[1])
            #print stat, timeslot
            if stat == 'dir':
                directional[timecodes[timeslot]] = row[2]
            elif stat == 'equipment':
                equip[timecodes[timeslot]] = row[2]
            elif stat == 'help':
                coll_serv[timecodes[timeslot]] = row[2]
            elif stat == 'ithelp':
                prin_soft[timecodes[timeslot]] = row[2]
            elif stat == 'referral':
                referral[timecodes[timeslot]] = row[2]

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
        "If we want everyday in the month"
        if len(str(date)) == 7:
            date_year, date_month = parse_date(str(date))
            cur.execute("SELECT refstat, sum(refcount) FROM refview WHERE date_part('year',refdate) = %s AND date_part('month',refdate) = %s GROUP BY refstat", (str(date_year), str(date_month)))
        else:
            cur.execute("SELECT refstat, refcount, refdate FROM refview WHERE refdate=%s", (str(date),))

        helpcodes = {
            "dir": 1,
            "equipment": 2,
            "help": 3,
            "ithelp": 4,
            "referral": 5
        }
        stack = [['Refstat', 'Directional', 'Equipment', 'Help with Collections/Services', 'Help with Printers/Software', 'Referral to Librarian', {'role': 'annotation'}]]
        time1 = ["8-10AM", None, None, None, None, None, '']
        time2 = ["10-11AM", None, None, None, None, None, '']
        time3 = ["11AM-12PM", None, None, None, None, None, '']
        time4 = ["12-1PM", None, None, None, None, None, '']
        time5 = ["1-2PM", None, None, None, None, None, '']
        time6 = ["2-3PM", None, None, None, None, None, '']
        time7 = ["3-4PM", None, None, None, None, None, '']
        time8 = ["4-5PM", None, None, None, None, None, '']
        time9 = ["5-6PM", None, None, None, None, None, '']
        time10 = ["6-7PM", None, None, None, None, None, '']
        time11 = ["7-Close", None, None, None, None, None, '']

        for row in cur.fetchall():
            timeslot, stat = parse_stat(row[0])
            #print(timeslot, stat, row[1])
            #print(helpcodes[stat])
            if timeslot == '8to10':
                time1[helpcodes[stat]] = row[1]
            elif timeslot == '10to11':
                time2[helpcodes[stat]] = row[1]
                #print(time2)
            elif timeslot == '11to12':
                time3[helpcodes[stat]] = row[1]
            elif timeslot == '12to1':
                time4[helpcodes[stat]] = row[1]
            elif timeslot == '1to2':
                time5[helpcodes[stat]] = row[1]
            elif timeslot == '2to3':
                time6[helpcodes[stat]] = row[1]
            elif timeslot == '3to4':
                time7[helpcodes[stat]] = row[1]
            elif timeslot == '4to5':
                time8[helpcodes[stat]] = row[1]
            elif timeslot == '5to6':
                time9[helpcodes[stat]] = row[1]
            elif timeslot == '6to7':
                time10[helpcodes[stat]] = row[1]
            elif timeslot == '7toclose':
                time11[helpcodes[stat]] = row[1]

        data.commit()
        data.close()
        for time in [time1, time2, time3, time4, time5, time6, time7, time8, time9, time10, time11]:
            stack.append(time)
            #print(time)
        #print(stack)
        return stack
    except Exception, e:
        print(e)

def get_weekdayArray(date):
    "Put the data into an array for google charts"
    try:
        data = get_db()
        cur = data.cursor()
        month = str(date) + '%'
        cur.execute("""
            SELECT refstat, refcount, day_of_week
            FROM refview_day_of_week
            WHERE refdate::text LIKE %s
            ORDER BY day_of_week""", (str(month),))

        helpcodes = {
            "dir": 1,
            "equipment": 2,
            "help": 3,
            "ithelp": 4,
            "referral": 5
        }

        stack = [['Days_of_Week', 'Directional', 'Equipment', 'Help with Collections/Services', 'Help with Printers/Software', 'Referral to Librarian', {'role': 'annotation'}]]
        days = [
            ["Sunday", 0, 0, 0, 0, 0, ''],
            ["Monday", 0, 0, 0, 0, 0, ''],
            ["Tuesday", 0, 0, 0, 0, 0, ''],
            ["Wednesday", 0, 0, 0, 0, 0, ''],
            ["Thursday", 0, 0, 0, 0, 0, ''],
            ["Friday", 0, 0, 0, 0, 0, ''],
            ["Saturday", 0, 0, 0, 0, 0, '']
        ]

        for row in cur.fetchall():
            "Get the data for each day of the month and do something useful with it"
            timeslot, stat = parse_stat(row[0])
            if row[2] == 0:
                days[0][helpcodes[stat]] += row[1]
            elif row[2] == 1:
                days[1][helpcodes[stat]] += row[1]
            elif row[2] == 2:
                days[2][helpcodes[stat]] += row[1]
            elif row[2] == 3:
                days[3][helpcodes[stat]] += row[1]
            elif row[2] == 4:
                days[4][helpcodes[stat]] += row[1]
            elif row[2] == 5:
                days[5][helpcodes[stat]] += row[1]
            elif row[2] == 6:
                days[6][helpcodes[stat]] += row[1]

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
                 y AS (SELECT missingdate AS generate_series(date %s,
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
        date.close()

        return missing
    except Exception, e:
        print(e)

@app.route(URL_BASE + 'view/', methods=['GET'])
@app.route(URL_BASE + 'view/<date>', methods=['GET'])
def show_stats(date=None):
    "Lets try to get all dates with data input"
    try:
        dates = get_stats()
        months = get_months()
        if date:
            tarray = get_timeArray(date)
            if len(str(date)) == 7:
                wdarray = get_weekdayArray(date)
                missing = get_missing(date)
                return render_template('show_mchart.html', dates=dates, \
                    tarray=tarray, date=date, wdarray=wdarray, months=months \
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

@app.route(URL_BASE + 'download/')
@app.route(URL_BASE + 'download/<filename>')
def download_file(filename=None):
    "Downloads a file in CSV format"
    try:
        if filename:
            filename = str(filename)
            csv_data = get_csv(filename)
            csv_file = filename + ".csv"
        else:
            csv_data = get_csv('alldata')
            csv_file = "alldata.csv"
        response = make_response(csv_data)
        response_header = "attachment; fname=" + csv_file
        response.headers["Content-Type"] = 'text/csv'
        response.headers["Content-Disposition"] = response_header
        return response
    except:
        return abort(500)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5555)
