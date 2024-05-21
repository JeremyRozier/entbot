"""Module which contains the whole code to make the bot work
in the class AmeticeBot."""

import asyncio
import json
from time import time
import os
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from constants import RegexPatterns, Headers, Payload, URL, LIST_TREATED_TYPES
from filename_parser import (
    get_valid_filename,
    get_nb_origin_same_filename,
    get_filename_nb,
    get_file_extension,
)
from timestamp_functions import get_beg_school_year
import logging
from logging_config import display_message
from dotenv import load_dotenv


class AmeticeBot:
    """This class is a bot for Ametice website.
    It is meant to get all the files from all the courses
    of an account with its credentials."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        show_messages=False,
    ) -> None:
        self.show_messages = show_messages
        self.session = session
        self.username = username
        self.password = password
        self.dic_course_downloaded_cm = {}
        self.dic_course_school_year = {}
        self.session_key = ""

    async def post_for_data(self, url, payload) -> dict:
        """Post the provided payload and returns the useful content
        of the response request."""
        async with self.session.post(url, json=payload) as response:
            data = json.loads(bytes.decode(await response.read()))[0]["data"]
        return data

    async def post_for_topic_data(
        self, url, course_id, course_name
    ) -> tuple[str, dict]:
        """Post the payload matching the course_id provided
        to get the topics data related to the course_id."""
        topics_data = await self.post_for_data(url, Payload.topics(course_id))
        data = json.loads(topics_data)
        return {"course_name": course_name, "data": data}

    async def login(self, login_url=URL.LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes
        - return True if login succeeded.
        - return False if login failed."""
        async with self.session.post(
            login_url, data=Payload.login(self.username, self.password)
        ) as response:
            if (
                response.status == 401
                or len(self.password) == 0
                or len(self.username) == 0
            ):
                return False
            return True

    async def get_session_key(self) -> int:
        """Method to get the session key delivered
        by ametice once connected."""
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

    async def post_for_table_courses_data(self) -> dict:
        """Method to get the informations related
        to the courses the student follows."""
        table_courses_data = await self.post_for_data(
            URL.course(self.session_key), Payload.COURSES
        )
        return table_courses_data

    def get_classified_cm_id(self, list_topics) -> dict:
        dic_cm_id_topic = {}
        for dic_topic in list_topics:
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

    def get_cm_folder_path(self, course_name, topic_name):
        school_year = self.dic_course_school_year[course_name]
        folder_path = os.path.join(
            "Fichiers_Ametice",
            get_valid_filename(school_year),
            get_valid_filename(course_name),
            get_valid_filename(topic_name),
        )
        return folder_path

    async def download_file(
        self, resource_url, resource_type, folder_path, filename
    ):
        async with self.session.get(resource_url) as response:
            file_url = str(response.url)
            file_content_type = response.content_type
            extension = get_file_extension(
                file_url, file_content_type, resource_type
            )
            filename_nb = get_filename_nb(folder_path, filename)
            os.makedirs(folder_path, exist_ok=True)
            if extension == ".txt":
                async with aiofiles.open(
                    f"{folder_path}/{filename}{extension}", mode="w"
                ) as file:
                    await file.write(file_url)
            else:
                async with aiofiles.open(
                    f"{folder_path}/{filename_nb}{extension}", mode="wb"
                ) as file:
                    async for chunk in response.content.iter_chunked(1024):
                        await file.write(chunk)

        if self.show_messages:
            self.callback_download_file(folder_path)

    def callback_download_file(self, folder_path):
        list_folders = folder_path.split("/")
        course_name = list_folders[-2]
        self.dic_course_downloaded_cm[course_name] -= 1
        if self.dic_course_downloaded_cm[course_name] == 0:
            display_message(
                f"Le cours '{course_name}' a été téléchargé avec succès."
            )

    def get_resource_type(self, url):
        return RegexPatterns.RESOURCE_TYPE.search(url).group(1)

    def get_resource_url(self, resource_type, url, resource_id):
        """Get the url pointing to the resource with its type"""
        if resource_type == "folder":
            resource_url = URL.folder(resource_id)

        else:
            resource_url = f"{url}&redirect=1"

        return resource_url

    async def download_all_documents(self):
        """Method to download all the documents
        from the Ametice account the session is
        connected to.
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
        display_message("Connecté.", self.show_messages)
        self.session_key = await self.get_session_key()
        display_message("Clé de session Ametice obtenue.", self.show_messages)
        display_message("Téléchargement des cours...", self.show_messages)
        deb = time()

        table_courses = (await self.post_for_table_courses_data())["courses"]
        list_tasks_topics = []
        for dic_course in table_courses:
            course_name = get_valid_filename(dic_course["fullname"])
            course_id = dic_course["id"]
            list_tasks_topics.append(
                asyncio.create_task(
                    self.post_for_topic_data(
                        URL.topics(self.session_key),
                        course_id,
                        course_name,
                    )
                )
            )
            start_date_timestamp = dic_course["startdate"]
            beg_school_year = get_beg_school_year(start_date_timestamp)
            self.dic_course_school_year[course_name] = (
                f"{beg_school_year}-{beg_school_year+1}"
            )

        table_topics = await asyncio.gather(*list_tasks_topics)
        list_tasks = []
        for dic_topic in table_topics:
            table_cms = dic_topic["data"]["cm"]
            # list_sections = dic_topic["data"]["course"]["sectionlist"]
            dic_cm_id_topic = self.get_classified_cm_id(
                list_topics=dic_topic["data"]["section"]
            )
            course_name = dic_topic["course_name"]
            self.dic_course_downloaded_cm[course_name] = len(table_cms)
            for dic_cm in table_cms:
                topic_name = dic_cm_id_topic[dic_cm["id"]]
                folder_path = self.get_cm_folder_path(
                    course_name,
                    topic_name,
                )
                if "url" not in dic_cm:
                    self.callback_download_file(folder_path)
                    continue

                resource_type = self.get_resource_type(dic_cm["url"])
                if resource_type not in LIST_TREATED_TYPES:
                    self.callback_download_file(folder_path)
                    continue

                resource_url = self.get_resource_url(
                    resource_type, dic_cm["url"], dic_cm["id"]
                )

                filename = get_valid_filename(dic_cm["name"])
                task = asyncio.create_task(
                    self.download_file(
                        resource_url, resource_type, folder_path, filename
                    ),
                )

                list_tasks.append(task)
        await asyncio.gather(*list_tasks)
        display_message(
            "Téléchargement terminé en" f" {round(time() - deb, 1)} secondes.",
            self.show_messages,
        )


async def main():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True, limit=50),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, username, password, show_messages=True)
        await bot.download_all_documents()
        # await bot.login()
        # async with bot.session.get(
        #     "https://ametice.univ-amu.fr/mod/label/label.php/?id=3457106&redirect=1",
        #     allow_redirects=False,
        # ) as response:
        #     print(await response.read())


if __name__ == "__main__":
    asyncio.run(main())
