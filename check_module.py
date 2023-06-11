import subprocess
import sys

try:
    import aiohttp
except ModuleNotFoundError:
    q = input("aiohttp est manquant, veux tu l'installer ? [y/n] : ")
    if q.lower() == "y":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    else:
        print("Abandon.")
        sys.exit()

try:
    import aiofiles
except ModuleNotFoundError:
    q = input("aiofiles est manquant, veux tu l'installer ? [y/n] : ")
    if q.lower() == "y":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiofiles"])
    else:
        print("Abandon.")
        sys.exit()

try:
    import bs4
except ModuleNotFoundError:
    q = input("bs4 est manquant, veux tu l'installer ? [y/n] : ")
    if q.lower() == "y":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bs4"])
    else:
        print("Abandon.")
        sys.exit()
