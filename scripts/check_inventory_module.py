# File: /scripts/check_inventory_module.py
# 재고관리 모듈 체크 스크립트

import os
import sys
import sqlite3

def check_inventory_module():
    """재고관리 모듈 상태 점검"""
    print("🔍 재고관리 모듈 점검 시작...\n")
    
    # 1. 파일 존재 확인
    print("1. 파일 구조 확인")
    required_files = [
        'modules/__init__.py',
        'modules/inventory/__init__.py',
        'modules/inventory/layouts.py',
        'modules/inventory/callbacks.py'
    ]
    
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"  ✅ {filepath} - 존재")
        else:
            print(f"  ❌ {filepath} - 없음")
            
            # 디렉토리 생성
            dir_path = os.path.dirname(filepath)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"     → {dir_path} 디렉토리 생성됨")
            
            # 빈 파일 생성
            if filepath.endswith('__init__.py'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    if 'inventory' in filepath:
                        f.write('''from .layouts import create_inventory_layout
from .callbacks import register_inventory_callbacks

__all__ = ['create_inventory_layout', 'register_inventory_callbacks']
''')
                    else:
                        f.write('')
                print(f"     → {filepath} 파일 생성됨")
    
    # 2. 데이터베이스 테이블 확인
    print("\n2. 데이터베이스 테이블 확인")
    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # 필요한 테이블들
        required_tables = {
            'item_master': '''
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
            ''',
            'stock_movements': '''
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
            ''',
            'stock_adjustments': '''
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
            '''
        }
        
        for table_name, create_sql in required_tables.items():
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                print(f"  ✅ {table_name} 테이블 - 존재")
            else:
                print(f"  ❌ {table_name} 테이블 - 없음")
                cursor.execute(create_sql)
                print(f"     → {table_name} 테이블 생성됨")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"  ❌ 데이터베이스 오류: {e}")
    
    # 3. 모듈 import 테스트
    print("\n3. 모듈 import 테스트")
    try:
        sys.path.insert(0, os.path.abspath('.'))
        from modules.inventory.layouts import create_inventory_layout
        from modules.inventory.callbacks import register_inventory_callbacks
        print("  ✅ 재고관리 모듈 import 성공")
    except ImportError as e:
        print(f"  ❌ 재고관리 모듈 import 실패: {e}")
    
    print("\n✅ 재고관리 모듈 점검 완료!")
    print("💡 문제가 있다면 위의 오류 메시지를 확인하세요.")

if __name__ == "__main__":
    check_inventory_module()
