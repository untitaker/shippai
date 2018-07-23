import os
import re
import sys

from types import CodeType

PY2 = sys.version_info[0] == 2


class ShippaiException(Exception):
    _variants = None
    _parent = None

    def __init__(self, msg, failure):
        self.failure = failure
        Exception.__init__(self, msg)

    @classmethod
    def _new_variant(cls, variant_name, discriminant):
        if cls is ShippaiException:
            raise RuntimeError('Baseclass cannot have variants')
        if cls._parent is not None:
            raise RuntimeError('Variant cannot have additional variants')

        if cls._variants is None:
            cls._variants = {}

        assert discriminant not in cls._variants

        class Exc(cls):
            _variants = None
            _parent = cls

        Exc.__name__ = variant_name

        setattr(cls, variant_name, Exc)
        cls._variants[discriminant] = Exc


class Shippai(object):
    __slots__ = ('_ffi', '_lib', '_errors', '_filter_frames',
                 '_rust_basepath', 'Base', 'Unknown')

    def __init__(self, ffi, lib, exception_baseclass=ShippaiException,
                 filter_frames=True, rust_basepath=None):
        self._ffi = ffi
        self._lib = lib
        self._filter_frames = filter_frames
        if rust_basepath:
            self._rust_basepath = rust_basepath.rstrip('/') + '/'
        else:
            self._rust_basepath = None
        self.Base = exception_baseclass

        self._generate_exceptions()

    def _generate_exceptions(self):
        try:
            self._lib.shippai_free_str
        except AttributeError:
            raise RuntimeError('Given library does not export shippai.')

        class Unknown(self.Base):
            pass

        self.Unknown = Unknown
        errors = {}

        def new_error(name):
            if name in errors:
                return errors[name]

            class Exc(ShippaiException):
                pass
            Exc.__name__ = name
            errors[name] = Exc
            return Exc

        for name in dir(self._lib):
            if name.startswith('shippai_is_error_'):
                new_error(name[len('shippai_is_error_'):])
            elif name.startswith('SHIPPAI_VARIANT_'):
                _, _, error_name, variant_name = name.split('_')
                Exc = new_error(error_name)
                discriminant = getattr(self._lib, name)
                Exc._new_variant(variant_name, discriminant)

        self._errors = errors

    def _owned_string_rv(self, c_str):
        if c_str == self._ffi.NULL:
            return None

        try:
            return self._ffi.string(c_str).decode('utf-8')
        finally:
            self._lib.shippai_free_str(c_str)

    def get_error(self, rust_error):
        for name, error_cls in self._errors.items():
            rust_fail = getattr(
                self._lib,
                'shippai_cast_error_{}'.format(name)
            )(rust_error)
            if rust_fail != self._ffi.NULL:
                return self._get_variant(error_cls, rust_fail)
        return self.Unknown

    def _get_variant(self, error_cls, rust_fail):
        if error_cls._variants is None:
            return error_cls

        rust_get_variant = getattr(
            self._lib,
            'shippai_get_variant_{}'.format(error_cls.__name__),
            None
        )

        if rust_get_variant is None:
            return error_cls

        discriminant = rust_get_variant(rust_fail)
        return error_cls._variants.get(discriminant, error_cls)

    def check_exception(self, rust_e):
        __tracebackhide__ = True

        if rust_e == self._ffi.NULL:
            return

        rust_e = self._ffi.gc(rust_e, self._lib.shippai_free_failure)
        exc_cls = self.get_error(rust_e)

        display = self._owned_string_rv(
            self._lib.shippai_get_display(rust_e)
        )

        exc = exc_cls(display, failure=rust_e)

        try:
            debug = self._owned_string_rv(self._lib.shippai_get_debug(rust_e))
            frames = _FailureDebugParser(debug).parse()
            frames = self._process_frames(frames)
            _raise_with_more_frames(exc, frames)
        except exc_cls:
            raise
        except Exception:
            raise exc

    def _process_frames(self, frames):
        if self._filter_frames:
            if callable(self._filter_frames):
                frames = self._filter_frames(frames)
            else:
                frames = _basic_filter_frames(frames)

        if self._rust_basepath:
            frames = (
                _RustFrame(
                    filename=os.path.join(self._rust_basepath, f.filename),
                    lineno=f.lineno,
                    funcname=f.funcname
                )
                for f in frames
            )
        return frames

    def __getattr__(self, name):
        try:
            return self._errors[name]
        except KeyError:
            raise AttributeError(name)


