import QtQuick
import QtQuick.Controls

Rectangle {
    required property var player
    implicitWidth: 118
    implicitHeight: 64
    radius: 12
    color: player.active ? "#286653" : "#193f37"
    border.color: player.active ? "#efca7b" : "#4d7162"
    border.width: player.active ? 2 : 1
    Column {
        anchors.centerIn: parent
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
    }
}
