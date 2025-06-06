# File: /tests/test_purchase.py

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from modules.purchase.layouts import create_purchase_layout
from modules.purchase.callbacks import register_purchase_callbacks

def test_purchase_layout():
    """구매관리 레이아웃 테스트"""
    layout = create_purchase_layout()
    assert layout is not None
    print("✅ 구매관리 레이아웃 생성 성공")

def test_purchase_tables():
    """구매관리 테이블 확인"""
    import sqlite3
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    tables = ['supplier_master', 'purchase_orders', 'purchase_order_details',
              'receiving_schedule', 'receiving_inspection', 'auto_po_rules']
    
    for table in tables:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        assert cursor.fetchone() is not None, f"{table} 테이블이 없습니다"
        print(f"✅ {table} 테이블 확인")
    
    conn.close()

if __name__ == "__main__":
    print("🧪 구매관리 모듈 테스트 시작...\n")
    test_purchase_layout()
    test_purchase_tables()
    print("\n✅ 모든 테스트 통과!")
