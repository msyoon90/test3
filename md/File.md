📁 Smart MES-ERP V1.0 파일별 기능 정리
🎯 핵심 파일
app.py (메인 애플리케이션)

시스템 진입점 및 전체 라우팅
네비게이션 바 생성
로그인/로그아웃 기능
대시보드 실시간 업데이트
데이터베이스 초기화 (init_database())
모든 모듈 콜백 등록

config.yaml (시스템 설정)

시스템 버전 관리 (V1.0.0)
모듈 활성화 설정 (5개 모듈 활성)
인증 설정 (세션 타임아웃 30분)
업데이트 주기 설정 (2초)

requirements.txt (의존성 관리)

Dash 2.14.0 기반 웹 프레임워크
Plotly 시각화
Pandas 데이터 처리
기타 필수 패키지

📊 모듈별 기능
1. MES (생산관리) 모듈
modules/mes/
├── layouts.py
│   ├── 작업 입력 폼 (LOT번호, 계획/실적)
│   ├── 생산 현황 조회
│   ├── 생산성 분석 차트
│   └── MES 설정 관리
└── callbacks.py
    ├── 달성률 실시간 계산
    ├── 작업 데이터 저장
    ├── 생산 통계 업데이트
    └── 분석 차트 생성
2. 재고관리 모듈
modules/inventory/
├── layouts.py
│   ├── 품목 마스터 관리
│   ├── 입출고 처리
│   ├── 재고 현황 조회
│   ├── 재고 조정
│   └── 재고 설정
└── callbacks.py
    ├── 품목 CRUD
    ├── 입출고 처리 로직
    ├── 재고 실시간 업데이트
    ├── 재고 부족 알림
    └── Excel 내보내기
3. 구매관리 모듈
modules/purchase/
├── layouts.py
│   ├── 발주서 관리
│   ├── 입고 검수
│   ├── 거래처 관리
│   ├── 구매 분석
│   └── 자동 발주 제안
└── callbacks.py
    ├── 발주서 생성/수정
    ├── 입고 검수 처리
    ├── 거래처 등록
    ├── 자동 발주 로직
    └── 구매 통계 분석
4. 회계관리 모듈
modules/accounting/
├── layouts.py
│   ├── 전표 관리
│   ├── 매출/매입 관리
│   ├── 재무제표 생성
│   ├── 원가 관리
│   ├── 예산 관리
│   └── 고정자산 관리
└── callbacks.py
    ├── 전표 입력/승인
    ├── 세금계산서 발행
    ├── 재무제표 자동생성
    ├── 예산 대비 실적
    └── 원가 계산
5. 영업관리 모듈 (V1.0 신규)
modules/sales/
├── layouts.py
│   ├── 견적서 관리
│   ├── 수주 관리
│   ├── 고객 관리
│   ├── 영업 분석
│   ├── CRM 대시보드
│   └── 영업 설정
└── callbacks.py
    ├── 견적서 생성/전환
    ├── 수주 처리
    ├── 고객 등급 관리
    ├── 영업 활동 기록
    ├── 영업 기회 관리
    └── 매출 예측
🛠️ 유틸리티 스크립트
데이터베이스 초기화

create_accounting_tables.py: 회계 테이블 생성
create_purchase_tables.py: 구매 테이블 생성
create_sales_tables.py: 영업 테이블 생성
init_all_database.py: 전체 DB 초기화

샘플 데이터 추가

add_accounting_sample_data.py: 회계 샘플 (전표, 예산 등)
add_purchase_sample_data.py: 구매 샘플 (발주서, 거래처)
add_sales_sample_data.py: 영업 샘플 (고객, 견적서)

설정 및 점검

setup_v1_0.py: V1.0 영업관리 설정
check_inventory_module.py: 재고모듈 상태 점검
init_and_setup_purchase.py: 구매모듈 통합 설정

📋 테스트 파일

test_accounting.py: 회계모듈 테스트
test_purchase.py: 구매모듈 테스트

📚 문서 파일

README V0.9.md: 시스템 전체 설명서
mockup V0.9.md: UI/UX 목업 및 설계

🎨 정적 파일

assets/style.css: 커스텀 CSS 스타일

🔧 기타 파일

run.bat: Windows 실행 스크립트
setup_modules.py: 모듈 구조 생성

📊 주요 기능 요약
통합 기능

실시간 대시보드: 모든 모듈 상태 한눈에
모듈 간 연계: 구매→재고→회계 자동 연동
권한 관리: admin/user 역할 구분
다중 창고: 창고별 재고 관리

특별 기능

자동 발주: 재고 부족 시 자동 제안
재무제표 자동생성: 실시간 손익계산서
영업 파이프라인: 견적→수주 전환율 추적
원가 계산: 제품별 원가 자동 계산

데이터 흐름
생산 → 재고 → 구매 → 회계
  ↓      ↓      ↓      ↓
 MES   입출고  발주   전표
         ↓      ↓      ↓
       원가   매입   재무제표
필요한 특정 기능에 대해 더 자세히 알고 싶으시면 말씀해주세요! 🚀
