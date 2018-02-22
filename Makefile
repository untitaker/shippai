.PHONY: test

install-dev:
	cd rust/ && cargo build --release
	cd python/ && pip install -e .
	cd python/example/ && $(MAKE) install-dev

test:
	cd rust/ && cargo test
	cd python/example/ && make test
