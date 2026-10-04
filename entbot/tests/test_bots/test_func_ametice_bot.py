"""Functional tests for AmeticeBot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from typeguard import check_type
from typing import List, Dict
from entbot.bots import AmeticeBot
from entbot.constants import Headers, Payload, URL, MAX_DOWNLOAD_ATTEMPTS

load_dotenv()
USERNAME = os.getenv("ENT_USERNAME")
PASSWORD = os.getenv("ENT_PASSWORD")


@pytest.mark.asyncio
async def test_login():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        assert await bot.login()


@pytest.mark.asyncio
async def test_post_for_data():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        await bot.login()
        table_courses = (
            await bot.post_for_data(
                URL.course(bot.session_key), Payload.COURSES
            )
        )["courses"]
        assert check_type(table_courses, List[Dict])


@pytest.mark.asyncio
async def test_post_for_table_courses_data():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        await bot.login()
        table_courses = (await bot.post_for_table_courses_data())["courses"]
        assert check_type(table_courses, List[Dict])


@pytest.mark.asyncio
async def test_post_for_topic_data():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        await bot.login()
        table_courses = (await bot.post_for_table_courses_data())["courses"]
        dic_course = table_courses[0]
        course_name = dic_course["fullname"]
        course_id = str(dic_course["id"])
        table_topics = (
            await bot.post_for_topic_data(
                URL.topics(bot.session_key),
                course_id,
                course_name,
            )
        )["data"]

        assert check_type(table_topics, Dict)


@pytest.mark.asyncio
async def test_download_file():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        await bot.login()
        test_filename = "test_download_file"
        await bot.download_file(
            cm_url="https://ametice.univ-amu.fr/mod/resource/view.php?id=3338465&redirect=1",
            cm_module="resource",
            folder_path=".",
            filename=test_filename,
        )
        assert os.path.exists(f"{test_filename}.pdf")
        os.remove(f"{test_filename}.pdf")


@pytest.mark.asyncio
async def test_download_file_skips_invalid_certificate(tmp_path):
    async with aiohttp.ClientSession() as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        await bot.download_file_with_error_handling(
            course_id="0",
            course_name="test_course",
            cm_url="https://expired.badssl.com/",
            cm_module="url",
            folder_path=str(tmp_path),
            filename="test_invalid_certificate",
        )
        assert not any(tmp_path.iterdir())


@pytest.mark.asyncio
async def test_callback_download_file():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        bot.dic_course_downloaded_cm["10010"] = 30
        bot.callback_download_file("10010", "TEST_COURSE_NAME")
        assert bot.dic_course_downloaded_cm["10010"] == 29


@pytest.mark.asyncio
async def test_download_file_gives_up_after_max_attempts(tmp_path, monkeypatch):
    monkeypatch.setattr("entbot.bots.ametice_bot.RETRY_DELAY_SECONDS", 0)
    async with aiohttp.ClientSession() as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        nb_calls = 0
        download_file = bot.download_file

        async def counting_download_file(*args):
            nonlocal nb_calls
            nb_calls += 1
            await download_file(*args)

        monkeypatch.setattr(bot, "download_file", counting_download_file)
        # Nothing listens on port 9 (discard) locally: the connection is refused.
        await bot.download_file_with_error_handling(
            course_id="0",
            course_name="test_course",
            cm_url="https://127.0.0.1:9/",
            cm_module="url",
            folder_path=str(tmp_path),
            filename="test_unreachable",
        )
        assert nb_calls == MAX_DOWNLOAD_ATTEMPTS
        assert not any(tmp_path.iterdir())
