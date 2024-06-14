"""Functional tests for BaseBot class"""

import os
import aiohttp
from dotenv import load_dotenv
import pytest
from entbot.bots.base import BaseBot
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
        bot = BaseBot(session, USERNAME, PASSWORD)
        assert await bot.login()
