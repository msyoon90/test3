# File: /modules/accounting/layouts.py

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_accounting_layout():
    """회계관리 모듈 메인 레이아웃"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-calculator me-2"), "회계관리 시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="전표 관리", tab_id="voucher-management"),
            dbc.Tab(label="매출/매입", tab_id="sales-purchase"),
            dbc.Tab(label="재무제표", tab_id="financial-statements"),
            dbc.Tab(label="원가 관리", tab_id="cost-management"),
            dbc.Tab(label="예산 관리", tab_id="budget-management"),
            dbc.Tab(label="고정자산", tab_id="fixed-assets"),
            dbc.Tab(label="회계 분석", tab_id="accounting-analysis"),
            dbc.Tab(label="설정", tab_id="accounting-settings")
        ], id="accounting-tabs", active_tab="voucher-management"),
        
        html.Div(id="accounting-tab-content", className="mt-4"),
        
        # 모달들
        create_voucher_modal(),
        create_tax_invoice_modal(),
        
        # 다운로드 컴포넌트
        dcc.Download(id="download-accounting-data")
    ], fluid=True, className="py-4")

def create_voucher_management():
    """전표 관리 화면"""
    return html.Div([
        # 전표 현황 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-file-invoice-dollar fa-2x text-primary mb-2"),
                        ], className="text-center"),
                        html.H6("오늘 전표", className="text-muted text-center"),
                        html.H3("0", id="today-vouchers", className="text-center"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="primary", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-check-circle fa-2x text-success mb-2"),
                        ], className="text-center"),
                        html.H6("승인 대기", className="text-muted text-center"),
                        html.H3("0", id="pending-vouchers", className="text-center"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="warning", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-balance-scale fa-2x text-info mb-2"),
                        ], className="text-center"),
                        html.H6("차대 불일치", className="text-muted text-center"),
                        html.H3("0", id="unbalanced-vouchers", className="text-center text-danger"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="danger", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-calendar-alt fa-2x text-secondary mb-2"),
                        ], className="text-center"),
                        html.H6("이번달 전표", className="text-muted text-center"),
                        html.H3("0", id="monthly-vouchers", className="text-center"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="secondary", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 전표 입력/조회
        dbc.Card([
            dbc.CardHeader([
                html.H4("전표 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "일반 전표"],
                        id="new-general-voucher-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-file-invoice me-2"), "매출 전표"],
                        id="new-sales-voucher-btn",
                        color="success",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-shopping-cart me-2"), "매입 전표"],
                        id="new-purchase-voucher-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 조회 조건
                dbc.Row([
                    dbc.Col([
                        dbc.Label("전표일자"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="voucher-start-date",
                                type="date",
                                value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="voucher-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("전표유형"),
                        dbc.Select(
                            id="voucher-type-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "입금", "value": "receipt"},
                                {"label": "출금", "value": "payment"},
                                {"label": "대체", "value": "transfer"},
                                {"label": "매출", "value": "sales"},
                                {"label": "매입", "value": "purchase"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("상태"),
                        dbc.Select(
                            id="voucher-status-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "작성중", "value": "draft"},
                                {"label": "승인대기", "value": "pending"},
                                {"label": "승인완료", "value": "approved"},
                                {"label": "취소", "value": "cancelled"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-voucher-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 전표 리스트
                html.Div(id="voucher-list-table")
            ])
        ])
    ])

def create_sales_purchase():
    """매출/매입 관리"""
    return html.Div([
        # 매출/매입 현황 - ID 변경
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("이번달 매출"),
                    dbc.CardBody([
                        html.H3("₩0", id="accounting-monthly-sales", className="text-primary"),
                        html.P("전월 대비: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("이번달 매입"),
                    dbc.CardBody([
                        html.H3("₩0", id="accounting-monthly-purchase", className="text-danger"),
                        html.P("전월 대비: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("매출총이익"),
                    dbc.CardBody([
                        html.H3("₩0", id="accounting-gross-profit", className="text-success"),
                        html.P("이익률: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("부가세"),
                    dbc.CardBody([
                        html.H3("₩0", id="accounting-vat-amount", className="text-info"),
                        html.P("예정신고", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 세금계산서 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("세금계산서 관리"),
                dbc.Button(
                    [html.I(className="fas fa-file-invoice me-2"), "세금계산서 발행"],
                    id="new-tax-invoice-btn",
                    color="primary",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                dbc.Tabs([
                    dbc.Tab(label="매출 세금계산서", tab_id="sales-invoice"),
                    dbc.Tab(label="매입 세금계산서", tab_id="purchase-invoice")
                ], id="invoice-tabs", active_tab="sales-invoice"),
                
                html.Div(id="invoice-content", className="mt-3")
            ])
        ])
    ])

def create_financial_statements():
    """재무제표"""
    return html.Div([
        # 기간 선택
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("회계기간"),
                        dbc.InputGroup([
                            dbc.Select(
                                id="fs-year",
                                options=[
                                    {"label": "2024년", "value": "2024"},
                                    {"label": "2025년", "value": "2025"}
                                ],
                                value="2025"
                            ),
                            dbc.Select(
                                id="fs-month",
                                options=[
                                    {"label": f"{i}월", "value": str(i)}
                                    for i in range(1, 13)
                                ],
                                value=str(datetime.now().month)
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-sync me-2"), "조회"],
                            id="refresh-fs-btn",
                            color="primary"
                        )
                    ], md=2)
                ])
            ])
        ], className="mb-4"),
        
        # 재무제표 탭
        dbc.Tabs([
            dbc.Tab(label="손익계산서", tab_id="income-statement"),
            dbc.Tab(label="재무상태표", tab_id="balance-sheet"),
            dbc.Tab(label="현금흐름표", tab_id="cash-flow"),
            dbc.Tab(label="원가명세서", tab_id="cost-statement")
        ], id="fs-tabs", active_tab="income-statement"),
        
        html.Div(id="fs-content", className="mt-4")
    ])

def create_cost_management():
    """원가 관리"""
    return html.Div([
        # 원가 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("원가 구성"),
                    dbc.CardBody([
                        dcc.Graph(id="cost-composition-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("제품별 원가율"),
                    dbc.CardBody([
                        dcc.Graph(id="product-cost-rate-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 원가 계산
        dbc.Card([
            dbc.CardHeader([
                html.H4("원가 계산"),
                dbc.Button(
                    [html.I(className="fas fa-calculator me-2"), "원가 계산"],
                    id="calc-cost-btn",
                    color="primary",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                html.Div(id="cost-calculation-table")
            ])
        ])
    ])

def create_budget_management():
    """예산 관리"""
    return html.Div([
        # 예산 집행 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("연간 예산", className="text-muted"),
                        html.H3("₩0", id="annual-budget"),
                        dbc.Progress(
                            value=0,
                            id="budget-progress",
                            striped=True,
                            animated=True
                        ),
                        html.P("집행률: 0%", className="text-muted mt-2 mb-0")
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # 부서별 예산
        dbc.Card([
            dbc.CardHeader("부서별 예산 집행 현황"),
            dbc.CardBody([
                dcc.Graph(id="dept-budget-chart")
            ])
        ], className="mb-4"),
        
        # 예산 편성/실적
        dbc.Card([
            dbc.CardHeader([
                html.H4("예산 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "예산 편성"],
                        id="new-budget-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-chart-line me-2"), "예실 분석"],
                        id="budget-analysis-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                html.Div(id="budget-table")
            ])
        ])
    ])

def create_fixed_assets():
    """고정자산 관리"""
    return html.Div([
        # 고정자산 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("총 자산", className="text-muted"),
                        html.H3("₩0", id="total-assets"),
                        html.P("건수: 0건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("당기 상각액", className="text-muted"),
                        html.H3("₩0", id="current-depreciation"),
                        html.P("월 상각액", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("누계 상각액", className="text-muted"),
                        html.H3("₩0", id="accumulated-depreciation"),
                        html.P("상각률: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("장부가액", className="text-muted"),
                        html.H3("₩0", id="book-value"),
                        html.P("잔존가치 포함", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 고정자산 목록
        dbc.Card([
            dbc.CardHeader([
                html.H4("고정자산 목록"),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "자산 등록"],
                    id="new-asset-btn",
                    color="primary",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                html.Div(id="asset-list-table")
            ])
        ])
    ])

def create_accounting_analysis():
    """회계 분석"""
    return html.Div([
        # 분석 기간 설정
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("분석 기간"),
                        dbc.RadioItems(
                            id="analysis-period-acc",
                            options=[
                                {"label": "월간", "value": "month"},
                                {"label": "분기", "value": "quarter"},
                                {"label": "반기", "value": "half"},
                                {"label": "연간", "value": "year"}
                            ],
                            value="month",
                            inline=True
                        )
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # 주요 지표
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("수익성 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="profitability-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("유동성 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="liquidity-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 비율 분석
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("매출 성장률"),
                    dbc.CardBody([
                        dcc.Graph(id="sales-growth-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("비용 구조 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="expense-structure-chart")
                    ])
                ])
            ], md=6)
        ])
    ])

def create_accounting_settings():
    """회계 설정"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-cog me-2"), "회계 설정"])
        ]),
        dbc.CardBody([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5("계정과목 설정", className="mb-3"),
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "계정과목 추가"],
                        id="add-account-btn",
                        color="primary",
                        size="sm",
                        className="mb-3"
                    ),
                    html.Div(id="account-tree")
                ], title="계정과목"),
                
                dbc.AccordionItem([
                    html.H5("결산 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("회계연도 시작월"),
                                dbc.Select(
                                    id="fiscal-year-start",
                                    options=[
                                        {"label": f"{i}월", "value": str(i)}
                                        for i in range(1, 13)
                                    ],
                                    value="1"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("감가상각 방법"),
                                dbc.Select(
                                    id="depreciation-method",
                                    options=[
                                        {"label": "정액법", "value": "straight"},
                                        {"label": "정률법", "value": "declining"},
                                        {"label": "생산량비례법", "value": "production"}
                                    ],
                                    value="straight"
                                )
                            ], md=6)
                        ])
                    ])
                ], title="결산"),
                
                dbc.AccordionItem([
                    html.H5("세무 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("부가세 신고 주기"),
                                dbc.RadioItems(
                                    id="vat-period",
                                    options=[
                                        {"label": "일반 (분기)", "value": "quarter"},
                                        {"label": "간이 (반기)", "value": "half"}
                                    ],
                                    value="quarter"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("전자세금계산서 연동"),
                                dbc.Switch(
                                    id="e-tax-invoice",
                                    value=False,
                                    label="사용"
                                )
                            ], md=6)
                        ])
                    ])
                ], title="세무"),
                
                dbc.AccordionItem([
                    html.H5("권한 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("전표 승인 권한"),
                                dbc.Checklist(
                                    id="voucher-approval-auth",
                                    options=[
                                        {"label": "관리자", "value": "admin"},
                                        {"label": "회계팀장", "value": "acc_manager"},
                                        {"label": "경영진", "value": "executive"}
                                    ],
                                    value=["admin", "acc_manager"]
                                )
                            ])
                        ])
                    ])
                ], title="권한")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "설정 저장"],
                        id="save-acc-settings-btn",
                        color="primary",
                        className="mt-3"
                    )
                ])
            ]),
            
            html.Div(id="acc-settings-message", className="mt-3")
        ])
    ])

