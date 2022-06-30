import QtQuick 2.8
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Button {
	id: bsqtbutton

	signal clicked()

	property string label: ""
	property var ico: ""
	property var fontSize: height / 4
	property bool btnhighlight: false
	property bool btnEnabled: true

	enabled: btnEnabled

	property bool press: homeButtonAction.containsPress || check
	property bool hover: homeButtonAction.containsMouse
	property bool check: false

	down: press
	flat: !nativeStyle

	icon.name: ico
	icon.height: height / 2
	icon.width: height / 2
	icon.color: colors.text

	Rectangle {
		id: bsqtButtonBG
		anchors.fill: parent

		visible: !nativeStyle
		color: press ? colors.highlight : (btnEnabled ? colors.button : colors.shadow)
		radius: 2

		border.width: 2
		border.color: hover ? (colors.highlight) : (btnhighlight ? colors.dark : (check ? colors.highlight : (btnEnabled ? colors.button : colors.shadow)))

		Behavior on border.color {
			ColorAnimation {
				duration: 100
			}
		}
		Behavior on color {
			ColorAnimation {
				duration: 50
			}
		}
	}


	Text {
		anchors.fill: parent
		font.pixelSize: fontSize
		font.family: outfit.name

		text: label
		color: (press || check) ? colors.highlightedText : colors.buttonText
		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
	}

	MouseArea {
		id: homeButtonAction
		enabled: btnEnabled
		anchors.fill: parent
		propagateComposedEvents: true
		hoverEnabled: true

		onPressed: parent.clicked()
	}
}
