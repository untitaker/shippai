import shippai_example
import traceback
import pytest

from textwrap import dedent

def test_basic():
    with pytest.raises(shippai_example.errors.MyError) as exc:
        shippai_example.authenticate("hans gans", "password")
    assert 'Invalid username' in str(exc.value)
    tb = ''.join(traceback.format_tb(exc.tb))
    assert 'in failure__backtrace__Backtrace__new__' in tb
    assert 'in backtrace__capture__' in tb
    assert 'in authenticate\n' in tb

    with pytest.raises(shippai_example.errors.MyError) as exc:
        shippai_example.authenticate("admin", "bassword")
    assert 'Invalid password' in str(exc.value)

    assert shippai_example.authenticate("admin", "password") == 'Hello world!'
