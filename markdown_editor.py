import os
import re
import sys
import ctypes

import markdown
from PyQt5.QtCore import QRect, QRegExp, QSize, Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import (QColor, QFont, QIcon, QImageReader, QKeySequence,
                         QPainter, QPixmap, QSyntaxHighlighter, QTextCharFormat,
                         QTextFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QInputDialog,
                             QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
                             QStyle, QTabWidget, QTextBrowser, QTextEdit,
                             QToolBar, QWidget)

APP_NAME = "MK编辑器"
APP_VERSION = "1.0.0"
FILE_FILTER = "Markdown 文件 (*.md *.markdown);;文本文件 (*.txt);;所有文件 (*.*)"


def setup_rounded_menu(menu):
    menu.setAttribute(Qt.WA_TranslucentBackground, True)
    menu.setWindowFlag(Qt.FramelessWindowHint, True)
    menu.setWindowFlag(Qt.NoDropShadowWindowHint, True)

LIGHT_QSS = """
QMenuBar,
QMenu,
QToolBar,
QToolButton,
QTabBar,
QStatusBar,
QPushButton,
QLineEdit,
QLabel {
    font-size: 22px;
}

QMenu::item,
QTabBar::tab {
    font-size: 22px;
}
QMainWindow { background: #f6f8fa; }
QMenuBar {
    background: #ffffff;
    color: #24292e;
    border-bottom: 1px solid #e1e4e8;
}
QMenuBar::item { background: transparent; padding: 6px 10px; border-radius: 4px; }
QMenuBar::item:selected { background: #eaecef; }
QMenuBar::item:pressed { background: #dfe2e5; }
QMenu {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 4px;
}
QMenu::item { padding: 8px 26px 8px 20px; border-radius: 4px; color: #24292e; }
QMenu::item:selected { background: #eaecef; }
QMenu::item:disabled { color: #b0b6bc; }
QMenu::separator { height: 1px; background: #eaecef; margin: 4px 8px; }
QToolBar {
    background: #f6f8fa;
    border: none;
    border-bottom: 1px solid #e1e4e8;
    padding: 3px;
    spacing: 2px;
}
QToolBar::separator { width: 1px; background: #d0d7de; margin: 4px 6px; }
QToolButton {
    background: transparent;
    border: none;
    border-radius: 5px;
    padding: 7px;
}
QToolButton:hover { background: #eaecef; }
QToolButton:pressed { background: #dfe2e5; }
QToolButton:disabled { color: #b0b6bc; }
QTabWidget::pane { border: none; background: #fdfdfd; }
QTabBar { background: #f6f8fa; }
QTabBar::tab {
    background: transparent;
    color: #57606a;
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: #0969da; border-bottom: 2px solid #0969da; }
QTabBar::tab:hover { background: #eaecef; }
QStatusBar {
    background: #ffffff;
    color: #57606a;
    border-top: 1px solid #e1e4e8;
    padding: 2px;
}
QPlainTextEdit#editor {
    background-color: #fdfdfd;
    color: #24292e;
    selection-background-color: #b3d7ff;
    border: none;
}
QTextBrowser#preview { background-color: #ffffff; border: none; }
QScrollBar:vertical { background: transparent; width: 12px; margin: 2px; }
QScrollBar::handle:vertical { background: #c8ccd0; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #a8adb2; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { background: transparent; height: 12px; margin: 2px; }
QScrollBar::handle:horizontal { background: #c8ccd0; border-radius: 5px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #a8adb2; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
QPushButton {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 5px 14px;
    color: #24292e;
}
QPushButton:hover { background: #eaecef; }
QPushButton:pressed { background: #dfe2e5; }
QPushButton:default { background: #0969da; color: #ffffff; border: none; }
QLineEdit {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 4px 8px;
    color: #24292e;
    selection-background-color: #b3d7ff;
}
QLabel { color: #24292e; }
QToolTip { background-color: #24292e; color: #ffffff; border: none; padding: 4px 8px; }
"""

