class Listener(object):
    """
    Listener class that subscribes for certain events from
    the Messenger instance
    """
    def __init__(self, evtDict):
        if evtDict:
            self.evtDict = evtDict
