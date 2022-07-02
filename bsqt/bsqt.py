#!/usr/bin/python3
###
# The Main Script
###

import os, sys, json, shutil, inputs

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


class InputWorker(QThread):
	input_event = pyqtSignal(str, bool)

	leftOnL = True
	rightOnL = True
	upOnL = True
	downOnL = True

	triggerL = True
	triggerR = True

	def __init__(self):
		super().__init__()

	def run(self):
		try:
			while not(self.isInterruptionRequested()):
				events = inputs.get_gamepad()
				for event in events:
					if not(event.code in ["ABS_X", "ABS_Y", "ABS_RX", "ABS_RY", "SYN_REPORT"]):
						print(event.code, event.state)

					# Confirm / Back
					if event.code == "BTN_SOUTH" and event.state == 1:
						self.input_event.emit("SOUTH", True)
					if event.code == "BTN_EAST" and event.state == 1:
						self.input_event.emit("EAST", True)

					# Bumpers
					if event.code == "BTN_TL" and event.state == 1:
						self.input_event.emit("PGLEFT", True)
					if event.code == "BTN_TR" and event.state == 1:
						self.input_event.emit("PGRIGHT", True)

					# Triggers
					if event.code == "ABS_Z":
						if event.state < 50:
							self.triggerL = True
						if event.state > 800 and self.triggerL:
							self.input_event.emit("PGLEFT", True)
							self.triggerL = False

					if event.code == "ABS_RZ":
						if event.state < 50:
							self.triggerR = True
						if event.state > 800 and self.triggerR:
							self.input_event.emit("PGRIGHT", True)
							self.triggerR = False

					# Dpad
					if event.code == "ABS_HAT0X":
						if event.state == -1:
							self.input_event.emit("LEFT", True)
						if event.state == 1:
							self.input_event.emit("RIGHT", True)

					if event.code == "ABS_HAT0Y":
						if event.state == -1:
							self.input_event.emit("UP", True)
						if event.state == 1:
							self.input_event.emit("DOWN", True)

					# Left Stick
					if (event.code == "ABS_X"):
						if abs(event.state) < STICK_DEADZONE:
							self.leftOnL = True
							self.rightOnL = True

						if (event.state < (STICK_THRESHOLD * -1)) and (self.leftOnL):
							self.input_event.emit("LEFT", True)
							self.leftOnL = False

						if (event.state > (STICK_THRESHOLD)) and (self.rightOnL):
							self.input_event.emit("RIGHT", True)
							self.rightOnL = False

					if (event.code == "ABS_Y"):
						if abs(event.state) < STICK_DEADZONE:
							self.upOnL = True
							self.downOnL = True

						if (event.state < (STICK_THRESHOLD * -1)) and (self.upOnL):
							self.input_event.emit("UP", True)
							self.upOnL = False

						if (event.state > (STICK_THRESHOLD)) and (self.downOnL):
							self.input_event.emit("DOWN", True)
							self.downOnL = False

					# Right Stick
					if (event.code == "ABS_RY"):
						if abs(event.state) < STICK_DEADZONE:
							self.input_event.emit("RUP", False)
							self.input_event.emit("RDOWN", False)

						if (event.state < (STICK_THRESHOLD * -1)):
							self.input_event.emit("RUP", True)

						if (event.state > (STICK_THRESHOLD)):
							self.input_event.emit("RDOWN", True)



		except Exception as e:
			print("Input Error: ", e)

	def stop(self):
		self.requestInterruption()
		self.setTerminationEnabled(True)
		self.terminate()
		self.wait()



class MainAppBackend(QObject):
	# Signals
	finishedTask = pyqtSignal()
	progressMsg = pyqtSignal(str, arguments=['msg'])
	sendSystemsData = pyqtSignal(list, int)

	inputEvent = pyqtSignal(str, bool)

	def __init__(self):
		super().__init__()

	def on_load(self):
		# Send Data
		print("[I]: QML Loaded")
		self.sendSystemsData.emit(list(convert.keys()), 0)
		self.sendSystemsData.emit(list(explats.keys()), 1)
		self.sendSystemsData.emit(list(options.values()), 2)
		self.sendSystemsData.emit([in_flatpak], 3)
		self.sendSystemsData.emit(list(info.values()), 4)

		self.input_thread = InputWorker()

		self.input_thread.start()
		self.input_thread.input_event.connect(self.send_input_event)

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

	def send_input_event(self, input_event, val):
		self.inputEvent.emit(input_event, val)


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
