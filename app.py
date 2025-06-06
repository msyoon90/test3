# app.py - Smart MES-ERP V1.2 메인 애플리케이션 (인사관리 모듈 + REST API 추가)

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import yaml
import os
import sqlite3
import json
import logging
from flask import session
import secrets
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import hashlib
import threading

# 로깅 설정
import os
os.makedirs('logs', exist_ok=True)  # logs 디렉토리 자동 생성

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 설정 파일 로드
def load_config():
    """설정 파일 로드"""
    default_config = {
        'system': {
            'name': 'Smart MES-ERP',
            'version': '1.2.0',
            'language': 'ko',
            'update_interval': 2000  # 2초
        },
        'modules': {
            'mes': True,
            'inventory': True,
            'purchase': True,
            'sales': True,
            'accounting': True,
            'quality': True,  # V1.1
            'hr': True  # V1.2
        },
        'authentication': {
            'enabled': True,
            'session_timeout': 30,
            'jwt_secret_key': secrets.token_urlsafe(32),
            'jwt_access_token_expires': 3600
        },
        'api': {  # V1.2
            'enabled': True,
            'host': '0.0.0.0',
            'port': 5001,
            'cors_origins': ['http://localhost:8050', 'http://localhost:3000'],
            'rate_limit': '100 per hour',
            'documentation': True
        },
        'database': {
            'path': 'data/database.db'
        },
        'sales': {
            'quote_validity_days': 30,
            'auto_quote_number': True,
            'customer_grades': {
                'VIP': 15,
                'Gold': 10,
                'Silver': 5,
                'Bronze': 0
            }
        },
        'quality': {  # V1.1
            'default_sampling_rate': 10,
            'target_defect_rate': 2.0,
            'spc_rules': ['rule1', 'rule2'],
            'calibration_reminder_days': 30
        },
        'hr': {  # V1.2
            'work_hours': {
                'start': '09:00',
                'end': '18:00',
                'break_time': 60
            },
            'overtime': {
                'weekday_rate': 1.5,
                'weekend_rate': 2.0,
                'holiday_rate': 2.5
            },
            'leave': {
                'annual_days': 15,
                'sick_leave_days': 10,
                'special_leave_days': 5
            },
            'payroll': {
                'pay_day': 25,
                'tax_rate': 0.033,
                'insurance_rates': {
                    'health': 0.0343,
                    'pension': 0.045,
                    'employment': 0.008,
                    'accident': 0.007
                }
            }
        }
    }
    
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # 기본값과 병합
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
                elif isinstance(default_config[key], dict):
                    for subkey in default_config[key]:
                        if subkey not in config[key]:
                            config[key][subkey] = default_config[key][subkey]
    else:
        config = default_config
        save_config(config)
    
    return config

def save_config(config):
    """설정 파일 저장"""
    os.makedirs(os.path.dirname('config.yaml'), exist_ok=True)
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

