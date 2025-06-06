🏭 Smart MES-ERP System V0.6
<div align="center">
  <img src="https://img.shields.io/badge/version-0.6.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/tests-312%20passed-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-92%25-brightgreen.svg" alt="Coverage">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>
<div align="center">
  <h3>🚀 코드 없이 커스터마이징 가능한 스마트 생산관리 시스템</h3>
  <p>MES에서 시작해 ERP로 확장 가능한 모듈식 통합 플랫폼</p>
  <p><strong>🎉 영업관리 모듈 출시! 견적에서 수주까지 원스톱 관리!</strong></p>
</div>
📋 목차

소개
V0.6 새로운 기능
시작하기
주요 기능
시스템 요구사항
프로젝트 구조
개발 로드맵
기여하기
라이선스

🆕 V0.6 새로운 기능
✨ 주요 업데이트
1. 영업관리 모듈 완성 ✅

견적 관리: 견적서 작성/수정/복사, PDF 출력
수주 관리: 견적→수주 전환, 수주 상태 추적
고객 관리(CRM): 고객 정보, 거래 이력, 등급 관리
출하/배송: 출하 지시, 배송 추적, 반품 처리
영업 분석: 매출 분석, 고객별 수익성, 제품별 판매 추이

2. 시스템 통합 강화 🔗

MES-영업 연계: 수주→생산계획 자동 연계
재고-영업 연계: 실시간 재고 확인, ATP 관리
구매-영업 연계: 수주 기반 자동 소요량 계산
통합 대시보드: 전사 KPI 한눈에 확인

3. UI/UX 개선 🎨

다크 모드: 눈의 피로 감소
모바일 최적화: 태블릿/스마트폰 완벽 지원
대시보드 커스터마이징: 위젯 드래그&드롭
실시간 알림: 웹 푸시 알림 지원

4. 성능 최적화 ⚡

데이터베이스 마이그레이션: SQLite → PostgreSQL 옵션
캐싱 적용: Redis 캐싱으로 50% 속도 향상
비동기 처리: 대량 데이터 처리 최적화
API 성능: RESTful API 응답속도 개선

📊 시스템 상태

구현 완료: MES ✅ | 재고관리 ✅ | 구매관리 ✅ | 영업관리 ✅
개발 중: 회계관리 🚧 (15%)
개발 예정: 인사관리 📅 | 품질관리 📅
코드 품질: Coverage 92% | Complexity 7.8 | Bugs 0

🚀 시작하기
📥 설치 방법 (개선됨!)

원클릭 설치 (Windows)

powershell# PowerShell 관리자 권한으로 실행
irm https://smart-mes-erp.com/install.ps1 | iex

Docker 설치 (권장)

bashdocker run -d -p 8050:8050 smartmes/erp:v0.6

수동 설치

bashgit clone https://github.com/yourusername/smart-mes-erp.git
cd smart-mes-erp
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
🌐 접속하기

URL: http://localhost:8050
기본 계정: admin / admin123
데모 사이트: https://demo.smart-mes-erp.com

🎨 주요 기능
📊 통합 대시보드 (신규)

실시간 KPI: 생산량, 매출, 재고, 품질 지표
AI 예측: 수요 예측, 생산 계획 제안
이상 감지: 실시간 알림 및 대응 가이드
맞춤형 위젯: 드래그&드롭으로 대시보드 구성

💼 영업관리 (V0.6 신규)
견적 관리:

제품 카탈로그 연동
자동 가격 계산
견적서 템플릿 관리
이메일 발송 통합

수주 관리:

견적→수주 원클릭 전환
수주 상태 실시간 추적
생산/재고 연계 확인
납기 자동 계산

고객 관리(CRM):

360도 고객 뷰
거래 이력 추적
고객 등급 자동 관리
마케팅 캠페인 연동

🏭 MES (제조실행시스템)

