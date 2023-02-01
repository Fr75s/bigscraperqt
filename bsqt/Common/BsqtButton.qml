import QtQuick 2.8
import QtQuick.Controls 2.15

Item {
	id: buttonRoot

	property bool active: true
	property bool outline: false

	Rectangle {
		id: buttonBack
		width: parent.width
		height: parent.height
		color: mouseHandler.containsMouse ? colors["button_highlight"] : colors["button"]

		radius: height / 4
		border.width: outline ? 2 : 0
		border.color: active ? colors["status_ready"] : colors["status_hold"]
	}

	FormText {
		anchors.centerIn: buttonBack
		font.pixelSize: 32

		text: "Begin Scraping"
		font.weight: Font.Medium
	}

	MouseArea {
		id: mouseHandler
		anchors.fill: parent
		hoverEnabled: true

		onClicked: action()
	}

	function action() { }
}