# 데이터베이스 초기화
def init_database():
    """데이터베이스 초기화"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 기본 시스템 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            department TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 작업 로그 테이블 (MES)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_number TEXT NOT NULL,
            work_date DATE NOT NULL,
            process TEXT NOT NULL,
            worker_id INTEGER,
            plan_qty INTEGER,
            prod_qty INTEGER,
            defect_qty INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES users (id)
        )
    ''')
    
    # 시스템 설정 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 폼 템플릿 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            config TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 품목 마스터 테이블 (재고관리용)
    cursor.execute('''
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
    ''')
    
    # 재고 이동 테이블
    cursor.execute('''
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
    ''')
    
    # 재고 조정 테이블
    cursor.execute('''
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
    ''')
    
    # 거래처 마스터 (구매관리)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_master (
            supplier_code TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            business_no TEXT,
            ceo_name TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            payment_terms TEXT DEFAULT 'CASH',
            lead_time INTEGER DEFAULT 7,
            rating INTEGER DEFAULT 3,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 발주서 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            po_number TEXT PRIMARY KEY,
            po_date DATE NOT NULL,
            supplier_code TEXT NOT NULL,
            delivery_date DATE,
            warehouse TEXT,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            approved_by INTEGER,
            approved_date TIMESTAMP,
            remarks TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_code) REFERENCES supplier_master (supplier_code)
        )
    ''')
    
    # 발주서 상세
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT NOT NULL,
            item_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            amount REAL NOT NULL,
            received_qty INTEGER DEFAULT 0,
            remarks TEXT,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    # 입고 예정
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receiving_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT NOT NULL,
            scheduled_date DATE NOT NULL,
            item_code TEXT NOT NULL,
            expected_qty INTEGER NOT NULL,
            received_qty INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    # 입고 검수
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receiving_inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receiving_date DATE NOT NULL,
            po_number TEXT NOT NULL,
            item_code TEXT NOT NULL,
            received_qty INTEGER NOT NULL,
            accepted_qty INTEGER NOT NULL,
            rejected_qty INTEGER DEFAULT 0,
            inspection_result TEXT,
            inspector_id INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_number) REFERENCES purchase_orders (po_number),
            FOREIGN KEY (item_code) REFERENCES item_master (item_code)
        )
    ''')
    
    # 자동 발주 규칙
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto_po_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL,
            supplier_code TEXT NOT NULL,
            reorder_point INTEGER NOT NULL,
            order_qty INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (supplier_code) REFERENCES supplier_master (supplier_code)
        )
    ''')
    
    # 계정과목 마스터 (회계관리)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_master (
            account_code TEXT PRIMARY KEY,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            parent_code TEXT,
            level INTEGER DEFAULT 1,
            is_control BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 전표 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_header (
            voucher_no TEXT PRIMARY KEY,
            voucher_date DATE NOT NULL,
            voucher_type TEXT NOT NULL,
            description TEXT,
            total_debit REAL DEFAULT 0,
            total_credit REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_by INTEGER,
            approved_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    # 전표 상세
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_no TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            account_code TEXT NOT NULL,
            debit_amount REAL DEFAULT 0,
            credit_amount REAL DEFAULT 0,
            description TEXT,
            cost_center TEXT,
            FOREIGN KEY (voucher_no) REFERENCES journal_header (voucher_no),
            FOREIGN KEY (account_code) REFERENCES account_master (account_code)
        )
    ''')
    
    # 세금계산서
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tax_invoice (
            invoice_no TEXT PRIMARY KEY,
            invoice_date DATE NOT NULL,
            invoice_type TEXT NOT NULL,
            customer_code TEXT,
            supplier_code TEXT,
            business_no TEXT,
            company_name TEXT,
            ceo_name TEXT,
            address TEXT,
            supply_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            voucher_no TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (voucher_no) REFERENCES journal_header (voucher_no)
        )
    ''')
    
    # 예산 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_master (
            budget_id TEXT PRIMARY KEY,
            budget_year INTEGER NOT NULL,
            budget_month INTEGER,
            department TEXT,
            account_code TEXT NOT NULL,
            budget_amount REAL DEFAULT 0,
            actual_amount REAL DEFAULT 0,
            variance REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_code) REFERENCES account_master (account_code)
        )
    ''')
    
    # 원가 계산
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cost_calculation (
            calc_id TEXT PRIMARY KEY,
            calc_date DATE NOT NULL,
            product_code TEXT NOT NULL,
            material_cost REAL DEFAULT 0,
            labor_cost REAL DEFAULT 0,
            overhead_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            production_qty INTEGER DEFAULT 0,
            unit_cost REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 결산 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS closing_master (
            closing_id TEXT PRIMARY KEY,
            closing_year INTEGER NOT NULL,
            closing_month INTEGER NOT NULL,
            closing_type TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            closed_date TIMESTAMP,
            closed_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (closed_by) REFERENCES users (id)
        )
    ''')
    
    # 고정자산 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fixed_asset (
            asset_code TEXT PRIMARY KEY,
            asset_name TEXT NOT NULL,
            asset_type TEXT,
            acquisition_date DATE NOT NULL,
            acquisition_cost REAL DEFAULT 0,
            depreciation_method TEXT DEFAULT 'straight',
            useful_life INTEGER DEFAULT 5,
            salvage_value REAL DEFAULT 0,
            accumulated_depreciation REAL DEFAULT 0,
            book_value REAL DEFAULT 0,
            disposal_date DATE,
            disposal_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # === V1.1 품질관리 테이블 ===
    
    # 입고검사 테이블
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
            inspection_result TEXT NOT NULL,
            defect_codes TEXT,
            inspector_id INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_code) REFERENCES item_master (item_code),
            FOREIGN KEY (inspector_id) REFERENCES users (id)
        )
    ''')
    
    # 공정검사 테이블
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
    
    # 출하검사 테이블
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
    
    # 불량유형 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_types (
            defect_code TEXT PRIMARY KEY,
            defect_name TEXT NOT NULL,
            defect_category TEXT,
            severity_level INTEGER DEFAULT 3,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 불량이력 테이블
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
            status TEXT DEFAULT 'open',
            closed_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (defect_code) REFERENCES defect_types (defect_code)
        )
    ''')
    
    # 측정장비 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurement_equipment (
            equipment_id TEXT PRIMARY KEY,
            equipment_name TEXT NOT NULL,
            equipment_type TEXT,
            manufacturer TEXT,
            model_no TEXT,
            serial_no TEXT,
            calibration_cycle INTEGER DEFAULT 365,
            last_calibration_date DATE,
            next_calibration_date DATE,
            calibration_certificate_no TEXT,
            location TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # SPC 데이터 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spc_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measurement_date TIMESTAMP NOT NULL,
            process_code TEXT NOT NULL,
            item_code TEXT NOT NULL,
            characteristic TEXT NOT NULL,
            measurement_value REAL NOT NULL,
            sample_no INTEGER,
            subgroup_no INTEGER,
            usl REAL,
            lsl REAL,
            target REAL,
            operator_id INTEGER,
            equipment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (operator_id) REFERENCES users (id)
        )
    ''')
    
    # 품질 성적서 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_certificates (
            certificate_no TEXT PRIMARY KEY,
            issue_date DATE NOT NULL,
            customer_code TEXT,
            order_number TEXT,
            product_code TEXT NOT NULL,
            lot_number TEXT,
            test_items TEXT,
            test_results TEXT,
            overall_result TEXT NOT NULL,
            issued_by INTEGER,
            approved_by INTEGER,
            file_path TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issued_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    # === V1.0 영업관리 테이블 ===
    
    # 고객 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_code TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            business_no TEXT,
            ceo_name TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            grade TEXT DEFAULT 'Bronze',  -- VIP, Gold, Silver, Bronze
            payment_terms TEXT DEFAULT 'NET30',
            credit_limit REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 견적서 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            quote_number TEXT PRIMARY KEY,
            quote_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            validity_date DATE NOT NULL,
            total_amount REAL DEFAULT 0,
            discount_rate REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',  -- draft, sent, reviewing, won, lost, expired
            notes TEXT,
            created_by INTEGER,
            approved_by INTEGER,
            approved_date TIMESTAMP,
            sent_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    # 견적서 상세
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotation_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_number TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            product_code TEXT,
            product_name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (quote_number) REFERENCES quotations (quote_number)
        )
    ''')
    
    # 수주 헤더
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_orders (
            order_number TEXT PRIMARY KEY,
            order_date DATE NOT NULL,
            customer_code TEXT NOT NULL,
            quote_number TEXT,
            delivery_date DATE,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'received',  -- received, confirmed, in_production, ready_for_delivery, completed, cancelled
            payment_status TEXT DEFAULT 'pending',  -- pending, partial, completed
            shipping_address TEXT,
            notes TEXT,
            created_by INTEGER,
            approved_by INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (quote_number) REFERENCES quotations (quote_number),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    # 수주 상세
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            product_code TEXT,
            product_name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            amount REAL NOT NULL,
            delivered_qty INTEGER DEFAULT 0,
            FOREIGN KEY (order_number) REFERENCES sales_orders (order_number)
        )
    ''')
    
    # 영업 활동
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date DATE NOT NULL,
            activity_type TEXT NOT NULL,  -- call, email, meeting, demo, follow_up
            customer_code TEXT,
            contact_person TEXT,
            subject TEXT,
            description TEXT,
            result TEXT,
            next_action TEXT,
            next_action_date DATE,
            sales_person_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (sales_person_id) REFERENCES users (id)
        )
    ''')
    
    # 영업 기회 (Opportunity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_name TEXT NOT NULL,
            customer_code TEXT NOT NULL,
            estimated_amount REAL DEFAULT 0,
            probability INTEGER DEFAULT 50,  -- 0-100%
            expected_close_date DATE,
            stage TEXT DEFAULT 'prospecting',  -- prospecting, qualification, proposal, negotiation, closed_won, closed_lost
            source TEXT,  -- referral, website, cold_call, exhibition, etc.
            competitor TEXT,
            sales_person_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (sales_person_id) REFERENCES users (id)
        )
    ''')
    
    # 제품 마스터 (영업용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_code TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            unit_price REAL DEFAULT 0,
            cost_price REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 가격 정책
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL,
            customer_grade TEXT,  -- VIP, Gold, Silver, Bronze
            product_category TEXT,
            discount_rate REAL DEFAULT 0,
            min_quantity INTEGER DEFAULT 1,
            effective_date DATE NOT NULL,
            expiry_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 배송 정보
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_number TEXT UNIQUE NOT NULL,
            order_number TEXT NOT NULL,
            delivery_date DATE,
            tracking_number TEXT,
            delivery_company TEXT,
            delivery_status TEXT DEFAULT 'preparing',  -- preparing, shipped, in_transit, delivered, failed
            recipient_name TEXT,
            recipient_phone TEXT,
            delivery_address TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES sales_orders (order_number)
        )
    ''')
    
    # 고객 연락 이력
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT NOT NULL,
            contact_date DATE NOT NULL,
            contact_type TEXT NOT NULL,  -- phone, email, visit, video_call
            contact_person TEXT,
            subject TEXT,
            content TEXT,
            result TEXT,
            sales_person_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code),
            FOREIGN KEY (sales_person_id) REFERENCES users (id)
        )
    ''')
    
    # 매출 목표
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_year INTEGER NOT NULL,
            target_month INTEGER,
            sales_person_id INTEGER,
            customer_code TEXT,
            product_category TEXT,
            target_amount REAL NOT NULL,
            actual_amount REAL DEFAULT 0,
            achievement_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sales_person_id) REFERENCES users (id),
            FOREIGN KEY (customer_code) REFERENCES customers (customer_code)
        )
    ''')
    
    # === V1.2 인사관리 테이블 ===
    
    # 직원 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            emp_name TEXT NOT NULL,
            emp_name_en TEXT,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date DATE NOT NULL,
            birth_date DATE,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT,
            employee_type TEXT DEFAULT 'regular',
            work_status TEXT DEFAULT 'active',
            resignation_date DATE,
            photo BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 근태 기록
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            work_date DATE NOT NULL,
            check_in_time TIMESTAMP,
            check_out_time TIMESTAMP,
            work_hours REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            status TEXT DEFAULT 'normal',
            late_minutes INTEGER DEFAULT 0,
            early_leave_minutes INTEGER DEFAULT 0,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
            UNIQUE(emp_id, work_date)
        )
    ''')
    
    # 휴가 신청
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            leave_days REAL NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            approver_id TEXT,
            approval_date TIMESTAMP,
            approval_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
            FOREIGN KEY (approver_id) REFERENCES employees (emp_id)
        )
    ''')
    
    # 급여 정보
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            salary_month TEXT NOT NULL,
            basic_salary REAL DEFAULT 0,
            position_allowance REAL DEFAULT 0,
            meal_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            overtime_pay REAL DEFAULT 0,
            bonus REAL DEFAULT 0,
            other_allowance REAL DEFAULT 0,
            total_earning REAL DEFAULT 0,
            income_tax REAL DEFAULT 0,
            resident_tax REAL DEFAULT 0,
            health_insurance REAL DEFAULT 0,
            pension REAL DEFAULT 0,
            employment_insurance REAL DEFAULT 0,
            accident_insurance REAL DEFAULT 0,
            other_deduction REAL DEFAULT 0,
            total_deduction REAL DEFAULT 0,
            net_salary REAL DEFAULT 0,
            payment_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees (emp_id),
            UNIQUE(emp_id, salary_month)
        )
    ''')
    
    # 부서 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            dept_code TEXT PRIMARY KEY,
            dept_name TEXT NOT NULL,
            dept_name_en TEXT,
            parent_dept TEXT,
            dept_head TEXT,
            location TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dept_head) REFERENCES employees (emp_id)
        )
    ''')
    
    # 직급 마스터
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            position_code TEXT PRIMARY KEY,
            position_name TEXT NOT NULL,
            position_name_en TEXT,
            position_level INTEGER,
            min_salary REAL,
            max_salary REAL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # === V1.2 API 테이블 ===
    
    # API 토큰
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            name TEXT,
            permissions TEXT,
            expires_at TIMESTAMP,
            last_used_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # API 로그
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            user_id INTEGER,
            ip_address TEXT,
            request_body TEXT,
            response_code INTEGER,
            response_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 기본 관리자 계정 생성 (V1.2: 비밀번호 해시화)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password, role, department, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            ('admin', password_hash, 'admin', '경영지원', 'admin@company.com', '010-1234-5678')
        )
    
    # 샘플 품목 데이터 추가
    cursor.execute("SELECT COUNT(*) FROM item_master")
    if cursor.fetchone()[0] == 0:
        sample_items = [
            ('ITEM001', '볼트 M10', '부품', 'EA', 100, 150, 500),
            ('ITEM002', '너트 M10', '부품', 'EA', 100, 200, 300),
            ('ITEM003', '철판 1.0T', '원자재', 'EA', 50, 75, 15000),
            ('ITEM004', '모터 DC24V', '부품', 'EA', 20, 25, 50000),
            ('ITEM005', '베어링 6201', '부품', 'EA', 50, 80, 3000)
        ]
        cursor.executemany(
            "INSERT INTO item_master (item_code, item_name, category, unit, safety_stock, current_stock, unit_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample_items
        )
    
    # 기본 고객 데이터 추가 (V1.0)
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ('CUST001', '(주)테크놀로지', '123-45-67890', '김대표', '이부장', '02-1234-5678', 
             'lee@technology.co.kr', '서울시 강남구 테헤란로 123', 'VIP', 'NET30', 100000000),
            ('CUST002', '글로벌산업(주)', '234-56-78901', '박사장', '최과장', '031-987-6543',
             'choi@global.com', '경기도 수원시 영통구 월드컵로 456', 'Gold', 'NET60', 50000000),
            ('CUST003', '스마트제조', '345-67-89012', '정대표', '김대리', '032-555-1234',
             'kim@smart.kr', '인천시 남동구 논현로 789', 'Silver', 'NET30', 30000000)
        ]
        cursor.executemany(
            "INSERT INTO customers (customer_code, customer_name, business_no, ceo_name, contact_person, phone, email, address, grade, payment_terms, credit_limit, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
            sample_customers
        )
    
    # 기본 제품 데이터 추가 (V1.0)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('PROD001', 'Smart MES 시스템', 'Software', 'MES 솔루션 패키지', 50000000, 30000000),
            ('PROD002', 'ERP 통합 솔루션', 'Software', 'ERP 시스템 구축', 80000000, 50000000),
            ('PROD003', '자동화 제어시스템', 'Hardware', 'PLC 기반 자동화', 30000000, 18000000)
        ]
        cursor.executemany(
            "INSERT INTO products (product_code, product_name, category, description, unit_price, cost_price, is_active) VALUES (?, ?, ?, ?, ?, ?, 1)",
            sample_products
        )
    
    conn.commit()
    conn.close()
    logger.info("데이터베이스 초기화 완료")

# 설정 로드
config = load_config()

# 앱 초기화
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True,
    title=config['system']['name']
)

# 서버 설정
server = app.server
server.secret_key = secrets.token_hex(16)

# 네비게이션 바
def create_navbar():
    """네비게이션 바 생성"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.A(
                        dbc.Row([
                            dbc.Col(html.I(className="fas fa-industry me-2")),
                            dbc.Col(dbc.NavbarBrand(config['system']['name'], className="ms-2")),
                        ], align="center", className="g-0"),
                        href="/",
                        style={"textDecoration": "none"}
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("대시보드", href="/", id="nav-dashboard")),
                        dbc.NavItem(dbc.NavLink("MES", href="/mes", id="nav-mes")) if config['modules']['mes'] else None,
                        dbc.NavItem(dbc.NavLink("재고관리", href="/inventory", id="nav-inventory")) if config['modules']['inventory'] else None,
                        dbc.NavItem(dbc.NavLink("구매관리", href="/purchase", id="nav-purchase")) if config['modules']['purchase'] else None,
                        dbc.NavItem(dbc.NavLink("영업관리", href="/sales", id="nav-sales")) if config['modules']['sales'] else None,
                        dbc.NavItem(dbc.NavLink("품질관리", href="/quality", id="nav-quality")) if config['modules'].get('quality', False) else None,
                        dbc.NavItem(dbc.NavLink("인사관리", href="/hr", id="nav-hr")) if config['modules'].get('hr', False) else None,  # V1.2 추가
                        dbc.NavItem(dbc.NavLink("회계관리", href="/accounting", id="nav-accounting")) if config['modules'].get('accounting', False) else None,
                        dbc.NavItem(dbc.NavLink("설정", href="/settings", id="nav-settings")),
                    ], className="ms-auto", navbar=True),
                    width="auto",
                    className="ms-auto"
                ),
            ], align="center", className="w-100"),
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.I(className="fas fa-user me-2"),
                        html.Span("Guest", id="username-display"),
                        dbc.Button("로그아웃", id="logout-btn", size="sm", className="ms-3", style={"display": "none"})
                    ], className="text-light"),
                    width="auto",
                    className="ms-auto"
                )
            ], className="mt-2") if config['authentication']['enabled'] else html.Div()
        ], fluid=True),
        color="dark",
        dark=True,
        sticky="top"
    )

