import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

import "../Common"

Item {
	id: home
	anchors.fill: parent

	FormText {
		width: contentWidth
		font.pixelSize: 64

		y: 65
		anchors.horizontalCenter: parent.horizontalCenter

		text: "bigscraper<b>qt</b>"
	}

	BsqtButton {
		width: parent.width * 0.625
		height: 60

		active: false
		outline: true

		anchors.horizontalCenter: parent.horizontalCenter
		anchors.bottom: parent.bottom
		anchors.bottomMargin: 30

		function action() {
			console.log("Begin Task")
		}
	}
}
