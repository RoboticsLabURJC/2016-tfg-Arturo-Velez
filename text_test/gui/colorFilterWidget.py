#
#  Copyright (C) 1997-2015 JDE Developers Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#  Authors :
#       Alberto Martin Florido <almartinflorido@gmail.com>
#

from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import (QBrush, QPainter, QPen, QPixmap, QColor)
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QWidget)
import cv2
import os


class ColorFilterWidget(QtGui.QWidget):

	IMAGE_COLS_MAX=640
	IMAGE_ROWS_MAX=360
	imageUpdate=QtCore.pyqtSignal()

    def __init__(self,winParent):      

		super(ColorFilterWidget, self).__init__()
		self.winParent=winParent

		self.imageUpdate.connect(self.updateImage)
		mainLayout = QVBoxLayout()

		self.setMouseTracking(False)
		self.setMinimumSize(QSize(640,480))	
		self.setLayout(mainLayout)
		self.setWindowTitle("Basic ROI")

		self.startPoint = QPoint(-10,-10)
		self.endPoint = QPoint(-10,-10)

	def mousePressEvent(self, event):

		if(event.buttons() == Qt.LeftButton): 	# Si se ha pulsado el boton izquierdo

			print("Left pressed")
			self.startPoint.setX(event.x())
			self.startPoint.setY(event.y())

		if(event.buttons() == Qt.RightButton):	# Si se ha pulsado el boton derecho

			self.startPoint = QPoint(-10,-10)
			self.endPoint = QPoint(-10,-10)
			self.update()	# se llama a PaintEvent para que se borre el ROI que hubiera


	def mouseReleaseEvent(self, event):

		print("released")
		self.endPoint.setX(event.x())
		self.endPoint.setY(event.y())
		print(self.startPoint, self.endPoint)

	def mouseMoveEvent(self, event):

		print("Mouse moved")
		self.endPoint.setX(event.x())
		self.endPoint.setY(event.y())
		self.update()	# Repintamos cada vez que el ratÛn se mueva.

	def closeEvent(self, event):

		event.accept()

	def setColorImage(self):

		img = self.winParent.getSensor().getColorImage()
		painter = QPainter(self)

		if img != None:

 			image = QtGui.QImage(img.data, img.shape[1], img.shape[0], img.shape[1] * img.shape[2], QtGui.QImage.Format_RGB888)
			painter.drawPixmap(0,0,640,480,QPixmap("image"))       		

	def updateImage(self):

		self.setColorImage()

	def closeEvent(self, event):

 		self.winParent.closeColorFilterWidget()
