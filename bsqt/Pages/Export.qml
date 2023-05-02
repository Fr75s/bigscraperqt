import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
//import QtQuick.Dialogs
import QtQuick.Dialogs 1.3

import "../CommonUI"

Item {
	id: exportPage
	anchors.fill: parent

	property var chosenFolder: ""
	property var chosenSystem: ""
	property var chosenExport: ""

	property int gpFocus: -1

	PageTitle {
		id: exportTitle
		text: "Export Data"
	}

	ButtonLabelRow {
		id: gameFolderSelect
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: exportTitle.bottom
		anchors.topMargin: 24

		focused: gpFocus == 0

		label: "Select Output Folder"
		btnIcon: (chosenFolder == "") ? "folder-symbolic" : ""
		btnLabel: folderPath(chosenFolder)

		function pushAction() {
			exportFolderSelect.open()
		}
	}

	/*
	ButtonLabelChoice {
		id: exportSelect
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: gameFolderSelect.bottom
		anchors.topMargin: 24

		label: "Select Export Type"
		choiceA: "Pegasus Frontend"
		choiceB: "EmulationStation"

		function pushActionA() {
			chosenExport = "pegasus"
			console.log("[UI]: Set Export (" + chosenExport + ")")
		}
		function pushActionB() {
			chosenExport = "es"
			console.log("[UI]: Set Export (" + chosenExport + ")")
		}
	}
	*/

	DDLabelRow {
		id: systemSelect
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: gameFolderSelect.bottom
		anchors.topMargin: 24

		focused: gpFocus == 1

		label: "Select System"
		btnIcon: (chosenSystem == "") ? "input-gamepad-symbolic" : ""
		btnLabel: chosenSystem
		dropDownModel: systemData

		function pushAction(md) {
			chosenSystem = md
			root.log("Selected System (" + md + ")")
		}

		z: 30
	}

	DDLabelRow {
		id: exportSelect
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: systemSelect.bottom
		anchors.topMargin: 24

		focused: gpFocus == 2

		label: "Export Type"
		btnIcon: (chosenExport == "") ? "export-symbolic" : ""
		btnLabel: chosenExport
		dropDownModel: exportData

		function pushAction(md) {
			chosenExport = md
			root.log("Selected Export (" + md + ")")
		}

		z: 20
	}



	BsqtButton {
		id: beginOneStep

		anchors.bottom: parent.bottom
		anchors.bottomMargin: 48

		focus: gpFocus == 3

		anchors.left: parent.left
		anchors.leftMargin: sidebarWidth + pageWidthOffset / 2

		width: pageWidth * 0.25
		height: 72

		label: "Begin"
		btnhighlight: true

		onClicked: {
			if (chosenFolder != "" && chosenSystem != "" && chosenExport != "") {
				working = true;
				runtask(3, chosenFolder + ";;;" + chosenSystem + ";;;" + chosenExport);
			}
		}
	}


	/*
	FolderDialog {
		id: exportFolderSelect
		title: "Choose Export Path"
		currentFolder: homeFolder

		modality: Qt.ApplicationModal

		acceptLabel: "Select"

		onAccepted: {
			chosenFolder = selectedFolder
			console.log("[UI]: Selected Folder (" + selectedFolder + ")")
		}
	}
	*/


	FileDialog {
		id: exportFolderSelect
		title: "Choose Export Path"
		folder: shortcuts.home
		selectFolder: !inFlatpak

		modality: Qt.ApplicationModal

		onAccepted: {
			exportFolderSelect.close()
			chosenFolder = inFlatpak ? dirFromFileUrl(fileUrl) : folder
			root.log("Selected Folder (" + chosenFolder + ")")
		}
	}



	function gpOnUp() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoUp()
		} else if (gpFocus == 2 && exportSelect.dropOn) {
			exportSelect.dropMenuGoUp()
		} else {
			gpFocus -= 1
			if (gpFocus < 0)
				gpFocus = 0
		}
	}

	function gpOnDown() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoDown()
		} else if (gpFocus == 2 && exportSelect.dropOn) {
			exportSelect.dropMenuGoDown()
		} else {
			gpFocus += 1
			if (gpFocus > 3)
				gpFocus = 3
		}
	}

	function gpOnRUp() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoUp()
		} else if (gpFocus == 2 && exportSelect.dropOn) {
			exportSelect.dropMenuGoUp()
		}
	}

	function gpOnRDown() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoDown()
		} else if (gpFocus == 2 && exportSelect.dropOn) {
			exportSelect.dropMenuGoDown()
		}
	}

	function gpOnA() {
		switch(gpFocus) {
			case 0:
				exportFolderSelect.open()
				break
			case 1:
				if (systemSelect.dropOn)
					systemSelect.simulateClick()
				else
					systemSelect.invokeDropMenu()
				break
			case 2:
				if (exportSelect.dropOn)
					exportSelect.simulateClick()
				else
					exportSelect.invokeDropMenu()
				break
			case 3:
				if (chosenFolder != "" && systemData.includes(chosenSystem) && exportData.includes(chosenExport)) {
					working = true;
					runtask(3, chosenFolder + ";;;" + chosenSystem + ";;;" + chosenExport);
				}
				break
		}
	}

	function gpOnB() {
		if (gpFocus == 1 && systemSelect.dropOn)
			systemSelect.hideDropMenu()
		else if (gpFocus == 2 && exportSelect.dropOn)
			exportSelect.hideDropMenu()
	}



	function resetValues() {
		chosenSystem = ""
		chosenExport = ""
	}

}
