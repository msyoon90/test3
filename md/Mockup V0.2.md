# 🎨 Smart MES-ERP 통합 시스템 Mockup V0.2

## 🚀 Version 0.2 업데이트 사항
- 📝 필수 코딩 가이드라인 추가
- 🔍 오류 해결 프롬프트 솔루션 추가
- 📊 확장된 로드맵 (v0.3 ~ v1.0)
- 🏗️ 향상된 시스템 아키텍처

---

## ⚠️ 필수 코딩 가이드라인 (MUST READ)

### 1️⃣ 풀 코드 작성 원칙
```
❌ 절대 금지사항:
- # ... existing code ... 
- # 기존 코드 유지
- # 나머지 코드는 동일

✅ 필수 준수사항:
- 모든 함수는 완전한 코드로 작성
- import 문부터 끝까지 전체 코드 제공
- 수정 시에도 전체 파일 내용 포함
```

### 2️⃣ 파일 경로 명시 원칙
```python
# 모든 코드 블록 상단에 파일 경로 명시
# File: /modules/mes/layouts.py

import dash
from dash import dcc, html
# ... 전체 코드 ...
```

### 3️⃣ 오류 해결 프롬프트 템플릿
```
오류 발생 시 다음 형식으로 요청:
"
파일: [정확한 파일 경로]
오류: [전체 오류 메시지]
현재 코드: [문제가 되는 부분의 전체 코드]
"
```

---

## 🛠️ 폴더별 오류 해결 가이드

### 📁 프로젝트 루트 디렉토리
```bash
# 프롬프트 명령어 - 초기 설정 검증
python -c "
import os
import sys

# 필수 디렉토리 체크 및 생성
dirs = ['data', 'logs', 'backups', 'assets', 'modules/mes', 'core', 'docs']
for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f'✅ {d} 디렉토리 확인/생성')

# 필수 파일 체크
files = ['app.py', 'requirements.txt', 'config.yaml']
for f in files:
    if os.path.exists(f):
        print(f'✅ {f} 파일 존재')
    else:
        print(f'❌ {f} 파일 없음 - 생성 필요')

# Python 버전 체크
print(f'Python 버전: {sys.version}')
"
```

### 📁 /modules 폴더 오류 해결
```python
# File: /debug_modules.py
"""모듈 임포트 문제 해결 스크립트"""
import sys
import os

def check_module_structure():
    """모듈 구조 검증 및 복구"""
    module_files = {
        'modules/__init__.py': '',
        'modules/mes/__init__.py': '''
from .layouts import create_mes_layout
from .callbacks import register_mes_callbacks

__all__ = ['create_mes_layout', 'register_mes_callbacks']
''',
    }
    
    for filepath, content in module_files.items():
        if not os.path.exists(filepath):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filepath} 생성 완료")
        else:
            print(f"✅ {filepath} 이미 존재")

if __name__ == "__main__":
    check_module_structure()
```

### 📁 /data 폴더 오류 해결
```python
# File: /debug_database.py
"""데이터베이스 문제 해결 스크립트"""
import sqlite3
import os

def check_database():
    """데이터베이스 상태 확인 및 복구"""
    db_path = 'data/database.db'
    
    try:
        # 디렉토리 확인
        os.makedirs('data', exist_ok=True)
        
        # DB 연결 테스트
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 데이터베이스 상태:")
        print(f"- 위치: {os.path.abspath(db_path)}")
        print(f"- 크기: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")
        print(f"- 테이블: {[t[0] for t in tables]}")
        
        # 필수 테이블 체크
        required_tables = ['users', 'work_logs', 'system_config', 'form_templates']
        missing_tables = [t for t in required_tables if t not in [table[0] for table in tables]]
        
        if missing_tables:
            print(f"⚠️ 누락된 테이블: {missing_tables}")
            print("💡 app.py의 init_database() 함수 실행 필요")
        else:
            print("✅ 모든 필수 테이블 존재")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")
        print("💡 해결방법: app.py 실행 또는 init_database() 함수 직접 호출")

if __name__ == "__main__":
    check_database()
```

### 📁 /assets 폴더 오류 해결
```python
# File: /debug_assets.py
"""정적 파일 문제 해결 스크립트"""
import os

def check_assets():
    """assets 폴더 및 CSS 파일 확인"""
    css_path = 'assets/style.css'
    
    if not os.path.exists('assets'):
        os.makedirs('assets')
        print("✅ assets 폴더 생성")
    
    if not os.path.exists(css_path):
        # 기본 CSS 생성
        default_css = """/* Smart MES-ERP 기본 스타일 */
body {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #f5f5f5;
}
"""
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(default_css)
        print("✅ style.css 기본 파일 생성")
    else:
        print(f"✅ CSS 파일 존재 ({os.path.getsize(css_path)} bytes)")

if __name__ == "__main__":
    check_assets()
```

---

## 🏗️ 향상된 시스템 아키텍처 V0.2

