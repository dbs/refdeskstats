"Collect daily reference desk statistics in a database"

from flask import Flask, abort, request, render_template, Response, make_response
from os.path import abspath, dirname
import datetime
import psycopg2
import sqlite3
import StringIO
import csv

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

@app.route('/refdesk-stats', methods=['GET', 'POST'])
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
        return "Your form was successfully submitted."
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
        cur.execute('SELECT DISTINCT refdate FROM refstats')
        dates = [dict(refdate=row[0]) for row in cur.fetchall()]
        # dates = ('2004-10-01', '2014-10-31')
        if dbase.closed:
            return "I was closed!"
        dbase.commit()
        dbase.close()
        return dates
    except Exception, e:
        print(e)

def get_csv(filename):
    "Get the data in CSV format"
    #filename = flask.request.args.get('filename', '')
    try:
        data = get_db()
        cur = data.cursor()
	    #filename = '2014-09-08'
	    #print(cur.mogrify("SELECT refdate, refstat, refcount FROM refstats WHERE refdate = %s", (str(filename),)))
	    cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate=%s", (str(filename),))
	    #cur.execute("SELECT refdate, refstat, refcount FROM refstats WHERE refdate='2014-09-08'")
	    csvgen = StringIO.StringIO()
	    csvfile = csv.writer(csvgen)
	    for row in cur.fetchall():
		    #wstr = str(row[0]),str(row[1]),str(row[2])
		    csvfile.writerow([row[0], row[1], row[2]]) 
	    csv_result = csvgen.getvalue()
	    csvgen.close()
	    #csv = "column1, column2, column3"
        data.commit()
        data.close()
        return csv_result
    except Exception, e:
        print(e)

@app.route('/showRefdesk-stats', methods=['GET'])
def show_stats():
    "Lets try to get all dates with data input"
    try:
        dates = get_stats()
        return render_template('show_stats.html', dates=dates)
    except:
        return abort(500)

@app.route('/download/<filename>')
def download_file(filename):
    try:
	filename = str(filename)
        #filename = flask.request.args.get('filename', '')
	    #print(filename)
        csv = get_csv(filename)
	    print(csv)
        response = make_response(csv)
        response_header = "attachment; fname=" + filename + ".csv"
	    response.headers["Content-Type"] = 'text/csv'
        response.headers["Content-Disposition"] = response_header
        return response
    except:
        return abort(500)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6666)
