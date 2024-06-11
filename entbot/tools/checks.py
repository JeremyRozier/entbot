"""This file contains functions to check user's settings
and modify them if necessary to make the bots work."""

import os
import subprocess
import sys
from importlib import import_module
import logging
from tools.logging_config import display_message


def check_cwd():
    """
    Ensures that the user has a correct
    current working directory to avoid any issues
    with reading files using relative paths.
    """
    cwd = os.getcwd()
    print(cwd)
    list_file_path = __file__.split("/")
    directory_file_path = "/".join(list_file_path[:-1])
    current_last_folder = cwd.split("/")[-1]
    file_last_folder = list_file_path[-2]

    if current_last_folder != file_last_folder:
        os.chdir(directory_file_path)


def check_module(module_name: str):
    """
    Ensures the module in argument is downloaded
    to make the bots work.
    """
    try:
        import_module(module_name)
    except ImportError:
        q = input(
            f"{module_name} est manquant, veux tu l'installer ? [y/n] : "
        )
        if q.lower() == "y":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", module_name]
            )
        else:
            display_message(
                "Ce module est nécessaire pour l'exécution du programme",
                level=logging.ERROR,
            )
            display_message("Abandon", level=logging.ERROR)
            sys.exit()
