"""验证「打开文件未修改却误报未保存」的修复。

覆盖两个最易触发 bug 的情况:
1. 文件以换行符结尾 (Qt 会剥离末尾换行)
2. 文件使用 \\r\\n 换行 (Qt 会规范化为 \\n)
"""
import os
import sys
import tempfile

from PyQt5.QtWidgets import QApplication

from markdown_editor import MainWindow

app = QApplication(sys.argv)

# 极端的文件内容: 末尾有换行, 中间用 Windows 换行
content = "第一行\r\n第二行\r\n第三行\r\n"
tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md",
                                  encoding="utf-8", delete=False)
tmp.write(content)
tmp.close()
path = tmp.name

win = MainWindow()
win.open_file(path)

dirty_after_open = win.is_dirty()
print("打开后 is_dirty (应为 False):", dirty_after_open)
print("窗口标题:", win.windowTitle())

# 真实编辑应正确标记为已修改
win.editor.insertPlainText("追加的文字")
dirty_after_edit = win.is_dirty()
print("编辑后 is_dirty (应为 True):", dirty_after_edit)

win.close()
os.unlink(path)

ok = (not dirty_after_open) and dirty_after_edit
print("RESULT:", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
