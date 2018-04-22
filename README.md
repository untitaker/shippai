# Shippai

> failure in other languages

[![Travis](https://img.shields.io/travis/untitaker/shippai.svg)](https://travis-ci.org/untitaker/shippai)
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
example](https://github.com/untitaker/shippai/tree/master/python/example) for a
rough idea of how it all plays together. Here is how a stacktrace looks like:

```
$ RUST_BACKTRACE=1 python
Python 3.6.4 (default, Dec 23 2017, 19:07:07)
[GCC 7.2.1 20171128] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import shippai_example
>>> shippai_example.authenticate('', '')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/untitaker/projects/shippai/python/example/shippai_example/__init__.py", line 9, in authenticate
    errors.check_exception(err[0])
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 89, in check_exception
    _raise_with_more_frames(exc, frames)
  File "/home/untitaker/projects/shippai/python/shippai/__init__.py", line 189, in _raise_with_more_frames
    func()
  File "c/_cffi_backend.c", line 3025, in cdata_call
  File "../src/x86/ffi64.c", line 525, in ffi_call
  File "src/lib.rs", line 52, in authenticate
  File "src/lib.rs", line 21, in shippai_example__authenticate_impl__ha1570dbb7766e67f
  File "/checkout/src/libcore/convert.rs", line 415, in _T_as_core__convert__Into_U____into__he2c4b3d4cce9bee4
[...]
shippai.MyError: Invalid username
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
