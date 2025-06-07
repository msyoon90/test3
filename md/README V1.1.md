# 🏭 Smart MES-ERP System V1.1

<div align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/modules-6%2F8-orange.svg" alt="Modules">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🚀 스마트 제조 통합 관리 시스템</h3>
  <p>생산부터 품질까지, 제조업의 핵심 프로세스를 하나로</p>
  <p><strong>🎉 V1.1 릴리스! 품질관리 모듈 추가!</strong></p>
</div>

## 🆕 V1.1 새로운 기능

### ✨ 주요 업데이트

1. **📋 품질관리 모듈 완성** ✅
   - 검사 관리 (입고/공정/출하 검사)
   - 불량 관리 (파레토 분석, 원인 추적)
   - SPC (X-bar/R 관리도, Cp/Cpk 분석)
   - 품질 성적서 발행
   - 측정 장비 교정 관리

2. **📱 모바일 반응형 UI 개선**
   - 터치 최적화 인터페이스
   - 모바일 전용 레이아웃
   - 제스처 기반 네비게이션

3. **🌐 다국어 지원 준비**
   - i18n 프레임워크 기반 구축
   - 한국어/영어 전환 준비

## 📊 시스템 구성

### 구현 완료 모듈 (6/8) - 75%
- ✅ **MES (생산관리)**: 작업 입력, 현황 조회, 생산 분석
- ✅ **재고관리**: 입출고, 재고 현황, 재고 조정
- ✅ **구매관리**: 발주, 입고 검수, 거래처 관리
- ✅ **영업관리**: 견적, 수주, 고객, CRM
- ✅ **회계관리**: 전표, 재무제표, 예산, 원가
- ✅ **품질관리**: 검사, 불량, SPC, 성적서 (V1.1 신규)

### 개발 예정 모듈
- 📅 **인사관리** (V1.2): 근태, 급여, 조직도
- 📅 **설비관리** (V1.3): 예방보전, 가동률

## 🚀 빠른 시작

### 1. 요구사항
```
- Python 3.8 이상
- 4GB 이상 RAM
- 10GB 이상 디스크 공간
```

### 2. 설치
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
pip install scipy==1.10.1  # V1.1 추가

# 4. 초기 설정
cd scripts
python create_quality_tables.py  # V1.1
python setup_v1_1.py

# 5. 실행
cd ..
python app.py
```

### 3. 접속
```
URL: http://localhost:8050
ID: admin / PW: admin123
```

## 📁 프로젝트 구조
```
Smart-MES-ERP-V1.1/
├── app.py                 # 메인 애플리케이션
├── requirements.txt       # 필수 패키지
├── config.yaml           # 시스템 설정
├── modules/              # 모듈별 코드
│   ├── mes/             # 생산관리
│   ├── inventory/       # 재고관리
│   ├── purchase/        # 구매관리
│   ├── sales/           # 영업관리
│   ├── accounting/      # 회계관리
│   └── quality/         # 품질관리 (V1.1 신규)
│       ├── __init__.py
│       ├── layouts.py   # UI 레이아웃
│       └── callbacks.py # 기능 구현
├── scripts/             # 유틸리티 스크립트
│   ├── setup_v1_1.py    # V1.1 설정
│   └── create_quality_tables.py
├── data/               # 데이터베이스
├── logs/               # 로그 파일
├── backups/            # 백업 파일
└── assets/             # 정적 파일
```

## 🛠️ 기술 스택

### Backend
- **Python 3.8+**: 메인 언어
- **Dash 2.14.0**: 웹 프레임워크
- **SQLite3**: 데이터베이스
- **Pandas**: 데이터 처리
- **NumPy/SciPy**: 통계 분석 (V1.1)

### Frontend
- **React**: Dash 컴포넌트
- **Bootstrap 5**: UI 프레임워크
- **Plotly**: 차트 라이브러리
- **Font Awesome**: 아이콘

## 💡 주요 기능

### 1. 품질관리 (V1.1 신규)
- **검사 관리**: 3단계 검사 체계 (입고→공정→출하)
- **불량 분석**: 파레토 차트, 원인별 추적
- **SPC**: 실시간 공정 모니터링, Cpk 분석
- **성적서**: 자동 발행, PDF 출력
- **장비 관리**: 교정 일정 관리

### 2. 통합 프로세스
```
구매 발주 → 입고 검사 → 재고 입고 → 생산 투입 → 공정 검사 
→ 제품 완성 → 출하 검사 → 고객 납품 → 품질 성적서 발행
```

### 3. 실시간 대시보드
- 품질 지표 모니터링
- 불량률 추이
- SPC 이상 감지 알림
- 교정 예정 장비 알림

## 📈 성능 및 제한사항

### 성능
- 동시 사용자: 최대 100명
- 응답 시간: 평균 < 1.5초
- 데이터 처리: 200만 건/일
- SPC 계산: 실시간 (< 0.5초)

### 제한사항
- 단일 서버 환경
- 파일 첨부 최대 10MB
- SPC 샘플 최대 1000개/차트

## 🔧 설정

### config.yaml
```yaml
system:
  name: Smart MES-ERP
  version: "1.1.0"
  language: ko
  update_interval: 2000

