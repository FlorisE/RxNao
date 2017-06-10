from rx import Observable
from naoqi import ALProxy
import MemorySingleton


__author__ = 'Floris'


class MemoryObservable(Observable):
    def __init__(self, event):
        self.subscribers = []
        super(Observable, self).__init__(self.subscribers.append)

        MemorySingleton.subscribers.append((event, self))

        memory = ALProxy("ALMemory")
        memory.subscribeToEvent(event,
                                "MemorySingleton",
                                "on_event")

    def event(self, value):
        for subscriber in self.subscribers:
            subscriber.on_next(value)