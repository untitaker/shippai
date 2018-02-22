import shippai_example
import pytest

def test_basic():
    with pytest.raises(shippai_example.errors.MyError) as exc:
        shippai_example.authenticate("hans gans", "password")
    assert 'Invalid username' in str(exc.value)

    with pytest.raises(shippai_example.errors.MyError) as exc:
        shippai_example.authenticate("admin", "bassword")
    assert 'Invalid password' in str(exc.value)

    assert shippai_example.authenticate("admin", "password") == 'Hello world!'
