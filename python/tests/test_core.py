import shippai

def test_rust_frame():
    cls = shippai._RustFrame
    f = cls('../.cargo/registry/src/github.com-1ecc6299db9ec823/failure-0.1.1/src/error.rs', 123, 'foo') # noqa
    assert f.guess_crate_name() == 'failure'
    f = cls('../.cargo/registry/src/github.com-1ecc6299db9ec823/fail-ure-0.1.1/src/error.rs', 123, 'foo') # noqa
    assert f.guess_crate_name() == 'fail-ure'
