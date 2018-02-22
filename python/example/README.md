# Example: Shippai in Python

This is an example for using Shippai in Python.

- It uses [milksnake](https://github.com/getsentry/milksnake) for embedding
  Rust in Python.
- It uses [cbindgen](https://github.com/eqrion/cbindgen) for generating the
  file `native.h`. If you want to generate this file yourself, install the CLI
  tool via `cargo install cbindgen` and then run `make native.h`.

Try out the tests by running `make install-dev test` in a virtualenv.
