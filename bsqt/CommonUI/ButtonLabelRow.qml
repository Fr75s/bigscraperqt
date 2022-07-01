import QtQuick 2.8
import QtQuick.Controls 2.15

Item {
	property var btnIcon: ""
	property string btnLabel: ""
	property string label: ""

	property bool btnEnable: true
	property bool btnCheckable: false
	property bool btnChecked: false
	property bool isCheck: btnLblRowButton.check

	property bool focused: false

	property var maxBtnWidth: 600
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

		width: (btnLblRowLabel.contentWidth + maxBtnWidth + btnSpacing > parent.width) ? (parent.width - btnLblRowLabel.contentWidth - btnSpacing) : maxBtnWidth
		height: parent.height

		focus: parent.focused

		check: btnChecked
		btnEnabled: btnEnable

		ico: btnIcon
		label: btnLabel

		onClicked: {
			pushAction()
			if (btnCheckable)
				check = !check
		}
	}
}
