import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

import "../CommonUI"

Item {
	id: work
	anchors.fill: parent

	PageTitle {
		id: workTitle
		text: "Working..."
	}

	Image {
		id: loadSpinner
		width: parent.height * 0.25
		height: width

		anchors.verticalCenter: parent.verticalCenter
		anchors.right: parent.right
		anchors.rightMargin: (parent.width - sidebarWidth) * 0.5 - (width / 2)

		mipmap: true
		source: "../res/spinner.png"

		NumberAnimation on rotation {
			from: 0
			to: 360

			running: visible
			loops: Animation.Infinite
			duration: 1500
		}
	}

	Text {
		id: workNotif
		width: parent.width - sidebarWidth
		height: parent.height

		anchors.right: parent.right
		anchors.top: parent.top
		anchors.topMargin: loadSpinner.height

		color: colors.text
		text: workMsg
		wrapMode: Text.WordWrap
		font.family: outfit.name
		font.pixelSize: 36
		font.weight: Font.Medium

		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
	}
}
