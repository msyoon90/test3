# File: scripts/init_all_database.py

import sqlite3
import os
from datetime import datetime

def init_all_tables():
    """모든 테이블 초기화"""
    # data 폴더 생성
    os.makedirs('../data', exist_ok=True)
    
    conn = sqlite3.connect('../data/database.db')
    cursor = conn.cursor()
    
    print("🔧 전체 데이터베이스 초기화 시작...")
    
    # 1. 사용자 테이블
    print("\n1. 기본 시스템 테이블 생성...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ users 테이블 생성")
    
    # 2. 작업 로그 테이블 (MES)
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
    print("  ✅ work_logs 테이블 생성")
    
    # 3. 시스템 설정 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ system_config 테이블 생성")
    
    # 4. 품목 마스터 테이블 (재고관리)
    print("\n2. 재고관리 테이블 생성...")
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
    
    # 5. 재고 이동 테이블
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
    print("  ✅ stock_movements 테이블 생성")
    
    # 6. 재고 조정 테이블
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
    print("  ✅ stock_adjustments 테이블 생성")
    
    # 7. 거래처 마스터 (구매관리)
    print("\n3. 구매관리 테이블 생성...")
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
    
    # 8. 발주서 헤더
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
            FOREIGN KEY (approved_by) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    print("  ✅ purchase_orders 테이블 생성")
    
    # 9. 발주서 상세
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
    print("  ✅ purchase_order_details 테이블 생성")
    
    # 10. 입고 예정
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
    print("  ✅ receiving_schedule 테이블 생성")
    
    # 11. 입고 검수
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
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (inspector_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ receiving_inspection 테이블 생성")
    
    # 12. 자동 발주 규칙
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
    print("  ✅ auto_po_rules 테이블 생성")
    
    # 13. 폼 템플릿 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            config TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ form_templates 테이블 생성")
    
    # 기본 관리자 계정 생성
    print("\n4. 기본 데이터 생성...")
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
        print("  ✅ 관리자 계정 생성 (admin/admin123)")
    
    # 기본 품목 데이터 추가
    cursor.execute("SELECT COUNT(*) FROM item_master")
    if cursor.fetchone()[0] == 0:
        sample_items = [
            ('ITEM001', '볼트 M10', '부품', 'EA', 100, 150, 500),
            ('ITEM002', '너트 M10', '부품', 'EA', 100, 200, 300),
            ('ITEM003', '철판 1.0T', '원자재', 'EA', 50, 75, 15000),
            ('ITEM004', '모터 DC24V', '부품', 'EA', 20, 25, 50000),
            ('ITEM005', '베어링 6201', '부품', 'EA', 50, 80, 3000),
            ('BOLT-M10', '볼트 M10x30', '부품', 'EA', 500, 750, 150),
            ('NUT-M10', '너트 M10', '부품', 'EA', 500, 800, 80),
            ('PLATE-1.0', '철판 1.0T', '원자재', 'EA', 50, 75, 15000),
            ('MOTOR-DC24', '모터 DC24V', '부품', 'EA', 20, 25, 85000),
            ('BEARING-6201', '베어링 6201', '부품', 'EA', 100, 150, 3500),
            ('OIL-10W30', '엔진오일 10W30', '소모품', 'L', 50, 60, 8000)
        ]
        cursor.executemany(
            "INSERT INTO item_master (item_code, item_name, category, unit, safety_stock, current_stock, unit_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample_items
        )
        print(f"  ✅ {len(sample_items)}개 기본 품목 추가")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 전체 데이터베이스 초기화 완료!")

if __name__ == "__main__":
    init_all_tables()