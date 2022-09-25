import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
	property var btnIcon: ""
	property string btnLabel: ""
	property string label: ""
	property var dropDownModel: []

	property bool focused: false
	property bool above: false
	property bool dropOn: dropMenu.visible

	property var maxBtnWidth: 600
	property var maxDDHeight: 600
	property var btnSpacing: 32

	Text {
		id: btnLblRowLabel

		anchors.top: parent.top

		width: pageWidth
		height: parent.height

		color: colors.text
		text: label
		wrapMode: Text.WordWrap

		font.family: outfit.name
		font.pixelSize: parent.height * 0.65
		font.weight: Font.Light
		verticalAlignment: Text.AlignVCenter
	}

	BsqtButton {
		id: btnLblRowButton

		anchors.right: parent.right
		anchors.top: parent.top

		width: (btnLblRowLabel.contentWidth + maxBtnWidth > parent.width) ? (parent.width - btnLblRowLabel.contentWidth - btnSpacing) : maxBtnWidth
		height: parent.height

		focus: parent.focused && !dropMenu.visible

		ico: btnIcon
		label: btnLabel

		onClicked: {
			if (!dropMenu.visible) {
				invokeDropMenu()
			} else {
				hideDropMenu()
			}

		}
	}

	ListView {
		id: dropMenu

		property int dropTopMargin: 12
		property int dropBotMargin: 64

		width: btnLblRowButton.width
		height: (dropDownModel.length * 50 > root.height * root.height * 0.0004) ? root.height * root.height * 0.0004 : dropDownModel.length * 50

		anchors.right: btnLblRowButton.right

		focus: parent.focused && dropMenu.visible
		visible: false
		snapMode: ListView.SnapToItem
		clip: true

		model: dropDownModel

		highlightFollowsCurrentItem: true
		highlightMoveDuration: 75

		delegate: Item {
			width: ListView.view.width
			height: 50

			BsqtButton {
				width: parent.width * 0.8
				height: parent.height * 0.8

				anchors.left: parent.left
				anchors.verticalCenter: parent.verticalCenter
				anchors.leftMargin: parent.height * 0.1

				focus: dropMenu.focus && dropMenu.currentIndex == index

				fontSize: height / 2
				label: modelData

				onClicked: {
					sclick()
				}
			}

			function sclick() {
				pushAction(modelData)
				dropMenu.visible = false
			}
		}

		ScrollBar.vertical: ScrollBar {
			parent: dropMenu.parent
			opacity: dropMenu.visible ? 1 : 0
			interactive: dropMenu.visible
			anchors.top: dropMenu.top
			anchors.right: dropMenu.right
			anchors.bottom: dropMenu.bottom

			minimumSize: 1 / 8
		}

		Rectangle {
			anchors.fill: parent
			color: colors.mid
			radius: 48 * 0.8 * 0.25
			z: parent.z - 1
		}
	}

	Component.onCompleted: {
		//dropTopMargin = 12
		if (above) {
			dropMenu.anchors.bottom = btnLblRowButton.top
			//dropMenu.anchors.bottomMargin = dropTopMargin
		} else {
			dropMenu.anchors.top = btnLblRowButton.bottom
			//dropMenu.anchors.topMargin = dropTopMargin
		}
	}





	function invokeDropMenu() {
		dropMenu.visible = true
		root.hideOtherDDLR(label)
	}

	function hideDropMenu() {
		dropMenu.visible = false
	}

	function simulateClick() {
		dropMenu.currentItem.sclick()
	}

	function dropMenuGoUp() {
		dropMenu.currentIndex -= 1
		if (dropMenu.currentIndex < 0)
			dropMenu.currentIndex = dropDownModel.length - 1
	}

	function dropMenuGoDown() {
		dropMenu.currentIndex += 1
		if (dropMenu.currentIndex > dropDownModel.length - 1)
			dropMenu.currentIndex = 0
	}



	Connections {
		target: root

		function onHideOtherDDLR(exclude) {
			if (label != exclude) {
				hideDropMenu()
			}
		}
	}



	/* Typing Search functionality
	 * Lets you type the name of the system when focused
	 */

	Timer {
		id: typeSearchClearTimer
		interval: 3000

		running: false
		repeat: false

		onTriggered: {
			typeSearchInput.clear()
		}
	}

	TextInput {
		id: typeSearchInput
		opacity: 0
		enabled: dropMenu.visible
		focus: dropMenu.visible && !(dropMenu.focus)

		onTextEdited: {
			typeSearchClearTimer.restart();
			for (let i = 0; i < dropDownModel.length; i++) {
				if (dropDownModel[i].toLowerCase().indexOf(typeSearchInput.text.toLowerCase()) === 0) {
					dropMenu.positionViewAtIndex(i, ListView.Beginning);
					break;
				}
			}
		}
	}
}
