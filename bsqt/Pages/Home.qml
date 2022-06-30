import QtQuick 2.8
import QtQuick.Window 2.15

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

import "../CommonUI"

Item {
	id: home
	anchors.fill: parent

	PageTitle {
		id: homeTitle
		text: "Welcome"
	}

	Text {
		width: pageWidth
		height: font.pixelSize * 8

		anchors.right: parent.right
		anchors.rightMargin: pageWidthOffset / 2
		anchors.top: homeTitle.bottom
		anchors.topMargin: 24

		color: colors.text
		text: "Welcome to bigscraper-qt. To get started, <a href=\"https://fr75s.github.io/bigscraperqt/guide/index.html\"> you may want to refer to the guide,</a> which will help you learn how to scrape games with this tool. Otherwise, choose an option above or below to scrape or export data."
		textFormat: Text.RichText
		wrapMode: Text.WordWrap
		font.family: outfit.name
		font.pixelSize: 18
		font.weight: Font.Medium

		onLinkActivated: Qt.openUrlExternally(link)
	}

	BsqtButton {
		id: scrapeShortcut

		anchors.bottom: parent.bottom
		anchors.bottomMargin: 48
		anchors.left: parent.left
		anchors.leftMargin: pageWidth * 0.1

		width: pageWidth * 0.4
		height: 72
		label: "Scrape"

		onClicked: {
			currentPage = 2
		}
	}

	BsqtButton {
		id: exportShortcut

		anchors.bottom: parent.bottom
		anchors.bottomMargin: 48
		anchors.right: parent.right
		anchors.rightMargin: pageWidth * 0.1

		width: pageWidth * 0.4
		height: 72
		label: "Export"

		onClicked: {
			currentPage = 3
		}
	}


}
