from ..core import Listener
from unittest.mock import MagicMock

def test_initListener():
    listener = Listener({'Test_EVT': MagicMock})
    assert listener
