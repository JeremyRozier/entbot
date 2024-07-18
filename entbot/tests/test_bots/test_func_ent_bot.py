"""Functional tests for BaseBot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from entbot.bots import ADEBot, ENTBot
from entbot.bots.ametice_bot import AmeticeBot
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
        bot = ENTBot(session, USERNAME, PASSWORD)
        assert await bot.login()


@pytest.mark.asyncio
async def test_get_ametice_bot():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ENTBot(session, USERNAME, PASSWORD)
        ametice_bot = await bot.get_ametice_bot()

        assert isinstance(ametice_bot, AmeticeBot)
        assert len(ametice_bot.session_key) > 0


@pytest.mark.asyncio
async def test_get_ade_bot():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = ENTBot(session, USERNAME, PASSWORD)
        ade_bot = await bot.get_ade_bot()

        assert isinstance(ade_bot, ADEBot)
        assert ade_bot.is_logged_in_ade
