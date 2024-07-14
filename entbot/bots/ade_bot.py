import asyncio
from datetime import datetime
import os
import re
from typing import List
import aiohttp
from entbot.bots.ent_bot import ENTBot
from entbot.constants import (
    URL,
    GWTPayload,
    Headers,
    RegexPatterns,
    TIMESTAMP_ID,
)
from entbot.tools.timestamp_functions import (
    get_base64_from_datetime,
)


class ADEBot(ENTBot):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        session_id=TIMESTAMP_ID,
        show_messages=False,
    ) -> None:
        super().__init__(session, username, password, show_messages)
        self.session_id = session_id
        self.gwt_payload = GWTPayload(self.session_id)
        self.is_logged_in_ade = False

    async def login_ade(self, url_ade_login=URL.ADE_LOGIN):
        """Method to get the session key and store it
        in the session_key attribute

        Returns (bool):
            - True if the operation succeeded.
            - False if the operation failed.
        """
        await self.session.get(url_ade_login)
        login_resp_object = await self.session.post(
            URL.MY_PLANNING,
            data=self.gwt_payload.ade_login(),
            headers=Headers.GWT_HEADERS,
        )
        self.is_logged_in_ade = (
            self.username in (await login_resp_object.read()).decode()
        )
        if self.is_logged_in_ade:
            await self.session.post(
                URL.WEB_CLIENT,
                data=self.gwt_payload.load_project(),
                headers=Headers.GWT_HEADERS,
            )
        return self.is_logged_in_ade

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
        if not self.is_logged_in_ent:
            if await super().login(login_url):
                return await self.login_ade(url_ade_login)
            else:
                return False
        else:
            return await self.login_ade(url_ade_login)

    async def get_tree_from_name(self, name: str) -> List[str]:
        """Get the"""
        response_object = await self.session.post(
            URL.DIRECT_PLANNING,
            data=self.gwt_payload.tree_ids(name),
            headers=Headers.GWT_HEADERS,
        )
        response = bytes.decode(await response_object.read())
        list_courses_id_name = re.findall(RegexPatterns.COURSE_ID, response)
        return list_courses_id_name

    async def get_semester_id(self, semester: int) -> str:
        return (await self.get_tree_from_name(f"{semester} MPCI"))[-1]

    async def get_groups_from_semester(
        self, semester_number: int
    ) -> list[str]:
        semester_id = await self.get_semester_id(semester_number)
        response_object = await self.session.post(
            URL.DIRECT_PLANNING,
            data=self.gwt_payload.children_from_semester(
                semester_id, semester_number
            ),
            headers=Headers.GWT_HEADERS,
        )
        response = bytes.decode(await response_object.read())
        list_courses_id_name = RegexPatterns.COURSE_ID_NAME.findall(response)
        return list_courses_id_name

    async def get_group_name_id(self, semester_number: int, group_number: int):
        list_courses_id = await self.get_groups_from_semester(semester_number)
        if len(list_courses_id) < group_number:
            raise ValueError(
                f"{group_number} group is not available in {semester_number}"
            )
        return list_courses_id[group_number]

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


async def main():
    from dotenv import load_dotenv

    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        ade_bot = ADEBot(
            session,
            username,
            password,
        )
        await ade_bot.login()


if __name__ == "__main__":
    asyncio.run(main())
