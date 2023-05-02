import QtQuick 2.8
import QtQuick.Controls 2.15

Item {
	id: dropRoot
	property var attachedTo
	property string ddid: ""
	property var dropDownModel: []

	property bool focused: false
	property bool above: false

	property int maxWidth: 600
	property var maxDDHeight: 600

	ListView {
		id: dropMenu

		property int dropTopMargin: 12
		property int dropBotMargin: 64

		width: parent.width
		height: (dropDownModel.length * 50 > root.height * root.height * 0.0004) ? root.height * root.height * 0.0004 : dropDownModel.length * 50

		anchors.right: parent.right

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
			visible: dropMenu.visible

			parent: dropMenu.parent
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
		refreshAnchors()
	}

	function refreshAnchors() {
		let dropTopMargin = 12
		if (above) {
			dropRoot.anchors.bottom = attachedTo.top
			dropRoot.anchors.bottomMargin = dropTopMargin
		} else {
			dropRoot.anchors.top = attachedTo.bottom
			dropRoot.anchors.topMargin = dropTopMargin
		}
	}





	function invoke() {
		dropRoot.visible = true
		refreshAnchors()
		console.log(attachedTo)
		root.hideOtherDDLR(ddid)
	}

	function hide() {
		dropRoot.visible = false
	}

	function simulateClick() {
		dropMenu.currentItem.sclick()
	}

	function navUp() {
		dropMenu.currentIndex -= 1
		if (dropMenu.currentIndex < 0)
			dropMenu.currentIndex = dropDownModel.length - 1
	}

	function navDown() {
		dropMenu.currentIndex += 1
		if (dropMenu.currentIndex > dropDownModel.length - 1)
			dropMenu.currentIndex = 0
	}



	Connections {
		target: root

		function onHideOtherDDLR(exclude) {
			if (ddid != exclude) {
				hide()
			}
		}
	}
}
