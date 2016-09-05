from ..core import getMessenger, initMessenger
from ..core.Messenger import MessengerInstance
from ..core.Utils import HandlerTuple
from unittest.mock import MagicMock

import time

def test_getMessenger():
    assert getMessenger() is not None

def test_Messenger_subscribe(messenger):
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    listener_mock.evtDict = {'Test_EVT_sub': handler_mock}
    messenger.subscribe(listener_mock)
    assert listener_mock in messenger.listeners
    assert 'Test_EVT_sub' in messenger.dispatcher

def test_Messenger_unSubscribe(messenger):
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    listener_mock.evtDict = {'Test_EVT_usub': handler_mock}
    messenger.subscribe(listener_mock)
    messenger.unSubscribe(listener_mock)
    assert listener_mock not in messenger.listeners
    assert 'Test_EVT_usub' not in messenger.dispatcher

def test_Messenger_unSubscribe_with_multiple(messenger):
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



def test_Messenger_postEvent(messenger):
    listener_mock = MagicMock()
    handler_mock = MagicMock()
    handler = HandlerTuple(handler_mock, None, None)
    listener_mock.evtDict = {'Test_EVT': handler}
    messenger.subscribe(listener_mock)
    data = {"data": "test"}
    messenger.postEvent('Test_EVT', data)
    time.sleep(0.3)
    handler_mock.assert_called_with(data)
