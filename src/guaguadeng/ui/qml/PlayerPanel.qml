import QtQuick
import QtQuick.Controls

Rectangle {
    id: panel
    required property var player
    implicitWidth: 150
    implicitHeight: 120
    radius: 12
    color: player.active ? "#286653" : "#193f37"
    border.color: player.active ? "#efca7b" : "#4d7162"
    border.width: player.active ? 2 : 1
    Column {
        anchors.centerIn: parent
        width: parent.width - 12
        spacing: 3
        Label {
            text: player.name + (player.dealer ? " · 庄" : "") + (player.active ? " · 出牌" : "")
            color: "#fff1d6"
            font.bold: true
        }
        Label {
            text: player.score + "分  ·  剩" + player.handCount + "张"
            color: "#d0dfd6"
            font.pixelSize: 12
        }
        Label {
            text: "已获 " + player.wonCount + " 张"
            color: "#efca7b"
            font.pixelSize: 12
        }
        Flickable {
            objectName: "wonCardsView"
            width: parent.width
            height: 36
            contentWidth: wonRow.width
            contentHeight: height
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            flickableDirection: Flickable.HorizontalFlick
            Row {
                id: wonRow
                spacing: 3
                Repeater {
                    model: panel.player.wonCards
                    delegate: CardTile {
                        required property var modelData
                        card: modelData
                        width: 22
                        height: 36
                        radius: 3
                        showBorder: false
                        fontSize: 12
                        suitSize: 12
                    }
                }
            }
            Label {
                visible: panel.player.wonCount === 0
                text: "暂无获牌"
                color: "#aec8b7"
                font.pixelSize: 11
            }
        }
    }
}
