import os

from ._native import ffi, lib
from shippai import Shippai

rust_basepath = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    '../rust/'
))

errors = Shippai(ffi, lib, rust_basepath=rust_basepath)


def authenticate(user, password):
    err = ffi.new("ShippaiError **")
    rv = lib.authenticate(user.encode('utf-8'), password.encode('utf-8'), err)
    errors.check_exception(err[0])
    try:
        return ffi.string(rv).decode('utf-8')
    finally:
        # free `rv` here
        pass
