# File: /scripts/add_purchase_sample_data.py

import sqlite3
from datetime import datetime, timedelta
import random

def add_purchase_sample_data():
    """구매관리 샘플 데이터 추가"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 1. 거래처 샘플 데이터
    print("거래처 데이터 추가 중...")
    
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
    print("\n발주서 데이터 추가 중...")
    
    # 최근 60일간의 발주 데이터 생성
    for i in range(60, -1, -5):  # 5일 간격
        po_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 하루에 1-3건의 발주
        for j in range(random.randint(1, 3)):
            po_number = f"PO-{po_date.replace('-', '')}-{j+1:03d}"
            supplier_code = random.choice([s[0] for s in suppliers])
            delivery_date = (datetime.strptime(po_date, '%Y-%m-%d') + 
                           timedelta(days=random.randint(3, 10))).strftime('%Y-%m-%d')
            
            # 상태 결정
            if i > 30:
                status = 'completed'
            elif i > 14:
                status = random.choice(['approved', 'receiving', 'completed'])
            elif i > 7:
                status = random.choice(['draft', 'pending', 'approved'])
            else:
                status = random.choice(['draft', 'pending'])
            
            total_amount = 0
            
            # 발주서 헤더
            cursor.execute("""
                INSERT OR IGNORE INTO purchase_orders
                (po_number, po_date, supplier_code, delivery_date, warehouse,
                 total_amount, status, remarks, created_by)
                VALUES (?, ?, ?, ?, 'wh1', 0, ?, '샘플 발주', 1)
            """, (po_number, po_date, supplier_code, delivery_date, status))
            
            # 발주 상세 (품목 2-5개)
            num_items = random.randint(2, 5)
            items = random.sample(['BOLT-M10', 'NUT-M10', 'PLATE-1.0', 
                                 'MOTOR-DC24', 'BEARING-6201'], num_items)
            
            for item_code in items:
                quantity = random.randint(10, 500)
                
                # 품목 정보 조회
                cursor.execute("SELECT unit_price FROM item_master WHERE item_code = ?", 
                             (item_code,))
                unit_price = cursor.fetchone()[0]
                amount = quantity * unit_price
                total_amount += amount
                
                cursor.execute("""
                    INSERT INTO purchase_order_details
                    (po_number, item_code, quantity, unit_price, amount)
                    VALUES (?, ?, ?, ?, ?)
                """, (po_number, item_code, quantity, unit_price, amount))
                
                # 입고 예정 (승인된 발주만)
                if status in ['approved', 'receiving']:
                    cursor.execute("""
                        INSERT INTO receiving_schedule
                        (po_number, scheduled_date, item_code, expected_qty, 
                         received_qty, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (po_number, delivery_date, item_code, quantity,
                          quantity if status == 'completed' else 0,
                          'completed' if status == 'completed' else 'pending'))
            
            # 총액 업데이트
            cursor.execute("""
                UPDATE purchase_orders SET total_amount = ? 
                WHERE po_number = ?
            """, (total_amount, po_number))
    
    print("  ✅ 발주서 데이터 추가 완료")
    
    # 3. 자동 발주 규칙
    print("\n자동 발주 규칙 추가 중...")
    
    auto_rules = [
        ('BOLT-M10', 'SUP001', 300, 500),
        ('NUT-M10', 'SUP001', 300, 500),
        ('MOTOR-DC24', 'SUP003', 10, 20),
        ('BEARING-6201', 'SUP004', 50, 100),
        ('OIL-10W30', 'SUP005', 30, 50)
    ]
    
    for rule in auto_rules:
        cursor.execute("""
            INSERT OR IGNORE INTO auto_po_rules
            (item_code, supplier_code, reorder_point, order_qty, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, rule)
    
    print(f"  ✅ {len(auto_rules)}개 자동 발주 규칙 추가 완료")
    
    # 4. 입고 검수 샘플 데이터
    print("\n입고 검수 데이터 추가 중...")
    
    # 완료된 발주서에 대한 검수 기록
    cursor.execute("""
        SELECT po_number, delivery_date FROM purchase_orders 
        WHERE status = 'completed'
    """)
    completed_pos = cursor.fetchall()
    
    for po_number, delivery_date in completed_pos:
        # 해당 발주의 품목들
        cursor.execute("""
            SELECT item_code, quantity FROM purchase_order_details
            WHERE po_number = ?
        """, (po_number,))
        
        items = cursor.fetchall()
        for item_code, quantity in items:
            # 대부분 정상 입고, 가끔 불량
            if random.random() > 0.9:  # 10% 불량
                rejected = random.randint(1, int(quantity * 0.1))
                accepted = quantity - rejected
                result = '불량포함'
            else:
                accepted = quantity
                rejected = 0
                result = '합격'
            
            cursor.execute("""
                INSERT OR IGNORE INTO receiving_inspection
                (receiving_date, po_number, item_code, received_qty,
                 accepted_qty, rejected_qty, inspection_result, inspector_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (delivery_date, po_number, item_code, quantity,
                  accepted, rejected, result))
    
    print("  ✅ 입고 검수 데이터 추가 완료")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 모든 구매관리 샘플 데이터 추가 완료!")

if __name__ == "__main__":
    print("🔧 구매관리 샘플 데이터 추가 시작...\n")
    
    # 테이블 생성 먼저 실행
    from create_purchase_tables import create_purchase_tables
    create_purchase_tables()
    
    # 샘플 데이터 추가
    add_purchase_sample_data()
