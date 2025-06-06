# run_mes_only.py - MES 전용 실행 스크립트

import os
import sys
import sqlite3
from datetime import datetime

def setup_mes_database():
    """MES 전용 데이터베이스 설정"""
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # 데이터베이스 연결
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("🔧 MES 데이터베이스 초기화 중...")
    
    # 1. 사용자 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. 작업 로그 테이블 (MES 핵심)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_number TEXT NOT NULL,
            work_date DATE NOT NULL,
            process TEXT NOT NULL,
            worker_id INTEGER,
            plan_qty INTEGER,
            prod_qty INTEGER,
            defect_qty INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES users (id)
        )
    ''')
    
    # 3. 시스템 설정 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4. 폼 템플릿 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            config TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 기본 관리자 계정 생성
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
        print("  ✅ 관리자 계정 생성 (admin/admin123)")
    
    # 샘플 작업자 추가
    sample_workers = [
        ('worker1', 'pass123', 'worker'),
        ('worker2', 'pass123', 'worker'),
        ('worker3', 'pass123', 'worker')
    ]
    
    for username, password, role in sample_workers:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
    
    print("  ✅ 작업자 계정 생성")
    
    # 샘플 작업 데이터 추가 (최근 7일)
    cursor.execute("SELECT COUNT(*) FROM work_logs")
    if cursor.fetchone()[0] == 0:
        print("  📊 샘플 작업 데이터 추가 중...")
        
        processes = ['절단', '가공', '조립', '검사', '포장']
        
        for i in range(7, -1, -1):
            work_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            for j in range(3):  # 하루 3건
                lot_number = f"LOT-{work_date.replace('-', '')}-{j+1:03d}"
                process = processes[j % len(processes)]
                worker_id = (j % 3) + 2  # worker1, worker2, worker3
                plan_qty = 100 + (j * 50)
                prod_qty = plan_qty - (i * 2)  # 날짜가 오래될수록 생산량 감소
                defect_qty = max(0, i)  # 날짜가 오래될수록 불량 증가
                
                cursor.execute("""
                    INSERT INTO work_logs 
                    (lot_number, work_date, process, worker_id, plan_qty, prod_qty, defect_qty)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (lot_number, work_date, process, worker_id, plan_qty, prod_qty, defect_qty))
        
        print("  ✅ 샘플 작업 데이터 추가 완료")
    
    conn.commit()
    conn.close()
    
    print("\n✅ MES 데이터베이스 설정 완료!")

def check_requirements():
    """필수 패키지 확인"""
    print("🔍 필수 패키지 확인 중...")
    
    required_packages = {
        'dash': 'dash==2.14.0',
        'dash_bootstrap_components': 'dash-bootstrap-components==1.5.0',
        'pandas': 'pandas==2.0.3',
        'plotly': 'plotly==5.17.0',
        'pyyaml': 'PyYAML==6.0.1'
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(install_name)
            print(f"  ❌ {package} - 설치 필요")
    
    if missing_packages:
        print("\n❌ 누락된 패키지가 있습니다.")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def run_mes_app():
    """MES 애플리케이션 실행"""
    print("\n🚀 Smart MES 시스템 시작 중...")
    
    # Python 경로에 현재 디렉토리 추가
    sys.path.insert(0, os.path.abspath('.'))
    
    try:
        # app_mes_only.py 실행
        if os.path.exists('app_mes_only.py'):
            print("📱 app_mes_only.py 실행...")
            os.system('python app_mes_only.py')
        else:
            print("❌ app_mes_only.py 파일을 찾을 수 없습니다.")
            print("먼저 app_mes_only.py 파일을 생성하세요.")
            
    except KeyboardInterrupt:
        print("\n\n👋 MES 시스템을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🏭 Smart MES System - 생산관리 전용 버전")
    print("=" * 50)
    
    # 1. 필수 패키지 확인
    if not check_requirements():
        print("\n필수 패키지를 먼저 설치하세요.")
        return
    
    # 2. 데이터베이스 설정
    setup_mes_database()
    
    # 3. 설정 파일 생성
    if not os.path.exists('config_mes_only.yaml'):
        print("\n📄 MES 전용 설정 파일 생성 중...")
        config_content = '''# Smart MES System Configuration
# MES 모듈만 활성화된 간소화 버전

# 시스템 기본 설정
system:
  name: Smart MES
  version: "1.0.0"
  language: ko
  update_interval: 2000  # 실시간 업데이트 주기 (밀리초)

# 모듈 활성화 설정
modules:
  mes: true          # MES (생산관리) - 활성화
  inventory: false   # 재고관리 - 비활성화
  purchase: false    # 구매관리 - 비활성화
  sales: false       # 영업관리 - 비활성화
  accounting: false  # 회계관리 - 비활성화

# 인증 설정
authentication:
  enabled: true           # 로그인 기능 사용 여부
  session_timeout: 30     # 세션 타임아웃 (분)

# 데이터베이스 설정
database:
  path: data/database.db  # SQLite 데이터베이스 파일 경로

# MES 설정
mes:
  processes:
    - 절단
    - 가공
    - 조립
    - 검사
    - 포장
  shifts:
    - day: "주간"
      start: "08:00"
      end: "17:00"
    - night: "야간"
      start: "17:00"
      end: "02:00"
'''
        
        with open('config_mes_only.yaml', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("  ✅ config_mes_only.yaml 생성 완료")
    
    # 4. 실행 옵션 선택
    print("\n" + "=" * 50)
    print("🎯 Smart MES 시스템 준비 완료!")
    print("=" * 50)
    print("\n실행 옵션:")
    print("1. MES 시스템 실행")
    print("2. 종료")
    
    choice = input("\n선택 (1-2): ")
    
    if choice == '1':
        run_mes_app()
    else:
        print("\n👋 종료합니다.")

if __name__ == "__main__":
    main()
