.PHONY: test

install-dev:
	cd rust/ && cargo build --release
	cd python/ && pip install -e .
	cd python/example/ && $(MAKE) install-dev

install-style:
	which cargo-install-update || cargo install cargo-update
	cargo +nightly install-update -i clippy
	cargo +nightly install-update -i rustfmt-nightly
	cargo +nightly install-update -i cargo-update

test:
	cd rust/ && cargo test
	cd python/example/ && make test

style:
	cd rust/ && cargo +nightly clippy
	cd rust/ && cargo fmt
	cd python/example/rust/ && cargo fmt
	cd python/example/rust/ && cargo +nightly clippy
