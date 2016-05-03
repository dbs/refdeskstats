#!/usr/bin/env python

"""Collect daily reference desk statistics in a database

Display the stats in a useful way with charts and download links"""

from flask import Flask, abort, request, redirect, url_for, \
                    render_template, make_response, g, session
from flask_babelex import Babel
from flask_login import LoginManager, login_required, current_user, \
                        login_user, logout_user, AnonymousUserMixin
from os.path import abspath, dirname
from data import lists
from conf import ConfigFile
import ldap
import sys
import datetime
import psycopg2
import StringIO
import copy
import csv
import random
import ConfigParser
from optparse import OptionParser

class LocalCGIRootFix(object):
    """Wrap the application in this middleware if you are using FastCGI or CGI
    and you have problems with your app root being set to the cgi script's path
    instead of the path users are going to visit
    .. versionchanged:: 0.9
       Added `app_root` parameter and renamed from `LighttpdCGIRootFix`.
    :param app: the WSGI application
    :param app_root: Defaulting to ``'/'``, you can set this to something else
        if your app is mounted somewhere else.

    Clone of workzeug.contrib.fixers.CGIRootFix, but doesn't strip leading '/'
    """

    def __init__(self, app, app_root='/'):
        self.app = app
        self.app_root = app_root

    def __call__(self, environ, start_response):
        # only set PATH_INFO for older versions of Lighty or if no
        # server software is provided.  That's because the test was
        # added in newer Werkzeug versions and we don't want to break
        # people's code if they are using this fixer in a test that
        # does not set the SERVER_SOFTWARE key.
        if 'SERVER_SOFTWARE' not in environ or \
           environ['SERVER_SOFTWARE'] < 'lighttpd/1.4.28':
            environ['PATH_INFO'] = environ.get('SCRIPT_NAME', '') + \
                environ.get('PATH_INFO', '')
        environ['SCRIPT_NAME'] = self.app_root.rstrip('/')
        return self.app(environ, start_response)

app = Flask(__name__)
app.root_path = abspath(dirname(__file__))

opt = {}
parser = OptionParser()
parser.add_option('-d', '--debug', dest='DEBUG', action='store_true',
            help='Provides debug output when unhandled exceptions occur.')
parser.add_option('-v', '--verbose', dest='VERBOSE', action='store_true',
            help='Provides verbose output for what is being done.')
parser.add_option('-s', '--student', dest='STUDENT', action='store_true',
            help='Connects to the student LDAP instead of the staff.')
cmd_opt, junk = parser.parse_args()

c = ConfigFile(app.root_path + '/config.ini')
keys = c.getsection('Refdesk') 
for key in keys:
    opt[key] = keys[key]

opt['DEBUG']  = cmd_opt.DEBUG
opt['VERBOSE'] = cmd_opt.VERBOSE
opt['STUDENT'] = cmd_opt.STUDENT

if opt['VERBOSE']:
    print('Root path: ' + app.root_path)
if opt['VERBOSE']:
    print(app.root_path + '/config.ini')

if opt['SECRET']:
    app.secret_key = opt['SECRET']
else:
    print('No secret key. Aborting.')
    exit()

app.wsgi_app = LocalCGIRootFix(app.wsgi_app, app_root=opt['APP_ROOT'])

babel = Babel(app)
login_manager = LoginManager()
login_manager.init_app(app)

def get_db():
    """
    Get a database connection

    With a host attribute in the mix, you could connect to a remote
    database, but then you would have to set up .pgpass or add a
    password parameter, so let's keep it simple.
    """
    try:
        return psycopg2.connect(
            database=opt['DB_NAME'],
            user=opt['DB_USER']
        )
    except Exception, ex:
        if opt['VERBOSE']:
            print(ex)

def get_ldap_connection():
    conn = ldap.initialize('ldap://'+opt['LDAP_HOST'])
    return conn

