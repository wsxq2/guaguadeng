import QtQuick
import QtQuick.Controls

Column {
    id: root
    required property var controller
    required property int playerId
    property var play: controller ? controller.roundPlays.find(p => p.playerId === playerId) : null
    property var award: controller && controller.showingPreviousRound
                        ? controller.roundAwards.find(a => a.playerId === playerId) : null
    spacing: 2
    Row {
        spacing: 3
        Repeater {
            model: root.play ? root.play.cards : []
            delegate: Rectangle {
                required property var modelData
                width: 28; height: 23; radius: 3
                color: "#fff8e8"
                Row {
                    anchors.centerIn: parent
                    Text { text: modelData.value; font.pixelSize: 12; color: modelData.red ? "#b52c37" : "#18382e" }
                    SuitIcon { suitName: modelData.suitName; width: 12; height: 16 }
                }
            }
        }
    }
    Label {
        visible: !!root.award
        text: root.award ? (root.award.winner ? "胜 · 获牌 +" + root.award.gained : "获牌 +0") : ""
        color: "#efca7b"
        font.pixelSize: 11
    }
}
