"""Qt abstraction layer supporting both PyQt6 and PySide6."""

import sys

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import (
        Qt, QPoint, QRect, QSize, QUrl, QTimer, QThread, QByteArray, QBuffer,
        QEvent, pyqtSignal as Signal, pyqtSlot as Slot
    )
    from PyQt6.QtGui import (
        QAction, QColor, QFont, QFontDatabase, QIcon, QImage, QKeySequence,
        QPainter, QPainterPath, QPen, QBrush, QPixmap, QLinearGradient,
        QRadialGradient, QCursor, QClipboard
    )
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QDialog, QMainWindow, QLabel, QPushButton,
        QLineEdit, QTextEdit, QScrollArea, QVBoxLayout, QHBoxLayout,
        QGridLayout, QStackedLayout, QFrame, QMenu, QSystemTrayIcon,
        QGraphicsDropShadowEffect, QSizePolicy, QFileDialog, QCheckBox,
        QSpinBox, QComboBox, QSplitter, QListWidget, QListWidgetItem
    )
    QT_BINDING = "PyQt6"
except ImportError:
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        from PySide6.QtCore import (
            Qt, QPoint, QRect, QSize, QUrl, QTimer, QThread, QByteArray, QBuffer,
            QEvent, Signal, Slot
        )
        from PySide6.QtGui import (
            QAction, QColor, QFont, QFontDatabase, QIcon, QImage, QKeySequence,
            QPainter, QPainterPath, QPen, QBrush, QPixmap, QLinearGradient,
            QRadialGradient, QCursor, QClipboard
        )
        from PySide6.QtWidgets import (
            QApplication, QWidget, QDialog, QMainWindow, QLabel, QPushButton,
            QLineEdit, QTextEdit, QScrollArea, QVBoxLayout, QHBoxLayout,
            QGridLayout, QStackedLayout, QFrame, QMenu, QSystemTrayIcon,
            QGraphicsDropShadowEffect, QSizePolicy, QFileDialog, QCheckBox,
            QSpinBox, QComboBox, QSplitter, QListWidget, QListWidgetItem
        )
        QT_BINDING = "PySide6"
    except ImportError:
        # Allow importing modules without Qt installed (e.g. for CLI/headless tests)
        QtCore = None
        QtGui = None
        QtWidgets = None
        Qt = None
        Signal = None
        Slot = None
        QByteArray = None
        QBuffer = None
        QEvent = None
        QT_BINDING = None
