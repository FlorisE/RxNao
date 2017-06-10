from __future__ import print_function
from rx import *
from naoqi import *
from rxqi import *
import threading

nao_address = "tcp://192.168.10.2:9559"
session = qi.Session(nao_address)

blueBlobDetection = BlueBlobDetectionSubject(session)
blueBlobDetection.daemon = True
blueBlobDetection.start()

tracker = session.service("ALTracker")
tracker.trackEvent("ALTracker/ColorBlobDetected")

blue_blobs = blueBlobDetection.subject.map(lambda item: Blob(item))
blue_blobs_samples = blue_blobs.sample(1000)
blue_blobs_windows = blue_blobs.window_with_time(1000)

def process(window):
    #distances = window.map(lambda item: item.distance())
    #window.scan(lambda previous, current: previous if current in previous else previous + [current], []).map(lambda lst: len(lst)).subscribe(print)
    window.scan(add_or_merge, []).map(len).subscribe(print)

def add_or_merge(existing, new):
    merged = False
    for item in existing:
        if item == new:
            merged = True
            item.merge_from(new)
            break
    if not merged:
        existing.append(new)

blue_blobs_windows.subscribe(process)

while(True):
    pass