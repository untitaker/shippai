# Shippai

> failure in other languages

[![Travis](https://travis-ci.org/untitaker/shippai.svg?branch=master)](https://travis-ci.org/untitaker/shippai)
[![PyPI](https://img.shields.io/pypi/v/shippai.svg)](https://pypi.python.org/pypi/shippai/)
[![Crates.io](https://img.shields.io/crates/v/shippai.svg)](https://crates.io/crates/shippai)

Shippai is a set of libraries that help you with handling
[failure](https://github.com/withoutboats/failure)-style errors from other
languages

Right now this project consists of:

- A [Rust library](https://github.com/untitaker/shippai/tree/master/rust) to
  generate FFI code for your `Fail` types.
- A [Python library](https://github.com/untitaker/shippai/tree/master/python)
  to:

  1. generate exception types from the information provided by that FFI
  2. convert errors passed through that interface into a corresponding
     exception and raise them together with a complete stacktrace

# Examples

Check out the [Python
example](https://github.com/untitaker/shippai/tree/master/examples/python) for a
rough idea of how it all plays together. Here is how a stacktrace looks like:

```
$ RUST_BACKTRACE=1 python
Python 3.6.5 (default, Apr 12 2018, 22:45:43) 
[GCC 7.3.1 20180312] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import shippai_example
>>> shippai_example.authenticate('', '')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/untitaker/projects/shippai/examples/python/shippai_example/__init__.py", line 17, in authenticate
    errors.check_exception(err[0])
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 110, in check_exception
    _raise_with_more_frames(exc, frames)
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 228, in _raise_with_more_frames
    func()
  File "/home/untitaker/projects/shippai/examples/python/rust/c/_cffi_backend.c", line 3025, in cdata_call
  File "/home/untitaker/projects/shippai/examples/python/rust/../src/x86/ffi64.c", line 525, in ffi_call
  File "/home/untitaker/projects/shippai/examples/python/rust/src/lib.rs", line 43, in authenticate
    let res = authenticate_impl(
  File "/home/untitaker/projects/shippai/examples/python/rust/src/lib.rs", line 27, in shippai_example__authenticate_impl__h040a48b77826a8f4
    return Err(MyError::UserWrong.into());
[...]
shippai.UserWrong: Invalid username
>>> 
```

# Caveats

Shippai is a work-in-progress, a lot of features are missing. (check the issue
tracker)

I also have no idea what I am doing. If you see funny code here (particularly
in the FFI parts), don't assume it is because of a good reason. Tell me where I
am wrong.

# License

Shippai is licensed under MIT, see `LICENSE`.
