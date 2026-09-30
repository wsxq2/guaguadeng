import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    required property var controller
    width: 840
    height: 480
    visible: true
    title: "刮刮登 · 交互验证"
    color: "#123f36"

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.topMargin: 12
        anchors.bottomMargin: 12
        spacing: 12

        // ApplicationWindow 已自动为系统安全区域留白，不重复叠加。
        ScrollView {
            id: bodyScroll
            objectName: "bodyScroll"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 0
            clip: true
            contentWidth: availableWidth
            contentHeight: body.implicitHeight
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            ColumnLayout {
                id: body
                width: bodyScroll.availableWidth
                spacing: 12
                Label {
                    text: "刮刮登"
                    color: "#f3ead5"
                    font.pixelSize: 26
                    font.bold: true
                }
                Label {
                    text: "点击选牌，再次点击取消。此页面仅验证选牌与规则调用，不执行对局。"
                    color: "#cfdfd7"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                Flickable {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 154
                    Layout.minimumHeight: 154
                    Layout.maximumHeight: 154
                    contentWidth: cardRow.width
                    contentHeight: height
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    Row {
                        id: cardRow
                        spacing: 12
                        x: Math.max(0, (parent.width - width) / 2)
                        Repeater {
                            model: window.controller.cards
                            delegate: Rectangle {
                                required property var modelData
                                width: 78
                                height: 124
                                y: modelData.selected ? 0 : 14
                                radius: 9
                                color: modelData.selected ? "#fff0c5" : "#fffaf0"
                                border.width: modelData.selected ? 3 : 1
                                border.color: modelData.selected ? "#e6b652" : "#b5c3b9"
                                Column {
                                    anchors.centerIn: parent
                                    spacing: 4
                                    Text {
                                        text: modelData.value
                                        font.pixelSize: 32
                                        color: modelData.red ? "#b52c37" : "#172c2a"
                                    }
                                    Text {
                                        text: modelData.suit
                                        font.pixelSize: 30
                                        color: modelData.red ? "#b52c37" : "#172c2a"
                                    }
                                }
                                TapHandler { onTapped: window.controller.toggle(modelData.index) }
                            }
                        }
                    }
                }
            }
        }
        Label {
            objectName: "feedbackLabel"
            text: window.controller.message
            color: "#ffffff"
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }
        RowLayout {
            objectName: "actionRow"
            Layout.minimumHeight: 48
            Layout.alignment: Qt.AlignHCenter
            spacing: 16
            Button {
                objectName: "clearButton"
                text: "清空选择"
                Layout.preferredHeight: 48
                onClicked: window.controller.clear()
            }
            Button {
                objectName: "validateButton"
                text: "验证领牌"
                enabled: window.controller.hasSelection
                Layout.preferredHeight: 48
                onClicked: window.controller.validate()
            }
        }
    }
}
