import unittest2
from mock import MagicMock
from subjects import RedColorBlobSubject, BlueColorBlobSubject, RedBallTrackerSubject


class TestRedColorBlobSubject(unittest2.TestCase):
    
    def test_create(self):
        module = MagicMock()
        proxy = MagicMock()
        RedColorBlobSubject(module, proxy)


class TestBlueColorSubject():

    def test_create(self):
        module = MagicMock()
        proxy = MagicMock()
        BlueColorSubject(module, proxy)


class TestRedBallDetectionSubject():

    def test_create(self):
        module = MagicMock()
        proxy = MagicMock()
        RedBallTrackerSubject(module, proxy)


if __name__ == "__main__":
    unittest2.main()
