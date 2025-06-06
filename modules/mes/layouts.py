# modules/mes/layouts.py - MES 모듈 레이아웃

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import json

def create_mes_layout():
    """MES 모듈 메인 레이아웃"""
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

def create_work_input_form():
    """작업 입력 폼"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-edit me-2"), "작업 실적 입력"]),
        ]),
        dbc.CardBody([
            dbc.Form([
                # 기본 정보
                dbc.Row([
                    dbc.Col([
                        dbc.Label("작업일자", html_for="work-date"),
                        dbc.Input(
                            id="work-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("LOT 번호", html_for="lot-number"),
                        dbc.Input(
                            id="lot-number",
                            placeholder="LOT-2024-001",
                            value=f"LOT-{datetime.now().strftime('%Y%m%d')}-"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                # 공정 정보
                dbc.Row([
                    dbc.Col([
                        dbc.Label("공정", html_for="process-select"),
                        dbc.Select(
                            id="process-select",
                            options=[
                                {"label": "절단", "value": "cutting"},
                                {"label": "가공", "value": "processing"},
                                {"label": "조립", "value": "assembly"},
                                {"label": "검사", "value": "inspection"},
                                {"label": "포장", "value": "packing"}
                            ]
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("작업자", html_for="worker-select"),
                        dbc.Select(
                            id="worker-select",
                            options=[
                                {"label": "홍길동", "value": "1"},
                                {"label": "김철수", "value": "2"},
                                {"label": "이영희", "value": "3"}
                            ]
                        )
                    ], md=6)
                ], className="mb-3"),
                
                # 수량 정보
                dbc.Row([
                    dbc.Col([
                        dbc.Label("계획 수량", html_for="plan-qty"),
                        dbc.Input(
                            id="plan-qty",
                            type="number",
                            placeholder="0",
                            min=0
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("생산 수량", html_for="prod-qty"),
                        dbc.Input(
                            id="prod-qty",
                            type="number",
                            placeholder="0",
                            min=0
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("불량 수량", html_for="defect-qty"),
                        dbc.Input(
                            id="defect-qty",
                            type="number",
                            placeholder="0",
                            min=0,
                            className="border-danger"
                        )
                    ], md=4)
                ], className="mb-3"),
                
                # 달성률 표시
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Label("달성률"),
                            dbc.Progress(
                                id="achievement-rate",
                                value=0,
                                striped=True,
                                animated=True,
                                className="mb-2"
                            ),
                            html.Div(id="achievement-text", className="text-center")
                        ])
                    ])
                ], className="mb-3"),
                
                # 버튼
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-save me-2"), "저장"],
                            id="save-work-btn",
                            color="primary",
                            size="lg",
                            className="w-100"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-undo me-2"), "초기화"],
                            id="reset-work-btn",
                            color="secondary",
                            size="lg",
                            className="w-100"
                        )
                    ], md=6)
                ])
            ]),
            
            # 메시지 영역
            html.Div(id="work-input-message", className="mt-3")
        ])
    ])

def create_status_view():
    """현황 조회 화면"""
    return html.Div([
        # 조회 조건
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("조회 기간"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="search-start-date",
                                type="date",
                                value=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="search-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Label("공정"),
                        dbc.Select(
                            id="search-process",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "절단", "value": "cutting"},
                                {"label": "가공", "value": "processing"},
                                {"label": "조립", "value": "assembly"},
                                {"label": "검사", "value": "inspection"},
                                {"label": "포장", "value": "packing"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),  # 빈 레이블로 정렬
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=3)
                ])
            ])
        ], className="mb-4"),
        
        # 요약 카드
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("총 생산량", className="text-muted"),
                        html.H3("0", id="total-production"),
                        html.P("개", className="text-muted mb-0")
                    ])
                ], color="primary", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("평균 달성률", className="text-muted"),
                        html.H3("0%", id="avg-achievement"),
                        html.P("계획 대비", className="text-muted mb-0")
                    ])
                ], color="success", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("불량률", className="text-muted"),
                        html.H3("0%", id="defect-rate"),
                        html.P("품질 지표", className="text-muted mb-0")
                    ])
                ], color="danger", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("작업 건수", className="text-muted"),
                        html.H3("0", id="work-count"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ], color="info", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 차트 영역
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("일별 생산 추이"),
                    dbc.CardBody([
                        dcc.Graph(id="daily-production-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("공정별 실적"),
                    dbc.CardBody([
                        dcc.Graph(id="process-performance-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 상세 데이터 테이블
        dbc.Card([
            dbc.CardHeader([
                html.H5("상세 작업 기록"),
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "Excel 다운로드"],
                    id="download-excel-btn",
                    color="success",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                html.Div(id="work-logs-table")
            ])
        ])
    ])

def create_analysis_view():
    """분석 화면"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("생산성 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="productivity-analysis-chart")
                    ])
                ])
            ], md=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("시간대별 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="hourly-analysis-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("작업자별 실적"),
                    dbc.CardBody([
                        dcc.Graph(id="worker-performance-chart")
                    ])
                ])
            ], md=6)
        ])
    ])

