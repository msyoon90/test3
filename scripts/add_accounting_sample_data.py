# File: scripts/add_accounting_sample_data.py

import sqlite3
from datetime import datetime, timedelta
import random
import os

def add_accounting_sample_data():
    """회계관리 샘플 데이터 추가"""
    if not os.path.exists('data/database.db'):
        print("❌ 데이터베이스가 없습니다. 먼저 create_accounting_tables.py를 실행하세요.")
        return
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 1. 계정과목 마스터 데이터
    print("계정과목 데이터 추가 중...")
    
    accounts = [
        # 자산 계정
        ('100', '자산', '자산', None, 1, 1, 1),
        ('110', '유동자산', '자산', '100', 2, 1, 1),
        ('111', '현금', '자산', '110', 3, 0, 1),
        ('112', '보통예금', '자산', '110', 3, 0, 1),
        ('113', '외상매출금', '자산', '110', 3, 0, 1),
        ('120', '재고자산', '자산', '100', 2, 1, 1),
        ('121', '원재료', '자산', '120', 3, 0, 1),
        ('122', '재공품', '자산', '120', 3, 0, 1),
        ('123', '제품', '자산', '120', 3, 0, 1),
        ('130', '고정자산', '자산', '100', 2, 1, 1),
        ('131', '건물', '자산', '130', 3, 0, 1),
        ('132', '기계장치', '자산', '130', 3, 0, 1),
        ('133', '차량운반구', '자산', '130', 3, 0, 1),
        
        # 부채 계정
        ('200', '부채', '부채', None, 1, 1, 1),
        ('210', '유동부채', '부채', '200', 2, 1, 1),
        ('211', '외상매입금', '부채', '210', 3, 0, 1),
        ('212', '미지급금', '부채', '210', 3, 0, 1),
        ('213', '예수금', '부채', '210', 3, 0, 1),
        
        # 자본 계정
        ('300', '자본', '자본', None, 1, 1, 1),
        ('310', '자본금', '자본', '300', 2, 0, 1),
        ('320', '이익잉여금', '자본', '300', 2, 0, 1),
        
        # 수익 계정
        ('400', '수익', '수익', None, 1, 1, 1),
        ('410', '매출', '수익', '400', 2, 0, 1),
        ('420', '영업외수익', '수익', '400', 2, 0, 1),
        
        # 비용 계정
        ('500', '비용', '비용', None, 1, 1, 1),
        ('510', '매출원가', '비용', '500', 2, 1, 1),
        ('511', '재료비', '비용', '510', 3, 0, 1),
        ('512', '노무비', '비용', '510', 3, 0, 1),
        ('513', '제조경비', '비용', '510', 3, 0, 1),
        ('520', '판매관리비', '비용', '500', 2, 1, 1),
        ('521', '급여', '비용', '520', 3, 0, 1),
        ('522', '임차료', '비용', '520', 3, 0, 1),
        ('523', '감가상각비', '비용', '520', 3, 0, 1),
        ('524', '통신비', '비용', '520', 3, 0, 1),
        ('525', '소모품비', '비용', '520', 3, 0, 1)
    ]
    
    for account in accounts:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO account_master 
                (account_code, account_name, account_type, parent_code, 
                 level, is_control, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, account)
        except Exception as e:
            print(f"  오류: {account[0]} - {e}")
    
    print(f"  ✅ {len(accounts)}개 계정과목 추가 완료")
    
    # 2. 전표 샘플 데이터 (최근 60일)
    print("\n전표 데이터 추가 중...")
    
    voucher_count = 0
    for i in range(60, -1, -1):
        voucher_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 하루에 5-15건의 전표
        daily_vouchers = random.randint(5, 15)
        
        for j in range(daily_vouchers):
            voucher_no = f"JV-{voucher_date.replace('-', '')}-{j+1:04d}"
            
            # 전표 유형 랜덤 선택
            voucher_types = ['receipt', 'payment', 'transfer', 'sales', 'purchase']
            voucher_type = random.choice(voucher_types)
            
            # 상태 (오래된 것은 승인완료)
            if i > 7:
                status = 'approved'
            else:
                status = random.choice(['draft', 'pending', 'approved'])
            
            try:
                # 전표 헤더
                if voucher_type == 'receipt':  # 입금
                    desc = f"매출 대금 입금 - 거래처{random.randint(1, 10)}"
                    total_amount = random.randint(100, 1000) * 10000
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO journal_header
                        (voucher_no, voucher_date, voucher_type, description,
                         total_debit, total_credit, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """, (voucher_no, voucher_date, voucher_type, desc,
                          total_amount, total_amount, status))
                    
                    # 전표 상세
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 1, '112', ?, 0, ?)
                    """, (voucher_no, total_amount, desc))
                    
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 2, '113', 0, ?, ?)
                    """, (voucher_no, total_amount, desc))
                    
                elif voucher_type == 'payment':  # 출금
                    desc = f"구매 대금 지급 - 거래처{random.randint(1, 10)}"
                    total_amount = random.randint(50, 500) * 10000
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO journal_header
                        (voucher_no, voucher_date, voucher_type, description,
                         total_debit, total_credit, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """, (voucher_no, voucher_date, voucher_type, desc,
                          total_amount, total_amount, status))
                    
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 1, '211', ?, 0, ?)
                    """, (voucher_no, total_amount, desc))
                    
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 2, '112', 0, ?, ?)
                    """, (voucher_no, total_amount, desc))
                    
                elif voucher_type == 'sales':  # 매출
                    desc = f"제품 판매 - 거래처{random.randint(1, 10)}"
                    sales_amount = random.randint(100, 1000) * 10000
                    vat_amount = int(sales_amount * 0.1)
                    total_amount = sales_amount + vat_amount
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO journal_header
                        (voucher_no, voucher_date, voucher_type, description,
                         total_debit, total_credit, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """, (voucher_no, voucher_date, voucher_type, desc,
                          total_amount, total_amount, status))
                    
                    # 외상매출금 (차변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 1, '113', ?, 0, ?)
                    """, (voucher_no, total_amount, desc))
                    
                    # 매출 (대변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 2, '410', 0, ?, ?)
                    """, (voucher_no, sales_amount, desc))
                    
                    # 부가세예수금 (대변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 3, '213', 0, ?, '부가세')
                    """, (voucher_no, vat_amount))
                    
                elif voucher_type == 'purchase':  # 매입
                    desc = f"원재료 구매 - 거래처{random.randint(1, 5)}"
                    purchase_amount = random.randint(50, 500) * 10000
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO journal_header
                        (voucher_no, voucher_date, voucher_type, description,
                         total_debit, total_credit, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """, (voucher_no, voucher_date, voucher_type, desc,
                          purchase_amount, purchase_amount, status))
                    
                    # 재료비 (차변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 1, '511', ?, 0, ?)
                    """, (voucher_no, purchase_amount, desc))
                    
                    # 외상매입금 (대변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 2, '211', 0, ?, ?)
                    """, (voucher_no, purchase_amount, desc))
                    
                else:  # transfer (대체)
                    # 급여, 임차료, 감가상각비 등
                    transfer_types = [
                        ('521', '급여', random.randint(300, 500) * 10000),
                        ('522', '임차료', random.randint(100, 200) * 10000),
                        ('523', '감가상각비', random.randint(50, 100) * 10000),
                        ('524', '통신비', random.randint(10, 30) * 10000),
                        ('525', '소모품비', random.randint(20, 50) * 10000)
                    ]
                    
                    account_code, desc, amount = random.choice(transfer_types)
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO journal_header
                        (voucher_no, voucher_date, voucher_type, description,
                         total_debit, total_credit, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """, (voucher_no, voucher_date, voucher_type, f"{desc} 지급",
                          amount, amount, status))
                    
                    # 비용 계정 (차변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 1, ?, ?, 0, ?)
                    """, (voucher_no, account_code, amount, desc))
                    
                    # 미지급금 또는 현금 (대변)
                    cursor.execute("""
                        INSERT INTO journal_details
                        (voucher_no, line_no, account_code, debit_amount, credit_amount, description)
                        VALUES (?, 2, '212', 0, ?, ?)
                    """, (voucher_no, amount, desc))
                
                voucher_count += 1
                
            except Exception as e:
                print(f"  전표 생성 오류: {voucher_no} - {e}")
    
    print(f"  ✅ {voucher_count}개 전표 추가 완료")
    
    # 3. 세금계산서 샘플 데이터
    print("\n세금계산서 데이터 추가 중...")
    
    invoice_count = 0
    # 매출 전표에 대한 세금계산서
    cursor.execute("""
        SELECT voucher_no, voucher_date, description 
        FROM journal_header 
        WHERE voucher_type = 'sales'
        LIMIT 30
    """)
    sales_vouchers = cursor.fetchall()
    
    for voucher_no, voucher_date, desc in sales_vouchers:
        invoice_no = f"TI-{voucher_date.replace('-', '')}-{invoice_count+1:04d}"
        company_name = f"거래처{random.randint(1, 10)}(주)"
        
        # 전표에서 금액 조회
        cursor.execute("""
            SELECT SUM(credit_amount) FROM journal_details
            WHERE voucher_no = ? AND account_code = '410'
        """, (voucher_no,))
        supply_amount = cursor.fetchone()[0] or 0
        tax_amount = int(supply_amount * 0.1)
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tax_invoice
                (invoice_no, invoice_date, invoice_type, customer_code,
                 business_no, company_name, ceo_name, address,
                 supply_amount, tax_amount, total_amount, status, voucher_no)
                VALUES (?, ?, 'sales', ?, ?, ?, ?, ?, ?, ?, ?, 'issued', ?)
            """, (invoice_no, voucher_date, f"CUST{random.randint(1, 10):03d}",
                  f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}",
                  company_name, f"대표{random.randint(1, 10)}", "서울시 강남구",
                  supply_amount, tax_amount, supply_amount + tax_amount, voucher_no))
            
            invoice_count += 1
        except Exception as e:
            print(f"  세금계산서 생성 오류: {invoice_no} - {e}")
    
    print(f"  ✅ {invoice_count}개 세금계산서 추가 완료")
    
    # 4. 예산 데이터
    print("\n예산 데이터 추가 중...")
    
    budget_count = 0
    current_year = datetime.now().year
    departments = ['생산부', '영업부', '관리부', '연구개발부']
    
    # 비용 계정들
    expense_accounts = [
        ('521', '급여', [5000, 3000, 2000, 4000]),
        ('522', '임차료', [2000, 1000, 1500, 1000]),
        ('523', '감가상각비', [1000, 500, 800, 600]),
        ('524', '통신비', [200, 300, 150, 100]),
        ('525', '소모품비', [300, 400, 200, 350])
    ]
    
    for month in range(1, 13):
        for dept_idx, dept in enumerate(departments):
            for account_code, account_name, budgets in expense_accounts:
                budget_id = f"BUD-{current_year}{month:02d}-{dept[:2]}-{account_code}"
                budget_amount = budgets[dept_idx] * 10000
                
                # 실적은 예산의 70-110% 랜덤
                if month <= datetime.now().month:
                    actual_amount = budget_amount * random.uniform(0.7, 1.1)
                else:
                    actual_amount = 0
                
                variance = actual_amount - budget_amount
                
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO budget_master
                        (budget_id, budget_year, budget_month, department,
                         account_code, budget_amount, actual_amount, variance, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
                    """, (budget_id, current_year, month, dept,
                          account_code, budget_amount, actual_amount, variance))
                    
                    budget_count += 1
                except Exception as e:
                    print(f"  예산 생성 오류: {budget_id} - {e}")
    
    print(f"  ✅ {budget_count}개 예산 데이터 추가 완료")
    
    # 5. 고정자산 데이터
    print("\n고정자산 데이터 추가 중...")
    
    assets = [
        ('FA-001', '사무실 건물', 'building', '2020-01-15', 500000000, 'straight', 40, 50000000),
        ('FA-002', 'CNC 가공기', 'machinery', '2021-03-20', 150000000, 'straight', 10, 10000000),
        ('FA-003', '화물차량', 'vehicle', '2022-06-10', 50000000, 'straight', 5, 5000000),
        ('FA-004', '프레스기', 'machinery', '2021-08-15', 80000000, 'straight', 8, 5000000),
        ('FA-005', '지게차', 'vehicle', '2023-02-01', 35000000, 'straight', 5, 3000000)
    ]
    
    for asset in assets:
        asset_code, name, asset_type, acq_date, cost, method, life, salvage = asset
        
        # 감가상각 계산
        acq_datetime = datetime.strptime(acq_date, '%Y-%m-%d')
        months_used = (datetime.now().year - acq_datetime.year) * 12 + \
                     (datetime.now().month - acq_datetime.month)
        
        if method == 'straight':
            annual_depreciation = (cost - salvage) / life
            monthly_depreciation = annual_depreciation / 12
            accumulated = monthly_depreciation * months_used
            book_value = cost - accumulated
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO fixed_asset
                (asset_code, asset_name, asset_type, acquisition_date,
                 acquisition_cost, depreciation_method, useful_life,
                 salvage_value, accumulated_depreciation, book_value, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (asset_code, name, asset_type, acq_date, cost, method,
                  life, salvage, accumulated, book_value))
        except Exception as e:
            print(f"  고정자산 생성 오류: {asset_code} - {e}")
    
    print(f"  ✅ {len(assets)}개 고정자산 추가 완료")
    
    # 6. 원가 계산 데이터
    print("\n원가 계산 데이터 추가 중...")
    
    cost_count = 0
    products = ['PROD-001', 'PROD-002', 'PROD-003']
    
    for i in range(30, -1, -1):
        calc_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        for product in products:
            calc_id = f"COST-{calc_date.replace('-', '')}-{product}"
            
            # 원가 구성
            production_qty = random.randint(100, 1000)
            material_cost = random.randint(100, 300) * production_qty
            labor_cost = random.randint(50, 150) * production_qty
            overhead_cost = random.randint(30, 100) * production_qty
            total_cost = material_cost + labor_cost + overhead_cost
            unit_cost = total_cost / production_qty
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO cost_calculation
                    (calc_id, calc_date, product_code, material_cost,
                     labor_cost, overhead_cost, total_cost, 
                     production_qty, unit_cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (calc_id, calc_date, product, material_cost,
                      labor_cost, overhead_cost, total_cost,
                      production_qty, unit_cost))
                
                cost_count += 1
            except Exception as e:
                print(f"  원가 계산 오류: {calc_id} - {e}")
    
    print(f"  ✅ {cost_count}개 원가 계산 데이터 추가 완료")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 모든 회계관리 샘플 데이터 추가 완료!")

if __name__ == "__main__":
    print("🔧 회계관리 샘플 데이터 추가 시작...\n")
    
    # 테이블이 없으면 먼저 생성
    if os.path.exists('scripts/create_accounting_tables.py'):
        from create_accounting_tables import create_accounting_tables
        create_accounting_tables()
    
    # 샘플 데이터 추가
    add_accounting_sample_data()
