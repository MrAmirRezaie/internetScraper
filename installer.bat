@echo off
:: Obfuscated Installer for Windows

:: Function to check if a command exists
:_a
where %1 >nul 2>&1
if %errorlevel% neq 0 (
    echo %1 not found. Please install %1.
    pause
    exit /b 1
)
goto :_b

:_b
:: Check if Python 3 is installed
call :_a python

:: Check if pip is installed
call :_a pip

:: Set installation directories
set _c="C:\Program Files\internetScraper"
set _d="C:\Program Files\internetScraper\output"

:: Create necessary directories using PowerShell
echo Creating directories...
powershell -Command "if (-not (Test-Path %_c%)) { New-Item -Path %_c% -ItemType Directory }" 2>&1
if %errorlevel% neq 0 (
    echo Failed to create installation directory.
    pause
    exit /b 1
)

powershell -Command "if (-not (Test-Path %_d%)) { New-Item -Path %_d% -ItemType Directory }" 2>&1
if %errorlevel% neq 0 (
    echo Failed to create output directory.
    pause
    exit /b 1
)

:: Copy script files using PowerShell
echo Copying files...
powershell -Command "Copy-Item -Path 'internetScraper.py' -Destination %_c%" 2>&1
if %errorlevel% neq 0 (
    echo Failed to copy internetScraper.py.
    pause
    exit /b 1
)

powershell -Command "Copy-Item -Path '.env' -Destination %_c%" 2>&1
if %errorlevel% neq 0 (
    echo Failed to copy .env file.
    pause
    exit /b 1
)

powershell -Command "Copy-Item -Path 'output\*' -Destination %_d% -Recurse" 2>&1
if %errorlevel% neq 0 (
    echo Failed to copy output directory.
    pause
    exit /b 1
)

:: Install required packages using PowerShell
echo Installing required packages...

:: List of required packages
set _e=(
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

:: Install each package using PowerShell
for %%p in (%_e%) do (
    echo Installing %%p...
    powershell -Command "pip install %%p --user" 2>&1
    if %errorlevel% neq 0 (
        echo Failed to install %%p
        pause
        exit /b 1
    )
)

:: Create a batch file for easy execution (optional)
echo @echo off > "%_c%\internetScraper.bat"
echo python "%_c%\internetScraper.py" %%* >> "%_c%\internetScraper.bat"

:: Add to PATH using PowerShell
echo Adding installation directory to PATH...
powershell -Command "[Environment]::SetEnvironmentVariable('PATH', [Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::Machine) + ';%_c%', [EnvironmentVariableTarget]::Machine)" 2>&1
if %errorlevel% neq 0 (
    echo Failed to add installation directory to PATH.
    pause
    exit /b 1
)

echo Installation completed successfully!
echo You can now run the script using the command 'internetScraper'.
pause