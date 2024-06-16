"""Functional tests for AmeticeBot class"""

from datetime import datetime
import os
import aiohttp
from dotenv import load_dotenv
import pytest
from entbot.bots.ade_bot import ADEBot
from entbot.constants import Headers


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
        bot = ADEBot(session, USERNAME, PASSWORD)
        assert await bot.login()


@pytest.mark.asyncio
async def test_get_tree_ids_from_name():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ADEBot(session, USERNAME, PASSWORD)
        await bot.login()
        list_courses_id = await bot.get_tree_ids_from_name("S5 MPCI")
        assert list_courses_id == [
            "-100",
            "-1",
            "686",
            "13105",
            "706",
            "13114",
            "1823",
            "1915",
        ]


@pytest.mark.asyncio
async def test_get_semester_id():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ADEBot(session, USERNAME, PASSWORD)
        await bot.login()
        semester_id = await bot.get_semester_id(5)
        assert semester_id == "1915"


@pytest.mark.asyncio
async def test_get_group_id():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ADEBot(session, USERNAME, PASSWORD)
        await bot.login()
        group_id = await bot.get_group_id(3, 2)
        assert group_id == "1895"


@pytest.mark.asyncio
async def test_get_timeline_url():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ADEBot(session, USERNAME, PASSWORD)
        await bot.login()
        beg_date = datetime(2023, 9, 1)
        end_date = datetime(2024, 9, 1)
        timeline_url = await bot.get_timeline_url("1915", beg_date, end_date)
        assert (
            timeline_url
            == "https://ade-web-consult.univ-amu.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?projectId=8&resources=1915&calType=ical&firstDate=2023-09-01&lastDate=2024-09-01"
        )
