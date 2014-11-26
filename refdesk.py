"Collect daily reference desk statistics in a database"
"Display the stats in a useful way with charts and download links"

from flask import Flask, abort, request, render_template, Response, make_response
from os.path import abspath, dirname
import datetime
import psycopg2
import sqlite3
import StringIO
import csv
import json

URL_BASE = '/refdesk-stats'

# Database connection info
DB_NAME = 'refstats'
#DB_HOST = 'localhost'
#DB_USER = 'refstats'

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

def get_db():
    """
    Get a database connection

    With a host attribute in the mix, you could connect to a remote
    database, but then you would have to set up .pgpass or add a
    password parameter, so let's keep it simple.
    """
    try:
        return psycopg2.connect(
            database=DB_NAME
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
        cur.execute('SELECT DISTINCT refdate FROM refstats ORDER BY refdate desc')
        dates = [dict(refdate=row[0]) for row in cur.fetchall()]
        if dbase.closed:
            return "I was closed!"
        dbase.commit()
        dbase.close()
        return dates
    except Exception, e:
        print(e)

def get_csv(filename):
    "Get the data in CSV format"
    try:
        data = get_db()
        cur = data.cursor()
	    #print(cur.mogrify("SELECT refdate, refstat, refcount FROM refstats WHERE refdate = %s", (str(filename),)))
        if str(filename) == 'alldata':
	        cur.execute("SELECT refdate, refstat, refcount FROM refstats")
        else:
	        cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate=%s", (str(filename),))
        csvgen = StringIO.StringIO()
        csvfile = csv.writer(csvgen)
        for row in cur.fetchall():
            csvfile.writerow([row[0], row[1], row[2]]) 
        csv_result = csvgen.getvalue()
	    # This will make JSON available is uncommented
	    #json_results = json.dumps(csvgen)
        csvgen.close()
        data.commit()
        data.close()
        return csv_result
    except Exception, e:
        print(e)

def get_dataArray(filename):
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate=%s", (str(filename),))
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
        stack = [['Timeslot', '8-10AM', '10-11AM', '11AM-12PM', '12-1PM', '1-2PM', '2-3PM', '3-4PM', '4-5PM', '5-6PM', '6-7PM', '7PM-Close', { 'role': 'annotation' } ]]

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

def get_timeArray(filename): 
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate=%s", (str(filename),))
        helpcodes = {
            "dir": 1,
            "equipment": 2,
            "help": 3,
            "ithelp": 4,
            "referral": 5
        }
        stack = [['Refstat', 'Directional','Equipment','Help with Collections/Services','Help with Printers/Software','Referral to Librarian',{ 'role': 'annotation' } ]]
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
            timeslot, stat = parse_stat(row[1])
            if timeslot == '8to10':
                time1[helpcodes[stat]] = row[2]
            elif timeslot == '10to11':
                time2[helpcodes[stat]] = row[2]
            elif timeslot == '11to12':
                time3[helpcodes[stat]] = row[2]
            elif timeslot == '12to1':
                time4[helpcodes[stat]] = row[2]
            elif timeslot == '1to2':
                time5[helpcodes[stat]] = row[2]
            elif timeslot == '2to3':
                time6[helpcodes[stat]] = row[2]
            elif timeslot == '3to4':
                time7[helpcodes[stat]] = row[2]
            elif timeslot == '4to5':
                time8[helpcodes[stat]] = row[2]
            elif timeslot == '5to6':
                time9[helpcodes[stat]] = row[2]
            elif timeslot == '6to7':
                time10[helpcodes[stat]] = row[2]
            elif timeslot == '7toclose':
                time11[helpcodes[stat]] = row[2]
        
        data.commit()
        data.close()
        for time in [time1, time2, time3, time4, time5, time6, time7, time8, time9, time10, time11]:
            stack.append(time)

        return stack
    except Exception, e:
        print(e)

def parse_stat(stat):
    "Returns the type of stat and the time slot"
    
    for s in ['dir', 'equipment', 'ithelp', 'referral', 'help']:
        pos = stat.find(s) 
        if pos > -1:
            return stat[0:pos], s

def get_missing():
    "Find the dates that are missing stats"
    try:
        print("Hello")
    except Exception, e:
	    print(e)

@app.route(URL_BASE + '/view/', methods=['GET'])
@app.route(URL_BASE + '/view/<date>', methods=['GET'])
def show_stats(date=None):
    "Lets try to get all dates with data input"
    try:
        if date:
            array = get_dataArray(date)
            tarray = get_timeArray(date)
            dates = get_stats()
            return render_template('show_chart.html', dates=dates, array=array, tarray=tarray,date=date)
        else:
            dates = get_stats()
            return render_template('show_stats.html', dates=dates)
    except:
        return abort(500)
@app.route(URL_BASE + '/download/')
@app.route(URL_BASE + '/download/<filename>')
def download_file(filename=None):
    try:
        if filename:
            filename = str(filename)
            csv = get_csv(filename)
            csv_file = filename + ".csv"
        else:
            csv = get_csv('alldata')
            csv_file = "alldata.csv"
        response = make_response(csv)
        response_header = "attachment; fname=" + csv_file
        response.headers["Content-Type"] = 'text/csv'
        response.headers["Content-Disposition"] = response_header
        return response
    except:
        return abort(500)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6666)
