#!/usr/bin/python3
###
# The Main Script
###

import os, sys, json, shutil

from yt_dlp import YoutubeDL

from .const import *

from .deftask import DefTask
from .scrapeone import ScrOneTask
from .scrapemany import ScrapeTask
from .export import ExportTask

from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtQml import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ProcessWorker(QObject):
	# Signals
	complete = pyqtSignal()
	progressMsg = pyqtSignal(str)

	task = 0 # Default: Nothing
	task_data = []

	def __init__(self, task_i, task_data_i):
		super().__init__()
		self.task = task_i
		self.task_data = task_data_i.split(";;;")

	def run(self):
		#print("[I]: " + str(self.task_data))
		if (self.task == 0):
			print("[I]: Default Task")

			self.t = DefTask()
			self.t.out.connect(self.report_progress)
			self.t.complete.connect(self.done)
			self.t.run()

		elif (self.task == 1):
			print("[I]: Scrape One Game")

			self.t = ScrOneTask(self.task_data)
			self.t.out.connect(self.report_progress)
			self.t.complete.connect(self.done)
			self.t.run()

		elif (self.task == 2):
			print("[I]: Scrape Folder")

			self.t = ScrapeTask(self.task_data)
			self.t.out.connect(self.report_progress)
			self.t.complete.connect(self.done)
			self.t.run()

		elif (self.task == 3):
			print("[I]: Export")

			self.t = ExportTask(self.task_data)
			self.t.out.connect(self.report_progress)
			self.t.complete.connect(self.done)
			self.t.run()

		else:
			print("[I]: Invalid Task")
			self.done()

	def report_progress(self, msg):
		self.progressMsg.emit(msg)

	def done(self):
		self.complete.emit()


class MainAppBackend(QObject):
	# Signals
	finishedTask = pyqtSignal()
	progressMsg = pyqtSignal(str, arguments=['msg'])
	sendSystemsData = pyqtSignal(list, int)

	sentData = False

	def __init__(self):
		super().__init__()

	def on_load(self):
		# One time send data
		if not(self.sentData):
			self.sentData = True
			self.sendSystemsData.emit(list(convert.keys()), 0)
			self.sendSystemsData.emit(list(explats.keys()), 1)
			self.sendSystemsData.emit(list(options.values()), 2)
			self.sendSystemsData.emit([in_flatpak], 3)
			self.sendSystemsData.emit(list(info.values()), 4)

	def toggle_option(self, option):
		options[option] = not(options[option])
		print("[I]: Changed " + option + " to " + str(options[option]))

		options_json = json.dumps(options, indent = 4)
		open(os.path.join(paths["OPTS"], "options.json"), "w").write(options_json)

	def run_task(self, taskID, taskData):
		# Init worker
		self.thread = QThread()
		self.taskWorker = ProcessWorker(taskID, taskData)
		self.taskWorker.moveToThread(self.thread)

		# Define behaviors on start and finish
		self.thread.started.connect(self.taskWorker.run)
		self.taskWorker.complete.connect(self.thread.quit)
		self.taskWorker.complete.connect(self.finishedTask.emit)

		self.taskWorker.complete.connect(self.taskWorker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)

		self.taskWorker.progressMsg.connect(self.report_progress)
		self.thread.start()

	def report_progress(self, msg):
		print("[O]: " + msg)
		self.progressMsg.emit(msg)


def init_filesystem():
	global options
	# Initialize Directories & Files
	if not(os.path.isdir(paths["OPTS"])):
		os.makedirs(paths["OPTS"])
	if not(os.path.isdir(paths["METADATA"])):
		os.makedirs(paths["METADATA"], exist_ok=True)
	if not(os.path.isdir(paths["MEDIA"])):
		os.makedirs(paths["MEDIA"], exist_ok=True)

	# Get Options if they exist
	if os.path.isfile(os.path.join(paths["OPTS"], "options.json")):
		print("[I]: Reading Options File")
		options_file = json.load(open(os.path.join(paths["OPTS"], "options.json")))
		# If there are changes to options, ensure they are confirmed
		if (len(options_file.keys()) == len(options.keys())):
			options = options_file
		else:
			for opt in options_file.keys():
				if opt in options:
					options[opt] = options_file[opt]
			options_json = json.dumps(options, indent = 4)
			open(os.path.join(paths["OPTS"], "options.json"), "w").write(options_json)

	else:
		print("[I]: Creating Options File")
		options_json = json.dumps(options, indent = 4)
		open(os.path.join(paths["OPTS"], "options.json"), "w").write(options_json)






def main():
	# Main Function

	print("Starting application...")
	print(version_info)

	if (in_flatpak):
		print("SANDBOXED MODE ENABLED")

	app = QApplication(sys.argv)
	app.setApplicationName(info["NAME"])
	app.setApplicationVersion(info["VERSION"])
	app.setOrganizationName("Fr75s")
	app.setWindowIcon(QIcon(os.path.dirname(__file__) + "/res/icon.png"))

	init_filesystem()

	engine = QQmlApplicationEngine()
	engine.quit.connect(app.quit)
	engine.load(os.path.dirname(__file__) + '/main.qml')

	backend = MainAppBackend()
	root = engine.rootObjects()[0]
	root.setProperty('backend', backend)

	root.runtask.connect(backend.run_task)
	root.doneloading.connect(backend.on_load)
	root.togopt.connect(backend.toggle_option)

	sys.exit(app.exec())
