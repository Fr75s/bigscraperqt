import QtQuick 2.8
import QtQuick.Controls 2.15

Item {
	property var btnIcon: ""
	property string btnLabel: ""
	property string label: ""
	property var dropDownModel: []

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

		ico: btnIcon
		label: btnLabel

		onClicked: dropMenu.visible = !dropMenu.visible
	}

	ListView {
		id: dropMenu

		property int dropTopMargin: 12
		property int dropBotMargin: 64

		width: btnLblRowButton.width
		height: (root.height * 0.5) - btnLblRowButton.height - dropTopMargin - dropBotMargin

		anchors.top: btnLblRowButton.bottom
		anchors.topMargin: dropTopMargin
		anchors.right: btnLblRowButton.right

		focus: parent.visible
		visible: false
		snapMode: ListView.SnapToItem
		clip: true

		model: dropDownModel

		delegate: Item {
			width: ListView.view.width
			height: 50

			BsqtButton {
				width: parent.width * 0.8
				height: parent.height * 0.8

				anchors.left: parent.left
				anchors.verticalCenter: parent.verticalCenter
				anchors.leftMargin: parent.height * 0.1

				fontSize: height / 2
				label: modelData

				onClicked: {
					pushAction(modelData)
					dropMenu.visible = false
				}
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