작업 관리: QR/바코드 스캔 지원
실시간 모니터링: 안돈 시스템 연동
품질 관리: SPC 차트, 불량 추적
설비 관리: OEE 분석, 예방보전

📦 재고관리

스마트 재고: AI 기반 발주점 제안
위치 관리: 창고별/랙별 관리
RFID 지원: 실시간 재고 추적
재고 최적화: ABC/XYZ 분석

🛒 구매관리

전자구매: EDI 연동
공급망 관리: 리드타임 최적화
가격 관리: 자동 가격 비교
성과 평가: 공급업체 스코어카드

🏗️ 프로젝트 구조
smart-mes-erp/
├── 📄 app.py                    # 메인 애플리케이션
├── 📄 requirements.txt          # Python 패키지
├── 📄 docker-compose.yml        # Docker 설정 (신규)
├── 📄 .env.example             # 환경변수 예제 (신규)
│
├── 📁 modules/                 # 비즈니스 모듈
│   ├── 📁 mes/                # MES 모듈 ✅
│   ├── 📁 inventory/          # 재고관리 모듈 ✅
│   ├── 📁 purchase/           # 구매관리 모듈 ✅
│   └── 📁 sales/              # 영업관리 모듈 ✅ (V0.6)
│       ├── __init__.py
│       ├── layouts.py         # UI 레이아웃
│       ├── callbacks.py       # 이벤트 핸들러
│       └── services.py        # 비즈니스 로직 (신규)
│
├── 📁 api/                     # RESTful API (신규)
│   ├── __init__.py
│   └── v1/
│       ├── auth.py
│       └── endpoints.py
│
├── 📁 tests/                   # 테스트 코드
│   ├── unit/                  # 단위 테스트
│   ├── integration/           # 통합 테스트
│   └── e2e/                   # E2E 테스트 (신규)
│
└── 📁 docs/                    # 문서
    ├── api/                   # API 문서 (신규)
    ├── user-guide/            # 사용자 가이드
    └── developer/             # 개발자 가이드
📈 개발 로드맵
✅ 완료된 버전

V0.1~0.5: 기초 시스템 → 구매관리
V0.6: 영업관리 + 시스템 통합 (현재)

🚧 개발 중
V0.7 - 회계관리 (2024 Q4)

매출/매입 관리
재무제표 자동 생성
원가 계산
예산 관리
세무 신고 연동

📅 개발 예정
V0.8 - 품질관리 (2025 Q1)

수입검사/공정검사/출하검사
SPC(통계적 공정 관리)
품질 코스트 분석
ISO 9001 지원

V0.9 - 인사관리 (2025 Q2)

근태 관리
급여 계산
성과 평가
교육 관리

V1.0 - 정식 출시 (2025 Q3)

엔터프라이즈 기능
클라우드 SaaS
24/7 기술 지원
다국어 지원 (10개 언어)

🧪 테스트
bash# 전체 테스트
pytest

# 커버리지 리포트
pytest --cov=./ --cov-report=html

# E2E 테스트 (신규)
pytest tests/e2e --headed
테스트 커버리지

전체: 92% (+3%)
영업관리: 88% (신규)
API: 95% (신규)
E2E: 82% (신규)

🤝 기여하기
기여 방법

Fork & Clone
Feature Branch 생성
코드 작성 & 테스트
Pull Request

코드 스타일

Black formatter 사용
Type hints 필수
Docstring (Google style)
테스트 커버리지 90% 이상

📞 지원

📧 이메일: support@smartmes.com
💬 디스코드: 커뮤니티 서버
📘 문서: docs.smart-mes-erp.com
🎥 YouTube: 튜토리얼 채널
🆘 원격 지원: TeamViewer/AnyDesk

📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.
<div align="center">
  <p>Made with ❤️ by Smart Manufacturing Team</p>
  <p>© 2024 Smart MES-ERP. All rights reserved.</p>
  <br>
  <p><b>Version 0.6.0</b> - Sales Management & System Integration!</p>
</div>