# 로그인 페이지
def create_login_page():
    """로그인 페이지 생성"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2("로그인", className="text-center mb-4"),
                        html.Hr(),
                        dbc.Form([
                            dbc.Row([
                                dbc.Label("사용자 ID", html_for="login-username", width=3),
                                dbc.Col(
                                    dbc.Input(id="login-username", placeholder="사용자 ID를 입력하세요"),
                                    width=9
                                )
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Label("비밀번호", html_for="login-password", width=3),
                                dbc.Col(
                                    dbc.Input(
                                        id="login-password",
                                        type="password",
                                        placeholder="비밀번호를 입력하세요"
                                    ),
                                    width=9
                                )
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "로그인",
                                        id="login-btn",
                                        color="primary",
                                        className="w-100"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Button(
                                        "게스트 접속",
                                        id="guest-btn",
                                        color="secondary",
                                        className="w-100"
                                    )
                                ], width=6)
                            ]),
                            html.Div(id="login-message", className="mt-3")
                        ])
                    ])
                ], className="shadow")
            ], width=6)
        ], justify="center", className="mt-5")
    ], className="vh-100")

# 메인 대시보드
def create_dashboard():
    """메인 대시보드 생성"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(f"Smart MES-ERP 대시보드 V{config['system']['version']}", className="mb-4"),
                html.Hr()
            ])
        ]),
        
        # 시스템 상태 카드
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([html.I(className="fas fa-server me-2"), "시스템 상태"]),
                        html.Hr(),
                        html.P([
                            html.I(className="fas fa-check-circle text-success me-2"),
                            "시스템 정상 작동 중"
                        ]),
                        html.P(f"업데이트 주기: {config['system']['update_interval']/1000}초"),
                        html.P(f"활성 모듈: {sum(config['modules'].values())}개"),
                        html.P([
                            html.I(className="fas fa-plug text-info me-2"),
                            f"API 서버: {'활성' if config.get('api', {}).get('enabled', False) else '비활성'}"
                        ], className="mb-0")
                    ])
                ])
            ], lg=4, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([html.I(className="fas fa-chart-line me-2"), "오늘의 생산"]),
                        html.Hr(),
                        html.H2("0", id="today-production", className="text-center text-primary"),
                        html.P("총 생산량", className="text-center")
                    ])
                ])
            ], lg=4, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([html.I(className="fas fa-boxes me-2"), "재고 현황"]),
                        html.Hr(),
                        html.H2("0", id="low-stock-items", className="text-center text-warning"),
                        html.P("부족 품목", className="text-center")
                    ])
                ])
            ], lg=4, className="mb-4")
        ]),
        
        # 모듈 상태
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([html.I(className="fas fa-puzzle-piece me-2"), "모듈 상태"]),
                        html.Hr(),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Badge(
                                        ["MES ", html.I(className="fas fa-check")],
                                        color="success" if config['modules']['mes'] else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["재고관리 ", html.I(className="fas fa-check")],
                                        color="success" if config['modules']['inventory'] else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["구매관리 ", html.I(className="fas fa-check")],
                                        color="success" if config['modules']['purchase'] else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["영업관리 ", html.I(className="fas fa-check")],
                                        color="success" if config['modules']['sales'] else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["품질관리 ", html.I(className="fas fa-check")],
                                        color="success" if config['modules'].get('quality', False) else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["인사관리 ", html.I(className="fas fa-check")],  # V1.2 추가
                                        color="success" if config['modules'].get('hr', False) else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["회계관리 ", html.I(className="fas fa-check")],
                                        color="success" if config['modules'].get('accounting', False) else "secondary",
                                        className="me-2 p-2"
                                    )
                                ])
                            ], className="mb-3"),
                            html.P(f"✅ 활성 모듈은 메뉴에서 접근 가능합니다. (V{config['system']['version']})", className="text-muted small")
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # 최근 활동
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([html.I(className="fas fa-history me-2"), "최근 활동"])
                    ]),
                    dbc.CardBody([
                        html.Div(id="recent-activities")
                    ])
                ])
            ], lg=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([html.I(className="fas fa-exclamation-triangle me-2"), "알림"])
                    ]),
                    dbc.CardBody([
                        html.Div(id="system-alerts")
                    ])
                ])
            ], lg=6)
        ], className="mb-4"),
        
        # API 정보 카드 (V1.2)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([html.I(className="fas fa-code me-2"), "API 정보"]),
                        html.Hr(),
                        html.P([
                            "REST API 엔드포인트: ",
                            html.Code(f"http://localhost:{config.get('api', {}).get('port', 5001)}")
                        ]),
                        html.P([
                            "API 문서: ",
                            html.A(
                                f"http://localhost:{config.get('api', {}).get('port', 5001)}/apidocs",
                                href=f"http://localhost:{config.get('api', {}).get('port', 5001)}/apidocs",
                                target="_blank"
                            )
                        ]),
                        html.P("인증 방식: JWT Bearer Token", className="mb-0")
                    ])
                ])
            ], lg=12) if config.get('api', {}).get('enabled', False) else html.Div()
        ], className="mb-4"),
        
        # 디버깅 콘솔 (숨김 상태)
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([html.I(className="fas fa-bug me-2"), "디버깅 콘솔"], className="mb-0"),
                    dbc.Button("×", id="close-debug", className="btn-close float-end")
                ]),
                dbc.CardBody([
                    html.Div(id="debug-output", style={"height": "200px", "overflowY": "auto"}),
                    dbc.Input(id="debug-input", placeholder="명령어 입력...", className="mt-2")
                ])
            ], className="position-fixed bottom-0 end-0 m-3", style={"width": "500px", "zIndex": 1050})
        ], id="debug-console", style={"display": "none"})
    ], fluid=True, className="py-4")

