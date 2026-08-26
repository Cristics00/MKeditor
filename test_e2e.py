# -*- coding: utf-8 -*-
"""端到端测试: 真实启动应用, 验证 WebEngine 中 KaTeX 实际渲染"""
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication
from markdown_editor import (MainWindow, WEBENGINE_AVAILABLE, _ExternalLinkPage,
                             configure_webengine)

assert WEBENGINE_AVAILABLE, "WebEngine 不可用"


class DebugPage(_ExternalLinkPage):
    def javaScriptConsoleMessage(self, level, msg, line, src):
        print("JS[%d] %s:%d %s" % (level, src, line, msg))

configure_webengine()
app = QApplication(sys.argv)
win = MainWindow()
win.preview.setPage(DebugPage(win.preview))
win.editor.setPlainText(
    "# 测试\n\n行内 $E = mc^2$ 公式。\n\n$$\n\\frac{a}{b} + \\sqrt{x}\n$$\n")
win.tabs.setCurrentIndex(1)  # 切到预览, 触发刷新
win.show()
win.resize(600, 400)


def check():
    def on_result(info):
        print("页面元素统计:", info)
        if info.get("katex") == 2:
            print("E2E TEST PASSED")
            QApplication.exit(0)
        else:
            print("E2E TEST FAILED")
            QApplication.exit(1)

    win.preview.page().runJavaScript(
        "({katex: document.querySelectorAll('.katex').length,"
        " inline: document.querySelectorAll('.math-inline').length,"
        " display: document.querySelectorAll('.math-display').length,"
        " fonts: document.fonts.size,"
        " hasKatex: typeof katex !== 'undefined'})", on_result)


# 等页面加载完成后检查; 10 秒超时兜底
def on_load(ok):
    print("loadFinished:", ok)
    QTimer.singleShot(500, check)


win.preview.loadFinished.connect(on_load)
win.preview.renderProcessTerminated.connect(
    lambda status, code: print("renderProcessTerminated:", status, code))
QTimer.singleShot(10000, lambda: (print("TIMEOUT"), QApplication.exit(2)))
sys.exit(app.exec_())