modules:
  mes: true
  inventory: true
  purchase: true
  sales: true
  accounting: true
  quality: true      # V1.1 신규

quality:
  default_sampling_rate: 10
  target_defect_rate: 2.0
  spc_rules: ['rule1', 'rule2']
  calibration_reminder_days: 30
```

## 🐛 알려진 이슈 및 해결

### V1.1에서 해결된 이슈
- ✅ 모바일 레이아웃 개선
- ✅ 차트 성능 최적화
- ✅ 실시간 업데이트 안정화

### 현재 알려진 이슈
- SPC 차트 대용량 데이터 처리 시 지연
- 모바일 가로 모드 일부 레이아웃 깨짐
- PDF 출력 시 한글 폰트 문제

## 🗺️ 로드맵

### V1.2 (2025년 10월)
- 👥 **인사관리 모듈**
- 🔌 **REST API**

### V1.3 (2025년 12월)
- 🔧 **설비관리 모듈**
- 📊 **고급 분석 기능**
- 🤖 **AI 예측 모델**
- 💬 **LLM 채팅 도우미**
  - 자연어 데이터 조회
  - 시스템 사용 가이드
  - 간단한 업무 지원

### V1.4 (2026년 2월)
- 📺 **대시보드 슬라이드쇼 기능**
  - 제조 현장 대형 TV 표시
  - 실시간 데이터 슬라이드쇼
  - 커스터마이징 가능

## 🎯 V1.4 대시보드 슬라이드쇼 기능 (예정)

### 📋 주요 기능

#### 1. 슬라이드 구성
- 📊 **생산 현황**: 실시간 생산 달성률, 불량률
- 📈 **품질 지표**: SPC 차트, 불량 파레토
- 📦 **재고 현황**: 주요 자재 재고 수준
- 💰 **매출 현황**: 일/월 매출 추이
- 🏭 **설비 가동률**: 라인별 가동 상태
- 📅 **일정 현황**: 금일 생산 계획, 납기 임박 건

#### 2. 커스터마이징 기능
- 슬라이드 순서 드래그&드롭 변경
- 각 슬라이드 표시 시간 설정 (5초~5분)
- 팀별/부서별 맞춤 슬라이드 세트
- 특정 슬라이드 on/off
- 긴급 공지사항 삽입

#### 3. 표시 모드
- 📺 **전체화면**: F11 또는 버튼 클릭
- 🌓 **테마**: 시간대별 자동 전환
- 📱 **반응형**: TV, 태블릿, 모바일
- 🔄 **자동 새로고침**: 실시간 업데이트

### 🎨 UI/UX 특징
- 큰 폰트와 명확한 색상 (원거리 가독성)
- 애니메이션 차트 (시선 집중)
- 중요 지표 강조 (빨강/초록)
- 깔끔한 레이아웃

### 💡 활용 시나리오
1. **생산 현장**: 작업자 실시간 목표 확인
2. **품질 회의실**: 품질 지표 모니터링
3. **경영진 사무실**: 주요 KPI 파악
4. **고객 방문**: 스마트 팩토리 시연

### 🔧 기술 구현
- Dash Interval: 자동 슬라이드 전환
- CSS Animation: 부드러운 효과
- LocalStorage: 사용자 설정 저장
- WebSocket: 실시간 알림 (옵션)

### 📱 추가 기능
- **QR 코드**: 모바일 상세 보기
- **음성 안내**: 중요 알림 TTS
- **원격 제어**: 관리자 원격 제어
- **스케줄링**: 시간대별 세트

## 📝 라이선스
MIT License - 자유롭게 사용 및 수정 가능

## 🤝 기여
기여를 환영합니다! 다음 절차를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- 📧 **Email**: support@smart-mes-erp.com
- 📚 **Documentation**: https://docs.smart-mes-erp.com
- 💬 **Discord**: https://discord.gg/smartmeserp
- 🐛 **Issues**: https://github.com/your-repo/smart-mes-erp/issues

## 🙏 감사의 말
이 프로젝트는 많은 오픈소스 커뮤니티의 도움으로 만들어졌습니다.
특히 Plotly Dash 팀과 모든 기여자들에게 감사드립니다.

---

<div align="center">
  <p>Made with ❤️ by Smart Factory Team</p>
  <p>© 2025 Smart MES-ERP. All rights reserved.</p>
</div>
