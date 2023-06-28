import re
from datetime import datetime


def check_datetime_format(datetime_str: str):
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    match = re.match(pattern, datetime_str)
    if match:
        try:
            datetime.strptime(datetime_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    else:
        return False
