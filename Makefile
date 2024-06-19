.PHONY: virtualenv install install_dev install-doc lint format test clean

### -------------------------- Installation -------------------------------- ###

NAME := entbot
VIRTUALENV = venv

PYTHON = $(VENV)/bin/python
VENV := $(shell echo $${VIRTUAL_ENV-.entbot_env})
INSTALL_STAMP := $(VENV)/.install.stamp
STAMP_DEV := $(VENV)/.dev_env_installed.stamp

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  virtualenv  	   prepare virtual environment"
	@echo "  install     	   install the project in editable mode and its dependencies using the constraints in requirements.txt"
	@echo "  install_dev 	   install packages in dev_requirements.txt"
	@echo "  test        	   run all the tests"
	@echo "  clean       	   remove all temporary files and virtual environments"
	@echo ""
	@echo "Check the Makefile to know exactly what each <target> is doing."

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) $(VENV)

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON) setup.py requirements/requirements.txt
	$(VENV)/bin/pip install -U pip
	$(VENV)/bin/pip install -Ue . -c requirements/requirements.txt
	touch $(INSTALL_STAMP)

install_dev: $(INSTALL_STAMP) $(STAMP_DEV)
$(STAMP_DEV): $(PYTHON) setup.py requirements/dev_requirements.txt
	$(VENV)/bin/pip install -Ur requirements/dev_requirements.txt
	touch $(STAMP_DEV)

clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};

lint: 
	$(VENV)/bin/isort --profile=black --lines-after-imports=2 --check-only $(NAME) --virtual-env=$(VENV)
	$(VENV)/bin/black --check $(NAME) --diff
	$(VENV)/bin/flake8 --per-file-ignores="__init__.py:F401" --ignore=W503,E501,E203,W605,W291 $(NAME)
	$(VENV)/bin/mypy $(NAME) --ignore-missing-imports
	$(VENV)/bin/bandit -r $(NAME) -s B608

format: 
	$(VENV)/bin/isort --profile=black --lines-after-imports=2 --check-only $(NAME) --virtual-env=$(VENV)
	$(VENV)/bin/black --check $(NAME)

test: 
	$(PYTHON) -m pytest entbot/tests/


### -------------------------- Building executables -------------------------------- ###

.PHONY: build_current

OS := $(shell uname)
ifeq ($(OS),Windows_NT)
	OS_TARGET = windows
else ifeq ($(OS),Linux)
	OS_TARGET = linux
else ifeq ($(OS),Darwin)
	OS_TARGET = macos
else
	$(error Unsupported OS: $(shell uname))
endif

build_current:
	@echo "Compiling for $(OS_TARGET)..."
	$(PYTHON) -m PyInstaller --distpath=build/executables/$(OS_TARGET) build/executables/ent_bot.spec
