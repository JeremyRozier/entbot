from setuptools import setup, find_packages

setup(
    name="entbot",
    version="1.3.0",
    description="Bot automating tasks on a university student portal (Moodle and ADE)",
    url="https://github.com/JeremyRozier/entbot",
    author="Jérémy Rozier",
    license="MIT",
    install_requires=[
        "aiohttp",
        "aiofiles",
        "beautifulsoup4",
    ],
    extras_require={
        "dev": [
            "python-dotenv",
            "pytest",
            "pytest-asyncio",
            "pyinstaller",
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
