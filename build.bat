@echo off
echo ================================================
echo            ������������������
echo ================================================
echo.

REM ���Python�Ƿ����
python --version >nul 2>&1
if errorlevel 1 (
    echo ����: δ�ҵ�Python�����Ȱ�װPython
    pause
    exit /b 1
)

echo ��ǰPython�汾:
python --version
echo.

REM �л����ű�Ŀ¼
cd /d "%~dp0"

REM ��鲢��װ����
echo ���������...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ��װ�������...
    pip install pyinstaller
    if errorlevel 1 (
        echo ������װʧ�ܣ�������������
        pause
        exit /b 1
    )
)

echo.
echo ��ʼ���Ӧ�ó���...
echo.

REM ���д���ű�
python build.py

echo.
echo �����ɣ�
echo.
echo ���ɵ��ļ��� dist Ŀ¼�У�
echo - ClipboardManager.exe (������)
echo - ClipboardManager_v1.0_Portable.zip (��Я��)
echo.

pause