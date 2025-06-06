# File: /modules/purchase/layouts.py

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_purchase_layout():
    """구매관리 모듈 메인 레이아웃"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-shopping-cart me-2"), "구매관리 시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="발주 관리", tab_id="po-management"),
            dbc.Tab(label="입고 검수", tab_id="receiving"),
            dbc.Tab(label="거래처 관리", tab_id="supplier"),
            dbc.Tab(label="구매 분석", tab_id="purchase-analysis"),
            dbc.Tab(label="설정", tab_id="purchase-settings")
        ], id="purchase-tabs", active_tab="po-management"),
        
        html.Div(id="purchase-tab-content", className="mt-4"),
        
        # 모달들
        create_po_modal(),
        create_supplier_modal(),
        
        # 다운로드 컴포넌트
        dcc.Download(id="download-purchase-data")
    ], fluid=True, className="py-4")

def create_po_management():
    """발주 관리 화면"""
    return html.Div([
        # 발주 현황 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-file-invoice fa-2x text-primary mb-2"),
                        ], className="text-center"),
                        html.H6("진행중 발주", className="text-muted text-center"),
                        html.H3("0", id="active-po-count", className="text-center"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="primary", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-clock fa-2x text-warning mb-2"),
                        ], className="text-center"),
                        html.H6("입고 대기", className="text-muted text-center"),
                        html.H3("0", id="pending-delivery", className="text-center"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="warning", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-exclamation-triangle fa-2x text-danger mb-2"),
                        ], className="text-center"),
                        html.H6("긴급 발주", className="text-muted text-center"),
                        html.H3("0", id="urgent-po", className="text-center text-danger"),
                        html.P("건", className="text-muted mb-0 text-center")
                    ])
                ], color="danger", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-won-sign fa-2x text-success mb-2"),
                        ], className="text-center"),
                        html.H6("이번달 구매액", className="text-muted text-center"),
                        html.H3("₩0", id="monthly-purchase", className="text-center"),
                        html.P("원", className="text-muted mb-0 text-center")
                    ])
                ], color="success", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 발주서 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("발주서 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "신규 발주"],
                        id="new-po-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-robot me-2"), "자동 발주"],
                        id="auto-po-btn",
                        color="info",
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
                                id="po-start-date",
                                type="date",
                                value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="po-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("상태"),
                        dbc.Select(
                            id="po-status-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "작성중", "value": "draft"},
                                {"label": "승인대기", "value": "pending"},
                                {"label": "승인완료", "value": "approved"},
                                {"label": "입고중", "value": "receiving"},
                                {"label": "완료", "value": "completed"},
                                {"label": "취소", "value": "cancelled"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("거래처"),
                        dbc.Select(
                            id="po-supplier-filter",
                            options=[{"label": "전체", "value": "all"}],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-po-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 발주서 리스트
                html.Div(id="po-list-table")
            ])
        ]),
        
        # 자동 발주 제안
        dbc.Card([
            dbc.CardHeader([
                html.H5("자동 발주 제안"),
                dbc.Badge("AI", color="info", className="ms-2")
            ]),
            dbc.CardBody([
                html.Div(id="auto-po-suggestions")
            ])
        ], className="mt-4")
    ])

def create_receiving():
    """입고 검수 화면"""
    return html.Div([
        # 입고 예정 현황
        dbc.Card([
            dbc.CardHeader([
                html.H4([html.I(className="fas fa-truck-loading me-2"), "입고 예정"])
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("입고 예정일"),
                        dbc.Input(
                            id="receiving-date-filter",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-sync me-2"), "새로고침"],
                            id="refresh-receiving",
                            color="secondary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                html.Div(id="receiving-schedule-table")
            ])
        ]),
        
        # 입고 검수 처리
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("입고 검수 처리"),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("발주번호"),
                                    dbc.Input(
                                        id="inspection-po-number",
                                        placeholder="발주번호 스캔/입력..."
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("입고일자"),
                                    dbc.Input(
                                        id="inspection-date",
                                        type="date",
                                        value=datetime.now().strftime('%Y-%m-%d')
                                    )
                                ], md=6)
                            ], className="mb-3"),
                            
                            # 품목별 검수
                            html.Div(id="inspection-items"),
                            
                            dbc.Button(
                                [html.I(className="fas fa-check-circle me-2"), "검수 완료"],
                                id="complete-inspection-btn",
                                color="success",
                                size="lg",
                                className="w-100 mt-3"
                            )
                        ]),
                        
                        html.Div(id="inspection-message", className="mt-3")
                    ])
                ])
            ], md=6),
            
            # 검수 이력
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("최근 검수 이력"),
                    dbc.CardBody([
                        html.Div(id="inspection-history")
                    ])
                ])
            ], md=6)
        ], className="mt-4")
    ])

def create_supplier_management():
    """거래처 관리 화면"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4([html.I(className="fas fa-building me-2"), "거래처 관리"]),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "거래처 등록"],
                    id="add-supplier-btn",
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
                                id="supplier-search",
                                placeholder="거래처명, 사업자번호로 검색..."
                            )
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Select(
                            id="supplier-rating-filter",
                            options=[
                                {"label": "전체 등급", "value": "all"},
                                {"label": "⭐⭐⭐⭐⭐ 우수", "value": "5"},
                                {"label": "⭐⭐⭐⭐ 양호", "value": "4"},
                                {"label": "⭐⭐⭐ 보통", "value": "3"},
                                {"label": "⭐⭐ 주의", "value": "2"},
                                {"label": "⭐ 위험", "value": "1"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-filter me-2"), "필터"],
                            id="filter-supplier-btn",
                            color="secondary",
                            className="w-100"
                        )
                    ], md=3)
                ], className="mb-3"),
                
                # 거래처 리스트
                html.Div(id="supplier-list-table")
            ])
        ]),
        
        # 거래처 상세 정보
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("거래처 실적"),
                    dbc.CardBody([
                        dcc.Graph(id="supplier-performance-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("품목별 공급 현황"),
                    dbc.CardBody([
                        html.Div(id="supplier-items-table")
                    ])
                ])
            ], md=6)
        ], className="mt-4")
    ])

