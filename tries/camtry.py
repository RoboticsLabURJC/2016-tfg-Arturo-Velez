from cv2 import *
import sys, traceback, Ice
import easyiceconfig as EasyIce
import jderobot
import numpy as np
import threading


ic = EasyIce.initialize(sys.argv)
properties = ic.getProperties()
basecamera = ic.propertyToProxy("Introrob.Camera.Proxy")
			
cameraProxy = jderobot.CameraPrx.checkedCast(basecamera)
		
try:
	ic = EasyIce.initialize(sys.argv)
	properties = ic.getProperties()
	basecamera = ic.propertyToProxy("Camtry.Camera.Proxy")
	cameraProxy = jderobot.CameraPrx.checkedCast(basecamera)

	if cameraProxy:
		image = cameraProxy.getImageData("RGB8")
		height= image.description.height
		width = image.description.width

		trackImage = np.zeros((height, width,3), np.uint8)
		trackImage.shape = height, width, 3
	
		thresoldImage = np.zeros((height, width,1), np.uint8)
		thresoldImage.shape = height, width,

	else:
		print 'Interface camera not connected'

def update():
	lock.acquire()
	updateCamera()
	lock.release()

def updateCamera():
	if cameraProxy:
		image = cameraProxy.getImageData("RGB8")
		height= image.description.height
		width = image.description.width


def getImage():
	if .cameraProxy:
		lock.acquire()
		img = np.zeros((height, width, 3), np.uint8)
		img = np.frombuffer(image.pixelData, dtype=np.uint8)
		img.shape = height, width, 3
		lock.release()
		return img;

	return None



while True:
    #next, frame = vc.imread()

	#gray = cvtColor(frame, COLOR_BGR2GRAY)
	#gauss = GaussianBlur(frame, (13,13), 100, 100)
   	#can = Canny(gauss, 0, 30, 3)
   	 
imshow("webcam1", can)
	
#if waitKey(50) >= 0:
#	break;


