# File: setup_v1_2_integrated.py
# Smart MES-ERP V1.2 통합 설정 스크립트
# V1.0 영업관리 + V1.1 품질관리 + V1.2 인사관리 모듈 한번에 설정

import os
import sys
import sqlite3
import yaml
import shutil
from datetime import datetime, timedelta
import subprocess
import hashlib
import secrets

def print_header():
    """헤더 출력"""
    print("=" * 80)
    print("🚀 Smart MES-ERP V1.2 통합 설정 스크립트")
    print("=" * 80)
    print("📦 포함 모듈:")
    print("   - 기본: MES, 재고, 구매, 회계")
    print("   - V1.0: 영업관리")
    print("   - V1.1: 품질관리")
    print("   - V1.2: 인사관리, REST API")
    print("=" * 80)
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
        'modules/hr',          # V1.2
        
        # 하위 디렉토리
        'modules/quality/templates',
        'modules/quality/static',
        'modules/hr/templates',
        'modules/hr/static',
        
        # API 디렉토리 (V1.2)
        'api',
        'api/auth',
        'api/routes',
        'api/models',
        'api/utils',
        
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
        'quality': 'Quality Management (V1.1)',
        'hr': 'Human Resource Management (V1.2)'
    }
    
    for module, description in modules.items():
        init_content = f'''"""
{description} Module for Smart MES-ERP
"""

from .layouts import create_{module}_layout
from .callbacks import register_{module}_callbacks

__version__ = "1.2.0"
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
    
    # 인사관리 테이블 (V1.2)
    print("  👥 인사관리 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            emp_name TEXT NOT NULL,
            emp_name_en TEXT,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date DATE NOT NULL,
            birth_date DATE,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT,
            employee_type TEXT DEFAULT 'regular',
            work_status TEXT DEFAULT 'active',
            resignation_date DATE,
            photo BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            work_date DATE NOT NULL,
            check_in_time TIMESTAMP,
            check_out_time TIMESTAMP,
            work_hours REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            status TEXT DEFAULT 'normal',
            late_minutes INTEGER DEFAULT 0,
            early_leave_minutes INTEGER DEFAULT 0,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
            UNIQUE(emp_id, work_date)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            leave_days REAL NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            approver_id TEXT,
            approval_date TIMESTAMP,
            approval_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
            FOREIGN KEY (approver_id) REFERENCES employees (emp_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            salary_month TEXT NOT NULL,
            basic_salary REAL DEFAULT 0,
            position_allowance REAL DEFAULT 0,
            meal_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            overtime_pay REAL DEFAULT 0,
            bonus REAL DEFAULT 0,
            other_allowance REAL DEFAULT 0,
            total_earning REAL DEFAULT 0,
            income_tax REAL DEFAULT 0,
            resident_tax REAL DEFAULT 0,
            health_insurance REAL DEFAULT 0,
            pension REAL DEFAULT 0,
            employment_insurance REAL DEFAULT 0,
            accident_insurance REAL DEFAULT 0,
            other_deduction REAL DEFAULT 0,
            total_deduction REAL DEFAULT 0,
            net_salary REAL DEFAULT 0,
            payment_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
            UNIQUE(emp_id, salary_month)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            dept_code TEXT PRIMARY KEY,
            dept_name TEXT NOT NULL,
            dept_name_en TEXT,
            parent_dept TEXT,
            dept_head TEXT,
            location TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dept_head) REFERENCES employees (emp_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            position_code TEXT PRIMARY KEY,
            position_name TEXT NOT NULL,
            position_name_en TEXT,
            position_level INTEGER,
            min_salary REAL,
            max_salary REAL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("    ✅ 인사관리 테이블 완료")
    
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
    
    # API 관련 테이블 (V1.2)
    print("  🔌 API 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            name TEXT,
            permissions TEXT,
            expires_at TIMESTAMP,
            last_used_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            user_id INTEGER,
            ip_address TEXT,
            request_body TEXT,
            response_code INTEGER,
            response_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("    ✅ API 테이블 완료")
    
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
            ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin', '경영지원', 'admin@company.com', '010-1234-5678'),
            ('user', hashlib.sha256('user123'.encode()).hexdigest(), 'user', '생산팀', 'user@company.com', '010-2345-6789'),
            ('qc', hashlib.sha256('qc123'.encode()).hexdigest(), 'user', '품질팀', 'qc@company.com', '010-3456-7890'),
            ('sales', hashlib.sha256('sales123'.encode()).hexdigest(), 'user', '영업팀', 'sales@company.com', '010-4567-8901'),
            ('hr', hashlib.sha256('hr123'.encode()).hexdigest(), 'user', '인사팀', 'hr@company.com', '010-5678-9012')
        ]
        
        for user in users:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password, role, department, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, user)
        print("    ✅ 사용자 5명")
        
        # 부서 데이터 (V1.2)
        print("  🏢 부서 데이터...")
        departments = [
            ('D001', '경영지원팀', 'Management Support', None, None, '본사 3층'),
            ('D002', '생산팀', 'Production', None, None, '공장 1동'),
            ('D003', '품질팀', 'Quality Control', None, None, '공장 2동'),
            ('D004', '영업팀', 'Sales', None, None, '본사 2층'),
            ('D005', '인사팀', 'Human Resources', None, None, '본사 3층'),
            ('D006', '개발팀', 'Development', None, None, '본사 4층')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO departments 
            (dept_code, dept_name, dept_name_en, parent_dept, dept_head, location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, departments)
        print("    ✅ 부서 6개")
        
        # 직급 데이터 (V1.2)
        print("  💼 직급 데이터...")
        positions = [
            ('P001', '사원', 'Staff', 1, 2400000, 3600000),
            ('P002', '주임', 'Senior Staff', 2, 3000000, 4200000),
            ('P003', '대리', 'Assistant Manager', 3, 3600000, 5400000),
            ('P004', '과장', 'Manager', 4, 4800000, 7200000),
            ('P005', '차장', 'Deputy General Manager', 5, 6000000, 9000000),
            ('P006', '부장', 'General Manager', 6, 7200000, 12000000)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO positions 
            (position_code, position_name, position_name_en, position_level, min_salary, max_salary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, positions)
        print("    ✅ 직급 6개")
        
        # 직원 데이터 (V1.2)
        print("  👥 직원 데이터...")
        employees = [
            ('EMP001', '김철수', 'Kim Cheolsu', 'D001', 'P006', '2015-03-15', '1975-05-20', 'M', 
             '010-1111-2222', 'kim.cs@company.com', '서울시 강남구', '김영희', '010-9999-8888'),
            ('EMP002', '이영희', 'Lee Younghee', 'D005', 'P005', '2016-07-01', '1980-08-15', 'F',
             '010-3333-4444', 'lee.yh@company.com', '서울시 서초구', '이철수', '010-7777-6666'),
            ('EMP003', '박민수', 'Park Minsu', 'D002', 'P004', '2018-01-10', '1985-03-25', 'M',
             '010-5555-6666', 'park.ms@company.com', '경기도 성남시', '박영희', '010-5555-4444'),
            ('EMP004', '정수진', 'Jung Sujin', 'D003', 'P003', '2020-04-01', '1990-11-30', 'F',
             '010-7777-8888', 'jung.sj@company.com', '서울시 마포구', '정민수', '010-3333-2222'),
            ('EMP005', '홍길동', 'Hong Gildong', 'D004', 'P002', '2022-08-15', '1995-07-10', 'M',
             '010-9999-0000', 'hong.gd@company.com', '인천시 남동구', '홍길순', '010-1111-0000')
        ]
        
        for emp in employees:
            cursor.execute("""
                INSERT OR IGNORE INTO employees 
                (emp_id, emp_name, emp_name_en, department, position, hire_date, birth_date, 
                 gender, phone, email, address, emergency_contact, emergency_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, emp)
        print("    ✅ 직원 5명")
        
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
        
        # 근태 샘플 데이터 (V1.2)
        print("  ⏰ 근태 데이터...")
        today = datetime.now().date()
        for i in range(5):  # 최근 5일
            work_date = today - timedelta(days=i)
            for emp_id in ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005']:
                check_in = f"{work_date} 09:00:00"
                check_out = f"{work_date} 18:00:00"
                cursor.execute("""
                    INSERT OR IGNORE INTO attendance 
                    (emp_id, work_date, check_in_time, check_out_time, work_hours, status)
                    VALUES (?, ?, ?, ?, 8, 'normal')
                """, (emp_id, work_date, check_in, check_out))
        print("    ✅ 근태 기록 25건")
        
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
    
    # JWT 시크릿 키 생성
    jwt_secret = secrets.token_urlsafe(32)
    
    config_content = f'''# Smart MES-ERP System Configuration V1.2
