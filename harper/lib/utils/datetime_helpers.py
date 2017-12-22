# External imports
import pytz

# System imports
import datetime as dt

# Prohect imports
from harper.settings import base as settings

def localize_datetime(naive_dt):
    eastern = pytz.timezone(settings.LOCAL_TIMEZONE)
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
