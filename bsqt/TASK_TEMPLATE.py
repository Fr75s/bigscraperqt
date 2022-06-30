#!/usr/bin/python3

import os, sys, json, shutil, requests
from lxml import html

from .const import *

from PyQt5.QtCore import *

class DefTask(QObject):
	complete = pyqtSignal()
	out = pyqtSignal(str)

	data = []

	def __init__(self):
		super().__init__()
		self.data = data_i

	def run(self):
		self.out.emit("OUTPUT")

		# Actions

		self.complete.emit()
