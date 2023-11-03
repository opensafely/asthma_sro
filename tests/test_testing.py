
import pytest

@pytest.fixture
def rh_fixture():
    return[1,2,3,4,5]

def test_sum(rh_fixture):
    assert sum(rh_fixture) == 15




