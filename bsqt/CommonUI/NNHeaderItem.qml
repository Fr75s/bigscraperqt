import QtQuick 2.8
import QtQuick.Controls 2.15
import QtLocation 5.6

Rectangle {

	property var ico: ""
	property string label: ""

	color: "transparent"

	property bool press: push.containsPress
	property bool hover: push.containsMouse

	border.width: 2
	border.color: hover ? colors.highlight : "transparent"
	radius: 2

	Text {
		id: headerText
		visible: label != ""

		anchors.centerIn: parent

		text: label
		color: colors.text

		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
	}

	MouseArea {
		id: push
		anchors.fill: parent
		propagateComposedEvents: true
		hoverEnabled: true

		onPressed: pushAction()
	}
}
