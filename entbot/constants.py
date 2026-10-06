"""Module to store all the constants needed.
There are also variable strings defined in 
the classes Payload and URL used for the bot."""

import re
import string

### Strings for giving indications to users

CHOICE_MODE_PROMPT = """Choose one of the services below by entering its number:\n
1 : Download all your courses available on Ametice
2 : Get the link of the timetable of your choice\n"""

LIST_MODULES = [
    "assign",
    "folder",
    "resource",
    "url",
    "quiz",
    "choice",
    "forum",
]
TUPLE_TREATED_MODULES = ["folder", "resource", "url", "quiz"]
MAX_DOWNLOAD_ATTEMPTS = 5
RETRY_DELAY_SECONDS = 1
TIMESTAMP_ID = "Y8XbcIu"

TUPLE_DIGITS_BASE64 = tuple(
    string.ascii_uppercase + string.ascii_lowercase + string.digits + "$_"
)


class URL:
    """Class used to store urls."""

    ENT_LOGIN = "https://ident.univ-amu.fr/cas/login"
    AMETICE = (
        "https://ident.univ-amu.fr/cas/login?service=https://"
        "ametice.univ-amu.fr/login/index.php?authCAS=CAS"
    )
    DIRECT_PLANNING = "https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy"
    ADE_LOGIN = "https://ident.univ-amu.fr/cas/login?service=https%3A%2F%2Fade-web-consult.univ-amu.fr%2Fdirect%2Fmyplanning.jsp"
    CORE_PLANNING = "https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/CorePlanningServiceProxy"
    CONFIG = "https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/ConfigurationServiceProxy"
    WEB_CLIENT = "https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/WebClientServiceProxy"
    MY_PLANNING = "https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/MyPlanningClientServiceProxy"

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
    def element(cm_id, cm_module):
        """Method to get the url redirection of a course module with its
        id and module name

        Args:
            - cm_id (str): The course id we want to get the url from.
            - cm_module (str): The module name associated to the course
            with id cm_id.

        Returns (str): The url redirecting to the file associated to the
        course module id.
        """

        if cm_module == "folder":
            cm_url = (
                "https://ametice.univ-amu.fr/mod/"
                f"folder/download_folder.php?id={cm_id}"
            )
        else:
            cm_url = (
                "https://ametice.univ-amu.fr/mod/"
                f"{cm_module}/view.php?id={cm_id}&redirect=1"
            )
        return cm_url


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
    def login(username, password, execution):
        """Return the HTTP Payload to post to URL_LOGIN.

        Args:
            - username (str): The username to sign in with.
            - password (str): The password to sign in with.
            - execution (str): The CAS flow state, read from the
            hidden "execution" field of the login form.
        """

        return {
            "username": f"{username}",
            "password": f"{password}",
            "_eventId": "submit",
            "execution": execution,
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


class GWTPayload:

    def __init__(self, sess_id) -> None:
        self.sess_id = sess_id
        super().__init__()

    def ade_login(self):
        """To use with URL.MY_PLANNING"""
        return f"7|0|8|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|2912ADA6C426CFB85D3ACABE4CE65F74|com.adesoft.gwt.directplan.client.rpc.MyPlanningClientServiceProxy|method1login|J|com.adesoft.gwt.core.client.rpc.data.LoginRequest/3705388826|com.adesoft.gwt.directplan.client.rpc.data.DirectLoginRequest/635437471||1|2|3|4|2|5|6|{self.sess_id}|7|0|0|0|1|1|8|8|-1|0|0|"

    def config(self):
        return f"7|0|7|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|2151F6DCAC1F72D0ABE4B87ADF1A9E37|com.adesoft.gwt.core.client.rpc.ConfigurationServiceProxy|method1getInitialConfiguration|J|java.lang.String/2004016611|fr|1|2|3|4|2|5|6|{self.sess_id}|7|"

    def year_mpci_id(self):
        return ""

    def tree_ids(self, name: str):
        return (
            '7|0|7|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|ED09B1B4CB67D19361C6552338791595|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method12searchResource|J|java.lang.String/2004016611|[1]{"StringField""NAME""""'
            + name
            + '""false""true""true""true""2147483647""false"[0]"CONTAINS""false""false""0"|1|2|3|4|2|5|6|'
            + self.sess_id
            + "|7|"
        )

    def children_from_semester(self, semester_id: str, semester_number: int):
        year_number = (
            semester_number // 2
            if semester_number % 2 == 0
            else semester_number // 2 + 1
        )
        return (
            '7|0|20|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|ED09B1B4CB67D19361C6552338791595|com.adesoft.gwt.directplan.client.rpc.DirectPlanningServiceProxy|method4getChildren|J|java.lang.String/2004016611|com.adesoft.gwt.directplan.client.ui.tree.TreeResourceConfig/2234901663|{"'
            + semester_id
            + '""true""6""-1""0""0""0""false"[2]{"ColorField""COLOR""LabelColor""255,255,255""false""false"{"StringField""NAME""LabelName""S'
            + str(semester_number)
            + ' MPCI""false""false""Sciences.L. MPCI.ST JEROME.L'
            + str(year_number)
            + " MPCI.ST JEROME.S"
            + str(semester_number)
            + ' MPCI""trainee""1""0"[0][0]|[I/2970817851|java.util.LinkedHashMap/3008245022|COLOR|com.adesoft.gwt.core.client.rpc.config.OutputField/870745015|LabelColor||com.adesoft.gwt.core.client.rpc.config.FieldType/1797283245|NAME|LabelName|java.util.ArrayList/4159755760|com.extjs.gxt.ui.client.data.SortInfo/1143517771|com.extjs.gxt.ui.client.Style$SortDir/3873584144|1|2|3|4|3|5|6|7|'
            + self.sess_id
            + "|8|7|0|9|2|-1|-1|10|0|2|6|11|12|0|13|11|14|15|11|0|0|6|16|12|0|17|16|14|15|4|0|0|18|0|18|0|19|20|1|16|18|0|"
        )

    def timeline_url(self, course_id: str, beg_base64: str, end_base64: str):
        return f"7|0|11|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|AB6CBED41BD6D0AD629E9C452786823C|com.adesoft.gwt.core.client.rpc.CorePlanningServiceProxy|method9getGeneratedUrl|J|java.util.List|java.lang.String/2004016611|java.util.Date/3385151746|java.lang.Integer/3438268394|java.util.ArrayList/4159755760|ical|1|2|3|4|7|5|6|7|8|8|9|9|{self.sess_id}|10|1|9|{course_id}|11|8|{beg_base64}|8|{end_base64}|9|8|9|518|"

    def webclient(self):
        return f"7|0|5|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|FE500F0EAC5A5732DFC902C566E7EBA7|com.adesoft.gwt.core.client.rpc.WebClientServiceProxy|method39isSsoConnected|J|1|2|3|4|1|5|{self.sess_id}|"

    def load_project(self):
        return f"7|0|7|https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/|FE500F0EAC5A5732DFC902C566E7EBA7|com.adesoft.gwt.core.client.rpc.WebClientServiceProxy|method6loadProject|J|I|Z|1|2|3|4|3|5|6|7|{self.sess_id}|8|0|"


class Headers:
    """Class used to store headers."""

    LOGIN_HEADERS = {
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ),
        "Connection": "keep-alive",
    }

    GWT_HEADERS = {
        "Content-Type": "text/x-gwt-rpc; charset=UTF-8",
        "X-GWT-Permutation": "6BB96DE630E95DDAAE138058924E4424",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ),
        "Connection": "keep-alive",
    }


class RegexPatterns:
    COURSE_ID = r"\{\\\"(-?[1-9][0-9]*)"
    COURSE_ID_NAME = re.compile(
        r"\{\\\"(-?[1-9][0-9]*).*?\\\"LabelName\\\"\\\"([a-zA-Z0-9 ]*)\\\""
    )
    TIMELINE_URL = r"\"(.*)\""
    URL_HEX_VALUES = r"\\x([0-9a-fA-F]{2})"
    JS_VARIABLE = re.compile(r"M\.cfg = ([^;]*)")
    FILENAME_FORBIDDEN_CHARS = re.compile(r"(?u)[^-\w.]")
    SCHOOL_YEAR_REGEX = re.compile(r"\d+\-\d+")
