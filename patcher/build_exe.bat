@echo off
setlocal
cd /d "%~dp0"

echo This script builds Outlast-HeadBob-Remover.exe with PyInstaller.
echo The window icon is embedded inside the .exe (no separate .ico needed).
pause

py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

py -3 -m PyInstaller --noconfirm --onefile --windowed ^
    --icon "Outlast-HeadBob-Remover.ico" ^
    --add-data "Outlast-HeadBob-Remover.ico;." ^
    --hidden-import minilzo ^
    --name "Outlast-HeadBob-Remover" ^
    Outlast-HeadBob-Remover.py
if errorlevel 1 goto :error

echo.
echo Done: dist\Outlast-HeadBob-Remover.exe
echo The .exe now carries the window icon; no separate .ico file is required.
pause
goto :end

:error
echo Failed to build the executable.
pause

:end
endlocal
