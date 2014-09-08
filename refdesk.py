from flask import Flask, request, render_template
from datetime import date
import psycopg2
import sqlite3

# Database connection info
DB_NAME = 'refstats'
DB_HOST = 'localhost'
DB_USER = 'refstats'

app = Flask(__name__)

# Table definition
# CREATE TABLE refstats (refdate DATE, refstat TEXT, refcount INTEGER, create_time TIMESTAMP DEFAULT NOW());
# ALTER TABLE refstats ADD PRIMARY KEY (refdate, refstat);

# Table permissions
# GRANT SELECT, INSERT, UPDATE, DELETE ON refstats TO refstats;

def get_db():
    return psycopg2.connect(
#        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER
    )

@app.route('/refdesk-stats', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        return eat_stat_form()
    else:
        return show_stat_form()

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

def eat_stat_form():
    try:
        db = get_db()
        cur = db.cursor()
        f = request.form
        d = f.getlist('refdate')[0]
        for key in f.keys():
            if key == 'refdate':
                continue
            for val in f.getlist(key):
                cur.execute('INSERT INTO refstats (refdate, refstat, refcount) VALUES (%s, %s, %s)', (d, key, val))
        db.commit()
        db.close()
        return "Your form was successfully submitted."
    except:
        return flask.abort(500)

def show_stat_form():
    return render_template('stat_form.html', today=date.today().isoformat())

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5555)
