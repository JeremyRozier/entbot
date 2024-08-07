from setuptools import setup, find_packages

setup(
    name="entbot",
    version="1.3.0",
    description="Ent bot to automate tasks on an AMU college account",
    url="https://github.com/JeremyRozier/entbot",
    author="Rozier Jérémy",
    license="MIT",
    install_requires=[
        "aiohttp",
        "aiofiles",
        "beautifulsoup4",
        "pytest-asyncio",
        "pyinstaller",
        "setuptools",
    ],
    extras_require={
        "dev": [
            "python-dotenv",
            "pytest",
            "isort",
            "black",
            "flake8",
            "mypy",
            "bandit",
            "typeguard",
        ],
    },
    packages=find_packages(),
    zip_safe=False,
)
