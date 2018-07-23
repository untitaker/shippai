import shippai_example
import traceback
import pytest


def test_basic():
    with pytest.raises(shippai_example.errors.MyError.UserWrong) as exc:
        shippai_example.authenticate("hans gans", "password")
    assert 'Invalid username' in str(exc.value)
    tb = ''.join(traceback.format_tb(exc.tb))
    assert '.rs' in tb
    assert 'in failure' not in tb
    assert 'in backtrace' not in tb
    assert 'in authenticate\n' in tb

    with pytest.raises(shippai_example.errors.MyError.PassWrong) as exc:
        shippai_example.authenticate("admin", "bassword")
    assert 'Invalid password' in str(exc.value)

    assert shippai_example.authenticate("admin", "password") == 'Hello world!'


def test_types():
    assert issubclass(shippai_example.errors.MyError.UserWrong,
                      shippai_example.errors.MyError)
    assert issubclass(shippai_example.errors.MyError.PassWrong,
                      shippai_example.errors.MyError)
