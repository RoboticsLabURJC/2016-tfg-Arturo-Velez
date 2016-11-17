from sensors import sensor
from gui import colorFilterWidget as CFW
import cv2
import numpy as np
import math

opflow_first = 1
previous = None

class MyAlgorithm():
	
	def __init__(self, sensor):
		self.sensor = sensor
		self.CFW = CFW
	
				
      
	def execute(self):
		input_image = self.sensor.getImage()
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
			elif (blancos == zref ):
				return 0
				
		#Optical flow function
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
						continue
					line_thickness = 1
					line_color = (255, 0, 0)

					p = (int(p0[i][0][0]), int(p0[i][0][1]))
					q = (int(p1[i][0][0]), int(p1[i][0][1]))
					print p

					#angle = math.atan2(p[1]-q[1], p[0]-q[0])
					#hypotenuse = math.sqrt(((p[1]-q[1])**2) + ((p[0]-q[0])**2))
					
					#q[0] = int(p[0]-1*hypotenuse*math.cos(angle))
					#q[1] = int(p[1]-1*hypotenuse*math.cos(angle))
					cv2.line(src, p, q, line_color, line_thickness, 0)

			image = src.copy()
			previous = image.copy()
			
			del img1
			del img2
			del src
			
			return image
			
			

		#Algorythm
		if input_image != None:
			
			
			res = flow(input_image)
			
		
		if res != None:
			print("alright!")
			self.sensor.setColorImage(res)
			
		
		
		#if maskshow != None:
		#	self.sensor.setThresoldImage(maskshow)