```
┌─────────────────────────────────────────────────────────────────┐
│                    🏭 Smart MES-ERP System V0.2                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 사용자 레이어                                               │
│  ├── 웹 브라우저 (반응형)                                      │
│  ├── 모바일 앱 (PWA) - v0.3 예정                              │
│  └── API 클라이언트 - v0.4 예정                               │
│                                                                 │
│  🎯 애플리케이션 레이어                                         │
│  ├── Dash Framework                                           │
│  ├── 인증/권한 관리                                           │
│  ├── 실시간 업데이트 (WebSocket)                              │
│  └── 캐싱 시스템 - v0.3 예정                                  │
│                                                                 │
│  📦 비즈니스 로직 레이어                                        │
│  ├── MES 모듈 ✅                                              │
│  ├── 재고관리 모듈 🚧 (v0.2)                                  │
│  ├── 구매관리 모듈 📅 (v0.3)                                  │
│  ├── 영업관리 모듈 📅 (v0.4)                                  │
│  └── 회계관리 모듈 📅 (v0.5)                                  │
│                                                                 │
│  💾 데이터 레이어                                               │
│  ├── SQLite (개발/소규모)                                      │
│  ├── PostgreSQL 지원 - v0.3 예정                              │
│  ├── 백업/복원 시스템                                         │
│  └── 데이터 마이그레이션 도구 - v0.3 예정                     │
│                                                                 │
│  🔧 인프라 레이어                                               │
│  ├── Docker 컨테이너화 - v0.3 예정                            │
│  ├── CI/CD 파이프라인 - v0.4 예정                             │
│  └── 모니터링/로깅 시스템                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📅 확장 로드맵 (v0.2 → v1.0)

### 🔹 Version 0.2 (현재 개발 중)
```
[재고관리 모듈]
✅ 품목 마스터 관리
✅ 입출고 처리
✅ 재고 현황 조회
✅ 안전재고 알림
🚧 바코드/QR 코드 지원
🚧 재고 실사 기능

[시스템 개선]
✅ Excel 업로드/다운로드
✅ 데이터 검증 강화
🚧 다국어 지원 (한/영)
🚧 테마 커스터마이징
```

### 🔹 Version 0.3
```
[구매관리 모듈]
- 발주 관리
- 입고 검수
- 거래처 관리
- 구매 분석

[기술 업그레이드]
- PostgreSQL 지원
- Docker 컨테이너화
- Redis 캐싱
- 성능 최적화
```

### 🔹 Version 0.4
```
[영업관리 모듈]
- 견적/수주 관리
- 출하 관리
- 고객 관리
- 매출 분석

[API 시스템]
- RESTful API
- GraphQL 지원
- API 문서화
- 외부 시스템 연동
```

### 🔹 Version 0.5
```
[회계관리 모듈]
- 매입/매출 관리
- 원가 계산
- 재무제표
- 세금계산서

[고급 기능]
- AI 수요 예측
- 최적 재고 제안
- 이상 탐지
- 자동 리포트
```

### 🔹 Version 1.0 (정식 출시)
```
[엔터프라이즈 기능]
- 다중 회사 지원
- 고급 권한 관리
- 감사 추적
- 규정 준수 보고서

[클라우드 지원]
- SaaS 버전
- 자동 스케일링
- 백업/복구
- 24/7 모니터링
```

---

## 🐛 디버깅 마스터 명령어

### 통합 디버깅 스크립트
```python
# File: /debug_all.py
"""전체 시스템 상태 점검 스크립트"""
import subprocess
import sys
import os

def run_all_checks():
    """모든 디버깅 스크립트 실행"""
    scripts = [
        'debug_modules.py',
        'debug_database.py',
        'debug_assets.py'
    ]
    
    print("🔍 Smart MES-ERP 시스템 점검 시작...\n")
    
    for script in scripts:
        print(f"--- {script} 실행 중 ---")
        if os.path.exists(script):
            subprocess.run([sys.executable, script])
        else:
            print(f"⚠️ {script} 파일이 없습니다.")
        print("\n")
    
    print("✅ 시스템 점검 완료!")
    print("💡 문제가 있다면 각 스크립트의 제안사항을 따르세요.")

if __name__ == "__main__":
    run_all_checks()
```

---

## 💡 V0.2 핵심 개선사항

### 1. 코드 품질 보증
- 모든 코드는 완전한 형태로 제공
- 파일 경로 명시 필수
- 주석과 문서화 강화

### 2. 오류 방지 시스템
- 사전 검증 스크립트
- 자동 복구 기능
- 상세한 오류 메시지

### 3. 확장성 고려
- 모듈식 설계 강화
- 플러그인 시스템 준비
- API 우선 접근법

### 4. 개발자 경험 향상
- 디버깅 도구 내장
- 자동화된 테스트
- 실시간 리로드

---

## 📝 다음 단계 체크리스트

- [ ] V0.2 재고관리 모듈 구현
- [ ] Excel 업로드/다운로드 기능
- [ ] 바코드 스캔 기능
- [ ] 다국어 지원 시스템
- [ ] PostgreSQL 마이그레이션 준비
- [ ] Docker 파일 작성
- [ ] API 설계 문서 작성
- [ ] 단위 테스트 추가
- [ ] 사용자 매뉴얼 작성
- [ ] 배포 가이드 작성
