.PHONY: test

install-dev:
	cd rust/ && cargo build
	cd python/ && pip install -e .
	cd python/ && pip install pytest
	cd examples/python/ && $(MAKE) install-dev

install-style:
	pip install flake8
	rustup component add rustfmt-preview
	cargo install --force --git https://github.com/rust-lang-nursery/rust-clippy clippy

test:
	cd python/ && py.test
	cd rust/ && cargo test
	cd examples/python/ && $(MAKE) test

style:
	flake8
	cd rust/ && cargo +nightly clippy
	cd rust/ && cargo fmt
	cd examples/python/rust/ && cargo fmt
	cd examples/python/rust/ && cargo +nightly clippy

release:
	cd python/ && python setup.py sdist bdist_wheel upload
	cd rust/shippai_derive/ && cargo publish
	cd rust/ && cargo publish
