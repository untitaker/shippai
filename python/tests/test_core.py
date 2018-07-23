import pytest
import shippai
import traceback

from fnmatch import fnmatch


def test_rust_frame():
    cls = shippai._RustFrame
    f = cls('../.cargo/registry/src/github.com-1ecc6299db9ec823/failure-0.1.1/src/error.rs', 123, 'foo') # noqa
    assert f.guess_crate_name() == 'failure'
    f = cls('../.cargo/registry/src/github.com-1ecc6299db9ec823/fail-ure-0.1.1/src/error.rs', 123, 'foo') # noqa
    assert f.guess_crate_name() == 'fail-ure'


def test_raise_frames():
    frames = [
        shippai._RustFrame('', 3, 'foo::foo'),
        shippai._RustFrame('bar.rs', 0, ''),
    ]
    e = ValueError()
    with pytest.raises(ValueError) as exc:
        shippai._raise_with_more_frames(e, frames)

    assert exc.value is e

    tb = ''.join(traceback.format_tb(exc.tb))

    assert tb.count('.rs') == 1
    assert tb.count('""') == 1
    assert tb.count('.py') == 3
