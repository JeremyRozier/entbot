"""Functional tests for AmeticeBot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from entbot.bots.ametice_bot import AmeticeBot
from entbot.constants import Headers

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


@pytest.mark.asyncio
async def test_login():
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True, limit=50),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, USERNAME, PASSWORD)
        assert await bot.login()