# -*- coding: utf-8 -*-
"""验证深浅主题下预览背景色与公式渲染"""
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from markdown_editor import (MainWindow, WEBENGINE_AVAILABLE, _ExternalLinkPage,
                             configure_webengine)

assert WEBENGINE_AVAILABLE


class DebugPage(_ExternalLinkPage):
    def javaScriptConsoleMessage(self, level, msg, line, src):
        print("JS[%d] %s:%d %s" % (level, src, line, msg))


configure_webengine()
app = QApplication(sys.argv)
win = MainWindow()
win.preview.setPage(DebugPage(win.preview))
win.editor.setPlainText("行内 $E=mc^2$\n\n$$\\frac{a}{b}$$\n")

results = {}
step = {"i": 0}


def probe(theme_name):
    def on_result(info):
        results[theme_name] = info
        next_step()
    win.preview.page().runJavaScript(
        "({bg: getComputedStyle(document.body).backgroundColor,"
        " color: getComputedStyle(document.body).color,"
        " katex: document.querySelectorAll('.katex').length})", on_result)


def next_step():
    i = step["i"]
    step["i"] += 1
    if i == 0:
        win.tabs.setCurrentIndex(1)  # 触发预览刷新
        win.show()
        QTimer.singleShot(800, lambda: probe("dark"))
    elif i == 1:
        win.dark = 0  # 切浅色
        win.apply_theme()
        QTimer.singleShot(1500, lambda: probe("light"))
    elif i == 2:
        print(results)
        dark, light = results["dark"], results["light"]
        ok = (dark["bg"] == "rgb(13, 17, 23)" and dark["katex"] == 2
              and light["bg"] == "rgb(255, 255, 255)" and light["katex"] == 2)
        print("THEME TEST PASSED" if ok else "THEME TEST FAILED")
        QApplication.exit(0 if ok else 1)


QTimer.singleShot(0, next_step)
QTimer.singleShot(15000, lambda: (print("TIMEOUT"), QApplication.exit(2)))
sys.exit(app.exec_())
