import QtQuick 2.8
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15

import QtQuick.Controls 2.15
//import QtQuick.Dialogs
import QtQuick.Dialogs 1.3

import "Pages"
import "Common"
import "Components"

ApplicationWindow {

	//
	///
	//// Window Definitions
	///
	//

    id: root

    width: 1280
    height: 800

    visible: true
    title: "bigscraperQt"

	color: colors["back_1"]

	FontLoader { id: outfit; source: "./res/font_outfit/Outfit_Variable.ttf" }

	//
	///
	//// Signals & Settings
	///
	//

	// Signals

	property QtObject backend
	signal runtask(int taskID, var taskData)
	signal doneloading()
	signal checkforcontroller()

	signal togopt(string option)
	signal setopt(string option, string value)
	signal action(string actionid)

	signal log(string msg)
	signal initOptions()

	// Backend Connections

	property int sentData: 0
	Connections {
		target: backend

		function onProgressMsg(msg) {
			workMsg = msg
		}

		function onStatisticsMsg(msg) {
			statsMsg = msg
		}

		function onProgressBar(res) {
			workP.updateProgress(res)
		}

		function onFinishedTask() {
			antiworkTimer.start()
		}

		function onSendSystemsData(data, type) {
			if (type == 0) {
				systemData = data
				resetValues()
				sentData += 1
			} else if (type == 1) {
				exportData = data
				sentData += 1
			} else if (type == 2) {
				defopts = data
				sentData += 1
			} else if (type == 3) {
				inFlatpak = data[0]
				nativeStyle = inFlatpak
				sentData += 1
			} else if (type == 4) {
				appInfo = data
				sentData += 1
			} else if (type == 5) {
				optionValuesInit = data
				sentData += 1
				//console.log("OPTIONS", Object.keys(data), Object.values(data))
			} else if (type == 6) {
				optionValues = data
				sentData += 1
			}


			if (sentData == 7) {
				root.initOptions()
			}
		}

		/*
		function onInputEvent(event, val) {
			if (event == "SOUTH")
				gpOnA()
			if (event == "EAST")
				gpOnB()

			if (event == "LEFT")
				gpOnLeft()
			if (event == "RIGHT")
				gpOnRight()
			if (event == "UP")
				gpOnUp()
			if (event == "DOWN")
				gpOnDown()

			if (event == "RUP")
				gpRUpTimer.running = val
			if (event == "RDOWN")
				gpRDownTimer.running = val

			if (event == "PGLEFT") {
				currentPage -= 1
				if (currentPage < 0) {
					currentPage = 4
				}
			}

			if (event == "PGRIGHT") {
				currentPage += 1
				if (currentPage > 4) {
					currentPage = 0
				}
			}
		}
		*/
	}

	// Task Tabs

	ListModel {
		id: operations

		ListElement {
			cap: false
			working: false
			status: 0
		}

		ListElement {
			cap: true
			working: false
			status: -1
		}
	}

	property int tab: 0

	property bool options: false

	property var colors: {
		"back_1": "#26282d",
		"back_2": "#16171a",
		"back_3": "#1e2126",
		"button": "#16171a",
		"button_highlight": "#1e2126",
		"status_ready": "#5a8eff",
		"status_input": "#ffe878",
		"status_error": "#f7597b",
		"status_select": "#f2f6ff",
		"status_hold": "#7c7f8e",
		"text": "#f2f6ff"
	}

	//
	///
	//// The Actual Interface
	///
	//

	HeaderBar {
		id: header
		width: parent.width
		height: 60

		tabWidth: 180
		tabGutter: 10
	}

	Home {
		id: home

		visible: !operations.get(tab).working && !options

		width: parent.width
		height: parent.height - header.height
		y: header.height
	}

	/*
	Work {
		id: work

		visible: operations.get(tab).working && !options

		width: parent.width
		height: parent.height - header.height
		y: header.height
	}

	Options {
		id: opts

		visible: options

		width: parent.width
		height: parent.height - header.height
		y: header.height
	}
	*/

}
