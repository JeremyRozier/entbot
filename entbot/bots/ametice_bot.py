"""File which contains the whole code to make the bot work
in the class AmeticeBot.
"""

import asyncio
import json
from time import time
import os
import logging
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from constants import (
    RegexPatterns,
    Headers,
    Payload,
    URL,
    TUPLE_TREATED_MODULES,
)
from tools.filename_parser import (
    get_valid_filename,
    get_filename_nb,
    get_file_extension,
    get_school_year,
)
from tools.logging_config import display_message


class AmeticeBot:
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

            - show_messages (bool): Indicates if logs are showed in the terminal.
            True : logs are showed.
            False : logs are hidden.

            - max_concurrent_requests (int): The number we pass in parameter of
            the class asyncio.Semaphore, that, in this program, is used to indicate
            how many requests, at most, can be made concurrently to avoid
            unintentional DDOS attacks.
            The default value, 30, is fine-tuned.

        Returns: None
        """
        self.show_messages = show_messages
        self.session = session
        self.username = username
        self.password = password
        self.dic_course_downloaded_cm = {}
        self.dic_course_school_year = {}
        self.session_key = ""
        self.sephamore_requests = asyncio.Semaphore(max_concurrent_requests)

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
        """Post the payload matching the course_id provided
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

    async def login(self, login_url=URL.LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes

        Args:
            - login_url (str): The url of the service hosting Moodle.
            The login page of Aix-Marseille Universités is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        async with self.session.post(
            login_url, data=Payload.login(self.username, self.password)
        ) as response:
            if (
                response.status == 401
                or len(self.password) == 0
                or len(self.username) == 0
            ):
                return False

        self.session_key = await self.get_session_key()
        return True

    async def get_session_key(self) -> str:
        """Method to get the session key delivered
        by ametice once connected.

        Returns (str): The key created by Ametice
        for the session we made."""
        async with self.session.get(URL.AMETICE) as response:
            content = await response.read()
            soup = BeautifulSoup(bytes.decode(content), features="html.parser")
            data = soup.find_all("script")[1].string
            string_js_variable = RegexPatterns.JS_VARIABLE.search(data).group(
                1
            )
            dic_js_variable = json.loads(string_js_variable)
            sesskey = dic_js_variable["sesskey"]
            return sesskey

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

    def get_classified_cm_id(self, table_topics: list[dict]) -> dict[str, str]:
        """Creates a dictionary that maps the course module ids
        to the topic names associated.

        Args:
            - table_topics (list[dict]): The table containing
            all the data of the followed topics.

        Returns (dict): A dictionary that maps the course module ids
        to the topic names associated.
        """
        dic_cm_id_topic = {}
        for dic_topic in table_topics:
            topic_name = dic_topic["title"]
            list_cm_id = dic_topic["cmlist"]
            dic_cm_id_topic.update(
                dict(
                    zip(
                        list_cm_id,
                        [topic_name for i in range(len(list_cm_id))],
                    )
                )
            )
        return dic_cm_id_topic

    def get_cm_folder_path(
        self, course_id: str, course_name: str, topic_name: str
    ) -> str:
        """Creates a folder path for the given
        course name and topic name.

        Args:
            course_name (str): The course name used for making the path.
            topic_name (str): The topic name used for making the path.

        Returns (str): The folder path for the given arguments.
        """
        school_year = self.dic_course_school_year[course_id]
        folder_path = os.path.join(
            "Fichiers_Ametice",
            get_valid_filename(school_year),
            get_valid_filename(course_name),
            get_valid_filename(topic_name),
        )
        return folder_path

    async def download_file_with_error_handling(
        self,
        course_id,
        course_name,
        cm_url: str,
        cm_module: str,
        folder_path: str,
        filename: str,
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

        Returns None
        """
        has_error = True
        while has_error:
            try:
                async with self.sephamore_requests:
                    await self.download_file(
                        cm_url, cm_module, folder_path, filename
                    )
            except aiohttp.ClientConnectorError:
                continue
            except aiohttp.ClientPayloadError:
                continue

            has_error = False

        if self.show_messages:
            self.callback_download_file(course_id, course_name)

    async def download_file(
        self, cm_url, cm_module, folder_path, filename
    ) -> None:
        """Downloads the file stored at the url : cm_url under a filename and
        in a specified location given in arguments.

        Args:
            - cm_url (str): The url pointing directly to the resource.
            - cm_module (str): The type of the resource (see TUPLE_TREATED_TYPES).
            - folder_path (str): The path of folders where the file will be downloaded.
            - filename (str): The filename under which the file will be downloaded.

        Returns None
        """
        async with self.session.get(cm_url) as response:
            file_url = str(response.url)
            file_content_type = response.content_type
            extension = get_file_extension(
                file_url, file_content_type, cm_module
            )
            filename_nb = get_filename_nb(folder_path, filename)
            os.makedirs(folder_path, exist_ok=True)
            if extension == "":
                async with aiofiles.open(
                    f"{folder_path}/{filename_nb}.txt", mode="w"
                ) as file:
                    await file.write(file_url)
            else:
                async with aiofiles.open(
                    f"{folder_path}/{filename_nb}{extension}", mode="wb"
                ) as file:
                    async for chunk in response.content.iter_chunked(1024):
                        await file.write(chunk)

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
        display_message("Connexion...", self.show_messages)
        is_logged = await self.login()
        if not is_logged:
            display_message(
                "Le mot de passe ou l'identifiant est incorrect.",
                self.show_messages,
                logging.ERROR,
            )
            return
        display_message(
            "Connecté et clé de session Ametice obtenue.", self.show_messages
        )
        display_message("Téléchargement des cours...", self.show_messages)
        deb = time()

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
        table_topics = await asyncio.gather(*list_tasks_topics)

        list_tasks_download_file = []
        for dic_topic in table_topics:
            course_name = dic_topic["course_name"]
            course_id = dic_topic["data"]["course"]["id"]
            table_cms = dic_topic["data"]["cm"]
            dic_cm_id_topic = self.get_classified_cm_id(
                table_topics=dic_topic["data"]["section"]
            )
            self.dic_course_downloaded_cm[course_id] = len(table_cms)
            for dic_cm in table_cms:
                topic_name = dic_cm_id_topic[dic_cm["id"]]
                folder_path = self.get_cm_folder_path(
                    course_id,
                    course_name,
                    topic_name,
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
        display_message(
            "Téléchargement terminé en" f" {round(time() - deb, 1)} secondes.",
            self.show_messages,
        )


async def main():
    from dotenv import load_dotenv # pylint: disable=C0415:import-outside-toplevel

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
        await bot.download_all_files()


if __name__ == "__main__":
    asyncio.run(main())
