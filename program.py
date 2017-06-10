from rx import *
from naoqi import *
import datetime
from rx.subjects import Subject
from threading import Thread
from math import *
import sys, time

nao_address = "tcp://127.0.0.1:9559"

session = qi.Session(nao_address)

from __future__ import print_function

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

		
class QiPullingMemorySubject(Thread):
    def __init__(self, field, session, pull_rate):
        Thread.__init__(self)
        self.session = session
        self.field = field
        self.pull_rate = pull_rate / 1000.0
        self.stopped = False
        self.subject = Subject()
        
    def run(self):
        mem = self.session.service("ALMemory")
        #latched_data = 0
        while not self.stopped:
            data = mem.getData(self.field)
            
            #if data < latched_data - 0.02 or data > latched_data + 0.02:
            self.subject.on_next(data)
            #    latched_data = data
            time.sleep(self.pull_rate)
        
    def stop(self):
        self.stopped = True
        print("Stopping")

		
class RedBallSubject(QiMemorySubject):
    def __init__(self, session):
        QiMemorySubject.__init__(self, "redBallDetected", session)

		
class HeadYawSubject(QiPullingMemorySubject):
    def __init__(self, session):
        QiPullingMemorySubject.__init__(self, "Device/SubDeviceList/HeadYaw/Position/Sensor/Value", session, 10)
		
		
redBallThread = RedBallSubject(session)
redBallThread.daemon = True
redBallThread.start()

leds = session.service("ALLeds")
leds.off("FaceLeds")

headYawThread = HeadYawSubject(session)
headYawThread.daemon = True
headYawThread.start()


class Ball():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
		

ball = redBallThread.subject.map(lambda ballInfo: Ball(ballInfo[1][0], ballInfo[1][1], ballInfo[1][2], ballInfo[1][3]))
head_yaw = headYawThread.subject
Stream = Observable


def led_brightness(intensity):
    leds.setIntensity("RightFaceLedsRed", intensity)
    leds.setIntensity("LeftFaceLedsRed", intensity)
	
	
def head_tracker(distance): print("head")
def head_body_tracker(distance): print("head and body")
def arm_tracker(arm): print(arm)


### Shared parts for both examples
## Global variables
# ball size
size = 4
## Functions
# calculating distance to a circular object using two parameters
dist2 = lambda width, height: (1/4.) * (size/tan(width) + size/tan(height))
# calculating distance to a ball using dist2
ball_distance = lambda ball: dist2(ball.width, ball.height)
## CEP graph
ballSamples = ball.sample(500)
distance = ballSamples.map(ball_distance)


### Example 1 specific
## Functions
# function for determining brightness from distance
def brightness(distance):
    if distance > 20:
        return 0
    elif distance > 5:
        return (-(distance-5)/15.) + 1
    else:
        return 1
## CEP graph
brightness = distance.map(brightness)
led_subscription = brightness.subscribe(led_brightness)


### Example 2 specific
## Functions
# mapping ball to a pair containing its x angle and distance
angle_dist_helper = lambda ball: (ball.x, dist2(ball.width, ball.height))
# combining head_yaw with robot_angle
combinator = lambda headYaw, ballAngle: (headYaw.value+ballAngle.value, 
                                         headYaw.timestamp-ballAngle.timestamp)
recent = lambda pair: pair[1].total_seconds() < 1
## CEP graph
# distance to head and head & body
head = distance.filter(lambda d: d >= 50)
head_subscription = head.subscribe(head_tracker)
head_body = distance.filter(lambda d: d >= 20 and d < 50)
head_body_subscription = head_body.subscribe(head_body_tracker)
# BallSamples to Camera angle time
cam_angle_dist = ballSamples.map(angle_dist_helper)
cam_angle_dist_filtered = cam_angle_dist.filter(lambda pair: pair[1] < 20)
cam_angle = cam_angle_dist_filtered.map(lambda pair: pair[0])
# product of object's camera angle and head yaw
cam_angle_timestamped = cam_angle.timestamp()
head_yaw_timestamped = head_yaw.timestamp()
robot_angle_timestamped = Stream.combine_latest(head_yaw_timestamped, 
                                                cam_angle_timestamped, 
                                                combinator)
robot_angle = robot_angle_timestamped.filter(recent)
arm = robot_angle.map(lambda a: "LArm" if a[0] > 0 else "RArm")
arm_subscription = arm.subscribe(arm_tracker)