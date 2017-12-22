# External imports
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
import pymongo
import pytz
import sqlite3

# System imports
import datetime as dt
import os

# Project imports
from lib.database.mongo import db

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
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

def prettify_datetime(inp_dt):
    dt = inp_dt if inp_dt.tzinfo else localize_datetime(inp_dt)
    return dt.strftime("%d %b, %y %I:%M %p") 

def datetime_to_epoch(input_dt):
    epoch = dt.datetime.utcfromtimestamp(0)
    delta = input_dt - epoch
    return int(delta.total_seconds()*1000)

@app.route('/')
def show_log():
    moistures = list(db.moisture.find().sort("_id", pymongo.DESCENDING))
    for item in moistures:
        item["datetime"] = prettify_datetime(item["datetime"])
    return render_template('show_log.pug', moistures=moistures)

@app.route('/moisture', methods=['GET'])
def get_moisture():
    moistures = list(db.moisture.find().sort("_id", pymongo.ASCENDING))
    def formatData(el):
        timestamp = datetime_to_epoch(el["datetime"])
        # The sensor reading is a measure of now dry the soil is
        # As such, you take the complement of this value to get the moisture analog
        # The complement is achieved by subtracting the value from 1024 (the maximum raeding from the 10 bit analog input on the MCU
        moisture = 1024 - float(el["measurement"])
        return [timestamp, moisture]

    response = jsonify(map(formatData, moistures))
    return response


@app.route('/moisture', methods=['POST'])
def add_measurement():
    if request.form['measurement']:
        db.moisture.insert({
            "measurement": float(request.form['measurement']),
            "datetime": dt.datetime.utcnow()
        })
        flash('New measurement was successfully posted')
    else:
        flash('Invalid measurement submitted')

    return redirect(url_for('show_log'))

@app.route('/moisture/irrigation', methods=['POST'])
def record_irrigation():
    print("ADD WATERING")
    return jsonify({"success": True})

