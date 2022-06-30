import QtQuick 2.8
import QtQuick.Controls 2.15

Item {
	property string label: ""
	property string choiceA: ""
	property string choiceB: ""

	property var maxBtnWidth: 300
	property var btnSpacing: 32
	property var btnBetween: 16

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
		id: btnLblRowButtonA

		anchors.right: btnLblRowButtonB.left
		anchors.rightMargin: btnBetween
		anchors.top: parent.top

		fontSize: height / 3
		label: choiceA

		width: (btnLblRowLabel.contentWidth + maxBtnWidth * 2 > parent.width) ? (parent.width - btnLblRowLabel.contentWidth - btnSpacing) / 2 : maxBtnWidth - btnBetween / 2
		height: parent.height

		onClicked: {
			pushActionA()
			check = true
			if (btnLblRowButtonB.check)
				btnLblRowButtonB.check = false
		}
	}

	BsqtButton {
		id: btnLblRowButtonB

		anchors.right: parent.right
		anchors.top: parent.top

		fontSize: height / 3
		label: choiceB

		width: (btnLblRowLabel.contentWidth + maxBtnWidth * 2 > parent.width) ? (parent.width - btnLblRowLabel.contentWidth - btnSpacing) / 2 - btnBetween : maxBtnWidth - btnBetween / 2
		height: parent.height

		onClicked: {
			pushActionB()
			check = true
			if (btnLblRowButtonA.check)
				btnLblRowButtonA.check = false
		}
	}
}
