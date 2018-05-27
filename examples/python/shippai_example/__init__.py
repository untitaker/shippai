import os

from ._native import ffi, lib
from shippai import Shippai

# `rust_basepath` is for the filenames in stacktraces. If you don't need that,
# you can leave this parameter out.
rust_basepath = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '../rust/'
))

errors = Shippai(ffi, lib, rust_basepath=rust_basepath)

# `errors` contains a bunch of exception classes now:
# - `errors.MyError.UserWrong`
# - `errors.MyError.PassWrong`
#
# `errors.MyError` is a superclass of both.


def authenticate(user, password):
    err = ffi.new("ShippaiError **")
    rv = lib.authenticate(user.encode('utf-8'), password.encode('utf-8'), err)
    errors.check_exception(err[0])
    try:
        return ffi.string(rv).decode('utf-8')
    finally:
        # free `rv` here
        pass