def create_purchase_analysis():
    """구매 분석 화면"""
    return html.Div([
        # 분석 기간 설정
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("분석 기간"),
                        dbc.RadioItems(
                            id="analysis-period",
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
        
        # 구매 비용 분석
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("구매 비용 추이"),
                    dbc.CardBody([
                        dcc.Graph(id="purchase-cost-trend")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("카테고리별 구매 비중"),
                    dbc.CardBody([
                        dcc.Graph(id="category-purchase-pie")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 거래처 분석
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOP 10 거래처"),
                    dbc.CardBody([
                        dcc.Graph(id="top-suppliers-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("리드타임 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="leadtime-analysis")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 상세 분석 테이블
        dbc.Card([
            dbc.CardHeader([
                html.H5("구매 상세 분석"),
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "리포트 다운로드"],
                    id="download-analysis-report",
                    color="success",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                html.Div(id="purchase-analysis-table")
            ])
        ])
    ])

def create_purchase_settings():
    """구매관리 설정"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-cog me-2"), "구매관리 설정"])
        ]),
        dbc.CardBody([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5("자동 발주 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("자동 발주 사용"),
                                dbc.Switch(
                                    id="enable-auto-po",
                                    value=True,
                                    label="활성화"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("발주점 계산 방식"),
                                dbc.RadioItems(
                                    id="reorder-calc-method",
                                    options=[
                                        {"label": "안전재고 기준", "value": "safety"},
                                        {"label": "평균 사용량 기준", "value": "average"},
                                        {"label": "리드타임 고려", "value": "leadtime"}
                                    ],
                                    value="safety"
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("발주 알림"),
                                dbc.Checklist(
                                    id="po-notifications",
                                    options=[
                                        {"label": "발주점 도달 시", "value": "reorder"},
                                        {"label": "입고 예정일 임박", "value": "delivery"},
                                        {"label": "긴급 발주 필요", "value": "urgent"}
                                    ],
                                    value=["reorder", "urgent"]
                                )
                            ])
                        ])
                    ])
                ], title="자동 발주"),
                
                dbc.AccordionItem([
                    html.H5("승인 프로세스", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("승인 권한 금액 (만원)"),
                                html.Div([
                                    dbc.InputGroup([
                                        dbc.InputGroupText("일반 사용자"),
                                        dbc.Input(
                                            id="approval-limit-user",
                                            type="number",
                                            value="100"
                                        ),
                                        dbc.InputGroupText("만원")
                                    ], className="mb-2"),
                                    dbc.InputGroup([
                                        dbc.InputGroupText("관리자"),
                                        dbc.Input(
                                            id="approval-limit-admin",
                                            type="number",
                                            value="1000"
                                        ),
                                        dbc.InputGroupText("만원")
                                    ])
                                ])
                            ])
                        ])
                    ])
                ], title="승인 설정"),
                
                dbc.AccordionItem([
                    html.H5("기본값 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("기본 리드타임 (일)"),
                                dbc.Input(
                                    id="default-leadtime",
                                    type="number",
                                    value="7"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("기본 결제조건"),
                                dbc.Select(
                                    id="default-payment-terms",
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
                    ])
                ], title="기본값")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "설정 저장"],
                        id="save-purchase-settings-btn",
                        color="primary",
                        className="mt-3"
                    )
                ])
            ]),
            
            html.Div(id="purchase-settings-message", className="mt-3")
        ])
    ])

def create_po_modal():
    """발주서 작성 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("발주서 작성")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("발주번호"),
                        dbc.Input(
                            id="modal-po-number",
                            value=f"PO-{datetime.now().strftime('%Y%m%d')}-",
                            disabled=True
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("발주일자"),
                        dbc.Input(
                            id="modal-po-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("거래처"),
                        dbc.Select(
                            id="modal-supplier",
                            options=[],
                            placeholder="거래처 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("납기일"),
                        dbc.Input(
                            id="modal-delivery-date",
                            type="date",
                            value=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                html.Hr(),
                
                # 품목 추가 영역
                html.H6("발주 품목"),
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="po-item-search",
                                placeholder="품목 검색..."
                            ),
                            dbc.Button(
                                html.I(className="fas fa-plus"),
                                id="add-po-item-btn",
                                color="primary"
                            )
                        ])
                    ])
                ], className="mb-3"),
                
                # 발주 품목 리스트
                html.Div(id="po-items-list"),
                
                html.Hr(),
                
                # 합계
                dbc.Row([
                    dbc.Col([
                        html.H5("합계 금액:", className="text-end")
                    ], md=8),
                    dbc.Col([
                        html.H5("₩0", id="po-total-amount", className="text-end text-primary")
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("비고"),
                        dbc.Textarea(
                            id="modal-po-remarks",
                            rows=2
                        )
                    ])
                ])
            ]),
            
            html.Div(id="po-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-po-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-po-btn",
                color="primary"
            )
        ])
    ], id="po-modal", size="xl", is_open=False)

