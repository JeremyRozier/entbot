"""Module which contains functions which parse filenames
"""

from mimetypes import guess_type
import unicodedata
import os
import re
from constants import RegexPatterns
from urllib.parse import urlparse
from mimetypes import guess_extension
from timestamp_functions import get_beg_school_year


def get_valid_filename(filename):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    """
    if "." in filename:
        tuple_before_after = os.path.splitext(filename)
        if guess_type(tuple_before_after[1]) is not None:
            filename = tuple_before_after[0]

    valid_filename = str(filename).strip().replace(" ", "_")
    valid_filename = RegexPatterns.FILENAME_FORBIDDEN_CHARS.sub(
        "", valid_filename
    )
    valid_filename = unicodedata.normalize("NFKD", valid_filename)
    valid_filename = "".join(
        [c for c in valid_filename if not unicodedata.combining(c)]
    )
    return valid_filename


def get_nb_origin_same_filename(folder_path, filename):
    """
    Returns for a given filename the number of files
    already saved which match with this pattern
    rf{filename}(_d+)?, or 0 if there aren't any conflicts.
    """
    list_files = [
        os.path.splitext(f)[0]
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    list_same_file = [f for f in list_files if f == filename]
    if len(list_same_file) == 0:
        return 0

    pattern = rf"{filename}(_\d+)?"
    list_similar = [f for f in list_files if re.match(pattern, f)]
    return len(list_similar)


def get_filename_nb(folder_path, filename):
    filename_nb = filename
    if os.path.exists(folder_path):
        nb_same_filename = get_nb_origin_same_filename(folder_path, filename)
        if nb_same_filename > 0:
            filename_nb = f"{filename}_{nb_same_filename}"
    return filename_nb


def get_file_extension(file_url, file_content_type, cm_module):
    if cm_module == "folder":
        extension = ".zip"
    elif cm_module == "resource":
        parsed = urlparse(file_url)
        extension = os.path.splitext(parsed.path)[1]
        if len(extension) == 0:
            extension = guess_extension(file_content_type)
            if extension is None:
                extension = ""
    else:
        extension = ".txt"
    return extension


def get_school_year(course_name: str, start_date_timestamp: int) -> str:
    match_school_year = RegexPatterns.SCHOOL_YEAR_REGEX.search(course_name)
    if match_school_year is not None:
        return match_school_year.group(0)
    beg_school_year = get_beg_school_year(start_date_timestamp)
    end_school_year = beg_school_year + 1
    return f"{str(beg_school_year)[-2:]}-{str(end_school_year)[-2:]}"
