# File: modules/sales/layouts.py
# 영업관리 모듈 레이아웃 - V1.0 신규

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_sales_layout():
    """영업관리 모듈 메인 레이아웃"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-chart-line me-2"), "영업관리 시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="견적 관리", tab_id="quotation"),
            dbc.Tab(label="수주 관리", tab_id="order"),
            dbc.Tab(label="고객 관리", tab_id="customer"),
            dbc.Tab(label="영업 분석", tab_id="sales-analysis"),
            dbc.Tab(label="CRM", tab_id="crm"),
            dbc.Tab(label="설정", tab_id="sales-settings")
        ], id="sales-tabs", active_tab="quotation"),
        
        html.Div(id="sales-tab-content", className="mt-4"),
        
        # 모달들
        create_quotation_modal(),
        create_order_modal(),
        create_customer_modal(),
        
        # 다운로드 컴포넌트
        dcc.Download(id="download-sales-data")
    ], fluid=True, className="py-4")

def create_quotation_management():
    """견적 관리 화면"""
    return html.Div([
        # 견적 현황 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-file-invoice fa-2x text-primary mb-2"),
                        ], className="text-center"),
                        html.H6("진행중 견적", className="text-muted text-center"),
                        html.H3("0", id="active-quotes", className="text-center"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="primary", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-handshake fa-2x text-success mb-2"),
                        ], className="text-center"),
                        html.H6("수주 전환율", className="text-muted text-center"),
                        html.H3("0%", id="conversion-rate", className="text-center"),
                        html.P("최근 30일", className="text-muted mb-0 text-center")
                    ])
                ], color="success", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-clock fa-2x text-warning mb-2"),
                        ], className="text-center"),
                        html.H6("응답 대기", className="text-muted text-center"),
                        html.H3("0", id="pending-quotes", className="text-center text-warning"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="warning", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-won-sign fa-2x text-info mb-2"),
                        ], className="text-center"),
                        html.H6("이번달 견적액", className="text-muted text-center"),
                        html.H3("₩0", id="monthly-quotes", className="text-center"),
                        html.P("원", className="text-muted mb-0 text-center")
                    ])
                ], color="info", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 견적서 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("견적서 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "신규 견적"],
                        id="new-quote-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-file-excel me-2"), "견적서 가져오기"],
                        id="import-quote-btn",
                        color="success",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 검색 필터
                dbc.Row([
                    dbc.Col([
                        dbc.Label("기간"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="quote-start-date",
                                type="date",
                                value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="quote-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("상태"),
                        dbc.Select(
                            id="quote-status-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "작성중", "value": "draft"},
                                {"label": "발송완료", "value": "sent"},
                                {"label": "고객검토", "value": "reviewing"},
                                {"label": "수주확정", "value": "won"},
                                {"label": "수주실패", "value": "lost"},
                                {"label": "만료", "value": "expired"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("고객"),
                        dbc.Select(
                            id="quote-customer-filter",
                            options=[{"label": "전체", "value": "all"}],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-quotes-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 견적서 리스트
                html.Div(id="quotation-list-table")
            ])
        ]),
        
        # 견적 현황 차트
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("월별 견적 추이"),
                    dbc.CardBody([
                        dcc.Graph(id="monthly-quote-trend")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("견적 상태별 분포"),
                    dbc.CardBody([
                        dcc.Graph(id="quote-status-pie")
                    ])
                ])
            ], md=6)
        ], className="mt-4")
    ])

def create_order_management():
    """수주 관리 화면"""
    return html.Div([
        # 수주 현황 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("이번달 수주"),
                    dbc.CardBody([
                        html.H3("₩0", id="monthly-orders", className="text-primary"),
                        html.P("전월 대비: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("진행중 수주"),
                    dbc.CardBody([
                        html.H3("0", id="active-orders", className="text-info"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("배송 예정"),
                    dbc.CardBody([
                        html.H3("0", id="pending-delivery-orders", className="text-warning"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("완료"),
                    dbc.CardBody([
                        html.H3("0", id="completed-orders", className="text-success"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 수주 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("수주 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "신규 수주"],
                        id="new-order-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-sync me-2"), "견적에서 변환"],
                        id="convert-quote-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 수주 리스트
                html.Div(id="order-list-table")
            ])
        ]),
        
        # 납기 관리
        dbc.Card([
            dbc.CardHeader("납기 관리"),
            dbc.CardBody([
                dcc.Graph(id="delivery-schedule-chart")
            ])
        ], className="mt-4")
    ])

def create_customer_management():
    """고객 관리 화면"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4([html.I(className="fas fa-users me-2"), "고객 관리"]),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "고객 등록"],
                    id="add-customer-btn",
                    color="primary",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                # 검색
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(
                                id="customer-search",
                                placeholder="고객명, 사업자번호로 검색..."
                            )
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Select(
                            id="customer-grade-filter",
                            options=[
                                {"label": "전체 등급", "value": "all"},
                                {"label": "VIP", "value": "VIP"},
                                {"label": "Gold", "value": "Gold"},
                                {"label": "Silver", "value": "Silver"},
                                {"label": "Bronze", "value": "Bronze"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-filter me-2"), "필터"],
                            id="filter-customer-btn",
                            color="secondary",
                            className="w-100"
                        )
                    ], md=3)
                ], className="mb-3"),
                
                # 고객 리스트
                html.Div(id="customer-list-table")
            ])
        ]),
        
        # 고객 분석
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("고객별 매출"),
                    dbc.CardBody([
                        dcc.Graph(id="customer-sales-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("고객 등급 분포"),
                    dbc.CardBody([
                        dcc.Graph(id="customer-grade-chart")
                    ])
                ])
            ], md=6)
        ], className="mt-4")
    ])

