# File: scripts/create_accounting_tables.py

import sqlite3
import os

def create_accounting_tables():
    """회계관리 관련 테이블 생성"""
    # data 폴더가 없으면 생성
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("회계관리 테이블 생성 중...")
    
    # 1. 계정과목 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_master (
            account_code TEXT PRIMARY KEY,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,  -- 자산, 부채, 자본, 수익, 비용
            parent_code TEXT,
            level INTEGER DEFAULT 1,
            is_control BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ account_master 테이블 생성")
    
    # 2. 전표 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_header (
            voucher_no TEXT PRIMARY KEY,
            voucher_date DATE NOT NULL,
            voucher_type TEXT NOT NULL,  -- 입금, 출금, 대체, 매출, 매입
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
    print("  ✅ journal_header 테이블 생성")
    
    # 3. 전표 상세
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_no TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            account_code TEXT NOT NULL,
            debit_amount REAL DEFAULT 0,
            credit_amount REAL DEFAULT 0,
            description TEXT,
            cost_center TEXT,
            FOREIGN KEY (voucher_no) REFERENCES journal_header (voucher_no),
            FOREIGN KEY (account_code) REFERENCES account_master (account_code)
        )
    ''')
    print("  ✅ journal_details 테이블 생성")
    
    # 4. 세금계산서
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tax_invoice (
            invoice_no TEXT PRIMARY KEY,
            invoice_date DATE NOT NULL,
            invoice_type TEXT NOT NULL,  -- 매출, 매입
            customer_code TEXT,
            supplier_code TEXT,
            business_no TEXT,
            company_name TEXT,
            ceo_name TEXT,
            address TEXT,
            supply_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            voucher_no TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (voucher_no) REFERENCES journal_header (voucher_no)
        )
    ''')
    print("  ✅ tax_invoice 테이블 생성")
    
    # 5. 예산 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_master (
            budget_id TEXT PRIMARY KEY,
            budget_year INTEGER NOT NULL,
            budget_month INTEGER,
            department TEXT,
            account_code TEXT NOT NULL,
            budget_amount REAL DEFAULT 0,
            actual_amount REAL DEFAULT 0,
            variance REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_code) REFERENCES account_master (account_code)
        )
    ''')
    print("  ✅ budget_master 테이블 생성")
    
    # 6. 원가 계산
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cost_calculation (
            calc_id TEXT PRIMARY KEY,
            calc_date DATE NOT NULL,
            product_code TEXT NOT NULL,
            material_cost REAL DEFAULT 0,
            labor_cost REAL DEFAULT 0,
            overhead_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            production_qty INTEGER DEFAULT 0,
            unit_cost REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ cost_calculation 테이블 생성")
    
    # 7. 결산 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS closing_master (
            closing_id TEXT PRIMARY KEY,
            closing_year INTEGER NOT NULL,
            closing_month INTEGER NOT NULL,
            closing_type TEXT NOT NULL,  -- 월마감, 연마감
            status TEXT DEFAULT 'open',
            closed_date TIMESTAMP,
            closed_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (closed_by) REFERENCES users (id)
        )
    ''')
    print("  ✅ closing_master 테이블 생성")
    
    # 8. 고정자산 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fixed_asset (
            asset_code TEXT PRIMARY KEY,
            asset_name TEXT NOT NULL,
            asset_type TEXT,
            acquisition_date DATE NOT NULL,
            acquisition_cost REAL DEFAULT 0,
            depreciation_method TEXT DEFAULT 'straight',
            useful_life INTEGER DEFAULT 5,
            salvage_value REAL DEFAULT 0,
            accumulated_depreciation REAL DEFAULT 0,
            book_value REAL DEFAULT 0,
            disposal_date DATE,
            disposal_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ fixed_asset 테이블 생성")
    
    conn.commit()
    conn.close()
    print("\n✅ 회계관리 테이블 생성 완료!")

if __name__ == "__main__":
    create_accounting_tables()
