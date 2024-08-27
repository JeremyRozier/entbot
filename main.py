"""File to execute to download all the files
from an Ametice session or to get timetables url from
an ADE session."""

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
from entbot import bots
from entbot.constants import Headers, CHOICE_MODE_PROMPT
from entbot.tools.filename_parser import turn_cwd_to_execution_dir
from entbot.tools.logging_config import display_message
from entbot.tools.timestamp_functions import get_beg_end_date


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
            print("")
            ent_bot = bots.ENTBot(session, username, password)
            display_message("Connexion...")
            if not await ent_bot.login():
                display_message("Mot de passe incorrect")
                continue
            display_message("Connecté.\n")
            break

        mode_choice = "0"
        print(CHOICE_MODE_PROMPT)
        while mode_choice not in ("1", "2"):
            mode_choice = input("Choix du service (1 ou 2): ")

        if mode_choice == "1":
            print("")
            ametice_bot = await ent_bot.get_ametice_bot()
            deb = time()
            display_message("Téléchargement de tous les cours...")
            await ametice_bot.download_all_files()
            display_message(
                "Tous les cours ont été téléchargés en"
                f" {round(time() - deb, 1)} secondes.",
            )

        else:
            ade_bot = await ent_bot.get_ade_bot()
            semester_str = "default"
            list_semesters = [str(s) for s in range(1, 7)]
            while semester_str not in list_semesters:
                semester_str = input("Numéro de semestre (1 à 6): ")
            print("")
            semester_number = int(semester_str)
            year_number = (
                semester_number // 2
                if semester_number % 2 == 0
                else semester_number // 2 + 1
            )
            display_message(
                f"Récupération des emplois du temps disponibles pour le S{semester_number} MPCI..."
            )
            list_tree_ids_semester = await ade_bot.get_tree_from_name(
                f"S{semester_number} MPCI"
            )
            semester_id = list_tree_ids_semester[-1]
            year_id = list_tree_ids_semester[-3]
            list_groups_id_name = await ade_bot.get_groups_from_semester(
                semester_number, semester_id
            )
            display_message("Récupération effectuée.")
            list_groups_id_name.insert(0, (year_id, f"L{year_number} MPCI"))
            prompt_group_choice = (
                "\nChoisis le numéro correspondant "
                "à l'emploi du temps de ton choix :\n\n"
            )
            list_available_choices = [
                str(choice) for choice in range(0, len(list_groups_id_name))
            ]
            for str_choice in list_available_choices:
                index_choice = int(str_choice)
                prompt_group_choice += (
                    f"{str_choice} : {list_groups_id_name[index_choice][1]}\n"
                )

            print(prompt_group_choice)
            group_choice = "default"
            while group_choice not in list_available_choices:
                group_choice = input(
                    f"Choix de l'emploi du temps (0 à {list_available_choices[-1]}): "
                )
            index_group_choice = int(group_choice)
            print("")
            display_message(f"Récupération du lien de {list_groups_id_name[index_group_choice][1]}...")
            timeline_id = list_groups_id_name[index_group_choice][0]
            beg_date, end_date = get_beg_end_date()
            timeline_url = await ade_bot.get_timeline_url(
                timeline_id, beg_date, end_date
            )
            display_message(f"Lien récupéré : {timeline_url}")


print(
    "\nENTBOT est un bot qui se connecte à ton compte AMU pour obtenir"
    " les liens des emplois du temps que tu as l'habitude d'obtenir sur le service ADE"
    " ou pour télécharger tous les fichiers, classés dans des dossiers, disponibles"
    " sur ton compte Ametice."
)
print(
    "Tous les fichiers téléchargés seront stockés dans le chemin :"
    " 'Fichiers_Ametice/annee_debut:annee_fin/UE/chapitre/fichier'"
    " dans le même dossier que le programme main.py."
)
print(
    "Tous les dossiers nécessaires à l'organisation des fichiers"
    " seront automatiquement créés par le programme."
)

turn_cwd_to_execution_dir()
print("")

asyncio.run(main())
