"""File to execute to download all the files
of an Ametice session"""

import asyncio
from getpass import getpass
import os
import sys
from time import time

from user_functions import check_module

check_module("aiohttp")
check_module("aiofiles")
check_module("bs4")

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
import aiohttp

ABSOLUTE_ROOT_PROJECT_PATH = "".join(os.path.dirname(__file__).split("/"))
if ABSOLUTE_ROOT_PROJECT_PATH not in sys.path:
    sys.path.append(ABSOLUTE_ROOT_PROJECT_PATH)

# pylint: disable=wrong-import-position
import entbot.bots as bots
from entbot.constants import Headers
from entbot.tools.filename_parser import turn_cwd_to_execution_dir
from entbot.tools.logging_config import display_message


async def main():
    """The main function to execute for downloading all ametice files
    from the account associated to the given credentials.

    Returns: None
    """
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        while True:
            username = input("Nom d'utilisateur : ")
            password = getpass("Mot de passe : ")
            ent_bot = bots.ENTBot(session, username, password)
            display_message("Connexion...")
            if not ent_bot.login():
                display_message("Mot de passe incorrect")
                continue
            display_message("Connecté.")
            break

        display_message("Choisis un des deux modes :")
        mode_choice = "0"
        while mode_choice not in ("1", "2"):
            mode_choice = input("Choix (1 ou 2): ")

        if mode_choice == "1":
            ametice_bot = await ent_bot.get_ametice_bot()
            deb = time()
            await ametice_bot.download_all_files()
            display_message(
                "Téléchargement terminé en"
                f" {round(time() - deb, 1)} secondes.",
            )

        else:
            ade_bot = await ent_bot.get_ade_bot()
            semester_str = "0"
            list_semesters = [str(s) for s in range(1, 7)]
            while semester_str not in list_semesters:
                semester_str = input("Ton numéro de semestre (1 à 6): ")

            semester_number = int(semester_str)
            ade_bot.get_semester_id(semester_number)
            list_groups_id = ade_bot.get_groups_from_semester(semester_number)
            prompt_group_choice = "Choisis parmis les groupes suivants"
            for i in range(1, len(list_groups_id) + 1):
                prompt_group_choice += f"G{i}"


display_message(
    "Ce programme permet de télécharger toutes les ressources disponibles sur ton compte Ametice."
)
display_message(
    "Tous les fichiers seront stockés dans le chemin :"
    " 'Fichiers_Ametice/annee_debut:annee_fin/UE/chapitre/fichier'"
    " dans le même dossier que le programme main.py."
)
display_message(
    "Tous les dossiers seront automatiquement créés par le programme."
)

turn_cwd_to_execution_dir()
print("")

asyncio.run(main())
