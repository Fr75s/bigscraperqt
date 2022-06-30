import QtQuick 2.8

Text {
	width: pageWidth
	height: font.pixelSize

	anchors.right: parent.right
	anchors.rightMargin: pageWidthOffset / 2
	anchors.top: parent.top
	anchors.topMargin: 48 + toolbarHeight

	horizontalAlignment: Text.AlignLeft
	verticalAlignment: Text.AlignVCenter

	color: colors.text
	text: "_"
	font.family: outfit.name
	font.pixelSize: 56
	font.weight: Font.Medium
}
