# Shippai for Rust

This crate is part of [Shippai](https://github.com/untitaker/shippai), a way to
consume Rust errors in other languages.  It deals with exporting information
about existing error types and provides FFI functions that code in other
languages can use to handle Rust errors.

It does so through a single macro that generates all those symbols and
functions. This is because [re-exporting the types of shippai in your own
library would not always work](https://github.com/rust-lang/rust/issues/36342).
