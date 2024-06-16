from datetime import datetime
from math import trunc


def get_beg_school_year(timestamp: int):
    current_date = datetime.fromtimestamp(timestamp)
    current_month = current_date.month
    if 8 <= current_month <= 12:
        beg_year = current_date.year
    else:
        beg_year = current_date.year - 1
    return beg_year


def long_from_base64(value: str):
    pos = 0
    long_val = base64_value(ord(value[pos]))
    pos += 1
    length = len(value)
    while pos < length:
        long_val = long_val << 6
        long_val += base64_value(ord(value[pos]))
        pos += 1
    return long_val


def base64_value(digit: str):
    if digit >= ord("A") and digit <= ord("Z"):
        return digit - ord("A")

    if digit >= ord("a"):
        return digit - ord("a") + 26

    if digit >= ord("0") and digit <= ord("9"):
        return digit - ord("0") + 52
    if digit == "$":
        return 62

    return 63


def long_to_base64(value):
    low = value & 0xFFFFFFFF
    high = value >> 32
    sb = []
    have_non_zero = base64_append(sb, (high >> 28) & 0xF, False)
    have_non_zero = base64_append(sb, (high >> 22) & 0x3F, have_non_zero)
    have_non_zero = base64_append(sb, (high >> 16) & 0x3F, have_non_zero)
    have_non_zero = base64_append(sb, (high >> 10) & 0x3F, have_non_zero)
    have_non_zero = base64_append(sb, (high >> 4) & 0x3F, have_non_zero)
    v = ((high & 0xF) << 2) | ((low >> 30) & 0x3)
    have_non_zero = base64_append(sb, v, have_non_zero)
    have_non_zero = base64_append(sb, (low >> 24) & 0x3F, have_non_zero)
    have_non_zero = base64_append(sb, (low >> 18) & 0x3F, have_non_zero)
    have_non_zero = base64_append(sb, (low >> 12) & 0x3F, have_non_zero)
    base64_append(sb, (low >> 6) & 0x3F, have_non_zero)
    base64_append(sb, low & 0x3F, True)
    return "".join(sb)


def base64_append(sb, digit, have_non_zero):
    if digit > 0:
        have_non_zero = True
    if have_non_zero:
        c = 0
        if digit < 26:
            c = ord("A") + digit
        elif digit < 52:
            c = ord("a") + digit - 26
        elif digit < 62:
            c = ord("0") + digit - 52
        elif digit == 62:
            c = ord("$")
        else:
            c = ord("_")
        sb.append(chr(c))
    return have_non_zero


def get_beg_end_date():
    current_date = datetime.now()
    current_month = current_date.month
    beg_year = 0
    if 10 <= current_month <= 12:
        beg_year = current_date.year
    else:
        beg_year = current_date.year - 1

    beg_date_timestamp = datetime(beg_year, 9, 1)
    end_date_timestamp = datetime(beg_year + 1, 9, 1)

    return (beg_date_timestamp, end_date_timestamp)


def get_base64_from_datetime(datetime_object: datetime):
    return long_to_base64(trunc(datetime_object.timestamp() * 1e3))


if __name__ == "__main__":
    print(long_from_base64("YtynhhU"))
