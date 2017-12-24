# External imports
import pytz

# System imports
import datetime as dt
import pytz

# Prohect imports
from harper.settings import base as settings
from harper.lib.utils import global_vars as gvars

def localize_datetime(inp_dt):
    eastern = pytz.timezone(settings.LOCAL_TIMEZONE)
    aware_dt = inp_dt if inp_dt.tzinfo else pytz.utc.localize(inp_dt)
    local_dt = aware_dt.astimezone(eastern)
    return local_dt

def prettify_datetime(inp_dt, format=gvars.DEFAULT_DT_FORMAT):
    dt = localize_datetime(inp_dt)
    return dt.strftime(format)

def datetime_to_epoch(input_dt):
    epoch = pytz.utc.localize(dt.datetime.utcfromtimestamp(0))
    delta = input_dt - epoch
    return int(delta.total_seconds()*1000)

def utcnow():
    return dt.datetime.now(pytz.utc)
