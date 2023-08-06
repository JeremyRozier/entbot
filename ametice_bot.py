"""Module which contains the whole code to make the bot work
in the class AmeticeBot."""

import asyncio
import json
import unicodedata
from time import time
import os
import re
from urllib.parse import urlparse
from mimetypes import guess_extension, guess_type
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from constants import DIC_NAME_REGEX, HEADERS, Payload, URL


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
    valid_filename = re.sub(r"(?u)[^-\w.]", "", valid_filename)
    valid_filename = unicodedata.normalize("NFKD", valid_filename)
    valid_filename = "".join(
        [c for c in valid_filename if not unicodedata.combining(c)]
    )
    return valid_filename


def get_nb_origin_same_filename(folder_path, filename):
    """
    Returns for a given filename the number of files
    already saved which match with this pattern
    rf{filename}(_d+)?
    or 0 if there aren't any conflicts.
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


class AmeticeBot:
    """This class is a bot for Ametice website.
    It is meant to get all the files from all the courses
    of an account with its credentials."""

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.dic_course_topics = {}
        self.sess_key = ""
        self.session = "aiohttp.ClientSession()"

    async def _get_content(self, name, url) -> tuple[str, str]:
        page = await self.session.get(url)
        content = await page.read()
        return (name, content)

    async def _get_content_file_save(self, **dic_args):
        file_url = dic_args["file_url"]
        resource_type = dic_args["resource_type"]
        folder_path = dic_args["folder_path"]
        filename = dic_args["filename"]

        has_connection_error = True
        while has_connection_error:
            try:
                page = await self.session.get(file_url)
            except aiohttp.ClientConnectionError:
                page = await self.session.get(file_url)
                continue

            has_connection_error = False

        has_payload_error = True
        while has_payload_error:
            try:
                binary_content = await page.read()
            except aiohttp.client_exceptions.ClientPayloadError:
                page = await self.session.get(file_url)
                continue
            has_payload_error = False

        await self._save_files(
            binary_content=binary_content,
            file_url=str(page.url),
            resource_type=resource_type,
            content_type=page.content_type,
            folder_path=folder_path,
            filename=filename,
        )

    async def _post_content(self, url, payload) -> dict:
        request = await self.session.post(url, json=payload)
        info = json.loads(bytes.decode(await request.read()))[0]["data"]
        return info

    async def _post_topics(
        self, url, course_id, course_name
    ) -> tuple[str, dict]:
        info = await self._post_content(url, Payload.topics(course_id))
        data = json.loads(info)
        return {"course_name": course_name, "data": data}

    async def _login(self, login_url=URL.LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes
        - return True if login succeeded.
        - return False if login failed."""
        print("\nConnexion...")
        resp_login = await self.session.post(
            login_url, data=Payload.login(self.username, self.password)
        )
        if (
            resp_login.status == 401
            or len(self.password) == 0
            or len(self.username) == 0
        ):
            print("Le mot de passe ou l'identifiant est incorrect.")
            return False
        print("Connecté.")
        return True

    async def _get_sess_key(self) -> int:
        """Method to get the session key delivered
        by ametice once connected."""
        resp_my = await self.session.get(URL.AMETICE)
        content = await resp_my.read()
        soup = BeautifulSoup(bytes.decode(content), features="html.parser")
        data = soup.find_all("script")[1].string
        pattern_js_variable = re.compile(r"M\.cfg = ([^;]*)")
        string_js_variable = re.findall(pattern_js_variable, data)[0]
        dic_js_variable = json.loads(string_js_variable)
        sesskey = dic_js_variable["sesskey"]

        return sesskey

    async def _get_courses_info(self) -> dict:
        """Method to get the informations related
        to the courses the student follows."""
        url_get_courses = URL.course(self.sess_key)
        courses_info = await self._post_content(
            url_get_courses, Payload.COURSES
        )
        return courses_info

    async def _get_topics_info(self, courses_info) -> list[dict]:
        """Method to get the informations related
        to the topics of the courses the student follows."""
        url_get_topics = URL.topics(self.sess_key)
        list_tasks = []
        for course_info in courses_info:
            current_course_name = course_info["fullname"]
            current_course_id = course_info["id"]
            list_tasks.append(
                asyncio.create_task(
                    self._post_topics(
                        url_get_topics, current_course_id, current_course_name
                    )
                )
            )
        return await asyncio.gather(*list_tasks)

    async def _save_files(self, **dic_args):
        """Save a file by creating necessary folders."""
        binary_content = dic_args["binary_content"]
        file_url = dic_args["file_url"]
        resource_type = dic_args["resource_type"]
        content_type = dic_args["content_type"]
        folder_path = dic_args["folder_path"]
        filename = dic_args["filename"]

        parsed = urlparse(file_url)
        extension = os.path.splitext(parsed.path)[1]
        if len(extension) == 0:
            extension = guess_extension(content_type)
            if extension is None:
                extension = ""

        if os.path.exists(folder_path):
            nb_same_filename = get_nb_origin_same_filename(
                folder_path, filename
            )
            if nb_same_filename > 0:
                filename = f"{filename}_{nb_same_filename}"

        if resource_type == "url":
            extension = ".txt"
            os.makedirs(folder_path, exist_ok=True)
            async with aiofiles.open(
                f"{folder_path}/{filename}{extension}", mode="w"
            ) as file:
                await file.write(file_url)
        else:
            if resource_type == "folder":
                extension = ".zip"
            os.makedirs(folder_path, exist_ok=True)
            async with aiofiles.open(
                f"{folder_path}/{filename}{extension}", mode="wb"
            ) as file:
                await file.write(binary_content)

    def _get_classified_cm_id(self, list_topics) -> dict:
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

    def _create_download_task(
        self, dic_topic_info, dic_cm_id_topic, dic_cm, school_year
    ):
        topic_name = dic_cm_id_topic[dic_cm["id"]]
        filename = dic_cm["name"]

        if "url" not in dic_cm:
            return None

        resource_url = dic_cm["url"]
        resource_type = self.get_resource_type(resource_url)

        if resource_type is None:
            return None

        if resource_type == "folder":
            resource_url = URL.folder(dic_cm["id"])

        else:
            resource_url = f"{resource_url}&redirect=1"

        folder_path = os.path.join(
            "Fichiers_Ametice",
            get_valid_filename(school_year),
            get_valid_filename(dic_topic_info["course_name"]),
            get_valid_filename(topic_name),
        )

        return asyncio.create_task(
            self._get_content_file_save(
                file_url=resource_url,
                resource_type=resource_type,
                folder_path=folder_path,
                filename=get_valid_filename(filename),
            )
        )

    def get_resource_type(self, resource_url):
        """Get the type of a resource with its url"""
        resource_type = None
        for re_name, re_url in DIC_NAME_REGEX.items():
            if re.match(re_url, resource_url):
                resource_type = re_name
        return resource_type

    async def download_all_documents(self):
        """Method to download all the documents
        from the Ametice account the session is
        connected to.
        """
        deb = time()

        async with aiohttp.ClientSession(
            headers=HEADERS,
            connector=aiohttp.TCPConnector(force_close=True),
            trust_env=True,
        ) as session:
            
            self.session = session
            is_logged = await self._login()
            if not is_logged:
                return
            self.sess_key = await self._get_sess_key()
            courses_info = (await self._get_courses_info())["courses"]
            school_year = "-".join(courses_info[0]["fullname"].split("-")[:2])
            table_topics_info = await self._get_topics_info(courses_info)
            list_tasks = []

            for dic_topic_info in table_topics_info:
                table_cms = dic_topic_info["data"]["cm"]
                dic_cm_id_topic = self._get_classified_cm_id(
                    list_topics=dic_topic_info["data"]["section"]
                )

                for dic_cm in table_cms:
                    task = self._create_download_task(
                        dic_topic_info, dic_cm_id_topic, dic_cm, school_year
                    )

                    if task is None:
                        continue

                    list_tasks.append(task)

            await asyncio.gather(*list_tasks)
            print(
                "\nTéléchargement terminé en"
                f" {round(time() - deb, 1)} secondes."
            )


if __name__ == "__main__":
    bot = AmeticeBot("username", "password")
    asyncio.run(bot.download_all_documents())
