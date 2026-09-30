# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'player_area.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_PlayerArea(object):
    def setupUi(self, PlayerArea):
        if not PlayerArea.objectName():
            PlayerArea.setObjectName(u"PlayerArea")
        PlayerArea.resize(400, 300)
        self.gridLayout = QGridLayout(PlayerArea)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelAvatar = QLabel(PlayerArea)
        self.labelAvatar.setObjectName(u"labelAvatar")

        self.horizontalLayout_2.addWidget(self.labelAvatar)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelName = QLabel(PlayerArea)
        self.labelName.setObjectName(u"labelName")

        self.verticalLayout.addWidget(self.labelName)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(PlayerArea)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.labelScore = QLabel(PlayerArea)
        self.labelScore.setObjectName(u"labelScore")

        self.horizontalLayout.addWidget(self.labelScore)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(PlayerArea)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.labelCardCount = QLabel(PlayerArea)
        self.labelCardCount.setObjectName(u"labelCardCount")

        self.horizontalLayout_3.addWidget(self.labelCardCount)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_7 = QLabel(PlayerArea)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_4.addWidget(self.label_7)

        self.widgetAcquiredCard = QWidget(PlayerArea)
        self.widgetAcquiredCard.setObjectName(u"widgetAcquiredCard")

        self.horizontalLayout_4.addWidget(self.widgetAcquiredCard)


        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_8 = QLabel(PlayerArea)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_5.addWidget(self.label_8)

        self.widgetOutCard = QWidget(PlayerArea)
        self.widgetOutCard.setObjectName(u"widgetOutCard")

        self.horizontalLayout_5.addWidget(self.widgetOutCard)


        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 0, 1, 1)

        self.labelCountdown = QLabel(PlayerArea)
        self.labelCountdown.setObjectName(u"labelCountdown")

        self.gridLayout.addWidget(self.labelCountdown, 4, 0, 1, 1)


        self.retranslateUi(PlayerArea)

        QMetaObject.connectSlotsByName(PlayerArea)
    # setupUi

    def retranslateUi(self, PlayerArea):
        PlayerArea.setWindowTitle(QCoreApplication.translate("PlayerArea", u"Form", None))
        self.labelAvatar.setText(QCoreApplication.translate("PlayerArea", u"TextLabel", None))
        self.labelName.setText(QCoreApplication.translate("PlayerArea", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("PlayerArea", u"\u5206\u6570\uff1a", None))
        self.labelScore.setText(QCoreApplication.translate("PlayerArea", u"TextLabel", None))
        self.label_5.setText(QCoreApplication.translate("PlayerArea", u"\u624b\u724c\u6570\u91cf\uff1a", None))
        self.labelCardCount.setText(QCoreApplication.translate("PlayerArea", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("PlayerArea", u"\u5df2\u83b7\u5361\u724c\uff1a", None))
        self.label_8.setText(QCoreApplication.translate("PlayerArea", u"\u51fa\u7684\u5361\u724c:", None))
        self.labelCountdown.setText(QCoreApplication.translate("PlayerArea", u"TextLabel", None))
    # retranslateUi

