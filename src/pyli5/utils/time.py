from datetime import datetime

def get_time_utc() -> str:
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')