def create_mes_settings():
    """MES 설정 화면"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-cog me-2"), "MES 설정"])
        ]),
        dbc.CardBody([
            dbc.Accordion([
                dbc.AccordionItem([
                    # 입력 폼 설정
                    html.H5("필드 관리", className="mb-3"),
                    dbc.ListGroup([
                        dbc.ListGroupItem([
                            dbc.Row([
                                dbc.Col("LOT 번호", width=3),
                                dbc.Col([
                                    dbc.Switch(
                                        id={"type": "field-switch", "field": "lot"},
                                        value=True,
                                        label="사용"
                                    )
                                ], width=2),
                                dbc.Col([
                                    dbc.Switch(
                                        id={"type": "field-required", "field": "lot"},
                                        value=True,
                                        label="필수"
                                    )
                                ], width=2),
                                dbc.Col([
                                    dbc.Input(
                                        id={"type": "field-default", "field": "lot"},
                                        placeholder="기본값",
                                        size="sm"
                                    )
                                ], width=5)
                            ])
                        ]),
                        dbc.ListGroupItem([
                            dbc.Row([
                                dbc.Col("작업일자", width=3),
                                dbc.Col([
                                    dbc.Switch(
                                        id={"type": "field-switch", "field": "date"},
                                        value=True,
                                        label="사용"
                                    )
                                ], width=2),
                                dbc.Col([
                                    dbc.Switch(
                                        id={"type": "field-required", "field": "date"},
                                        value=True,
                                        label="필수"
                                    )
                                ], width=2)
                            ])
                        ])
                    ])
                ], title="입력 폼 커스터마이징"),
                
                dbc.AccordionItem([
                    # 검증 규칙
                    html.H5("데이터 검증 규칙", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("최소 생산 수량"),
                                dbc.Input(type="number", value="1", min="0")
                            ], md=6),
                            dbc.Col([
                                dbc.Label("최대 불량률 (%)"),
                                dbc.Input(type="number", value="10", min="0", max="100")
                            ], md=6)
                        ])
                    ])
                ], title="검증 규칙"),
                
                dbc.AccordionItem([
                    # 알림 설정
                    html.H5("알림 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Checklist(
                                    options=[
                                        {"label": "목표 달성 시 알림", "value": "achievement"},
                                        {"label": "불량률 초과 시 알림", "value": "defect"},
                                        {"label": "일일 마감 알림", "value": "daily"}
                                    ],
                                    value=["achievement", "defect"],
                                    id="notification-settings"
                                )
                            ])
                        ])
                    ])
                ], title="알림")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "설정 저장"],
                        id="save-mes-settings-btn",
                        color="primary",
                        className="mt-3"
                    )
                ])
            ])
        ])
    ])

# 헬퍼 함수들
def calculate_achievement_rate(plan_qty, prod_qty):
    """달성률 계산"""
    if plan_qty and plan_qty > 0:
        return min(round((prod_qty / plan_qty) * 100, 1), 100)
    return 0

def get_work_logs(start_date, end_date, process=None):
    """작업 로그 조회"""
    conn = sqlite3.connect('data/database.db')
    query = """
        SELECT w.*, u.username 
        FROM work_logs w
        LEFT JOIN users u ON w.worker_id = u.id
        WHERE work_date BETWEEN ? AND ?
    """
    params = [start_date, end_date]
    
    if process and process != 'all':
        query += " AND process = ?"
        params.append(process)
    
    query += " ORDER BY work_date DESC, created_at DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def create_work_logs_table(df):
    """작업 로그 테이블 생성"""
    if df.empty:
        return html.Div("조회된 데이터가 없습니다.", className="text-center text-muted p-4")
    
    # 달성률 계산
    df['achievement_rate'] = df.apply(
        lambda row: calculate_achievement_rate(row['plan_qty'], row['prod_qty']), 
        axis=1
    )
    
    # 불량률 계산
    df['defect_rate'] = df.apply(
        lambda row: round((row['defect_qty'] / row['prod_qty'] * 100), 1) if row['prod_qty'] > 0 else 0,
        axis=1
    )
    
    # 테이블 생성
    return dbc.Table.from_dataframe(
        df[['work_date', 'lot_number', 'process', 'username', 'plan_qty', 
            'prod_qty', 'defect_qty', 'achievement_rate', 'defect_rate']],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0"
    )
