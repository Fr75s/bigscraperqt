import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

import "../CommonUI"

Item {
	id: options
	anchors.fill: parent

	property int gpFocus: 0

	Text {
		id: versionInfoLabel

		width: parent.width
		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: parent.top
		anchors.topMargin: 16 + toolbarHeight

		text: appInfo[0] + " v" + appInfo[1]

		horizontalAlignment: Text.AlignRight
		verticalAlignment: Text.AlignTop

		color: colors.text
		font.family: outfit.name
		font.pixelSize: 16
		font.weight: Font.Medium
	}

	PageTitle {
		id: optionsTitle
		text: "Options"
	}

	PageSubtitle {
		id: subtitleScrapeOpts
		text: "Scraping Options"

		anchors.top: optionsTitle.bottom
		anchors.topMargin: 18
	}

	ButtonLabelRow {
		id: sOption1
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: subtitleScrapeOpts.bottom
		anchors.topMargin: 24

		focused: gpFocus == 0

		label: "Video Downloads"
		btnIcon: "checkbox"
		btnCheckable: true
		btnChecked: defopts[0]

		function pushAction() {
			root.togopt("video")
		}
	}

	Image {
		id: sOption2Info
		width: height
		height: 48

		anchors.top: sOption1.bottom
		anchors.topMargin: 24
		anchors.left: parent.left
		anchors.leftMargin: pageWidthOffset / 2

		source: "../res/info.png"
		mipmap: true

		MouseArea {
			anchors.fill: parent
			onClicked: sOption2Modal.invoke()
		}
	}

	ButtonLabelRow {
		id: sOption2
		width: pageWidth - sOption2Info.width - 16
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: sOption1.bottom
		anchors.topMargin: 24

		label: "Remove 5 Minute Limit"
		btnIcon: "checkbox"
		btnEnable: sOption1.isCheck

		focused: gpFocus == 1

		btnCheckable: true
		btnChecked: defopts[1]

		function pushAction() {
			root.togopt("videoOverLimit")
		}
	}

	/*
	PageSubtitle {
		id: subtitleInterOpts
		text: "Interface Options"

		anchors.top: sOption2.bottom
		anchors.topMargin: 36
	}

	ButtonLabelRow {
		id: iOption1
		width: pageWidth
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: subtitleInterOpts.bottom
		anchors.topMargin: 24

		label: "Transparent Navigation Bar"
		btnIcon: "checkbox"
		btnCheckable: true
		btnChecked: defopts[3]

		function pushAction() {
			root.togopt("glassyTitle")
			blurTitlebar = !blurTitlebar
		}
	}
	*/



	InfoModal {
		id: sOption2Modal
		infoIcon: InfoModal.InfoIcon.Warning
		information: "If you turn off this option, there is a high chance that you may download a video that's hours long. Many games that have videos on Launchbox have videos of longplays and the like; even common games may have videos up to 7 hours long. It is best to turn off this option, but if your network can handle it and you have the patience, it is here for you to turn off.<br><br>Note that if you turn on this option, be aware that bigscraper-qt doesn't track video download progress in the GUI. You will need to open it from the terminal to see yt-dlp's output."
	}



	function gpOnUp() {
		gpFocus -= 1
		if (gpFocus < 0)
			gpFocus = 0
	}

	function gpOnDown() {
		gpFocus += 1
		if (gpFocus > 2)
			gpFocus = 2
	}

	function gpOnA() {
		switch(gpFocus) {
			case 0:
				sOption1.btnChecked = !sOption1.btnChecked
				root.togopt("video")
				break
			case 1:
				sOption2.btnChecked = !sOption2.btnChecked
				root.togopt("videoOverLimit")
				break
		}
	}


}