class User():
    __tablename__ = 'users'

    def __init__(self, username, session_id = None):
        self.uname = username
        if not session_id:
            self.id = random.SystemRandom().randint(-0xFFFFFF, 0xFFFFFF)
        else:
            self.id = session_id
        if opt['VERBOSE']:
            print(self.id)
   
    @staticmethod 
    def try_login(username, password):
        conn = get_ldap_connection()
        if opt['STUDENT']:
            conn.simple_bind_s('cn=%s,ou=STD,o=LUL' % username, password)
        else:
            conn.simple_bind_s('cn=%s,ou=Empl,o=LUL' % username, password)
 
    @staticmethod
    def get_by_id(id):
        dbh = get_db()
        cur = dbh.cursor()
        cur.execute("SELECT id, uname FROM users where id = %s" % id)
        row = cur.fetchone()
        try:
            if row[0]:
                i = row[0]
                u = row[1]
                dbh.close()
                return User(u, i)
            else:
                dbh.close()
                return None
        except Exception, ex:
            if opt['VERBOSE']:
                print(ex)
        dbh.close()
        # Executes is query returns no rows.
        return None

    @staticmethod
    def get_by_uname(uname):
        dbh = get_db()
        cur = dbh.cursor()
        cur.execute("SELECT id, uname FROM users")
        for row in cur.fetchall():
            if uname == row[1]:
                dbh.close()
                return User(row[1], row[0])
            else:
                return None
        dbh.close()
        return None

    def add_to_db(self):
        dbh = get_db()
        cur = dbh.cursor()
        cur.execute("""
            INSERT INTO users (id, uname)
            VALUES (%s, %s)""", (self.id, self.uname))
        dbh.commit()
        dbh.close()
    
    def logout(self):
        dbh = get_db()
        cur = dbh.cursor()
        cur.execute("""
            DELETE FROM users WHERE uname = '%s'""" % self.uname)
        dbh.commit()
        dbh.close()

    def expired(self):
        dbh = get_db()
        cur = dbh.cursor()
        cur.execute("""SELECT expires FROM users WHERE uname = %s AND id = %s""", (self.uname, self.id))
        row = cur.fetchone()
        if row[0] < datetime.datetime.now():
            dbh.close()
            return True
        dbh.close()
        return False

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

@babel.localeselector
def get_locale():
    return g.get('current_lang','en');

@app.before_request
def pre_request():
    try:
        if opt['VERBOSE']:
            print(session['uid'])
        current_user = User.get_by_id(session['uid'])
        if current_user.expired():
            current_user.logout()
            logout_user()
    except Exception, ex:
        if opt['VERBOSE']:
            print('User is anonymous.')

    try:
        g.user = current_user
    except Exception, ex:
        if opt['VERBOSE']:
            print('No user object set for session.')

    if request.view_args and 'lang' in request.view_args:
        lang = request.view_args['lang']
        if lang in ['en', 'fr']:
            g.current_lang = lang
            request.view_args.pop('lang')
        else:
            return abort(404)

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(id) 

@app.route('/<lang>/', methods=['GET', 'POST'])
@login_required
def submit(date=None):
    "Either show the form, or process the form"
    if request.method == 'POST':
        return eat_stat_form()
    else:
        #return show_stat_form()
        if opt['VERBOSE']:
            print('Before queueing data edit.')
        return edit_data(date)

@app.errorhandler(401)
def page_forbidden(err):
    "Redirect to the login page."
    return render_template('login.html'), 200

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

def login():
    """
    Attempt to log into the LDAP server with the authentication
    provided by a form.
    """
    try:
        if current_user.is_authenticated():
            if opt['VERBOSE']:
                print(current_user)
            return redirect(url_for('edit_data', lang='en')), 302

        form = request.form
        username = form['user']
        password = form['pass']

        if opt['VERBOSE']:
            print(username)

        User.try_login(username, password)
        user = User.get_by_uname(username)
        if not user:
            user = User(username)
            user.add_to_db()
        session['uid'] = user.id
        login_user(user)
        return redirect(url_for('edit_data', lang='en')), 302

    except Exception, ex:
        if opt['VERBOSE']:
            print(ex)
        return render_template('login_fail.html'), 401

def eat_stat_form():
    "Shove the form data into the database"
    try:
        dbh = get_db()
        cur = dbh.cursor()
        form = request.form
        fdate = form['refdate']
        if opt['VERBOSE']:
            print('reached data insertion...')
        for time in lists['timelist']:
            for stat in lists['helplist']:
                if opt['VERBOSE']:
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
        if opt['VERBOSE']:
            print(ex)
        return abort(500)

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
        if opt['VERBOSE']:
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
        if opt['VERBOSE']:
            print(ex)

def get_csv(filename):
    "Get the data in CSV format"
    try:
        data = get_db()
        cur = data.cursor()
        #print(cur.mogrify("SELECT refdate, refstat, refcount FROM refstats WHERE refdate = %s", (str(filename),)))
        if str(filename) == 'allstats':
            cur.execute("SELECT refdate, reftime, reftype, refcount_en, refcount_fr FROM refstatview ORDER BY refdate, reftime, reftype")
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
        if opt['VERBOSE']:
            print(ex)

