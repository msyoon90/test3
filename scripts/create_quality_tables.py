# File: scripts/create_quality_tables.py
# 품질관리 모듈 테이블 생성 스크립트 - V1.1

import sqlite3
import os
import logging
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_quality_tables():
    """품질관리 관련 테이블 생성"""
    
    # 데이터베이스 경로
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')
    
    # 데이터 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 입고검사 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incoming_inspection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_no TEXT UNIQUE NOT NULL,
                inspection_date DATE NOT NULL,
                po_number TEXT,
                item_code TEXT NOT NULL,
                lot_number TEXT,
                received_qty INTEGER NOT NULL,
                sample_qty INTEGER NOT NULL,
                passed_qty INTEGER NOT NULL,
                failed_qty INTEGER DEFAULT 0,
                inspection_result TEXT NOT NULL,  -- pass, fail, conditional
                defect_codes TEXT,
                inspector_id INTEGER,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_code) REFERENCES item_master (item_code),
                FOREIGN KEY (inspector_id) REFERENCES users (id)
            )
        ''')
        logger.info("✓ incoming_inspection 테이블 생성 완료")
        
        # 2. 공정검사 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_inspection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_no TEXT UNIQUE NOT NULL,
                inspection_date DATE NOT NULL,
                work_order_no TEXT,
                process_code TEXT,
                item_code TEXT NOT NULL,
                lot_number TEXT,
                production_qty INTEGER NOT NULL,
                sample_qty INTEGER NOT NULL,
                passed_qty INTEGER NOT NULL,
                failed_qty INTEGER DEFAULT 0,
                inspection_result TEXT NOT NULL,
                defect_codes TEXT,
                inspector_id INTEGER,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_code) REFERENCES item_master (item_code),
                FOREIGN KEY (inspector_id) REFERENCES users (id)
            )
        ''')
        logger.info("✓ process_inspection 테이블 생성 완료")
        
        # 3. 출하검사 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS final_inspection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_no TEXT UNIQUE NOT NULL,
                inspection_date DATE NOT NULL,
                order_number TEXT,
                product_code TEXT NOT NULL,
                lot_number TEXT,
                inspection_qty INTEGER NOT NULL,
                sample_qty INTEGER NOT NULL,
                passed_qty INTEGER NOT NULL,
                failed_qty INTEGER DEFAULT 0,
                inspection_result TEXT NOT NULL,
                defect_codes TEXT,
                inspector_id INTEGER,
                certificate_no TEXT,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inspector_id) REFERENCES users (id)
            )
        ''')
        logger.info("✓ final_inspection 테이블 생성 완료")
        
        # 4. 불량유형 마스터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS defect_types (
                defect_code TEXT PRIMARY KEY,
                defect_name TEXT NOT NULL,
                defect_category TEXT,  -- appearance, dimension, function, material
                severity_level INTEGER DEFAULT 3,  -- 1: Critical, 2: Major, 3: Minor
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ defect_types 테이블 생성 완료")
        
        # 5. 불량이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS defect_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                defect_date DATE NOT NULL,
                inspection_no TEXT,
                defect_code TEXT NOT NULL,
                item_code TEXT,
                defect_qty INTEGER NOT NULL,
                defect_location TEXT,
                cause_analysis TEXT,
                corrective_action TEXT,
                prevention_action TEXT,
                responsible_person TEXT,
                status TEXT DEFAULT 'open',  -- open, in_progress, closed
                closed_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (defect_code) REFERENCES defect_types (defect_code)
            )
        ''')
        logger.info("✓ defect_history 테이블 생성 완료")
        
        # 6. SPC 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spc_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_date TIMESTAMP NOT NULL,
                process_code TEXT NOT NULL,
                item_code TEXT NOT NULL,
                characteristic TEXT NOT NULL,  -- length, width, thickness, weight, etc.
                measurement_value REAL NOT NULL,
                sample_no INTEGER,
                subgroup_no INTEGER,
                usl REAL,  -- Upper Specification Limit
                lsl REAL,  -- Lower Specification Limit
                target REAL,
                operator_id INTEGER,
                equipment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operator_id) REFERENCES users (id)
            )
        ''')
        logger.info("✓ spc_data 테이블 생성 완료")
        
        # 7. 품질 성적서 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_certificates (
                certificate_no TEXT PRIMARY KEY,
                issue_date DATE NOT NULL,
                customer_code TEXT,
                order_number TEXT,
                product_code TEXT NOT NULL,
                lot_number TEXT,
                test_items TEXT,  -- JSON format
                test_results TEXT,  -- JSON format
                overall_result TEXT NOT NULL,  -- pass, fail
                issued_by INTEGER,
                approved_by INTEGER,
                file_path TEXT,
                status TEXT DEFAULT 'draft',  -- draft, issued, cancelled
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (issued_by) REFERENCES users (id),
                FOREIGN KEY (approved_by) REFERENCES users (id)
            )
        ''')
        logger.info("✓ quality_certificates 테이블 생성 완료")
        
        # 8. 측정장비 마스터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurement_equipment (
                equipment_id TEXT PRIMARY KEY,
                equipment_name TEXT NOT NULL,
                equipment_type TEXT,
                manufacturer TEXT,
                model_no TEXT,
                serial_no TEXT,
                calibration_cycle INTEGER DEFAULT 365,  -- days
                last_calibration_date DATE,
                next_calibration_date DATE,
                calibration_certificate_no TEXT,
                location TEXT,
                status TEXT DEFAULT 'active',  -- active, calibrating, repair, retired
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ measurement_equipment 테이블 생성 완료")
        
        # 9. 검사기준 마스터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inspection_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT NOT NULL,
                inspection_type TEXT NOT NULL,  -- incoming, process, final
                inspection_item TEXT NOT NULL,
                inspection_method TEXT,
                standard_value TEXT,
                tolerance_upper REAL,
                tolerance_lower REAL,
                sampling_plan TEXT,
                aql REAL,  -- Acceptable Quality Level
                is_critical BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_code) REFERENCES item_master (item_code)
            )
        ''')
        logger.info("✓ inspection_standards 테이블 생성 완료")
        
        # 10. 품질 비용 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cost_date DATE NOT NULL,
                cost_category TEXT NOT NULL,  -- prevention, appraisal, internal_failure, external_failure
                cost_item TEXT NOT NULL,
                amount REAL NOT NULL,
                department TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ quality_costs 테이블 생성 완료")
        
        # 기본 불량유형 데이터 삽입
        cursor.execute("SELECT COUNT(*) FROM defect_types")
        if cursor.fetchone()[0] == 0:
            defect_types = [
                ('DEF001', '외관불량', 'appearance', 3, '제품 외관상의 결함'),
                ('DEF002', '치수불량', 'dimension', 2, '규격 치수 벗어남'),
                ('DEF003', '기능불량', 'function', 1, '제품 기능 이상'),
                ('DEF004', '재료불량', 'material', 2, '원재료 품질 불량'),
                ('DEF005', '포장불량', 'appearance', 3, '포장 상태 불량'),
                ('DEF006', '라벨불량', 'appearance', 3, '라벨 인쇄 또는 부착 불량'),
                ('DEF007', '조립불량', 'function', 2, '부품 조립 상태 불량'),
                ('DEF008', '도장불량', 'appearance', 3, '도장 상태 불량'),
                ('DEF009', '용접불량', 'function', 1, '용접 품질 불량'),
                ('DEF010', '전기불량', 'function', 1, '전기적 특성 불량')
            ]
            cursor.executemany(
                "INSERT INTO defect_types (defect_code, defect_name, defect_category, severity_level, description) VALUES (?, ?, ?, ?, ?)",
                defect_types
            )
            logger.info("✓ 기본 불량유형 데이터 삽입 완료")
        
        # 샘플 측정장비 데이터 삽입
        cursor.execute("SELECT COUNT(*) FROM measurement_equipment")
        if cursor.fetchone()[0] == 0:
            equipment = [
                ('EQ001', '버니어 캘리퍼스', 'dimension', 'Mitutoyo', 'CD-15CPX', 'SN12345', 365, 
                 '2024-01-15', '2025-01-15', 'CERT-2024-001', '품질관리실', 'active'),
                ('EQ002', '마이크로미터', 'dimension', 'Mitutoyo', 'MDC-25PX', 'SN23456', 365,
                 '2024-02-20', '2025-02-20', 'CERT-2024-002', '품질관리실', 'active'),
                ('EQ003', '하이트 게이지', 'dimension', 'Mitutoyo', 'HDS-20C', 'SN34567', 365,
                 '2024-03-10', '2025-03-10', 'CERT-2024-003', '품질관리실', 'active'),
                ('EQ004', '경도계', 'material', 'Mitutoyo', 'HR-320MS', 'SN45678', 730,
                 '2023-12-01', '2025-12-01', 'CERT-2023-004', '시험실', 'active'),
                ('EQ005', '전자저울', 'weight', 'AND', 'GX-6000', 'SN56789', 365,
                 '2024-04-05', '2025-04-05', 'CERT-2024-005', '품질관리실', 'active')
            ]
            cursor.executemany(
                """INSERT INTO measurement_equipment 
                   (equipment_id, equipment_name, equipment_type, manufacturer, model_no, 
                    serial_no, calibration_cycle, last_calibration_date, next_calibration_date,
                    calibration_certificate_no, location, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                equipment
            )
            logger.info("✓ 샘플 측정장비 데이터 삽입 완료")
        
        conn.commit()
        logger.info("\n✅ 품질관리 테이블 생성 완료!")
        
    except Exception as e:
        logger.error(f"❌ 테이블 생성 중 오류 발생: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_sample_quality_data():
    """샘플 품질 데이터 추가"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 샘플 입고검사 데이터
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        incoming_inspections = [
            (f'INC-{today.replace("-", "")}-0001', today, 'PO-2024-001', 'ITEM001', 'LOT-001', 
             100, 10, 10, 0, 'pass', None, 1, '전량 합격'),
            (f'INC-{yesterday.replace("-", "")}-0001', yesterday, 'PO-2024-002', 'ITEM002', 'LOT-002',
             200, 20, 19, 1, 'conditional', 'DEF001', 1, '조건부 합격')
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO incoming_inspection 
               (inspection_no, inspection_date, po_number, item_code, lot_number,
                received_qty, sample_qty, passed_qty, failed_qty, inspection_result,
                defect_codes, inspector_id, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            incoming_inspections
        )
        
        # 샘플 SPC 데이터
        spc_data = []
        base_time = datetime.now()
        for i in range(50):
            timestamp = (base_time - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
            value = 10.0 + (i % 5) * 0.02 + (-0.05 if i % 7 == 0 else 0)
            spc_data.append(
                (timestamp, 'PROC-001', 'ITEM001', 'length', value, i % 5 + 1, i // 5 + 1,
                 10.3, 9.7, 10.0, 1, 'EQ001')
            )
        
        cursor.executemany(
            """INSERT OR IGNORE INTO spc_data
               (measurement_date, process_code, item_code, characteristic, measurement_value,
                sample_no, subgroup_no, usl, lsl, target, operator_id, equipment_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            spc_data
        )
        
        conn.commit()
        logger.info("✓ 샘플 품질 데이터 추가 완료")
        
    except Exception as e:
        logger.error(f"샘플 데이터 추가 중 오류: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("품질관리 테이블 생성 시작...")
    create_quality_tables()
    
    # 샘플 데이터 추가 옵션
    response = input("\n샘플 데이터를 추가하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        add_sample_quality_data()
    
    logger.info("\n✅ 품질관리 모듈 초기화 완료!")