# 레이아웃
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    create_navbar(),
    html.Div(id='page-content'),
    dcc.Interval(id='interval-component', interval=config['system']['update_interval'])
])

# 페이지 라우팅 콜백
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    """페이지 라우팅 처리"""
    # 인증이 필요한 경우
    if config['authentication']['enabled']:
        if not session_data or not session_data.get('authenticated'):
            return create_login_page()
    
    if pathname == '/' or pathname == '/dashboard':
        return create_dashboard()
    elif pathname == '/mes':
        try:
            from modules.mes.layouts import create_mes_layout
            return create_mes_layout()
        except ImportError:
            return create_mes_layout_inline()
    elif pathname == '/inventory':
        try:
            from modules.inventory.layouts import create_inventory_layout
            return create_inventory_layout()
        except ImportError as e:
            logger.error(f"재고관리 모듈 로드 실패: {e}")
            return error_layout("재고관리", e)
    elif pathname == '/purchase':
        try:
            from modules.purchase.layouts import create_purchase_layout
            return create_purchase_layout()
        except ImportError as e:
            logger.error(f"구매관리 모듈 로드 실패: {e}")
            return error_layout("구매관리", e)
    elif pathname == '/sales':
        try:
            from modules.sales.layouts import create_sales_layout
            return create_sales_layout()
        except ImportError as e:
            logger.error(f"영업관리 모듈 로드 실패: {e}")
            return error_layout("영업관리", e)
    elif pathname == '/quality':
        try:
            from modules.quality.layouts import create_quality_layout
            return create_quality_layout()
        except ImportError as e:
            logger.error(f"품질관리 모듈 로드 실패: {e}")
            return error_layout("품질관리", e)
    elif pathname == '/hr':  # V1.2 인사관리 라우팅 추가
        try:
            from modules.hr.layouts import create_hr_layout
            return create_hr_layout()
        except ImportError as e:
            logger.error(f"인사관리 모듈 로드 실패: {e}")
            return error_layout("인사관리", e)
    elif pathname == '/accounting':
        try:
            from modules.accounting.layouts import create_accounting_layout
            return create_accounting_layout()
        except ImportError as e:
            logger.error(f"회계관리 모듈 로드 실패: {e}")
            return error_layout("회계관리", e)
    elif pathname == '/settings':
        return create_settings_page()
    else:
        return create_dashboard()

