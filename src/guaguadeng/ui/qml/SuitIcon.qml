import QtQuick

// 绘制花色轮廓，不依赖 Android 字体或 emoji 回退。
Canvas {
    required property string suitName
    property color ink: (suitName === "HEARTS" || suitName === "DIAMONDS") ? "#c33343" : "#18382e"
    implicitWidth: 24
    implicitHeight: 24
    onSuitNameChanged: requestPaint()
    onInkChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onPaint: {
        let c = getContext("2d")
        c.reset(); c.scale(width / 100, height / 100)
        c.fillStyle = ink; c.beginPath()
        if (suitName === "DIAMONDS") {
            c.moveTo(50, 3); c.lineTo(93, 50); c.lineTo(50, 97); c.lineTo(7, 50)
        } else if (suitName === "HEARTS") {
            c.moveTo(50, 94)
            c.bezierCurveTo(-30, 38, 8, -18, 50, 22)
            c.bezierCurveTo(92, -18, 130, 38, 50, 94)
        } else if (suitName === "SPADES") {
            c.moveTo(50, 3)
            c.bezierCurveTo(-25, 56, 8, 100, 44, 68)
            c.lineTo(30, 97); c.lineTo(70, 97); c.lineTo(56, 68)
            c.bezierCurveTo(92, 100, 125, 56, 50, 3)
        } else {
            c.arc(50, 25, 23, 0, 2*Math.PI)
            c.moveTo(50, 59); c.arc(26, 59, 23, 0, 2*Math.PI)
            c.moveTo(97, 59); c.arc(74, 59, 23, 0, 2*Math.PI)
            c.moveTo(44, 60); c.lineTo(30, 97); c.lineTo(70, 97); c.lineTo(56, 60)
        }
        c.closePath(); c.fill()
    }
}
