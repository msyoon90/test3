# File: scripts/setup_v1_1_integrated.py
# Smart MES-ERP V1.1 통합 설정 스크립트
# V1.0 영업관리 + V1.1 품질관리 모듈 한번에 설정

import os
import sys
import sqlite3
import yaml
import shutil
from datetime import datetime
import subprocess

def print_header():
    """헤더 출력"""
    print("=" * 70)
    print("🚀 Smart MES-ERP V1.1 통합 설정 스크립트")
    print("=" * 70)
    print("📦 포함 모듈: MES, 재고, 구매, 영업(V1.0), 회계, 품질(V1.1)")
    print("=" * 70)
    print()

def check_requirements():
    """시스템 요구사항 확인"""
    print("🔍 시스템 요구사항 확인 중...")
    
    # Python 버전 확인
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        return False
    print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 필수 모듈 확인
    required_modules = {
        'dash': '2.14.0',
        'dash_bootstrap_components': '1.5.0',
        'pandas': '2.0.3',
        'plotly': '5.17.0',
        'yaml': None,
        'numpy': '1.24.3',
        'scipy': '1.10.1'  # V1.1 품질관리용
    }
    
    missing_modules = []
    for module, version in required_modules.items():
        try:
            imported = __import__(module)
            if hasattr(imported, '__version__') and version:
                print(f"  ✅ {module} ({imported.__version__})")
            else:
                print(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(f"{module}=={version}" if version else module)
            print(f"  ❌ {module}")
    
    if missing_modules:
        print(f"\n❌ 누락된 모듈: {', '.join(missing_modules)}")
        print("\n다음 명령으로 설치하세요:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def create_directory_structure():
    """전체 디렉토리 구조 생성"""
    print("\n📁 디렉토리 구조 생성 중...")
    
    directories = [
        # 기본 디렉토리
        'data',
        'logs',
        'backups',
        'assets',
        'tests',
        'docs',
        
        # 모듈 디렉토리
        'modules/mes',
        'modules/inventory',
        'modules/purchase',
        'modules/sales',        # V1.0
        'modules/accounting',
        'modules/quality',      # V1.1
        
        # 품질관리 하위 디렉토리
        'modules/quality/templates',
        'modules/quality/static',
        
        # 스크립트 디렉토리
        'scripts/db_init',
        'scripts/sample_data',
        'scripts/utils'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("  ✅ 디렉토리 구조 생성 완료")

def create_module_init_files():
    """모듈별 __init__.py 파일 생성"""
    print("\n📝 모듈 초기화 파일 생성 중...")
    
    modules = {
        'mes': 'MES (Manufacturing Execution System)',
        'inventory': 'Inventory Management',
        'purchase': 'Purchase Management',
        'sales': 'Sales Management (V1.0)',
        'accounting': 'Accounting Management',
        'quality': 'Quality Management (V1.1)'
    }
    
    for module, description in modules.items():
        init_content = f'''"""
{description} Module for Smart MES-ERP
"""

from .layouts import create_{module}_layout
from .callbacks import register_{module}_callbacks

__version__ = "1.1.0"
__author__ = "Smart Factory Team"

__all__ = ['create_{module}_layout', 'register_{module}_callbacks']
'''
        
        init_path = f'modules/{module}/__init__.py'
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(init_content)
        print(f"  ✅ {init_path}")

def initialize_database():
    """데이터베이스 초기화 및 모든 테이블 생성"""
    print("\n🗄️ 데이터베이스 초기화 중...")
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 기본 시스템 테이블
    print("  📋 기본 시스템 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            department TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            module TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("    ✅ 시스템 테이블 완료")
    
    # MES 테이블
    print("  🏭 MES 테이블 생성...")
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
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES users (id)
        )
    ''')
    print("    ✅ MES 테이블 완료")
    
    # 재고관리 테이블
    print("  📦 재고관리 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_master (
            item_code TEXT PRIMARY KEY,
            item_name TEXT NOT NULL,
            category TEXT,
            unit TEXT DEFAULT 'EA',
            safety_stock INTEGER DEFAULT 0,
            current_stock INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0,
            location TEXT,
            barcode TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movement_date DATE NOT NULL,
            movement_type TEXT NOT NULL,
            item_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            warehouse TEXT,
            lot_number TEXT,
            remarks TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    print("    ✅ 재고관리 테이블 완료")
    
    # 구매관리 테이블
    print("  🛒 구매관리 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_master (
            supplier_code TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            business_no TEXT,
            ceo_name TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            payment_terms TEXT DEFAULT 'CASH',
            lead_time INTEGER DEFAULT 7,
            rating INTEGER DEFAULT 3,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            po_number TEXT PRIMARY KEY,
            po_date DATE NOT NULL,
            supplier_code TEXT NOT NULL,
            delivery_date DATE,
            warehouse TEXT,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            approved_by INTEGER,
            approved_date TIMESTAMP,
            remarks TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_code) REFERENCES supplier_master (supplier_code),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    print("    ✅ 구매관리 테이블 완료")
    
    # 영업관리 테이블 (V1.0)
    print("  💼 영업관리 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_code TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            business_no TEXT,
            ceo_name TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            grade TEXT DEFAULT 'Bronze',
            payment_terms TEXT DEFAULT 'NET30',
            credit_limit REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            quote_number TEXT PRIMARY KEY,
            quote_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            validity_date DATE NOT NULL,
            total_amount REAL DEFAULT 0,
            discount_rate REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            notes TEXT,
            created_by INTEGER,
            approved_by INTEGER,
            approved_date TIMESTAMP,
            sent_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_orders (
            order_number TEXT PRIMARY KEY,
            order_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            quote_number TEXT,
            delivery_date DATE,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'received',
            payment_status TEXT DEFAULT 'pending',
            shipping_address TEXT,
            notes TEXT,
            created_by INTEGER,
            approved_by INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (quote_number) REFERENCES quotations (quote_number),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_code TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            unit_price REAL DEFAULT 0,
            cost_price REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("    ✅ 영업관리 테이블 완료")
    
    # 품질관리 테이블 (V1.1)
    print("  🔍 품질관리 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL,
            inspection_type TEXT NOT NULL,
            inspection_item TEXT NOT NULL,
            standard_value TEXT,
            upper_limit REAL,
            lower_limit REAL,
            unit TEXT,
            inspection_method TEXT,
            sampling_rate REAL DEFAULT 100,
            is_critical BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incoming_inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_no TEXT UNIQUE NOT NULL,
            inspection_date DATE NOT NULL,
            po_number TEXT NOT NULL,
            item_code TEXT NOT NULL,
            lot_number TEXT,
            received_qty INTEGER NOT NULL,
            sample_qty INTEGER NOT NULL,
            passed_qty INTEGER NOT NULL,
            failed_qty INTEGER DEFAULT 0,
            inspection_result TEXT NOT NULL,
            defect_type TEXT,
            defect_description TEXT,
            inspector_id INTEGER,
            approval_status TEXT DEFAULT 'pending',
            approved_by INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (inspector_id) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_types (
            defect_code TEXT PRIMARY KEY,
            defect_name TEXT NOT NULL,
            defect_category TEXT,
            severity_level INTEGER DEFAULT 3,
            description TEXT,
            corrective_action TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurement_equipment (
            equipment_id TEXT PRIMARY KEY,
            equipment_name TEXT NOT NULL,
            equipment_type TEXT,
            manufacturer TEXT,
            model_no TEXT,
            serial_no TEXT,
            calibration_date DATE,
            next_calibration_date DATE,
            calibration_cycle INTEGER DEFAULT 365,
            location TEXT,
            status TEXT DEFAULT 'active',
            responsible_person INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (responsible_person) REFERENCES users (id)
        )
    ''')
    print("    ✅ 품질관리 테이블 완료")
    
    # 회계관리 테이블
    print("  💰 회계관리 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_master (
            account_code TEXT PRIMARY KEY,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            parent_code TEXT,
            level INTEGER DEFAULT 1,
            is_control BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_header (
            voucher_no TEXT PRIMARY KEY,
            voucher_date DATE NOT NULL,
            voucher_type TEXT NOT NULL,
            description TEXT,
            total_debit REAL DEFAULT 0,
            total_credit REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_by INTEGER,
            approved_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    print("    ✅ 회계관리 테이블 완료")
    
    conn.commit()
    conn.close()
    print("  ✅ 데이터베이스 초기화 완료")

def insert_sample_data():
    """샘플 데이터 추가"""
    print("\n📊 샘플 데이터 추가 중...")
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # 기본 사용자 생성
        print("  👤 사용자 데이터...")
        users = [
            ('admin', 'admin123', 'admin', '경영지원', 'admin@company.com', '010-1234-5678'),
            ('user', 'user123', 'user', '생산팀', 'user@company.com', '010-2345-6789'),
            ('qc', 'qc123', 'user', '품질팀', 'qc@company.com', '010-3456-7890'),
            ('sales', 'sales123', 'user', '영업팀', 'sales@company.com', '010-4567-8901')
        ]
        
        for user in users:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password, role, department, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, user)
        print("    ✅ 사용자 4명")
        
        # 품목 마스터 데이터
        print("  📦 품목 데이터...")
        items = [
            ('ITEM001', '볼트 M10', '부품', 'EA', 100, 150, 500),
            ('ITEM002', '너트 M10', '부품', 'EA', 100, 200, 300),
            ('ITEM003', '철판 1.0T', '원자재', 'EA', 50, 75, 15000),
            ('ITEM004', '모터 DC24V', '부품', 'EA', 20, 25, 50000),
            ('ITEM005', '베어링 6201', '부품', 'EA', 50, 80, 3000)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO item_master 
            (item_code, item_name, category, unit, safety_stock, current_stock, unit_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, items)
        print("    ✅ 품목 5개")
        
        # 고객 데이터 (V1.0)
        print("  💼 고객 데이터...")
        customers = [
            ('CUST001', '(주)테크놀로지', '123-45-67890', '김대표', '이부장', '02-1234-5678', 
             'lee@technology.co.kr', '서울시 강남구 테헤란로 123', 'VIP', 'NET30', 100000000),
            ('CUST002', '글로벌산업(주)', '234-56-78901', '박사장', '최과장', '031-987-6543',
             'choi@global.com', '경기도 수원시 영통구 월드컵로 456', 'Gold', 'NET60', 50000000),
            ('CUST003', '스마트제조', '345-67-89012', '정대표', '김대리', '032-555-1234',
             'kim@smart.kr', '인천시 남동구 논현로 789', 'Silver', 'NET30', 30000000)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO customers 
            (customer_code, customer_name, business_no, ceo_name, contact_person,
             phone, email, address, grade, payment_terms, credit_limit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, customers)
        print("    ✅ 고객 3개")
        
        # 제품 데이터 (V1.0)
        print("  📱 제품 데이터...")
        products = [
            ('PROD001', 'Smart MES 시스템', 'Software', 'MES 솔루션 패키지', 50000000, 30000000),
            ('PROD002', 'ERP 통합 솔루션', 'Software', 'ERP 시스템 구축', 80000000, 50000000),
            ('PROD003', '자동화 제어시스템', 'Hardware', 'PLC 기반 자동화', 30000000, 18000000)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO products 
            (product_code, product_name, category, description, unit_price, cost_price, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, products)
        print("    ✅ 제품 3개")
        
        # 불량 유형 데이터 (V1.1)
        print("  🔍 불량 유형 데이터...")
        defects = [
            ('D001', '치수 불량', 'dimension', 2, '규격 치수 벗어남', '재가공 또는 폐기'),
            ('D002', '외관 불량', 'appearance', 3, '스크래치, 찍힘, 변색', '재작업 가능시 보수'),
            ('D003', '기능 불량', 'function', 1, '작동 불량, 성능 미달', '원인 분석 후 재제작'),
            ('D004', '재료 불량', 'material', 2, '재질 불량, 이물질 혼입', '재료 교체 및 재생산'),
            ('D005', '포장 불량', 'appearance', 3, '포장 파손, 라벨 오류', '재포장')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO defect_types 
            (defect_code, defect_name, defect_category, severity_level, description, corrective_action)
            VALUES (?, ?, ?, ?, ?, ?)
        """, defects)
        print("    ✅ 불량 유형 5개")
        
        # 측정 장비 데이터 (V1.1)
        print("  🔧 측정 장비 데이터...")
        equipment = [
            ('EQ001', '버니어 캘리퍼스', '치수측정', 'Mitutoyo', 'CD-15CPX', 'SN12345', 
             '2025-01-15', '2026-01-15', 365, '품질관리실', 'active', 3),
            ('EQ002', '마이크로미터', '치수측정', 'Mitutoyo', 'MDC-25PX', 'SN23456', 
             '2025-01-15', '2026-01-15', 365, '품질관리실', 'active', 3)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO measurement_equipment 
            (equipment_id, equipment_name, equipment_type, manufacturer, model_no, serial_no,
             calibration_date, next_calibration_date, calibration_cycle, location, status, responsible_person)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, equipment)
        print("    ✅ 측정 장비 2개")
        
        conn.commit()
        print("  ✅ 샘플 데이터 추가 완료")
        
    except Exception as e:
        print(f"  ❌ 샘플 데이터 추가 중 오류: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_config_file():
    """config.yaml 파일 생성"""
    print("\n⚙️ 설정 파일 생성 중...")
    
    config_content = '''# Smart MES-ERP System Configuration V1.1
# 시스템 설정 파일

# 시스템 기본 설정
system:
  name: Smart MES-ERP
  version: "1.1.0"
  language: ko
  update_interval: 2000  # 실시간 업데이트 주기 (밀리초)

# 모듈 활성화 설정
modules:
  mes: true          # MES (생산관리)
  inventory: true    # 재고관리
  purchase: true     # 구매관리
  sales: true        # 영업관리 (V1.0)
  accounting: true   # 회계관리
  quality: true      # 품질관리 (V1.1)

# 인증 설정
authentication:
  enabled: true           # 로그인 기능 사용 여부
  session_timeout: 30     # 세션 타임아웃 (분)
  password_policy:
    min_length: 8
    require_special: true
    require_number: true

# 데이터베이스 설정
database:
  path: data/database.db  # SQLite 데이터베이스 파일 경로
  backup_enabled: true
  backup_interval: daily

# 로깅 설정
logging:
  level: INFO             # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
  file: logs/app.log      # 로그 파일 경로
  max_size: 10485760      # 최대 파일 크기 (10MB)
  backup_count: 5

# 백업 설정
backup:
  enabled: true           # 자동 백업 사용
  interval: daily         # 백업 주기 (daily, weekly, monthly)
  path: backups/          # 백업 파일 저장 경로
  retention: 30           # 백업 보관 기간 (일)

# 영업관리 설정 (V1.0)
sales:
  quote_validity_days: 30    # 견적서 기본 유효기간
  auto_quote_number: true    # 자동 견적번호 생성
  customer_grades:           # 고객 등급별 할인율
    VIP: 15
    Gold: 10
    Silver: 5
    Bronze: 0

# 품질관리 설정 (V1.1)
quality:
  default_sampling_rate: 10      # 기본 샘플링 비율 (%)
  target_defect_rate: 2.0        # 목표 불량률 (%)
  spc_rules:                     # SPC 관리도 규칙
    - rule1  # 1점이 관리한계 벗어남
    - rule2  # 연속 7점이 중심선 한쪽
  calibration_reminder_days: 30  # 교정 예정 알림 (일)

# 알림 설정
notifications:
  enabled: true
  channels:
    - dashboard  # 대시보드 알림
    - email      # 이메일 알림 (추후 구현)
  triggers:
    - low_stock           # 재고 부족
    - quality_issue       # 품질 이슈
    - calibration_due     # 교정 예정
    - quote_expiry        # 견적 만료 임박

# 성능 설정
performance:
  cache_enabled: true
  cache_timeout: 300  # 캐시 유효시간 (초)
  max_records_per_page: 100
  chart_data_points: 50

# 보안 설정
security:
  session_key: auto  # 자동 생성
  secure_cookie: true
  max_login_attempts: 5
  lockout_duration: 30  # 분
'''
    
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("  ✅ config.yaml 생성 완료")

def create_requirements_file():
    """requirements.txt 파일 생성/업데이트"""
    print("\n📋 requirements.txt 생성 중...")
    
    requirements_content = '''# Smart MES-ERP System Requirements V1.1
# Python 3.8+

# Core Framework
dash==2.14.0
dash-bootstrap-components==1.5.0
dash-core-components==2.0.0
dash-html-components==2.0.0
dash-table==5.0.0

# Plotting
plotly==5.17.0

# Web Server
Flask==2.2.5
Werkzeug==2.2.3

# Data Processing
pandas==2.0.3
numpy==1.24.3
scipy==1.10.1  # V1.1 품질관리 SPC 분석용

# Database
# SQLite3 is included in Python standard library

# Configuration
PyYAML==6.0.1

# Date/Time
python-dateutil==2.8.2

# Excel Export
openpyxl==3.1.2
xlsxwriter==3.1.3

# Development Tools
python-dotenv==1.0.0

# Security
cryptography==41.0.4

# Logging
colorlog==6.7.0

# Testing (optional)
pytest==7.4.3
pytest-cov==4.1.0
'''
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    print("  ✅ requirements.txt 생성 완료")

def create_batch_files():
    """실행 배치 파일 생성"""
    print("\n🚀 실행 파일 생성 중...")
    
    # Windows 배치 파일
    bat_content = '''@echo off
echo Starting Smart MES-ERP V1.1...
echo.

REM 가상환경 활성화 (있는 경우)
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate
)

REM 필요 패키지 확인
python -c "import dash" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM 앱 실행
echo Launching application...
python app.py

pause
'''
    
    with open('run.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print("  ✅ run.bat (Windows)")
    
    # Linux/Mac 쉘 스크립트
    sh_content = '''#!/bin/bash
echo "Starting Smart MES-ERP V1.1..."
echo

# 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 필요 패키지 확인
python -c "import dash" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# 앱 실행
echo "Launching application..."
python app.py
'''
    
    with open('run.sh', 'w', encoding='utf-8') as f:
        f.write(sh_content)
    os.chmod('run.sh', 0o755)  # 실행 권한 부여
    print("  ✅ run.sh (Linux/Mac)")

def create_readme_file():
    """간단한 README 파일 생성"""
    print("\n📄 README 파일 생성 중...")
    
    readme_content = '''# Smart MES-ERP V1.1

## 빠른 시작

1. **요구사항 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **앱 실행**
   - Windows: `run.bat` 더블클릭
   - Linux/Mac: `./run.sh`
   - 또는: `python app.py`

3. **접속**
   - URL: http://localhost:8050
   - ID: admin / PW: admin123

## 모듈 구성
- ✅ MES (생산관리)
- ✅ 재고관리
- ✅ 구매관리
- ✅ 영업관리 (V1.0)
- ✅ 회계관리
- ✅ 품질관리 (V1.1)

## 문제 해결
- 포트 충돌 시: app.py의 포트 번호 변경
- 모듈 오류 시: `pip install -r requirements.txt` 재실행

## 문의
- Email: support@smart-mes-erp.com
- Documentation: docs/README_V1.1.md
'''
    
    with open('README_QUICK.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("  ✅ README_QUICK.md 생성 완료")

def show_completion_message():
    """완료 메시지 표시"""
    print("\n" + "=" * 70)
    print("✅ Smart MES-ERP V1.1 통합 설정 완료!")
    print("=" * 70)
    
    print("\n📊 설치 요약:")
    print("  • 6개 모듈 설치 완료 (MES, 재고, 구매, 영업, 회계, 품질)")
    print("  • 데이터베이스 초기화 완료")
    print("  • 샘플 데이터 추가 완료")
    print("  • 설정 파일 생성 완료")
    
    print("\n🎯 다음 단계:")
    print("  1. 필요 패키지 설치:")
    print("     pip install -r requirements.txt")
    print()
    print("  2. 앱 실행:")
    print("     python app.py")
    print("     또는")
    print("     run.bat (Windows) / ./run.sh (Linux/Mac)")
    print()
    print("  3. 웹 브라우저에서 접속:")
    print("     http://localhost:8050")
    print()
    print("  4. 로그인:")
    print("     ID: admin / PW: admin123")
    
    print("\n📚 추가 정보:")
    print("  • 상세 문서: docs/README_V1.1.md")
    print("  • 빠른 시작: README_QUICK.md")
    print("  • 로그 파일: logs/app.log")
    
    print("\n🚀 새로운 기능 (V1.1):")
    print("  📋 품질관리 모듈")
    print("    - 입고/공정/출하 검사")
    print("    - 불량 관리 및 분석")
    print("    - SPC (통계적 공정 관리)")
    print("    - 품질 성적서 발행")
    print("    - 측정 장비 관리")
    
    print("\n💡 팁:")
    print("  • F5: 화면 새로고침")
    print("  • F11: 전체화면 모드")
    print("  • Ctrl+Shift+I: 개발자 도구")
    
    print("\n" + "=" * 70)
    print("Happy Manufacturing! 🏭")
    print("=" * 70)

def main():
    """메인 실행 함수"""
    # 헤더 출력
    print_header()
    
    # 요구사항 확인
    if not check_requirements():
        print("\n❌ 요구사항을 먼저 설치해주세요.")
        print("pip install dash dash-bootstrap-components pandas plotly pyyaml numpy scipy")
        sys.exit(1)
    
    try:
        # 디렉토리 구조 생성
        create_directory_structure()
        
        # 모듈 초기화 파일 생성
        create_module_init_files()
        
        # 데이터베이스 초기화
        initialize_database()
        
        # 샘플 데이터 추가
        insert_sample_data()
        
        # 설정 파일 생성
        create_config_file()
        
        # requirements.txt 생성
        create_requirements_file()
        
        # 실행 파일 생성
        create_batch_files()
        
        # README 생성
        create_readme_file()
        
        # 완료 메시지
        show_completion_message()
        
    except Exception as e:
        print(f"\n❌ 설정 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 프로젝트 루트로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # 메인 실행
    main()