def error_layout(module_name, error):
    """모듈 로드 오류 레이아웃"""
    return dbc.Container([
        dbc.Alert(
            [
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"{module_name} 모듈을 불러올 수 없습니다.",
                html.Br(),
                html.Small(f"오류: {str(error)}")
            ],
            color="danger"
        )
    ], className="mt-4")

# MES 레이아웃 인라인 정의 (별도 파일이 없을 때를 위해)
def create_mes_layout_inline():
    """MES 모듈 메인 레이아웃 (인라인)"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-industry me-2"), "MES - 생산관리시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="작업 입력", tab_id="work-input"),
            dbc.Tab(label="현황 조회", tab_id="status-view"),
            dbc.Tab(label="분석", tab_id="analysis"),
            dbc.Tab(label="설정", tab_id="mes-settings")
        ], id="mes-tabs", active_tab="work-input"),
        
        html.Div(id="mes-tab-content", className="mt-4")
    ], fluid=True, className="py-4")

# 설정 페이지
def create_settings_page():
    """시스템 설정 페이지"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-cog me-2"), "시스템 설정"]),
                html.Hr()
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([html.I(className="fas fa-puzzle-piece me-2"), "모듈 관리"])
                    ]),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("MES (생산관리)", className="mb-0"),
                                        html.Small("작업 입력, 현황 조회, 생산 분석", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-mes-switch",
                                            value=config['modules']['mes'],
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("재고관리", className="mb-0"),
                                        html.Small("입출고, 재고 현황, 재고 조정", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-inventory-switch",
                                            value=config['modules']['inventory'],
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("구매관리", className="mb-0"),
                                        html.Small("발주, 입고, 거래처 관리", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-purchase-switch",
                                            value=config['modules']['purchase'],
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("영업관리", className="mb-0"),
                                        html.Small("견적, 수주, 고객 관리, CRM", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-sales-switch",
                                            value=config['modules'].get('sales', False),
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("품질관리", className="mb-0"),
                                        html.Small("검사, 불량 관리, SPC, 성적서", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-quality-switch",
                                            value=config['modules'].get('quality', False),
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ]),
                            dbc.ListGroupItem([  # V1.2 인사관리 추가
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("인사관리", className="mb-0"),
                                        html.Small("직원, 근태, 급여, 휴가 관리", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-hr-switch",
                                            value=config['modules'].get('hr', False),
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ]),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("회계관리", className="mb-0"),
                                        html.Small("전표, 재무제표, 예산 관리", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-accounting-switch",
                                            value=config['modules'].get('accounting', False),
                                            className="float-end"
                                        )
                                    ], width=4)
                                ])
                            ])
                        ])
                    ])
                ])
            ], lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([html.I(className="fas fa-shield-alt me-2"), "인증 설정"])
                    ]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("로그인 사용"),
                                    dbc.Switch(
                                        id="auth-enabled-switch",
                                        value=config['authentication']['enabled'],
                                        className="mb-3"
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("세션 타임아웃 (분)"),
                                    dbc.Input(
                                        id="session-timeout",
                                        type="number",
                                        value=config['authentication']['session_timeout'],
                                        min=5,
                                        max=120
                                    )
                                ])
                            ])
                        ])
                    ])
                ]),
                dbc.Card([  # V1.2 API 설정 추가
                    dbc.CardHeader([
                        html.H4([html.I(className="fas fa-plug me-2"), "API 설정"])
                    ]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("REST API 활성화"),
                                    dbc.Switch(
                                        id="api-enabled-switch",
                                        value=config.get('api', {}).get('enabled', False),
                                        className="mb-3"
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("API 포트"),
                                    dbc.Input(
                                        id="api-port",
                                        type="number",
                                        value=config.get('api', {}).get('port', 5001),
                                        min=1024,
                                        max=65535
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Rate Limit"),
                                    dbc.Input(
                                        id="api-rate-limit",
                                        type="text",
                                        value=config.get('api', {}).get('rate_limit', '100 per hour')
                                    )
                                ], md=6)
                            ])
                        ])
                    ])
                ], className="mt-3")
            ], lg=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([html.I(className="fas fa-clock me-2"), "시스템 설정"])
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("실시간 업데이트 주기 (초)"),
                                dbc.Input(
                                    id="update-interval",
                                    type="number",
                                    value=config['system']['update_interval']/1000,
                                    min=1,
                                    max=60
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("언어"),
                                dbc.Select(
                                    id="language-select",
                                    options=[
                                        {"label": "한국어", "value": "ko"},
                                        {"label": "English", "value": "en", "disabled": True}
                                    ],
                                    value=config['system']['language']
                                )
                            ], md=6)
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-save me-2"), "설정 저장"],
                    id="save-settings-btn",
                    color="primary",
                    size="lg"
                )
            ])
        ]),
        
        html.Div(id="settings-message", className="mt-3")
    ], fluid=True, className="py-4")

