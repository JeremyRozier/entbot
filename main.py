"""File to execute to download all the files
from an Ametice session or to get timetables url from
an ADE session."""

import asyncio
from getpass import getpass
from time import time

import aiohttp

from entbot import bots
from entbot.constants import Headers, CHOICE_MODE_PROMPT
from entbot.tools.filename_parser import turn_cwd_to_execution_dir
from entbot.tools.logging_config import display_message
from entbot.tools.timestamp_functions import get_beg_end_date


INTRO_MESSAGE = (
    "\nENTBOT is a bot that logs into your university account to get"
    " the links of the timetables you usually get on the ADE service"
    " or to download all the files, sorted into folders, available"
    " on your Ametice account.\n"
    "All downloaded files will be stored under the path:"
    " 'Ametice_Files/start_year:end_year/course/section/file'"
    " in the same folder as main.py.\n"
    "All the folders needed to organize the files"
    " will be created automatically by the program.\n"
)


def ask_choice(prompt: str, valid_choices: list[str]) -> str:
    """Asks the user for input until it is one of the valid choices.

    Args:
        - prompt (str): The text displayed to the user.
        - valid_choices (list[str]): The accepted answers.

    Returns (str): The choice of the user.
    """
    choice = input(prompt)
    while choice not in valid_choices:
        choice = input(prompt)
    return choice


async def login(session: aiohttp.ClientSession) -> bots.ENTBot:
    """Asks the user for credentials until the login succeeds.

    Args:
        - session (aiohttp.ClientSession): The session used for requests.

    Returns (ENTBot): The bot logged into the ENT.
    """
    while True:
        username = input("Username: ")
        password = getpass("Password: ")
        print("")
        ent_bot = bots.ENTBot(session, username, password)
        display_message("Logging in...")
        if await ent_bot.login():
            display_message("Logged in.\n")
            return ent_bot
        display_message("Wrong username or password")


async def download_ametice_files(ent_bot: bots.ENTBot) -> None:
    """Downloads all the files available on the Ametice account.

    Args:
        - ent_bot (ENTBot): The bot logged into the ENT.

    Returns: None
    """
    print("")
    ametice_bot = await ent_bot.get_ametice_bot()
    start_time = time()
    display_message("Downloading all courses...")
    await ametice_bot.download_all_files()
    display_message(
        "All courses were downloaded in"
        f" {round(time() - start_time, 1)} seconds.",
    )


async def get_ade_timetable_url(ent_bot: bots.ENTBot) -> None:
    """Asks the user for a semester and a group, then displays
    the url of the matching ADE timetable.

    Args:
        - ent_bot (ENTBot): The bot logged into the ENT.

    Returns: None
    """
    ade_bot = await ent_bot.get_ade_bot()
    semester_number = int(
        ask_choice(
            "Semester number (1 to 6): ", [str(s) for s in range(1, 7)]
        )
    )
    print("")
    year_number = (semester_number + 1) // 2

    display_message(
        f"Getting the available timetables for S{semester_number} MPCI..."
    )
    list_tree_ids_semester = await ade_bot.get_tree_from_name(
        f"S{semester_number} MPCI"
    )
    semester_id = list_tree_ids_semester[-1]
    year_id = list_tree_ids_semester[-3]
    list_groups_id_name = await ade_bot.get_groups_from_semester(
        semester_number, semester_id
    )
    display_message("Timetables retrieved.")
    list_groups_id_name.insert(0, (year_id, f"L{year_number} MPCI"))

    prompt_group_choice = (
        "\nEnter the number of the timetable of your choice:\n\n"
    )
    for index, (_, group_name) in enumerate(list_groups_id_name):
        prompt_group_choice += f"{index} : {group_name}\n"
    print(prompt_group_choice)

    last_index = len(list_groups_id_name) - 1
    group_choice = ask_choice(
        f"Timetable choice (0 to {last_index}): ",
        [str(index) for index in range(last_index + 1)],
    )
    timeline_id, group_name = list_groups_id_name[int(group_choice)]
    print("")
    display_message(f"Getting the link of {group_name}...")
    beg_date, end_date = get_beg_end_date()
    timeline_url = await ade_bot.get_timeline_url(
        timeline_id, beg_date, end_date
    )
    display_message(f"Link retrieved: {timeline_url}")


async def main():
    """Logs the user in, then runs the service of their choice:
    downloading all Ametice files or getting an ADE timetable url.

    Returns: None
    """
    async with aiohttp.ClientSession(
        headers=Headers.LOGIN_HEADERS,
        connector=aiohttp.TCPConnector(force_close=True),
        timeout=aiohttp.ClientTimeout(total=600),
        trust_env=True,
    ) as session:
        ent_bot = await login(session)

        print(CHOICE_MODE_PROMPT)
        mode_choice = ask_choice("Service choice (1 or 2): ", ["1", "2"])
        if mode_choice == "1":
            await download_ametice_files(ent_bot)
        else:
            await get_ade_timetable_url(ent_bot)


if __name__ == "__main__":
    print(INTRO_MESSAGE)
    turn_cwd_to_execution_dir()
    asyncio.run(main())
