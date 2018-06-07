.PHONY: test

install-dev:
	cd rust/ && cargo build
	cd python/ && pip install -e .
	cd examples/python/ && $(MAKE) install-dev

install-style:
	which cargo-install-update || cargo install cargo-update
	cd python/ && pip install flake8
	cargo +nightly install-update -i clippy
	cargo +nightly install-update -i rustfmt-nightly
	cargo +nightly install-update -i cargo-update

test:
	cd rust/ && cargo test
	cd examples/python/ && $(MAKE) test

style:
	cd rust/ && cargo +nightly clippy
	cd rust/ && cargo fmt
	cd python/ && flake8
	cd examples/python/rust/ && cargo fmt
	cd examples/python/rust/ && cargo +nightly clippy

release:
	cd python/ && python setup.py sdist bdist_wheel upload
	cd rust/shippai_derive/ && cargo publish
	cd rust/ && cargo publish