class _RustFrame(object):
    __slots__ = ('filename', 'lineno', 'funcname')

    def __init__(self, filename, lineno, funcname):
        self.filename = str(filename or "")
        self.lineno = lineno
        self.funcname = str(funcname or "")

    def guess_crate_name(self):
        for match in re.finditer(r"\.cargo/registry/src/[^/]+/([^/]+)/",
                                 self.filename):
            return match.group(1).rsplit('-', 1)[0]


def _basic_filter_frames(frames):
    for frame in frames:
        if not frame.filename:
            continue
        if frame.filename.endswith('.c'):
            continue
        if frame.guess_crate_name() in ('failure', 'backtrace'):
            continue
        yield frame


class _FailureDebugParser(object):
    def __init__(self, raw_string):
        self.input = raw_string

    def parse(self):
        self.lines = iter(self.input.splitlines())
        self.output = []

        try:
            while 'stack backtrace:' not in next(self.lines):
                pass
            while True:
                self.parse_line()
        except StopIteration:
            return self.output

    def parse_line(self):
        line = next(self.lines).strip()

        if line.startswith('at '):
            self.parse_filename_and_lineno(line)
        else:
            funcname = line.split(' - ')[-1]
            self.output.append(_RustFrame(None, None, funcname))

    def parse_filename_and_lineno(self, line):
        if not self.output:
            return

        filename = line[len('at '):]
        lineno = None
        if ':' in filename:
            filename, lineno = filename.split(':')
            try:
                lineno = int(lineno)
            except ValueError:
                lineno = None

        self.output[-1].filename = filename
        self.output[-1].lineno = lineno


def _raise_with_more_frames(exc, frames):
    __tracebackhide__ = True

    frames = list(frames)
    exc_info = type(exc), exc, None

    for frame in frames[:-1]:
        try:
            _append_frame(exc_info, frame)
        except BaseException:
            exc_info = sys.exc_info()
            exc_info = exc_info[0], exc_info[1], exc_info[2].tb_next.tb_next

    _append_frame(exc_info, frames[-1])


if PY2:
    # single exec misses a frame, wrap in another exec to actually append frame
    RERAISE_CODE = (
        'exec("raise _shippai_exc_info[0], _shippai_exc_info[1], '
        '_shippai_exc_info[2]")'
    )
else:
    RERAISE_CODE = (
        'raise _shippai_exc_info[1].with_traceback(_shippai_exc_info[2])'
    )


def _append_frame(exc_info, frame):
    __tracebackhide__ = True

    code = '\n' * ((frame.lineno or 1) - 1)
    code += RERAISE_CODE
    code = compile(code, frame.filename, 'exec')

    if PY2:
        code = CodeType(0, code.co_nlocals, code.co_stacksize,
                        code.co_flags, code.co_code, code.co_consts,
                        code.co_names, code.co_varnames, frame.filename,
                        frame.funcname, code.co_firstlineno,
                        code.co_lnotab, (), ())
    else:
        code = CodeType(0, code.co_kwonlyargcount,
                        code.co_nlocals, code.co_stacksize,
                        code.co_flags, code.co_code, code.co_consts,
                        code.co_names, code.co_varnames, frame.filename,
                        frame.funcname, code.co_firstlineno,
                        code.co_lnotab, (), ())

    ns = dict(_shippai_exc_info=exc_info)
    exec(code, ns)
