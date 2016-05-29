import cv2
import numpy as np
from sensors import sensor


class MyOpenCV():

	def houghcircles(input_image)
         
		img = cv2.imread(input_image,0)
		img = cv2.medianBlur(img,5)
		cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

		circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,
                          param1=50,param2=30,minRadius=0,maxRadius=0)

		circles = np.uint16(np.around(circles))
		for i in circles[0,:]:
    		# draw the outer circle
    		cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
    		# draw the center of the circle
    		cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

			cv2.imshow('detected circles',cimg)	
			
	def laplacian(input_image)
         
		img = cv2.imread(input_image,0)
		laplacian = cv2.Laplacian(img,cv2.CV_64F)
		cv2.imshow('laplacian',laplacian)	

	def colorfilter(input_image, Hmax, Smax, Vmax, Hmin, Smin, Vmin)
		img = cv2.imread(input_image,0)
    	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    	lower_red = np.array([Hmin,Smin,Vmin])
    	upper_red = np.array([Hmax,Smax,Vmax])
    
    	mask = cv2.inRange(hsv, lower_red, upper_red)
    	res = cv2.bitwise_and(frame,frame, mask= mask)

    	cv2.imshow('color filtered',res)



