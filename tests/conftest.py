# content of conftest.py

import pytest
from ..core import getMessenger, delMessenger

@pytest.fixture(scope="module")
def messenger():
    messenger = getMessenger()
    yield messenger  # provide the fixture value
    delMessenger()
