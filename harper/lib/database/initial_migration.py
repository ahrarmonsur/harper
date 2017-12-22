"""
Script to initially migrate from the sqlite3 database to MongoDB
"""
import json, pytz
import dateutil.parser as dup
from harper.lib.database.mongo import db

with open("/root/dev/harper/harper/backup/20171215_moistureData.json", "r") as backup:
    dump = json.load(backup)
    moisture_coll = db.moisture
    for entry in dump:
        measurement = entry["moisture"]
        time = dup.parse(entry["time"])
        aware_time = pytz.utc.localize(time)
        moisture_coll.insert({
            "measurement": measurement,
            "datetime": aware_time
        })

    print "**Migration Done**"











