@echo off
cd /d "%~dp0"
REM Build with the project Python that has PyQt5/PyQtWebEngine/PyInstaller installed.
REM MKEditor.spec already includes the icon and assets/katex data directories.
E:\python\python.exe -m PyInstaller MKEditor.spec --clean -y
if %errorlevel%==0 (
    echo Build succeeded. Output: dist\MKEditor\MKEditor.exe
) else (
    echo Build failed. See error messages above.
)
pause
