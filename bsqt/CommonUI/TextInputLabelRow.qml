import QtQuick 2.8
import QtQuick.Controls 2.15

Item {
	id: txtLblRow

	property string label: ""
	property string defaultIn: ""
	property bool enableInput: true

	property bool focused: false
	property bool passinput: false

	property var maxWidth: 600
	property var spacing: 32

	Text {
		id: txtLblRowLabel

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

	Rectangle {
		id: txtLblRowBG

		anchors.top: parent.top
		anchors.right: parent.right

		width: (txtLblRowLabel.contentWidth + maxWidth + spacing > parent.width) ? (parent.width - txtLblRowLabel.contentWidth - spacing) : maxWidth
		height: parent.height

		color: colors.mid
		radius: height / 4

		TextInput {
			id: txtLblRowInput

			width: parent.width * 0.9
			height: parent.height
			anchors.horizontalCenter: parent.horizontalCenter

			focus: txtLblRow.focused
			color: colors.text
			text: defaultIn

			font.family: outfit.name
			font.pixelSize: height * 0.65
			verticalAlignment: Text.AlignVCenter

			echoMode: passinput ? TextInput.PasswordEchoOnEdit : TextInput.Normal

			onEditingFinished: {
				enterAction(txtLblRowInput.text)
			}
		}
	}
}
