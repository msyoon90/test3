# scripts/add_hr_sample_data.py - 인사관리 샘플 데이터

import sqlite3
from datetime import datetime, timedelta
import random
import os

def add_hr_sample_data():
    """인사관리 샘플 데이터 추가"""
    if not os.path.exists('data/database.db'):
        print("❌ 데이터베이스가 없습니다. 먼저 create_hr_tables.py를 실행하세요.")
        return
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 1. 부서 데이터
    print("부서 데이터 추가 중...")
    departments = [
        ('management', '경영지원부', None),
        ('production', '생산부', None),
        ('quality', '품질관리부', None),
        ('sales', '영업부', None),
        ('rnd', '연구개발부', None)
    ]
    
    for dept in departments:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO departments 
                (dept_code, dept_name, parent_dept)
                VALUES (?, ?, ?)
            """, dept)
        except Exception as e:
            print(f"  부서 추가 오류: {dept[0]} - {e}")
    
    print(f"  ✅ {len(departments)}개 부서 추가 완료")
    
    # 2. 직급 데이터
    print("\n직급 데이터 추가 중...")
    positions = [
        ('staff', '사원', 1, 2400000, 3600000),
        ('senior', '주임', 2, 3000000, 4200000),
        ('assistant', '대리', 3, 3600000, 5400000),
        ('manager', '과장', 4, 4800000, 7200000),
        ('deputy', '차장', 5, 6000000, 9000000),
        ('general', '부장', 6, 7200000, 12000000),
        ('director', '이사', 7, 9600000, 18000000)
    ]
    
    for pos in positions:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO positions
                (position_code, position_name, position_level, min_salary, max_salary)
                VALUES (?, ?, ?, ?, ?)
            """, pos)
        except Exception as e:
            print(f"  직급 추가 오류: {pos[0]} - {e}")
    
    print(f"  ✅ {len(positions)}개 직급 추가 완료")
    
    # 3. 직원 샘플 데이터
    print("\n직원 데이터 추가 중...")
    
    # 샘플 직원 목록
    employees_data = [
        # (이름, 영문명, 성별, 부서, 직급, 입사일, 기본급)
        ('김영호', 'Kim Young-ho', 'M', 'management', 'general', '2015-03-15', 8500000),
        ('이미경', 'Lee Mi-kyung', 'F', 'management', 'manager', '2018-07-20', 5500000),
        ('박준서', 'Park Jun-seo', 'M', 'management', 'assistant', '2020-09-10', 4200000),
        
        ('최강민', 'Choi Kang-min', 'M', 'production', 'deputy', '2016-05-01', 7200000),
        ('정수진', 'Jung Su-jin', 'F', 'production', 'manager', '2019-02-15', 5200000),
        ('한동욱', 'Han Dong-wook', 'M', 'production', 'senior', '2021-11-20', 3600000),
        ('김민지', 'Kim Min-ji', 'F', 'production', 'staff', '2023-03-05', 2800000),
        
        ('이상훈', 'Lee Sang-hoon', 'M', 'quality', 'manager', '2017-08-10', 5800000),
        ('박지은', 'Park Ji-eun', 'F', 'quality', 'assistant', '2020-04-25', 4500000),
        ('송민호', 'Song Min-ho', 'M', 'quality', 'staff', '2022-07-15', 3200000),
        
        ('강태영', 'Kang Tae-young', 'M', 'sales', 'deputy', '2016-11-30', 7800000),
        ('윤서연', 'Yoon Seo-yeon', 'F', 'sales', 'manager', '2018-06-15', 5600000),
        ('조현우', 'Jo Hyun-woo', 'M', 'sales', 'assistant', '2021-01-20', 4800000),
        ('임채원', 'Lim Chae-won', 'F', 'sales', 'senior', '2022-09-05', 3800000),
        
        ('황준혁', 'Hwang Jun-hyuk', 'M', 'rnd', 'general', '2014-09-20', 9200000),
        ('서유진', 'Seo Yu-jin', 'F', 'rnd', 'manager', '2019-12-10', 6200000),
        ('노태현', 'Noh Tae-hyun', 'M', 'rnd', 'assistant', '2021-06-30', 4600000),
        ('배수빈', 'Bae Su-bin', 'F', 'rnd', 'staff', '2023-02-15', 3400000)
    ]
    
    employee_count = 0
    for idx, emp_data in enumerate(employees_data):
        name, name_en, gender, dept, position, join_date, salary = emp_data
        
        # 사번 생성
        join_year = join_date[:4]
        employee_id = f"{join_year}{idx+1:04d}"
        
        # 생년월일 (나이 25~55세 랜덤)
        age = random.randint(25, 55)
        birth_year = datetime.now().year - age
        birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        # 연락처
        mobile = f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        email = f"{name_en.lower().replace(' ', '.').replace('-', '')}@company.com"
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO employees
                (employee_id, name, name_en, gender, birth_date,
                 department, position, join_date, employment_type,
                 employment_status, base_salary, mobile_phone, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'regular', 'active', ?, ?, ?)
            """, (employee_id, name, name_en, gender, birth_date,
                  dept, position, join_date, salary, mobile, email))
            
            employee_count += 1
            
            # 부서장 설정
            if position == 'general':
                cursor.execute("""
                    UPDATE departments 
                    SET dept_head_id = ? 
                    WHERE dept_code = ?
                """, (employee_id, dept))
            
        except Exception as e:
            print(f"  직원 추가 오류: {name} - {e}")
    
    print(f"  ✅ {employee_count}명 직원 추가 완료")
    
    # 4. 근태 데이터 (최근 30일)
    print("\n근태 데이터 추가 중...")
    
    attendance_count = 0
    today = datetime.now()
    
    # 모든 직원 조회
    cursor.execute("SELECT employee_id FROM employees WHERE employment_status = 'active'")
    active_employees = [row[0] for row in cursor.fetchall()]
    
    for days_ago in range(30, -1, -1):
        attendance_date = (today - timedelta(days=days_ago))
        
        # 주말은 제외
        if attendance_date.weekday() in [5, 6]:  # 토, 일
            continue
        
        date_str = attendance_date.strftime('%Y-%m-%d')
        
        for emp_id in active_employees:
            # 90% 확률로 정상 출근
            attendance_type = 'normal'
            check_in = "09:00"
            check_out = "18:00"
            overtime = 0
            
            rand = random.random()
            if rand < 0.05:  # 5% 지각
                attendance_type = 'late'
                check_in = f"09:{random.randint(10,59):02d}"
            elif rand < 0.08:  # 3% 조퇴
                attendance_type = 'early'
                check_out = f"{random.randint(14,17)}:{random.randint(0,59):02d}"
            elif rand < 0.10:  # 2% 휴가
                attendance_type = 'leave'
                check_in = None
                check_out = None
            elif rand < 0.95:  # 85% 정상, 일부는 야근
                if random.random() < 0.3:  # 30% 야근
                    overtime = random.randint(1, 3)
                    check_out = f"{18+overtime}:{random.randint(0,59):02d}"
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO attendance
                    (employee_id, attendance_date, check_in_time, check_out_time,
                     attendance_type, overtime_hours)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (emp_id, date_str, check_in, check_out, attendance_type, overtime))
                
                attendance_count += 1
            except Exception as e:
                pass  # 중복 무시
    
    print(f"  ✅ {attendance_count}건 근태 기록 추가 완료")
    
    # 5. 연차 데이터
    print("\n연차 데이터 추가 중...")
    
    current_year = datetime.now().year
    leave_count = 0
    
    for emp_id in active_employees:
        # 근속년수 계산
        cursor.execute("SELECT join_date FROM employees WHERE employee_id = ?", (emp_id,))
        join_date = datetime.strptime(cursor.fetchone()[0], '%Y-%m-%d')
        years_of_service = (datetime.now() - join_date).days // 365
        
        # 연차 일수 (기본 15일 + 근속년수 추가)
        total_days = min(15 + (years_of_service // 2), 25)
        used_days = random.randint(0, int(total_days * 0.7))
        remaining_days = total_days - used_days
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO annual_leave
                (employee_id, year, total_days, used_days, remaining_days)
                VALUES (?, ?, ?, ?, ?)
            """, (emp_id, current_year, total_days, used_days, remaining_days))
            
            leave_count += 1
        except Exception as e:
            print(f"  연차 추가 오류: {emp_id} - {e}")
    
    print(f"  ✅ {leave_count}명 연차 데이터 추가 완료")
    
    # 6. 급여 데이터 (최근 3개월)
    print("\n급여 데이터 추가 중...")
    
    payroll_count = 0
    for month_offset in range(3):
        pay_date = datetime.now() - timedelta(days=30 * month_offset)
        pay_year = pay_date.year
        pay_month = pay_date.month
        
        for emp_id in active_employees:
            # 직원 정보 조회
            cursor.execute("""
                SELECT base_salary FROM employees 
                WHERE employee_id = ?
            """, (emp_id,))
            base_salary = cursor.fetchone()[0]
            
            # 야근 수당 계산
            cursor.execute("""
                SELECT SUM(overtime_hours) FROM attendance
                WHERE employee_id = ? 
                AND strftime('%Y-%m', attendance_date) = ?
            """, (emp_id, f"{pay_year}-{pay_month:02d}"))
            overtime_hours = cursor.fetchone()[0] or 0
            overtime_pay = (base_salary / 209) * overtime_hours * 1.5
            
            # 상여금 (분기마다)
            bonus = base_salary * 0.5 if pay_month % 3 == 0 else 0
            
            # 총 지급액
            gross_salary = base_salary + overtime_pay + bonus
            
            # 공제 항목
            income_tax = gross_salary * 0.033
            health_insurance = gross_salary * 0.0343
            pension = gross_salary * 0.045
            employment_insurance = gross_salary * 0.008
            
            # 회사 부담 보험료
            insurance_company = gross_salary * 0.09
            
            # 실 지급액
            net_salary = gross_salary - income_tax - health_insurance - pension - employment_insurance
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO payroll
                    (employee_id, pay_year, pay_month, base_salary, overtime_pay,
                     bonus, gross_salary, income_tax, health_insurance, pension,
                     employment_insurance, net_salary, insurance_company,
                     pay_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'paid')
                """, (emp_id, pay_year, pay_month, base_salary, overtime_pay,
                      bonus, gross_salary, income_tax, health_insurance, pension,
                      employment_insurance, net_salary, insurance_company,
                      f"{pay_year}-{pay_month:02d}-25"))
                
                payroll_count += 1
            except Exception as e:
                print(f"  급여 추가 오류: {emp_id} - {e}")
    
    print(f"  ✅ {payroll_count}건 급여 데이터 추가 완료")
    
    # 7. 교육 프로그램
    print("\n교육 프로그램 추가 중...")
    
    training_programs = [
        ('정보보안 교육', 'mandatory', '전 직원 필수 정보보안 교육', '보안팀', '2025-01-15', '2025-01-15', 2),
        ('성희롱 예방 교육', 'mandatory', '법정 필수 교육', '인사팀', '2025-02-10', '2025-02-10', 1),
        ('리더십 과정', 'optional', '관리자 리더십 향상 프로그램', '외부강사', '2025-03-01', '2025-03-31', 40),
        ('엑셀 실무 과정', 'optional', '엑셀 고급 기능 활용', 'IT팀', '2025-01-20', '2025-01-22', 16),
        ('품질관리 교육', 'internal', 'ISO 품질관리 시스템 교육', '품질팀', '2025-02-15', '2025-02-16', 8)
    ]
    
    for program in training_programs:
        try:
            cursor.execute("""
                INSERT INTO training_programs
                (program_name, program_type, description, instructor,
                 start_date, end_date, duration_hours, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'planned')
            """, program)
        except Exception as e:
            print(f"  교육 프로그램 추가 오류: {program[0]} - {e}")
    
    print(f"  ✅ {len(training_programs)}개 교육 프로그램 추가 완료")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 모든 인사관리 샘플 데이터 추가 완료!")

if __name__ == "__main__":
    print("🔧 인사관리 샘플 데이터 추가 시작...\n")
    
    # 테이블이 없으면 먼저 생성
    if os.path.exists('scripts/create_hr_tables.py'):
        from create_hr_tables import create_hr_tables
        create_hr_tables()
    
    # 샘플 데이터 추가
    add_hr_sample_data()
