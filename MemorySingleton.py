__author__ = 'Floris'

from naoqi import ALModule


class MemorySingleton(ALModule):
    """ Mandatory docstring.
        comment needed to create a new python module
    """

    subscribers = []

    def on_event(self, key, value, message):
        """ Mandatory docstring.
            comment needed to create a bound method
        """
        for (event_name, event) in MemorySingleton.subscribers:
            if event_name == key:
                event(value)