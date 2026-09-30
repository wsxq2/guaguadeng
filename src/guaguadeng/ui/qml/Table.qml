import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    required property var controller
    property int startWidth: 960
    property int startHeight: 640
    width: startWidth
    height: startHeight
    visibility: Qt.platform.os === "android" ? Window.FullScreen : Window.Windowed
    title: "刮刮登"
    color: "#103b32"
    property bool compact: width < 560

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 6
        spacing: 3
        Label {
            objectName: "feedbackLabel"
            text: "第" + controller.gameNumber + "局 · " + controller.message
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 16
            color: "#fff3db"
            horizontalAlignment: Text.AlignHCenter
        }
        Item {
            id: table
            objectName: "tableArea"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 0
            // 北方玩家在所有窗口比例下都固定正上方。
            PlayerPanel {
                id: north
                objectName: "northPlayer"
                player: controller.players[1]
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
            }
            SeatPlay {
                objectName: "northPlay"
                controller: window.controller; playerId: 1
                anchors.left: window.compact ? north.left : north.right
                anchors.leftMargin: 5
                anchors.top: window.compact ? north.bottom : north.top
            }
            PlayerPanel {
                id: west
                objectName: "westPlayer"
                player: controller.players[2]
                anchors.left: parent.left
                anchors.bottom: parent.bottom
            }
            SeatPlay {
                objectName: "westPlay"
                controller: window.controller; playerId: 2
                anchors.left: window.compact ? west.left : west.right
                anchors.leftMargin: window.compact ? 0 : 5
                anchors.bottom: window.compact ? west.top : west.bottom
            }
            PlayerPanel {
                id: east
                objectName: "eastPlayer"
                player: controller.players[0]
                anchors.right: parent.right
                anchors.bottom: parent.bottom
            }
            SeatPlay {
                objectName: "eastPlay"
                controller: window.controller; playerId: 0
                anchors.right: window.compact ? east.right : east.left
                anchors.rightMargin: window.compact ? 0 : 5
                anchors.bottom: window.compact ? east.top : east.bottom
            }
            SeatPlay {
                objectName: "southPlay"
                controller: window.controller; playerId: 3
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
            }
            Rectangle {
                visible: controller.phase === "FINISHED" || controller.phase === "ENDED"
                anchors.centerIn: parent
                width: Math.min(210, parent.width)
                height: summary.implicitHeight + 12
                color: "#174a3d"
                radius: 8
                Column {
                    id: summary
                    anchors.centerIn: parent
                    spacing: 2
                    Label { text: "累计积分"; color: "#efca7b"; font.pixelSize: 12 }
                    Repeater {
                        model: controller.players
                        delegate: Label {
                            required property var modelData
                            text: modelData.name + "：" + modelData.score + "分"
                                + (controller.phase === "FINISHED" ? " （本局 " + modelData.gameScore + "）" : "")
                            color: "#fff3db"
                            font.pixelSize: 12
                        }
                    }
                }
            }
        }
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 4
            visible: controller.phase === "PLAYING" || controller.phase === "FINISHED"
            Button {
                objectName: "endButton"
                text: "结束"
                Layout.preferredWidth: 96
                Layout.preferredHeight: 48
                font.pixelSize: 12
                onClicked: endDialog.open()
            }
            Button {
                objectName: "clearButton"
                visible: controller.phase === "PLAYING"
                text: "清空"
                Layout.preferredWidth: 96
                Layout.preferredHeight: 48
                font.pixelSize: 12
                enabled: controller.humanTurn && controller.hasSelection
                onClicked: controller.clear()
            }
            Button {
                objectName: "hintButton"
                visible: controller.phase === "PLAYING"
                text: "提示"
                Layout.preferredWidth: 96
                Layout.preferredHeight: 48
                font.pixelSize: 12
                enabled: controller.humanTurn
                onClicked: controller.hint()
            }
            Button {
                objectName: "playButton"
                visible: controller.phase === "PLAYING"
                text: "出牌"
                Layout.preferredWidth: 96
                Layout.preferredHeight: 48
                font.pixelSize: 12
                enabled: controller.humanTurn && controller.hasSelection
                onClicked: controller.submit()
            }
        }
        Button {
            objectName: "startButton"
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 96
                Layout.preferredHeight: 48
                font.pixelSize: 12
            visible: controller.phase !== "PLAYING"
            enabled: !controller.reviewingRound
            text: controller.phase === "READY" ? "开始游戏" : controller.phase === "FINISHED" ? "下一局" : "新的一场"
            onClicked: {
                if (controller.phase === "ENDED") controller.newSession()
                controller.startNextGame()
            }
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 6
            PlayerPanel {
                objectName: "selfPlayer"
                player: controller.players[3]
                Layout.alignment: Qt.AlignVCenter
            }
                Flickable {
                    id: hand
                    objectName: "handView"
                    Layout.fillWidth: true
                    Layout.preferredHeight: window.height < 400 ? 72 : 100
                    Layout.minimumHeight: Layout.preferredHeight
                    Layout.maximumHeight: Layout.preferredHeight
                    contentWidth: handRow.x + handRow.width
                    contentHeight: height
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    Row {
                        id: handRow
                        spacing: 6
                        x: 12
                        Repeater {
                            model: controller.cards
                            delegate: CardTile {
                                required property var modelData
                                objectName: "handCard" + modelData.index
                                card: modelData
                                y: modelData.selected ? 0 : 10
                                radius: 8
                                selected: modelData.selected
                                TapHandler {
                                    enabled: controller.humanTurn
                                    onTapped: controller.toggle(modelData.index)
                                }
                            }
                        }
                    }
                }
        }
    }
    Shortcut {
        sequence: "F11"
        onActivated: window.visibility = window.visibility === Window.FullScreen ? Window.Windowed : Window.FullScreen
    }
    Dialog {
        id: endDialog
        objectName: "endDialog"
        anchors.centerIn: parent
        width: Math.min(window.width - 40, 350)
        modal: true
        title: "结束本场？"
        standardButtons: Dialog.Ok | Dialog.Cancel
        Label {
            width: parent.width
            text: "保留已完成局的累计积分，未完成局不计分。"
            wrapMode: Text.WordWrap
        }
        onAccepted: controller.endSession()
    }
}
