import QtQuick
import QtQuick.Controls

Rectangle {
    id: panel
    required property var player
    implicitWidth: 118
    implicitHeight: 88
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
            height: 22
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
                    delegate: Rectangle {
                        required property var modelData
                        width: 28
                        height: 22
                        radius: 3
                        color: "#fff8e8"
                        Row {
                            anchors.centerIn: parent
                            Text {
                                text: modelData.value
                                font.pixelSize: 12
                                color: modelData.red ? "#b52c37" : "#18382e"
                            }
                            SuitIcon { suitName: modelData.suitName; width: 12; height: 16 }
                        }
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
