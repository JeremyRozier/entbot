"""This file contains functions to check user's settings
and modify them if necessary to make the bots work."""

import subprocess
import sys
from importlib import import_module


def check_module(module_name: str):
    """
    Ensures necessary dependencies are downloaded
    to make the bots work.
    """
    try:
        import_module(module_name)
    except ModuleNotFoundError:
        q = input(
            f"{module_name} est manquant, veux tu l'installer ? [y/n] : "
        )
        if q.lower() == "y":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", module_name]
            )
        else:
            print("Abandon.")
            sys.exit()
