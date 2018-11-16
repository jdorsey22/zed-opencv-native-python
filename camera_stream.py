################################################################################

# threaded frame capture from camera to avoid camera frame buffering delays
# (always delivers the latest frame from the camera)

# Copyright (c) 2018 Toby Breckon, Durham University, UK
# Copyright (c) 2015-2016 Adrian Rosebrock, http://www.pyimagesearch.com
# MIT License (MIT)

# based on code from this tutorial, with changes to make object method call compatible
# with cv2.VideoCapture(src) as far as possible:
# https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

################################################################################

# import the necessary packages

from threading import Thread
import cv2

################################################################################

class CameraVideoStream:
	def __init__(self, name="CameraVideoStream"):

		# initialize the thread name
		self.name = name

		# initialize the variables used to indicate if the thread should
		# be stopped or suspended
		self.stopped = False
		self.suspend = False

		# set these to null values initially
		self.grabbed = 0;
		self.frame = None;

	def open(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.camera = cv2.VideoCapture(src)
		(self.grabbed, self.frame) = self.camera.read()

		# only start the thread if in-fact the camera read was successful
		if (self.grabbed):
			# start the thread to read frames from the video stream
			t = Thread(target=self.update, name=self.name, args=())
			t.daemon = True
			t.start()

		return (self.grabbed > 0);

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				self.grabbed = 0; # set flag to ensure isOpen() returns False
				self.camera.release(); # cleanly release camera hardware
				return

			# otherwise, read the next frame from the stream
			# provided we are not suspended

			if not(self.suspend):
				(self.grabbed, self.frame) = self.camera.read()

	def read(self):
		# return the frame most recently read
		return (self.grabbed, self.frame)

	def isOpened(self):
		# indicate that the camera is open successfully
		return (self.grabbed > 0);

	def release(self):
		# indicate that the thread should be stopped
		self.stopped = True

	def set(self, property_name, property_value):
		# set a video capture property (behavior as per OpenCV manual for VideoCapture)

		# first suspend thread
		self.suspend = True;

		# set value - wrapping it in grabs() so it takes effect
		self.camera.grab()
		ret_val = self.camera.set(property_name, property_value)
		self.camera.grab()

		# whilst we are still suspended flush the frame buffer held inside
		# the object by reading a new frame with new settings otherwise a race
		# condition will exist between the thread's next call to update() after
		# it un-suspends and the next call to read() by the object user
		(self.grabbed, self.frame) = self.camera.read()

		# restart thread by unsuspending it
		self.suspend = False;

		return ret_val;

	def get(self, property_name):
		# get a video capture property (behvavior as per OpenCV manual for VideoCapture)
		return self.camera.get(property_name)

	def getBackendName():
		 # get a video capture backend (behvavior as per OpenCV manual for VideoCapture)
		 return self.camera.getBackendName()

################################################################################
