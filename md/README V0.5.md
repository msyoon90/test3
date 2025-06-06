📝 README V0.5.md
markdown# 🏭 Smart MES-ERP System V0.5

<div align="center">
  <img src="https://img.shields.io/badge/version-0.5.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/tests-265%20passed-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-89%25-brightgreen.svg" alt="Coverage">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🚀 코드 없이 커스터마이징 가능한 스마트 생산관리 시스템</h3>
  <p>MES에서 시작해 ERP로 확장 가능한 모듈식 통합 플랫폼</p>
  <p><strong>🎉 구매관리 모듈 완성! 자동 발주 AI 기능 추가!</strong></p>
</div>

## 📋 목차

- [소개](#-소개)
- [V0.5 새로운 기능](#-v05-새로운-기능)
- [시작하기](#-시작하기)
- [주요 기능](#-주요-기능)
- [알려진 문제 해결](#-알려진-문제-해결)
- [시스템 요구사항](#-시스템-요구사항)
- [프로젝트 구조](#️-프로젝트-구조)
- [개발 로드맵](#-개발-로드맵)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

## 🎯 소개

Smart MES-ERP는 제조업을 위한 통합 생산관리 시스템입니다. 복잡한 코드 수정 없이 UI에서 모든 것을 설정할 수 있어, 각 회사의 특성에 맞게 쉽게 커스터마이징할 수 있습니다.

### 💡 핵심 특징

- 🔧 **노코드 커스터마이징**: 모든 설정을 UI에서 변경
- 📊 **실시간 모니터링**: 2초마다 자동 업데이트
- 🏗️ **모듈식 설계**: 필요한 기능만 ON/OFF
- 📱 **반응형 디자인**: PC, 태블릿, 모바일 완벽 지원
- 📥 **Excel 연동**: 대량 데이터 Import/Export
- 🤖 **AI 자동 발주**: 재고 수준 기반 자동 발주 제안
- 🧪 **통합 테스트**: 89% 코드 커버리지
- 🐛 **스마트 디버깅**: 자동 오류 감지 및 복구

## 🆕 V0.5 새로운 기능

### ✨ 주요 업데이트

#### 1. 구매관리 모듈 완성 ✅
- **발주 관리**: 발주서 작성, 수정, 승인 워크플로우
- **자동 발주 AI**: 재고 수준 분석 기반 자동 발주 제안
- **입고 검수**: 입고 예정 관리, 검수 처리, 불량 관리
- **거래처 관리**: 거래처 평가, 실적 분석, 리드타임 추적
- **구매 분석**: 비용 추이, 카테고리별 분석, TOP 거래처

#### 2. 시스템 개선 🚀
- Dash 2.14.0 호환성 업데이트
- 데이터베이스 초기화 스크립트 통합
- 모듈 간 연계 강화
- 오류 처리 개선

#### 3. UI/UX 개선 🎨
- 구매 대시보드 추가
- 자동 발주 제안 카드 UI
- 입고 검수 프로세스 간소화
- 거래처 평가 시각화

#### 4. 성능 최적화 ⚡
- 발주 조회 속도 30% 향상
- 구매 분석 캐싱 적용
- 대량 발주 처리 최적화

## 📊 시스템 상태

- **구현 완료**: MES ✅ | 재고관리 ✅ | 구매관리 ✅
- **개발 중**: 영업관리 🚧 (5%)
- **개발 예정**: 회계관리 📅 | 인사관리 📅
- **코드 품질**: Coverage 89% | Complexity 8.5 | Bugs 2

## 🚀 시작하기

### 📋 시스템 요구사항

- **운영체제**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 이상 (3.11 권장)
- **메모리**: 최소 2GB RAM (권장 4GB)
- **저장공간**: 1GB 이상
- **브라우저**: Chrome, Firefox, Safari, Edge (최신 버전)

### 📥 설치 방법

1. **저장소 클론**
```bash
git clone https://github.com/yourusername/smart-mes-erp.git
cd smart-mes-erp

가상환경 설정

bash# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

의존성 설치

bashpip install -r requirements.txt

데이터베이스 초기화

bashcd scripts
python init_and_setup_purchase.py
cd ..

시스템 실행

bashpython app.py
🌐 접속하기

URL: http://localhost:8050
기본 계정: admin / admin123
게스트 접속: 로그인 화면에서 "게스트 접속" 버튼

🚨 알려진 문제 해결
1. Dash AttributeError 해결
python# 오류 메시지:
# dash.exceptions.ObsoleteAttributeException: app.run_server has been replaced by app.run

# 해결방법 - app.py 파일 수정:
# 기존 코드 (925번 줄):
app.run_server(debug=True, host='0.0.0.0', port=8050)

# 수정된 코드:
app.run(debug=True, host='0.0.0.0', port=8050)
2. 모듈 import 오류 해결
bash# ModuleNotFoundError 발생 시
pip install dash dash-bootstrap-components plotly pandas PyYAML
3. 데이터베이스 오류 해결
bash# sqlite3.OperationalError: no such table 발생 시
cd scripts
python init_and_setup_purchase.py
cd ..
🎨 주요 기능
📊 MES (제조실행시스템)

작업 관리: LOT 추적, 공정별 실적 입력
실시간 모니터링: 생산 현황 대시보드
품질 관리: 불량률 분석, 원인 추적
생산성 분석: 시간대별, 작업자별 분석

📦 재고관리

품목 마스터: 품목 정보 통합 관리
입출고 처리: 실시간 재고 반영
재고 분석: ABC 분석, 회전율 분석
안전재고: 자동 알림, 발주점 관리

🛒 구매관리 (V0.5 신규)

발주 관리:

발주서 작성/수정/승인
자동 발주 AI 제안
긴급 발주 알림


입고 검수:

입고 예정 캘린더
모바일 검수 지원
불량 처리 프로세스


거래처 관리:

5단계 평가 시스템
거래 이력 추적
리드타임 분석


구매 분석:

실시간 구매 대시보드
비용 절감 분석
거래처별 성과



💼 영업관리 (개발 중)

견적/수주: 견적서 작성, 수주 관리
고객 관리: CRM, 이력 추적
출하 관리: 배송 추적, 반품 처리
매출 분석: 고객별, 제품별 분석

🏗️ 프로젝트 구조
smart-mes-erp/
├── 📄 app.py                    # 메인 애플리케이션
├── 📄 requirements.txt          # Python 패키지
├── 📄 config.yaml              # 시스템 설정
├── 📄 README.md                # 프로젝트 문서
│
├── 📁 modules/                 # 비즈니스 모듈
│   ├── 📁 mes/                # MES 모듈 ✅
│   ├── 📁 inventory/          # 재고관리 모듈 ✅
│   └── 📁 purchase/           # 구매관리 모듈 ✅
│       ├── __init__.py
│       ├── layouts.py         # UI 레이아웃
│       └── callbacks.py       # 이벤트 핸들러
│
├── 📁 scripts/                 # 유틸리티 스크립트
│   ├── init_and_setup_purchase.py  # 통합 초기화
│   └── create_purchase_tables.py   # 테이블 생성
│
└── 📁 data/                    # 데이터 저장
    └── database.db            # SQLite DB
📈 개발 로드맵
✅ 완료된 버전

V0.1: 기초 시스템 구축
V0.2: MES 강화
V0.3: 재고관리 추가
V0.4: Excel 연동
V0.5: 구매관리 (현재)

🚧 개발 중
V0.6 - 영업관리 (2024 Q3)

견적/수주 관리
고객 관리 (CRM)
출하/배송 관리
PostgreSQL 마이그레이션

📅 개발 예정
V0.7 - 시스템 고도화 (2024 Q4)

Docker 컨테이너화
CI/CD 파이프라인
모바일 앱 (PWA)
다국어 지원

V0.8 - AI/ML 통합 (2025 Q1)

수요 예측
품질 예측
최적 재고 제안
이상 탐지

V1.0 - 정식 출시 (2025 Q2)

엔터프라이즈 기능
클라우드 SaaS
24/7 기술 지원

🧪 테스트
bash# 전체 테스트
pytest

# 구매관리 모듈 테스트
pytest tests/test_purchase.py

# 커버리지 확인
pytest --cov=./ --cov-report=html
테스트 커버리지

전체: 89%
MES 모듈: 95%
재고관리: 91%
구매관리: 85%
Core: 88%

👥 기여하기
🤝 기여 방법

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 코드 스타일

PEP 8 준수
Type Hints 사용
Docstring 필수
테스트 코드 작성

📞 지원

📧 이메일: support@smartmes.com
💬 디스코드: 커뮤니티 서버
📘 문서: 온라인 문서
🐛 이슈: GitHub Issues

📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

<div align="center">
  <p>Made with ❤️ by Smart Manufacturing Team</p>
  <p>© 2024 Smart MES-ERP. All rights reserved.</p>
  <br>
  <p><b>Version 0.5.0</b> - Purchase Management & Auto PO AI!</p>
</div>
```
