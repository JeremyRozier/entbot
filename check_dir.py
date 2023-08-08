"""Ensure the user has a correct current working directory
to avoid any issues with reading files using relative paths"""

import os

cwd = os.getcwd()
list_file_path = __file__.split("/")
DIRECTORY_FILE_PATH = "/".join(list_file_path[:-1])
current_last_folder = cwd.split("/")[-1]
file_last_folder = list_file_path[-2]

if current_last_folder != file_last_folder:
    os.chdir(DIRECTORY_FILE_PATH)
