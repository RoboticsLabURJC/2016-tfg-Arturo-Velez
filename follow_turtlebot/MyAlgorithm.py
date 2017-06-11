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
	#Renference values
	imgcentery = 130.0
	imgcenterx = 145.0
	zrefmax = 450.0
	zrefmin = 350.0
	zref = 400.0
		
	#Check how many whites are in the pic
	def chkImg(img):
		Al = len(img)
		An = len(img[0])
		blancos = 0
		for i in range(Al):
			for j in range(An):
				if (img[i][j] != 0):
					blancos = blancos + 1
			
		return blancos
		
	#Check if the whites in-pic is upper than the threshold	
	def isDark(img):
		wh = chkImg(img)
		
		return (wh < 31)
		
	#Check the whites in-pic and adjust the height to the threshold
	def setHeight(img):
		
		blancos = chkImg(img)
		
		if (blancos < zrefmin):
			return ((float(blancos)-zref)/zref)
		elif (blancos > zrefmax):
			return ((float(blancos)-zref)/zref)
		elif (blancos == zref):
			return 0

		#Algorythm
	if input_image != None:
				
		#Filtrado de color
		hsv = cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)
            
		lower = np.array([50,140,50])
		upper = np.array([120,255,255])
	    
		mask = cv2.inRange(hsv, lower, upper)
		maskshow = mask.copy()
		res = cv2.bitwise_and(input_image,input_image, mask= mask)
			
		res = cv2.cvtColor(res, cv2.COLOR_HSV2RGB)
			
		if isDark(mask):
			vz = 1
			vy = 0
			vx = 0
			self.cmdvel.sendCMDVel(vy, vx, vz, 0, 0, 0)
		else:

			_, contours, _= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			cnt = contours[0]
			M = cv2.moments(cnt)
			centroid_x = int(M['m10']/M['m00'])
			centroid_y = int(M['m01']/M['m00'])
			res_b, res_g, res_r = cv2.split(res)
			res_r[centroid_y][centroid_x] = 255
			res_r[centroid_y+1][centroid_x] = 255
			res_r[centroid_y-1][centroid_x] = 255
			res_r[centroid_y][centroid_x+1] = 255
			res_r[centroid_y][centroid_x-1] = 255
			res = cv2.merge([res_r, res_g, res_b])
			
			
			vx = (imgcenterx-float(centroid_x))/imgcenterx
			vy = (imgcentery-float(centroid_y))/imgcentery
			vz = setHeight(mask)
			if (vz == None):
				vz = 0

			print(vz)
			self.cmdvel.sendCMDVel(vy, vx, vz, 0, 0, 0)
			
			
		
	if res != None:
		self.camera.setColorImage(res)
			
		
		
	if maskshow != None:
		self.camera.setThresoldImage(maskshow)