DARK_QSS = """
QMenuBar,
QMenu,
QToolBar,
QToolButton,
QTabBar,
QStatusBar,
QPushButton,
QLineEdit,
QLabel {
    font-size: 22px;
}

QMenu::item,
QTabBar::tab {
    font-size: 22px;
}
QMainWindow { background: #0d1117; }
QMenuBar {
    background: #161b22;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
}
QMenuBar::item { background: transparent; padding: 8px 26px 8px 20px; border-radius: 4px; }
QMenuBar::item:selected { background: #21262d; }
QMenuBar::item:pressed { background: #30363d; }
QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 4px;
}
QMenu::item { padding: 8px 26px 8px 20px; border-radius: 4px; color: #e6edf3; }
QMenu::item:selected { background: #21262d; }
QMenu::item:disabled { color: #6e7681; }
QMenu::separator { height: 1px; background: #30363d; margin: 4px 8px; }
QToolBar {
    background: #161b22;
    border: none;
    border-bottom: 1px solid #30363d;
    padding: 3px;
    spacing: 2px;
}
QToolBar::separator { width: 1px; background: #30363d; margin: 4px 6px; }
QToolButton {
    background: transparent;
    border: none;
    border-radius: 5px;
    padding: 7px;
}
QToolButton:hover { background: #21262d; }
QToolButton:pressed { background: #30363d; }
QToolButton:disabled { color: #6e7681; }
QTabWidget::pane { border: none; background: #0d1117; }
QTabBar { background: #161b22; }
QTabBar::tab {
    background: transparent;
    color: #8b949e;
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected { color: #58a6ff; border-bottom: 2px solid #58a6ff; }
QTabBar::tab:hover { background: #21262d; }
QStatusBar {
    background: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
    padding: 2px;
}
QPlainTextEdit#editor {
    background-color: #0d1117;
    color: #e6edf3;
    selection-background-color: #264f78;
    border: none;
}
QTextBrowser#preview { background-color: #0d1117; border: none; }
QScrollBar:vertical { background: transparent; width: 12px; margin: 2px; }
QScrollBar::handle:vertical { background: #484f58; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #5c636d; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { background: transparent; height: 12px; margin: 2px; }
QScrollBar::handle:horizontal { background: #484f58; border-radius: 5px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #5c636d; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
QPushButton {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 14px;
    color: #e6edf3;
}
QPushButton:hover { background: #30363d; }
QPushButton:pressed { background: #21262d; }
QPushButton:default { background: #1f6feb; color: #ffffff; border: none; }
QLineEdit {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 8px;
    color: #e6edf3;
    selection-background-color: #264f78;
}
QLabel { color: #e6edf3; }
QToolTip { background-color: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 4px 8px; }
"""

def build_preview_css(zoom, dark=1):
    body = int(round(17 * zoom))
    if dark:
        text = "#e6edf3"
        code_bg = "#161b22"
        code_border = "#30363d"
        quote_color = "#8b949e"
        quote_border = "#30363d"
        table_border = "#30363d"
        th_bg = "#161b22"
        hr_color = "#30363d"
        link = "#58a6ff"
    else:
        text = "#24292e"
        code_bg = "#f6f8fa"
        code_border = "#e1e4e8"
        quote_color = "#6a737d"
        quote_border = "#dfe2e5"
        table_border = "#dfe2e5"
        th_bg = "#f6f8fa"
        hr_color = "#eaecef"
        link = "#0366d6"
    return """
body {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: %dpx;
    color: %s;
    line-height: 1.6;
    margin: 12px;
}
code {
    font-family: "Consolas", "Courier New", monospace;
    background-color: %s;
    padding: .15em .4em;
    border-radius: 4px;
    font-size: 0.9em;
}
pre {
    background-color: %s;
    border: 1px solid %s;
    border-radius: 6px;
    padding: 12px;
    overflow-x: auto;
}
pre code { background: none; padding: 0; border: none; }
blockquote {
    border-left: 4px solid %s;
    color: %s;
    margin: 0;
    padding: 0 1em;
}
table { border-collapse: collapse; }
th, td { border: 1px solid %s; padding: 6px 13px; }
th { background-color: %s; }
img { max-width: 100%%; }
hr { border: none; border-top: 2px solid %s; }
a { color: %s; text-decoration: none; }
""" % (body, text, code_bg, code_bg, code_border, quote_border, quote_color,
       table_border, th_bg, hr_color, link)


