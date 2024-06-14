"""Functional tests for AmeticeBot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from typeguard import check_type
from typing import List, Dict
from entbot.bots.ametice_bot import AmeticeBot
from entbot.constants import Headers, Payload, URL

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


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
        assert len(bot.session_key) > 0


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

        # This last example illustrates the need to set ssl = False for some servers.
        # This is handled in download_file_with_error_handling.
        test_filename = "test_download_file"
        await bot.download_file(
            cm_url="https://math.univ-cotedazur.fr/~diener/L3MASS19/Cours3_19.pdf",
            cm_module="url",
            folder_path=".",
            filename=test_filename,
            ssl=False,
        )
        assert os.path.exists(f"{test_filename}.pdf")
        os.remove(f"{test_filename}.pdf")


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
