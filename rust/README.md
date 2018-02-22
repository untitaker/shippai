# Shippai in Rust

This is the part of shippai that deals with exporting failure/error type
information.

It does so through a single macro that generates all types that e.g. the Python
library needs. This is because [re-exporting the types of shippai in your own
library would not always work](https://github.com/rust-lang/rust/issues/36342).

Check out one of the full examples from the main README for usage.
