import threading
import queue
import logging


class _Messenger(threading.Thread):
    """
    Messenger class which services listeners with events.
    """
    def __init__(self):
        super().__init__()
        self.dispatcher = {}
        self.listeners = []
        self.__lock = threading.RLock()
        self.__pauseThread = threading.Event()
        self.__stopThread = threading.Event()
        self.__msgQueue = queue.Queue()

    def subscribe(self, listener):
        """
        Subscribe to events
        :param listener: provide the listener object which contains the events
                         interested and the handlers associated with it.
        :return: None
        """
        if listener not in self.listeners:
            self.__pauseThread.set()
            with self.__lock:
                self.listeners.append(listener)
                for evt, handler in listener.evtDict.items():
                    if evt not in self.dispatcher:
                        self.dispatcher[evt] = []
                    if handler not in self.dispatcher[evt]:
                        self.dispatcher[evt].append(handler)
            self.__pauseThread.clear()

    def unSubscribe(self, listener):
        if listener not in self.listeners:
            return
        self.__pauseThread.set()
        with self.__lock:
            for evt, handler in listener.evtDict.items():
                if handler in self.dispatcher[evt]:
                    self.dispatcher[evt].remove(handler)
                    if not self.dispatcher[evt]:
                        self.dispatcher.pop(evt)
            self.listeners.remove(listener)
        self.__pauseThread.clear()

    def postEvent(self, evt, data):
        try:
            self.__msgQueue.put_nowait((evt, data))
        except queue.Full:
            logging.exception('Unable to post event because queue is full')

    def stop(self):
        self.__stopThread.set()

    def run(self):
        """
        Main thread loop

        """
        while not self.__stopThread.is_set():
            if not self.__pauseThread.is_set():
                try:
                    msg = self.__msgQueue.get_nowait()
                    if msg:
                        evt, data = msg
                        with self.__lock:
                            handlers = self.dispatcher.get(evt, None)
                            if handlers:
                                for handler in handlers:
                                    if data:
                                        data = [data]
                                    else:
                                        data = []
                                    if handler.args:
                                        args = data + handler.args
                                    else:
                                        args = data
                                    if handler.kwargs:
                                        kwargs = handler.kwargs
                                    else:
                                        kwargs = {}
                                    try:
                                        handler.func(*args, **kwargs)
                                    except Exception as e:
                                        logging.exception('Could not execute' \
                                                'callback handler {} with args: {}' \
                                                ' and kwargs: {}'.format(
                                                                    handler.func,
                                                                    handler.args,
                                                                    handler.kwargs
                                                                    ))
                except queue.Empty:
                    pass



MessengerInstance = None

def initMessenger():
   """
   Initialize Messenger
   :return: None
   """
   global MessengerInstance
   if not MessengerInstance:
       MessengerInstance = _Messenger()
       MessengerInstance.start()

def getMessenger():
   """
   Get messenger instance. Create one if not present
   :return: _Messenger
   """
   global MessengerInstance
   if not MessengerInstance:
       initMessenger()
   return MessengerInstance

def delMessenger():
    """
    Delete messenger instance
    """
    global MessengerInstance
    if MessengerInstance:
        MessengerInstance.stop()
        MessengerInstance = None
