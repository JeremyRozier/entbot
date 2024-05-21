from datetime import datetime
from timestamp_functions import get_beg_school_year


def test_get_beg_scholar_year():
    test_date_1 = datetime(2024, 2, 18)
    test_date_2 = datetime(2023, 8, 30)
    timestamp_1 = round(test_date_1.timestamp())
    timestamp_2 = round(test_date_2.timestamp())
    assert get_beg_school_year(timestamp_1) == 2023
    assert get_beg_school_year(timestamp_2) == 2023
