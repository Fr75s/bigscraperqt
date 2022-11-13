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

	property var mainProgFactor: 0.0
	property var gameProgFactor: 0.0
	property var secProgFactor: 0.0

	Image {
		id: loadSpinner
		width: parent.height * 0.25
		height: width

		anchors.verticalCenter: parent.verticalCenter
		anchors.right: parent.right
		anchors.rightMargin: (parent.width - sidebarWidth) * 0.5 - (width / 2)

		visible: false
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

	Rectangle {
		id: progMain
		width: parent.width * 0.5
		height: 16

		anchors.verticalCenter: parent.verticalCenter
		anchors.right: parent.right
		anchors.rightMargin: (parent.width - sidebarWidth) * 0.5 - (width / 2)

		visible: false
		color: colors.dark
		radius: height / 2

		Rectangle {
			id: progMainBar

			width: parent.width * mainProgFactor - (anchors.margins * 2)
			height: parent.height - 4

			anchors.verticalCenter: parent.verticalCenter
			anchors.left: parent.left
			anchors.leftMargin: 2

			color: colors.text
			radius: height / 2
		}
	}

	Text {
		id: progMainLabel
		width: progMain.width
		height: font.pixelSize

		anchors.horizontalCenter: progMain.horizontalCenter
		anchors.top: progMain.bottom
		anchors.topMargin: 8

		color: colors.text
		text: ""
		wrapMode: Text.WordWrap
		font.family: outfit.name
		font.pixelSize: 16
		font.weight: Font.Medium

		visible: progMain.visible

		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
	}

	Rectangle {
		id: progGame
		width: parent.width * 0.5
		height: 12

		anchors.top: workNotif.bottom
		anchors.topMargin: 24

		anchors.right: parent.right
		anchors.rightMargin: (parent.width - sidebarWidth) * 0.5 - (width / 2)

		visible: false
		color: colors.dark
		radius: height / 2

		Rectangle {
			id: progGameBar

			width: parent.width * gameProgFactor - (anchors.margins * 2)
			height: parent.height - 4

			anchors.verticalCenter: parent.verticalCenter
			anchors.left: parent.left
			anchors.leftMargin: 2

			color: colors.text
			radius: height / 2
		}
	}

	Rectangle {
		id: progSecGame
		width: parent.width * 0.5
		height: 12

		anchors.top: progGame.bottom
		anchors.topMargin: 12

		anchors.right: parent.right
		anchors.rightMargin: (parent.width - sidebarWidth) * 0.5 - (width / 2)

		visible: false
		color: colors.dark
		radius: height / 2

		Rectangle {
			id: progSecGameBar

			width: parent.width * secProgFactor - (anchors.margins * 2)
			height: parent.height - 4

			anchors.verticalCenter: parent.verticalCenter
			anchors.left: parent.left
			anchors.leftMargin: 2

			color: colors.text
			radius: height / 2
		}
	}

	Text {
		id: workNotif
		width: parent.width - sidebarWidth
		height: font.pixelSize

		anchors.right: parent.right
		anchors.top: parent.top
		anchors.topMargin: parent.height * 0.7

		color: colors.text
		text: workMsg
		wrapMode: Text.WordWrap
		font.family: outfit.name
		font.pixelSize: 36
		font.weight: Font.Medium

		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
	}

	Text {
		id: statsText
		width: parent.width * 0.5
		height: parent.height * 0.5

		anchors.right: parent.right
		anchors.top: parent.top
		anchors.margins: parent.height * 0.05

		color: colors.text
		text: statsMsg
		wrapMode: Text.WordWrap

		font.family: outfit.name
		font.pixelSize: 18
		font.weight: Font.Medium

		horizontalAlignment: Text.AlignRight
		verticalAlignment: Text.AlignTop
	}

	function updateProgress(res) {
		let action = res[0]

		switch(action) {
			case 0:
				if (res[1] == 0)
					progMain.visible = false
				else
					progMain.visible = true
				break
			case 1:
				if (res[1] == 0)
					progGame.visible = false
				else
					progGame.visible = true
				break
			case 2:
				mainProgFactor = ((res[1] * 1.0) / res[2])
				progMainLabel.text = "" + res[1] + " / " + res[2]
				break
			case 3:
				gameProgFactor = ((res[1] * 1.0) / res[2])
				break
			case 4:
				if (res[1] == 0)
					progSecGame.visible = false
				else
					progSecGame.visible = true
				break
			case 5:
				secProgFactor = ((res[1] * 1.0) / res[2])
				break
		}
	}
}
