from datetime import datetime


def get_beg_school_year(timestamp: int):
    current_date = datetime.fromtimestamp(timestamp)
    current_month = current_date.month
    if 8 <= current_month <= 12:
        beg_year = current_date.year
    else:
        beg_year = current_date.year - 1
    return beg_year
