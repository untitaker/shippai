import os
import re
import sys

PY2 = sys.PY2 = sys.version_info[0] == 2


class ShippaiException(Exception):
    def __init__(self, msg, failure):
        self.failure = failure
        Exception.__init__(self, msg)


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
                return

            class Exc(ShippaiException):
                pass
            Exc.__name__ = name
            errors[name] = (Exc, {})

        def new_variant(error_name, variant_name, discriminant):
            error, variants = errors[error_name]
            assert discriminant not in variants

            class Exc(error):
                pass
            Exc.__name__ = variant_name
            setattr(error, variant_name, Exc)
            variants[discriminant] = Exc

        for name in dir(self._lib):
            if name.startswith('shippai_is_error_'):
                new_error(name[len('shippai_is_error_'):])
            elif name.startswith('SHIPPAI_VARIANT_'):
                _, _, error_name, variant_name = name.split('_')
                new_error(error_name)
                discriminant = getattr(self._lib, name)
                new_variant(error_name, variant_name, discriminant)

        self._errors = errors

    def _owned_string_rv(self, c_str):
        if c_str == self._ffi.NULL:
            return None

        try:
            return self._ffi.string(c_str).decode('utf-8')
        finally:
            self._lib.shippai_free_str(c_str)

    def get_error(self, rust_e):
        for name, (cls, variants) in self._errors.items():
            if getattr(self._lib, 'shippai_is_error_{}'.format(name))(rust_e):
                return self._get_variant(rust_e, name, cls, variants)
        return self.Unknown

    def _get_variant(self, rust_e, error_name, error_cls, variants):
        discriminant = getattr(
            self._lib,
            'shippai_get_variant_{}'.format(error_name)
        )(rust_e)
        return variants.get(discriminant, error_cls)

    def check_exception(self, rust_e):
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
            frames = _filter_frames(frames)
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
            return self._errors[name][0]
        except KeyError:
            raise AttributeError(name)


class _RustFrame(object):
    __slots__ = ('filename', 'lineno', 'funcname')

    def __init__(self, filename, lineno, funcname):
        self.filename = filename
        self.lineno = lineno
        self.funcname = funcname

    def safe_funcname(self):
        return re.sub('[^0-9a-zA-Z_]', '_', self.funcname)

    def safe_filename(self):
        return self.filename or '???'


def _filter_frames(frames):
    for frame in frames:
        if not frame.filename:
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
    frames = iter(frames)

    frame = next(frames, None)
    if frame is None:
        raise exc

    code = '\n' * ((frame.lineno or 1) - 1)
    code += 'def {}(): raise _shippai_fake'.format(frame.safe_funcname())
    code = compile(code, frame.safe_filename(), 'exec')
    ns = dict(_shippai_fake=exc)
    exec(code, ns)
    func = ns[frame.safe_funcname()]

    for frame in frames:
        code = '\n' * ((frame.lineno or 1) - 1)
        if frame.funcname == '<lambda>':
            code += '_shippai_new_fake = lambda: _shippai_fake()'
            funcname = '_shippai_new_fake'
        else:
            code += 'def {}(): _shippai_fake()'.format(frame.safe_funcname())
            funcname = frame.safe_funcname()
        code = compile(code, frame.safe_filename(), 'exec')
        ns = dict(_shippai_fake=func)
        exec(code, ns)
        func = ns[funcname]

    func()
