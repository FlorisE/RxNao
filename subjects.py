from rx.subjects import Subject
from naoqi import ALProxy, ALModule, ALBroker
from threading import Thread
import sys, time


NAO_IP = "192.168.10.2"
NAO_PORT = 9559


memory = None
ColorBlobMod = None


class ColorBlobModule(ALModule):
    """ a module to listen for color blob events """

    def __init__(self, module, proxy, name, stream):
        module.__init__(self, name)
        self.stream = stream
        thread = CheckForBlobsThread(proxy, stream)
        thread.daemon = True
        # thread.start()


class CheckForBlobsThread(Thread):

    def __init__(self, proxy, stream):
        Thread.__init__(self)
        self.proxy = proxy
        self.stream = stream

    def run(self):
        """ called when a blob is detected """

        memory = self.proxy("ALMemory")
        data_latch = None
        while True:
            data = memory.getData("ALTracker/ColorBlobDetected")
            if data != data_latch:
                print("blob detected")
                self.stream.on_next(data)
                data_latch = data
            time.sleep(1)


class ColorBlobSubject():

    def __init__(self, module, proxy, r, g, b,treshold, minSize=50, span=0.05, shape="Circle"):
        self.stream = Subject()
        
        self.color_blob = proxy("ALColorBlobDetection")
        self.color_blob.setColor(r, g, b, treshold)
        self.color_blob.setObjectProperties(minSize, span, shape)
        
        global ColorBlobMod
        ColorBlobMod = ColorBlobModule(module, proxy, "ColorBlobMod", self.stream)


class RedBallTrackerSubject(ALModule):
    """ module for detecting red balls """

    def __init__(self, module, proxy):
        self.stream = Subject()

        red_ball = proxy("ALRedBallDetection")

        thread = CheckForRedBallThread(proxy, self.stream)
        thread.daemon = True
        thread.start()


class CheckForRedBallThread(Thread):

    def __init__(self, proxy, stream):
        Thread.__init__(self)
        self.proxy = proxy
        self.stream = stream

    def run(self):
        memory = self.proxy("ALMemory")
        data_latch = None
        while True:
            data = memory.getData("redBallDetected")
            if data != data_latch:
                self.stream.on_next(data)
                data_latch = data
            time.sleep(1)


class RedColorBlobSubject(ColorBlobSubject):

    def __init__(self, module, proxy):
        ColorBlobSubject.__init__(self, module, proxy, 160, 50, 50, 30)


class BlueColorBlobSubject(ColorBlobSubject):

    def __init__(self, module, proxy):
        ColorBlobSubject.__init__(self, module, proxy, 38, 100, 150, 30)


if __name__ == "__main__":
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, NAO_IP, NAO_PORT)
    BlueColorBlobSubject(ALModule, ALProxy)
