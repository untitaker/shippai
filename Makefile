.PHONY: test

export RUST_BACKTRACE := 1

install-dev:
	cd rust/ && cargo build --release
	cd python/ && pip install -e .
	cd python/example/ && $(MAKE) install-dev

install-style:
	which cargo-install-update || cargo install cargo-update
	cd python/ && pip install flake8
	cargo +nightly install-update -i clippy
	cargo +nightly install-update -i rustfmt-nightly
	cargo +nightly install-update -i cargo-update

test:
	cd rust/ && cargo test
	cd python/example/ && $(MAKE) test

style:
	cd rust/ && cargo +nightly clippy
	cd rust/ && cargo fmt
	cd python/ && flake8
	cd python/example/rust/ && cargo fmt
	cd python/example/rust/ && cargo +nightly clippy

release:
	cd python/ && python setup.py sdist bdist_wheel upload
	cd rust/shippai_derive/ && cargo publish
	cd rust/ && cargo publish
