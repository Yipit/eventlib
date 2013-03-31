PACKAGE=eventlib

all: unit functional integration steadymark

unit:
	@make run_test suite=unit

functional:
	@make run_test suite=functional

integration:
	@make run_test suite=integration

run_test:
	@if [ -d tests/$(suite) ]; then \
		echo "Running \033[0;32m$(suite)\033[0m test suite"; \
		make prepare; \
		nosetests --stop --with-coverage --cover-package=$(PACKAGE) \
			--cover-branches --verbosity=2 -s tests/$(suite) ; \
	fi

steadymark:
	@if hash steadymark 2>/dev/null; then \
		steadymark; \
	fi

prepare: clean install_deps

install_deps:
	@echo "Installing missing dependencies..."
	@[ -e requirements.txt ] && (pip install -r requirements.txt) 2>&1>>.build.log
	@[ -e development.txt ] && (pip install -r development.txt) 2>&1>>.build.log

clean:
	@echo "Removing garbage..."
	@find . -name '*.pyc' -delete
	@rm -rf .coverage *.egg-info *.log build dist MANIFEST

publish:
	python setup.py sdist upload
