from PyQt4 import QtGui,QtCore


class CameraWidget(QtGui.QWidget):
	IMAGE_COLS_MAX=640
	IMAGE_ROWS_MAX=360
	LINX=0.3
	LINY=0.3
	LINZ=0.8
	ANGZ=1.0
	ANGY=0.0
	ANGX=0.0

	imageUpdate=QtCore.pyqtSignal()

	def __init__(self,winParent):  
		super(CameraWidget, self).__init__()
		self.winParent=winParent
		self.imageUpdate.connect(self.updateImage)
		self.initUI()

	def initUI(self):
	
		self.setMinimumSize(680,500)
		self.setMaximumSize(680,500)

		self.setWindowTitle("Camera")
		changeCamButton=QtGui.QPushButton("Change Camera")
		changeCamButton.resize(170,40)
		changeCamButton.move(245,450)
		changeCamButton.setParent(self)
		changeCamButton.clicked.connect(self.changeCamera)

		self.imgLabel=QtGui.QLabel(self)
		self.imgLabel.resize(self.IMAGE_COLS_MAX,self.IMAGE_ROWS_MAX)
		self.imgLabel.move(10,5)
		self.imgLabel.show()

	def updateImage(self):

		img = self.winParent.getSensor().getImage()
		if img != None:
			image = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*img.shape[2], QtGui.QImage.Format_RGB888);

			if img.shape[1]==self.IMAGE_COLS_MAX:
				x=20
			else:
				x=(self.IMAGE_COLS_MAX+20)/2-(img.shape[1]/2)
			if img.shape[0]==self.IMAGE_ROWS_MAX:
				y=40
		else:
			y=(self.IMAGE_ROWS_MAX+40)/2-(img.shape[0]/2)

		size=QtCore.QSize(img.shape[1],img.shape[0])
		self.imgLabel.move(x,y)
		self.imgLabel.resize(size)
		self.imgLabel.setPixmap(QtGui.QPixmap.fromImage(image))

	def closeEvent(self, event):
		self.winParent.closeCameraWidget()

	def changeCamera(self):
		self.winParent.getSensor().toggleCam()