def get_data_array(date):
    "Put the data into an array for Google charts"
    try:
        data = get_db()
        cur = data.cursor()
        cur.execute("""SELECT refdate, reftime, reftype, refcount_en,
                       refcount_fr FROM refstatview WHERE refdate=%s""",
                       (str(date),))
        stack = copy.deepcopy(lists['stack_a'])
        array = copy.deepcopy(lists['array'])

        for row in cur.fetchall():
            timeslot = str(row[1])
            stat = row[2]
            array[lists['helpcodes'][stat+'_en']-1][lists['timecodes'][timeslot]] = row[3]
            array[lists['helpcodes'][stat+'_fr']-1][lists['timecodes'][timeslot]] = row[4]

        data.commit()
        data.close()

        for stat_data in array:
            stack.append(stat_data)

        return stack
    except Exception, ex:
        if opt['VERBOSE']:
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
            if opt['VERBOSE']:
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

        stack = copy.deepcopy(lists['stack_b'])
        times = copy.deepcopy(lists['times'])

        if opt['VERBOSE']:
            print(times)

        for row in cur.fetchall():
            timeslot = str(row[0])
            stat = row[1]
            #print(helpcodes[stat])
            #if timeslot in lists['timelist']:
            times[lists['timecodes'][timeslot]-1][lists['helpcodes'][stat+'_en']] = row[2]
            times[lists['timecodes'][timeslot]-1][lists['helpcodes'][stat+'_fr']] = row[3]

        
        if opt['VERBOSE']:
            print(times)
            
        data.commit()
        data.close()
        for time in times:
            stack.append(time)
            #print(time)
        #print(stack)
        return stack
    except Exception, ex:
        if opt['VERBOSE']:
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

        stack = copy.deepcopy(lists['stack_b'])
        days = copy.deepcopy(lists['days'])

        for row in cur.fetchall():
            """Get the data for each day of the month and do something useful with it"""
            timeslot = row[0]
            stat = row[1]
            if row[4] >= 0 and row[4] <= 6:
                days[int(row[4])][lists['helpcodes'][stat+'_en']] += row[2]
                days[int(row[4])][lists['helpcodes'][stat+'_fr']] += row[3]

        data.commit()
        data.close()

        for day in days:
            stack.append(day)
        #print(stack)
        return stack

    except Exception, ex:
        if opt['VERBOSE']:
            print(ex)

def parse_date(date):
    "Returns the year and the month separately from the date"

    date_parts = str(date).split('-')
    return date_parts[0], date_parts[1]

def parse_stat(stat):
    "Returns the type of stat and the time slot"

    for s in lists['helplist']:
        if opt['VERBOSE']: 
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
        if opt['VERBOSE']:
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
        if opt['VERBOSE']:
            print(ex)

@app.route('/<lang>/login/', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        return login()
    else:
        return render_template('login.html');

@app.route('/<lang>/logout/', methods=['GET'])
@login_required
def logout():
    current_user.logout()
    logout_user()
    return redirect(url_for('login_form', lang='en')), 302

@app.route('/<lang>/view/', methods=['GET'])
@app.route('/<lang>/view/<date>', methods=['GET'])
@login_required
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

@app.route('/<lang>/', methods=['GET','POST'])
@app.route('/<lang>/edit/<date>', methods=['GET','POST'])
@login_required
def edit_data(date):
    "Add data to missing days or edit current data"
    if request.method == 'POST':
        return eat_stat_form()
    try:
        if date:
            stats = get_current_data(date)
            #if opt['VERBOSE']:
            #    print(date + 'stats:' + stats)
            #if stats:
            if opt['VERBOSE']:
                print ('before page render: stats found')
            return render_template('stat_form.html', today=date, stats=stats)
            #else:
                #return render_template('stat_form.html', today=date)
                #return render_template('edit_stat_form.html', today=date, stats=stats)
        else:
            if opt['VERBOSE']:
                print ('before page render: no stats')
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            if opt['VERBOSE']:
                print(date)
            stats = get_current_data(date)
            return render_template('stat_form.html', today=((datetime.datetime.now() + datetime.timedelta(hours=-2)).date().isoformat()), stats=stats)
    except Exception, ex:
        if opt['VERBOSE']:
            print(ex)
        return abort(500)

@app.route('/<lang>/download/')
@app.route('/<lang>/download/<filename>')
@login_required
def download_file(filename='allstats'):
    "Downloads a file in CSV format"
    try:
        filename = str(filename)
        csv_data = get_csv(filename)
        csv_file = filename + ".csv"

        response = make_response(csv_data)
        response_header = "attachment; fname=" + csv_file
        response.headers["Content-Type"] = 'text/csv'
        response.headers["Content-Disposition"] = response_header
        return response
    except Exception, ex:
        if opt['VERBOSE']:
            print(ex)
        return abort(500)

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == '__main__':
    #app.run(debug=opt['DEBUG'], host=opt['HOST'], port=opt['PORT'])
    from twisted.internet import reactor
    from twisted.web.server import Site
    from twisted.web.wsgi import WSGIResource

    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)

    reactor.listenTCP(opt['PORT'], site, interface=opt['HOST'])
    reactor.run()
