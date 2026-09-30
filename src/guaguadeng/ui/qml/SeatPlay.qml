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
        spacing: 4
        Repeater {
            model: root.play ? root.play.cards : []
            delegate: CardTile {
                required property var modelData
                card: modelData
                radius: 4
                showBorder: false
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
