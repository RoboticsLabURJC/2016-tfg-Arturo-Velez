import cv2
import numpy as np

capture = cv2.VideoCapture(0)

def colorfilter(cap):

	while(1):
		_, frame = cap.read()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    	
		lower = np.array([110,150,50])
		upper = np.array([130,255,255])
    
		mask = cv2.inRange(hsv, lower, upper)
		res = cv2.bitwise_and(frame,frame, mask= mask)

		cv2.imshow('frame',frame)
		cv2.imshow('mask',mask)
		cv2.imshow('res',res)
    
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break
			
def cannyedge(cap):
	while(1):

		_, frame = cap.read()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		cv2.imshow('Original',frame)
		edges = cv2.Canny(frame,50,100)
		cv2.imshow('Edges',edges)

		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break
			
def laplace(cap):
	while(1):

		_, frame = cap.read()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		medianframe = cv2.medianBlur(frame,15)
    
		laplacian = cv2.Laplacian(medianframe,cv2.CV_64F)
		
		cv2.imshow('Original',frame)
		cv2.imshow('Median', medianframe)
		cv2.imshow('laplacian',laplacian)
		
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break

def sobel(cap):
	while(1):
 
 		_, frame = cap.read()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
		sobelx = cv2.Sobel(frame,cv2.CV_64F,1,0,ksize=5)
		sobely = cv2.Sobel(frame,cv2.CV_64F,0,1,ksize=5)

		cv2.imshow('Original',frame)
		cv2.imshow('sobelx',sobelx)
		cv2.imshow('sobely',sobely)
	
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break

def houghcircles(cap):

	while(1):
		_, frame = cap.read()
		img = cv2.medianBlur(frame,5)
		imgg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
		cimg = cv2.cvtColor(imgg,cv2.COLOR_GRAY2BGR)
		circles = cv2.HoughCircles(imgg,cv2.cv.CV_HOUGH_GRADIENT,1,10,param1=100,param2=30,minRadius=5,maxRadius=20)

		circles = np.uint16(np.around(circles))
		for i in circles[0,:]:
			cv2.circle(cframe,(i[0],i[1]),i[2],(0,255,0),1) # draw the outer circle
			cv2.circle(cframe,(i[0],i[1]),2,(0,0,255),3) # draw the center of the circle
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break
			
def GFTT(cap):
	#_, frame = cap.read()
	frame = cv2.imread(cap)
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)	
		
	corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
	corners = np.int0(corners)

	for i in corners:
		x,y = i.ravel()
		cv2.circle(frame,(x,y),3,255,-1)
			
	cv2.imshow('Original',frame)



print("Estas son las funciones disponibles:")
print("1. ColorFilter")
print("2. Canny Edges")
print("3. Laplacian")
print("4. Filtro Sobel")
print("5. Hough Circles")
print("6. Good features to track")
eleccion = input("Elija una opcion: ")
if eleccion == 1:
	colorfilter(capture)
	cv2.destroyAllWindows()
	capture.release()
elif eleccion == 2:
	cannyedge(capture)
	cv2.destroyAllWindows()
	capture.release()
elif eleccion == 3:
	laplace(capture)
	cv2.destroyAllWindows()
	capture.release()
elif eleccion == 4:
	sobel(capture)
	cv2.destroyAllWindows()
	capture.release()
elif eleccion == 5:
	houghcircles(capture)
	cv2.destroyAllWindows()
	capture.release()
elif eleccion == 6:
	while(1):
		_, frame = capture.read()
		GFTT(frame)
	
	cv2.destroyAllWindows()
	capture.release()	
	


