@echo off
setlocal enabledelayedexpansion

echo ============================
echo   Obscure LNG Tool
echo ============================

set FILE=%~1

if "%FILE%"=="" (
    echo.
    echo Drag and drop a .lng file onto this .bat
    echo.
    pause
    exit /b
)

echo File: %FILE%
echo.

echo Choose output format:
echo [1] TXT
echo [2] CSV
echo [3] BOTH
echo.
echo Or type: txt / csv / both
echo.

set /p choice=Option: 

set FORMAT=

REM normalize input (lowercase-ish handling)
for %%A in (%choice%) do set choice=%%A

if "%choice%"=="1" set FORMAT=txt
if "%choice%"=="2" set FORMAT=csv
if "%choice%"=="3" set FORMAT=both

if /I "%choice%"=="txt" set FORMAT=txt
if /I "%choice%"=="csv" set FORMAT=csv
if /I "%choice%"=="both" set FORMAT=both

if "%FORMAT%"=="" (
    echo Invalid option.
    pause
    exit /b
)

echo.
echo Running extraction...
echo Format: %FORMAT%
echo.

python obscure_lng_tool.py extract "%FILE%" --format %FORMAT%

echo.
echo Done!
pause