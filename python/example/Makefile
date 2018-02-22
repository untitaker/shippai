.PHONY: native.h install-dev test

native.h:
	cbindgen -c cbindgen.toml rust/ > $@

install-dev:
	pip install cffi pytest
	pip install -e .

test:
	py.test
