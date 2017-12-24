# External imports
from bson import json_util as jsutils
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
from dateutil import parser as dtparser
import pymongo
import pytz
import sqlite3

# System imports
import datetime as dt
import os

# Project imports
from lib.database.mongo import db
from lib.comms import messaging
from lib.utils import datetime_helpers as dth
from lib.utils import global_vars as gvars

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='password'
))

app.config.from_envvar('HARPER_SETTINGS', silent=True)
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')


@app.route('/')
def show_log():
    moistures = list(db.coll('moisture').find().sort('_id', pymongo.DESCENDING))
    for item in moistures:
        item['datetime'] = dth.prettify_datetime(item['datetime'])
    return render_template('show_log.pug', moistures=moistures)

@app.route('/moisture', methods=['GET'])
def get_moisture():
    moistures = list(db.coll('moisture').find().sort('_id', pymongo.ASCENDING))
    def formatData(el):
        timestamp = dth.datetime_to_epoch(el['datetime'])
        # The sensor reading is a measure of now dry the soil is
        # As such, you take the complement of this value to get the moisture analog
        # The complement is achieved by subtracting the value from 1024 (the maximum raeding from the 10 bit analog input on the MCU
        moisture = 1024 - float(el['measurement'])
        return [timestamp, moisture]

    response = jsonify(map(formatData, moistures))
    return response


@app.route('/moisture', methods=['POST'])
def add_measurement():
    if request.form['measurement']:
        db.coll('moisture').insert({
            'measurement': float(request.form['measurement']),
            'datetime': dth.utcnow()
        })
        flash('New measurement was successfully posted')
    else:
        flash('Invalid measurement submitted')

    return redirect(url_for('show_log'))

@app.route('/moisture/irrigation', methods=['POST'])
def record_irrigation():
    date = request.form.get('datetime', None)
    record = {
        'type': request.form.get('type', None),
        'plantName': request.form.get('plantName', None),
        'datetime': dtparser.parse(date) if date else dth.utcnow(),
        'duration': request.form.get('duration', None)
    }

    entry_id = db.coll('irrigation').insert(record)
    db_record = db.find_one('irrigation', {'_id': entry_id})

    # Broadcast a message to contact list
    message = "{} sipped some water{} on {}".format(
        record['plantName'] or "Your Plant",
        (" for {} milliseconds".format(record['duration']) if record['duration'] else ""),
        dth.prettify_datetime(record['datetime'], gvars.HUMANIZED_DT_FORMAT)
    )

    messaging.broadcast_message(message)

    return jsonify({'success': True, 'resp': db_record})

