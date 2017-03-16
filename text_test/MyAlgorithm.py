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
refPt = []
unpaired = 0
numpoints = 90
croppingExt = False
lin = np.zeros((360,640), np.uint8)

cut = False


time_cycle = 80

class MyAlgorithm(threading.Thread):
	global lin

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

	def click_and_crop(self, event, x, y, flags, param):
		# referencias del grab a las variables globales
		global refPt, croppingExt, refMov, lin
		# Si el boton izquierdo del raton se pulsa, graba los primeros (x,y) e indica que el corte (cropping) se esta
		# realizando
		if event == cv2.EVENT_LBUTTONDOWN:
			refPt = [(x, y)]
			refMov = [(x, y)]
			croppingExt = True
		# Mira a ver si el boton izquierdo ha dejado de presionarse
		elif event == cv2.EVENT_LBUTTONUP:
			# guarda las coordenadas finales (x ,y) e indica que el corte (cropping) se ha acabado
			refPt.append((x, y))
			croppingExt = False
			# Dentro de este elif dibujo un rectangulo alrededor de la region de interes
			lin = np.zeros((360, 640), dtype=np.uint8)
			cv2.rectangle(lin, refPt[0], refPt[1], 255, 2)
			print("En click")			
			print(len(refPt))
	
		if (event == cv2.EVENT_MOUSEMOVE) and (croppingExt == True):
			if len(refMov) == 1:
				refMov.append((x, y))
				lin = np.zeros((360, 640), dtype=np.uint8)
				cv2.rectangle(lin, refMov[0], refMov[1], 255, 2)

			elif len(refMov) == 2:
				refMov[1] = ((x, y))
				lin = np.zeros((360, 640), dtype=np.uint8)
				cv2.rectangle(lin, refMov[0], refMov[1], 255, 2)

	def execute(self):
		input_image = self.camera.getImage()
		

		#Check if the point is inside a ROI	
		def isValid(point, i):
			return int(point[i][0][0]) >= roixmin and int(point[i][0][0]) <= roixmax and  int(point[i][0][1]) >= roiymin and int(point[i][0][1]) <= roiymax 
			
		#Check if the vector is longer than a threshold
		def isVector(point0, point1, i):
			return (math.sqrt(((point1[i][0][0]-point0[i][0][0])**2)+((point1[i][0][1]-point0[i][0][1])**2))) > 5 and (math.sqrt(((point1[i][0][0]-point0[i][0][0])**2)+((point1[i][0][1]-point0[i][0][1])**2))) < 30
			
		#Check the outer point
		def outPt (points, c):
			maxPt = points[0][0][c]
			minPt = points[0][0][c]
			minPtindex = 0
			maxPtindex = 0
			for i in range(len(points)):
				if isValid(points, i):
					if maxPt < points[i][0][c]:
						maxPt = points[i][0][c]
						maxPtindex = i
					if minPt > points[i][0][c]:
						minPt = points[i][0][c]
						minPtindex = i
			return maxPt, minPt, minPtindex, maxPtindex 
			 	
		#Check if the ROI is small than a size
		def smallROI(xmax, xmin, ymax, ymin):

			return ((xmax - xmin) < 20 or (ymax - ymin) < 20)  

		def setROI():
			global roixmin, roiymin, roixmax, roiymax, cut, refPt
			
			frame1 = self.camera.getImage()
			gray_frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
			gray_frame1 = gray_frame1[60:420, 0:640]
			img = cv2.add(gray_frame1, lin)
			if not cut:			
				cv2.imshow('ROI SELECTION', img)
				cv2.setMouseCallback('ROI SELECTION', self.click_and_crop)


			while (not cut):
				frame = self.camera.getImage()
				gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				gray_frame = gray_frame[60:420, 0:640]
				img_tru = cv2.add(gray_frame, lin)
				cv2.imshow('ROI SELECTION', img_tru)
				key = cv2.waitKey(1) & 0xFF
				if len(refPt) == 2 and not cut:
					cv2.destroyWindow('ROI SELECTION')
					cut = True
					break
				else:
					continue

			
			roixmin= refPt[0][0]
			roiymin = refPt[0][1]
			roixmax = refPt[1][0]
			roiymax = refPt[1][1]


		def resizeROI(pt0,pt1,imax,imin,c):
			if c == 0:
				roimin = roixmin
				roimax = roixmax
			elif c == 1:
				roimin = roiymin
				roimax = roiymax
			
			if pt1[imin][0][c] < roimin:
				roimin = pt1[imin][0][c]
			if pt1[imax][0][c] > roimax:
				roimax = pt1[imax][0][c]
			if pt1[imin][0][c] > roimin:
				roimin = pt0[imin][0][c]
			if pt1[imax][0][c] < roimax:
				roimax = pt0[imax][0][c]
				
			return roimax, roimin

		def lowPoints(xmax,xmin,ymax,ymin,points):
			count = 0			
			for i in range(len(points)):
				if points[i][0][0] < xmin or points[i][0][0] > xmax or points[i][0][1] < ymin or points[i][0][1] > ymax:
					count = count + 1
			
			return count < 20

		#Optical flow function
		def flow(image):
			global opflow_first, previous, roixmin, roiymin, roixmax, roiymax, unpaired,lin,  refMov, cut,refPt
			setROI()
			print("init")
			print(refPt)
			print(roixmin, roiymin, roixmax, roiymax)
			
			src = image.copy()
			unpaired = 0
				
			if (opflow_first):
				if (previous == None):
					previous = src.copy()
					opflow_first = 0
					del src
					return

			lk_params = dict(winSize  = (31,31), maxLevel = 5, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03))
			criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03)

			img1 =cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
			#img1= cv2.blur(img1,(5,5))
			img2 =cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
			#img2= cv2.blur(img2,(5,5))
			
			
			
			p0 = cv2.goodFeaturesToTrack(img1, numpoints, .01, .01)
			#Max and min point: 0 for x axis, 1 for y axis
			
			maxXpt, minXpt, xindexmin, xindexmax  = outPt(p0, 0)
			maxYpt, minYpt, yindexmin, yindexmax = outPt(p0, 1)
		
			
			
			if (len(p0)>0):
				#cv2.cornerSubPix(img1, p0, (15,15), (-1,-1), criteria)
				p1, st, error = cv2.calcOpticalFlowPyrLK(img1, img2, p0, None, **lk_params)
				 
				roixmax, roixmin = resizeROI(p0,p1,xindexmax,xindexmin, 0)
				roiymax, roiymin = resizeROI(p0,p1,yindexmax,yindexmin, 1)


				for i in range(len(p1)):
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

					if i == xindexmax or i == yindexmax or i == yindexmin or i == xindexmin:
						cv2.circle(src, p, 5, (0,0,255), -1)
						cv2.circle(src, q, 5, (255,255,255), -1)
						cv2.line(src, p, q, line_color, line_thickness, 0)
					else:	
						cv2.circle(src, p, 5, (0,255,0), -1)
						cv2.circle(src, q, 5, (255,0,0), -1)
						cv2.line(src, p, q, line_color, line_thickness, 0)
						
			cv2.rectangle(src, (roixmin,roiymin), (roixmax,roiymax), (0,255,0), thickness=2, lineType=8, shift=0)
			
			previous = image.copy()

			if smallROI(roixmax, roixmin, roiymax, roiymin): 
					cut = False
					print("pre")
					print(refPt)
					refPt = []					
					setROI()
					print("post")
					print(refPt)
			
			del img1
			del img2
			
			
			return src
			
			

		#Algorythm
		if input_image != None:
	
			res = flow(input_image)
			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText(res,str(unpaired), (40,100),font,2,(255,255,255),2)
		
		if res != None:
			self.camera.setColorImage(res)
			
		
		
		#if maskshow != None:
		#	self.sensor.setThresoldImage(maskshow)

