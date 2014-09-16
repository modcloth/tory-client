MAX_COMPLEXITY ?= 13
PYTEST ?= py.test
PYTEST_FLAGS ?= \
	--cov-report term-missing \
	--cov tory_client \
	--pep8 -rs --pdb

.PHONY: all
all: clean lint test

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
