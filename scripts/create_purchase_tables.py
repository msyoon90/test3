# File: scripts/create_purchase_tables.py

import sqlite3
import os

def create_purchase_tables():
    """구매관리 관련 테이블 생성"""
    # data 폴더가 없으면 생성
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("구매관리 테이블 생성 중...")
    
    # 거래처 마스터
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
    
    # 발주서 헤더
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
    print("  ✅ purchase_orders 테이블 생성")
    
    # 발주서 상세
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
    
    # 입고 예정
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
    
    # 입고 검수
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
    print("  ✅ receiving_inspection 테이블 생성")
    
    # 자동 발주 규칙
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
    
    conn.commit()
    conn.close()
    print("\n✅ 구매관리 테이블 생성 완료!")

if __name__ == "__main__":
    create_purchase_tables()