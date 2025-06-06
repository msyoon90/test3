# File: scripts/add_purchase_sample_data.py

import sqlite3
from datetime import datetime, timedelta
import random
import os

def add_purchase_sample_data():
    """구매관리 샘플 데이터 추가"""
    if not os.path.exists('data/database.db'):
        print("❌ 데이터베이스가 없습니다. 먼저 create_purchase_tables.py를 실행하세요.")
        return
    
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
    
    # 2. 품목이 있는지 확인
    cursor.execute("SELECT COUNT(*) FROM item_master")
    item_count = cursor.fetchone()[0]
    
    if item_count == 0:
        print("\n품목 마스터가 비어있습니다. 기본 품목 추가 중...")
        basic_items = [
            ('BOLT-M10', '볼트 M10x30', '부품', 'EA', 500, 750, 150),
            ('NUT-M10', '너트 M10', '부품', 'EA', 500, 800, 80),
            ('PLATE-1.0', '철판 1.0T', '원자재', 'EA', 50, 75, 15000),
            ('MOTOR-DC24', '모터 DC24V', '부품', 'EA', 20, 25, 85000),
            ('BEARING-6201', '베어링 6201', '부품', 'EA', 100, 150, 3500),
            ('OIL-10W30', '엔진오일 10W30', '소모품', 'L', 50, 60, 8000)
        ]
        
        for item in basic_items:
            cursor.execute("""
                INSERT OR REPLACE INTO item_master 
                (item_code, item_name, category, unit, safety_stock, current_stock, unit_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, item)
        print(f"  ✅ {len(basic_items)}개 기본 품목 추가 완료")
    
    # 3. 발주서 샘플 데이터
    print("\n발주서 데이터 추가 중...")
    
    # 사용 가능한 품목 조회
    cursor.execute("SELECT item_code, unit_price FROM item_master")
    available_items = cursor.fetchall()
    
    if not available_items:
        print("  ❌ 품목이 없어 발주서를 생성할 수 없습니다.")
        return
    
    po_count = 0
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
            
            try:
                # 발주서 헤더
                cursor.execute("""
                    INSERT OR IGNORE INTO purchase_orders
                    (po_number, po_date, supplier_code, delivery_date, warehouse,
                     total_amount, status, remarks, created_by)
                    VALUES (?, ?, ?, ?, 'wh1', 0, ?, '샘플 발주', 1)
                """, (po_number, po_date, supplier_code, delivery_date, status))
                
                # 발주 상세 (품목 2-5개)
                num_items = min(random.randint(2, 5), len(available_items))
                selected_items = random.sample(available_items, num_items)
                
                for item_code, unit_price in selected_items:
                    quantity = random.randint(10, 500)
                    amount = quantity * unit_price
                    total_amount += amount
                    
                    cursor.execute("""
                        INSERT INTO purchase_order_details
                        (po_number, item_code, quantity, unit_price, amount)
                        VALUES (?, ?, ?, ?, ?)
                    """, (po_number, item_code, quantity, unit_price, amount))
                    
                    # 입고 예정 (승인된 발주만)
                    if status in ['approved', 'receiving', 'completed']:
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
                
                po_count += 1
                
            except Exception as e:
                print(f"  발주서 생성 오류: {po_number} - {e}")
    
    print(f"  ✅ {po_count}개 발주서 데이터 추가 완료")
    
    # 4. 자동 발주 규칙
    print("\n자동 발주 규칙 추가 중...")
    
    # 실제 존재하는 품목만 사용
    cursor.execute("SELECT item_code FROM item_master LIMIT 5")
    items_for_rules = cursor.fetchall()
    
    rule_count = 0
    for idx, (item_code,) in enumerate(items_for_rules):
        supplier_code = suppliers[idx % len(suppliers)][0]
        cursor.execute("""
            INSERT OR IGNORE INTO auto_po_rules
            (item_code, supplier_code, reorder_point, order_qty, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (item_code, supplier_code, random.randint(50, 300), random.randint(100, 500)))
        rule_count += 1
    
    print(f"  ✅ {rule_count}개 자동 발주 규칙 추가 완료")
    
    # 5. 입고 검수 샘플 데이터
    print("\n입고 검수 데이터 추가 중...")
    
    # 완료된 발주서에 대한 검수 기록
    cursor.execute("""
        SELECT po_number, delivery_date FROM purchase_orders 
        WHERE status = 'completed'
        LIMIT 20
    """)
    completed_pos = cursor.fetchall()
    
    inspection_count = 0
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
                rejected = random.randint(1, max(1, int(quantity * 0.1)))
                accepted = quantity - rejected
                result = '불량포함'
            else:
                accepted = quantity
                rejected = 0
                result = '합격'
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO receiving_inspection
                    (receiving_date, po_number, item_code, received_qty,
                     accepted_qty, rejected_qty, inspection_result, inspector_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (delivery_date, po_number, item_code, quantity,
                      accepted, rejected, result))
                inspection_count += 1
            except Exception as e:
                print(f"  검수 기록 오류: {e}")
    
    print(f"  ✅ {inspection_count}개 입고 검수 데이터 추가 완료")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 모든 구매관리 샘플 데이터 추가 완료!")

if __name__ == "__main__":
    print("🔧 구매관리 샘플 데이터 추가 시작...\n")
    
    # 테이블이 없으면 먼저 생성
    if os.path.exists('scripts/create_purchase_tables.py'):
        from create_purchase_tables import create_purchase_tables
        create_purchase_tables()
    else:
        print("⚠️  create_purchase_tables.py를 먼저 실행하세요!")
        print("   또는 이 스크립트와 같은 폴더에 있는지 확인하세요.")
    
    # 샘플 데이터 추가
    add_purchase_sample_data()