SLACK_APP := slackapp
SLACK_APP_TESTS := tests
INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  install    install packages and prepare environment"
	@echo "  clean      remove all temporary files"
	@echo "  lint       run the code linters"
	@echo "  format     reformat code"
	@echo "  test       run all the tests"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install
	# en_core_web_sm required by spacy needs to be installed separately
	$(POETRY) run python -m spacy download en_core_web_sm 
	touch $(INSTALL_STAMP)

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf $(INSTALL_STAMP) .coverage .mypy_cache

.PHONY: lint
lint: $(INSTALL_STAMP)
	$(POETRY) run isort --check-only --profile=black --lines-after-imports=2 $(SLACK_APP) $(SLACK_APP_TESTS)
	$(POETRY) run black --check $(SLACK_APP) $(SLACK_APP_TESTS) --diff
	$(POETRY) run flake8 --ignore=W503,E501,F401 $(SLACK_APP) $(SLACK_APP_TESTS)
	# $(POETRY) run mypy $(SLACK_APP) $(SLACK_APP_TESTS) --ignore-missing-imports

.PHONY: format
format: $(INSTALL_STAMP)
	$(POETRY) run isort --profile=black --lines-after-imports=2 $(SLACK_APP) $(SLACK_APP_TESTS)
	$(POETRY) run black $(SLACK_APP) $(SLACK_APP_TESTS)

.PHONY: test
test: $(INSTALL_STAMP)
	$(POETRY) run pytest $(SLACK_APP_TESTS) --cov-report term-missing --cov-fail-under 50 --cov=$(SLACK_APP)