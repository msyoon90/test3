# scripts/create_hr_tables.py - 인사관리 테이블 생성

import sqlite3
import os

def create_hr_tables():
    """인사관리 관련 테이블 생성"""
    # data 폴더가 없으면 생성
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("인사관리 테이블 생성 중...")
    
    # 1. 직원 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            name_en TEXT,
            resident_no TEXT,  -- 암호화 저장
            gender TEXT CHECK(gender IN ('M', 'F')),
            birth_date DATE,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            join_date DATE NOT NULL,
            resignation_date DATE,
            employment_type TEXT DEFAULT 'regular',  -- regular, contract, parttime, intern
            employment_status TEXT DEFAULT 'active',  -- active, leave, resigned
            base_salary REAL DEFAULT 0,
            mobile_phone TEXT,
            email TEXT,
            address TEXT,
            bank_name TEXT,
            bank_account TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ employees 테이블 생성")
    
    # 2. 부서 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            dept_code TEXT PRIMARY KEY,
            dept_name TEXT NOT NULL,
            parent_dept TEXT,
            dept_head_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dept_head_id) REFERENCES employees (employee_id)
        )
    ''')
    print("  ✅ departments 테이블 생성")
    
    # 3. 직급 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            position_code TEXT PRIMARY KEY,
            position_name TEXT NOT NULL,
            position_level INTEGER,
            min_salary REAL,
            max_salary REAL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ positions 테이블 생성")
    
    # 4. 근태 기록
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            attendance_date DATE NOT NULL,
            check_in_time TIME,
            check_out_time TIME,
            attendance_type TEXT DEFAULT 'normal',  -- normal, late, early, absent, leave, business
            overtime_hours REAL DEFAULT 0,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            UNIQUE(employee_id, attendance_date)
        )
    ''')
    print("  ✅ attendance 테이블 생성")
    
    # 5. 휴가 신청
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,  -- annual, sick, special, official, unpaid
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            leave_days REAL NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',  -- pending, approved, rejected, cancelled
            approver_id TEXT,
            approved_date TIMESTAMP,
            reject_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            FOREIGN KEY (approver_id) REFERENCES employees (employee_id)
        )
    ''')
    print("  ✅ leave_requests 테이블 생성")
    
    # 6. 연차 관리
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annual_leave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            total_days REAL DEFAULT 15,
            used_days REAL DEFAULT 0,
            remaining_days REAL DEFAULT 15,
            carried_over REAL DEFAULT 0,
            adjustment_days REAL DEFAULT 0,
            adjustment_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            UNIQUE(employee_id, year)
        )
    ''')
    print("  ✅ annual_leave 테이블 생성")
    
    # 7. 급여 대장
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            pay_year INTEGER NOT NULL,
            pay_month INTEGER NOT NULL,
            base_salary REAL DEFAULT 0,
            overtime_pay REAL DEFAULT 0,
            bonus REAL DEFAULT 0,
            allowances REAL DEFAULT 0,
            gross_salary REAL DEFAULT 0,
            income_tax REAL DEFAULT 0,
            health_insurance REAL DEFAULT 0,
            pension REAL DEFAULT 0,
            employment_insurance REAL DEFAULT 0,
            other_deductions REAL DEFAULT 0,
            net_salary REAL DEFAULT 0,
            insurance_company REAL DEFAULT 0,  -- 회사 부담 보험료
            pay_date DATE,
            status TEXT DEFAULT 'draft',  -- draft, confirmed, paid
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            UNIQUE(employee_id, pay_year, pay_month)
        )
    ''')
    print("  ✅ payroll 테이블 생성")
    
    # 8. 급여 항목 상세
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,  -- earning, deduction
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            amount REAL DEFAULT 0,
            remarks TEXT,
            FOREIGN KEY (payroll_id) REFERENCES payroll (payroll_id)
        )
    ''')
    print("  ✅ payroll_details 테이블 생성")
    
    # 9. 인사 평가
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_evaluation (
            eval_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            eval_year INTEGER NOT NULL,
            eval_period TEXT NOT NULL,  -- annual, semi-annual, quarterly
            evaluator_id TEXT NOT NULL,
            eval_type TEXT NOT NULL,  -- supervisor, peer, self, subordinate
            performance_score INTEGER,
            competency_score INTEGER,
            overall_score INTEGER,
            grade TEXT,  -- S, A, B, C, D
            strengths TEXT,
            improvements TEXT,
            development_plan TEXT,
            status TEXT DEFAULT 'draft',  -- draft, submitted, confirmed
            submitted_date TIMESTAMP,
            confirmed_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            FOREIGN KEY (evaluator_id) REFERENCES employees (employee_id)
        )
    ''')
    print("  ✅ performance_evaluation 테이블 생성")
    
    # 10. 교육 훈련
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_programs (
            program_id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT NOT NULL,
            program_type TEXT,  -- mandatory, optional, external, internal
            description TEXT,
            instructor TEXT,
            start_date DATE,
            end_date DATE,
            duration_hours INTEGER,
            location TEXT,
            max_participants INTEGER,
            cost REAL DEFAULT 0,
            status TEXT DEFAULT 'planned',  -- planned, ongoing, completed, cancelled
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ training_programs 테이블 생성")
    
    # 11. 교육 이수 기록
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER NOT NULL,
            employee_id TEXT NOT NULL,
            enrollment_date DATE,
            completion_date DATE,
            attendance_rate REAL,
            test_score INTEGER,
            certificate_no TEXT,
            status TEXT DEFAULT 'enrolled',  -- enrolled, completed, failed, dropped
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (program_id) REFERENCES training_programs (program_id),
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
    ''')
    print("  ✅ training_history 테이블 생성")
    
    # 12. 조직 이력
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organization_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            change_date DATE NOT NULL,
            change_type TEXT NOT NULL,  -- join, promotion, transfer, resignation
            from_department TEXT,
            to_department TEXT,
            from_position TEXT,
            to_position TEXT,
            from_salary REAL,
            to_salary REAL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
    ''')
    print("  ✅ organization_history 테이블 생성")
    
    # 13. 근로계약서
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employment_contracts (
            contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            contract_type TEXT NOT NULL,  -- permanent, fixed-term
            start_date DATE NOT NULL,
            end_date DATE,
            position TEXT NOT NULL,
            department TEXT NOT NULL,
            base_salary REAL NOT NULL,
            work_hours_per_week INTEGER DEFAULT 40,
            probation_period INTEGER DEFAULT 3,  -- months
            annual_leave_days INTEGER DEFAULT 15,
            special_terms TEXT,
            file_path TEXT,
            status TEXT DEFAULT 'active',  -- active, expired, terminated
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
    ''')
    print("  ✅ employment_contracts 테이블 생성")
    
    # 14. 복리후생
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benefits (
            benefit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            benefit_name TEXT NOT NULL,
            benefit_type TEXT,  -- insurance, allowance, facility, other
            description TEXT,
            eligibility TEXT,
            amount REAL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ benefits 테이블 생성")
    
    # 15. 직원 복리후생
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_benefits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            benefit_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
            FOREIGN KEY (benefit_id) REFERENCES benefits (benefit_id)
        )
    ''')
    print("  ✅ employee_benefits 테이블 생성")
    
    conn.commit()
    conn.close()
    print("\n✅ 인사관리 테이블 생성 완료!")

if __name__ == "__main__":
    create_hr_tables()
