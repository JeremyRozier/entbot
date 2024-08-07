"""File which contains the whole code to make the bot work
in the class AmeticeBot.
"""

import asyncio
import json
import os
import aiohttp
from bs4 import BeautifulSoup

from entbot.bots.ent_bot import ENTBot
from entbot.constants import (
    RegexPatterns,
    Headers,
    Payload,
    URL,
    TUPLE_TREATED_MODULES,
)
from entbot.tools.dic_operations import get_classified_cm_id
from entbot.tools.filename_parser import (
    get_cm_folder_path,
    get_valid_filename,
    get_filename_nb,
    get_file_extension,
    get_school_year,
    write_binary_with_error_handling,
    write_with_error_handling,
    turn_cwd_to_execution_dir,
)
from entbot.tools.logging_config import display_message


class AmeticeBot(ENTBot):
    """This class is a bot for Ametice website.
    It is meant to get all the files from all the courses
    of an account with its credentials.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        show_messages=False,
        max_concurrent_requests=30,
    ) -> None:
        """Constructor of AmeticeBot.

        Args:
            - session (aiohttp.ClientSession): The aiohttp session which will be
            used throughout the whole lifetime of the bot.

            - username (str): The username to sign in on the Aix Marseille website.

            - password (str): The password to sign in on the Aix Marseille website.

            - show_messages (bool): Indicates whether logs are showed in the terminal or not.
            True : logs are showed.
            False : logs are hidden.

            - max_concurrent_requests (int): The number we pass in parameter of
            the class asyncio.Semaphore, that, in this program, is used to indicate
            how many requests, at most, can be made concurrently to avoid
            unintentional DDOS attacks.
            The default value, 30, is fine-tuned.

        Returns: None
        """
        super().__init__(session, username, password, show_messages)
        self.sephamore_requests = asyncio.Semaphore(max_concurrent_requests)
        self.dic_course_downloaded_cm = {}
        self.dic_course_school_year = {}
        self.session_key = ""

    async def post_for_data(self, url: str, payload: dict) -> list[dict]:
        """Post the provided payload and returns the useful content
        of the response request.

        Args:
            - url (str): The url used in the post request.
            - payload (dict): The payload provided in the post request.

        Returns list[dict]: A table containing the useful content
        of the response request.
        """
        async with self.session.post(url, json=payload) as response:
            data = json.loads(bytes.decode(await response.read()))[0]["data"]
        return data

    async def post_for_topic_data(
        self, url: str, course_id: str, course_name
    ) -> dict:
        """Post the payload matching the provided course_id
        to get the topics data related to the course_id.

        Args:
            - url (str): The url used in the post request.
            - course_id (str): The course id associated to the course module
            we want the topics from.
            - course_name (str): The course name associated to the course
            we want the topics from.

        Returns (dict): A dictionary with 2 keys :
            - "course_name" associated to the course name
            value specified in the arguments.
            - "data" asspciated to the dictionary returned by
            the request.
        """
        topics_data = await self.post_for_data(url, Payload.topics(course_id))
        data = json.loads(topics_data)
        return {"course_name": course_name, "data": data}

    async def load_ametice_session(self, url_ametice=URL.AMETICE):
        """Method to get the session key and store it
        in the session_key attribute

        Returns (bool):
            - True if the operation succeeded.
            - False if the operation failed.
        """
        display_message(
            "Obtention de la clé de session Ametice...", self.show_messages
        )
        self.session_key = await self.get_session_key(url_ametice)
        if len(self.session_key) > 0:
            display_message(
                "Clé de session Ametice obtenue.", self.show_messages
            )
            return True
        return False

    async def login(self, login_url=URL.ENT_LOGIN):
        """Method to login with the credentials given in the class attributes.
        This method overrides the one in BaseBot to use it and then get
        the session key for Ametice.

        Args:
            - login_url (str): The url of the service hosting Moodle.
            The login page of Aix-Marseille Universités is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        if not self.is_logged_in_ent:
            if await super().login(login_url):
                return await self.load_ametice_session()

        return False

    async def get_session_key(self, url_ametice=URL.AMETICE) -> str:
        """Method to get the session key delivered
        by ametice once connected.

        Returns (str): The key created by Ametice
        for the session we made."""
        async with self.session.get(url_ametice) as response:
            content = await response.read()
            soup = BeautifulSoup(bytes.decode(content), features="html.parser")
            data = soup.find_all("script")[1].string
            string_js_variable = RegexPatterns.JS_VARIABLE.search(data).group(
                1
            )
            dic_js_variable = json.loads(string_js_variable)
            session_key = dic_js_variable["sesskey"]
            return session_key

    async def post_for_table_courses_data(self) -> list[dict]:
        """Method to get the courses data related
        to the courses the student follows.

        Returns (list[dict]): A dictionary containing all the data
        related to the courses the student follows.
        """
        table_courses_data = await self.post_for_data(
            URL.course(self.session_key), Payload.COURSES
        )
        return table_courses_data

    async def download_file_with_error_handling(
        self,
        course_id,
        course_name,
        cm_url: str,
        cm_module: str,
        folder_path: str,
        filename: str,
        ssl=True,
    ) -> None:
        """Encapsulates the download_file method with a try and catch block
        for avoiding the aiohttp.ClientConnectorError error which was occurring randomly.
        This way the encapsulation is cleaner than if it were made directly
        in the download_file method.

        Args:
            - course_id (str): The course id associated to the course module.
            - cm_url (str): The url pointing directly to the resource.
            - cm_module (str): The type of the resource (see TUPLE_TREATED_TYPES).
            - folder_path (str): The path of folders where the file will be downloaded.
            - filename (str): The filename under which the file will be downloaded.
            - ssl (bool): Indicates whether SSL is activated or not for the request
            necessary to download the current file

        Returns None
        """
        has_error = True
        while has_error:
            try:
                async with self.sephamore_requests:
                    await self.download_file(
                        cm_url, cm_module, folder_path, filename, ssl
                    )
            except aiohttp.ClientConnectorCertificateError:
                ssl = False
                continue
            except aiohttp.ClientConnectorError:
                continue
            except aiohttp.ClientPayloadError:
                continue

            has_error = False

        if self.show_messages:
            self.callback_download_file(course_id, course_name)

    async def download_file(
        self, cm_url, cm_module, folder_path, filename, ssl=True
    ) -> None:
        """Downloads the file stored at the url : cm_url under a filename and
        in a specified location given in arguments.

        Args:
            - cm_url (str): The url pointing directly to the resource.
            - cm_module (str): The type of the resource (see TUPLE_TREATED_TYPES).
            - folder_path (str): The path of folders where the file will be downloaded.
            - filename (str): The filename under which the file will be downloaded.
            - ssl (bool): Indicates whether SSL is activated or not for the request
            necessary to download the current file

        Returns None
        """
        async with self.session.get(cm_url, ssl=ssl) as response:
            file_url = str(response.url)
            file_content_type = response.content_type
            extension = get_file_extension(
                file_url, file_content_type, cm_module
            )
            filename_nb = get_filename_nb(folder_path, filename)
            os.makedirs(folder_path, exist_ok=True)
            if extension == "":
                absolute_path = os.path.abspath(
                    f"{folder_path}/{filename_nb}.txt"
                )
                await write_with_error_handling(
                    absolute_path,
                    content_to_write=file_url,
                )
            else:
                absolute_path = os.path.abspath(
                    f"{folder_path}/{filename_nb}{extension}"
                )
                await write_binary_with_error_handling(
                    absolute_path,
                    content_to_write=response,
                )

    def callback_download_file(self, course_id, course_name) -> None:
        """Updates the self.dic_course_downloaded_cm to know
        in real time which courses have been successfully downloaded.

        Args:
            - course_id (str): The id of the course associated to the downloaded
            course module.
            - course_name (str): The name of the course associated to the downloaded
            course module.

        Returns: None
        """
        self.dic_course_downloaded_cm[course_id] -= 1
        if self.dic_course_downloaded_cm[course_id] == 0:
            display_message(
                f"Le cours '{course_name}' a été téléchargé avec succès."
            )

    async def download_all_files(self) -> None:
        """Method to download all the files
        from the Ametice account the session is
        connected to.

        Returns None
        """
        table_courses = (await self.post_for_table_courses_data())["courses"]
        list_tasks_topics = []
        for dic_course in table_courses:
            course_name = dic_course["fullname"]
            course_id = str(dic_course["id"])
            task_topics = asyncio.create_task(
                self.post_for_topic_data(
                    URL.topics(self.session_key),
                    course_id,
                    course_name,
                )
            )
            list_tasks_topics.append(task_topics)
            start_date_timestamp = dic_course["startdate"]
            school_year = get_school_year(course_name, start_date_timestamp)
            self.dic_course_school_year[course_id] = school_year
        table_topics_data = await asyncio.gather(*list_tasks_topics)

        list_tasks_download_file = []
        for dic_topic_data in table_topics_data:
            course_name = dic_topic_data["course_name"]
            course_id = dic_topic_data["data"]["course"]["id"]
            table_cms = dic_topic_data["data"]["cm"]
            dic_cm_id_topic = get_classified_cm_id(
                table_topics=dic_topic_data["data"]["section"]
            )
            self.dic_course_downloaded_cm[course_id] = len(table_cms)
            for dic_cm in table_cms:
                topic_name = dic_cm_id_topic[dic_cm["id"]]
                folder_path = get_cm_folder_path(
                    school_year=self.dic_course_school_year[course_id],
                    course_name=course_name,
                    topic_name=topic_name,
                )

                cm_module = dic_cm["module"]
                if cm_module not in TUPLE_TREATED_MODULES:
                    if self.show_messages:
                        self.callback_download_file(course_id, course_name)
                    continue

                cm_url = URL.element(cm_id=dic_cm["id"], cm_module=cm_module)
                filename = get_valid_filename(dic_cm["name"])
                task_download_file = asyncio.create_task(
                    self.download_file_with_error_handling(
                        course_id,
                        course_name,
                        cm_url,
                        cm_module,
                        folder_path,
                        filename,
                    ),
                )
                list_tasks_download_file.append(task_download_file)

        await asyncio.gather(*list_tasks_download_file)


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
        bot = AmeticeBot(session, username, password, show_messages=True)
        await bot.login()
        await bot.download_all_files()


if __name__ == "__main__":
    turn_cwd_to_execution_dir()
    asyncio.run(main())
