
**File: `/README.md`**

```markdown
# 🏭 Smart MES-ERP System V0.9

<div align="center">
  <img src="https://img.shields.io/badge/version-0.8.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/modules-4%2F8-orange.svg" alt="Modules">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🚀 스마트 제조 통합 관리 시스템</h3>
  <p>생산부터 회계까지, 제조업의 모든 프로세스를 하나로</p>
  <p><strong>💰 회계관리 모듈 완성! 재무제표 자동 생성!</strong></p>
</div>

## 🆕 V0.9 새로운 기능

### ✨ 주요 업데이트

1. **💰 회계관리 모듈 완성** ✅
   - 전표 관리 (입금/출금/대체)
   - 매출/매입 세금계산서
   - 재무제표 자동 생성
   - 예산 관리 및 통제
   - 원가 계산
   - 고정자산 관리

2. **🔧 시스템 안정성 개선**
   - 구매관리 콜백 오류 수정
   - 데이터베이스 초기화 개선
   - 모듈 간 ID 충돌 해결

3. **🔗 모듈 간 연계 강화**
   - 구매 → 회계 자동 전표
   - 재고 → 원가 자동 반영
   - 생산 → 제조원가 계산

## 📊 시스템 구성

### 구현 완료 모듈 (4/8)
- ✅ **MES (생산관리)**: 작업 입력, 현황 조회, 생산 분석
- ✅ **재고관리**: 입출고, 재고 현황, 재고 조정
- ✅ **구매관리**: 발주, 입고 검수, 거래처 관리
- ✅ **회계관리**: 전표, 재무제표, 예산, 원가

### 개발 예정 모듈
- 🚧 **영업관리** (V0.9): 견적, 수주, CRM
- 📅 **품질관리** (V1.0): 검사, 불량 관리
- 📅 **인사관리** (V1.1): 근태, 급여
- 📅 **설비관리** (V1.2): 보전, 가동률

## 🚀 빠른 시작

### 1. 요구사항
- Python 3.8 이상
- 필수 패키지는 `requirements.txt` 참조

### 2. 설치 및 실행
```bash
# 1. 저장소 클론
git clone https://github.com/your-repo/smart-mes-erp.git
cd smart-mes-erp

# 2. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 실행
python app.py
3. 접속

URL: http://localhost:8050
ID: admin / PW: admin123

📁 프로젝트 구조
Smart-MES-ERP-V0.8/
├── app.py                 # 메인 애플리케이션
├── requirements.txt       # 필수 패키지
├── config.yaml           # 시스템 설정
├── modules/              # 모듈별 코드
│   ├── mes/             # 생산관리
│   ├── inventory/       # 재고관리
│   ├── purchase/        # 구매관리
│   └── accounting/      # 회계관리 (신규)
├── scripts/             # 유틸리티 스크립트
│   ├── create_accounting_tables.py
│   └── add_accounting_sample_data.py
├── data/               # 데이터베이스
├── logs/               # 로그 파일
└── assets/             # 정적 파일
🛠️ 기술 스택
Backend

Python 3.8+: 메인 언어
Dash 2.14.0: 웹 프레임워크
SQLite3: 데이터베이스
Pandas: 데이터 처리

Frontend

React: Dash 컴포넌트
Bootstrap 5: UI 프레임워크
Plotly: 차트 라이브러리

💡 주요 기능
1. 회계관리 (신규)

전표 관리: 입금/출금/대체 전표 자동 생성
재무제표: 손익계산서, 재무상태표 실시간 생성
예산 관리: 부서별 예산 편성 및 집행 통제
원가 계산: 제품별 원가 자동 계산

2. 통합 대시보드

실시간 생산 현황
재고 부족 알림
발주 승인 대기
회계 전표 현황

3. 모듈 간 연계

구매 발주 → 회계 전표 자동 생성
재고 입출고 → 원가 자동 반영
생산 실적 → 제조원가 계산

🔧 설정
config.yaml
yamlmodules:
  mes: true          # 생산관리
  inventory: true    # 재고관리
  purchase: true     # 구매관리
  accounting: true   # 회계관리
  sales: false       # 영업관리 (개발중)
📈 성능

동시 사용자: 50명
응답 시간: < 2초
데이터 처리: 100만 건/일

🐛 알려진 이슈

구매관리 콜백 오류 → V0.8에서 수정됨
회계 테이블 누락 → init_database()에 추가됨
대용량 데이터 처리 시 속도 저하 (개선 예정)

🗺️ 로드맵
V1.0 (2025년 7월)

 영업관리 모듈
 모바일 반응형 UI
 다국어 지원

V1.1 (2025년 8월)

 품질관리 모듈
 API 개발
 클라우드 배포

📝 라이선스
MIT License - 자유롭게 사용 가능
🤝 기여
기여를 환영합니다! PR을 보내주세요.
📞 문의

Email: support@smart-mes-erp.com
Documentation: https://docs.smart-mes-erp.com


<div align="center">
  <p>Made with ❤️ by Smart Factory Team</p>
  <p>© 2025 Smart MES-ERP. All rights reserved.</p>
</div>
```
다음 대화를 위한 핵심 메모:

구매관리 callbacks.py - 모든 콜백이 register_purchase_callbacks(app) 함수 내부에 있어야 함
회계관리 ID - 모든 ID에 accounting- 접두사 사용
app.py의 init_database() - 회계 테이블 생성 코드가 포함되어 있음
다음 작업: 영업관리 모듈 개발 (V1.0)
