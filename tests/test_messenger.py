from ..core import getMessenger, initMessenger
from ..core.Messenger import MessengerInstance
from unittest.mock import MagicMock

def test_getMessenger():
    assert getMessenger() is not None

def test_Messenger_subscribe():
    messenger = getMessenger()
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    listener_mock.evtDict = {'Test_EVT_sub': handler_mock}
    messenger.subscribe(listener_mock)
    assert listener_mock in messenger.listeners
    assert 'Test_EVT_sub' in messenger.dispatcher

def test_Messenger_unSubscribe():
    messenger = getMessenger()
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    listener_mock.evtDict = {'Test_EVT_usub': handler_mock}
    messenger.subscribe(listener_mock)
    messenger.unSubscribe(listener_mock)
    assert listener_mock not in messenger.listeners
    assert 'Test_EVT_usub' not in messenger.dispatcher

def test_Messenger_unSubscribe_with_multiple():
    messenger = getMessenger()
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    listener_mock.evtDict = {'Test_EVT_usub2': handler_mock}
    messenger.subscribe(listener_mock)
    listener2_mock = MagicMock()
    handler2_mock = MagicMock()
    listener2_mock.evtDict = {'Test_EVT_usub2': handler2_mock}
    messenger.subscribe(listener2_mock)
    messenger.unSubscribe(listener_mock)
    assert listener_mock not in messenger.listeners
    assert messenger.dispatcher['Test_EVT_usub2'] == [handler2_mock]



def test_Messenger_postEvent():
    messenger = getMessenger()
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    listener_mock.evtDict = {'Test_EVT': handler_mock}
    messenger.subscribe(listener_mock)
    messenger.postEvent('Test_EVT')
    assert listener_mock.is_called()
