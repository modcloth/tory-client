PYTEST ?= py.test
PYTEST_FLAGS ?= \
	--cov-report term-missing \
	--cov tory_sync_from_joyent \
	--cov tory_register \
	--cov tory_inventory \
	--pep8 -rs --pdb

.PHONY: all
all: clean test

.PHONY: test
test:
	$(PYTEST) $(PYTEST_FLAGS) tests/

.PHONY: clean
clean:
	git ls-files -o | xargs $(RM)

.PHONY: distclean
distclean:
	git clean -dfx
