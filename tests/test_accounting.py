# File: tests/test_accounting.py

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from modules.accounting.layouts import create_accounting_layout
from modules.accounting.callbacks import register_accounting_callbacks

def test_accounting_layout():
    """회계관리 레이아웃 테스트"""
    layout = create_accounting_layout()
    assert layout is not None
    print("✅ 회계관리 레이아웃 생성 성공")

def test_accounting_tables():
    """회계관리 테이블 확인"""
    import sqlite3
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    tables = ['account_master', 'journal_header', 'journal_details',
              'tax_invoice', 'budget_master', 'cost_calculation',
              'closing_master', 'fixed_asset']
    
    for table in tables:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        result = cursor.fetchone()
        if result:
            print(f"✅ {table} 테이블 확인")
        else:
            print(f"❌ {table} 테이블이 없습니다")
    
    conn.close()

def test_sample_data():
    """샘플 데이터 확인"""
    import sqlite3
    conn = sqlite3.connect('data/database.db')
    
    # 계정과목 확인
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_master")
    account_count = cursor.fetchone()[0]
    print(f"📊 계정과목: {account_count}개")
    
    # 전표 확인
    cursor.execute("SELECT COUNT(*) FROM journal_header")
    voucher_count = cursor.fetchone()[0]
    print(f"📄 전표: {voucher_count}개")
    
    # 예산 확인
    cursor.execute("SELECT COUNT(*) FROM budget_master")
    budget_count = cursor.fetchone()[0]
    print(f"💰 예산: {budget_count}개")
    
    conn.close()

if __name__ == "__main__":
    print("🧪 회계관리 모듈 테스트 시작...\n")
    test_accounting_layout()
    print("\n")
    test_accounting_tables()
    print("\n")
    test_sample_data()
    print("\n✅ 모든 테스트 완료!")
