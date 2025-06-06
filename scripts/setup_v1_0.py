# File: scripts/setup_v1_0.py
# Smart MES-ERP V1.0 영업관리 모듈 설정 스크립트

import os
import sys
import sqlite3
from datetime import datetime

def setup_v1_0():
    """V1.0 영업관리 모듈 설정"""
    print("🚀 Smart MES-ERP V1.0 설정 시작")
    print("=" * 50)
    
    # 1. 디렉토리 구조 생성
    print("\n1. 디렉토리 구조 생성 중...")
    directories = [
        'modules/sales',
        'data',
        'logs', 
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")
    
    # 2. 영업관리 모듈 파일 생성
    print("\n2. 영업관리 모듈 파일 생성 중...")
    
    # __init__.py
    init_content = '''from .layouts import create_sales_layout
from .callbacks import register_sales_callbacks

__all__ = ['create_sales_layout', 'register_sales_callbacks']
'''
    with open('modules/sales/__init__.py', 'w', encoding='utf-8') as f:
        f.write(init_content)
    print("  ✅ modules/sales/__init__.py")
    
    # 3. 데이터베이스 테이블 생성
    print("\n3. 데이터베이스 테이블 생성 중...")
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 영업관리 테이블들
    tables = {
        'customers': '''
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
        ''',
        'quotations': '''
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
        ''',
        'quotation_details': '''
            CREATE TABLE IF NOT EXISTS quotation_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_number TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                product_code TEXT,
                product_name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (quote_number) REFERENCES quotations (quote_number)
            )
        ''',
        'sales_orders': '''
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
        ''',
        'sales_order_details': '''
            CREATE TABLE IF NOT EXISTS sales_order_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                product_code TEXT,
                product_name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                amount REAL NOT NULL,
                delivered_qty INTEGER DEFAULT 0,
                FOREIGN KEY (order_number) REFERENCES sales_orders (order_number)
            )
        ''',
        'sales_activities': '''
            CREATE TABLE IF NOT EXISTS sales_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_date DATE NOT NULL,
                activity_type TEXT NOT NULL,
                customer_code TEXT,
                contact_person TEXT,
                subject TEXT,
                description TEXT,
                result TEXT,
                next_action TEXT,
                next_action_date DATE,
                sales_person_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
                FOREIGN KEY (sales_person_id) REFERENCES users (id)
            )
        ''',
        'sales_opportunities': '''
            CREATE TABLE IF NOT EXISTS sales_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_name TEXT NOT NULL,
                customer_code TEXT NOT NULL,
                estimated_amount REAL DEFAULT 0,
                probability INTEGER DEFAULT 50,
                expected_close_date DATE,
                stage TEXT DEFAULT 'prospecting',
                source TEXT,
                competitor TEXT,
                sales_person_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
                FOREIGN KEY (sales_person_id) REFERENCES users (id)
            )
        ''',
        'products': '''
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
        '''
    }
    
    for table_name, create_sql in tables.items():
        cursor.execute(create_sql)
        print(f"  ✅ {table_name} 테이블")
    
    # 4. 기본 데이터 추가
    print("\n4. 기본 데이터 추가 중...")
    
    # 기본 고객 데이터
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ('CUST001', '(주)테크놀로지', '123-45-67890', '김대표', '이부장', '02-1234-5678', 
             'lee@technology.co.kr', '서울시 강남구 테헤란로 123', 'VIP', 'NET30', 100000000),
            ('CUST002', '글로벌산업(주)', '234-56-78901', '박사장', '최과장', '031-987-6543',
             'choi@global.com', '경기도 수원시 영통구 월드컵로 456', 'Gold', 'NET60', 50000000),
            ('CUST003', '스마트제조', '345-67-89012', '정대표', '김대리', '032-555-1234',
             'kim@smart.kr', '인천시 남동구 논현로 789', 'Silver', 'NET30', 30000000)
        ]
        cursor.executemany("""
            INSERT INTO customers 
            (customer_code, customer_name, business_no, ceo_name, contact_person,
             phone, email, address, grade, payment_terms, credit_limit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, sample_customers)
        print(f"  ✅ {len(sample_customers)}개 고객 데이터")
    
    # 기본 제품 데이터
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('PROD001', 'Smart MES 시스템', 'Software', 'MES 솔루션 패키지', 50000000, 30000000),
            ('PROD002', 'ERP 통합 솔루션', 'Software', 'ERP 시스템 구축', 80000000, 50000000),
            ('PROD003', '자동화 제어시스템', 'Hardware', 'PLC 기반 자동화', 30000000, 18000000)
        ]
        cursor.executemany("""
            INSERT INTO products 
            (product_code, product_name, category, description, unit_price, cost_price, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, sample_products)
        print(f"  ✅ {len(sample_products)}개 제품 데이터")
    
    conn.commit()
    conn.close()
    
    # 5. config.yaml 업데이트
    print("\n5. config.yaml 업데이트 중...")
    
    config_content = '''# Smart MES-ERP System Configuration V1.0
# 시스템 설정 파일

# 시스템 기본 설정
system:
  name: Smart MES-ERP
  version: "1.0.0"
  language: ko
  update_interval: 2000  # 실시간 업데이트 주기 (밀리초)

# 모듈 활성화 설정
modules:
  mes: true          # MES (생산관리) - 활성화
  inventory: true    # 재고관리 - 활성화
  purchase: true     # 구매관리 - 활성화 
  sales: true        # 영업관리 - 활성화 (V1.0 신규)
  accounting: true   # 회계관리 - 활성화

# 인증 설정
authentication:
  enabled: true           # 로그인 기능 사용 여부
  session_timeout: 30     # 세션 타임아웃 (분)

# 데이터베이스 설정
database:
  path: data/database.db  # SQLite 데이터베이스 파일 경로

# 로깅 설정
logging:
  level: INFO             # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
  file: logs/app.log      # 로그 파일 경로

# 백업 설정
backup:
  enabled: true           # 자동 백업 사용
  interval: daily         # 백업 주기 (daily, weekly, monthly)
  path: backups/          # 백업 파일 저장 경로
  retention: 30           # 백업 보관 기간 (일)

# 영업관리 설정 (V1.0 신규)
sales:
  quote_validity_days: 30    # 견적서 기본 유효기간
  auto_quote_number: true    # 자동 견적번호 생성
  customer_grades:           # 고객 등급별 할인율
    VIP: 15
    Gold: 10  
    Silver: 5
    Bronze: 0
'''
    
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("  ✅ config.yaml 업데이트")
    
    # 6. 완료 메시지
    print("\n" + "=" * 50)
    print("✅ Smart MES-ERP V1.0 설정 완료!")
    print("\n🎉 새로운 기능:")
    print("  📈 영업관리 모듈")
    print("    - 견적서 관리")
    print("    - 수주 관리") 
    print("    - 고객 관리")
    print("    - 영업 분석")
    print("    - CRM 기능")
    
    print("\n💡 다음 단계:")
    print("  1. python app.py 실행")
    print("  2. http://localhost:8050 접속")
    print("  3. 영업관리 메뉴 확인")
    print("  4. admin/admin123 로그인")
    
    print("\n📊 구현 완료 모듈: 5/8")
    print("  ✅ MES (생산관리)")
    print("  ✅ 재고관리")
    print("  ✅ 구매관리") 
    print("  ✅ 회계관리")
    print("  ✅ 영업관리 (신규)")
    
    print("\n🚧 다음 개발 예정:")
    print("  📅 V1.1: 품질관리")
    print("  📅 V1.2: 인사관리")
    print("  📅 V1.3: 설비관리")

def check_requirements():
    """필요 조건 확인"""
    print("🔍 시스템 요구사항 확인 중...")
    
    # Python 버전 확인
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        return False
    print(f"  ✅ Python {python_version.major}.{python_version.minor}")
    
    # 필수 모듈 확인
    required_modules = [
        'dash', 'dash_bootstrap_components', 'pandas', 
        'plotly', 'sqlite3', 'yaml'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"  ❌ {module}")
    
    if missing_modules:
        print(f"\n❌ 누락된 모듈: {', '.join(missing_modules)}")
        print("pip install -r requirements.txt 실행하세요.")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Smart MES-ERP V1.0 설정 도구")
    print("=" * 50)
    
    # 요구사항 확인
    if not check_requirements():
        sys.exit(1)
    
    # V1.0 설정 실행
    setup_v1_0()
    
    print("\n🎯 V1.0 설정이 완료되었습니다!")
    print("이제 영업관리 모듈을 사용할 수 있습니다.")
