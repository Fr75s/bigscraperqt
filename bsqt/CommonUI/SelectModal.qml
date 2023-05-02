import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
	id: modalRoot
	anchors.fill: parent

	color: "#66" + striphash(colors.shadow)

	property string title: ""
	property bool invoked: false

	property var itemmodel: []

	visible: false


	MouseArea {
		anchors.fill: parent
	}

	Rectangle {
		anchors.fill: parent
		anchors.margins: pageWidthOffset

		color: colors.window

		radius: 24

		Text {
			width: parent.width * 0.9
			height: parent.height * 0.95

			anchors.centerIn: parent
			text: title
			color: colors.text

			horizontalAlignment: Text.AlignHCenter
			verticalAlignment: Text.AlignTop

			textFormat: Text.RichText
			wrapMode: Text.WordWrap
			font.family: outfit.name
			font.pixelSize: 32
		}

		ListView {
			id: dropMenu

			property int dropBotMargin: 8

			width: parent.width * 0.8
			height: parent.height * 0.8

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: dropBotMargin

			focus: invoked
			snapMode: ListView.SnapToItem
			clip: true

			model: itemmodel

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
					close(modelData)
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
	}

	function invoke(data) {
		visible = true
		invoked = true
		itemmodel = data
	}

	function close(data) {
		invoked = false
		visible = false
		dataOperation(data)
	}



	function dropMenuGoUp() {
		dropMenu.currentIndex -= 1
		if (dropMenu.currentIndex < 0)
			dropMenu.currentIndex = itemmodel.length - 1
	}

	function dropMenuGoDown() {
		dropMenu.currentIndex += 1
		if (dropMenu.currentIndex > itemmodel.length - 1)
			dropMenu.currentIndex = 0
	}

	function simulateClick() {
		dropMenu.currentItem.sclick()
	}
}
