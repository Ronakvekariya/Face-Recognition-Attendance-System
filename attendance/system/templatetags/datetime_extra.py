from django import template
from datetime import datetime

register = template.Library()

@register.filter
def time_diff(out_time, in_time):
    """
    Calculate the difference between out_time and in_time.
    Both times are assumed to be in the format 'HH:MM:SS'.
    Returns the difference formatted as 'H:MM:SS'.
    """
    try:
        # Convert time strings to datetime objects (using a dummy date)
        time_format = "%H:%M:%S"
        out_dt = datetime.strptime(out_time, time_format)
        in_dt = datetime.strptime(in_time, time_format)
        diff = out_dt - in_dt
        # In case the times cross midnight, adjust accordingly
        if diff.days < 0:
            diff = diff + datetime.strptime("24:00:00", time_format) - datetime.strptime("00:00:00", time_format)

        total_seconds = diff.seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return "{}:{:02d}:{:02d}".format(hours, minutes, seconds)
    except Exception:
        return ''
