from datetime import datetime, timedelta, date
import calendar


def get_current_week_date():
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_last_week_date():
    today = datetime.now().date()
    start = today + timedelta(-today.weekday(), weeks=-1)
    end = today + timedelta(-today.weekday() - 1)
    return start, end


def get_current_month_date():
    today = datetime.today()
    day = calendar.monthrange(today.year, today.month)
    s_date_month = "{}-{}-{}".format(today.year, today.month, 1)
    l_date_month = "{}-{}-{}".format(today.year, today.month, day[1])
    return s_date_month, l_date_month

def get_last_month_date():
    today = datetime.today()
    l_date_month = today.replace(day=1) - timedelta(days=1)
    s_date_month = today.replace(day=1) - timedelta(days=l_date_month.day)
    return s_date_month, l_date_month