from datetime import datetime
from math import trunc, log
from entbot.constants import TUPLE_DIGITS_BASE64


def get_beg_school_year(timestamp: int):
    current_date = datetime.fromtimestamp(timestamp)
    current_month = current_date.month
    if 8 <= current_month <= 12:
        beg_year = current_date.year
    else:
        beg_year = current_date.year - 1
    return beg_year


def long_from_base64(value: str):
    long_value = 0
    nb_digits = len(value)
    for i in range(0, nb_digits):
        current_digit = value[i]
        current_power = nb_digits - i - 1
        long_value += (
            TUPLE_DIGITS_BASE64.index(current_digit) * 64**current_power
        )
    return long_value


def long_to_base64(value: int):
    max_power = trunc(log(value, 64))
    string_base64 = ""
    for current_power in range(max_power, -1, -1):
        index = value // 64**current_power
        index = index if index <= 63 else 63
        string_base64 += TUPLE_DIGITS_BASE64[index]
        value -= index * 64**current_power

    return string_base64


def get_beg_end_date():
    current_date = datetime.now()
    current_month = current_date.month
    beg_year = 0
    if 9 <= current_month <= 12:
        beg_year = current_date.year
    else:
        beg_year = current_date.year - 1

    beg_date = datetime(beg_year, 9, 1)
    end_date = datetime(beg_year + 1, 9, 1)

    return (beg_date, end_date)


def get_base64_from_datetime(datetime_object: datetime):
    return long_to_base64(trunc(datetime_object.timestamp() * 1e3))
