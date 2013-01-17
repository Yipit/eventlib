PACKAGE=eventlib

all: install_deps test

export PYTHONPATH:=  ${PWD}:${PWD}/tests/resources

filename=$(PACKAGE)-`python -c 'from $(PACKAGE) import version; print version'`.tar.gz
install_deps:
	@pip install -r requirements.txt

test:
	@rm -f .coverage
	@echo "running python tests..."
	@nosetests --verbosity=2 -sd tests
	@echo "running documentation examples..."
	@steadymark README.md

clean:
	@printf "Cleaning up files that are already in .gitignore... "
	@for pattern in `cat .gitignore`; do rm -rf $$pattern; find . -name "$$pattern" -exec rm -rf {} \;; done
	@echo "OK!"

release: clean test publish
	@printf "Exporting to $(filename)... "
	@tar czf $(filename) $(PACKAGE) setup.py README.md COPYING
	@echo "DONE!"

publish:
	@python setup.py sdist register upload
