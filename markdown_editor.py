import os
import re
import sys

import markdown
from PyQt5.QtCore import QRegExp, Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import (QColor, QFont, QIcon, QImageReader, QKeySequence,
                         QSyntaxHighlighter, QTextCharFormat)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QInputDialog,
                             QMainWindow, QMessageBox, QPlainTextEdit, QStyle,
                             QTabWidget, QTextBrowser, QToolBar)

APP_NAME = "MK编辑器"
APP_VERSION = "1.0.0"
FILE_FILTER = "Markdown 文件 (*.md *.markdown);;文本文件 (*.txt);;所有文件 (*.*)"

EDIT_STYLESHEET = """
QPlainTextEdit {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    background-color: #fdfdfd;
    color: #24292e;
    selection-background-color: #b3d7ff;
    border: none;
}
"""

def build_preview_css(zoom):
    body = int(round(17 * zoom))
    return """
body {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: %dpx;
    color: #24292e;
    line-height: 1.6;
    margin: 12px;
}
code {
    font-family: "Consolas", "Courier New", monospace;
    background-color: #f6f8fa;
    padding: .15em .4em;
    border-radius: 4px;
    font-size: 0.9em;
}
pre {
    background-color: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 12px;
    overflow-x: auto;
}
pre code { background: none; padding: 0; border: none; }
blockquote {
    border-left: 4px solid #dfe2e5;
    color: #6a737d;
    margin: 0;
    padding: 0 1em;
}
table { border-collapse: collapse; }
th, td { border: 1px solid #dfe2e5; padding: 6px 13px; }
th { background-color: #f6f8fa; }
img { max-width: 100%%; }
hr { border: none; border-top: 2px solid #eaecef; }
a { color: #0366d6; text-decoration: none; }
""" % body


def resource_path(relative):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        self.fmt_code = QTextCharFormat()
        self.fmt_code.setForeground(QColor("#d73a49"))
        self.init_rules()

    def _fmt(self, color, bold=False, italic=False):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def init_rules(self):
        self.rules = [
            (QRegExp(r"^#{1,6}\s.*$"), self._fmt("#0366d6", bold=True)),
            (QRegExp(r"\*\*[^*\n]+\*\*"), self._fmt("#6f42c1", bold=True)),
            (QRegExp(r"__[^_\n]+__"), self._fmt("#6f42c1", bold=True)),
            (QRegExp(r"(?<!\*)\*[^*\n]+\*(?!\*)"), self._fmt("#e36209", italic=True)),
            (QRegExp(r"(?<!_)_[^_\n]+_(?!_)"), self._fmt("#e36209", italic=True)),
            (QRegExp(r"`[^`\n]+`"), self._fmt("#d73a49")),
            (QRegExp(r"\[[^\]]+\]\([^)\s]+\)"), self._fmt("#0366d6")),
            (QRegExp(r"^\s*(?:[-*+]|\d+\.)\s+"), self._fmt("#e36209")),
            (QRegExp(r"^\s*>.*$"), self._fmt("#6a737d", italic=True)),
            (QRegExp(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$"), self._fmt("#d1d5da")),
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


class EditorPane(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(13)
        self.setFont(font)
        self.highlighter = MarkdownHighlighter(self.document())

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
        self.setOpenExternalLinks(True)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            self.ctrl_wheel.emit(event.angleDelta().y() > 0)
            event.accept()
            return
        super().wheelEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.saved_text = ""
        self.setWindowTitle(APP_NAME)
        self.resize(1024, 720)

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.editor = EditorPane()
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
        self.refresh_preview()

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
        self.act_refresh = QAction("刷新预览", self)
        self.act_bold = QAction("加粗", self)
        self.act_italic = QAction("斜体", self)
        self.act_zoom_in = QAction("放大字体", self)
        self.act_zoom_out = QAction("缩小字体", self)
        self.act_zoom_reset = QAction("恢复默认字号", self)
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
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_open)
        menu_file.addSeparator()
        menu_file.addAction(self.act_save)
        menu_file.addAction(self.act_save_as)
        menu_file.addSeparator()
        menu_file.addAction(self.act_exit)

        menu_edit = self.menuBar().addMenu("编辑(&E)")
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
        menu_view.addAction(self.act_refresh)
        menu_view.addSeparator()
        menu_view.addAction(self.act_zoom_in)
        menu_view.addAction(self.act_zoom_out)
        menu_view.addAction(self.act_zoom_reset)

        menu_help = self.menuBar().addMenu("帮助(&H)")
        menu_help.addAction(self.act_about)

    def _build_toolbar(self):
        toolbar = QToolBar("工具栏", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
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
            "<body>%s</body></html>" % (build_preview_css(self.preview_zoom), html))
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
            "Ctrl+B/I 加粗/斜体 | F5 刷新预览 | Ctrl+滚轮 缩放字体/预览</p>"
            % (APP_NAME, APP_VERSION))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        window.open_file(sys.argv[1])
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
