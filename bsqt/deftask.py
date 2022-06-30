#!/usr/bin/python3

import time
from PyQt5.QtCore import *

class DefTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

	def __init__(self):
		super().__init__()

	def run(self):
		self.out.emit("Starting")

		time.sleep(2.0)
		self.out.emit("Finished")

		self.complete.emit()
