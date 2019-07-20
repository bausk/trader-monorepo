from datetime import datetime

sql_timestamp_format = "%Y-%m-%d %H:%M:%S.%f"

def get_utcnow_sql_timestamp():
    now = datetime.utcnow()
    return now.strftime(sql_timestamp_format)

def get_unixtime_sql_timestamp(unix_timestamp):
    now = datetime.fromtimestamp(unix_timestamp)
    return now.strftime(sql_timestamp_format)
