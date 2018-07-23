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
$ make install-dev
$ RUST_BACKTRACE=1 python
Python 3.6.5 (default, May 11 2018, 04:00:52)
[GCC 8.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import shippai_example
>>> shippai_example.authenticate('', '')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/untitaker/projects/shippai/examples/python/shippai_example/__init__.py", line 25, in authenticate
    errors.check_exception(err[0])
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 144, in check_exception
    _raise_with_more_frames(exc, frames)
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 262, in _raise_with_more_frames
    _append_frame(exc_info, frames[-1])
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 296, in _append_frame
    exec(code, ns)
  File "/home/untitaker/projects/shippai/examples/python/rust/src/lib.rs", line 43, in authenticate
    let res = authenticate_impl(
  File "/home/untitaker/projects/shippai/examples/python/rust/src/lib.rs", line 27, in shippai_example::authenticate_impl::he2a2e071e069a869
    return Err(MyError::UserWrong.into());
  File "/checkout/src/libcore/convert.rs", line 396, in <T as core::convert::Into<U>>::into::hda623f1239c06654
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
