"""Functional tests for AmeticeBot class"""

from datetime import datetime
import os
import aiohttp
from dotenv import load_dotenv
import pytest
from entbot.bots import ENTBot, ADEBot
from entbot.constants import Headers


load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


@pytest.mark.asyncio
async def test_login_ade():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ADEBot(session, USERNAME, PASSWORD)
        assert not await bot.login_ade()
        ent_bot = ENTBot(session, USERNAME, PASSWORD)
        assert await ent_bot.login()
        ade_bot = ADEBot(session, USERNAME, PASSWORD)
        assert await ade_bot.login_ade()


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
        list_courses_id = await bot.get_tree_from_name("S5 MPCI")
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
async def test_get_groups_from_semester():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ADEBot(session, USERNAME, PASSWORD)
        await bot.login()
        list_tree_ids = await bot.get_tree_from_name("S3 MPCI")
        list_groups_id_name = await bot.get_groups_from_semester(3, semester_id=list_tree_ids[-1])
        assert list_groups_id_name == [
            ("1714", "S3 MPCI"),
            ("1880", "GR1"),
            ("1895", "GR2"),
            ("2455", "GR3"),
            ("1850", "GR4"),
            ("1797", "GR5"),
            ("1783", "GR6"),
            ("2469", "GR7"),
            ("1715", "GR8"),
            ("131179", "GR9"),
            ("2189", "Gr10"),
            ("9682", "Gr11"),
            ("9781", "Gr12"),
        ]


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
