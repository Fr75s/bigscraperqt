import QtQuick 2.8
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15

import QtQuick.Controls 2.15
//import QtQuick.Dialogs
import QtQuick.Dialogs 1.3

import "Pages"
import "CommonUI"

ApplicationWindow {
    id: root

    width: 1280
    height: 800

    visible: true
    title: "Bigscraper-Qt"

	color: "#88" + striphash(colors.window)

	// Backend Connections
	property QtObject backend
	signal runtask(int taskID, var taskData)
	signal doneloading()
	signal checkforcontroller()
	signal togopt(string option)
	signal setopt(string option, string value)

	signal log(string msg)
	signal initOptions()

	property int sentData: 0
	Connections {
		target: backend

		function onProgressMsg(msg) {
			workMsg = msg
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
			} else if (type == 6) {
				optionValues = data
				sentData += 1
			}


			if (sentData == 7) {
				root.initOptions()
			}
		}

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
	}

	Timer {
		id: antiworkTimer
		interval: 3000
		repeat: false
		running: false

		onTriggered: working = false
	}

	Timer {
		id: controllerCheck
		interval: 10000
		repeat: true
		running: true

		onTriggered: root.checkforcontroller()
	}

	Timer {
		interval: 10
		running: true

		onTriggered: root.doneloading()
	}

	// Fonts
	FontLoader { source: "./res/font_outfit/Outfit-Thin.ttf" }
	FontLoader { source: "./res/font_outfit/Outfit-Light.ttf" }
	FontLoader { id: outfit; source: "./res/font_outfit/Outfit-Regular.ttf" }
	FontLoader { source: "./res/font_outfit/Outfit-Medium.ttf" }
	FontLoader { source: "./res/font_outfit/Outfit-Bold.ttf" }

	// Variables
	property string workMsg: "Doing Something..."

	property int currentPage: 0
	property bool working: false

	// Constants
	signal hideOtherDDLR(string excludedLabel)

	property int sidebarWidth: working ? 0 : 0 //96
	property int toolbarHeight: working ? 0 : 42
	property int pageWidthOffset: 96
	property int pageWidth: bg.width - pageWidthOffset

	property bool inFlatpak: false
	property bool nativeStyle: inFlatpak

	property var systemData: []
	property var exportData: []
	property var appInfo: []
	property var defopts: []

	property var optionValuesInit: {}
	property var optionValues: {}

	SystemPalette {
		id: colors
		colorGroup: SystemPalette.Active
	}

	// Menu
	RowLayout {
		width: parent.width * 0.9
		height: toolbarHeight
		visible: !working
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.top: parent.top

		// Native
		MenuItem { visible: nativeStyle; action: homeAction }
		MenuItem { visible: nativeStyle; action: scr1Action }
		MenuItem { visible: nativeStyle; action: scrapeAction }
		MenuItem { visible: nativeStyle; action: exportAction }
		MenuItem { visible: nativeStyle; action: optionsAction }

		// Non-Native
		NNHeaderItem {
			Layout.fillWidth: true; Layout.preferredHeight: parent.height / 1.5
			visible: !nativeStyle; ico: "user-home-symbolic"; label: "Home"
			color: currentPage == 0 ? "#44" + striphash(colors.highlight) : "transparent"
			function pushAction() { currentPage = 0; }
		}
		NNHeaderItem {
			Layout.fillWidth: true; Layout.preferredHeight: parent.height / 1.5
			visible: !nativeStyle; ico: "download-symbolic"; label: "Scrape One"
			color: currentPage == 1 ? "#44" + striphash(colors.highlight) : "transparent"
			function pushAction() { currentPage = 1; }
		}
		NNHeaderItem {
			Layout.fillWidth: true; Layout.preferredHeight: parent.height / 1.5
			visible: !nativeStyle; ico: "folder-symbolic"; label: "Scrape"
			color: currentPage == 2 ? "#44" + striphash(colors.highlight) : "transparent"
			function pushAction() { currentPage = 2; }
		}
		NNHeaderItem {
			Layout.fillWidth: true; Layout.preferredHeight: parent.height / 1.5
			visible: !nativeStyle; ico: "export-symbolic"; label: "Export"
			color: currentPage == 3 ? "#44" + striphash(colors.highlight) : "transparent"
			function pushAction() { currentPage = 3; }
		}
		NNHeaderItem {
			Layout.fillWidth: true; Layout.preferredHeight: parent.height / 1.5
			visible: !nativeStyle; ico: "settings-configure"; label: "Options"
			color: currentPage == 4 ? "#44" + striphash(colors.highlight) : "transparent"
			function pushAction() { currentPage = 4; }
		}

	}

	// Native
	Action {
		id: homeAction; icon.name: "user-home-symbolic"; text: "Home"
		onTriggered: { currentPage = 0; }
	}

	Action {
		id: scr1Action; icon.name: "download-symbolic"; text: "Scrape One"
		onTriggered: { currentPage = 1; }
	}

	Action {
		id: scrapeAction; icon.name: "folder-symbolic"; text: "Scrape"
		onTriggered: { currentPage = 2; }
	}

	Action {
		id: exportAction; icon.name: "export-symbolic"; text: "Export"
		onTriggered: { currentPage = 3; }
	}

	Action {
		id: optionsAction; icon.name: "settings-configure"; text: "Options"
		onTriggered: { currentPage = 4; }
	}

	/*
	Rectangle {
		width: sidebarWidth
		height: parent.height
		anchors.left: parent.left

		color: "transparent"
		visible: !working

		Column {
			anchors.fill: parent
			anchors.margins: parent.width * 0.2
			spacing: parent.width * 0.2

			BsqtButton {
				id: homeButton
				width: parent.width
				height: width

				icon.name: "user-home-symbolic"

				onClicked: { currentPage = 0; root.doneloading() }
			}

			BsqtButton {
				id: oneButton
				width: parent.width
				height: width
				icon.name: "arrow-down"

				onClicked: { currentPage = 1; root.doneloading() }
			}

			BsqtButton {
				id: manyButton
				width: parent.width
				height: width

				icon.name: "folder-symbolic"

				onClicked: { currentPage = 2; root.doneloading() }
			}

			BsqtButton {
				id: exportButton
				width: parent.width
				height: width
				icon.name: "document-export"

				onClicked: { currentPage = 3; root.doneloading() }
			}

			BsqtButton {
				id: optsButton
				width: parent.width
				height: width
				icon.name: "settings-configure"

				onClicked: { currentPage = 4; root.doneloading() }
			}
		}
	}
	*/

	// Background
	Rectangle {
		id: bg
		width: parent.width - sidebarWidth
		height: parent.height - toolbarHeight
		anchors.right: parent.right
		anchors.bottom: parent.bottom

		color: colors.window
	}

	// Pages
	Home { id: homeP; visible: currentPage == 0 && !working }
	ScrapeOne { id: scrapeOneP; visible: currentPage == 1 && !working }
	ScrapeMany { id: scrapeP; visible: currentPage == 2 && !working }
	Export { id: exportP; visible: currentPage == 3 && !working }
	Options { id: optionsP; visible: currentPage == 4 && !working }

	Work { id: workP; visible: working }

	function striphash(instr) {
		let outv = instr + ""
		return outv.replace("#", "")
	}

	function fileBasename(fileUrl) {
		return fileUrl.toString().split("/").reverse()[0]
	}

	function dirFromFileUrl(fileUrl) {
		return fileUrl.toString().substring(0, fileUrl.toString().lastIndexOf("/") + 1)
	}

	function folderPath(folderUrl) {
		return folderUrl.toString().replace("file://", "")
	}


	// Gamepad Controls
	Timer {
		id: gpRUpTimer

		interval: 75
		repeat: true
		running: false

		onTriggered: {
			switch(currentPage) {
				case 1:
					scrapeOneP.gpOnRUp()
					break
				case 2:
					scrapeP.gpOnRUp()
					break
				case 3:
					exportP.gpOnRUp()
					break
			}
		}
	}

	Timer {
		id: gpRDownTimer

		interval: 75
		repeat: true
		running: false

		onTriggered: {
			switch(currentPage) {
				case 1:
					scrapeOneP.gpOnRDown()
					break
				case 2:
					scrapeP.gpOnRDown()
					break
				case 3:
					exportP.gpOnRDown()
					break
			}
		}
	}

	// Push Actions
	function gpOnLeft() {
		switch(currentPage) {
			case 0:
				homeP.gpOnLeft()
				break
		}
	}

	function gpOnRight() {
		switch(currentPage) {
			case 0:
				homeP.gpOnRight()
				break
		}
	}

	function gpOnUp() {
		switch(currentPage) {
			case 1:
				scrapeOneP.gpOnUp()
				break
			case 2:
				scrapeP.gpOnUp()
				break
			case 3:
				exportP.gpOnUp()
				break
			case 4:
				optionsP.gpOnUp()
				break
		}
	}

	function gpOnDown() {
		switch(currentPage) {
			case 1:
				scrapeOneP.gpOnDown()
				break
			case 2:
				scrapeP.gpOnDown()
				break
			case 3:
				exportP.gpOnDown()
				break
			case 4:
				optionsP.gpOnDown()
				break
		}
	}

	function gpOnA() {
		switch(currentPage) {
			case 0:
				homeP.gpOnA()
				break
			case 1:
				scrapeOneP.gpOnA()
				break
			case 2:
				scrapeP.gpOnA()
				break
			case 3:
				exportP.gpOnA()
				break
			case 4:
				optionsP.gpOnA()
				break
		}
	}

	function gpOnB() {
		switch(currentPage) {
			case 0:
				Qt.quit()
			case 1:
				scrapeOneP.gpOnB()
				break
			case 2:
				scrapeP.gpOnB()
				break
			case 3:
				exportP.gpOnB()
				break
			case 4:
				optionsP.gpOnB()
				break
		}
	}



	function resetValues() {
		exportP.resetValues()
		scrapeP.resetValues()
		scrapeOneP.resetValues()
	}
}
