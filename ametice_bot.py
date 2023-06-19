import asyncio
import json
import unicodedata
from time import time
import os
import re
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from constants import DIC_NAME_REGEX, URL_LOGIN, URL_AMETICE, LIST_NOT_TREATED_TYPES


def get_valid_filename(filename):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    """
    valid_filename = str(filename).strip().replace(" ", "_")
    valid_filename = re.sub(r"(?u)[^-\w.]", "", valid_filename)
    valid_filename = unicodedata.normalize("NFKD", valid_filename)
    valid_filename = "".join(
        [c for c in valid_filename if not unicodedata.combining(c)]
    )
    return valid_filename


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

        self.login_payload = {
            "username": f"{self.username}",
            "password": f"{self.password}",
            "_eventId": "submit",
            "execution": "486eecad-5c6c-4128-a041-54316439b2ab_ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LkRsdnFrajF4aUY0SkdiSUJnUlhPeF9MN2kyT3U0M1JEZzNMSklScmxZYVJ4ZS11c1FodDlZWUpqVjJpWUtrYnNYLXZ5X0hpSGU2WmxwQ1RaRVpHUUNLWkhVVC1VeWFFX1o2bE51NXJRQ2tCZXBzNDd0dzl4T211R1BodzA5QkJiWnNfOEtzUS1mMkZoNXBUMEJlTXVrbUNTZ3RDV3VlcE1MWVp5bEtLRnB3QTdIdXY5dDR1MXVpUW8tclg5blk4Sm9zVUdGbXZsSTVmMlJoUUNUSVprQ2FNdXE0aEo0Z2ItMDNGaHJCZ1ZVMjItOGJJdWNKeThYOHVYTWxkNnpEVlNPYVUtem9oQmxyc0tVTlBwTFlaQlpyMnE1b0h4UWlsOVlwcVlpTGs3NUdyU2xHeXpLSHdjOXF6MnFNdFR1VWxLQ0lRRmJXUUMtMGpudDIxcTJCeXY0RzB2dUhWTDRtTDgwZ3ZyV0E2NEVITklJaHA3c0Y5c1dQTHVLMmltdXZ4aVUzcWFuMnRhbVI3YlJwRjdhejQ5ckc4TEs4ZjZGT3F0RDVKaXg4REZjLTd1ODZjMlByZ0o4N2lnQ3NNcjYzaDVlclBRUnE4bEhDTkVwemlkdkhuenFWWmluM1QwcHkzN3JNRlN4S3puUnZKTFdMb1JnQTBNeHR1N3V1VnFIQzdzMW4ySENzQXJ2WU5MSmh5Q3g1ZmtKYU5oNTlqSkhrQ3ByYUc1WlZfaFVzYUdZYlo5TklJUU13SzVIQzVSSWx1Tkt5cDhxUGJYRG41RXdSQmFHb183eWFvLUMzS1BFV0FGZ29zQ3g0UEMwUXd2VXd2VS1lTHB3cGJtN29vajEwMUFiZXBZcmlUMUNteW41b3NSS3lEc0p3TmFTd0ZtQjY5amc1R0VKemhDb04wMzRxel93bXdFQTdQU19hMF9KUHcxUS1WMGF1bTE2LVVveFd0dWpTZ3U0YktfdGUyenRSSU1QbWpVTjBtZC1RNndreFpOQUp0aWtSM0hrbENyb3JCQVJVbFMzazhQQnhEeENsM2FfRW5jTm0tSGhIOEhsby1qLWFCcFBZRTZJOEdQZjVHQ3hHVElOV3ZlUkRDaGJUanNRRktqR0pjdWVFOFB3bWtnNjlkNnZpLWxyZkdJOHc5U0tESmdLQ2RvNlFvRjlMUFY1N2h5b2FuTy15MlRpdDJwZkZNSVM5b3prc3RzMkUtR2I3RDlMRnJITHJRY0pZcVJEMHFQWUdpb24wY28ybk1RQ2JtREVITGVrdWlrcHJubkR2RHRpbVdNUklXZzdhQTNsYlBFcU55S2hnR1B6YjZzd2JxOVI2X1N2QVJXSkJ0SVFDZ25hMHZzZWpSanU0OU5RcGh2TV9qbEh4N2YzVGRLQTFmY2JCNUV5alV6MTRodVlORThrQzVZNjl0cFpieGxIaG90U2ozTlJjY1VPSG1CdlNkVU9LdU9KN3RzV2hIRklDVUZZamFtN0V0RkppYVNPUXViSEJudExJd1VzazRiNnBNcVpvR1JpM3M5bGZlb2hCc1ZuY0tSaU13VEFaQS1mc2ljU080UjlmZE5PTE81eUxOdzhSQ2oxWnpMWUFjQ1YzemNKVWFnci16SnYtVFJaRFN4SWx1blVGWjRXQTZHRWdlX3VkR2VaeDhWcjhCcmZCdUdtMndTQzRocHI1aUlmSUZnbnFEc19GTG9OdmZDNlVsRHhsa0c0Q3ZvWG16SHpUUW94ZnhqOG9CTTQwWWNCeHNlbXJrM2RPWEFfeTY0RFdDSC1lUFoxdGlic1J6UW1QN2ZqYkFjNFVVTllSTVdyUWN4aGxtTWw3Y2dfXzNZeDVnWDZ1MkNRWTZZLTRnZEtEMmlFOGJCWTBLV2ZlcFQyTUJZQWQ5MnNoM3VJaUJBWUNROElKV1Y2QnJTZTJVUnkxNXJib3FXZFcya2E1d2NuOWo4d3VxS0NHSmRLSUp1Nkszc1Y4VVpKLWYxekVIMUUwRkdrOEdld1NEN24tYUZkejQwc1VvQ1Z1aDdEVWhhMVZTMlZieEp2dFlIOEFpT1pvVkZncVJNUGJ0dHVMWGlSeXZMdjRyTXJ2V3g0RWFTWG56NEx0OFJFMXRaYzZORDRCWE15SmV2TGhodTZFSFg2WC1KeV9oOFRVenctU1lvLWEyQnB0SnpaaG4xbkFUYS1WU3RtYjNla1I3cS1fUTJKbndjc1lpRXJpTmxnUUcySHQ4M1VRU3VzVjVxazhWdEVscDVQclVVc1hZU2hJWEdDOGJLdXdvaXIwVGY0RzBabmJYX1Z4Vm5iUTlocUMwbk52aUJLakx2Rjk2WFB6NWNUWXp4QlROZEU2elRPNEdaUU5sanlzQlRFSTVGc2FPOUFUWW1ETlF0Sks0Q1ZoV0wxYmlrcDExdUVOYXhvWUhYRk5aNFVwM0pWTVVjTG5fTkFrYlhrYW40LWotMU5yalJjMFg5ZHNHRExvZFFsTm5oWG43M2VlZGR4QnhRSzFXc3h6WklpRWhwajJXMUtpUmMwX25jTkkwRm1oeDRFMHFRcW56MjQ0Q3kzUEg0enA4dzVaQ0JkNTNIMmptM1lDSkVUU1F6TVBWNEZwR0tNR1BEWk44WGw5UjdqRFZxMF9tZ3RVaGRnb1BlRTAtR0FiZ00xcmxaNWhDNXJJQ1J4eFRYMFJLa2JRQkRNcDB6MzNVb0E2eUtnZ1ZwME04Umo3TnpERUxoQmpqc2NKM2lXbWhLWjFrTkhLRUVKRGstUUQ4ZFZqM2Z4U1M4bmN4ZFdlc3gxZWFQeWFMTVIwWEZxUXBNLUt5N2NVMHR2WmlqX1NrQ3J0MTNQRG5YaDRiX0NVbl9NZVJtWm1SS05PUmU2QlBjbTBSTkYtaHF6RGJ6NHBjS3k0ZkQ0Z21xOHNfd3RtRjF5cHRDUWRuY0lOR2RZZjNQSjBwRGxwZktzdVpZd2p4YVlzeFpaV1Y4anRCQy1HTk9PT2NBQlpYaTFGMzZRcHczdGU1YUxtckRzdWlGeWFNdUtfMkx5VHhDSzhOWWxvekp2REk1RTBFT3lCNUNLR3YyYlhpVnBNQ0ZULThQNGJhRHJYZHo3ZnJNSTdTNUlNZDh6XzVveGMtMFpWRFZPTzF4YUl1TzJweVFhZk1MVjloN2tZUUdFV3haSFg0a2dvQkZWYWl4VU1VaUpzUjFCY0ZjdXBoNjR6bTJuVUlaTVlsTTNhTVV1LUtWUXRHN21LTC02V1VDQjVObzRJbE9TWF9Tbk01UVQxdmw5RldoNzVlNGFWb1hSdkh6WlFWdV9mTTVqVWE2ZHVSSzIyYUp2ajRRdmVFMEM0dmxKRDJZNG5MUDVNZU9oZWo1UVpWcU05SGNTMUp0ZTdRSFpJWmlUa1pKUkNMcVg1TTZkTC1mUTk4aVpFa0I4RE8wMG5YTTNxWEJVSUhOYTdKNGZfZlhoQWoyam5XNUNhbDdxanpKNGlJS3ByRFFleE9YWmJDNVFVczNiTkltZ0tsLV9TRy1SY2M3YlFNbm0xamhYaHFXb3NFaUFkdnB4Y3N4WGpndXBMcHY0VTB5TDdwUDFDRWFpLVdUaEw0OWdBYlBoR1N4aVU1SGFDa1Q2dGM3eVZGbUJJaWR5RTJWVnY4OEFXcEFNOVRrUjlacFB4QTNYZnZ1aEpJQjR5S09DV3lFUzROb0VyWHYtd2gwc1Q2RU9MZ0MxSWNFdHVtWDJHQm9yZm5YZmRKWFR4RVFaa0RTWGtHX1JXMlUxdExCVEZSdF9sOEczLVFDQUxNbjNqdktzNm9NeENjZWdUbEVnMHpWV1cwOEFSRFN3dVhodkoycWJwdmRPRUN0RUxfR1U3dmRnbk1MSko1TXljYUJOVExQenBBWjgyekgtd3RYR2NlMC1Yb29XQWtqQXktdUM5TzZOaTU1c3BVZFBXdVdnOGxTS2hYcEt5RGFIMUd4bjRaUWNSR3pramY4NVhWU1V4UWIxMXp0WE1ybVdFOUFLang5bl9VX2lleE8wWmd5VGYwMkcwZXB5UEgwa0VCOVU2Vm9QeHVBaUIxbUEybVJQalFwRlRpZkZHTmdBS0hIQk5wUzlOVGZ1YXhOaGVkRndQWFVvSDNucTVZY0JZcmhPeEhVZFUyWHkwQVVkTGdMZVNoY21udVZHZlptclJvSnBjZ2hfdk52X2NWTmFfQnJ0SmZBMXFpOFFFbFZqTENYejBrWDFuT21KZWF2ZllVSjVQOXJFNng2UzVYdWtXT2ZEVVRzRU9vZWx1YXVSZ0lFS0RZNFZaNEMtaHlQSVFRSmxrd1Bmam9OajlLcFlPLW5uNUphOU1yd0plTGVTVDFyM2RNalZGT2I1NkpPUC1NdkNKRjRsdVB0UVBlNkdnMVpNUlJid29adWVzM1FTZXRlNk52NERROWpiMnJSTi1EcXpCMVBOSmsyTldTQXF4MmpMRko2Uzk3amE4ZFNpMmRDZjgzZG1HM1NXd2xTM18xT05ndGgtc3dRdWRuUGM0ZDh4RlkyMVRuaVV1TGxVYXZZNmt6Vmk4ZXVWVTRoZ2hzTWl5NDVSNEVkb3FPVjIxb1lGckM1TnFBTVpjcFAtU0lRcV94Xzd4bDZld0ExVVVza0s3RTFZaGx6cERfdnNBczRmXzJ1SkFYblAwSVlnS29FMmZaNEU4cmZ3M1R5bF9RSzFkQ0R3LU5uWjB2STY5OVpBN28xeWNjOVlVYU00WkpZaEVaTmNNdHowbUUtLUpSN080NnV5VHZjb3Jra0d1anVDOXlxN3BPaGoxSGFlZFpTUFlLRU0taV9OTDlsSUZTNlZ0bVNzeGliRzlxbmM3b2JZdW42Mi1EMXVXX280M01GZXQwOGZVLU9uRWdpcWxQZVQtSGp3dExuRVFmbl9YLVZMRU1kaWx6c281N18tOXVoUVFvODFOcHZzVEtLYUFaSnVaY0NYUzVKcWVkMm9KN0pYU09hb1lLZmhRSUVOY1VRRkdtTFAzaGNmVjVzSkNpYWNJZEM1cEx6YUxRVldmSmhNY0ktU3ROWTJqb1BnWm1PdlZLXzQ5ZlRuM21hRTVHV25kQlRyckExbGlYemNCaWZVZnBwTjZ4WC10aUdldWxIOEstR0FmY01EckZ3T3ZBSEtWa1cyaDI0V0Jjb2FCS21GM1ZpdGxENndWcUxLTVVpT3NGVGNpdXlWaFlsTlVEMzhPSy1BYUtLTnJNZ3pwMk84UnNUUEVSTFNZLVI2c1hzUWtuRURvWl9zS1FvWEdSNUJ1SGd5bXI1NzhYYS5NR2NaOVpacnY2NmRUV0tTSTVKUkVkVDZHcGw5ZTB2RnhpZHhNOWZQQXFOck5Eb3RvR2hua25MWkh4ZTgyaVNmb3lFLVJuTTR0Z215VV9zNnZRRUZBdw==",
        }

        self.courses_payload = [
            {
                "index": 0,
                "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
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

        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
        }

    async def _get_content(self, name, url) -> tuple[str, str]:
        page = await self.session.get(url)
        content = await page.read()
        return (name, content)

    async def _get_content_file_save(self, tuple_url, folder_path, filename):
        url = tuple_url[0]
        content_type = tuple_url[1]

        has_connection_error = True
        while has_connection_error:
            try:
                page = await self.session.get(url)
            except aiohttp.ClientConnectionError:
                page = await self.session.get(url)
                continue

            has_connection_error = False

        has_payload_error = True
        while has_payload_error:
            try:
                binary_content = await page.read()
            except aiohttp.client_exceptions.ClientPayloadError:
                page = await self.session.get(url)
                continue
            has_payload_error = False

        await self._save_files(
            binary_content, str(page.url), content_type, folder_path, filename
        )

    async def _post_content(self, url, payload) -> dict:
        request = await self.session.post(url, json=payload)
        info = json.loads(bytes.decode(await request.read()))[0]["data"]
        return info

    async def _post_topics(self, url, payload, course_name) -> tuple[str, dict]:
        info = await self._post_content(url, payload)
        data = json.loads(info)
        return (course_name, data)

    async def _login(self, login_url=URL_LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes
        - return True if login succeeded.
        - return False if login failed."""
        print("\nConnexion...")
        resp_login = await self.session.post(login_url, data=self.login_payload)
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
        resp_my = await self.session.get(URL_AMETICE)
        content = await resp_my.read()
        soup = BeautifulSoup(bytes.decode(content), features="html.parser")
        input_sess_key = soup.find("input", attrs={"name": "sesskey"})
        sess_key = input_sess_key["value"]
        return sess_key

    async def _get_courses_info(self) -> dict:
        """Method to get the informations related
        to the courses the student follows."""
        url_get_courses = f"https://ametice.univ-amu.fr/lib/ajax/service.php?sesskey={self.sess_key}&info=core_course_get_enrolled_courses_by_timeline_classification"
        courses_info = await self._post_content(url_get_courses, self.courses_payload)
        return courses_info

    async def _get_topics_info(self, courses_info) -> dict:
        """Method to get the informations related
        to the topics of the courses the student follows."""
        url_get_topics = f"https://ametice.univ-amu.fr/lib/ajax/service.php?sesskey={self.sess_key}&info=core_courseformat_get_state"
        list_tasks = []
        for course_info in courses_info:
            current_course_name = course_info["fullname"]
            current_course_id = course_info["id"]
            topics_payload = [
                {
                    "index": 0,
                    "methodname": "core_courseformat_get_state",
                    "args": {"courseid": current_course_id},
                }
            ]
            list_tasks.append(
                asyncio.create_task(
                    self._post_topics(
                        url_get_topics, topics_payload, current_course_name
                    )
                )
            )
        return await asyncio.gather(*list_tasks)

    async def _save_files(
        self, binary_content, file_url, content_type, folder_path, filename
    ):
        extension = file_url.split(".")[-1]
        if "?forcedownload=1" in extension:
            extension = extension.replace("?forcedownload=1", "")
        if content_type == "url":
            extension = "txt"
            os.makedirs(folder_path, exist_ok=True)
            async with aiofiles.open(
                f"{folder_path}/{filename}.{extension}", mode="w"
            ) as file:
                await file.write(file_url)
        else:
            if content_type == "folder":
                extension = "zip"
            os.makedirs(folder_path, exist_ok=True)
            async with aiofiles.open(
                f"{folder_path}/{filename}.{extension}", mode="wb"
            ) as file:
                await file.write(binary_content)

    async def download_all_documents(self):
        """Method to download all the documents
        from the Ametice account the session is
        connected to.
        """
        deb = time()
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(
            headers=self.headers, connector=connector, trust_env=True
        ) as session:
            self.session = session
            is_logged = await self._login()
            if not is_logged:
                return
            self.sess_key = await self._get_sess_key()
            courses_info = (await self._get_courses_info())["courses"]
            school_year = "-".join(courses_info[0]["fullname"].split("-")[:2])
            self.dic_course_topics = {
                course_info["fullname"]: {} for course_info in courses_info
            }
            topics_info = await self._get_topics_info(courses_info)
            for topic_info in topics_info:
                course_name = topic_info[0]
                dic_data = topic_info[1]
                list_topics = dic_data["section"]
                list_dic_cm = dic_data["cm"]
                for dic_topic in list_topics:
                    topic_name = dic_topic["title"]
                    self.dic_course_topics[course_name][topic_name] = []
                    list_cm_id = dic_topic["cmlist"]
                    nb_treated = 0
                    for dic_cm in list_dic_cm:
                        cm_id = dic_cm["id"]
                        if cm_id in list_cm_id:
                            filename = dic_cm["name"]
                            if "url" not in dic_cm:
                                continue
                            file_url = dic_cm["url"]
                            is_url_not_treated = False
                            for re_name, re_url in DIC_NAME_REGEX.items():
                                if re_name in LIST_NOT_TREATED_TYPES and re.match(
                                    re_url, file_url
                                ):
                                    is_url_not_treated = True

                            if is_url_not_treated:
                                continue
                            if (
                                re.match(DIC_NAME_REGEX["resource"], file_url)
                                is not None
                            ):
                                tuple_url = (f"{file_url}&redirect=1", "resource")

                            elif re.match(DIC_NAME_REGEX["url"], file_url) is not None:
                                tuple_url = (f"{file_url}&redirect=1", "url")

                            elif (
                                re.match(DIC_NAME_REGEX["folder"], file_url) is not None
                            ):
                                tuple_url = (
                                    f"https://ametice.univ-amu.fr/mod/folder/download_folder.php?id={cm_id}",
                                    "folder",
                                )

                            self.dic_course_topics[course_name][topic_name].append(
                                {
                                    "filename": filename,
                                    "tuple_url": tuple_url,
                                }
                            )
                            nb_treated += 1
                            if nb_treated == len(list_cm_id):
                                break

            list_tasks = []
            for course_name in self.dic_course_topics:
                for topic_name in self.dic_course_topics[course_name]:
                    for dic_file in self.dic_course_topics[course_name][topic_name]:
                        file_url = dic_file["tuple_url"]
                        valid_filename = get_valid_filename(dic_file["filename"])
                        valid_school_year = get_valid_filename(school_year)
                        valid_course_name = get_valid_filename(course_name)
                        valid_topic_name = get_valid_filename(topic_name)
                        folder_path = f"Fichiers_Ametice/{valid_school_year}/{valid_course_name}/{valid_topic_name}"
                        list_tasks.append(
                            asyncio.create_task(
                                self._get_content_file_save(
                                    file_url, folder_path, valid_filename
                                )
                            )
                        )
            await asyncio.gather(*list_tasks)
            print(f"\nTéléchargement terminé en {round(time() - deb, 1)} secondes.")


if __name__ == "__main__":
    bot = AmeticeBot("username", "password")
    asyncio.run(bot.download_all_documents())
