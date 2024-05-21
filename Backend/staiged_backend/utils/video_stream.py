import cv2
from threading import Thread
import os


class VideoStream:
    def __init__(self, src=0, resolution=(320, 240), framerate=32, name="VideoStream"):
        os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
        self.stream = cv2.VideoCapture(src)
        self.name = name
        self.stopped = False
        (self.grabbed, self.frame) = self.stream.read()

    def start(self):
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while not self.stopped:
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream = None
