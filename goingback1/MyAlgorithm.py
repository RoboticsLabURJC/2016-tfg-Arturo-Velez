import threading
import time
from datetime import datetime
import cv2
import numpy as np

from sensors.cameraFilter import CameraFilter
from parallelIce.navDataClient import NavDataClient
from parallelIce.cmdvel import CMDVel
from parallelIce.extra import Extra
from parallelIce.pose3dClient import Pose3DClient

opflow_first = 1
previous = None


time_cycle = 80

class MyAlgorithm(threading.Thread):

    def __init__(self, camera, navdata, pose, cmdvel, extra):
        self.camera = camera
        self.navdata = navdata
        self.pose = pose
        self.cmdvel = cmdvel
        self.extra = extra

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

    def run (self):

        self.stop_event.clear()

        while (not self.kill_event.is_set()):
           
            start_time = datetime.now()

            if not self.stop_event.is_set():
                self.execute()

            finish_Time = datetime.now()

            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop (self):
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()


    def execute(self):
	input_image = self.camera.getImage()
	
	def flow(image):
			global opflow_first
			global previous
			src = image.copy()
			if (opflow_first):
				if (previous == None):
					previous = src.copy()
					opflow_first = 0
					del src
					return

			criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03)
			lk_params = dict(winSize  = (31,31), maxLevel = 5, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03))

			img1 =cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
			img1= cv2.blur(img1,(5,5))
			img2 =cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
			img2= cv2.blur(img2,(5,5))
			
			numpoints = 90
			
			p0 = cv2.goodFeaturesToTrack(img1, numpoints, .01, .01)
			
			if (len(p0)>0):
				cv2.cornerSubPix(img1, p0, (15,15), (-1,-1), criteria)
				p1, st, error = cv2.calcOpticalFlowPyrLK(img1, img2, p0, None, **lk_params)

				for i in range(numpoints):
					if (st[i] == 0):
						p = (int(p0[i][0][0]), int(p0[i][0][1]))
						q = (int(p1[i][0][0]), int(p1[i][0][1]))
						cv2.circle(src, p, 5, (255,255,0), -1)
						cv2.circle(src, q, 5, (0,255,255), -1)
					
					line_thickness = 1
					line_color = (0, 0, 255)
					
					
					p = (int(p0[i][0][0]), int(p0[i][0][1]))
					q = (int(p1[i][0][0]), int(p1[i][0][1]))
					cv2.circle(src, p, 5, (0,255,0), -1)
					cv2.circle(src, q, 5, (255,0,0), -1)
					cv2.line(src, p, q, line_color, line_thickness, 0)
						

			
			previous = image.copy()
			
			del img1
			del img2
			
			
			return src

			
			

		#Algorythm
	if input_image != None:
		res = flow(input_image)
			
		
	if res != None:
		print("alright!")
		self.camera.setColorImage(res)