def create_supplier_modal():
    """거래처 등록/수정 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("거래처 등록")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("거래처 코드", html_for="modal-supplier-code"),
                        dbc.Input(
                            id="modal-supplier-code",
                            placeholder="예: SUP001"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("거래처명", html_for="modal-supplier-name"),
                        dbc.Input(
                            id="modal-supplier-name",
                            placeholder="예: (주)ABC"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("사업자번호"),
                        dbc.Input(
                            id="modal-business-no",
                            placeholder="123-45-67890"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("대표자명"),
                        dbc.Input(
                            id="modal-ceo-name"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("담당자"),
                        dbc.Input(
                            id="modal-contact-person"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("전화번호"),
                        dbc.Input(
                            id="modal-phone",
                            placeholder="02-1234-5678"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("이메일"),
                        dbc.Input(
                            id="modal-email",
                            type="email"
                        )
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("주소"),
                        dbc.Textarea(
                            id="modal-address",
                            rows=2
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("결제조건"),
                        dbc.Select(
                            id="modal-payment-terms",
                            options=[
                                {"label": "현금", "value": "CASH"},
                                {"label": "30일", "value": "NET30"},
                                {"label": "60일", "value": "NET60"},
                                {"label": "90일", "value": "NET90"}
                            ],
                            value="NET30"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("리드타임 (일)"),
                        dbc.Input(
                            id="modal-leadtime",
                            type="number",
                            value="7"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("등급"),
                        dbc.Select(
                            id="modal-rating",
                            options=[
                                {"label": "⭐⭐⭐⭐⭐ 우수", "value": "5"},
                                {"label": "⭐⭐⭐⭐ 양호", "value": "4"},
                                {"label": "⭐⭐⭐ 보통", "value": "3"},
                                {"label": "⭐⭐ 주의", "value": "2"},
                                {"label": "⭐ 위험", "value": "1"}
                            ],
                            value="3"
                        )
                    ], md=4)
                ])
            ]),
            
            html.Div(id="supplier-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-supplier-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-supplier-btn",
                color="primary"
            )
        ])
    ], id="supplier-modal", size="lg", is_open=False)
