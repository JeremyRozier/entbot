"""Module to store all the constants needed.
There are also variable strings defined in 
the classes Payload and URL used for the bot."""

import re
import check_dir  # pylint:disable=W0611:unused-import

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ),
    "Connection": "keep-alive",
}

LIST_TYPES = ["assign", "folder", "resource", "url", "quiz", "choice", "forum"]
LIST_TREATED_TYPES = ["folder", "resource", "url"]

with open("execution_code.txt", "r", encoding="utf-8") as file:
    EXECUTION_CODE = file.read()


class URL:
    """Class used to store urls."""

    LOGIN = "https://ident.univ-amu.fr/cas/login"
    AMETICE = (
        "https://ident.univ-amu.fr/cas/login?service=https://"
        "ametice.univ-amu.fr/login/index.php?authCAS=CAS"
    )

    @staticmethod
    def course(session_key):
        """Method to get the url to get the courses data."""
        return (
            "https://ametice.univ-amu.fr/lib/ajax/"
            f"service.php?sesskey={session_key}&"
            "info=core_course_get_enrolled_courses_by_timeline_classification"
        )

    @staticmethod
    def topics(session_key):
        """Method to get the url of a topic with
        a session key."""
        return (
            "https://ametice.univ-amu.fr/lib/ajax/service.php"
            f"?sesskey={session_key}&info=core_courseformat_get_state"
        )

    @staticmethod
    def folder(cm_id):
        """Method to get the url of a folder with
        a course module id"""
        return (
            "https://ametice.univ-amu.fr/mod/"
            f"folder/download_folder.php?id={cm_id}"
        )


class Payload:
    """Class used to store payloads."""

    COURSES = [
        {
            "index": 0,
            "methodname": (
                "core_course_get_enrolled_courses_by_timeline_classification"
            ),
            "args": {
                "offset": 0,
                "limit": 24,
                "classification": "all",
                "sort": "fullname",
                "customfieldname": "",
                "customfieldvalue": "",
            },
        }
    ]

    @staticmethod
    def login(username, password):
        """Return the HTTP Payload to post to URL_LOGIN."""

        return {
            "username": f"{username}",
            "password": f"{password}",
            "_eventId": "submit",
            "execution": EXECUTION_CODE,
        }

    @staticmethod
    def topics(course_id):
        """Return the HTTP Payload to post to get topics informations
        from a course."""
        return [
            {
                "index": 0,
                "methodname": "core_courseformat_get_state",
                "args": {"courseid": course_id},
            }
        ]


class RegexPatterns:
    COURSE_ID = r"\{\\\"(-?[1-9][0-9]*)"
    TIMELINE_URL = r"\"(.*)\""
    URL_HEX_VALUES = r"\\x([0-9a-fA-F]{2})"
    JS_VARIABLE = re.compile(r"M\.cfg = ([^;]*)")
    RESOURCE_TYPE = re.compile(
        rf"https://ametice\.univ-amu\.fr/mod/(.*)/view\.php\?id=[0-9]+"
    )
    SCHOOL_YEAR_REGEX = re.compile(r"\[\d+\-\d+\]")
