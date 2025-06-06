README V0.1.md
🏭 Smart MES-ERP System
<div align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>
<div align="center">
  <h3>🚀 코드 없이 커스터마이징 가능한 스마트 생산관리 시스템</h3>
  <p>MES에서 시작해 ERP로 확장 가능한 모듈식 통합 플랫폼</p>
</div>

📋 목차

소개
주요 기능
시작하기
사용 방법
시스템 구조
커스터마이징
문제 해결
라이선스


🎯 소개
Smart MES-ERP는 제조업을 위한 통합 생산관리 시스템입니다. 복잡한 코드 수정 없이 UI에서 모든 것을 설정할 수 있어, 각 회사의 특성에 맞게 쉽게 커스터마이징할 수 있습니다.
💡 핵심 특징

🔧 노코드 커스터마이징: 모든 설정을 UI에서 변경
📊 실시간 모니터링: 2초마다 자동 업데이트
🏗️ 모듈식 설계: 필요한 기능만 ON/OFF
📱 반응형 디자인: PC, 태블릿, 모바일 완벽 지원
🐛 스마트 디버깅: 에러 자동 감지 및 해결 제안


✨ 주요 기능
1️⃣ MES (제조실행시스템)

✅ 작업 입력 및 관리
✅ 실시간 생산 현황 모니터링
✅ LOT 추적 관리
✅ 불량률 분석 및 리포트
✅ 작업자별 실적 관리

2️⃣ 확장 가능한 모듈 (추후 개발)

📦 재고관리
🛒 구매관리
💰 영업관리
📊 회계관리

3️⃣ 시스템 기능

🔐 사용자 인증 (ON/OFF 가능)
⚙️ UI 커스터마이징
💾 자동 백업/복원
📊 데이터 분석 대시보드


🚀 시작하기
📋 필요 사항

Python 3.8 이상
웹 브라우저 (Chrome, Firefox, Safari, Edge)

📥 설치 방법
bash# 1. 저장소 클론
git clone https://github.com/yourusername/smart-mes-erp.git
cd smart-mes-erp

# 2. 가상환경 생성 (권장)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. 필요 패키지 설치
pip install -r requirements.txt

# 4. 시스템 실행
python app.py
🌐 접속하기
http://localhost:8050
기본 계정 (로그인 기능 활성화 시):

ID: admin
PW: admin123


📖 사용 방법
1️⃣ 첫 실행
시스템을 처음 실행하면 자동으로:

✅ 데이터베이스 생성
✅ 기본 설정 적용
✅ 샘플 데이터 생성 (선택)

2️⃣ 기본 작업 흐름
1. 작업 입력
   MES → 작업입력 → 정보 입력 → 저장

2. 현황 조회
   MES → 현황조회 → 기간/조건 선택 → 조회

3. 분석/리포트
   MES → 분석 → 리포트 종류 선택 → 생성
3️⃣ 설정 변경
모든 설정은 UI에서 변경 가능:
⚙️ 설정 → 원하는 항목 선택 → 변경 → 저장

🏗️ 시스템 구조
smart-mes-erp/
├── app.py                 # 메인 애플리케이션
├── config.yaml           # 시스템 설정
├── requirements.txt      # 필요 패키지
├── README.md            # 이 문서
│
├── core/                # 핵심 시스템
│   ├── __init__.py
│   ├── logger.py        # 로깅 시스템
│   ├── database.py      # DB 관리
│   └── auth.py          # 인증 시스템
│
├── modules/             # 비즈니스 모듈
│   ├── mes/            # MES 모듈
│   │   ├── __init__.py
│   │   ├── models.py   # 데이터 모델
│   │   ├── layouts.py  # UI 레이아웃
│   │   └── callbacks.py # 이벤트 처리
│   └── ...             # 다른 모듈들
│
├── assets/             # 정적 파일
│   └── style.css      # 스타일시트
│
├── data/              # 데이터 저장
│   └── database.db    # SQLite DB
│
└── logs/              # 로그 파일
    └── app.log       # 애플리케이션 로그

🎨 커스터마이징
1️⃣ UI에서 설정 가능한 항목
📝 입력 폼 커스터마이징

필드 추가/삭제/순서 변경
입력 타입 변경
필수/선택 설정
검증 규칙 추가

🎨 레이아웃 변경

컬럼 수 조정
섹션 구성
색상 테마
폰트 크기

⚙️ 시스템 설정

모듈 ON/OFF
인증 사용 여부
백업 주기
실시간 업데이트 간격

2️⃣ 설정 파일 (config.yaml)
yaml# 시스템 기본 설정
system:
  name: "Smart MES-ERP"
  language: "ko"

# 모듈 활성화
modules:
  mes: true
  inventory: false
  
# 인증 설정
authentication:
  enabled: true
  session_timeout: 30

🔧 문제 해결
❓ 자주 묻는 질문
<details>
<summary><b>Q: 시스템이 시작되지 않아요</b></summary>
A: 다음을 확인해주세요:

Python 3.8 이상 설치 확인
필요 패키지 설치: pip install -r requirements.txt
포트 8050이 사용 중인지 확인

</details>
<details>
<summary><b>Q: 로그인이 안 돼요</b></summary>
A:

기본 계정: admin / admin123
로그인 기능 비활성화: 설정 → 인증 → 로그인 사용 OFF

</details>
<details>
<summary><b>Q: 데이터가 사라졌어요</b></summary>
A:

자동 백업 확인: ./backups/ 폴더
복원: 설정 → 데이터베이스 → 백업 복원

</details>
🐛 디버깅
시스템에 내장된 디버깅 콘솔 사용:

F12 키로 콘솔 열기/닫기
에러 발생 시 자동으로 해결 방법 제시

📞 지원

이슈 등록: GitHub Issues
이메일: support@smartmes.com
문서: Wiki


📈 로드맵
✅ 완료 (v1.0)

MES 기본 기능
UI 커스터마이징
실시간 모니터링
인증 시스템

🚧 진행 중 (v1.1)

재고관리 모듈
모바일 앱
API 개발

📋 계획 (v2.0)

구매관리 모듈
영업관리 모듈
AI 예측 분석
다국어 지원


👥 기여하기
기여를 환영합니다!

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request


📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

🙏 감사의 말

Dash 팀의 훌륭한 프레임워크
모든 오픈소스 기여자들
피드백을 주신 사용자 여러분


<div align="center">
  <p>Made with ❤️ by Smart Manufacturing Team</p>
  <p>© 2024 Smart MES-ERP. All rights reserved.</p>
</div>
