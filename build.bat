@echo off
chcp 65001 >nul
echo 正在打包 MK编辑器(非压缩方式)...
pyinstaller --noconsole --name=MKEditor --icon=icon.ico --add-data "icon.ico;." --clean -y markdown_editor.py
if %errorlevel%==0 (
    echo.
    echo 打包完成!程序位于 dist\MKEditor\MKEditor.exe
) else (
    echo.
    echo 打包失败,请检查上方错误信息。
)
pause
