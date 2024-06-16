"""Module to store all the constants needed.
There are also variable strings defined in 
the classes Payload and URL used for the bot."""

import re

EXECUTION_CODE = "486eecad-5c6c-4128-a041-54316439b2ab_ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LkRsdnFrajF4aUY0SkdiSUJnUlhPeF9MN2kyT3U0M1JEZzNMSklScmxZYVJ4ZS11c1FodDlZWUpqVjJpWUtrYnNYLXZ5X0hpSGU2WmxwQ1RaRVpHUUNLWkhVVC1VeWFFX1o2bE51NXJRQ2tCZXBzNDd0dzl4T211R1BodzA5QkJiWnNfOEtzUS1mMkZoNXBUMEJlTXVrbUNTZ3RDV3VlcE1MWVp5bEtLRnB3QTdIdXY5dDR1MXVpUW8tclg5blk4Sm9zVUdGbXZsSTVmMlJoUUNUSVprQ2FNdXE0aEo0Z2ItMDNGaHJCZ1ZVMjItOGJJdWNKeThYOHVYTWxkNnpEVlNPYVUtem9oQmxyc0tVTlBwTFlaQlpyMnE1b0h4UWlsOVlwcVlpTGs3NUdyU2xHeXpLSHdjOXF6MnFNdFR1VWxLQ0lRRmJXUUMtMGpudDIxcTJCeXY0RzB2dUhWTDRtTDgwZ3ZyV0E2NEVITklJaHA3c0Y5c1dQTHVLMmltdXZ4aVUzcWFuMnRhbVI3YlJwRjdhejQ5ckc4TEs4ZjZGT3F0RDVKaXg4REZjLTd1ODZjMlByZ0o4N2lnQ3NNcjYzaDVlclBRUnE4bEhDTkVwemlkdkhuenFWWmluM1QwcHkzN3JNRlN4S3puUnZKTFdMb1JnQTBNeHR1N3V1VnFIQzdzMW4ySENzQXJ2WU5MSmh5Q3g1ZmtKYU5oNTlqSkhrQ3ByYUc1WlZfaFVzYUdZYlo5TklJUU13SzVIQzVSSWx1Tkt5cDhxUGJYRG41RXdSQmFHb183eWFvLUMzS1BFV0FGZ29zQ3g0UEMwUXd2VXd2VS1lTHB3cGJtN29vajEwMUFiZXBZcmlUMUNteW41b3NSS3lEc0p3TmFTd0ZtQjY5amc1R0VKemhDb04wMzRxel93bXdFQTdQU19hMF9KUHcxUS1WMGF1bTE2LVVveFd0dWpTZ3U0YktfdGUyenRSSU1QbWpVTjBtZC1RNndreFpOQUp0aWtSM0hrbENyb3JCQVJVbFMzazhQQnhEeENsM2FfRW5jTm0tSGhIOEhsby1qLWFCcFBZRTZJOEdQZjVHQ3hHVElOV3ZlUkRDaGJUanNRRktqR0pjdWVFOFB3bWtnNjlkNnZpLWxyZkdJOHc5U0tESmdLQ2RvNlFvRjlMUFY1N2h5b2FuTy15MlRpdDJwZkZNSVM5b3prc3RzMkUtR2I3RDlMRnJITHJRY0pZcVJEMHFQWUdpb24wY28ybk1RQ2JtREVITGVrdWlrcHJubkR2RHRpbVdNUklXZzdhQTNsYlBFcU55S2hnR1B6YjZzd2JxOVI2X1N2QVJXSkJ0SVFDZ25hMHZzZWpSanU0OU5RcGh2TV9qbEh4N2YzVGRLQTFmY2JCNUV5alV6MTRodVlORThrQzVZNjl0cFpieGxIaG90U2ozTlJjY1VPSG1CdlNkVU9LdU9KN3RzV2hIRklDVUZZamFtN0V0RkppYVNPUXViSEJudExJd1VzazRiNnBNcVpvR1JpM3M5bGZlb2hCc1ZuY0tSaU13VEFaQS1mc2ljU080UjlmZE5PTE81eUxOdzhSQ2oxWnpMWUFjQ1YzemNKVWFnci16SnYtVFJaRFN4SWx1blVGWjRXQTZHRWdlX3VkR2VaeDhWcjhCcmZCdUdtMndTQzRocHI1aUlmSUZnbnFEc19GTG9OdmZDNlVsRHhsa0c0Q3ZvWG16SHpUUW94ZnhqOG9CTTQwWWNCeHNlbXJrM2RPWEFfeTY0RFdDSC1lUFoxdGlic1J6UW1QN2ZqYkFjNFVVTllSTVdyUWN4aGxtTWw3Y2dfXzNZeDVnWDZ1MkNRWTZZLTRnZEtEMmlFOGJCWTBLV2ZlcFQyTUJZQWQ5MnNoM3VJaUJBWUNROElKV1Y2QnJTZTJVUnkxNXJib3FXZFcya2E1d2NuOWo4d3VxS0NHSmRLSUp1Nkszc1Y4VVpKLWYxekVIMUUwRkdrOEdld1NEN24tYUZkejQwc1VvQ1Z1aDdEVWhhMVZTMlZieEp2dFlIOEFpT1pvVkZncVJNUGJ0dHVMWGlSeXZMdjRyTXJ2V3g0RWFTWG56NEx0OFJFMXRaYzZORDRCWE15SmV2TGhodTZFSFg2WC1KeV9oOFRVenctU1lvLWEyQnB0SnpaaG4xbkFUYS1WU3RtYjNla1I3cS1fUTJKbndjc1lpRXJpTmxnUUcySHQ4M1VRU3VzVjVxazhWdEVscDVQclVVc1hZU2hJWEdDOGJLdXdvaXIwVGY0RzBabmJYX1Z4Vm5iUTlocUMwbk52aUJLakx2Rjk2WFB6NWNUWXp4QlROZEU2elRPNEdaUU5sanlzQlRFSTVGc2FPOUFUWW1ETlF0Sks0Q1ZoV0wxYmlrcDExdUVOYXhvWUhYRk5aNFVwM0pWTVVjTG5fTkFrYlhrYW40LWotMU5yalJjMFg5ZHNHRExvZFFsTm5oWG43M2VlZGR4QnhRSzFXc3h6WklpRWhwajJXMUtpUmMwX25jTkkwRm1oeDRFMHFRcW56MjQ0Q3kzUEg0enA4dzVaQ0JkNTNIMmptM1lDSkVUU1F6TVBWNEZwR0tNR1BEWk44WGw5UjdqRFZxMF9tZ3RVaGRnb1BlRTAtR0FiZ00xcmxaNWhDNXJJQ1J4eFRYMFJLa2JRQkRNcDB6MzNVb0E2eUtnZ1ZwME04Umo3TnpERUxoQmpqc2NKM2lXbWhLWjFrTkhLRUVKRGstUUQ4ZFZqM2Z4U1M4bmN4ZFdlc3gxZWFQeWFMTVIwWEZxUXBNLUt5N2NVMHR2WmlqX1NrQ3J0MTNQRG5YaDRiX0NVbl9NZVJtWm1SS05PUmU2QlBjbTBSTkYtaHF6RGJ6NHBjS3k0ZkQ0Z21xOHNfd3RtRjF5cHRDUWRuY0lOR2RZZjNQSjBwRGxwZktzdVpZd2p4YVlzeFpaV1Y4anRCQy1HTk9PT2NBQlpYaTFGMzZRcHczdGU1YUxtckRzdWlGeWFNdUtfMkx5VHhDSzhOWWxvekp2REk1RTBFT3lCNUNLR3YyYlhpVnBNQ0ZULThQNGJhRHJYZHo3ZnJNSTdTNUlNZDh6XzVveGMtMFpWRFZPTzF4YUl1TzJweVFhZk1MVjloN2tZUUdFV3haSFg0a2dvQkZWYWl4VU1VaUpzUjFCY0ZjdXBoNjR6bTJuVUlaTVlsTTNhTVV1LUtWUXRHN21LTC02V1VDQjVObzRJbE9TWF9Tbk01UVQxdmw5RldoNzVlNGFWb1hSdkh6WlFWdV9mTTVqVWE2ZHVSSzIyYUp2ajRRdmVFMEM0dmxKRDJZNG5MUDVNZU9oZWo1UVpWcU05SGNTMUp0ZTdRSFpJWmlUa1pKUkNMcVg1TTZkTC1mUTk4aVpFa0I4RE8wMG5YTTNxWEJVSUhOYTdKNGZfZlhoQWoyam5XNUNhbDdxanpKNGlJS3ByRFFleE9YWmJDNVFVczNiTkltZ0tsLV9TRy1SY2M3YlFNbm0xamhYaHFXb3NFaUFkdnB4Y3N4WGpndXBMcHY0VTB5TDdwUDFDRWFpLVdUaEw0OWdBYlBoR1N4aVU1SGFDa1Q2dGM3eVZGbUJJaWR5RTJWVnY4OEFXcEFNOVRrUjlacFB4QTNYZnZ1aEpJQjR5S09DV3lFUzROb0VyWHYtd2gwc1Q2RU9MZ0MxSWNFdHVtWDJHQm9yZm5YZmRKWFR4RVFaa0RTWGtHX1JXMlUxdExCVEZSdF9sOEczLVFDQUxNbjNqdktzNm9NeENjZWdUbEVnMHpWV1cwOEFSRFN3dVhodkoycWJwdmRPRUN0RUxfR1U3dmRnbk1MSko1TXljYUJOVExQenBBWjgyekgtd3RYR2NlMC1Yb29XQWtqQXktdUM5TzZOaTU1c3BVZFBXdVdnOGxTS2hYcEt5RGFIMUd4bjRaUWNSR3pramY4NVhWU1V4UWIxMXp0WE1ybVdFOUFLang5bl9VX2lleE8wWmd5VGYwMkcwZXB5UEgwa0VCOVU2Vm9QeHVBaUIxbUEybVJQalFwRlRpZkZHTmdBS0hIQk5wUzlOVGZ1YXhOaGVkRndQWFVvSDNucTVZY0JZcmhPeEhVZFUyWHkwQVVkTGdMZVNoY21udVZHZlptclJvSnBjZ2hfdk52X2NWTmFfQnJ0SmZBMXFpOFFFbFZqTENYejBrWDFuT21KZWF2ZllVSjVQOXJFNng2UzVYdWtXT2ZEVVRzRU9vZWx1YXVSZ0lFS0RZNFZaNEMtaHlQSVFRSmxrd1Bmam9OajlLcFlPLW5uNUphOU1yd0plTGVTVDFyM2RNalZGT2I1NkpPUC1NdkNKRjRsdVB0UVBlNkdnMVpNUlJid29adWVzM1FTZXRlNk52NERROWpiMnJSTi1EcXpCMVBOSmsyTldTQXF4MmpMRko2Uzk3amE4ZFNpMmRDZjgzZG1HM1NXd2xTM18xT05ndGgtc3dRdWRuUGM0ZDh4RlkyMVRuaVV1TGxVYXZZNmt6Vmk4ZXVWVTRoZ2hzTWl5NDVSNEVkb3FPVjIxb1lGckM1TnFBTVpjcFAtU0lRcV94Xzd4bDZld0ExVVVza0s3RTFZaGx6cERfdnNBczRmXzJ1SkFYblAwSVlnS29FMmZaNEU4cmZ3M1R5bF9RSzFkQ0R3LU5uWjB2STY5OVpBN28xeWNjOVlVYU00WkpZaEVaTmNNdHowbUUtLUpSN080NnV5VHZjb3Jra0d1anVDOXlxN3BPaGoxSGFlZFpTUFlLRU0taV9OTDlsSUZTNlZ0bVNzeGliRzlxbmM3b2JZdW42Mi1EMXVXX280M01GZXQwOGZVLU9uRWdpcWxQZVQtSGp3dExuRVFmbl9YLVZMRU1kaWx6c281N18tOXVoUVFvODFOcHZzVEtLYUFaSnVaY0NYUzVKcWVkMm9KN0pYU09hb1lLZmhRSUVOY1VRRkdtTFAzaGNmVjVzSkNpYWNJZEM1cEx6YUxRVldmSmhNY0ktU3ROWTJqb1BnWm1PdlZLXzQ5ZlRuM21hRTVHV25kQlRyckExbGlYemNCaWZVZnBwTjZ4WC10aUdldWxIOEstR0FmY01EckZ3T3ZBSEtWa1cyaDI0V0Jjb2FCS21GM1ZpdGxENndWcUxLTVVpT3NGVGNpdXlWaFlsTlVEMzhPSy1BYUtLTnJNZ3pwMk84UnNUUEVSTFNZLVI2c1hzUWtuRURvWl9zS1FvWEdSNUJ1SGd5bXI1NzhYYS5NR2NaOVpacnY2NmRUV0tTSTVKUkVkVDZHcGw5ZTB2RnhpZHhNOWZQQXFOck5Eb3RvR2hua25MWkh4ZTgyaVNmb3lFLVJuTTR0Z215VV9zNnZRRUZBdw=="

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
TIMESTAMP_ID = "Y8XbcIu"


class URL:
    """Class used to store urls."""

    ENT_LOGIN = "https://ident.univ-amu.fr/cas/login"
    AMETICE = (
        "https://ident.univ-amu.fr/cas/login?service=https://"
        "ametice.univ-amu.fr/login/index.php?authCAS=CAS"
    )
    DIRECT_PLANNING = "https://ade-web-consult.univ-amu.fr/direct/gwtdirectplanning/DirectPlanningServiceProxy"
    ADE_LOGIN = "https://ident.univ-amu.fr/cas/login?service=http%3A%2F%2Fade-web-consult.univ-amu.fr%2Fdirect%2Fmyplanning.jsp"
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
    TIMELINE_URL = r"\"(.*)\""
    URL_HEX_VALUES = r"\\x([0-9a-fA-F]{2})"
    JS_VARIABLE = re.compile(r"M\.cfg = ([^;]*)")
    FILENAME_FORBIDDEN_CHARS = re.compile(r"(?u)[^-\w.]")
    SCHOOL_YEAR_REGEX = re.compile(r"\d+\-\d+")
