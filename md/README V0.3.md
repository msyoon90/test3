# 🏭 Smart MES-ERP System V0.3

<div align="center">
  <img src="https://img.shields.io/badge/version-0.3.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/dash-2.14.0-red.svg" alt="Dash">
  <img src="https://img.shields.io/badge/tests-45%20passed-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-87%25-yellowgreen.svg" alt="Coverage">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🚀 코드 없이 커스터마이징 가능한 스마트 생산관리 시스템</h3>
  <p>MES에서 시작해 ERP로 확장 가능한 모듈식 통합 플랫폼</p>
  <p><strong>이제 재고관리와 테스트 시스템을 포함합니다!</strong></p>
</div>

---

## 📋 목차

- [소개](#-소개)
- [V0.3 새로운 기능](#-v03-새로운-기능)
- [시작하기](#-시작하기)
- [테스트 실행](#-테스트-실행)
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
- 🧪 **통합 테스트**: 자동화된 테스트 시스템
- 🐛 **고급 디버깅**: 실시간 성능 모니터링

---

## 🆕 V0.3 새로운 기능

### ✨ 주요 업데이트

#### 1. **재고관리 모듈 완성** ✅
- 품목 마스터 관리
- 입출고 처리
- 재고 현황 대시보드
- 재고 조정 기능
- 안전재고 알림

#### 2. **테스트 시스템** 🧪
- pytest 기반 자동화 테스트
- 단위/통합/UI/성능 테스트
- 코드 커버리지 측정
- CI/CD 통합 준비

#### 3. **디버깅 도구 강화** 🐛
- 실시간 로그 뷰어
- SQL 쿼리 분석
- 성능 프로파일링
- 시스템 리소스 모니터링

### 📊 시스템 상태
```
구현 완료: MES ✅ | 재고관리 ✅
개발 예정: 구매관리 🚧 | 영업관리 🚧 | 회계관리 🚧
코드 품질: Coverage 87% | Bugs 0.3/KLOC
```

---

## 🚀 시작하기

### 📋 필요 사항
- Python 3.8 이상
- 웹 브라우저 (Chrome, Firefox, Safari, Edge)

### 📥 설치 방법

```bash
# 1. 저장소 클론
git clone https://github.com/msyoon90/my-mes-dashboardv0.1.git
cd my-mes-dashboardv0.1

# 2. 가상환경 생성 (권장)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. 필요 패키지 설치
pip install -r requirements.txt

# 4. 개발 패키지 설치 (테스트용)
pip install -r requirements-dev.txt

# 5. 시스템 실행
python app.py
```

### 🌐 접속하기
- URL: http://localhost:8050
- 기본 계정: admin / admin123
- 게스트 접속: 로그인 화면에서 "게스트 접속" 버튼

---

## 🧪 테스트 실행

### 전체 테스트 실행
```bash
# 모든 테스트 실행
python -m pytest

# 커버리지 포함
python -m pytest --cov=./ --cov-report=html

# 특정 모듈만 테스트
python -m pytest tests/test_mes.py
python -m pytest tests/test_inventory.py
```

### 테스트 카테고리별 실행
```bash
# 단위 테스트만
python -m pytest -m "unit"

# 통합 테스트만
python -m pytest -m "integration"

# 성능 테스트만
python -m pytest -m "performance"
```

### 테스트 리포트 확인
```bash
# HTML 커버리지 리포트 열기
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

---

## 🔧 문제 해결

### 🐛 디버그 모드 실행
```bash
# 디버그 모드로 실행
python app.py --debug

# 상세 로그 출력
python app.py --log-level=DEBUG
```

### 📊 성능 프로파일링
```bash
# 성능 프로파일 생성
python -m cProfile -o profile.stats app.py

# 프로파일 분석
python -m pstats profile.stats
```

### ❓ 자주 발생하는 문제

<details>
<summary><b>테스트 실패: ModuleNotFoundError</b></summary>

```bash
# 해결 방법
pip install -r requirements-dev.txt
export PYTHONPATH="${PYTHONPATH}:${PWD}"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows
```
</details>

<details>
<summary><b>재고 데이터가 표시되지 않음</b></summary>

```bash
# 데이터베이스 재초기화
python -c "from app import init_database; init_database()"

# 샘플 데이터 추가
python scripts/add_sample_data.py
```
</details>

<details>
<summary><b>느린 응답 속도</b></summary>

1. 디버그 콘솔에서 성능 탭 확인
2. 느린 쿼리 확인: `logs/slow_queries.log`
3. 인덱스 최적화: `python scripts/optimize_db.py`
</details>

---

## 🏗️ 프로젝트 구조

```
my-mes-dashboardv0.1/
├── 📄 app.py                    # 메인 애플리케이션
├── 📄 requirements.txt          # 운영 패키지
├── 📄 requirements-dev.txt      # 개발/테스트 패키지
├── 📄 pytest.ini               # 테스트 설정
├── 📄 .coveragerc              # 커버리지 설정
│
├── 📁 modules/                 # 비즈니스 모듈
│   ├── 📁 mes/                # MES 모듈 ✅
│   └── 📁 inventory/          # 재고관리 모듈 ✅
│
├── 📁 tests/                   # 테스트 코드
│   ├── 📄 conftest.py         # 테스트 설정
│   ├── 📄 test_app.py         # 앱 테스트
│   ├── 📄 test_database.py    # DB 테스트
│   ├── 📄 test_mes.py         # MES 테스트
│   └── 📄 test_inventory.py   # 재고 테스트
│
├── 📁 scripts/                 # 유틸리티 스크립트
│   ├── 📄 run_tests.py        # 테스트 실행기
│   ├── 📄 add_sample_data.py  # 샘플 데이터
│   └── 📄 optimize_db.py      # DB 최적화
│
└── 📁 docs/                    # 문서
    ├── 📄 testing_guide.md     # 테스트 가이드
    └── 📄 debugging_guide.md   # 디버깅 가이드
```

---

## 📈 개발 로드맵

### ✅ V0.1 (완료)
- [x] MES 기본 기능
- [x] 사용자 인증
- [x] 실시간 모니터링

### ✅ V0.2 (완료)
- [x] 재고관리 모듈 설계
- [x] 데이터베이스 스키마 확장

### 🚧 V0.3 (현재)
- [x] 재고관리 모듈 구현
- [x] 테스트 시스템 구축
- [ ] Excel 업로드/다운로드
- [ ] 성능 최적화

### 📅 V0.4 (2024 Q2)
- [ ] 구매관리 모듈
- [ ] PostgreSQL 지원
- [ ] Docker 컨테이너화
- [ ] API 개발

### 📅 V0.5 (2024 Q3)
- [ ] 영업관리 모듈
- [ ] 모바일 앱 (PWA)
- [ ] AI 수요 예측

### 🎯 V1.0 (2025 Q1)
- [ ] 회계관리 모듈
- [ ] 엔터프라이즈 기능
- [ ] 클라우드 SaaS 버전

---

## 👥 기여하기

### 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Write Tests (`pytest tests/test_your_feature.py`)
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

### 📝 코드 기여 규칙
- 모든 새 기능에는 테스트 필수
- 코드 커버리지 90% 이상 유지
- PEP 8 스타일 가이드 준수
- 타입 힌트 사용 권장

### 🧪 테스트 작성 가이드
```python
# tests/test_example.py
import pytest
from modules.inventory import calculate_stock

def test_calculate_stock():
    """재고 계산 테스트"""
    result = calculate_stock(100, 20)
    assert result == 80
    
@pytest.mark.integration
def test_stock_workflow():
    """재고 워크플로우 통합 테스트"""
    # 통합 테스트 코드
    pass
```

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
  <p><b>Version 0.3.0</b> - Now with Inventory Management and Testing Suite!</p>
</div>
