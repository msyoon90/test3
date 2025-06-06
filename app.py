# app.py - Smart MES-ERP 메인 애플리케이션

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
            'language': 'ko',
            'update_interval': 2000  # 2초
        },
        'modules': {
            'mes': True,
            'inventory': True,
            'purchase': True,
            'sales': False,
            'accounting': True  
        },
        'authentication': {
            'enabled': True,
            'session_timeout': 30
        },
        'database': {
            'path': 'data/database.db'
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
    
    # 사용자 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 작업 로그 테이블
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
    
    # 계정과목 마스터
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
    
    # 기본 관리자 계정 생성
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
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
                        dbc.NavItem(dbc.NavLink("구매관리", href="/purchase", id="nav-purchase", disabled=True)) if config['modules']['purchase'] else None,
                        dbc.NavItem(dbc.NavLink("영업관리", href="/sales", id="nav-sales", disabled=True)) if config['modules']['sales'] else None,
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
                html.H1("Smart MES-ERP 대시보드", className="mb-4"),
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
                        html.P(f"활성 모듈: {sum(config['modules'].values())}개")
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
                                        ["구매관리 ", html.I(className="fas fa-times")],
                                        color="success" if config['modules']['purchase'] else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(
                                        ["영업관리 ", html.I(className="fas fa-times")],
                                        color="success" if config['modules']['sales'] else "secondary",
                                        className="me-2 p-2"
                                    ),
                                    dbc.Badge(  # ← 여기부터 추가
                                        ["회계관리 ", html.I(className="fas fa-check")],
                                        color="success" if config['modules'].get('accounting', False) else "secondary",
                                        className="me-2 p-2"
                                    )  # ← 여기까지 추가
                                ])
                            ], className="mb-3"),
                            html.P("✅ 활성 모듈은 메뉴에서 접근 가능합니다.", className="text-muted small")
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

# 페이지 라우팅 콜백 수정
# 페이지 라우팅 콜백에 구매관리 추가
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
    elif pathname == '/accounting':  # ← 이 부분부터
        try:
            from modules.accounting.layouts import create_accounting_layout
            return create_accounting_layout()
        except ImportError as e:
            logger.error(f"회계관리 모듈 로드 실패: {e}")
            return error_layout("회계관리", e)  # ← 여기까지 추가
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
                                            className="float-end",
                                            disabled=True
                                        )
                                    ], width=4)
                                ])
                            ], color="light"),
                            dbc.ListGroupItem([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("영업관리", className="mb-0"),
                                        html.Small("견적, 수주, 고객 관리", className="text-muted")
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Switch(
                                            id="module-sales-switch",
                                            value=config['modules']['sales'],
                                            className="float-end",
                                            disabled=True
                                        )
                                    ], width=4)
                                ])
                            ], color="light"),
                            dbc.ListGroupItem([  # ← 여기부터 추가
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
                            ])  # ← 여기까지 추가
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
                ])
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
        
        # 데이터베이스에서 사용자 확인
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
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
          State('module-purchase-switch', 'value'),  # ← 이 줄 추가
     State('module-accounting-switch', 'value'),  # ← 이 줄 추가
     State('auth-enabled-switch', 'value'),
     State('session-timeout', 'value'),
     State('update-interval', 'value'),
     State('language-select', 'value')],
    prevent_initial_call=True
)
def save_settings(n_clicks, mes_enabled, inventory_enabled, purchase_enabled,
                 accounting_enabled, auth_enabled, session_timeout, 
                 update_interval, language):
    """시스템 설정 저장"""
    global config
    
    config['modules']['mes'] = mes_enabled
    config['modules']['inventory'] = inventory_enabled
    config['modules']['purchase'] = purchase_enabled  # ← 이 줄 추가
    config['modules']['accounting'] = accounting_enabled  # ← 이 줄 추가
    config['authentication']['enabled'] = auth_enabled
    config['authentication']['session_timeout'] = session_timeout
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

# 구매관리 부분만 주석 처리
try:
    from modules.purchase.callbacks import register_purchase_callbacks
    register_purchase_callbacks(app)
except ImportError:
    logger.warning("구매관리 모듈 콜백을 불러올 수 없습니다.")

# 회계관리 모듈 콜백 등록  # ← 여기부터 추가
try:
    from modules.accounting.callbacks import register_accounting_callbacks
    register_accounting_callbacks(app)
except ImportError:
    logger.warning("회계관리 모듈 콜백을 불러올 수 없습니다.")  # ← 여기까지 추가

if __name__ == '__main__':
    # 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # 데이터베이스 초기화
    init_database()
    
    # 앱 실행
    logger.info(f"{config['system']['name']} 시작")
    logger.info("http://localhost:8050 에서 접속 가능")
    
    app.run(debug=True, host='0.0.0.0', port=8050, use_reloader=False)
    
