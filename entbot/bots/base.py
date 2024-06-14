import aiohttp
from entbot.constants import Payload, URL


class BaseBot:
    """This class is a bot for AMU website.
    It is meant to login to the ENT service so that
    it can be used in its subclasses to then access
    other services.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ) -> None:
        self.session = session
        self.username = username
        self.password = password

    async def login(self, login_url=URL.LOGIN) -> bool:
        """Method to login with the
        credentials given in the class attributes

        Args:
            - login_url (str): The url of the service hosting Moodle.
            The login page of Aix-Marseille Universités is the default url.

        Returns (bool):
            - True if login succeeded.
            - False if login failed.
        """
        async with self.session.post(
            login_url, data=Payload.login(self.username, self.password)
        ) as response:
            if (
                response.status == 401
                or len(self.password) == 0
                or len(self.username) == 0
            ):
                return False
        return True
