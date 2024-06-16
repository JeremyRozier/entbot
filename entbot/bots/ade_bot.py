from datetime import datetime
import re
from typing import List, Dict
import aiohttp
from entbot.bots.base import BaseBot
from entbot.constants import (
    URL,
    GWTPayload,
    Headers,
    RegexPatterns,
    TIMESTAMP_ID,
)
from entbot.tools.timestamp_functions import (
    get_base64_from_datetime,
    long_to_base64,
)


class ADEBot(BaseBot):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        session_id=TIMESTAMP_ID,
    ) -> None:
        super().__init__(session, username, password)
        self.session_id = session_id
        self.gwt_payload = GWTPayload(self.session_id)

    async def login(
        self, login_url=URL.ENT_LOGIN, url_ade_login=URL.ADE_LOGIN
    ) -> bool:
        """Method to login with the
        credentials given in the class attributes

        Args:
            - login_url (str): The url of the service hosting Moodle.
            The login page of Aix-Marseille Universités is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        if await super().login(login_url):
            await self.session.get(url_ade_login)
            await self.session.post(
                URL.MY_PLANNING,
                data=self.gwt_payload.ade_login(),
                headers=Headers.GWT_HEADERS,
            )
            await self.session.post(
                URL.WEB_CLIENT,
                data=self.gwt_payload.load_project(),
                headers=Headers.GWT_HEADERS,
            )
            return True
        return False

    async def get_tree_ids_from_name(self, name: str) -> List[str]:
        """Get the"""
        response_object = await self.session.post(
            URL.DIRECT_PLANNING,
            data=self.gwt_payload.tree_ids(name),
            headers=Headers.GWT_HEADERS,
        )
        response = bytes.decode(await response_object.read())
        list_courses_id = re.findall(RegexPatterns.COURSE_ID, response)
        return list_courses_id

    async def get_semester_id(self, semester: int) -> str:
        return (await self.get_tree_ids_from_name(f"{semester} MPCI"))[-1]

    async def get_group_id(self, semester: int, group: int):
        semester_id = await self.get_semester_id(semester)
        response_object = await self.session.post(
            URL.DIRECT_PLANNING,
            data=self.gwt_payload.children_from_semester(
                semester_id, semester
            ),
            headers=Headers.GWT_HEADERS,
        )
        response = bytes.decode(await response_object.read())
        list_courses_id = re.findall(RegexPatterns.COURSE_ID, response)
        if len(list_courses_id) < group:
            raise ValueError(f"{group} group is not available in {semester}")
        return list_courses_id[group]

    async def get_timeline_url(
        self,
        course_id: str,
        beg_date: datetime,
        end_date: datetime,
    ) -> str:
        beg_base64 = get_base64_from_datetime(beg_date)
        end_base64 = get_base64_from_datetime(end_date)
        response_object = await self.session.post(
            URL.CORE_PLANNING,
            data=self.gwt_payload.timeline_url(
                course_id,
                beg_base64,
                end_base64,
            ),
            headers=Headers.GWT_HEADERS,
        )
        response = bytes.decode(await response_object.read())
        encoded_url = re.search(RegexPatterns.TIMELINE_URL, response).group(1)
        url = re.sub(
            RegexPatterns.URL_HEX_VALUES,
            lambda match: chr(int(match.group(1), 16)),
            encoded_url,
        )
        return url
