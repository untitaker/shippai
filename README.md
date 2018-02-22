# shipppai

> failure in other languages

[![Build Status](https://travis-ci.org/untitaker/shippai.svg?branch=master)](https://travis-ci.org/untitaker/shippai)

Shippai is a set of libraries that help you with handling
[failure](https://github.com/withoutboats/failure)-style errors from other
languages

Right now this project consists of:

- A [Rust library](https://github.com/untitaker/shippai/tree/master/rust) to
  generate a FFI for a given list of `T: Fail` via a macro.
- A [Python library](https://github.com/untitaker/shippai/tree/master/python)
  to:

  1. generate exception types from the information provided by that FFI
  2. convert errors passed through that interface into a corresponding
     exception and raise it

# Examples

Check out the [Python
example](https://github.com/untitaker/shippai/tree/master/python/example) for a rough
idea about how it all plays together.

# Todo

Shippai is a work-in-progress, a lot of features are missing. Be aware of the following:

- Shippai does not have a result type.
- Shippai does not expose information about the stacktrace of a failure.
- Shippai does not expose information about the cause of a failure.
- Shippai cannot differentiate between enum variants of a fail (sometimes
  called `ErrorKind`s), but only between the types that implement `Fail`.
- `failure` itself is not stable yet, though [that will change
  soon](https://boats.gitlab.io/blog/post/2018-02-22-failure-1.0/).
- I have no idea what I am doing. If you see funny code here (particularly in
  the FFI parts), don't assume it is because of a good reason. Tell me where I
  am wrong.

# License

Shippai is licensed under MIT, see `LICENSE`.
