import naoqi
from rx.subjects import Subject
from threading import Thread
from blobs import *
import sys, time


class QiMemorySubject(Thread):
    def __init__(self, field, session):
        Thread.__init__(self)
        self.session = session
        self.field = field
        self.stopped = False
        self.subject = Subject()

    def run(self):
        mem = self.session.service("ALMemory")
        self.subscriber = mem.subscriber(self.field)
        self.signal = self.subscriber.signal.connect(self.subject.on_next)
        while not self.stopped:
            time.sleep(1)

    def stop(self):
        self.stopped = True
        self.subscriber.signal.disconnect(self.signal)
        print("Stopping")


class RedBallSubject(QiMemorySubject):
    def __init__(self, session):
        QiMemorySubject.__init__(self, "redBallDetected", session)


class BlobDetectionSubject(QiMemorySubject):
    def __init__(self, session):
        QiMemorySubject.__init__(self, "ALTracker/ColorBlobDetected", session)


class BlueBlobDetectionSubject(BlobDetectionSubject):
    def __init__(self, session):
        BlobDetectionSubject.__init__(self, session)
        blobDetection = session.service("ALColorBlobDetection")
        blobDetection.setColor(40, 130, 180, 20) # change these values to match the ball color
        blobDetection.setObjectProperties(20, 0.04, "Circle")