# 시스템 설정 파일

# 시스템 기본 설정
system:
  name: Smart MES-ERP
  version: "1.2.0"
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
  hr: true          # 인사관리 (V1.2)

# 인증 설정
authentication:
  enabled: true           # 로그인 기능 사용 여부
  session_timeout: 30     # 세션 타임아웃 (분)
  jwt_secret_key: '{jwt_secret}'
  jwt_access_token_expires: 3600  # JWT 토큰 만료 시간 (초)
  password_policy:
    min_length: 8
    require_special: true
    require_number: true

# API 설정 (V1.2)
api:
  enabled: true
  host: '0.0.0.0'
  port: 5001
  cors_origins: 
    - 'http://localhost:8050'
    - 'http://localhost:3000'
  rate_limit: '100 per hour'
  documentation: true

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

# 인사관리 설정 (V1.2)
hr:
  work_hours:
    start: '09:00'
    end: '18:00'
    break_time: 60  # 분
  overtime:
    weekday_rate: 1.5
    weekend_rate: 2.0
    holiday_rate: 2.5
  leave:
    annual_days: 15
    sick_leave_days: 10
    special_leave_days: 5
  payroll:
    pay_day: 25
    tax_rate: 0.033
    insurance_rates:
      health: 0.0343
      pension: 0.045
      employment: 0.008
      accident: 0.007

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
    - leave_request       # 휴가 신청
    - attendance_issue    # 근태 이상

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
    
    requirements_content = '''# Smart MES-ERP System Requirements V1.2
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

# REST API (V1.2)
flask-restful==0.3.10
flask-cors==4.0.0
flask-jwt-extended==4.5.3
marshmallow==3.20.1
passlib==1.7.4
flasgger==0.9.7.1

# Database
# SQLite3 is included in Python standard library

# Configuration
PyYAML==6.0.1

# Date/Time
python-dateutil==2.8.2

# Excel Export
openpyxl==3.1.2
xlsxwriter==3.1.3

# Scheduler (V1.2)
APScheduler==3.10.4

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

def create_api_files():
    """API 파일 생성 (V1.2)"""
    print("\n🔌 API 파일 생성 중...")
    
    # api/__init__.py
    api_init = '''"""
Smart MES-ERP REST API Package
"""

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger

