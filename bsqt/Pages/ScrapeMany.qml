import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
//import QtQuick.Dialogs
import QtQuick.Dialogs 1.3

import "../CommonUI"

Item {
	id: scrapeMany
	anchors.fill: parent

	property var chosenFolder: ""
	property var chosenSystem: ""

	property int gpFocus: -1

	PageTitle {
		id: scrapeManyTitle
		text: "Scrape A Folder"
	}

	ButtonLabelRow {
		id: gameFolderSelect
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: scrapeManyTitle.bottom
		anchors.topMargin: 24

		focused: gpFocus == 0

		label: "Select Game Folder"
		btnIcon: (chosenFolder == "") ? "folder-symbolic" : ""
		btnLabel: folderPath(chosenFolder)

		function pushAction() {
			scrapeManyFolderSelect.open()
		}
	}

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
	}

	BsqtButton {
		id: beginOneStep

		anchors.bottom: parent.bottom
		anchors.bottomMargin: 48

		focus: gpFocus == 2

		anchors.left: parent.left
		anchors.leftMargin: sidebarWidth + pageWidthOffset / 2

		width: pageWidth * 0.25
		height: 72

		label: "Begin"
		btnhighlight: true

		onClicked: {
			if (chosenFolder != "" && chosenSystem != "") {
				working = true;
				runtask(2, chosenFolder + ";;;" + chosenSystem);
			}
		}
	}


	/*
	FolderDialog {
		id: scrapeManyFolderSelect
		title: "Choose Game Folder"
		currentFolder: homeFolder

		modality: Qt.ApplicationModal

		acceptLabel: "Select"

		onAccepted: {
			chosenFolder = selectedFolder
			console.log("[UI]: Selected Folder (" + chosenFolder + ")")
		}
	}
	*/

	/* NOTE:
	 * When building this app as a flatpak, a strange bug occurs when selecting a folder. [folder]
	 * itself always updates itself to the home folder when opening the 1st time, then to whatever
	 * directory you are running the flatpak from upon choosing the 2nd time. No clue why this
	 * happens, but I force the user to choose any file in the desired folder instead. Yes, this
	 * means that in the flatpak build, you can't pick an empty folder without putting something
	 * in there, sorry. (it took way too long for me to even figure out how to build this app as
	 * a flatpak; it's a miracle it even happened, this is the least I can do.)
	 *
	 */

	FileDialog {
		id: scrapeManyFolderSelect
		title: "Choose Game Folder"
		folder: shortcuts.home
		selectFolder: !inFlatpak

		modality: Qt.ApplicationModal

		onAccepted: {
			scrapeManyFolderSelect.close()
			chosenFolder = inFlatpak ? dirFromFileUrl(fileUrl) : folder
			root.log("Selected Folder (" + chosenFolder + ")")
		}
	}



	function gpOnUp() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoUp()
		} else {
			gpFocus -= 1
			if (gpFocus < 0)
				gpFocus = 0
		}
	}

	function gpOnDown() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoDown()
		} else {
			gpFocus += 1
			if (gpFocus > 2)
				gpFocus = 2
		}
	}

	function gpOnRUp() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoUp()
		}
	}

	function gpOnRDown() {
		if (gpFocus == 1 && systemSelect.dropOn) {
			systemSelect.dropMenuGoDown()
		}
	}

	function gpOnA() {
		switch(gpFocus) {
			case 0:
				scrapeManyFolderSelect.open()
				break
			case 1:
				if (systemSelect.dropOn)
					systemSelect.simulateClick()
				else
					systemSelect.invokeDropMenu()
				break
			case 2:
				if (chosenFolder != "" && chosenSystem != "") {
					working = true;
					runtask(2, chosenFile + ";;;" + chosenSystem);
				}
				break
		}
	}

	function gpOnB() {
		if (gpFocus == 1 && systemSelect.dropOn)
			systemSelect.hideDropMenu()
	}



	function resetValues() {
		chosenSystem = ""
	}

}
