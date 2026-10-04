# ENT Bot

A command-line bot that logs into a French university's student portal (ENT) and automates two tedious tasks:

- **Course files**: downloads every file from every course on the university's Moodle platform, sorted into folders by school year, course and section.
- **Timetables**: retrieves the iCal link of any timetable from the ADE scheduling service, ready to import into Google Calendar, Apple Calendar or Outlook.

None of these services offers a public API, so the bot replays the HTTP requests made by the browser.

> Personal project built during my bachelor's degree (2022–2024). It targets my university's infrastructure as it was at the time and may stop working if those services change.

## How it works

The bot works only with raw HTTP requests, without a headless browser. It uses [aiohttp](https://docs.aiohttp.org/) for asynchronous I/O.

1. **Single sign-on (CAS)**: `ENTBot` posts the credentials to the university's CAS login form. The resulting session cookies are then shared with the other services.
2. **Moodle**: `AmeticeBot` extracts the `sesskey` from the dashboard page and calls Moodle's internal AJAX web services (`lib/ajax/service.php`) to list the courses and their content. It then downloads the files concurrently, with a semaphore that caps parallel requests at 10 so the server isn't flooded.
3. **ADE**: the timetable app is a GWT application. `ADEBot` sends hand-built GWT-RPC payloads, reverse-engineered from the browser's network traffic. It walks the resource tree, lists the groups of a semester and requests the export URL. Dates are encoded in GWT's base64 `long` format, implemented in `tools/timestamp_functions.py`.

```
ENTBot (CAS login)
├── AmeticeBot  → Moodle AJAX API → async file downloads
└── ADEBot      → GWT-RPC calls  → iCal timetable URL
```

## Project structure

```
entbot/
├── bots/
│   ├── ent_bot.py         # CAS authentication, entry point to the other bots
│   ├── ametice_bot.py     # Moodle course listing and file downloads
│   └── ade_bot.py         # GWT-RPC requests to the ADE timetable service
├── tools/
│   ├── filename_parser.py      # safe filenames, folder layout, file writing
│   ├── timestamp_functions.py  # school year computation, GWT date encoding
│   ├── dic_operations.py       # mapping course modules to their sections
│   └── logging_config.py
├── constants.py           # URLs, headers, request payloads, regex patterns
└── tests/
main.py                    # interactive command-line interface
```

## Getting started

### Requirements

- Python 3.11+
- A student account on the university's ENT

### Installation

```bash
git clone https://github.com/JeremyRozier/entbot
cd entbot

make virtualenv
source .entbot_env/bin/activate
make install
```

### Usage

```bash
python main.py
```

The program asks for your credentials. The password is typed without being shown, through `getpass`, and is never stored. You then choose a service:

- **1 – Moodle**: every file is downloaded to `Ametice_Files/<school year>/<course>/<section>/` next to `main.py`.
- **2 – ADE**: pick a semester, then a group. The bot prints the timetable's iCal URL.

> The ADE flow is tailored to the degree program I was enrolled in.

## Development

```bash
make install_dev   # pytest, linters, type checker…
make test          # run the test suite
make lint          # isort, black, flake8, mypy, bandit
```

The tests in `entbot/tests/test_bots/` make real requests to the university's services. They read credentials from a `.env` file at the project root. This file is git-ignored, so never commit it:

```
ENT_USERNAME=your_username
ENT_PASSWORD=your_password
```

The tests in `entbot/tests/test_tools/` run offline.

## Tech stack

Python · asyncio · aiohttp · aiofiles · BeautifulSoup · pytest / pytest-asyncio · black · flake8 · mypy · bandit

## License

[MIT](LICENSE)