def create_sales_analysis():
    """영업 분석 화면"""
    return html.Div([
        # 분석 기간 설정
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("분석 기간"),
                        dbc.RadioItems(
                            id="sales-analysis-period",
                            options=[
                                {"label": "이번달", "value": "month"},
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
                    dbc.CardHeader("매출 성과"),
                    dbc.CardBody([
                        dcc.Graph(id="sales-performance-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("영업 파이프라인"),
                    dbc.CardBody([
                        dcc.Graph(id="sales-pipeline-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 영업사원별 분석
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("영업사원별 실적"),
                    dbc.CardBody([
                        dcc.Graph(id="salesperson-performance-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("제품별 매출"),
                    dbc.CardBody([
                        dcc.Graph(id="product-sales-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 예측 분석
        dbc.Card([
            dbc.CardHeader([
                html.H5("매출 예측"),
                dbc.Badge("AI", color="info", className="ms-2")
            ]),
            dbc.CardBody([
                dcc.Graph(id="sales-forecast-chart")
            ])
        ])
    ])

def create_crm():
    """CRM 화면"""
    return html.Div([
        # 활동 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("오늘 활동", className="text-muted"),
                        html.H3("0", id="today-activities"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("이번주 미팅", className="text-muted"),
                        html.H3("0", id="week-meetings"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("팔로업 대기", className="text-muted"),
                        html.H3("0", id="pending-followup"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Hot 리드", className="text-muted"),
                        html.H3("0", id="hot-leads"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # CRM 대시보드
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("영업 활동 관리"),
                    dbc.CardBody([
                        dbc.ButtonGroup([
                            dbc.Button(
                                [html.I(className="fas fa-plus me-2"), "활동 추가"],
                                id="add-activity-btn",
                                color="primary",
                                size="sm"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-calendar me-2"), "미팅 일정"],
                                id="schedule-meeting-btn",
                                color="info",
                                size="sm"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-envelope me-2"), "이메일 발송"],
                                id="send-email-btn",
                                color="success",
                                size="sm"
                            )
                        ], className="mb-3"),
                        
                        html.Div(id="activity-list")
                    ])
                ])
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("영업 기회"),
                    dbc.CardBody([
                        html.Div(id="opportunity-list")
                    ])
                ])
            ], md=4)
        ])
    ])

def create_sales_settings():
    """영업관리 설정"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-cog me-2"), "영업관리 설정"])
        ]),
        dbc.CardBody([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5("견적서 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("견적서 유효기간 (일)"),
                                dbc.Input(
                                    id="quote-validity-days",
                                    type="number",
                                    value="30"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("기본 할인율 (%)"),
                                dbc.Input(
                                    id="default-discount-rate",
                                    type="number",
                                    value="0",
                                    min="0",
                                    max="50"
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("자동 견적 번호"),
                                dbc.Switch(
                                    id="auto-quote-number",
                                    value=True,
                                    label="사용"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("견적서 템플릿"),
                                dbc.Select(
                                    id="quote-template",
                                    options=[
                                        {"label": "기본 템플릿", "value": "default"},
                                        {"label": "상세 템플릿", "value": "detailed"},
                                        {"label": "간소 템플릿", "value": "simple"}
                                    ],
                                    value="default"
                                )
                            ], md=6)
                        ])
                    ])
                ], title="견적서"),
                
                dbc.AccordionItem([
                    html.H5("영업 프로세스", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("영업 단계"),
                                dbc.ListGroup([
                                    dbc.ListGroupItem("1. 리드 생성"),
                                    dbc.ListGroupItem("2. 초기 접촉"),
                                    dbc.ListGroupItem("3. 요구사항 분석"),
                                    dbc.ListGroupItem("4. 견적 제출"),
                                    dbc.ListGroupItem("5. 협상"),
                                    dbc.ListGroupItem("6. 계약 체결"),
                                    dbc.ListGroupItem("7. 완료")
                                ])
                            ])
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("자동 알림"),
                                dbc.Checklist(
                                    id="sales-notifications",
                                    options=[
                                        {"label": "견적서 만료 알림", "value": "quote_expiry"},
                                        {"label": "팔로업 알림", "value": "followup"},
                                        {"label": "납기일 알림", "value": "delivery"},
                                        {"label": "고객 생일 알림", "value": "birthday"}
                                    ],
                                    value=["quote_expiry", "followup", "delivery"]
                                )
                            ])
                        ])
                    ])
                ], title="프로세스"),
                
                dbc.AccordionItem([
                    html.H5("고객 등급 관리", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("등급 기준 (연간 매출액)"),
                                html.Div([
                                    dbc.InputGroup([
                                        dbc.InputGroupText("VIP"),
                                        dbc.Input(
                                            id="vip-threshold",
                                            type="number",
                                            value="100000000"
                                        ),
                                        dbc.InputGroupText("원 이상")
                                    ], className="mb-2"),
                                    dbc.InputGroup([
                                        dbc.InputGroupText("Gold"),
                                        dbc.Input(
                                            id="gold-threshold",
                                            type="number",
                                            value="50000000"
                                        ),
                                        dbc.InputGroupText("원 이상")
                                    ], className="mb-2"),
                                    dbc.InputGroup([
                                        dbc.InputGroupText("Silver"),
                                        dbc.Input(
                                            id="silver-threshold",
                                            type="number",
                                            value="10000000"
                                        ),
                                        dbc.InputGroupText("원 이상")
                                    ])
                                ])
                            ])
                        ])
                    ])
                ], title="고객 등급")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "설정 저장"],
                        id="save-sales-settings-btn",
                        color="primary",
                        className="mt-3"
                    )
                ])
            ]),
            
            html.Div(id="sales-settings-message", className="mt-3")
        ])
    ])

def create_quotation_modal():
    """견적서 작성 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("견적서 작성")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("견적번호"),
                        dbc.Input(
                            id="modal-quote-number",
                            value=f"QT-{datetime.now().strftime('%Y%m%d')}-",
                            disabled=True
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("견적일자"),
                        dbc.Input(
                            id="modal-quote-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("고객"),
                        dbc.Select(
                            id="modal-quote-customer",
                            options=[],
                            placeholder="고객 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("유효기간"),
                        dbc.Input(
                            id="modal-quote-validity",
                            type="date",
                            value=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                html.Hr(),
                
                # 견적 품목 추가 영역
                html.H6("견적 품목"),
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="quote-product-search",
                                placeholder="제품 검색..."
                            ),
                            dbc.Button(
                                html.I(className="fas fa-plus"),
                                id="add-quote-item-btn",
                                color="primary"
                            )
                        ])
                    ])
                ], className="mb-3"),
                
                # 견적 품목 리스트
                html.Div(id="quote-items-list"),
                
                html.Hr(),
                
                # 합계
                dbc.Row([
                    dbc.Col([
                        html.H5("총 견적금액:", className="text-end")
                    ], md=8),
                    dbc.Col([
                        html.H5("₩0", id="quote-total-amount", className="text-end text-primary")
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("특이사항"),
                        dbc.Textarea(
                            id="modal-quote-notes",
                            rows=3
                        )
                    ])
                ])
            ]),
            
            html.Div(id="quote-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-quote-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-quote-btn",
                color="primary"
            )
        ])
    ], id="quotation-modal", size="xl", is_open=False)

def create_order_modal():
    """수주 입력 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("수주 등록")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("수주번호"),
                        dbc.Input(
                            id="modal-order-number",
                            value=f"SO-{datetime.now().strftime('%Y%m%d')}-",
                            disabled=True
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("수주일자"),
                        dbc.Input(
                            id="modal-order-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("고객"),
                        dbc.Select(
                            id="modal-order-customer",
                            options=[],
                            placeholder="고객 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("납기일"),
                        dbc.Input(
                            id="modal-delivery-date",
                            type="date",
                            value=(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("견적번호 (선택)"),
                        dbc.Select(
                            id="modal-related-quote",
                            options=[{"label": "견적서 없음", "value": "none"}],
                            value="none"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("수주 상태"),
                        dbc.Select(
                            id="modal-order-status",
                            options=[
                                {"label": "접수", "value": "received"},
                                {"label": "확정", "value": "confirmed"},
                                {"label": "생산중", "value": "in_production"},
                                {"label": "완료", "value": "completed"}
                            ],
                            value="received"
                        )
                    ], md=6)
                ])
            ]),
            
            html.Div(id="order-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-order-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-order-btn",
                color="primary"
            )
        ])
    ], id="order-modal", size="lg", is_open=False)

def create_customer_modal():
    """고객 등록/수정 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("고객 등록")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("고객코드", html_for="modal-customer-code"),
                        dbc.Input(
                            id="modal-customer-code",
                            placeholder="예: CUST001"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("고객명", html_for="modal-customer-name"),
                        dbc.Input(
                            id="modal-customer-name",
                            placeholder="예: (주)ABC"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("사업자번호"),
                        dbc.Input(
                            id="modal-customer-business-no",
                            placeholder="123-45-67890"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("대표자명"),
                        dbc.Input(
                            id="modal-customer-ceo"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("담당자"),
                        dbc.Input(
                            id="modal-customer-contact"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("전화번호"),
                        dbc.Input(
                            id="modal-customer-phone",
                            placeholder="02-1234-5678"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("이메일"),
                        dbc.Input(
                            id="modal-customer-email",
                            type="email"
                        )
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("주소"),
                        dbc.Textarea(
                            id="modal-customer-address",
                            rows=2
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("고객 등급"),
                        dbc.Select(
                            id="modal-customer-grade",
                            options=[
                                {"label": "VIP", "value": "VIP"},
                                {"label": "Gold", "value": "Gold"},
                                {"label": "Silver", "value": "Silver"},
                                {"label": "Bronze", "value": "Bronze"}
                            ],
                            value="Bronze"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("결제조건"),
                        dbc.Select(
                            id="modal-customer-payment-terms",
                            options=[
                                {"label": "현금", "value": "CASH"},
                                {"label": "30일", "value": "NET30"},
                                {"label": "60일", "value": "NET60"},
                                {"label": "90일", "value": "NET90"}
                            ],
                            value="NET30"
                        )
                    ], md=6)
                ])
            ]),
            
            html.Div(id="customer-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-customer-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-customer-btn",
                color="primary"
            )
        ])
    ], id="customer-modal", size="lg", is_open=False)
