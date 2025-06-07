# File: scripts/create_quality_tables.py
# 품질관리 모듈 테이블 생성 스크립트

import sqlite3
import os

def create_quality_tables():
    """품질관리 관련 테이블 생성"""
    # data 폴더가 없으면 생성
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    print("품질관리 테이블 생성 중...")
    
    # 1. 검사 기준 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL,
            inspection_type TEXT NOT NULL,  -- incoming, process, final
            inspection_item TEXT NOT NULL,
            standard_value TEXT,
            upper_limit REAL,
            lower_limit REAL,
            unit TEXT,
            inspection_method TEXT,
            sampling_rate REAL DEFAULT 100,  -- 검사 비율 (%)
            is_critical BOOLEAN DEFAULT 0,   -- 중요 검사 항목
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    print("  ✅ inspection_standards 테이블 생성")
    
    # 2. 입고 검사
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incoming_inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_no TEXT UNIQUE NOT NULL,
            inspection_date DATE NOT NULL,
            po_number TEXT NOT NULL,
            item_code TEXT NOT NULL,
            lot_number TEXT,
            received_qty INTEGER NOT NULL,
            sample_qty INTEGER NOT NULL,
            passed_qty INTEGER NOT NULL,
            failed_qty INTEGER DEFAULT 0,
            inspection_result TEXT NOT NULL,  -- pass, fail, conditional
            defect_type TEXT,
            defect_description TEXT,
            inspector_id INTEGER,
            approval_status TEXT DEFAULT 'pending',  -- pending, approved, rejected
            approved_by INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (inspector_id) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    print("  ✅ incoming_inspection 테이블 생성")
    
    # 3. 공정 검사
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS process_inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_no TEXT UNIQUE NOT NULL,
            inspection_date DATE NOT NULL,
            work_order_no TEXT,
            process_name TEXT NOT NULL,
            item_code TEXT NOT NULL,
            lot_number TEXT,
            production_qty INTEGER NOT NULL,
            sample_qty INTEGER NOT NULL,
            passed_qty INTEGER NOT NULL,
            failed_qty INTEGER DEFAULT 0,
            inspection_result TEXT NOT NULL,  -- pass, fail, rework
            measurement_data TEXT,  -- JSON 형태로 측정값 저장
            spc_data TEXT,         -- SPC 차트 데이터
            inspector_id INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (inspector_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ process_inspection 테이블 생성")
    
    # 4. 출하 검사
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS final_inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_no TEXT UNIQUE NOT NULL,
            inspection_date DATE NOT NULL,
            order_number TEXT,
            product_code TEXT NOT NULL,
            lot_number TEXT,
            production_date DATE,
            inspection_qty INTEGER NOT NULL,
            sample_qty INTEGER NOT NULL,
            passed_qty INTEGER NOT NULL,
            failed_qty INTEGER DEFAULT 0,
            inspection_result TEXT NOT NULL,  -- pass, fail, hold
            certificate_no TEXT,  -- 성적서 번호
            inspector_id INTEGER,
            qa_manager_id INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES sales_orders (order_number),
            FOREIGN KEY (inspector_id) REFERENCES users (id),
            FOREIGN KEY (qa_manager_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ final_inspection 테이블 생성")
    
    # 5. 불량 유형 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_types (
            defect_code TEXT PRIMARY KEY,
            defect_name TEXT NOT NULL,
            defect_category TEXT,  -- appearance, dimension, function, material
            severity_level INTEGER DEFAULT 3,  -- 1: Critical, 2: Major, 3: Minor
            description TEXT,
            corrective_action TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ defect_types 테이블 생성")
    
    # 6. 불량 이력
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_type TEXT NOT NULL,  -- incoming, process, final
            inspection_no TEXT NOT NULL,
            defect_date DATE NOT NULL,
            item_code TEXT NOT NULL,
            defect_code TEXT NOT NULL,
            defect_qty INTEGER NOT NULL,
            defect_rate REAL,
            cause_analysis TEXT,
            corrective_action TEXT,
            preventive_action TEXT,
            responsible_dept TEXT,
            status TEXT DEFAULT 'open',  -- open, in_progress, closed
            closed_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (defect_code) REFERENCES defect_types (defect_code)
        )
    ''')
    print("  ✅ defect_history 테이블 생성")
    
    # 7. SPC (통계적 공정 관리) 데이터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spc_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measurement_date DATE NOT NULL,
            process_name TEXT NOT NULL,
            item_code TEXT NOT NULL,
            characteristic TEXT NOT NULL,  -- 측정 특성
            sample_no INTEGER NOT NULL,
            measurement_value REAL NOT NULL,
            ucl REAL,  -- Upper Control Limit
            lcl REAL,  -- Lower Control Limit
            cl REAL,   -- Center Line
            usl REAL,  -- Upper Spec Limit
            lsl REAL,  -- Lower Spec Limit
            cp REAL,   -- Process Capability
            cpk REAL,  -- Process Capability Index
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    print("  ✅ spc_data 테이블 생성")
    
    # 8. 품질 성적서
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_certificates (
            certificate_no TEXT PRIMARY KEY,
            issue_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            order_number TEXT,
            product_code TEXT NOT NULL,
            lot_number TEXT NOT NULL,
            production_date DATE,
            inspection_date DATE,
            test_items TEXT,  -- JSON 형태로 시험 항목 및 결과 저장
            overall_result TEXT NOT NULL,  -- pass, fail
            issuer_id INTEGER,
            qa_manager_id INTEGER,
            remarks TEXT,
            is_sent BOOLEAN DEFAULT 0,
            sent_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (order_number) REFERENCES sales_orders (order_number),
            FOREIGN KEY (issuer_id) REFERENCES users (id),
            FOREIGN KEY (qa_manager_id) REFERENCES users (id)
        )
    ''')
    print("  ✅ quality_certificates 테이블 생성")
    
    # 9. 측정 장비 관리
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurement_equipment (
            equipment_id TEXT PRIMARY KEY,
            equipment_name TEXT NOT NULL,
            equipment_type TEXT,
            manufacturer TEXT,
            model_no TEXT,
            serial_no TEXT,
            calibration_date DATE,
            next_calibration_date DATE,
            calibration_cycle INTEGER DEFAULT 365,  -- 교정 주기 (일)
            location TEXT,
            status TEXT DEFAULT 'active',  -- active, calibrating, repair, inactive
            responsible_person INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (responsible_person) REFERENCES users (id)
        )
    ''')
    print("  ✅ measurement_equipment 테이블 생성")
    
    # 10. 품질 목표 및 KPI
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_kpi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kpi_year INTEGER NOT NULL,
            kpi_month INTEGER,
            kpi_type TEXT NOT NULL,  -- defect_rate, customer_complaint, process_capability
            target_value REAL NOT NULL,
            actual_value REAL DEFAULT 0,
            achievement_rate REAL DEFAULT 0,
            department TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ quality_kpi 테이블 생성")
    
    # 샘플 불량 유형 데이터 추가
    cursor.execute("SELECT COUNT(*) FROM defect_types")
    if cursor.fetchone()[0] == 0:
        sample_defects = [
            ('D001', '치수 불량', 'dimension', 2, '규격 치수 벗어남', '재가공 또는 폐기'),
            ('D002', '외관 불량', 'appearance', 3, '스크래치, 찍힘, 변색', '재작업 가능시 보수'),
            ('D003', '기능 불량', 'function', 1, '작동 불량, 성능 미달', '원인 분석 후 재제작'),
            ('D004', '재료 불량', 'material', 2, '재질 불량, 이물질 혼입', '재료 교체 및 재생산'),
            ('D005', '포장 불량', 'appearance', 3, '포장 파손, 라벨 오류', '재포장')
        ]
        cursor.executemany(
            "INSERT INTO defect_types (defect_code, defect_name, defect_category, severity_level, description, corrective_action) VALUES (?, ?, ?, ?, ?, ?)",
            sample_defects
        )
        print("  ✅ 샘플 불량 유형 데이터 추가")
    
    # 샘플 측정 장비 데이터 추가
    cursor.execute("SELECT COUNT(*) FROM measurement_equipment")
    if cursor.fetchone()[0] == 0:
        sample_equipment = [
            ('EQ001', '버니어 캘리퍼스', '치수측정', 'Mitutoyo', 'CD-15CPX', 'SN12345', '2025-01-15', '2026-01-15', 365, '품질관리실', 'active'),
            ('EQ002', '마이크로미터', '치수측정', 'Mitutoyo', 'MDC-25PX', 'SN23456', '2025-01-15', '2026-01-15', 365, '품질관리실', 'active'),
            ('EQ003', '표면조도계', '표면측정', 'Mitutoyo', 'SJ-210', 'SN34567', '2025-02-01', '2026-02-01', 365, '품질관리실', 'active'),
            ('EQ004', '경도시험기', '경도측정', 'Mitutoyo', 'HR-522', 'SN45678', '2025-03-01', '2026-03-01', 365, '시험실', 'active')
        ]
        cursor.executemany(
            "INSERT INTO measurement_equipment (equipment_id, equipment_name, equipment_type, manufacturer, model_no, serial_no, calibration_date, next_calibration_date, calibration_cycle, location, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            sample_equipment
        )
        print("  ✅ 샘플 측정 장비 데이터 추가")
    
    conn.commit()
    conn.close()
    print("\n✅ 품질관리 테이블 생성 완료!")

if __name__ == "__main__":
    create_quality_tables()
