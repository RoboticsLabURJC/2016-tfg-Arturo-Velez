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
lin = np.zeros((240,320), np.uint8)
center = [120, 160]
refCenter = [160, 120]

href = 0
velX = 1.0
velY = 0.0
velZ = 0.0
sec= 1
secless=0
init = False
size = (0,0)
timeflag=[0,0,0]


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
			lin = np.zeros(size, dtype=np.uint8)
			cv2.rectangle(lin, refPt[0], refPt[1], 255, 2)

	
		if (event == cv2.EVENT_MOUSEMOVE) and (croppingExt == True):
			if len(refMov) == 1:
				refMov.append((x, y))
				lin = np.zeros(size, dtype=np.uint8)
				cv2.rectangle(lin, refMov[0], refMov[1], 255, 2)

			elif len(refMov) == 2:
				refMov[1] = ((x, y))
				lin = np.zeros(size, dtype=np.uint8)
				cv2.rectangle(lin, refMov[0], refMov[1], 255, 2)

	def execute(self):
		input_image = self.camera.getImage()
		

			
		#Check if the vector is longer than a threshold
		def isVector(point0, point1, i):
			return (math.sqrt(((point1[i][0][0]-point0[i][0][0])**2)+((point1[i][0][1]-point0[i][0][1])**2))) > 5 and (math.sqrt(((point1[i][0][0]-point0[i][0][0])**2)+((point1[i][0][1]-point0[i][0][1])**2))) < 30
			
			 	 

		def setROI():
			global refPt, size
			
			refImg = self.camera.getImage()
			size = refImg.shape
			schSize = ((size[1]-10),(size[0]-10))
			refPt = [(10, 10), schSize]


		
		def squareCenter(xmax, xmin, ymax, ymin):
			global center
			center[0] = ((xmax + xmin)/2)
			center[1] = ((ymax + ymin)/2)
		
		def changeTime():
			global sec, secless
			if sec > secless and sec <30:
				secless = sec
				sec = sec + 1
			elif sec < secless + 2 and sec > 2:
				secless = sec
				sec = sec 
			else:
				sec = 1
				secless = 0
			
		
		def changeDirection():
			global velX, velY, sec
			
			if velX != 0.0 and velY == 0.0:
				velY = -velX
				velX = 0.0
			elif velX == 0.0 and velY != 0.0:
				velX = velY
				velY = 0.0 
			
		
		def seek():
			global velX, velY, sec, secless, timeflag
			self.cmdvel.sendCMDVel(velY, velX, 0,0,0,0)
			#print (str(sec) + " SECONDS")
			#time.sleep(sec)
			timenow = datetime.now()
			t = time.mktime(timenow.timetuple())
		
			if t == timeflag[2]:
				changeTime()
				changeDirection()
				timeflag = [0,0,0]
			if t > timeflag[2]:
				timeflag = [0,0,0]
				
				
			print("AT SEEK: " + str(timeflag) + " WHEN " +  str(sec) + " SECONDS AND " + str(t))		
				
		

		#Optical flow function
		def flow(image):
			global opflow_first, previous, unpaired,lin,  refMov, cut,refPt, center, refCenter, init, sec, timeflag
			print("AT INIT: " + str(timeflag)+ " WHEN " +  str(sec) + " SECONDS")
			
			setROI()
			
			
			
			src = image.copy()
			
			src = cv2.medianBlur(src, 3)
			src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
			unpaired = 0
				
			p0 = cv2.goodFeaturesToTrack(src_gray, 100, 0.01, 10, None, None, 7)
			
			index = 0
			if p0 != None:
				for i in (p0):
					if (i[0][0] < refPt[0][0]) or (i[0][0] > refPt[1][0]) or (i[0][1] < refPt[0][1]) or (i[0][1] > refPt[1][1]):
						p0 = np.delete(p0, index, axis=0)
				
					else:
						index = index + 1
			
			
				while(True):
					src2 = self.camera.getImage()
				
					src2 = cv2.medianBlur(src2, 3)
					src2_gray = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)

					p1, st, err = cv2.calcOpticalFlowPyrLK(src_gray, src2_gray, p0, None,
		                                           None, None,
		                                           (30, 30), 2,
		                                           (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
	
										
					if p1 != None:

										
						good_p1 = p1[st==1]
						#print("LENGHT GOOD_P1: " + str(len(good_p1)))
						
						if len(good_p1) == 0:
							maxX = refPt[1][0]
							maxY = refPt[1][1]
							minX = refPt[0][0]
							minY = refPt[0][1]
							cv2.rectangle(src2, (np.int0(minX), np.int0(minY)), (np.int0(maxX), np.int0(maxY)), (255,0,0), 2)
							font = cv2.FONT_HERSHEY_SIMPLEX
							cv2.putText(src2,"All 0", (40,100),font,2,(255,255,255),2)
							timenow = datetime.now()
							t = time.mktime(timenow.timetuple())
							if timeflag[0] == 0 and timeflag[1] == 0:
								timeflag[0] = 1
								timeflag[2] = t + sec							
							seek()
			
							if src2 is not None:
								print("SHOWIIING WHEN NO GOOD")
								self.camera.setColorImage(src2)	
							break					

						#print("NOT BREAK")
						
						maxAll = np.amax(good_p1, axis = 0)
						minAll = np.amin(good_p1, axis = 0)
						maxX = maxAll[0]#[0]
						maxY = maxAll[1]#[1]
						minX = minAll[0]#[0]
						minY = minAll[1]#[1]

						squareCenter(maxX, minX, maxY, minY)
						print(center)	
						velX = ((refCenter[0] - center[0])/refCenter[0])
						velY = ((refCenter[1] - center[1])/refCenter[1])
						print(velX, velY)
						self.cmdvel.sendCMDVel(velY, velX, 0,0,0,0)					
						
				
				
				
					#Max and min point: 0 for x axis, 1 for y axis
			
						for i,(f2,f1) in enumerate(zip(p1,p0)):
					
							a, b = f2.ravel()
							c, d = f1.ravel()
							cv2.circle(src2, (a, b), 5, (0, 255, 0), -1)
							cv2.circle(src2, (c, d), 5, (255, 0, 0), -1)
							cv2.circle(src2, (int(center[0]), int(center[1])), 10, (255, 255, 255), -1)
							cv2.line(src2, (a, b), (c, d), (0,0,255), 2)
							
					
						
						cv2.rectangle(src2, (np.int0(minX), np.int0(minY)), (np.int0(maxX), np.int0(maxY)), (0,255,0), 2)
						font = cv2.FONT_HERSHEY_SIMPLEX
						cv2.putText(src2,str(len(p1)), (40,100),font,2,(255,255,255),2)
						timeflag = [0,0,0]
						sec = 1
						secless = 0
			
						if src2 is not None:
							self.camera.setColorImage(src2)

						src_gray = np.copy(src2_gray)


						p0 = cv2.goodFeaturesToTrack(src_gray, 100, 0.01, 10, None, None, 7)
						index2 = 0
						if p0 != None:
							for p in (p0):
								if (p[0][0] < (np.int0(minX) -2) or p[0][0] > (np.int0(maxX) +2)) or (p[0][1] < (np.int0(minY)-2) or p[0][1] > (np.int0(maxY)+2)):
									p0 = np.delete(p0, index2, axis=0)
								else:
									index2 = index2 + 1

							if len(p0)<10:
								print("INDEX 3")
								cv2.rectangle(src2, (np.int0(minX), np.int0(minY)), (np.copy(maxX), np.int0(maxY)), (0, 255, 0), 2)
								p0 = cv2.goodFeaturesToTrack(src_gray, 100, 0.01, 10, None, None, 7)
								index3 = 0
								for g in (p0):
									if ((g[0][0] < (minX - 20)) or (g[0][0] > (maxX + 20))) or ((g[0][1] < (minY - 20)) or (g[0][1] > (maxY + 20))):
										p0 = np.delete(p0, index3, axis=0)
									else:
										index3 = index3 + 1
					else:
						maxX = refPt[1][0]
						maxY = refPt[1][1]
						minX = refPt[0][0]
						minY = refPt[0][1]
						cv2.rectangle(src2, (np.int0(minX), np.int0(minY)), (np.int0(maxX), np.int0(maxY)), (255,0,0), 2)
						font = cv2.FONT_HERSHEY_SIMPLEX
						cv2.putText(src2,"All 0", (40,100),font,2,(255,255,255),2)
						timenow = datetime.now()
						t = time.mktime(timenow.timetuple())
						if timeflag[0] == 0 and timeflag[1] == 0:
							#print("SECOND FLAG")
							timeflag[1] = 1
							timeflag[2] = t + sec						
						seek()
			
						if src2 is not None:
							print("SHOWIIING")
							self.camera.setColorImage(src2)	
						break						
			else:
				maxX = refPt[1][0]
				maxY = refPt[1][1]
				minX = refPt[0][0]
				minY = refPt[0][1]
				cv2.rectangle(src, (np.int0(minX), np.int0(minY)), (np.int0(maxX), np.int0(maxY)), (255,0,0), 2)
				font = cv2.FONT_HERSHEY_SIMPLEX
				cv2.putText(src,"All 0", (40,100),font,2,(255,255,255),2)
				timenow = datetime.now()
				t = time.mktime(timenow.timetuple())
				if timeflag[0] == 0 and timeflag[1] == 0:
					#print("SECOND FLAG")
					timeflag[1] = 1
					timeflag[2] = t + sec						
				seek()

				if src is not None:
					print("NOOOOOO")
					self.camera.setColorImage(src)	
				
		#Algorythm
		if input_image != None:
	
			flow(input_image)


