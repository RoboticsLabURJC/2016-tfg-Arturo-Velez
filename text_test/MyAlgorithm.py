from sensors import sensor
from gui import colorFilterWidget as CFW
import cv2
import numpy as np
import math


opflow_first = 1
previous = None
roixmin = 225
roixmax = 425
roiymin = 150
roiymax = 350
unpaired = 0

class MyAlgorithm():
	
	def __init__(self, sensor):
		self.sensor = sensor
		self.CFW = CFW
	
				
      
	def execute(self):
		input_image = self.sensor.getImage()
		
		#Check if the point is inside a ROI	
		def isValid(point, i):
			return int(point[i][0][0]) >= roixmin and int(point[i][0][0]) <= roixmax and  int(point[i][0][1]) >= roiymin and int(point[i][0][1]) <= roiymax 
			
		#Check if the vector is longer than a threshold
		def isVector(point0, point1, i):
			return (math.sqrt(((point1[i][0][0]-point0[i][0][0])**2)+((point1[i][0][1]-point0[i][0][1])**2))) > 5 and (math.sqrt(((point1[i][0][0]-point0[i][0][0])**2)+((point1[i][0][1]-point0[i][0][1])**2))) < 30
			
		#Check if the ROI is small than a size
		def smallROI(xmax,xmin,ymax,ymin):
		 return (xmax - xmin) < 10 or (ymax - ymin) < 10 
		 
		def setROI (event, x, y):
			global roixmin, roiymin, roixmax, roiymax
			print(event)
			
			if event == cv2.EVENT_LBUTTONDOWN:
				roixmin = x
				roiymin = y
			elif event == cv2.EVENT_LBUTTONUP:
				roixmax = x
				roiymax = y
		  
				
		#Optical flow function
		def flow(image):
			global opflow_first, previous, roixmin, roiymin, roixmax, roiymax, unpaired
			
			src = image.copy()
			unpaired = 0
				
			if (opflow_first):
				if (previous == None):
					previous = src.copy()
					opflow_first = 0
					del src
					return

			criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03)
			lk_params = dict(winSize  = (31,31), maxLevel = 5, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03))

			img1 =cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
			#img1= cv2.blur(img1,(5,5))
			img2 =cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
			#img2= cv2.blur(img2,(5,5))
			
			numpoints = 90
			
			p0 = cv2.goodFeaturesToTrack(img1, numpoints, .01, .01)
			
			if (len(p0)>0):
				#cv2.cornerSubPix(img1, p0, (15,15), (-1,-1), criteria)
				p1, st, error = cv2.calcOpticalFlowPyrLK(img1, img2, p0, None, **lk_params)


				for i in range(numpoints):
					if (st[i] == 0):
						p = (int(p0[i][0][0]), int(p0[i][0][1]))
						q = (int(p1[i][0][0]), int(p1[i][0][1]))
						unpaired = unpaired + 1
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
			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText(res,str(unpaired), (40,100),font,2,(255,255,255),2)
		
		if res != None:
			self.sensor.setColorImage(res)
			
		
		
		#if maskshow != None:
		#	self.sensor.setThresoldImage(maskshow)

