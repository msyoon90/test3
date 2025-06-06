# 🏭 Smart MES-ERP System V0.2

<div align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🚀 코드 없이 커스터마이징 가능한 스마트 생산관리 시스템</h3>
  <p>MES에서 시작해 ERP로 확장 가능한 모듈식 통합 플랫폼</p>
</div>

---

## 📋 목차

- [소개](#-소개)
- [V0.2 새로운 기능](#-v02-새로운-기능)
- [필수 코딩 규칙](#-필수-코딩-규칙-중요)
- [시작하기](#-시작하기)
- [문제 해결](#-문제-해결)
- [프로젝트 구조](#-프로젝트-구조)
- [개발 로드맵](#-개발-로드맵)
- [기여하기](#-기여하기)

---

## 🎯 소개

Smart MES-ERP는 제조업을 위한 통합 생산관리 시스템입니다. 복잡한 코드 수정 없이 UI에서 모든 것을 설정할 수 있어, 각 회사의 특성에 맞게 쉽게 커스터마이징할 수 있습니다.

### 💡 핵심 특징

- 🔧 **노코드 커스터마이징**: 모든 설정을 UI에서 변경
- 📊 **실시간 모니터링**: 2초마다 자동 업데이트
- 🏗️ **모듈식 설계**: 필요한 기능만 ON/OFF
- 📱 **반응형 디자인**: PC, 태블릿, 모바일 완벽 지원
- 🐛 **스마트 디버깅**: 에러 자동 감지 및 해결 제안

---

## 🆕 V0.2 새로운 기능

### ✨ 주요 업데이트
- **재고관리 모듈** (개발 중)
  - 품목 마스터 관리
  - 입출고 처리
  - 재고 현황 대시보드
  - 안전재고 알림

- **시스템 개선**
  - Excel 업로드/다운로드 기능
  - 향상된 데이터 검증
  - 디버깅 도구 내장
  - 오류 자동 해결 스크립트

### 🔄 변경 사항
- 코드 작성 가이드라인 강화
- 폴더별 디버깅 솔루션 추가
- 확장된 로드맵 (v1.0까지)
- 향상된 시스템 아키텍처

---

## ⚠️ 필수 코딩 규칙 (중요!)

### 1️⃣ 풀 코드 작성 원칙
```python
# ❌ 잘못된 예시 - 절대 금지!
def some_function():
    # ... existing code ...
    pass

# ✅ 올바른 예시 - 전체 코드 제공
def some_function():
    """완전한 함수 구현"""
    result = calculate_value()
    return result
```

### 2️⃣ 파일 경로 명시
```python
# File: /modules/mes/layouts.py
# 모든 코드 파일 상단에 정확한 경로 명시

import dash
from dash import dcc, html
# ... 전체 코드 ...
```

### 3️⃣ 오류 보고 형식
```
파일: /app.py
줄번호: 125
오류: ImportError: No module named 'dash_bootstrap_components'
전체 오류 메시지: [전체 traceback]
```

---

## 🚀 시작하기

### 📋 필요 사항
- Python 3.8 이상
- 웹 브라우저 (Chrome, Firefox, Safari, Edge)

### 📥 설치 방법

#### 1. 저장소 클론
```bash
git clone https://github.com/msyoon90/my-mes-dashboardv0.1.git
cd my-mes-dashboardv0.1
```

#### 2. 가상환경 설정 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

#### 4. 초기 설정 검증
```bash
# 시스템 상태 점검
python debug_all.py
```

#### 5. 시스템 실행
```bash
python app.py
```

### 🌐 접속하기
- URL: http://localhost:8050
- 기본 계정: admin / admin123
- 게스트 접속: 로그인 화면에서 "게스트 접속" 버튼

---

## 🔧 문제 해결

### 🐛 자동 디버깅 도구

#### 전체 시스템 점검
```bash
python debug_all.py
```

#### 개별 문제 해결
```bash
python debug_modules.py    # 모듈 임포트 문제
python debug_database.py   # 데이터베이스 문제
python debug_assets.py     # 정적 파일 문제
```

### ❓ 자주 발생하는 문제

<details>
<summary><b>ModuleNotFoundError: No module named 'dash_bootstrap_components'</b></summary>

```bash
# 해결 방법
pip install dash-bootstrap-components
# 또는
pip install -r requirements.txt
```
</details>

<details>
<summary><b>FileNotFoundError: [Errno 2] No such file or directory: 'logs/app.log'</b></summary>

```bash
# 해결 방법
mkdir logs data backups
# 또는
python -c "import os; os.makedirs('logs', exist_ok=True); os.makedirs('data', exist_ok=True); os.makedirs('backups', exist_ok=True)"
```
</details>

<details>
<summary><b>데이터베이스 오류</b></summary>

```bash
# 해결 방법
python debug_database.py
# 데이터베이스 재초기화가 필요한 경우
python -c "from app import init_database; init_database()"
```
</details>

---

## 🏗️ 프로젝트 구조

```
my-mes-dashboardv0.1/
├── 📄 app.py                    # 메인 애플리케이션
├── 📄 requirements.txt          # Python 패키지 목록
├── 📄 config.yaml              # 시스템 설정
├── 📄 run.sh / run.bat         # 실행 스크립트
│
├── 📁 assets/                  # 정적 파일
│   └── style.css              # 커스텀 스타일시트
│
├── 📁 modules/                 # 비즈니스 모듈
│   ├── __init__.py
│   └── 📁 mes/                # MES 모듈
│       ├── __init__.py
│       ├── layouts.py         # UI 레이아웃
│       └── callbacks.py       # 이벤트 핸들러
│
├── 📁 core/                    # 핵심 시스템
│   ├── __init__.py
│   ├── logger.py              # 로깅 시스템
│   ├── database.py            # DB 관리
│   └── auth.py                # 인증 시스템
│
├── 📁 data/                    # 데이터 저장
│   └── database.db            # SQLite DB
│
├── 📁 logs/                    # 로그 파일
├── 📁 backups/                 # 백업 파일
│
├── 📁 docs/                    # 문서
│   ├── MES-ERP_Mockup V0.2.md
│   └── README V0.2.md
│
└── 🔧 디버깅 스크립트
    ├── debug_all.py           # 통합 점검
    ├── debug_modules.py       # 모듈 점검
    ├── debug_database.py      # DB 점검
    └── debug_assets.py        # 정적 파일 점검
```

---

## 📈 개발 로드맵

### ✅ V0.1 (완료)
- [x] MES 기본 기능
- [x] 사용자 인증
- [x] 실시간 모니터링
- [x] UI 커스터마이징

### 🚧 V0.2 (현재)
- [ ] 재고관리 모듈
- [ ] Excel 업로드/다운로드
- [ ] 바코드/QR 코드 지원
- [ ] 다국어 지원 (한/영)

### 📅 V0.3 (2024 Q2)
- [ ] 구매관리 모듈
- [ ] PostgreSQL 지원
- [ ] Docker 컨테이너화
- [ ] Redis 캐싱

### 📅 V0.4 (2024 Q3)
- [ ] 영업관리 모듈
- [ ] RESTful API
- [ ] 모바일 앱 (PWA)
- [ ] 외부 시스템 연동

### 📅 V0.5 (2024 Q4)
- [ ] 회계관리 모듈
- [ ] AI 수요 예측
- [ ] 고급 분석 대시보드
- [ ] 자동화 워크플로우

### 🎯 V1.0 (2025 Q1)
- [ ] 엔터프라이즈 기능
- [ ] 클라우드 SaaS 버전
- [ ] 고급 보안 기능
- [ ] 24/7 기술 지원

---

## 👥 기여하기

### 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📝 코드 기여 규칙
- 모든 코드는 **전체 내용** 포함
- 파일 경로 명시 필수
- 주석과 docstring 포함
- 테스트 코드 작성 권장

### 🐛 버그 리포트
이슈 등록 시 다음 정보 포함:
- 시스템 환경 (OS, Python 버전)
- 전체 오류 메시지
- 재현 단계
- 예상 동작 vs 실제 동작

---

## 📞 지원

- 📧 이메일: support@smartmes.com
- 📘 위키: [GitHub Wiki](https://github.com/msyoon90/my-mes-dashboardv0.1/wiki)
- 💬 디스코드: [커뮤니티 서버](https://discord.gg/smartmes)
- 🐛 이슈: [GitHub Issues](https://github.com/msyoon90/my-mes-dashboardv0.1/issues)

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">
  <p>Made with ❤️ by Smart Manufacturing Team</p>
  <p>© 2024 Smart MES-ERP. All rights reserved.</p>
  <br>
  <p><b>Version 0.2.0</b> - Enhanced with debugging tools and inventory management</p>
</div>
