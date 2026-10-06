import aiohttp
from bs4 import BeautifulSoup
from entbot.constants import Payload, URL
from entbot import bots


class ENTBot:
    """This class is a bot for the university website.
    It is meant to login to the ENT service so that
    it can be used in its subclasses to then access
    other services.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        show_messages=False,
    ) -> None:
        self.session = session
        self.username = username
        self.password = password
        self.show_messages = show_messages
        self.is_logged_in_ent = False

    async def get_execution_code(self, login_url=URL.ENT_LOGIN) -> str | None:
        """Method to get the CAS "execution" value from the login form.
        CAS stores the state of the login flow in this hidden field,
        so it has to be read from a fresh login page before each login.

        Args:
            - login_url (str): The url of the CAS login page.

        Returns (str | None): The execution value, or None if the
        login form was not found.
        """
        async with self.session.get(login_url) as response:
            content = await response.read()
        soup = BeautifulSoup(bytes.decode(content), features="html.parser")
        execution_input = soup.find("input", attrs={"name": "execution"})
        if execution_input is None:
            return None
        return execution_input.get("value")

    async def login(self, login_url=URL.ENT_LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes

        Args:
            - login_url (str): The url of the service hosting Moodle.
            The university CAS login page is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        execution = await self.get_execution_code(login_url)
        if execution is None:
            self.is_logged_in_ent = False
            return self.is_logged_in_ent

        async with self.session.post(
            login_url,
            data=Payload.login(self.username, self.password, execution),
        ) as response:
            if (
                response.status == 401
                or len(self.password) == 0
                or len(self.username) == 0
            ):
                self.is_logged_in_ent = False
            else:
                self.is_logged_in_ent = True

        return self.is_logged_in_ent

    async def get_ametice_bot(
        self, url_ametice=URL.AMETICE
    ) -> "bots.AmeticeBot":
        ametice_bot = bots.AmeticeBot(
            self.session, self.username, self.password, show_messages=True
        )
        if self.is_logged_in_ent:
            await ametice_bot.load_ametice_session(url_ametice)
        else:
            await ametice_bot.login(url_ametice)
        return ametice_bot

    async def get_ade_bot(self, url_ade_login=URL.ADE_LOGIN) -> "bots.ADEBot":

        ade_bot = bots.ADEBot(
            self.session, self.username, self.password, show_messages=True
        )
        if self.is_logged_in_ent:
            await ade_bot.login_ade(url_ade_login)
        else:
            await ade_bot.login()
        return ade_bot
