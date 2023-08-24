import re
from datetime import timedelta

from .env import Env

def to_timedelta_from(td_string):
    """Convert timestame from "2d 4h 13m 5.2s" like format

    :param string: "2d 4h 13m 5.2s"
    :type string: str
    :return: converted timedelta
    :rtype: datetime.timedelta
    """    
    mult = {"s": 1, "m": 60, "h": 60*60, "d": 60*60*24}

    parts = re.findall(r"(\d+(?:\.\d)?)([smhd])", td_string)
    total_seconds = sum(float(x) * mult[m] for x, m in parts)

    return timedelta(seconds=total_seconds)