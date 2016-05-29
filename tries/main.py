import sys
#from MyAlgorithm import MyAlgorithm
from sensors import Sensor
#from sensors.threadSensor import ThreadSensor
#from gui.threadGUI import ThreadGUI
from GUI import MainWindow
from PyQt4 import QtGui

import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
	sensor = Sensor()
	app = QtGui.QApplication(sys.argv)
	frame = MainWindow()
	frame.setSensor(sensor)
	frame.show()
	#algorithm=MyAlgorithm(sensor)
	#t1 = ThreadSensor(sensor,algorithm)  
	#t1.daemon=True
	#t1.start()

	#t2 = ThreadGUI(frame)  
	#t2.daemon=True
	#t2.start()
    
	sys.exit(app.exec_()) 
