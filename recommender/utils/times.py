'''
Functions to handle different timezones and push them to the relevant formats.

'''

from pytz import timezone
from datetime import datetime

def find_timezone(name):
  '''Retrieves the given timezone by name.'''
  try:
    return timezone(name)
  except:
    return None

def current_timezone():
  '''Retrieves the currently active timezone.'''
  raise NotImplementedError()

def localize_datetime(dt, tz='UTC'):
  if isinstance(tz, str):
    tz = timezone(tz)
  return tz.localize(dt)

def safe_datetime(ts):
  '''Generates a safe datetime from the input information.

  Args:
    ts: object to convert to datetime

  Returns:
    `datetime` object if converted or `None`
  '''
  # check if special case
  if ts is None or isinstance(ts, datetime):
    return ts
  # convert from int or string
  try:
    dt = unix_to_datetime(ts)
    return dt
  except:
    pass
  # try relevant string formats
  if isinstance(ts, str):
    # TODO: improve list
    for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y.%m.%d %H:%M:%S']:
      try:
        dt = datetime.strptime(date_time_str, fmt)
        if dt.tzinfo is None:
          print("WARNING: No timezone given for timestamp, infering 'UTC' as default!")
          dt = timezone('UTC').localize(dt)
        return dt
      except:
        pass
  return None

def unix_to_datetime(ts, tz=None):
  '''Converts the given objects into a datetime.

  Args:
    ts: `int` or `long` that contains the timestamp
    tz: `pytz.timezone` that is used for localization

  Returns:
    `datetime` object that contains the time
  '''
  # check if should be parsed
  if isinstance(ts, str):
    try:
      ts = int(ts)
    except:
      pass
  # check if can be converted
  if isinstance(ts, int):
    # convert to datetime
    dt = datetime.utcfromtimestamp(ts)
    dt = timezone('UTC').localize(dt)
    if tz is not None:
      dt = dt.astimezone(tz)
    else:
      print("WARNING: No timezone given for timestamp, infering 'UTC' as default!")
    return dt
  else:
    raise ValueError("Given object ({}) is not a valid int or long item!".format(ts))

def parse_time(time_str, format, timezone):
  '''Parses the given time based on the format and timezone (if provdied).

  Returns:
    (timzone-aware) datetime object
  '''
  if isinstance(timezone, str):
    timezone = find_timezone(timezone)
  if isinstance(time_str, datetime):
    dt = time_str
  else:
    dt = datetime.strptime(time_str, format)
  if timezone is not None:
    dt = dt.replace(tzinfo=timezone)
  return dt


def adjust_datetime(dt, timezone, target_timezone=None):
  '''Adjusts the given timezone to the target timezone.'''
  raise NotImplementedError()
