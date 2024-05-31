"""This file contains functions to check user's settings
and modify them if necessary to make the bots work."""

import os
import subprocess
import sys


def check_cwd():
    """
    Ensures that the user has a correct
    current working directory to avoid any issues
    with reading files using relative paths.
    """
    cwd = os.getcwd()
    list_file_path = __file__.split("/")
    directory_file_path = "/".join(list_file_path[:-1])
    current_last_folder = cwd.split("/")[-1]
    file_last_folder = list_file_path[-2]

    if current_last_folder != file_last_folder:
        os.chdir(directory_file_path)


def check_dependencies():
    """
    Ensures necessary dependencies are downloaded
    to make the bots work.
    """
    if "aiohttp" in sys.modules:
        q = input("aiohttp est manquant, veux tu l'installer ? [y/n] : ")
        if q.lower() == "y":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "aiohttp"]
            )
        else:
            print("Abandon.")
            sys.exit()

    if "aiofiles" in sys.modules:
        q = input("aiofiles est manquant, veux tu l'installer ? [y/n] : ")
        if q.lower() == "y":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "aiofiles"]
            )
        else:
            print("Abandon.")
            sys.exit()

    if "bs4" in sys.modules:
        q = input("bs4 est manquant, veux tu l'installer ? [y/n] : ")
        if q.lower() == "y":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "bs4"]
            )
        else:
            print("Abandon.")
            sys.exit()
