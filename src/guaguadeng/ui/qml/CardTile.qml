import QtQuick
import QtQuick.Window

// 统一的牌面：点数在上、花色在下；供手牌、出牌区、已获牌复用。
// 默认尺寸随所在窗口高度自适应（矮窗口用小尺寸），使用处也可显式覆盖。
Rectangle {
    id: tile
    required property var card
    property bool selected: false
    property bool showBorder: true
    readonly property bool compact: Window.window !== null && Window.height < 400
    implicitWidth: compact ? 30 : 58
    implicitHeight: (compact ? 85 : 100) - 10
    property int fontSize: compact ? 20 : 28
    property int suitSize: compact ? 20 : 26
    radius: 6
    color: selected ? "#ffe2a0" : "#fff8e8"
    border.width: showBorder ? (selected ? 3 : 1) : 0
    border.color: selected ? "#e8b54d" : "#b2c4b7"
    Column {
        anchors.centerIn: parent
        spacing: 2
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: tile.card.value
            font.pixelSize: tile.fontSize
            color: tile.card.red ? "#b52c37" : "#18382e"
        }
        SuitIcon {
            anchors.horizontalCenter: parent.horizontalCenter
            suitName: tile.card.suitName
            width: tile.suitSize
            height: width
        }
    }
}
