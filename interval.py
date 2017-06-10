from __future__ import print_function
from rx import *
from naoqi import *
from rxqi import *
import threading
from enum import Enum
import random

ass = Observable.interval(500).map(lambda x: (x, "a", random.randint(1, 100)))
bss = Observable.interval(400).map(lambda x: (x, "b", random.randint(1, 100)))
css = Observable.interval(100).map(lambda x: (x, "c", random.randint(1, 100)))

streams = [ass, bss, css]

Observable.merge(
    *streams
).window_with_time(
    1000
).map(
    lambda observable: observable.min(lambda x, y: x[2] - y[2])
).subscribe(
    lambda observable: observable.subscribe(print)
)
