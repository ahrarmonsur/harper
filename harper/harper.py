import os
import sqlite3
import datetime as dt
import pytz
from flask import (
        Flask,
        request,
        session, g,
        redirect,
        url_for,
        abort,
        render_template,
        flash,
        jsonify,
    )

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'harper.sq3'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    TIMEZONE='Canada/Eastern'
))
app.config.from_envvar('HARPER_SETTINGS', silent=True)
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

def localize_datetime(naive_dt):
    eastern = pytz.timezone(app.config['TIMEZONE'])
    aware_dt = pytz.utc.localize(naive_dt)
    local_dt = aware_dt.astimezone(eastern)
    return local_dt

def datetime_to_epoch(input_dt):
    epoch = dt.datetime.utcfromtimestamp(0)
    delta = input_dt - epoch
    return int(delta.total_seconds()*1000)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_COLNAMES)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def show_log():
    db = get_db()
    cur = db.execute('select measurement, timestamp from moisture order by id desc')
    moistures = cur.fetchall()
    return render_template('show_log.pug', moistures=moistures)

@app.route('/moisture', methods=['GET'])
def get_moisture():
    def convert_to_local_timestamp(dt):
        pass
    db = get_db()
    cur = db.execute('select timestamp as "ts [timestamp]", measurement from moisture order by id asc')
    moistures = cur.fetchall()
    def formatData(row):
        timestamp = datetime_to_epoch(row[0])
        # The sensor reading is a measure of now dry the soil is
        # As such, you take the complement of this value to get the moisture analog
        # The complement is achieved by subtracting the value from 1024 (the maximum raeding from the 10 bit analog input on the MCU
        moisture = 1024 - row[1]
        return [timestamp, moisture]

    response = jsonify(map(formatData, moistures))
    return response


@app.route('/moisture', methods=['POST'])
def add_measurement():
    if request.form['measurement']:
        db = get_db()
        db.execute('insert into moisture (measurement, timestamp) values (?, ?)',
                     [request.form['measurement'], dt.datetime.utcnow()])
        db.commit()
        flash('New measurement was successfully posted')
    else:
        flash('Invalid measurement submitted')

    return redirect(url_for('show_log'))
