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
		
if cameraProxy:
		vc = cameraProxy.getImageData("RGB8")
		height= image.description.height
		width = image.description.width

	
else:
	print 'Interface camera not connected'


#namedWindow("webcam1")
#namedWindow("webcam2")
#vc = VideoCapture(0);



while True:
    next, frame = vc.imread()

	#gray = cvtColor(frame, COLOR_BGR2GRAY)
	#gauss = GaussianBlur(frame, (13,13), 100, 100)
   	#can = Canny(gauss, 0, 30, 3)
   	 
imshow("webcam1", can)
	
#if waitKey(50) >= 0:
#	break;


