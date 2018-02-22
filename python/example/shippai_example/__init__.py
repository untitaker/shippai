from ._native import ffi, lib
from shippai import Shippai

errors = Shippai(ffi, lib)

def authenticate(user, password):
    err = ffi.cast("ShippaiError **", ffi.new_handle(ffi.NULL))
    rv = lib.authenticate(user.encode('utf-8'), password.encode('utf-8'), err)
    errors.check_exception(err[0])
    try:
        return ffi.string(rv).decode('utf-8')
    finally:
        # free `rv` here
        pass
