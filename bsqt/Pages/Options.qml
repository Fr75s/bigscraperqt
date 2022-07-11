import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

import "../CommonUI"

Item {
	id: options
	anchors.fill: parent

	property int gpFocus: -1

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

	Connections {
		target: root

		function onInitOptions() {
			[
				{
					id: "subScraping",
					type: "label",
					title: "Scraping Options"
				},

				{
					id: "optVideo",
					type: "setting",
					title: "Video Downloads",
					setting: "video",
					initial: defopts[0],

					info: ""
				},
				{
					id: "optVideoLimit",
					type: "setting",
					title: "Remove Video Length Limit",
					setting: "videoOverLimit",
					initial: defopts[1],

					info: "This option toggles whether bigscraper-qt downloads videos over 5 minutes. Note that if turned off, you may see yourself downloading an hours long video - in this case, bigscraper-qt may appear frozen. It is best to keep this option off, unless your bandwidth can handle the extremely long videos.",
					infoType: InfoModal.InfoIcon.Warning
				},
				{
					id: "optVideoLimit",
					type: "setting",
					title: "Recache Mode",
					setting: "recache",
					initial: defopts[4],

					info: "Recache mode allows you to redownload previously scraped data, useful if a new feature is implemented that adds to scraped data.<br>It is recommended to turn this off as this uses more bandwidth than necessary, as with recache mode, you always redownload everything.",
					infoType: InfoModal.InfoIcon.Info
				}

			].forEach(function(e) { optionEntries.append(e); });
		}
	}

	ListModel {
		id: optionEntries
	}



	ListView {
		id: optsView

		anchors.top: optionsTitle.bottom
		anchors.topMargin: 24

		anchors.bottom: parent.bottom
		anchors.bottomMargin: 24

		width: pageWidth

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2

		model: optionEntries
		clip: true
		focus: (currentPage == 4)

		keyNavigationWraps: true
		highlightFollowsCurrentItem: true
		highlightMoveDuration: 75

		delegate: Item {
			width: ListView.view.width
			height: 60

			property bool skip: (type == "label")

			PageSubtitle {
				visible: (type == "label")

				id: optSubtitle
				text: title

				width: parent.width
				height: parent.height * 0.8

				anchors.top: parent.top
				anchors.horizontalCenter: parent.horizontalCenter
			}

			Image {
				visible: (type == "setting" && info != "")

				id: infoIndicator
				width: height
				height: parent.height * 0.4

				anchors.verticalCenter: parent.verticalCenter
				anchors.left: parent.left
				anchors.leftMargin: pageWidthOffset / 2

				source: "../res/info.png"
				mipmap: true

				MouseArea {
					anchors.fill: parent
					onClicked: {
						generalInfoModal.infoIcon = infoType
						generalInfoModal.information = info

						generalInfoModal.invoke()
					}
				}
			}

			ButtonLabelRow {
				visible: (type == "setting")

				id: optionButton
				width: infoIndicator.visible ? parent.width - infoIndicator.width - 16 - (anchors.rightMargin * 2) : parent.width - (anchors.rightMargin * 2)
				height: parent.height * 0.8

				focused: (index == optsView.currentIndex)

				anchors.right: parent.right
				anchors.rightMargin: pageWidthOffset / 2

				anchors.top: parent.top
				anchors.topMargin: parent.height * 0.1

				label: title
				btnIcon: "checkbox"
				btnCheckable: true
				btnChecked: initial

				function pushAction() {
					root.togopt(setting)
				}
			}

			function gpOnA() {
				optionButton.btnChecked = !optionButton.btnChecked
				optionButton.pushAction()
			}

			function gpOnB() {
				if (infoIndicator.visible) {
					generalInfoModal.infoIcon = infoType
					generalInfoModal.information = info

					generalInfoModal.invoke()
				}
			}
		}

		ScrollBar.vertical: ScrollBar {
			visible: optsView.visible

			parent: optsView.parent
			anchors.top: optsView.top
			anchors.right: optsView.right
			anchors.bottom: optsView.bottom

			minimumSize: 1 / 8
		}
	}

	InfoModal {
		id: generalInfoModal
	}



	/*
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

	Image {
		id: sOption3Info
		width: height
		height: 48

		anchors.top: sOption2.bottom
		anchors.topMargin: 24
		anchors.left: parent.left
		anchors.leftMargin: pageWidthOffset / 2

		source: "../res/info.png"
		mipmap: true

		MouseArea {
			anchors.fill: parent
			onClicked: sOption3Modal.invoke()
		}
	}

	ButtonLabelRow {
		id: sOption3
		width: pageWidth - sOption2Info.width - 16
		height: 48

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: sOption2.bottom
		anchors.topMargin: 24

		label: "Recache Mode"
		btnIcon: "checkbox"

		focused: gpFocus == 2

		btnCheckable: true
		btnChecked: defopts[4]

		function pushAction() {
			root.togopt("recache")
		}
	}

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



	InfoModal {
		id: sOption2Modal
		infoIcon: InfoModal.InfoIcon.Warning
		information: "If you turn off this option, there is a high chance that you may download a video that's hours long. Many games that have videos on Launchbox have videos of longplays and the like; even common games may have videos up to 7 hours long. It is best to turn off this option, but if your network can handle it and you have the patience, it is here for you to turn off.<br><br>Note that if you turn on this option, be aware that bigscraper-qt doesn't track video download progress in the GUI. You will need to open it from the terminal to see yt-dlp's output."
	}

	InfoModal {
		id: sOption3Modal
		infoIcon: InfoModal.InfoIcon.Info
		information: "Recache mode allows you to redownload previously scraped data, useful if a new feature is implemented that adds to scraped data.<br>It is recommended to turn this off as this uses more bandwidth than necessary, as with recache mode, you always redownload everything."
	}
	*/



	function gpOnUp() {
		optsView.decrementCurrentIndex()
		while (optsView.currentItem.skip == true) {
			optsView.decrementCurrentIndex()
		}
	}

	function gpOnDown() {
		optsView.incrementCurrentIndex()
		while (optsView.currentItem.skip == true) {
			optsView.incrementCurrentIndex()
		}
	}

	function gpOnA() {
		optsView.currentItem.gpOnA()
	}

	function gpOnB() {
		optsView.currentItem.gpOnB()
	}


}

