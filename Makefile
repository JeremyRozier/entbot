.PHONY: virtualenv install install-dev install-doc lint format test doc-serve run clean docker_clean prepare docker_terminal docker_run_gpu

### -------------------------- Installation -------------------------------- ###

NAME := entbot
VIRTUALENV = virtualenv --python=python3.11.6

PYTHON = $(VENV)/bin/python
VENV := $(shell echo $${VIRTUAL_ENV-.ent_env})
INSTALL_STAMP := $(VENV)/.install.stamp

print-%  : ; @echo $* = $($*)

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  virtualenv  	   prepare virtual environment"
	@echo "  install     	   install packages in requirements.txt"
	@echo "  clean       	   remove all temporary files and virtual environments"
	@echo "  lint        	   run the code linters"
	@echo "  format      	   reformat code"
	@echo "  test        	   run all the tests"
	@echo ""
	@echo "Check the Makefile to know exactly what each <target> is doing."

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) $(VENV)

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON) setup.py requirements.txt
	$(VENV)/bin/pip install -U pip
	$(VENV)/bin/pip install -Ue . -c requirements.txt
	touch $(INSTALL_STAMP)

clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf $(VENV) $(INSTALL_STAMP) .coverage .mypy_cache .pytest_cache

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