# 로그인 처리 콜백
@app.callback(
    [Output('session-store', 'data'),
     Output('login-message', 'children'),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('login-btn', 'n_clicks'),
     Input('guest-btn', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login(login_clicks, guest_clicks, username, password):
    """로그인 처리"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'guest-btn':
        session_data = {
            'authenticated': True,
            'username': 'Guest',
            'role': 'guest'
        }
        return session_data, None, '/'
    
    elif button_id == 'login-btn':
        if not username or not password:
            return dash.no_update, dbc.Alert("사용자 ID와 비밀번호를 입력하세요.", color="warning"), dash.no_update
        
        # 데이터베이스에서 사용자 확인 (V1.2: 비밀번호 해시 비교)
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session_data = {
                'authenticated': True,
                'username': username,
                'user_id': user[0],
                'role': user[1]
            }
            return session_data, None, '/'
        else:
            return dash.no_update, dbc.Alert("잘못된 사용자 ID 또는 비밀번호입니다.", color="danger"), dash.no_update
    
    return dash.no_update, dash.no_update, dash.no_update

# 실시간 업데이트 콜백
@app.callback(
    [Output('today-production', 'children'),
     Output('low-stock-items', 'children'),
     Output('recent-activities', 'children'),
     Output('system-alerts', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    """대시보드 실시간 업데이트"""
    conn = sqlite3.connect('data/database.db')
    
    # 오늘의 생산량
    today = datetime.now().strftime('%Y-%m-%d')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(prod_qty) FROM work_logs WHERE work_date = ?", (today,))
    today_production = cursor.fetchone()[0] or 0
    
    # 재고 부족 품목
    cursor.execute("SELECT COUNT(*) FROM item_master WHERE current_stock < safety_stock")
    low_stock = cursor.fetchone()[0] or 0
    
    # 최근 활동
    activities_query = """
        SELECT 'MES' as module, '작업 입력' as action, created_at 
        FROM work_logs 
        ORDER BY created_at DESC 
        LIMIT 5
    """
    activities_df = pd.read_sql_query(activities_query, conn)
    
    activities_list = []
    for _, row in activities_df.iterrows():
        activities_list.append(
            html.Div([
                html.I(className="fas fa-circle text-primary me-2", style={"fontSize": "8px"}),
                html.Span(f"{row['module']} - {row['action']}", className="me-2"),
                html.Small(row['created_at'], className="text-muted")
            ], className="mb-2")
        )
    
    if not activities_list:
        activities_list = [html.P("최근 활동이 없습니다.", className="text-muted")]
    
    # 시스템 알림
    alerts = []
    
    # 재고 부족 알림
    if low_stock > 0:
        alerts.append(
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"{low_stock}개 품목의 재고가 부족합니다."
            ], color="warning", className="mb-2")
        )
    
    # V1.0 영업관리 알림
    try:
        # 견적서 만료 임박 알림
        cursor.execute("""
            SELECT COUNT(*) FROM quotations 
            WHERE validity_date <= date('now', '+3 days') 
            AND status IN ('sent', 'reviewing')
        """)
        expiring_quotes = cursor.fetchone()[0]
        
        if expiring_quotes > 0:
            alerts.append(
                dbc.Alert([
                    html.I(className="fas fa-clock me-2"),
                    f"{expiring_quotes}개 견적서가 곧 만료됩니다."
                ], color="info", className="mb-2")
            )
    except:
        pass  # 테이블이 없을 경우 무시
    
    # V1.1 품질관리 알림
    try:
        # 교정 예정 장비 알림
        cursor.execute("""
            SELECT COUNT(*) FROM measurement_equipment 
            WHERE next_calibration_date <= date('now', '+30 days')
            AND status = 'active'
        """)
        calibration_due = cursor.fetchone()[0]
        
        if calibration_due > 0:
            alerts.append(
                dbc.Alert([
                    html.I(className="fas fa-tools me-2"),
                    f"{calibration_due}개 측정 장비의 교정이 예정되어 있습니다."
                ], color="info", className="mb-2")
            )
        
        # 중대 불량 알림
        cursor.execute("""
            SELECT COUNT(*) 
            FROM defect_history dh
            JOIN defect_types dt ON dh.defect_code = dt.defect_code
            WHERE dt.severity_level = 1
            AND dh.status != 'closed'
        """)
        critical_defects = cursor.fetchone()[0]
        
        if critical_defects > 0:
            alerts.append(
                dbc.Alert([
                    html.I(className="fas fa-exclamation-circle me-2"),
                    f"{critical_defects}건의 중대 불량이 처리 중입니다."
                ], color="danger", className="mb-2")
            )
    except:
        pass  # 테이블이 없을 경우 무시
    
    # V1.2 인사관리 알림
    try:
        # 미승인 휴가 신청
        cursor.execute("""
            SELECT COUNT(*) FROM leave_requests 
            WHERE status = 'pending'
        """)
        pending_leaves = cursor.fetchone()[0]
        
        if pending_leaves > 0:
            alerts.append(
                dbc.Alert([
                    html.I(className="fas fa-calendar-alt me-2"),
                    f"{pending_leaves}건의 휴가 신청이 승인 대기 중입니다."
                ], color="info", className="mb-2")
            )
        
        # 오늘 출근하지 않은 직원
        cursor.execute("""
            SELECT COUNT(*) FROM employees e
            WHERE e.work_status = 'active'
            AND e.emp_id NOT IN (
                SELECT emp_id FROM attendance WHERE work_date = ?
            )
        """, (today,))
        absent_employees = cursor.fetchone()[0]
        
        if absent_employees > 0 and datetime.now().hour > 10:  # 오전 10시 이후
            alerts.append(
                dbc.Alert([
                    html.I(className="fas fa-user-clock me-2"),
                    f"{absent_employees}명의 직원이 아직 출근하지 않았습니다."
                ], color="warning", className="mb-2")
            )
    except:
        pass  # 테이블이 없을 경우 무시
    
    # 목표 달성 알림
    cursor.execute("""
        SELECT COUNT(*) FROM work_logs 
        WHERE work_date = ? AND prod_qty >= plan_qty
    """, (today,))
    achieved = cursor.fetchone()[0]
    
    if achieved > 0:
        alerts.append(
            dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"오늘 {achieved}건의 작업이 목표를 달성했습니다!"
            ], color="success", className="mb-2")
        )
    
    if not alerts:
        alerts = [html.P("새로운 알림이 없습니다.", className="text-muted")]
    
    conn.close()
    
    return (
        f"{today_production:,}",
        f"{low_stock:,}",
        activities_list,
        alerts
    )

# 디버깅 콘솔 토글
@app.callback(
    Output('debug-console', 'style'),
    Input('close-debug', 'n_clicks'),
    State('debug-console', 'style'),
    prevent_initial_call=True
)
def toggle_debug_console(n_clicks, current_style):
    """디버깅 콘솔 토글"""
    if current_style.get('display') == 'none':
        return {'display': 'block'}
    return {'display': 'none'}

# 설정 저장
@app.callback(
    Output('settings-message', 'children'),
    Input('save-settings-btn', 'n_clicks'),
    [State('module-mes-switch', 'value'),
     State('module-inventory-switch', 'value'),
     State('module-purchase-switch', 'value'),
     State('module-sales-switch', 'value'),
     State('module-quality-switch', 'value'),
     State('module-hr-switch', 'value'),  # V1.2 추가
     State('module-accounting-switch', 'value'),
     State('auth-enabled-switch', 'value'),
     State('session-timeout', 'value'),
     State('api-enabled-switch', 'value'),  # V1.2 추가
     State('api-port', 'value'),  # V1.2 추가
     State('api-rate-limit', 'value'),  # V1.2 추가
     State('update-interval', 'value'),
     State('language-select', 'value')],
    prevent_initial_call=True
)
def save_settings(n_clicks, mes_enabled, inventory_enabled, purchase_enabled,
                 sales_enabled, quality_enabled, hr_enabled, accounting_enabled, 
                 auth_enabled, session_timeout, api_enabled, api_port, api_rate_limit,
                 update_interval, language):
    """시스템 설정 저장"""
    global config
    
    config['modules']['mes'] = mes_enabled
    config['modules']['inventory'] = inventory_enabled
    config['modules']['purchase'] = purchase_enabled
    config['modules']['sales'] = sales_enabled
    config['modules']['quality'] = quality_enabled
    config['modules']['hr'] = hr_enabled  # V1.2 추가
    config['modules']['accounting'] = accounting_enabled
    config['authentication']['enabled'] = auth_enabled
    config['authentication']['session_timeout'] = session_timeout
    config['api']['enabled'] = api_enabled  # V1.2 추가
    config['api']['port'] = api_port  # V1.2 추가
    config['api']['rate_limit'] = api_rate_limit  # V1.2 추가
    config['system']['update_interval'] = update_interval * 1000
    config['system']['language'] = language
    
    save_config(config)
    
    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            "설정이 저장되었습니다. 일부 변경사항은 재시작 후 적용됩니다."
        ],
        color="success",
        dismissable=True
    )

# MES 모듈 콜백 등록 (모듈이 있을 경우)
try:
    from modules.mes.callbacks import register_mes_callbacks
    register_mes_callbacks(app)
except ImportError:
    logger.warning("MES 모듈 콜백을 불러올 수 없습니다.")

# 재고관리 모듈 콜백 등록 (모듈이 있을 경우)
try:
    from modules.inventory.callbacks import register_inventory_callbacks
    register_inventory_callbacks(app)
except ImportError:
    logger.warning("재고관리 모듈 콜백을 불러올 수 없습니다.")

# 구매관리 모듈 콜백 등록 (모듈이 있을 경우)
try:
    from modules.purchase.callbacks import register_purchase_callbacks
    register_purchase_callbacks(app)
except ImportError:
    logger.warning("구매관리 모듈 콜백을 불러올 수 없습니다.")

# 영업관리 모듈 콜백 등록 (V1.0 추가)
try:
    from modules.sales.callbacks import register_sales_callbacks
    register_sales_callbacks(app)
except ImportError:
    logger.warning("영업관리 모듈 콜백을 불러올 수 없습니다.")

# 품질관리 모듈 콜백 등록 (V1.1 추가)
try:
    from modules.quality.callbacks import register_quality_callbacks
    register_quality_callbacks(app)
except ImportError:
    logger.warning("품질관리 모듈 콜백을 불러올 수 없습니다.")

# 인사관리 모듈 콜백 등록 (V1.2 추가)
try:
    from modules.hr.callbacks import register_hr_callbacks
    register_hr_callbacks(app)
except ImportError:
    logger.warning("인사관리 모듈 콜백을 불러올 수 없습니다.")

# 회계관리 모듈 콜백 등록
try:
    from modules.accounting.callbacks import register_accounting_callbacks
    register_accounting_callbacks(app)
except ImportError:
    logger.warning("회계관리 모듈 콜백을 불러올 수 없습니다.")

if __name__ == '__main__':
    # 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # 데이터베이스 초기화
    init_database()
    
    # V1.2: API 서버 실행 (별도 스레드)
    if config.get('api', {}).get('enabled', False):
        def run_api():
            try:
                from api import create_api_app
                api_app, api = create_api_app(config)
                api_port = config['api'].get('port', 5001)
                logger.info(f"REST API 서버 시작: http://localhost:{api_port}")
                logger.info(f"API 문서: http://localhost:{api_port}/apidocs")
                api_app.run(
                    host=config['api'].get('host', '0.0.0.0'),
                    port=api_port,
                    debug=False,
                    use_reloader=False
                )
            except Exception as e:
                logger.error(f"API 서버 시작 실패: {e}")
        
        api_thread = threading.Thread(target=run_api)
        api_thread.daemon = True
        api_thread.start()
    
    # 앱 실행
    logger.info(f"{config['system']['name']} V{config['system']['version']} 시작")
    logger.info("http://localhost:8050 에서 접속 가능")
    logger.info(f"활성 모듈: {[k for k, v in config['modules'].items() if v]}")
    
    app.run(debug=True, host='0.0.0.0', port=8050, use_reloader=False)
