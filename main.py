"""File to execute to download all the files
of an Ametice session"""

from checks import check_cwd, check_dependencies

check_dependencies()
check_cwd()

from ametice_bot import AmeticeBot
from constants import Headers
import aiohttp
import asyncio
from getpass import getpass
from logging_config import display_message


async def download(username, password):
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        bot = AmeticeBot(session, username, password, show_messages=True)
        await bot.download_all_files()


display_message(
    """Ce programme permet de télécharger toutes les ressources disponibles sur ton compte Ametice.
Tous les fichiers seront stockés dans le chemin : 
    'Fichiers_Ametice/annee_debut:annee_fin/UE/chapitre/fichier'.
Tous les dossiers seront automatiquement créés par le programme."""
)

print("")

username = input("Nom d'utilisateur : ")
password = getpass(prompt="Mot de passe : ")

print("")

asyncio.run(download(username, password))
