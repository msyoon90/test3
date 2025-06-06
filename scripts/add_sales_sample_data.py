# File: scripts/add_sales_sample_data.py
# 영업관리 모듈 샘플 데이터 추가 스크립트

import sqlite3
from datetime import datetime, timedelta
import random
import os

def add_sales_sample_data():
    """영업관리 샘플 데이터 추가"""
    if not os.path.exists('data/database.db'):
        print("❌ 데이터베이스가 없습니다. 먼저 create_sales_tables.py를 실행하세요.")
        return
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("🏢 영업관리 샘플 데이터 추가 시작...\n")
    
    # 1. 고객 데이터
    print("1. 고객 데이터 추가 중...")
    customers = [
        ('CUST001', '(주)테크놀로지', '123-45-67890', '김대표', '이부장', '02-1234-5678', 
         'lee@technology.co.kr', '서울시 강남구 테헤란로 123', 'VIP', 'NET30', 100000000),
        ('CUST002', '글로벌산업(주)', '234-56-78901', '박사장', '최과장', '031-987-6543',
         'choi@global.com', '경기도 수원시 영통구 월드컵로 456', 'Gold', 'NET60', 50000000),
        ('CUST003', '스마트제조', '345-67-89012', '정대표', '김대리', '032-555-1234',
         'kim@smart.kr', '인천시 남동구 논현로 789', 'Silver', 'NET30', 30000000),
        ('CUST004', '혁신솔루션(주)', '456-78-90123', '이사장', '박팀장', '051-777-8888',
         'park@innovation.co.kr', '부산시 해운대구 센텀로 321', 'Gold', 'NET30', 70000000),
        ('CUST005', '미래기업', '567-89-01234', '최회장', '송차장', '062-333-4444',
         'song@future.com', '광주시 서구 상무로 999', 'Bronze', 'NET90', 20000000),
        ('CUST006', '디지털코퍼레이션', '678-90-12345', '장대표', '윤부장', '054-222-3333',
         'yoon@digital.kr', '경북 포항시 남구 지곡로 555', 'Silver', 'NET30', 40000000),
        ('CUST007', '한국오토메이션', '789-01-23456', '임사장', '조과장', '055-666-7777',
         'cho@automation.co.kr', '경남 창원시 성산구 원이대로 777', 'VIP', 'NET30', 80000000),
        ('CUST008', '첨단시스템즈', '890-12-34567', '한대표', '유대리', '063-888-9999',
         'yu@advanced.com', '전북 전주시 덕진구 기린대로 888', 'Bronze', 'NET60', 15000000)
    ]
    
    for customer in customers:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO customers 
                (customer_code, customer_name, business_no, ceo_name, contact_person,
                 phone, email, address, grade, payment_terms, credit_limit, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, customer)
        except Exception as e:
            print(f"  오류: {customer[0]} - {e}")
    
    print(f"  ✅ {len(customers)}개 고객 추가 완료")
    
    # 2. 제품 데이터
    print("\n2. 제품 데이터 추가 중...")
    products = [
        ('PROD001', 'Smart MES 시스템', 'Software', 'MES 솔루션 패키지', 50000000, 30000000),
        ('PROD002', 'ERP 통합 솔루션', 'Software', 'ERP 시스템 구축', 80000000, 50000000),
        ('PROD003', '자동화 제어시스템', 'Hardware', 'PLC 기반 자동화', 30000000, 18000000),
        ('PROD004', 'IoT 센서 패키지', 'Hardware', '스마트 팩토리 센서', 15000000, 9000000),
        ('PROD005', '데이터 분석 플랫폼', 'Software', 'BI 및 분석 도구', 25000000, 15000000),
        ('PROD006', '품질관리 시스템', 'Software', 'QMS 솔루션', 35000000, 21000000),
        ('PROD007', '설비관리 솔루션', 'Software', 'CMMS 시스템', 40000000, 24000000),
        ('PROD008', '스마트 HMI', 'Hardware', '터치 인터페이스', 12000000, 7200000)
    ]
    
    for product in products:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO products 
                (product_code, product_name, category, description, unit_price, cost_price, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, product)
        except Exception as e:
            print(f"  오류: {product[0]} - {e}")
    
    print(f"  ✅ {len(products)}개 제품 추가 완료")
    
    # 3. 견적서 데이터 (최근 90일)
    print("\n3. 견적서 데이터 추가 중...")
    
    quote_count = 0
    for i in range(90, -1, -3):  # 3일 간격
        quote_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 하루에 1-2건의 견적
        for j in range(random.randint(1, 2)):
            quote_number = f"QT-{quote_date.replace('-', '')}-{j+1:04d}"
            customer_code = random.choice([c[0] for c in customers])
            validity_date = (datetime.strptime(quote_date, '%Y-%m-%d') + 
                           timedelta(days=30)).strftime('%Y-%m-%d')
            
            # 상태 결정 (시간이 지날수록 진행)
            if i > 60:
                status = random.choice(['won', 'lost'])
            elif i > 30:
                status = random.choice(['won', 'lost', 'reviewing'])
            elif i > 14:
                status = random.choice(['sent', 'reviewing', 'won'])
            else:
                status = random.choice(['draft', 'sent', 'reviewing'])
            
            # 할인율 (VIP는 높은 할인)
            cursor.execute("SELECT grade FROM customers WHERE customer_code = ?", (customer_code,))
            grade = cursor.fetchone()[0]
            if grade == 'VIP':
                discount_rate = random.uniform(10, 20)
            elif grade == 'Gold':
                discount_rate = random.uniform(5, 15)
            elif grade == 'Silver':
                discount_rate = random.uniform(3, 10)
            else:
                discount_rate = random.uniform(0, 5)
            
            total_amount = 0
            
            try:
                # 견적서 헤더
                cursor.execute("""
                    INSERT OR IGNORE INTO quotations
                    (quote_number, quote_date, customer_code, validity_date,
                     total_amount, discount_rate, status, notes, created_by)
                    VALUES (?, ?, ?, ?, 0, ?, ?, '샘플 견적서', 1)
                """, (quote_number, quote_date, customer_code, validity_date, discount_rate, status))
                
                # 견적 상세 (제품 1-3개)
                num_products = random.randint(1, 3)
                selected_products = random.sample(products, num_products)
                
                for line_no, product in enumerate(selected_products, 1):
                    product_code, product_name, category, description, unit_price, cost_price = product
                    quantity = random.randint(1, 5)
                    amount = quantity * unit_price
                    total_amount += amount
                    
                    cursor.execute("""
                        INSERT INTO quotation_details
                        (quote_number, line_no, product_code, product_name, 
                         description, quantity, unit_price, amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (quote_number, line_no, product_code, product_name,
                          description, quantity, unit_price, amount))
                
                # 할인 적용
                discount_amount = total_amount * (discount_rate / 100)
                final_amount = total_amount - discount_amount
                
                # 총액 업데이트
                cursor.execute("""
                    UPDATE quotations 
                    SET total_amount = ?, discount_amount = ?
                    WHERE quote_number = ?
                """, (final_amount, discount_amount, quote_number))
                
                quote_count += 1
                
            except Exception as e:
                print(f"  견적서 생성 오류: {quote_number} - {e}")
    
    print(f"  ✅ {quote_count}개 견적서 추가 완료")
    
    # 4. 수주 데이터 (견적서 중 수주 확정된 것들)
    print("\n4. 수주 데이터 추가 중...")
    
    # 수주 확정된 견적서 조회
    cursor.execute("""
        SELECT quote_number, quote_date, customer_code, total_amount
        FROM quotations 
        WHERE status = 'won'
    """)
    won_quotes = cursor.fetchall()
    
    order_count = 0
    for quote_number, quote_date, customer_code, total_amount in won_quotes:
        order_date = (datetime.strptime(quote_date, '%Y-%m-%d') + 
                     timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
        
        # 수주번호 생성
        cursor.execute("SELECT COUNT(*) FROM sales_orders WHERE order_date = ?", (order_date,))
        count = cursor.fetchone()[0]
        order_number = f"SO-{order_date.replace('-', '')}-{count+1:04d}"
        
        delivery_date = (datetime.strptime(order_date, '%Y-%m-%d') + 
                        timedelta(days=random.randint(14, 45))).strftime('%Y-%m-%d')
        
        # 수주 상태
        days_since_order = (datetime.now() - datetime.strptime(order_date, '%Y-%m-%d')).days
        if days_since_order > 30:
            status = random.choice(['completed', 'completed', 'ready_for_delivery'])
        elif days_since_order > 14:
            status = random.choice(['in_production', 'ready_for_delivery'])
        else:
            status = random.choice(['confirmed', 'in_production'])
        
        try:
            # 수주 헤더
            cursor.execute("""
                INSERT OR IGNORE INTO sales_orders
                (order_number, order_date, customer_code, quote_number, delivery_date,
                 total_amount, status, notes, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, '견적서에서 전환', 1)
            """, (order_number, order_date, customer_code, quote_number, 
                  delivery_date, total_amount, status))
            
            # 견적 상세를 수주 상세로 복사
            cursor.execute("""
                SELECT line_no, product_code, product_name, description, 
                       quantity, unit_price, amount
                FROM quotation_details 
                WHERE quote_number = ?
            """, (quote_number,))
            
            quote_details = cursor.fetchall()
            for detail in quote_details:
                cursor.execute("""
                    INSERT INTO sales_order_details
                    (order_number, line_no, product_code, product_name, 
                     description, quantity, unit_price, amount, delivered_qty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (order_number, detail[0], detail[1], detail[2], detail[3],
                      detail[4], detail[5], detail[6], 
                      detail[4] if status == 'completed' else 0))
            
            order_count += 1
            
        except Exception as e:
            print(f"  수주 생성 오류: {order_number} - {e}")
    
    print(f"  ✅ {order_count}개 수주 추가 완료")
    
    # 5. 영업 활동 데이터
    print("\n5. 영업 활동 데이터 추가 중...")
    
    activity_types = [
        ('call', '전화 상담'),
        ('email', '이메일 발송'),
        ('meeting', '고객 미팅'),
        ('demo', '제품 데모'),
        ('follow_up', '팔로업')
    ]
    
    activity_count = 0
    for i in range(30, -1, -1):  # 최근 30일
        activity_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 하루에 2-5건의 활동
        for _ in range(random.randint(2, 5)):
            activity_type, subject_prefix = random.choice(activity_types)
            customer_code = random.choice([c[0] for c in customers])
            
            # 고객 담당자 조회
            cursor.execute("SELECT contact_person FROM customers WHERE customer_code = ?", 
                          (customer_code,))
            contact_result = cursor.fetchone()
            contact_person = contact_result[0] if contact_result else "담당자"
            
            subject = f"{subject_prefix} - {contact_person}"
            description = f"{customer_code} {contact_person}과의 {subject_prefix}"
            
            results = ["긍정적 반응", "추가 검토 필요", "경쟁사 비교 중", "예산 확인 중", "의사결정 보류"]
            result = random.choice(results)
            
            next_actions = ["재연락 예정", "견적서 발송", "추가 미팅 일정", "제안서 준비", "계약서 검토"]
            next_action = random.choice(next_actions)
            next_action_date = (datetime.strptime(activity_date, '%Y-%m-%d') + 
                              timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d')
            
            try:
                cursor.execute("""
                    INSERT INTO sales_activities
                    (activity_date, activity_type, customer_code, contact_person,
                     subject, description, result, next_action, next_action_date, sales_person_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (activity_date, activity_type, customer_code, contact_person,
                      subject, description, result, next_action, next_action_date))
                
                activity_count += 1
                
            except Exception as e:
                print(f"  영업 활동 생성 오류: {e}")
    
    print(f"  ✅ {activity_count}개 영업 활동 추가 완료")
    
    # 6. 영업 기회 데이터
    print("\n6. 영업 기회 데이터 추가 중...")
    
    opportunities = [
        ("스마트 팩토리 구축 프로젝트", "CUST001", 200000000, 80, "negotiation"),
        ("ERP 시스템 업그레이드", "CUST002", 150000000, 60, "proposal"),
        ("생산 자동화 시스템", "CUST003", 120000000, 70, "qualification"),
        ("품질관리 시스템 도입", "CUST004", 80000000, 50, "prospecting"),
        ("IoT 기반 모니터링", "CUST005", 60000000, 40, "qualification"),
        ("데이터 분석 플랫폼", "CUST006", 90000000, 65, "proposal"),
        ("설비관리 솔루션", "CUST007", 110000000, 75, "negotiation"),
        ("디지털 트랜스포메이션", "CUST008", 180000000, 55, "qualification")
    ]
    
    for opportunity in opportunities:
        name, customer_code, amount, probability, stage = opportunity
        expected_close_date = (datetime.now() + 
                             timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d')
        
        sources = ["referral", "website", "cold_call", "exhibition", "partner"]
        source = random.choice(sources)
        
        competitors = ["경쟁사A", "경쟁사B", "경쟁사C", "자체개발", "현상유지"]
        competitor = random.choice(competitors)
        
        try:
            cursor.execute("""
                INSERT INTO sales_opportunities
                (opportunity_name, customer_code, estimated_amount, probability,
                 expected_close_date, stage, source, competitor, sales_person_id,
                 description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (name, customer_code, amount, probability, expected_close_date,
                  stage, source, competitor, f"{name} 관련 영업 기회"))
            
        except Exception as e:
            print(f"  영업 기회 생성 오류: {e}")
    
    print(f"  ✅ {len(opportunities)}개 영업 기회 추가 완료")
    
    # 7. 가격 정책 데이터
    print("\n7. 가격 정책 데이터 추가 중...")
    
    price_policies = [
        ("VIP 고객 할인", "VIP", None, 15.0, 1, "2025-01-01", "2025-12-31"),
        ("Gold 고객 할인", "Gold", None, 10.0, 1, "2025-01-01", "2025-12-31"),
        ("Silver 고객 할인", "Silver", None, 5.0, 1, "2025-01-01", "2025-12-31"),
        ("대량 구매 할인", None, "Software", 20.0, 5, "2025-01-01", "2025-12-31"),
        ("하드웨어 패키지 할인", None, "Hardware", 12.0, 3, "2025-01-01", "2025-12-31")
    ]
    
    for policy in price_policies:
        try:
            cursor.execute("""
                INSERT INTO price_policies
                (policy_name, customer_grade, product_category, discount_rate,
                 min_quantity, effective_date, expiry_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, policy)
        except Exception as e:
            print(f"  가격 정책 생성 오류: {e}")
    
    print(f"  ✅ {len(price_policies)}개 가격 정책 추가 완료")
    
    # 8. 매출 목표 데이터
    print("\n8. 매출 목표 데이터 추가 중...")
    
    current_year = datetime.now().year
    
    # 월별 매출 목표
    for month in range(1, 13):
        target_amount = random.randint(300, 500) * 1000000  # 3-5억
        
        # 실적 계산 (현재 월까지만)
        if month <= datetime.now().month:
            # 실제 매출 조회
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales_orders
                WHERE strftime('%Y', order_date) = ? 
                AND strftime('%m', order_date) = ?
                AND status IN ('completed', 'ready_for_delivery')
            """, (str(current_year), f"{month:02d}"))
            actual_amount = cursor.fetchone()[0]
        else:
            actual_amount = 0
        
        achievement_rate = (actual_amount / target_amount * 100) if target_amount > 0 else 0
        
        try:
            cursor.execute("""
                INSERT INTO sales_targets
                (target_year, target_month, sales_person_id, target_amount,
                 actual_amount, achievement_rate)
                VALUES (?, ?, 1, ?, ?, ?)
            """, (current_year, month, target_amount, actual_amount, achievement_rate))
        except Exception as e:
            print(f"  매출 목표 생성 오류: {month}월 - {e}")
    
    print(f"  ✅ 12개월 매출 목표 추가 완료")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 모든 영업관리 샘플 데이터 추가 완료!")
    print(f"""
📊 추가된 데이터 요약:
  - 고객: {len(customers)}개
  - 제품: {len(products)}개  
  - 견적서: {quote_count}개
  - 수주: {order_count}개
  - 영업활동: {activity_count}개
  - 영업기회: {len(opportunities)}개
  - 가격정책: {len(price_policies)}개
  - 매출목표: 12개월
    """)

if __name__ == "__main__":
    print("🚀 영업관리 샘플 데이터 추가 시작...\n")
    
    # 테이블이 없으면 먼저 생성
    if os.path.exists('scripts/create_sales_tables.py'):
        from create_sales_tables import create_sales_tables
        create_sales_tables()
    else:
        print("⚠️  create_sales_tables.py를 먼저 실행하세요!")
        print("   또는 이 스크립트와 같은 폴더에 있는지 확인하세요.")
    
    # 샘플 데이터 추가
    add_sales_sample_data()
