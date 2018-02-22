import sys

PY2 = sys.PY2 = sys.version_info[0] == 2


class ShippaiException(Exception):
    def __init__(self, msg, failure):
        self.failure = failure
        Exception.__init__(self, msg)


def _normalize_exception_name(name):
    return name.title().replace('_', '')


class Shippai(object):
    __slots__ = ('_ffi', '_lib', '_exc_python_names', '_exc_rust_names')

    def __init__(self, ffi, lib, exception_baseclass=ShippaiException):
        self._ffi = ffi
        self._lib = lib
        self._generate_exceptions(exception_baseclass)

    def _generate_exceptions(self, baseclass):
        try:
            cause_names = self._lib.shippai_get_cause_names()
        except AttributeError:
            raise RuntimeError('Given library does not export shippai.')

        cause_names = self._ffi.string(cause_names)
        if not PY2:
            cause_names = cause_names.decode('utf-8')
        cause_names = cause_names.split(',')

        exc_python_names = {}
        exc_rust_names = {}

        exc_python_names['Base'] = baseclass

        class Unknown(baseclass):
            pass

        exc_python_names['Unknown'] = Unknown

        for rust_name in cause_names:
            if not rust_name or rust_name in exc_rust_names:
                continue

            name = _normalize_exception_name(rust_name)

            class Exc(ShippaiException):
                pass

            Exc.__name__ = name
            exc_python_names[name] = Exc
            exc_rust_names[rust_name] = Exc

        self._exc_python_names = exc_python_names
        self._exc_rust_names = exc_rust_names

    def _owned_string_rv(self, c_str):
        try:
            return self._ffi.string(c_str).decode('utf-8')
        finally:
            self._lib.shippai_free_str(c_str)

    def check_exception(self, rust_e):
        if rust_e == self._ffi.NULL:
            return

        rust_e = self._ffi.gc(rust_e, self._lib.shippai_free_failure)
        e = self._exc_rust_names.get(
            self._owned_string_rv(self._lib.shippai_get_cause_name(rust_e)),
            self.Unknown
        )

        display = self._owned_string_rv(
            self._lib.shippai_get_cause_display(rust_e)
        )

        raise e(display, failure=rust_e)

    def __getattr__(self, name):
        try:
            return self._exc_python_names[name]
        except KeyError:
            raise AttributeError(name)
