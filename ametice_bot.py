"""Module which contains the whole code to make the bot work
in the class AmeticeBot."""

import asyncio
import json
from time import time
import os
from urllib.parse import urlparse
from mimetypes import guess_extension
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from constants import RegexPatterns, Headers, Payload, URL, LIST_TREATED_TYPES
from filename_parser import get_valid_filename, get_nb_origin_same_filename
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
        self.dic_course_topics = {}
        self.session_key = ""

    async def _get_binary_content(self, url):
        has_connection_error = True
        while has_connection_error:
            try:
                response = await self.session.get(url)
            except aiohttp.ClientConnectionError:
                response = await self.session.get(url)
                continue

            has_connection_error = False

        has_payload_error = True
        while has_payload_error:
            try:
                binary_content = await response.read()
            except aiohttp.client_exceptions.ClientPayloadError:
                response = await self.session.get(url)
                continue
            has_payload_error = False

        return {"response": response, "binary_content": binary_content}

    async def _get_content_file_save(self, **dic_args):
        dic_content = await self._get_binary_content(dic_args["resource_url"])
        await self.save_files(
            binary_content=dic_content["binary_content"],
            file_url=str(dic_content["response"].url),
            resource_type=dic_args["resource_type"],
            content_type=dic_content["response"].content_type,
            folder_path=dic_args["folder_path"],
            filename=dic_args["filename"],
        )

    async def _get_data(self, url, payload) -> dict:
        """Post the provided payload and returns the useful content
        of the response request."""
        request = await self.session.post(url, json=payload)
        data = json.loads(bytes.decode(await request.read()))[0]["data"]
        return data

    async def _get_topics_data(
        self, url, course_id, course_name
    ) -> tuple[str, dict]:
        """Post the payload matching the course_id provided
        to get the topics data related to the course_id."""
        topics_data = await self._get_data(url, Payload.topics(course_id))
        data = json.loads(topics_data)
        return {"course_name": course_name, "data": data}

    async def login(self, login_url=URL.LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes
        - return True if login succeeded.
        - return False if login failed."""
        resp_login = await self.session.post(
            login_url, data=Payload.login(self.username, self.password)
        )
        if (
            resp_login.status == 401
            or len(self.password) == 0
            or len(self.username) == 0
        ):
            return False
        return True

    async def get_session_key(self) -> int:
        """Method to get the session key delivered
        by ametice once connected."""
        resp_my = await self.session.get(URL.AMETICE)
        content = await resp_my.read()
        soup = BeautifulSoup(bytes.decode(content), features="html.parser")
        data = soup.find_all("script")[1].string
        string_js_variable = RegexPatterns.JS_VARIABLE.search(data).group(1)
        dic_js_variable = json.loads(string_js_variable)
        sesskey = dic_js_variable["sesskey"]

        return sesskey

    async def get_table_courses_data(self) -> dict:
        """Method to get the informations related
        to the courses the student follows."""
        table_courses_data = await self._get_data(
            URL.course(self.session_key), Payload.COURSES
        )
        return table_courses_data

    async def get_table_topics_data(self, courses_info) -> list[dict]:
        """Method to get the data related
        to the topics of the courses the student follows."""
        url_get_topics = URL.topics(self.session_key)
        list_tasks = []
        for course_info in courses_info:
            current_course_name = course_info["fullname"]
            current_course_id = course_info["id"]
            list_tasks.append(
                asyncio.create_task(
                    self._get_topics_data(
                        url_get_topics, current_course_id, current_course_name
                    )
                )
            )
        return await asyncio.gather(*list_tasks)

    async def save_files(self, **dic_args):
        """Save a file by creating necessary folders."""
        filename = dic_args["filename"]
        folder_path = dic_args["folder_path"]

        parsed = urlparse(dic_args["file_url"])
        extension = os.path.splitext(parsed.path)[1]
        if len(extension) == 0:
            extension = guess_extension(dic_args["content_type"])
            if extension is None:
                extension = ""

        if os.path.exists(dic_args["folder_path"]):
            nb_same_filename = get_nb_origin_same_filename(
                folder_path, filename
            )
            if nb_same_filename > 0:
                filename = f"{filename}_{nb_same_filename}"

        os.makedirs(folder_path, exist_ok=True)
        if dic_args["resource_type"] == "url":
            extension = ".txt"
            writing_mode = "w"
            content_key = "file_url"

        else:
            if dic_args["resource_type"] == "folder":
                extension = ".zip"
            writing_mode = "wb"
            content_key = "binary_content"

        async with aiofiles.open(
            f"{folder_path}/{filename}{extension}", mode=writing_mode
        ) as file:
            await file.write(dic_args[content_key])

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

    def create_download_task(
        self, resource_type, dic_topic_info, dic_cm_id_topic, dic_cm
    ):
        resource_url = self.get_resource_url(
            resource_type, dic_cm["url"], dic_cm["id"]
        )

        topic_name = dic_cm_id_topic[dic_cm["id"]]
        filename = dic_cm["name"]
        fullname = dic_topic_info["course_name"]
        school_year = RegexPatterns.SCHOOL_YEAR_REGEX.search(fullname).group(0)
        folder_path = os.path.join(
            "Fichiers_Ametice",
            get_valid_filename(school_year),
            get_valid_filename(fullname),
            get_valid_filename(topic_name),
        )

        return asyncio.create_task(
            self._get_content_file_save(
                resource_url=resource_url,
                resource_type=resource_type,
                folder_path=folder_path,
                filename=get_valid_filename(filename),
            )
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
        display_message(
            "Récupération et téléchargement des cours...", self.show_messages
        )
        deb = time()
        table_courses_data = (await self.get_table_courses_data())["courses"]
        table_topics_data = await self.get_table_topics_data(
            table_courses_data
        )
        list_tasks = []

        for dic_topic_info in table_topics_data:
            table_cms = dic_topic_info["data"]["cm"]
            dic_cm_id_topic = self.get_classified_cm_id(
                list_topics=dic_topic_info["data"]["section"]
            )

            for dic_cm in table_cms:
                if "url" not in dic_cm:
                    continue
                resource_type = self.get_resource_type(dic_cm["url"])

                if resource_type not in LIST_TREATED_TYPES:
                    continue

                task = self.create_download_task(
                    resource_type, dic_topic_info, dic_cm_id_topic, dic_cm
                )

                if task is None:
                    continue

                list_tasks.append(task)

        await asyncio.gather(*list_tasks)
        display_message(
            "Téléchargement terminé en" f" {round(time() - deb, 1)} secondes."
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


if __name__ == "__main__":
    asyncio.run(main())
