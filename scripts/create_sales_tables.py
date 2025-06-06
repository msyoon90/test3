# File: scripts/create_sales_tables.py
# 영업관리 모듈 테이블 생성 스크립트

import sqlite3
import os

def create_sales_tables():
    """영업관리 관련 테이블 생성"""
    # data 폴더가 없으면 생성
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("영업관리 테이블 생성 중...")
    
    # 1. 고객 마스터
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
            grade TEXT DEFAULT 'Bronze',  -- VIP, Gold, Silver, Bronze
            payment_terms TEXT DEFAULT 'NET30',
            credit_limit REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ customers 테이블 생성")
    
    # 2. 견적서 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            quote_number TEXT PRIMARY KEY,
            quote_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            validity_date DATE NOT NULL,
            total_amount REAL DEFAULT 0,
            discount_rate REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',  -- draft, sent, reviewing, won, lost, expired
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
    print("  ✅ quotations 테이블 생성")
    
    # 3. 견적서 상세
    cursor.execute('''
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
    ''')
    print("  ✅ quotation_details 테이블 생성")
    
    # 4. 수주 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_orders (
            order_number TEXT PRIMARY KEY,
            order_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            quote_number TEXT,
            delivery_date DATE,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'received',  -- received, confirmed, in_production, ready_for_delivery, completed, cancelled
            payment_status TEXT DEFAULT 'pending',  -- pending, partial, completed
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
    print("  ✅ sales_orders 테이블 생성")
    
    # 5. 수주 상세
    cursor.execute('''
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
    ''')
    print("  ✅ sales_order_details 테이블 생성")
    
    # 6. 영업 활동
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date DATE NOT NULL,
            activity_type TEXT NOT NULL,  -- call, email, meeting, demo, follow_up
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
    ''')
    print("  ✅ sales_activities 테이블 생성")
    
    # 7. 영업 기회 (Opportunity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_name TEXT NOT NULL,
            customer_code TEXT NOT NULL,
            estimated_amount REAL DEFAULT 0,
            probability INTEGER DEFAULT 50,  -- 0-100%
            expected_close_date DATE,
            stage TEXT DEFAULT 'prospecting',  -- prospecting, qualification, proposal, negotiation, closed_won, closed_lost
            source TEXT,  -- referral, website, cold_call, exhibition, etc.
            competitor TEXT,
            sales_person_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (sales_person_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ sales_opportunities 테이블 생성")
    
    # 8. 제품 마스터 (영업용)
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
    print("  ✅ products 테이블 생성")
    
    # 9. 가격 정책
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL,
            customer_grade TEXT,  -- VIP, Gold, Silver, Bronze
            product_category TEXT,
            discount_rate REAL DEFAULT 0,
            min_quantity INTEGER DEFAULT 1,
            effective_date DATE NOT NULL,
            expiry_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ price_policies 테이블 생성")
    
    # 10. 배송 정보
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_number TEXT UNIQUE NOT NULL,
            order_number TEXT NOT NULL,
            delivery_date DATE,
            tracking_number TEXT,
            delivery_company TEXT,
            delivery_status TEXT DEFAULT 'preparing',  -- preparing, shipped, in_transit, delivered, failed
            recipient_name TEXT,
            recipient_phone TEXT,
            delivery_address TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES sales_orders (order_number)
        )
    ''')
    print("  ✅ deliveries 테이블 생성")
    
    # 11. 고객 연락 이력
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT NOT NULL,
            contact_date DATE NOT NULL,
            contact_type TEXT NOT NULL,  -- phone, email, visit, video_call
            contact_person TEXT,
            subject TEXT,
            content TEXT,
            result TEXT,
            sales_person_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (sales_person_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ customer_contacts 테이블 생성")
    
    # 12. 매출 목표
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_year INTEGER NOT NULL,
            target_month INTEGER,
            sales_person_id INTEGER,
            customer_code TEXT,
            product_category TEXT,
            target_amount REAL NOT NULL,
            actual_amount REAL DEFAULT 0,
            achievement_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sales_person_id) REFERENCES users (id),
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code)
        )
    ''')
    print("  ✅ sales_targets 테이블 생성")
    
    conn.commit()
    conn.close()
    print("\n✅ 영업관리 테이블 생성 완료!")

if __name__ == "__main__":
    create_sales_tables()
