# --- Windows용 run.bat ---
: '
@echo off
echo 🚀 Smart MES-ERP 시스템을 시작합니다...

:: Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

:: 가상환경 확인 및 활성화
if exist venv\ (
    echo ✅ 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo 📦 가상환경을 생성합니다...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo 📥 필요한 패키지를 설치합니다...
    pip install -r requirements.txt
)

:: 디렉토리 생성
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups

:: 애플리케이션 실행
echo 🌐 브라우저에서 http://localhost:8050 으로 접속하세요.
echo 종료하려면 Ctrl+C를 누르세요.
python app.py
pause
'