def create_voucher_modal():
    """전표 입력 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("전표 입력")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("전표번호"),
                        dbc.Input(
                            id="modal-voucher-no",
                            disabled=True
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("전표일자"),
                        dbc.Input(
                            id="modal-voucher-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("전표유형"),
                        dbc.Select(
                            id="modal-voucher-type",
                            options=[
                                {"label": "입금", "value": "receipt"},
                                {"label": "출금", "value": "payment"},
                                {"label": "대체", "value": "transfer"}
                            ]
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("적요"),
                        dbc.Input(
                            id="modal-voucher-desc"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                html.Hr(),
                
                # 전표 상세 입력 영역
                html.Div([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "행 추가"],
                        id="add-voucher-line-btn",
                        color="secondary",
                        size="sm",
                        className="mb-2"
                    ),
                    html.Div(id="voucher-lines")
                ]),
                
                html.Hr(),
                
                # 차대 합계
                dbc.Row([
                    dbc.Col([
                        html.H6("차변 합계: "),
                        html.H5("₩0", id="total-debit", className="text-primary")
                    ], md=6),
                    dbc.Col([
                        html.H6("대변 합계: "),
                        html.H5("₩0", id="total-credit", className="text-danger")
                    ], md=6, className="text-end")
                ])
            ]),
            
            html.Div(id="voucher-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-voucher-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-voucher-btn",
                color="primary"
            )
        ])
    ], id="voucher-modal", size="xl", is_open=False)

def create_tax_invoice_modal():
    """세금계산서 발행 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("세금계산서 발행")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("구분"),
                        dbc.RadioItems(
                            id="invoice-type",
                            options=[
                                {"label": "매출", "value": "sales"},
                                {"label": "매입", "value": "purchase"}
                            ],
                            value="sales",
                            inline=True
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("거래처"),
                        dbc.Input(
                            id="invoice-company",
                            placeholder="거래처명"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("사업자번호"),
                        dbc.Input(
                            id="invoice-business-no",
                            placeholder="123-45-67890"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("공급가액"),
                        dbc.Input(
                            id="invoice-supply-amount",
                            type="number",
                            value=0
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("부가세"),
                        dbc.Input(
                            id="invoice-tax-amount",
                            type="number",
                            value=0
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("합계"),
                        dbc.Input(
                            id="invoice-total-amount",
                            type="number",
                            value=0,
                            disabled=True
                        )
                    ], md=4)
                ], className="mb-3")
            ]),
            
            html.Div(id="invoice-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-invoice-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-file-invoice me-2"), "발행"],
                id="issue-invoice-btn",
                color="primary"
            )
        ])
    ], id="tax-invoice-modal", size="lg", is_open=False)
