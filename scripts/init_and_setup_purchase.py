# File: scripts/init_and_setup_purchase.py

import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random

def get_db_path():
    """데이터베이스 경로 가져오기"""
    # 스크립트 위치에 따라 경로 조정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # 가능한 경로들 확인
    possible_paths = [
        os.path.join(parent_dir, 'data', 'database.db'),
        os.path.join(current_dir, '..', 'data', 'database.db'),
        'data/database.db',
        '../data/database.db'
    ]
    
    # 존재하는 경로 찾기
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ 데이터베이스 찾음: {path}")
            return path
    
    # 없으면 생성
    data_dir = os.path.join(parent_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'database.db')
    print(f"📁 새 데이터베이스 생성: {db_path}")
    return db_path

def init_all_tables(conn):
    """모든 필요한 테이블 생성"""
    cursor = conn.cursor()
    
    print("\n🔧 테이블 생성 시작...")
    
    # 1. 기본 시스템 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. MES 테이블
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
    
    # 3. 재고관리 테이블 - 중요!
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_master (
            item_code TEXT PRIMARY KEY,
            item_name TEXT NOT NULL,
            category TEXT,
            unit TEXT DEFAULT 'EA',
            safety_stock INTEGER DEFAULT 0,
            current_stock INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ item_master 테이블 생성")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movement_date DATE NOT NULL,
            movement_type TEXT NOT NULL,
            item_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            warehouse TEXT,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adjustment_date DATE NOT NULL,
            item_code TEXT NOT NULL,
            adjustment_type TEXT,
            before_qty INTEGER,
            after_qty INTEGER,
            difference INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    # 4. 구매관리 테이블
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
    print("  ✅ supplier_master 테이블 생성")
    
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
            FOREIGN KEY (supplier_code) REFERENCES supplier_master (supplier_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT NOT NULL,
            item_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            amount REAL NOT NULL,
            received_qty INTEGER DEFAULT 0,
            remarks TEXT,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receiving_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT NOT NULL,
            scheduled_date DATE NOT NULL,
            item_code TEXT NOT NULL,
            expected_qty INTEGER NOT NULL,
            received_qty INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receiving_inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receiving_date DATE NOT NULL,
            po_number TEXT NOT NULL,
            item_code TEXT NOT NULL,
            received_qty INTEGER NOT NULL,
            accepted_qty INTEGER NOT NULL,
            rejected_qty INTEGER DEFAULT 0,
            inspection_result TEXT,
            inspector_id INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto_po_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL,
            supplier_code TEXT NOT NULL,
            reorder_point INTEGER NOT NULL,
            order_qty INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (supplier_code) REFERENCES supplier_master (supplier_code)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            config TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("✅ 모든 테이블 생성 완료")

def add_basic_data(conn):
    """기본 데이터 추가"""
    cursor = conn.cursor()
    
    # 1. 기본 사용자
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
        print("✅ 관리자 계정 생성 (admin/admin123)")
    
    # 2. 기본 품목 데이터
    cursor.execute("SELECT COUNT(*) FROM item_master")
    if cursor.fetchone()[0] == 0:
        print("\n📦 기본 품목 추가 중...")
        sample_items = [
            ('BOLT-M10', '볼트 M10x30', '부품', 'EA', 500, 750, 150),
            ('BOLT-M12', '볼트 M12x40', '부품', 'EA', 300, 420, 200),
            ('NUT-M10', '너트 M10', '부품', 'EA', 500, 800, 80),
            ('NUT-M12', '너트 M12', '부품', 'EA', 300, 350, 100),
            ('PLATE-1.0', '철판 1.0T', '원자재', 'EA', 50, 75, 15000),
            ('PLATE-2.0', '철판 2.0T', '원자재', 'EA', 30, 45, 25000),
            ('MOTOR-DC24', '모터 DC24V', '부품', 'EA', 20, 25, 85000),
            ('MOTOR-AC220', '모터 AC220V', '부품', 'EA', 15, 18, 120000),
            ('BEARING-6201', '베어링 6201', '부품', 'EA', 100, 150, 3500),
            ('BEARING-6202', '베어링 6202', '부품', 'EA', 100, 80, 4500),
            ('OIL-10W30', '엔진오일 10W30', '소모품', 'L', 50, 60, 8000),
            ('GREASE-MP2', '구리스 MP2', '소모품', 'KG', 20, 25, 15000)
        ]
        
        for item in sample_items:
            try:
                cursor.execute("""
                    INSERT INTO item_master 
                    (item_code, item_name, category, unit, safety_stock, current_stock, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, item)
            except sqlite3.IntegrityError:
                pass  # 이미 존재하는 경우 무시
        
        print(f"  ✅ {len(sample_items)}개 품목 추가 완료")
    
    conn.commit()

def add_purchase_data(conn):
    """구매관리 샘플 데이터 추가"""
    cursor = conn.cursor()
    
    # 1. 거래처 데이터
    print("\n🏢 거래처 데이터 추가 중...")
    suppliers = [
        ('SUP001', '(주)한국부품', '123-45-67890', '김철수', '이영희', '02-1234-5678', 
         'purchase@kparts.com', '서울시 강남구 테헤란로 123', 'NET30', 7, 5),
        ('SUP002', '대한철강(주)', '234-56-78901', '박민수', '최지훈', '031-987-6543',
         'steel@daehan.co.kr', '경기도 안산시 공단로 456', 'NET60', 10, 4),
        ('SUP003', '글로벌모터스', '345-67-89012', '이상훈', '김미영', '032-555-1234',
         'motor@global.com', '인천시 남동구 산업로 789', 'NET30', 5, 5),
        ('SUP004', '정밀기계(주)', '456-78-90123', '정대표', '박과장', '051-777-8888',
         'sales@precision.kr', '부산시 사상구 공장로 321', 'CASH', 3, 3),
        ('SUP005', '소모품마트', '567-89-01234', '최사장', '김대리', '02-3333-4444',
         'order@supplies.com', '서울시 금천구 디지털로 999', 'NET30', 2, 4)
    ]
    
    for supplier in suppliers:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO supplier_master 
                (supplier_code, supplier_name, business_no, ceo_name, contact_person,
                 phone, email, address, payment_terms, lead_time, rating, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, supplier)
        except Exception as e:
            print(f"  오류: {supplier[0]} - {e}")
    
    print(f"  ✅ {len(suppliers)}개 거래처 추가 완료")
    
    # 2. 발주서 샘플 데이터
    print("\n📋 발주서 데이터 추가 중...")
    
    # 사용 가능한 품목 조회
    cursor.execute("SELECT item_code, unit_price FROM item_master")
    available_items = cursor.fetchall()
    
    po_count = 0
    for i in range(30, -1, -3):  # 3일 간격으로 30일치
        po_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 하루에 1-2건의 발주
        for j in range(random.randint(1, 2)):
            po_number = f"PO-{po_date.replace('-', '')}-{j+1:03d}"
            supplier_code = random.choice([s[0] for s in suppliers])
            delivery_date = (datetime.strptime(po_date, '%Y-%m-%d') + 
                           timedelta(days=random.randint(3, 10))).strftime('%Y-%m-%d')
            
            # 상태 결정
            if i > 20:
                status = 'completed'
            elif i > 10:
                status = random.choice(['approved', 'receiving', 'completed'])
            else:
                status = random.choice(['draft', 'pending', 'approved'])
            
            total_amount = 0
            
            try:
                # 발주서 헤더
                cursor.execute("""
                    INSERT OR IGNORE INTO purchase_orders
                    (po_number, po_date, supplier_code, delivery_date, warehouse,
                     total_amount, status, remarks, created_by)
                    VALUES (?, ?, ?, ?, 'wh1', 0, ?, '샘플 발주', 1)
                """, (po_number, po_date, supplier_code, delivery_date, status))
                
                # 발주 상세 (품목 2-4개)
                num_items = min(random.randint(2, 4), len(available_items))
                selected_items = random.sample(available_items, num_items)
                
                for item_code, unit_price in selected_items:
                    quantity = random.randint(10, 200)
                    amount = quantity * unit_price
                    total_amount += amount
                    
                    cursor.execute("""
                        INSERT INTO purchase_order_details
                        (po_number, item_code, quantity, unit_price, amount)
                        VALUES (?, ?, ?, ?, ?)
                    """, (po_number, item_code, quantity, unit_price, amount))
                
                # 총액 업데이트
                cursor.execute("""
                    UPDATE purchase_orders SET total_amount = ? 
                    WHERE po_number = ?
                """, (total_amount, po_number))
                
                po_count += 1
                
            except Exception as e:
                print(f"  발주서 생성 오류: {po_number} - {e}")
    
    print(f"  ✅ {po_count}개 발주서 추가 완료")
    
    # 3. 자동 발주 규칙
    print("\n⚙️ 자동 발주 규칙 추가 중...")
    
    auto_rules = [
        ('BOLT-M10', 'SUP001', 300, 500),
        ('NUT-M10', 'SUP001', 300, 500),
        ('MOTOR-DC24', 'SUP003', 10, 20),
        ('BEARING-6201', 'SUP004', 50, 100),
        ('OIL-10W30', 'SUP005', 30, 50)
    ]
    
    for rule in auto_rules:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO auto_po_rules
                (item_code, supplier_code, reorder_point, order_qty, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, rule)
        except:
            pass
    
    print(f"  ✅ {len(auto_rules)}개 자동 발주 규칙 추가 완료")
    
    conn.commit()

def main():
    """메인 실행 함수"""
    print("🚀 Smart MES-ERP 구매관리 모듈 설정")
    print("=" * 50)
    
    # 데이터베이스 경로 찾기
    db_path = get_db_path()
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    
    try:
        # 1. 테이블 생성
        init_all_tables(conn)
        
        # 2. 기본 데이터 추가
        add_basic_data(conn)
        
        # 3. 구매관리 데이터 추가
        add_purchase_data(conn)
        
        print("\n✅ 모든 설정 완료!")
        print("\n💡 이제 다음 명령으로 앱을 실행하세요:")
        print("   cd ..")
        print("   python app.py")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()