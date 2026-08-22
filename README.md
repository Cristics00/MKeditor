[README.md](https://github.com/user-attachments/files/31335696/README.md)
# MK编辑器 (MKeditor)

一款基于 **Python + PyQt5** 开发的简洁 Markdown 编辑器,支持语法高亮编辑、实时预览、深浅主题切换,并可将源码打包为 Windows 可执行程序(exe)。

## 功能特性

- **Markdown 编辑与预览**
  - 「编辑」页签:Markdown 语法高亮(标题、加粗、斜体、行内代码、代码块、链接、列表、引用、分隔线)
  - 「预览」页签:HTML 渲染预览,支持表格、代码块、引用、图片等样式
- **文件操作**
  - 新建 / 打开 / 保存 / 另存为(`.md` / `.markdown` / `.txt`)
  - 支持拖拽文件到窗口直接打开
  - 编码自动识别(UTF-8 / GBK),未保存修改在标题栏以 `*` 标记,关闭时提醒
- **编辑增强**
  - 行号栏与当前行高亮
  - 撤销 / 重做、查找、加粗 / 斜体快捷插入
  - 编辑区 Ctrl+滚轮缩放字体
- **预览缩放**
  - 预览页 Ctrl+滚轮同步缩放正文、标题与图片(50% ~ 300%),状态栏显示百分比
- **界面美化**
  - 浅色(GitHub 风格)/ 深色(GitHub Dark 风格)双主题,一键切换,标题栏配色同步(Windows 10/11)
  - 圆角下拉菜单、图标化工具栏(悬浮提示)、圆角滚动条等细节样式
- **中文界面** + 自定义程序图标(白色圆角方框 + MK)

## 运行方式

### 方式一:直接运行打包好的程序(推荐给普通用户)

进入 `dist/MKEditor/` 文件夹,双击 `MKEditor.exe` 即可(整个文件夹需保持完整,exe 依赖同目录下的 `_internal`)。

### 方式二:运行源码(适合开发调试)

```bash
# 安装依赖
pip install pyqt5 markdown pillow pyinstaller

# 运行
python markdown_editor.py
```

也可以在命令行传入文件路径直接打开:

```bash
python markdown_editor.py 文档.md
```

## 快捷键

| 快捷键 | 功能 |
| --- | --- |
| `Ctrl+N` / `Ctrl+O` / `Ctrl+S` | 新建 / 打开 / 保存 |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+Z` / `Ctrl+Y` | 撤销 / 重做 |
| `Ctrl+F` | 查找 |
| `Ctrl+B` / `Ctrl+I` | 插入加粗 / 斜体标记 |
| `F5` | 刷新预览 |
| `Ctrl+滚轮` | 编辑区:缩放字体;预览区:缩放正文/标题/图片 |
| `Ctrl+=` / `Ctrl+-` / `Ctrl+0` | 放大 / 缩小 / 恢复默认字号(作用于当前页签) |
| `Ctrl+Shift+D` | 切换浅色 / 深色主题 |
| `Ctrl+Q` | 退出 |

## 项目结构

```
MKeditor/
├── markdown_editor.py   # 主程序(全部功能)
├── make_icon.py         # 图标生成脚本(Pillow 绘制 icon.ico)
├── icon.ico             # 程序图标
├── build.bat            # 一键打包脚本
├── MKEditor.spec        # PyInstaller 配置(自动生成)
├── build/               # 打包中间产物(自动生成)
└── dist/
    └── MKEditor/
        └── MKEditor.exe # 打包好的程序(非压缩/onedir 方式)
```

## 打包为 exe

双击 `build.bat`,或手动执行:

```bash
pyinstaller --noconsole --name=MKEditor --icon=icon.ico --add-data "icon.ico;." --clean -y markdown_editor.py
```

打包完成后程序位于 `dist/MKEditor/MKEditor.exe`。

> 采用非压缩(onedir)方式打包:产物结构透明、启动快、便于排查问题;修改源码后重新打包,若依赖未变化,只替换 exe 文件即可更新。

### 重新生成图标

```bash
python make_icon.py
```

## 技术要点

- 界面框架:PyQt5(Fusion 样式 + QSS 主题)
- Markdown 渲染:`markdown` 库(extra、sane_lists 扩展)
- 语法高亮:`QSyntaxHighlighter`,深浅主题两套配色
- 预览缩放:Qt 富文本引擎会忽略 h1-h6 的 CSS 字号且不接受小数 px,故对 HTML 后处理——标题转为带整数 px 内联样式的段落,图片按缩放系数注入 width/height
- 圆角菜单:`WA_TranslucentBackground` + `FramelessWindowHint` + `NoDropShadowWindowHint` 三件套
- 深色标题栏:Windows 下通过 DWM API 实现
