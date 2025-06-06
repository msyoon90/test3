# app_mes_only.py - Smart MES 시스템 (다른 모듈 비활성화)

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
            'name': 'Smart MES',
            'version': '1.0.0',
            'language': 'ko',
            'update_interval': 2000  # 2초
        },
        'modules': {
            'mes': True,
            # 'inventory': False,  # 비활성화
            # 'purchase': False,   # 비활성화
            # 'sales': False,      # 비활성화
            # 'accounting': False  # 비활성화
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
    """데이터베이스 초기화 - MES 관련 테이블만"""
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
    
    # 기본 관리자 계정 생성
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
    
    # 샘플 작업자 추가
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'worker'")
    if cursor.fetchone()[0] == 0:
        sample_workers = [
            ('worker1', 'pass123', 'worker'),
            ('worker2', 'pass123', 'worker'),
            ('worker3', 'pass123', 'worker')
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            sample_workers
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
                        # 다른 모듈들은 주석처리
                        # dbc.NavItem(dbc.NavLink("재고관리", href="/inventory", id="nav-inventory")) if config['modules'].get('inventory', False) else None,
                        # dbc.NavItem(dbc.NavLink("구매관리", href="/purchase", id="nav-purchase")) if config['modules'].get('purchase', False) else None,
                        # dbc.NavItem(dbc.NavLink("영업관리", href="/sales", id="nav-sales")) if config['modules'].get('sales', False) else None,
                        # dbc.NavItem(dbc.NavLink("회계관리", href="/accounting", id="nav-accounting")) if config['modules'].get('accounting', False) else None,
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
    """MES 중심 대시보드"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(f"Smart MES 대시보드", className="mb-4"),
                html.Hr()
            ])
        ]),
        
        # MES 상태 카드
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([html.I(className="fas fa-server me-2"), "시스템 상태"]),
                        html.Hr(),
                        html.P([
                            html.I(className="fas fa-check-circle text-success me-2"),
                            "MES 시스템 정상 작동 중"
                        ]),
                        html.P(f"업데이트 주기: {config['system']['update_interval']/1000}초"),
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
                        html.H4([html.I(className="fas fa-percentage me-2"), "달성률"]),
                        html.Hr(),
                        html.H2("0%", id="today-achievement", className="text-center text-success"),
                        html.P("평균 달성률", className="text-center")
                    ])
                ])
            ], lg=4, className="mb-4")
        ]),
        
        # 최근 작업 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([html.I(className="fas fa-history me-2"), "최근 작업 현황"])
                    ]),
                    dbc.CardBody([
                        html.Div(id="recent-works")
                    ])
                ])
            ], lg=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([html.I(className="fas fa-chart-bar me-2"), "공정별 실적"])
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="process-performance-mini")
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
    elif pathname == '/settings':
        return create_settings_page()
    else:
        return create_dashboard()

# MES 레이아웃 인라인 정의
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

# 설정 페이지 (MES만 표시)
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
                            # 다른 모듈들은 주석처리
                            # dbc.ListGroupItem([...]),
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
     Output('today-achievement', 'children'),
     Output('recent-works', 'children'),
     Output('process-performance-mini', 'figure')],
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
    
    # 평균 달성률
    cursor.execute("""
        SELECT AVG(CAST(prod_qty AS FLOAT) / NULLIF(plan_qty, 0) * 100) 
        FROM work_logs 
        WHERE work_date = ?
    """, (today,))
    avg_achievement = cursor.fetchone()[0] or 0
    
    # 최근 작업 현황
    recent_query = """
        SELECT w.lot_number, w.process, w.plan_qty, w.prod_qty, 
               u.username, w.created_at
        FROM work_logs w
        LEFT JOIN users u ON w.worker_id = u.id
        ORDER BY w.created_at DESC
        LIMIT 5
    """
    recent_df = pd.read_sql_query(recent_query, conn)
    
    recent_works = []
    for _, row in recent_df.iterrows():
        achievement = (row['prod_qty'] / row['plan_qty'] * 100) if row['plan_qty'] > 0 else 0
        color = "success" if achievement >= 100 else "warning" if achievement >= 80 else "danger"
        
        recent_works.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Small(f"LOT: {row['lot_number']}", className="text-muted"),
                            html.H6(f"{row['process']} 공정"),
                        ], width=6),
                        dbc.Col([
                            html.Small(f"실적: {row['prod_qty']}/{row['plan_qty']}"),
                            dbc.Progress(value=achievement, color=color, className="mb-1", style={"height": "10px"}),
                        ], width=6)
                    ])
                ])
            ], className="mb-2")
        )
    
    if not recent_works:
        recent_works = [html.P("최근 작업이 없습니다.", className="text-muted text-center")]
    
    # 공정별 실적 차트
    process_query = """
        SELECT process, SUM(plan_qty) as plan, SUM(prod_qty) as prod
        FROM work_logs
        WHERE work_date >= date('now', '-7 days')
        GROUP BY process
    """
    process_df = pd.read_sql_query(process_query, conn)
    
    fig = go.Figure()
    if not process_df.empty:
        fig.add_trace(go.Bar(name='계획', x=process_df['process'], y=process_df['plan'], marker_color='lightblue'))
        fig.add_trace(go.Bar(name='실적', x=process_df['process'], y=process_df['prod'], marker_color='#0066cc'))
        fig.update_layout(
            showlegend=True,
            height=250,
            margin=dict(l=0, r=0, t=0, b=0),
            barmode='group'
        )
    else:
        fig.add_annotation(
            text="데이터가 없습니다",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
    
    conn.close()
    
    return (
        f"{today_production:,}",
        f"{avg_achievement:.1f}%",
        recent_works,
        fig
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
     State('auth-enabled-switch', 'value'),
     State('session-timeout', 'value'),
     State('update-interval', 'value'),
     State('language-select', 'value')],
    prevent_initial_call=True
)
def save_settings(n_clicks, mes_enabled, auth_enabled, session_timeout, 
                 update_interval, language):
    """시스템 설정 저장"""
    global config
    
    config['modules']['mes'] = mes_enabled
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

# MES 모듈 콜백 등록
try:
    from modules.mes.callbacks import register_mes_callbacks
    register_mes_callbacks(app)
except ImportError:
    logger.warning("MES 모듈 콜백을 불러올 수 없습니다.")

if __name__ == '__main__':
    # 디렉토리 생성
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # 데이터베이스 초기화
    init_database()
    
    # 앱 실행
    logger.info(f"{config['system']['name']} V{config['system']['version']} 시작")
    logger.info("http://localhost:8050 에서 접속 가능")
    logger.info("MES 모듈만 활성화됨")
    
    app.run(debug=True, host='0.0.0.0', port=8050, use_reloader=False)
