"Collect daily reference desk statistics in a database"

from flask import Flask, abort, request, render_template
from os.path import abspath, dirname
import datetime
import psycopg2
import sqlite3

# Database connection info
DB_NAME = 'refstats'
DB_HOST = 'localhost'
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

def get_db():
    """
    Get a database connection

    With a host attribute in the mix, you could connect to a remote
    database, but then you would have to set up .pgpass or add a
    password parameter, so let's keep it simple.
    """
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER
    )

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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5555)
