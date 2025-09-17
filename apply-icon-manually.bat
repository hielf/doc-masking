@echo off
echo Applying icon to Doc Masking.exe...
echo.

REM Check if rcedit is available
where rcedit >nul 2>nul
if %errorlevel% neq 0 (
    echo rcedit not found. Please install it first:
    echo npm install -g rcedit
    pause
    exit /b 1
)

REM Apply the icon
rcedit "Doc Masking.exe" --set-icon "icon.ico"

if %errorlevel% equ 0 (
    echo Icon applied successfully!
) else (
    echo Failed to apply icon.
)

pause