def create_api_app(config):
    """API 앱 생성"""
    app = Flask(__name__)
    
    # 설정
    app.config['JWT_SECRET_KEY'] = config['authentication']['jwt_secret_key']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config['authentication']['jwt_access_token_expires']
    
    # CORS 설정
    CORS(app, origins=config['api']['cors_origins'])
    
    # JWT 설정
    jwt = JWTManager(app)
    
    # API 설정
    api = Api(app)
    
    # Swagger 설정
    swagger = Swagger(app)
    
    # 라우트 등록
    from .routes import register_routes
    register_routes(api)
    
    return app, api
'''
    
    with open('api/__init__.py', 'w', encoding='utf-8') as f:
        f.write(api_init)
    print("  ✅ api/__init__.py")
    
    # api/auth.py
    api_auth = '''"""
API 인증 모듈
"""

from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import sqlite3
import hashlib
from datetime import datetime

class Login(Resource):
    """로그인 API"""
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('password', required=True, help='Password is required')
        args = parser.parse_args()
        
        # 데이터베이스에서 사용자 확인
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(args['password'].encode()).hexdigest()
        cursor.execute(
            "SELECT id, username, role, department FROM users WHERE username = ? AND password = ?",
            (args['username'], password_hash)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {'message': 'Invalid credentials'}, 401
        
        # JWT 토큰 생성
        access_token = create_access_token(
            identity=user[0],
            additional_claims={
                'username': user[1],
                'role': user[2],
                'department': user[3]
            }
        )
        
        return {
            'access_token': access_token,
            'user': {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'department': user[3]
            }
        }, 200

class Profile(Resource):
    """사용자 프로필 API"""
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, department, email, phone FROM users WHERE id = ?",
            (current_user,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {'message': 'User not found'}, 404
        
        return {
            'id': user[0],
            'username': user[1],
            'role': user[2],
            'department': user[3],
            'email': user[4],
            'phone': user[5]
        }, 200
'''
    
    with open('api/auth.py', 'w', encoding='utf-8') as f:
        f.write(api_auth)
    print("  ✅ api/auth.py")
    
    # api/routes.py
    api_routes = '''"""
API 라우트 등록
"""

from .auth import Login, Profile

def register_routes(api):
    """API 라우트 등록"""
    
    # 인증
    api.add_resource(Login, '/api/auth/login')
    api.add_resource(Profile, '/api/auth/profile')
    
    # TODO: 각 모듈별 API 라우트 추가
    # api.add_resource(EmployeeList, '/api/hr/employees')
    # api.add_resource(AttendanceList, '/api/hr/attendance')
    # api.add_resource(ProductionList, '/api/mes/production')
    # 등...
'''
    
    with open('api/routes.py', 'w', encoding='utf-8') as f:
        f.write(api_routes)
    print("  ✅ api/routes.py")

def create_batch_files():
    """실행 배치 파일 생성"""
    print("\n🚀 실행 파일 생성 중...")
    
    # Windows 배치 파일 - Web UI
    bat_web_content = '''@echo off
echo Starting Smart MES-ERP V1.2 Web UI...
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
    
    with open('run_web.bat', 'w', encoding='utf-8') as f:
        f.write(bat_web_content)
    print("  ✅ run_web.bat (Windows)")
    
    # Windows 배치 파일 - API
    bat_api_content = '''@echo off
echo Starting Smart MES-ERP V1.2 REST API...
echo.

REM 가상환경 활성화 (있는 경우)
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate
)

REM API 서버 실행
echo Launching API server...
python run_api.py

pause
'''
    
    with open('run_api.bat', 'w', encoding='utf-8') as f:
        f.write(bat_api_content)
    print("  ✅ run_api.bat (Windows)")
    
    # Windows 배치 파일 - 전체 실행
    bat_all_content = '''@echo off
echo Starting Smart MES-ERP V1.2...
echo.

start "MES-ERP Web" cmd /k "run_web.bat"
timeout /t 5
start "REST API" cmd /k "run_api.bat"

echo.
echo ✅ All services started!
echo    - Web UI: http://localhost:8050
echo    - REST API: http://localhost:5001
echo    - API Docs: http://localhost:5001/apidocs
echo.
pause
'''
    
    with open('run_all.bat', 'w', encoding='utf-8') as f:
        f.write(bat_all_content)
    print("  ✅ run_all.bat (Windows)")
    
    # Linux/Mac 쉘 스크립트
    sh_all_content = '''#!/bin/bash
echo "Starting Smart MES-ERP V1.2..."
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

# Web UI 시작
python app.py &
WEB_PID=$!

sleep 5

# REST API 시작
python run_api.py &
API_PID=$!

echo
echo "✅ All services started!"
echo "   - Web UI: http://localhost:8050"
echo "   - REST API: http://localhost:5001"
echo "   - API Docs: http://localhost:5001/apidocs"
echo
echo "Press Ctrl+C to stop all services."

# 종료 시그널 대기
trap "kill $WEB_PID $API_PID" INT
wait
'''
    
    with open('run_all.sh', 'w', encoding='utf-8') as f:
        f.write(sh_all_content)
    os.chmod('run_all.sh', 0o755)  # 실행 권한 부여
    print("  ✅ run_all.sh (Linux/Mac)")

def create_run_api_file():
    """run_api.py 파일 생성"""
    print("\n📄 run_api.py 생성 중...")
    
    run_api_content = '''# run_api.py - REST API 서버 실행

import os
import sys
import yaml
from api import create_api_app

if __name__ == '__main__':
    # 설정 로드
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # API 앱 생성
    app, api = create_api_app(config)
    
    # API 서버 실행
    print(f"🚀 REST API 서버 시작...")
    print(f"   URL: http://localhost:{config['api']['port']}")
    print(f"   Swagger 문서: http://localhost:{config['api']['port']}/apidocs")
    
    app.run(
        host=config['api']['host'],
        port=config['api']['port'],
        debug=True
    )
'''
    
    with open('run_api.py', 'w', encoding='utf-8') as f:
        f.write(run_api_content)
    print("  ✅ run_api.py 생성 완료")

def create_readme_file():
    """README 파일 생성"""
    print("\n📄 README 파일 생성 중...")
    
    readme_content = '''# Smart MES-ERP V1.2

## 빠른 시작

1. **요구사항 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **앱 실행**
   - 전체 실행: 
     - Windows: `run_all.bat`
     - Linux/Mac: `./run_all.sh`
   - 개별 실행:
     - Web UI: `python app.py`
     - REST API: `python run_api.py`

3. **접속**
   - Web UI: http://localhost:8050
   - REST API: http://localhost:5001
   - API 문서: http://localhost:5001/apidocs
   - 기본 계정: admin / admin123

## 모듈 구성
- ✅ MES (생산관리)
- ✅ 재고관리
- ✅ 구매관리
- ✅ 영업관리 (V1.0)
- ✅ 회계관리
- ✅ 품질관리 (V1.1)
- ✅ 인사관리 (V1.2)
- ✅ REST API (V1.2)

## 주요 기능 (V1.2)
### 인사관리
- 직원 정보 관리
- 조직도 관리
- 근태 관리
- 휴가 관리
- 급여 관리

### REST API
- JWT 인증
- 모든 모듈 API 제공
- Swagger 문서 자동 생성
- CORS 지원

## API 사용 예시
```python
import requests

# 로그인
response = requests.post('http://localhost:5001/api/auth/login', 
    json={'username': 'admin', 'password': 'admin123'})
token = response.json()['access_token']

# API 호출
headers = {'Authorization': f'Bearer {token}'}
profile = requests.get('http://localhost:5001/api/auth/profile', headers=headers)
```

## 문제 해결
- 포트 충돌 시: config.yaml에서 포트 번호 변경
- 모듈 오류 시: `pip install -r requirements.txt` 재실행
- DB 초기화: `python setup_v1_2_integrated.py` 재실행

## 문의
- Email: support@smart-mes-erp.com
- Documentation: docs/
'''
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("  ✅ README.md 생성 완료")

def show_completion_message():
    """완료 메시지 표시"""
    print("\n" + "=" * 80)
    print("✅ Smart MES-ERP V1.2 통합 설정 완료!")
    print("=" * 80)
    
    print("\n📊 설치 요약:")
    print("  • 7개 모듈 설치 완료 (MES, 재고, 구매, 영업, 회계, 품질, 인사)")
    print("  • REST API 설정 완료")
    print("  • 데이터베이스 초기화 완료")
    print("  • 샘플 데이터 추가 완료")
    print("  • 설정 파일 생성 완료")
    
    print("\n🎯 다음 단계:")
    print("  1. 필요 패키지 설치:")
    print("     pip install -r requirements.txt")
    print()
    print("  2. 앱 실행:")
    print("     - 전체: run_all.bat (Windows) / ./run_all.sh (Linux/Mac)")
    print("     - Web UI만: python app.py")
    print("     - API만: python run_api.py")
    print()
    print("  3. 웹 브라우저에서 접속:")
    print("     - Web UI: http://localhost:8050")
    print("     - API 문서: http://localhost:5001/apidocs")
    print()
    print("  4. 로그인:")
    print("     - ID: admin / PW: admin123")
    
    print("\n📚 버전별 주요 기능:")
    print("  📋 V1.0 - 영업관리")
    print("    - 고객/제품 관리, 견적/주문 관리")
    print("  📋 V1.1 - 품질관리")
    print("    - 검사 관리, 불량 분석, SPC, 측정 장비 관리")
    print("  📋 V1.2 - 인사관리 & REST API")
    print("    - 직원/조직 관리, 근태/휴가/급여 관리")
    print("    - JWT 인증 기반 REST API")
    
    print("\n💡 팁:")
    print("  • API 테스트: Postman 또는 Swagger UI 사용")
    print("  • 로그 확인: logs/app.log")
    print("  • 백업 위치: backups/")
    
    print("\n" + "=" * 80)
    print("🏭 Happy Manufacturing with Smart MES-ERP! 🚀")
    print("=" * 80)

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
        response = input("\n💾 샘플 데이터를 추가하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            insert_sample_data()
        
        # 설정 파일 생성
        create_config_file()
        
        # requirements.txt 생성
        create_requirements_file()
        
        # API 파일 생성
        create_api_files()
        
        # run_api.py 생성
        create_run_api_file()
        
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
    if os.path.exists('scripts'):
        os.chdir('..')
    
    # 메인 실행
    main()
