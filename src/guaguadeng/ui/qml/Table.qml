import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    required property var controller
    width: 960
    height: 640
    visible: true
    title: "刮刮登"
    color: "#103b32"
    property bool compact: width < 560

    // ApplicationWindow 负责系统安全区域；仅在内容区添加普通边距。
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "刮刮登" + (controller.gameNumber ? " · 第" + controller.gameNumber + "局" : "")
                font.pixelSize: 20
                font.bold: true
                color: "#f5e7c9"
                Layout.fillWidth: true
            }
            Button {
                objectName: "endButton"
                text: "结束本场"
                visible: controller.phase === "PLAYING" || controller.phase === "FINISHED"
                onClicked: endDialog.open()
            }
        }
        ScrollView {
            id: scroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 0
            contentWidth: availableWidth
            contentHeight: body.implicitHeight
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ColumnLayout {
                id: body
                width: scroll.availableWidth
                spacing: 10
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: window.compact ? 310 : 230
                    PlayerPanel {
                        player: controller.players[1]
                        anchors.top: parent.top
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    PlayerPanel {
                        player: controller.players[2]
                        anchors.left: parent.left
                        y: window.compact ? 75 : 83
                    }
                    PlayerPanel {
                        player: controller.players[0]
                        anchors.right: parent.right
                        y: window.compact ? 75 : 83
                    }
                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        y: window.compact ? 145 : 72
                        width: window.compact ? parent.width : Math.max(180, parent.width - 256)
                        height: 150
                        radius: 16
                        color: "#174a3d"
                        border.color: "#3a6656"
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            Label {
                                text: controller.showingPreviousRound ? "上一轮出牌" : "本轮出牌 · 逆时针行动"
                                color: "#d5bf86"
                                font.pixelSize: 12
                            }
                            Repeater {
                                model: controller.roundPlays
                                delegate: Label {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    text: controller.players[modelData.playerId].name + "：  "
                                          + modelData.cards.map(c => c.value + c.suit).join("   ")
                                    color: "#fff3db"
                                    font.pixelSize: 16
                                    elide: Text.ElideRight
                                }
                            }
                            Label {
                                visible: controller.roundPlays.length === 0
                                text: controller.phase === "READY" ? "一位真人 · 三位 AI\n准备好就开始吧" : "等待领牌"
                                color: "#aec8b7"
                            }
                            Item { Layout.fillHeight: true }
                        }
                    }
                }
                Label {
                    Layout.fillWidth: true
                    text: "你 · " + controller.players[3].score + "分"
                          + (controller.players[3].dealer ? " · 庄家" : "")
                          + "  |  已获" + controller.players[3].wonCount + "张"
                          + (controller.humanTurn ? "  ·  轮到你" : "")
                    color: controller.humanTurn ? "#efca7b" : "#d0dfd6"
                    horizontalAlignment: Text.AlignHCenter
                }
                Flickable {
                    id: hand
                    objectName: "handView"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    contentWidth: handRow.width
                    contentHeight: height
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    Row {
                        id: handRow
                        spacing: 6
                        x: Math.max(0, (hand.width - width) / 2)
                        Repeater {
                            model: controller.cards
                            delegate: Rectangle {
                                required property var modelData
                                objectName: "handCard" + modelData.index
                                width: 58
                                height: 90
                                y: modelData.selected ? 0 : 10
                                radius: 8
                                color: modelData.selected ? "#ffe2a0" : "#fff8e8"
                                border.color: modelData.selected ? "#e8b54d" : "#b2c4b7"
                                border.width: modelData.selected ? 3 : 1
                                Column {
                                    anchors.centerIn: parent
                                    Text {
                                        text: modelData.value
                                        font.pixelSize: 28
                                        color: modelData.red ? "#b52c37" : "#18382e"
                                    }
                                    Text {
                                        text: modelData.suit
                                        font.pixelSize: 24
                                        color: modelData.red ? "#b52c37" : "#18382e"
                                    }
                                }
                                TapHandler {
                                    enabled: controller.humanTurn
                                    onTapped: controller.toggle(modelData.index)
                                }
                            }
                        }
                    }
                }
                Label {
                    visible: controller.phase === "PLAYING" && controller.cards.length > 0
                    text: "点击选牌，再次点击取消 · 手牌可左右滑动"
                    color: "#aec8b7"
                    font.pixelSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
                ColumnLayout {
                    visible: controller.phase === "FINISHED" || controller.phase === "ENDED"
                    Layout.fillWidth: true
                    Label {
                        text: controller.phase === "FINISHED" ? "本局结算" : "本场结束 · 累计积分"
                        color: "#efca7b"
                        font.pixelSize: 20
                    }
                    Repeater {
                        model: controller.players
                        delegate: Label {
                            required property var modelData
                            text: modelData.name + "：" + modelData.score + "分"
                                  + (controller.phase === "FINISHED"
                                     ? " （本局 " + (modelData.gameScore > 0 ? "+" : "") + modelData.gameScore + "）" : "")
                            color: "#fff3db"
                        }
                    }
                }
            }
        }
        Label {
            objectName: "feedbackLabel"
            text: controller.message
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            color: "#fff3db"
        }
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 8
            visible: controller.phase === "PLAYING"
            Button {
                objectName: "clearButton"
                text: "清空"
                Layout.preferredHeight: 48
                enabled: controller.humanTurn && controller.hasSelection
                onClicked: controller.clear()
            }
            Button {
                objectName: "hintButton"
                text: "提示"
                Layout.preferredHeight: 48
                enabled: controller.humanTurn
                onClicked: controller.hint()
            }
            Button {
                objectName: "playButton"
                text: "出牌"
                Layout.preferredHeight: 48
                enabled: controller.humanTurn && controller.hasSelection
                onClicked: controller.submit()
            }
        }
        Button {
            objectName: "startButton"
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredHeight: 48
            visible: controller.phase !== "PLAYING"
            text: controller.phase === "READY" ? "开始游戏" : controller.phase === "FINISHED" ? "下一局" : "新的一场"
            onClicked: {
                if (controller.phase === "ENDED") controller.newSession()
                controller.startNextGame()
            }
        }
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
