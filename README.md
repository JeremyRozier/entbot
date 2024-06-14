# ENT Bot

## Purpose

ENT Bot is a bot that logs into your AMU account and then either get the link of any timetables you are used to get on ADE service or download all the files, ordered in folders, available on your Ametice (based on the Moodle API) account.

The credentials the programs require are the one you are used to enter on the following page :

![Menu ENT](assets/readme_assets//screenshot_ent.png)

# Quickstart

## Requirements

Python 3.11.6 (the virtual environment will use this version)

## Installation

First clone the library from your terminal and move to the cloned folder :

```
git clone https://github.com/JeremyRozier/entbot
cd entbot/
```

### To install entbot, run:

```
make virtualenv

source .entbot_env/bin/activate

make install

```

### To install entbot for development, run:

```
make virtualenv

source .entbot_env/bin/activate

make install

make install_dev

make test
```

Note: Use `make help` to see the available commands and also check the content of `Makefile` to know exactly what each command is meant to do.
