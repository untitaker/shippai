import re
import sys
import traceback

PY2 = sys.PY2 = sys.version_info[0] == 2


class ShippaiException(Exception):
    def __init__(self, msg, failure):
        self.failure = failure
        Exception.__init__(self, msg)


def _normalize_exception_name(name):
    return name.title().replace('_', '')


class Shippai(object):
    __slots__ = ('_ffi', '_lib', '_exc_python_names', '_exc_rust_names',
                 '_filter_frames')

    def __init__(self, ffi, lib, exception_baseclass=ShippaiException,
                 filter_frames=True):
        self._ffi = ffi
        self._lib = lib
        self._filter_frames = filter_frames
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
        rust_name = self._owned_string_rv(self._lib.shippai_get_cause_name(rust_e))
        exc_cls = self._exc_rust_names.get(rust_name, self.Unknown)

        display = self._owned_string_rv(
            self._lib.shippai_get_cause_display(rust_e)
        )

        exc = exc_cls(display, failure=rust_e)

        try:
            debug = self._owned_string_rv(self._lib.shippai_get_debug(rust_e))
            frames = _FailureDebugParser(debug).parse()
            if self._filter_frames:
                frames = _filter_frames(frames)
            _raise_with_more_frames(exc, frames)
        except exc_cls:
            raise
        except Exception:
            raise exc

    def __getattr__(self, name):
        try:
            return self._exc_python_names[name]
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
