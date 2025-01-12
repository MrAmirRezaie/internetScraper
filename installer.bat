@echo off
:: Installer for Windows

:: Check if Python 3 is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 not found. Please install Python 3.
    pause
    exit /b 1
)

:: Check if pip is installed
where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found. Please install pip.
    pause
    exit /b 1
)

:: Create necessary directories
set INSTALL_DIR="C:\Program Files\internetScraper"
set OUTPUT_DIR="C:\Program Files\internetScraper\output"
mkdir %INSTALL_DIR%
mkdir %OUTPUT_DIR%

:: Copy script files
copy internetScraper.py %INSTALL_DIR%
copy .env %INSTALL_DIR%
xcopy /E /I output %OUTPUT_DIR%

:: Install required packages
echo Installing required packages...

:: List of required packages
set REQUIRED_PACKAGES=(
    selenium
    openpyxl
    numpy
    pandas
    matplotlib
    seaborn
    sqlalchemy
    beautifulsoup4
    nltk
    pycryptodome
    python-dotenv
    Pillow
    requests
    pyTelegramBotAPI
    googletrans==4.0.0-rc1
    cryptography
    tensorflow
)

:: Install each package
for %%p in (%REQUIRED_PACKAGES%) do (
    echo Installing %%p...
    pip install %%p
    if errorlevel 1 (
        echo Failed to install %%p
        pause
        exit /b 1
    )
)

:: Create a batch file for easy execution (optional)
echo @echo off > "%INSTALL_DIR%\internetScraper.bat"
echo python "%INSTALL_DIR%\internetScraper.py" %%* >> "%INSTALL_DIR%\internetScraper.bat"

:: Add to PATH (optional)
setx PATH "%PATH%;%INSTALL_DIR%"

echo Installation completed successfully!
echo You can now run the script using the command 'internetScraper'.
pause