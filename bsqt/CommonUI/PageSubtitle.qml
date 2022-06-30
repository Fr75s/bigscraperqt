import QtQuick 2.8

Text {
	width: pageWidth
	height: font.pixelSize

	anchors.right: parent.right
	anchors.rightMargin: pageWidthOffset / 2

	horizontalAlignment: Text.AlignLeft
	verticalAlignment: Text.AlignVCenter

	color: colors.text
	text: "_"
	font.family: outfit.name
	font.pixelSize: 24
	font.weight: Font.Medium
}
