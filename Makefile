VERSION ?= $(shell cat VERSION)
MAX_COMPLEXITY ?= 12
PYTEST ?= py.test
PYTEST_FLAGS ?= \
	--cov-report term-missing \
	--cov tory_sync_from_joyent \
	--cov tory_register \
	--cov tory_inventory \
	--pep8 -rs --pdb

.PHONY: all
all: clean normversion lint test

.PHONY: lint
lint:
	flake8 --max-complexity=$(MAX_COMPLEXITY) $(shell git ls-files '*.py')

.PHONY: test
test:
	$(PYTEST) $(PYTEST_FLAGS) tests/

.PHONY: clean
clean:
	git ls-files -o | xargs $(RM)

.PHONY: distclean
distclean:
	git clean -dfx

.PHONY: normversion
normversion: $(shell git ls-files '*.py')
	git grep -l '__version__ =' | grep -v Makefile | \
	    xargs sed -i -e "s/__version__ = '.*'/__version__ = '$(VERSION)'/"
