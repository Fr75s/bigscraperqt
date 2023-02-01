import QtQuick 2.8
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15

import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

Rectangle {

	id: headerRoot

	/* HeaderBar
	 *   Defines the header for the application
	 */

	property int tabWidth: 180
	property int tabGutter: 15

	color: colors["back_2"]

	ListView {
		id: taskTabs

		x: tabGutter
		y: tabGutter

		width: parent.width - tabGutter * 3 - settingsBack.width
		height: headerRoot.height - tabGutter * 2

		orientation: ListView.Horizontal
		spacing: tabGutter
		clip: true

		model: operations
		delegate: Item {
			height: headerRoot.height - tabGutter * 2
			width: cap ? height : tabWidth

			Rectangle {
				width: parent.width
				height: parent.height

				radius: height / 5
				color: "#1e2126"
			}
		}
	}

	Rectangle {
		id: settingsBack

		width: height
		height: headerRoot.height - tabGutter * 2

		anchors.right: parent.right
		anchors.rightMargin: tabGutter

		y: tabGutter

		radius: height / 5
		color: "#1e2126"
	}
}