def make_text_icon(text, color, bold=False, italic=False):
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    font = QFont("Segoe UI", 42)
    font.setBold(bold)
    font.setItalic(italic)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(pm.rect(), Qt.AlignCenter, text)
    painter.end()
    return QIcon(pm)


def resource_path(relative):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


class MarkdownHighlighter(QSyntaxHighlighter):
    PALETTES = {
        "light": {
            "header": "#0366d6", "bold": "#6f42c1", "italic": "#e36209",
            "code": "#d73a49", "link": "#0366d6", "list": "#e36209",
            "quote": "#6a737d", "hr": "#d1d5da", "codeblock": "#d73a49",
        },
        "dark": {
            "header": "#79b8ff", "bold": "#bc8cff", "italic": "#ffab70",
            "code": "#ff7b72", "link": "#79b8ff", "list": "#ffab70",
            "quote": "#8b949e", "hr": "#484f58", "codeblock": "#ff7b72",
        },
    }

    def __init__(self, document, dark=1):
        super().__init__(document)
        self.dark = dark
        self.rules = []
        self.fmt_code = QTextCharFormat()
        self.init_rules()

    def set_dark(self, dark):
        if dark == self.dark:
            return
        self.dark = dark
        self.init_rules()
        self.rehighlight()

    def _fmt(self, color, bold=False, italic=False):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def init_rules(self):
        p = self.PALETTES["dark" if self.dark else "light"]
        self.fmt_code.setForeground(QColor(p["codeblock"]))
        self.rules = [
            (QRegExp(r"^#{1,6}\s.*$"), self._fmt(p["header"], bold=True)),
            (QRegExp(r"\*\*[^*\n]+\*\*"), self._fmt(p["bold"], bold=True)),
            (QRegExp(r"__[^_\n]+__"), self._fmt(p["bold"], bold=True)),
            (QRegExp(r"(?<!\*)\*[^*\n]+\*(?!\*)"), self._fmt(p["italic"], italic=True)),
            (QRegExp(r"(?<!_)_[^_\n]+_(?!_)"), self._fmt(p["italic"], italic=True)),
            (QRegExp(r"`[^`\n]+`"), self._fmt(p["code"])),
            (QRegExp(r"\[[^\]]+\]\([^)\s]+\)"), self._fmt(p["link"])),
            (QRegExp(r"^\s*(?:[-*+]|\d+\.)\s+"), self._fmt(p["list"])),
            (QRegExp(r"^\s*>.*$"), self._fmt(p["quote"], italic=True)),
            (QRegExp(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$"), self._fmt(p["hr"])),
        ]

    def highlightBlock(self, text):
        if self.previousBlockState() == 1:
            self.setFormat(0, len(text), self.fmt_code)
            if re.match(r"^\s*```", text):
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
            return
        for regex, fmt in self.rules:
            index = regex.indexIn(text)
            while index >= 0:
                length = regex.matchedLength()
                self.setFormat(index, length, fmt)
                index = regex.indexIn(text, index + length)
        if re.match(r"^\s*```", text):
            self.setCurrentBlockState(1)
        else:
            self.setCurrentBlockState(0)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint(event)


class EditorPane(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark = 1
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(13)
        self.setFont(font)
        self.highlighter = MarkdownHighlighter(self.document())
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def set_dark(self, dark):
        self.dark = dark
        self.highlighter.set_dark(dark)
        self.line_number_area.update()
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 14 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _=0):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#161b22" if self.dark else "#f6f8fa"))
        w = self.line_number_area.width()
        painter.fillRect(
            QRect(w - 1, event.rect().top(), 1, event.rect().height()),
            QColor("#30363d" if self.dark else "#e1e4e8"))
        painter.setPen(QColor("#8b949e"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(
            block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        height = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(0, top, w - 10, height,
                                 Qt.AlignRight, str(block_number + 1))
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(
            QColor("#161b22" if self.dark else "#f0f7ff"))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        setup_rounded_menu(menu)
        menu.exec_(event.globalPos())

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    def zoom_in(self):
        font = self.font()
        if font.pointSize() < 40:
            font.setPointSize(font.pointSize() + 1)
            self.setFont(font)

    def zoom_out(self):
        font = self.font()
        if font.pointSize() > 8:
            font.setPointSize(font.pointSize() - 1)
            self.setFont(font)


class PreviewPane(QTextBrowser):
    ctrl_wheel = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("preview")
        self.setOpenExternalLinks(True)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            self.ctrl_wheel.emit(event.angleDelta().y() > 0)
            event.accept()
            return
        super().wheelEvent(event)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        setup_rounded_menu(menu)
        menu.exec_(event.globalPos())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.saved_text = ""
        self.dark = 1
        self.setWindowTitle(APP_NAME)
        self.resize(1024, 720)

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.editor = EditorPane()
        self.editor.setObjectName("editor")
        self.preview = PreviewPane()
        self.preview_zoom = 1.0

        self.tabs = QTabWidget()
        self.tabs.addTab(self.editor, "编辑")
        self.tabs.addTab(self.preview, "预览")
        self.setCentralWidget(self.tabs)

        self._build_actions()
        self._build_menu()
        self._build_toolbar()

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_status)
        self.preview.ctrl_wheel.connect(self.zoom_preview)

        self.statusBar().showMessage("就绪")
        self.apply_theme()
    # ---------- Windows 10/11 深色标题栏 ----------
    def set_title_bar_theme(self, dark):
        if os.name != "nt":
            return

        hwnd = int(self.winId())
        value = ctypes.c_int(1 if dark else 0)
        dwmapi = ctypes.windll.dwmapi

        # 20 适用于较新的 Windows，19 兼容部分旧版本
        result = dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
        )

        if result != 0:
            dwmapi.DwmSetWindowAttribute(
                hwnd, 19, ctypes.byref(value), ctypes.sizeof(value)
            )
    # ---------- 界面构建 ----------
    def _build_actions(self):
        style = self.style()
        self.act_new = QAction(style.standardIcon(QStyle.SP_FileIcon), "新建", self)
        self.act_open = QAction(style.standardIcon(QStyle.SP_DialogOpenButton), "打开...", self)
        self.act_save = QAction(style.standardIcon(QStyle.SP_DialogSaveButton), "保存", self)
        self.act_save_as = QAction("另存为...", self)
        self.act_exit = QAction("退出", self)
        self.act_undo = QAction(style.standardIcon(QStyle.SP_ArrowBack), "撤销", self)
        self.act_redo = QAction(style.standardIcon(QStyle.SP_ArrowForward), "重做", self)
        self.act_cut = QAction("剪切", self)
        self.act_copy = QAction("复制", self)
        self.act_paste = QAction("粘贴", self)
        self.act_select_all = QAction("全选", self)
        self.act_find = QAction("查找...", self)
        self.act_refresh = QAction(
            style.standardIcon(QStyle.SP_BrowserReload), "刷新预览", self)
        self.act_bold = QAction(make_text_icon("B", "#24292e", bold=True), "加粗", self)
        self.act_italic = QAction(make_text_icon("I", "#24292e", italic=True), "斜体", self)
        self.act_zoom_in = QAction("放大字体", self)
        self.act_zoom_out = QAction("缩小字体", self)
        self.act_zoom_reset = QAction("恢复默认字号", self)
        self.act_theme = QAction("切换到深色主题", self)
        self.act_about = QAction("关于", self)

        self.act_new.setShortcut(QKeySequence.New)
        self.act_open.setShortcut(QKeySequence.Open)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.act_exit.setShortcut("Ctrl+Q")
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.act_redo.setShortcut(QKeySequence.Redo)
        self.act_cut.setShortcut(QKeySequence.Cut)
        self.act_copy.setShortcut(QKeySequence.Copy)
        self.act_paste.setShortcut(QKeySequence.Paste)
        self.act_select_all.setShortcut(QKeySequence.SelectAll)
        self.act_find.setShortcut(QKeySequence.Find)
        self.act_refresh.setShortcut("F5")
        self.act_bold.setShortcut(QKeySequence.Bold)
        self.act_italic.setShortcut(QKeySequence.Italic)
        self.act_zoom_in.setShortcut(QKeySequence.ZoomIn)
        self.act_zoom_out.setShortcut(QKeySequence.ZoomOut)
        self.act_zoom_reset.setShortcut("Ctrl+0")
        self.act_theme.setShortcut("Ctrl+Shift+D")

        for action, tip in [
            (self.act_new, "新建 (Ctrl+N)"),
            (self.act_open, "打开 (Ctrl+O)"),
            (self.act_save, "保存 (Ctrl+S)"),
            (self.act_undo, "撤销 (Ctrl+Z)"),
            (self.act_redo, "重做 (Ctrl+Y)"),
            (self.act_bold, "加粗 (Ctrl+B)"),
            (self.act_italic, "斜体 (Ctrl+I)"),
            (self.act_refresh, "刷新预览 (F5)"),
        ]:
            action.setToolTip(tip)

        self.act_new.triggered.connect(self.new_file)
        self.act_open.triggered.connect(self.open_file)
        self.act_save.triggered.connect(self.save_file)
        self.act_save_as.triggered.connect(self.save_file_as)
        self.act_exit.triggered.connect(self.close)
        self.act_undo.triggered.connect(self.editor.undo)
        self.act_redo.triggered.connect(self.editor.redo)
        self.act_cut.triggered.connect(self.editor.cut)
        self.act_copy.triggered.connect(self.editor.copy)
        self.act_paste.triggered.connect(self.editor.paste)
        self.act_select_all.triggered.connect(self.editor.selectAll)
        self.act_find.triggered.connect(self.find_text)
        self.act_refresh.triggered.connect(self.refresh_preview)
        self.act_bold.triggered.connect(lambda: self.wrap_selection("**"))
        self.act_italic.triggered.connect(lambda: self.wrap_selection("*"))
        self.act_zoom_in.triggered.connect(self.zoom_in_active)
        self.act_zoom_out.triggered.connect(self.zoom_out_active)
        self.act_zoom_reset.triggered.connect(self.zoom_reset)
        self.act_theme.triggered.connect(self.toggle_theme)
        self.act_about.triggered.connect(self.show_about)

        self.act_undo.setEnabled(False)
        self.act_redo.setEnabled(False)
        self.act_cut.setEnabled(False)
        self.act_copy.setEnabled(False)
        self.editor.undoAvailable.connect(self.act_undo.setEnabled)
        self.editor.redoAvailable.connect(self.act_redo.setEnabled)
        self.editor.copyAvailable.connect(self.act_cut.setEnabled)
        self.editor.copyAvailable.connect(self.act_copy.setEnabled)

    def _build_menu(self):
        menu_file = self.menuBar().addMenu("文件(&F)")
        setup_rounded_menu(menu_file)
        menu_file.setMinimumWidth(200)
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_open)
        menu_file.addSeparator()
        menu_file.addAction(self.act_save)
        menu_file.addAction(self.act_save_as)
        menu_file.addSeparator()
        menu_file.addAction(self.act_exit)

        menu_edit = self.menuBar().addMenu("编辑(&E)")
        setup_rounded_menu(menu_edit)
        menu_edit.addAction(self.act_undo)
        menu_edit.addAction(self.act_redo)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_cut)
        menu_edit.addAction(self.act_copy)
        menu_edit.addAction(self.act_paste)
        menu_edit.addAction(self.act_select_all)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_find)

        menu_view = self.menuBar().addMenu("视图(&V)")
        setup_rounded_menu(menu_view)
        menu_view.setMinimumWidth(375)
        menu_view.addAction(self.act_refresh)
        menu_view.addAction(self.act_theme)
        menu_view.addSeparator()
        menu_view.addAction(self.act_zoom_in)
        menu_view.addAction(self.act_zoom_out)
        menu_view.addAction(self.act_zoom_reset)

        menu_help = self.menuBar().addMenu("帮助(&H)")
        setup_rounded_menu(menu_help)
        menu_help.addAction(self.act_about)

    def _build_toolbar(self):
        toolbar = QToolBar("工具栏", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        toolbar.addAction(self.act_new)
        toolbar.addAction(self.act_open)
        toolbar.addAction(self.act_save)
        toolbar.addSeparator()
        toolbar.addAction(self.act_undo)
        toolbar.addAction(self.act_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.act_bold)
        toolbar.addAction(self.act_italic)
        toolbar.addSeparator()
        toolbar.addAction(self.act_refresh)

    # ---------- 主题 ----------
    def apply_theme(self):
        QApplication.instance().setStyleSheet(DARK_QSS if self.dark else LIGHT_QSS)
        self.editor.set_dark(self.dark)
        self.set_title_bar_theme(self.dark)
        color = "#e6edf3" if self.dark else "#24292e"
        self.act_bold.setIcon(make_text_icon("B", color, bold=True))
        self.act_italic.setIcon(make_text_icon("I", color, italic=True))
        self.act_theme.setText("切换到浅色主题" if self.dark else "切换到深色主题")
        self.refresh_preview()

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme()
        self.act_theme.setText("切换到浅色主题" if self.dark else "切换到深色主题")
        self.statusBar().showMessage(
            "已切换到深色主题" if self.dark else "已切换到浅色主题")

    # ---------- 核心功能 ----------
    def is_dirty(self):
        return self.editor.toPlainText() != self.saved_text

    def on_text_changed(self):
        title = APP_NAME
        name = os.path.basename(self.current_file) if self.current_file else "无标题"
        title = "%s%s - %s" % (name, "*" if self.is_dirty() else "", APP_NAME)
        self.setWindowTitle(title)
        self.update_status()

    def update_status(self):
        text = self.editor.toPlainText()
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.statusBar().showMessage(
            "第 %d 行, 第 %d 列 | 共 %d 字符" % (line, col, len(text)))

    def on_tab_changed(self, index):
        if index == 1:
            self.refresh_preview()

    def refresh_preview(self):
        html = markdown.markdown(
            self.editor.toPlainText(), extensions=["extra", "sane_lists"])
        html = self._postprocess_html(html, self.preview_zoom)
        self.preview.setHtml(
            "<html><head><meta charset='utf-8'><style>%s</style></head>"
            "<body>%s</body></html>" % (build_preview_css(self.preview_zoom, self.dark), html))
        if self.current_file:
            self.preview.document().setBaseUrl(
                QUrl.fromLocalFile(os.path.dirname(os.path.abspath(self.current_file)) + os.sep))

    def _postprocess_html(self, html, zoom):
        sizes = [32, 24, 19, 16, 13, 11]
        margins = [(16, 8), (14, 7), (12, 6), (10, 5), (8, 4), (6, 3)]

        def heading_open(match):
            level = int(match.group(1))
            size = int(round(sizes[level - 1] * zoom))
            top, bottom = margins[level - 1]
            return ('<p style="font-size:%dpx;font-weight:bold;'
                    'margin-top:%dpx;margin-bottom:%dpx">'
                    % (size, int(round(top * zoom)), int(round(bottom * zoom))))

        html = re.sub(r"<h([1-6])>", heading_open, html)
        html = re.sub(r"</h[1-6]>", "</p>", html)
        return self._scale_images(html, zoom)

    def _scale_images(self, html, zoom):
        if zoom == 1.0:
            return html

        def repl(match):
            if "width=" in match.group(0) or "height=" in match.group(0):
                return match.group(0)
            head, src, rest, slash = match.groups()
            path = None
            if src.startswith("file:///"):
                path = QUrl(src).toLocalFile()
            elif not src.startswith(("http://", "https://", "data:")):
                base = (os.path.dirname(os.path.abspath(self.current_file))
                        if self.current_file else ".")
                path = os.path.join(base, src)
            if not path or not os.path.isfile(path):
                return match.group(0)
            size = QImageReader(path).size()
            if not size.isValid():
                return match.group(0)
            w = max(1, round(size.width() * zoom))
            h = max(1, round(size.height() * zoom))
            return '%s%s width="%d" height="%d"%s>' % (head, rest, w, h, slash)

        return re.sub(r'(<img[^>]*?src="([^"]+)")([^>]*?)(/?)>', repl, html)

    def zoom_preview(self, up):
        old = self.preview_zoom
        new = old * (1.1 if up else 1 / 1.1)
        self.preview_zoom = max(0.5, min(3.0, new))
        if abs(self.preview_zoom - old) < 1e-9:
            return
        bar = self.preview.verticalScrollBar()
        pos = bar.value()
        self.refresh_preview()
        QTimer.singleShot(0, lambda: bar.setValue(pos))
        self.statusBar().showMessage("预览缩放: %d%%" % round(self.preview_zoom * 100))

    def zoom_in_active(self):
        if self.tabs.currentIndex() == 1:
            self.zoom_preview(True)
        else:
            self.editor.zoom_in()

    def zoom_out_active(self):
        if self.tabs.currentIndex() == 1:
            self.zoom_preview(False)
        else:
            self.editor.zoom_out()

    def zoom_reset(self):
        if self.tabs.currentIndex() == 1:
            self.preview_zoom = 1.0
            self.refresh_preview()
            self.statusBar().showMessage("预览缩放: 100%")
        else:
            font = QFont("Consolas")
            font.setStyleHint(QFont.Monospace)
            font.setPointSize(13)
            self.editor.setFont(font)

    def wrap_selection(self, token):
        cursor = self.editor.textCursor()
        text = cursor.selectedText()
        if not text:
            text = "文字"
        cursor.insertText(token + text + token)
        cursor.setPosition(cursor.position() - len(token))
        if not cursor.selectedText():
            self.editor.setTextCursor(cursor)

    def find_text(self):
        keyword, ok = QInputDialog.getText(self, "查找", "输入要查找的内容:")
        if not ok or not keyword:
            return
        found = self.editor.find(keyword)
        if not found:
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(keyword)
        self.statusBar().showMessage(
            "已找到: %s" % keyword if found else "未找到: %s" % keyword)

    # ---------- 文件操作 ----------
    def maybe_discard(self):
        if not self.is_dirty():
            return True
        ret = QMessageBox.question(
            self, APP_NAME, "当前文件有未保存的修改,是否放弃修改?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            return True
        if ret == QMessageBox.No:
            return self.save_file()
        return False

    def new_file(self):
        if not self.maybe_discard():
            return
        self.current_file = None
        self.saved_text = ""
        self.editor.clear()
        self.refresh_preview()
        self.statusBar().showMessage("已新建文件")

    @staticmethod
    def _read_text(path):
        raw = open(path, "rb").read()
        for enc in ("utf-8-sig", "utf-8", "gbk"):
            try:
                return raw.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return raw.decode("utf-8", errors="replace")

    def open_file(self, path=None):
        if not self.maybe_discard():
            return
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, "打开文件", "", FILE_FILTER)
        if not path:
            return
        try:
            text = self._read_text(path)
        except OSError as e:
            QMessageBox.critical(self, APP_NAME, "无法打开文件:\n%s" % e)
            return
        self.current_file = path
        self.saved_text = text
        self.editor.setPlainText(text)
        self.editor.moveCursor(self.editor.textCursor().Start)
        self.refresh_preview()
        self.on_text_changed()
        self.statusBar().showMessage("已打开: %s" % path)

    def save_file(self):
        if self.current_file:
            return self._write_file(self.current_file)
        return self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", self.current_file or "未命名.md", FILE_FILTER)
        if not path:
            return False
        return self._write_file(path)

    def _write_file(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
        except OSError as e:
            QMessageBox.critical(self, APP_NAME, "无法保存文件:\n%s" % e)
            return False
        self.current_file = path
        self.saved_text = self.editor.toPlainText()
        self.on_text_changed()
        self.statusBar().showMessage("已保存: %s" % path)
        return True

    # ---------- 拖放与关闭 ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and os.path.isfile(path):
                self.open_file(path)
                break

    def closeEvent(self, event):
        if self.maybe_discard():
            event.accept()
        else:
            event.ignore()

    def show_about(self):
        QMessageBox.about(
            self, "关于 %s" % APP_NAME,
            "<h3>%s v%s</h3>"
            "<p>一款简洁的 Markdown 编辑器,支持语法高亮编辑与实时预览。</p>"
            "<p>快捷键: Ctrl+N 新建 | Ctrl+O 打开 | Ctrl+S 保存 | "
            "Ctrl+B/I 加粗/斜体 | F5 刷新预览 | Ctrl+滚轮 缩放字体/预览 | "
            "Ctrl+Shift+D 切换主题</p>"
            % (APP_NAME, APP_VERSION))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        window.open_file(sys.argv[1])
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
