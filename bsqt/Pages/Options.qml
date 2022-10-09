import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

import "../CommonUI"

Item {
	id: options
	anchors.fill: parent

	property int gpFocus: -1
	property bool viewCredits: false

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

		MouseArea {
			anchors.fill: parent
			hoverEnabled: true

			cursorShape: Qt.PointingHandCursor

			onClicked: viewCredits = !viewCredits
		}
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
					id: "optModule",
					type: "multiSetting",
					title: "Scraping Service",
					setting: "module",
					initialChoice: optionValuesInit["module"],

					info: "Select from one of several scraping services available for you to use. Using multiple services is ideal for getting all metadata for your games, as each provides its own set of metadata.",
					infoType: InfoModal.InfoIcon.Info
				},

				{
					id: "optRegion",
					type: "multiSetting",
					title: "Region",
					setting: "region",
					initialChoice: optionValuesInit["region"],

					info: "Selecting a region decides what type of metadata is prioritized when scraped. Choosing a region allows exported metadata to match your region of choice as well.",
					infoType: InfoModal.InfoIcon.Info
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
					id: "optLocalPaths",
					type: "setting",
					title: "Use Local Paths",
					setting: "localPaths",
					initial: defopts[4],

					info: "This option toggles whether exported files use local paths or full paths for games, e.g. <tt>[Game.rom]</tt> vs <tt>[/path/to/Game.rom]</tt>.<br><br>This is recommended for console ROMs as it allows you to easily transfer metadata along with your games to other devices.<br>This is not recommended for PC Games, as their executables are likely installed in different directories from eachother.",
					infoType: InfoModal.InfoIcon.Info
				},
				{
					id: "optRecache",
					type: "setting",
					title: "Recache Mode",
					setting: "recache",
					initial: defopts[3],

					info: "Recache mode allows you to redownload previously scraped data, useful if a new feature is implemented that adds to scraped data.<br>It is recommended to turn this off as this uses more bandwidth than necessary, as with recache mode, you always redownload everything.",
					infoType: InfoModal.InfoIcon.Info
				},


				{
					id: "subScreenScraper",
					type: "label",
					title: "ScreenScraper"
				},

				{
					id: "module",
					type: "inputSetting",
					title: "Username",
					setting: "screenScraperUser",
					initialChoice: optionValuesInit["screenScraperUser"],
					info: ""
				},
				{
					id: "module",
					type: "inputSetting",
					title: "Password",
					setting: "screenScraperPass",
					initialChoice: optionValuesInit["screenScraperPass"],
					pass: true,
					info: ""
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
		visible: !viewCredits

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2

		model: optionEntries
		clip: true
		focus: (currentPage == 4)

		boundsBehavior: Flickable.StopAtBounds
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
				height: parent.height

				anchors.top: parent.top
				anchors.horizontalCenter: parent.horizontalCenter
			}

			Image {
				visible: (type != "label" && info != "")

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
					hoverEnabled: true
					cursorShape: Qt.PointingHandCursor
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

				focused: (index == optsView.currentIndex && type == "setting")

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

			TextInputLabelRow {
				visible: (type == "inputSetting")

				id: optionTextInput
				width: infoIndicator.visible ? parent.width - infoIndicator.width - 16 - (anchors.rightMargin * 2) : parent.width - (anchors.rightMargin * 2)
				height: parent.height * 0.8

				focused: false
				passinput: type == "inputSetting" ? pass : false
				defaultIn: type == "inputSetting" ? initialChoice : ""

				anchors.right: parent.right
				anchors.rightMargin: pageWidthOffset / 2

				anchors.top: parent.top
				anchors.topMargin: parent.height * 0.1

				label: title

				function enterAction(text) {
					root.setopt(setting, text)
				}
			}

			ButtonLabelRow {
				visible: (type == "multiSetting")

				id: optionModalInvoker
				width: infoIndicator.visible ? parent.width - infoIndicator.width - 16 - (anchors.rightMargin * 2) : parent.width - (anchors.rightMargin * 2)
				height: parent.height * 0.8

				focused: (index == optsView.currentIndex && type == "multiSetting")

				anchors.right: parent.right
				anchors.rightMargin: pageWidthOffset / 2

				anchors.top: parent.top
				anchors.topMargin: parent.height * 0.1

				label: title
				btnLabel: (initialChoice ? initialChoice : "")

				function pushAction() {
					optsView.currentIndex = index
					//console.log(optionValuesInit[setting])
					generalSelectModal.title = "Select Scraping Module"
					generalSelectModal.invoke(optionValues[setting])
				}
			}

			function selectAction(set, data) {
				optionModalInvoker.btnLabel = data
				root.setopt(set, data)
			}



			function gpOnA() {
				if (type == "setting") {
					optionButton.btnChecked = !optionButton.btnChecked
					optionButton.pushAction()
				} else if (type == "multiSetting") {
					optionModalInvoker.pushAction()
				} else if (type == "inputSetting") {
					optionTextInput.focused = true
				}
			}

			function gpOnB() {
				if (infoIndicator.visible) {
					generalInfoModal.infoIcon = infoType
					generalInfoModal.information = info

					generalInfoModal.invoke()
				}
				if (optionTextInput.focused) {
					optionTextInput.focused = false
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

	SelectModal {
		id: generalSelectModal

		function dataOperation(data) {
			optsView.currentItem.selectAction(optionEntries.get(optsView.currentIndex).setting, data)
		}
	}



	Flickable {
		id: credits
		anchors.top: optionsTitle.bottom
		anchors.topMargin: 24

		anchors.bottom: parent.bottom
		anchors.bottomMargin: 24

		anchors.horizontalCenter: parent.horizontalCenter

		width: pageWidth * 0.8
		visible: viewCredits



		clip: true

		contentWidth: width
		contentHeight: creditsContainer.height
		boundsBehavior: Flickable.StopAtBounds

		ScrollBar.vertical: ScrollBar { id: creditsScroll }

		Column {
			id: creditsContainer
			width: parent.width - (creditsScroll.visible ? creditsScroll.width : 0)
			anchors.left: parent.left
			anchors.top: parent.top

			spacing: 8

			Text {
				width: parent.width
				height: contentHeight

				anchors.left: parent.left

				color: colors.text
				text: "bigscraper<b>qt</b>"

				textFormat: Text.RichText
				font.family: outfit.name
				font.pixelSize: 36

			}

			Text {
				width: parent.width
				height: contentHeight

				anchors.left: parent.left

				color: colors.text
				text: `Made By <a href="https://github.com/Fr75s">Fr75s</a>. Licensed Under the <a href="https://github.com/Fr75s/bigscraperqt/blob/main/LICENSE">GNU GPL-3.0 License</a>.

				<br><br><br>
				Scraping Services Used:

				<br><br>
				<b>LaunchBox</b><br>
				Copyright © <a href="https://www.unbrokensoftware.com/">Unbroken Software, LLC</a>.<br>
				<a href="https://www.launchbox-app.com/">Website</a>

				<br><br>
				<b>Arcade Database</b><br>
				Made By motoschifo.<br>
				<a href="http://adb.arcadeitalia.net/">Website</a>

				<br><br>
				<b>ScreenScraper</b><br>
				Made By the ScreenScraper Community.<br>
				<a href="https://www.screenscraper.fr/">Website</a>

				`
				/*, /*<a href="https://gamesdb.launchbox-app.com/">Database</a>*/

				textFormat: Text.RichText
				wrapMode: Text.WordWrap
				font.family: outfit.name
				font.pixelSize: 18
				font.weight: Font.Medium

				onLinkActivated: Qt.openUrlExternally(link)
			}
		}
	}





	function gpOnUp() {
		if (generalSelectModal.invoked) {
			generalSelectModal.dropMenuGoUp()
		} else {
			optsView.decrementCurrentIndex()
			while (optsView.currentItem.skip == true) {
				optsView.decrementCurrentIndex()
			}
		}
	}

	function gpOnDown() {
		if (generalSelectModal.invoked) {
			generalSelectModal.dropMenuGoDown()
		} else {
			optsView.incrementCurrentIndex()
			while (optsView.currentItem.skip == true) {
				optsView.incrementCurrentIndex()
			}
		}
	}

	function gpOnRUp() {
		if (generalSelectModal.invoked)
			generalSelectModal.dropMenuGoUp()
	}

	function gpOnRDown() {
		if (generalSelectModal.invoked)
			generalSelectModal.dropMenuGoDown()
	}

	function gpOnA() {
		if (generalSelectModal.invoked)
			generalSelectModal.simulateClick()
		else if (generalInfoModal.invoked)
			generalInfoModal.close()
		else
			optsView.currentItem.gpOnA()
	}

	function gpOnB() {
		if (generalInfoModal.invoked)
			generalInfoModal.close()
		else
			optsView.currentItem.gpOnB()
	}
}

