import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
	id: modalRoot
	anchors.fill: parent
	color: "#66" + striphash(colors.shadow)

	enum InfoIcon {
		None,
		Info,
		Warning
	}

	property int infoIcon: InfoModal.InfoIcon.Info
	property string information: ""

	visible: false


	MouseArea {
		anchors.fill: parent
	}


	Rectangle {
		anchors.fill: parent
		anchors.margins: pageWidthOffset

		color: colors.window

		radius: 48

		Image {
			width: height
			height: parent.height * 0.15

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.top: parent.top
			anchors.topMargin: parent.height * 0.05

			mipmap: true
			source: {
				switch(infoIcon) {
					case InfoModal.InfoIcon.None:
						return ""
						break
					case InfoModal.InfoIcon.Info:
						return "../res/info.png"
						break
					case InfoModal.InfoIcon.Warning:
						return "../res/warning.png"
						break
					default:
						return ""
						break
				}
			}
		}

		Text {
			width: parent.width * 0.9
			height: parent.height * 0.5

			anchors.centerIn: parent
			text: information
			color: "white"

			textFormat: Text.RichText
			wrapMode: Text.WordWrap
			font.family: outfit.name
			font.pixelSize: parent.height * 0.048

			lineHeight: parent.height * 0.052
			lineHeightMode: Text.FixedHeight
			font.weight: Font.Medium
		}

		BsqtButton {
			width: parent.width * 0.65
			height: parent.height * 0.15

			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			anchors.bottomMargin: parent.height * 0.05

			label: "OK"
			onClicked: {
				close()
			}
		}
	}

	function invoke() {
		visible = true
	}

	function close() {
		visible = false
	}
}
