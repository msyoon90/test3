# File: /modules/inventory/layouts.py
# 재고관리 모듈 레이아웃 - 전체 코드

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_inventory_layout():
    """재고관리 모듈 메인 레이아웃"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-boxes me-2"), "재고관리 시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="품목 관리", tab_id="item-master"),
            dbc.Tab(label="입출고", tab_id="stock-inout"),
            dbc.Tab(label="재고 현황", tab_id="stock-status"),
            dbc.Tab(label="재고 조정", tab_id="stock-adjust"),
            dbc.Tab(label="설정", tab_id="inv-settings")
        ], id="inventory-tabs", active_tab="item-master"),
        
        html.Div(id="inventory-tab-content", className="mt-4"),
        
        # 품목 추가/수정 모달
        create_item_modal(),
        
        # Excel 다운로드 컴포넌트
        dcc.Download(id="download-dataframe-xlsx")
    ], fluid=True, className="py-4")

def create_item_master():
    """품목 마스터 관리"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4([html.I(className="fas fa-cube me-2"), "품목 마스터"]),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "신규 품목"],
                    id="add-item-btn",
                    color="primary",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                # 검색 영역
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(
                                id="item-search",
                                placeholder="품목코드, 품목명으로 검색..."
                            )
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Select(
                            id="item-category",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "원자재", "value": "material"},
                                {"label": "부품", "value": "component"},
                                {"label": "제품", "value": "product"},
                                {"label": "소모품", "value": "consumable"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-filter me-2"), "필터"],
                            id="filter-items-btn",
                            color="secondary",
                            className="w-100"
                        )
                    ], md=3)
                ], className="mb-3"),
                
                # 품목 리스트 테이블
                html.Div(id="item-master-table"),
                
                # 페이지네이션
                dbc.Pagination(
                    id="item-pagination",
                    max_value=10,
                    fully_expanded=False,
                    first_last=True,
                    previous_next=True,
                    className="mt-3"
                )
            ])
        ])
    ])

def create_stock_inout():
    """입출고 관리"""
    return html.Div([
        dbc.Row([
            # 입고 카드
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([html.I(className="fas fa-sign-in-alt me-2"), "입고 처리"]),
                    ]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("입고일자"),
                                    dbc.Input(
                                        id="in-date",
                                        type="date",
                                        value=datetime.now().strftime('%Y-%m-%d')
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("입고유형"),
                                    dbc.Select(
                                        id="in-type",
                                        options=[
                                            {"label": "구매입고", "value": "purchase"},
                                            {"label": "생산입고", "value": "production"},
                                            {"label": "반품입고", "value": "return"},
                                            {"label": "기타입고", "value": "other"}
                                        ]
                                    )
                                ], md=6)
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("품목 선택"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="in-item-search",
                                            placeholder="품목코드 또는 품목명..."
                                        ),
                                        dbc.Button(
                                            html.I(className="fas fa-search"),
                                            id="search-in-item-btn",
                                            color="primary"
                                        )
                                    ])
                                ])
                            ], className="mb-3"),
                            
                            # 선택된 품목 표시
                            html.Div(id="in-item-display", className="mb-3"),
                            
                            # 숨겨진 품목코드 필드
                            dbc.Input(id="in-item-code", type="hidden"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("수량"),
                                    dbc.Input(
                                        id="in-qty",
                                        type="number",
                                        min=1
                                    )
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("단위"),
                                    dbc.Input(
                                        id="in-unit",
                                        value="EA",
                                        disabled=True
                                    )
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("창고"),
                                    dbc.Select(
                                        id="in-warehouse",
                                        options=[
                                            {"label": "창고1", "value": "wh1"},
                                            {"label": "창고2", "value": "wh2"}
                                        ]
                                    )
                                ], md=4)
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("비고"),
                                    dbc.Textarea(
                                        id="in-remarks",
                                        rows=2
                                    )
                                ])
                            ], className="mb-3"),
                            
                            dbc.Button(
                                [html.I(className="fas fa-save me-2"), "입고 처리"],
                                id="save-in-btn",
                                color="success",
                                size="lg",
                                className="w-100"
                            ),
                            
                            # 메시지 영역
                            html.Div(id="in-message", className="mt-3")
                        ])
                    ])
                ])
            ], md=6),
            
            # 출고 카드
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([html.I(className="fas fa-sign-out-alt me-2"), "출고 처리"]),
                    ]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("출고일자"),
                                    dbc.Input(
                                        id="out-date",
                                        type="date",
                                        value=datetime.now().strftime('%Y-%m-%d')
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("출고유형"),
                                    dbc.Select(
                                        id="out-type",
                                        options=[
                                            {"label": "생산출고", "value": "production"},
                                            {"label": "판매출고", "value": "sales"},
                                            {"label": "폐기출고", "value": "disposal"},
                                            {"label": "기타출고", "value": "other"}
                                        ]
                                    )
                                ], md=6)
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("품목 선택"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="out-item-search",
                                            placeholder="품목코드 또는 품목명..."
                                        ),
                                        dbc.Button(
                                            html.I(className="fas fa-search"),
                                            id="search-out-item-btn",
                                            color="primary"
                                        )
                                    ])
                                ])
                            ], className="mb-3"),
                            
                            # 선택된 품목 표시
                            html.Div(id="out-item-display", className="mb-3"),
                            
                            # 숨겨진 품목코드 필드
                            dbc.Input(id="out-item-code", type="hidden"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("수량"),
                                    dbc.Input(
                                        id="out-qty",
                                        type="number",
                                        min=1
                                    )
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("단위"),
                                    dbc.Input(
                                        id="out-unit",
                                        value="EA",
                                        disabled=True
                                    )
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("창고"),
                                    dbc.Select(
                                        id="out-warehouse",
                                        options=[
                                            {"label": "창고1", "value": "wh1"},
                                            {"label": "창고2", "value": "wh2"}
                                        ]
                                    )
                                ], md=4)
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("비고"),
                                    dbc.Textarea(
                                        id="out-remarks",
                                        rows=2
                                    )
                                ])
                            ], className="mb-3"),
                            
                            dbc.Button(
                                [html.I(className="fas fa-save me-2"), "출고 처리"],
                                id="save-out-btn",
                                color="danger",
                                size="lg",
                                className="w-100"
                            ),
                            
                            # 메시지 영역
                            html.Div(id="out-message", className="mt-3")
                        ])
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 입출고 이력
        dbc.Card([
            dbc.CardHeader([
                html.H5("최근 입출고 이력"),
                dbc.Button(
                    [html.I(className="fas fa-sync me-2"), "새로고침"],
                    id="refresh-inout-history",
                    color="secondary",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                html.Div(id="inout-history-table")
            ])
        ])
    ])

def create_stock_status():
    """재고 현황"""
    return html.Div([
        # 요약 카드
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-cubes fa-2x text-primary mb-2"),
                        ], className="text-center"),
                        html.H6("전체 품목", className="text-muted text-center"),
                        html.H3("0", id="total-items", className="text-center"),
                        html.P("종", className="text-muted mb-0 text-center")
                    ])
                ], color="primary", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-won-sign fa-2x text-success mb-2"),
                        ], className="text-center"),
                        html.H6("총 재고금액", className="text-muted text-center"),
                        html.H3("₩0", id="total-stock-value", className="text-center"),
                        html.P("원", className="text-muted mb-0 text-center")
                    ])
                ], color="success", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-exclamation-triangle fa-2x text-danger mb-2"),
                        ], className="text-center"),
                        html.H6("부족 품목", className="text-muted text-center"),
                        html.H3("0", id="shortage-items", className="text-center text-danger"),
                        html.P("종", className="text-muted mb-0 text-center")
                    ])
                ], color="danger", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-archive fa-2x text-warning mb-2"),
                        ], className="text-center"),
                        html.H6("과잉 품목", className="text-muted text-center"),
                        html.H3("0", id="excess-items", className="text-center text-warning"),
                        html.P("종", className="text-muted mb-0 text-center")
                    ])
                ], color="warning", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 재고 현황 테이블
        dbc.Card([
            dbc.CardHeader([
                html.H4("재고 현황"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-file-excel me-2"), "Excel"],
                        id="export-stock-excel",
                        color="success",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-print me-2"), "인쇄"],
                        id="print-stock",
                        color="secondary",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 필터
                dbc.Row([
                    dbc.Col([
                        dbc.Label("창고"),
                        dbc.Select(
                            id="stock-warehouse-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "창고1", "value": "wh1"},
                                {"label": "창고2", "value": "wh2"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("재고상태"),
                        dbc.Select(
                            id="stock-status-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "정상", "value": "normal"},
                                {"label": "부족", "value": "shortage"},
                                {"label": "과잉", "value": "excess"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),  # 빈 레이블로 정렬
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-stock-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 재고 테이블
                html.Div(id="stock-status-table")
            ])
        ]),
        
        # 재고 추이 차트
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("재고 추이"),
                    dbc.CardBody([
                        dcc.Graph(id="stock-trend-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("창고별 재고 현황"),
                    dbc.CardBody([
                        dcc.Graph(id="warehouse-stock-chart")
                    ])
                ])
            ], md=6)
        ], className="mt-4")
    ])

def create_stock_adjust():
    """재고 조정"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4([html.I(className="fas fa-sliders-h me-2"), "재고 조정"])
            ]),
            dbc.CardBody([
                dbc.Alert(
                    [
                        html.I(className="fas fa-info-circle me-2"),
                        "재고 조정은 실사 결과나 시스템 오류로 인한 재고 수량 보정 시 사용합니다."
                    ],
                    color="info"
                ),
                
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("조정일자"),
                            dbc.Input(
                                id="adjust-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ], md=6),
                        dbc.Col([
                            dbc.Label("조정유형"),
                            dbc.Select(
                                id="adjust-type",
                                options=[
                                    {"label": "실사조정", "value": "inventory"},
                                    {"label": "손실처리", "value": "loss"},
                                    {"label": "시스템오류", "value": "system"},
                                    {"label": "기타", "value": "other"}
                                ]
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("품목 선택"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="adjust-item-search",
                                    placeholder="품목코드 또는 품목명..."
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-search"),
                                    id="search-adjust-item-btn",
                                    color="primary"
                                )
                            ])
                        ])
                    ], className="mb-3"),
                    
# File: /modules/inventory/layouts.py (계속)

                   # 선택된 품목 표시
                   html.Div(id="adjust-item-display", className="mb-3"),
                   
                   # 숨겨진 품목코드 필드
                   dbc.Input(id="adjust-item-code", type="hidden"),
                   
                   dbc.Row([
                       dbc.Col([
                           dbc.Label("현재 재고"),
                           dbc.Input(
                               id="current-stock",
                               type="number",
                               disabled=True
                           )
                       ], md=4),
                       dbc.Col([
                           dbc.Label("조정 후 재고"),
                           dbc.Input(
                               id="adjusted-stock",
                               type="number",
                               min=0
                           )
                       ], md=4),
                       dbc.Col([
                           dbc.Label("차이"),
                           dbc.Input(
                               id="adjust-diff",
                               type="number",
                               disabled=True
                           )
                       ], md=4)
                   ], className="mb-3"),
                   
                   dbc.Row([
                       dbc.Col([
                           dbc.Label("조정 사유"),
                           dbc.Textarea(
                               id="adjust-reason",
                               rows=3,
                               placeholder="조정 사유를 상세히 입력하세요..."
                           )
                       ])
                   ], className="mb-3"),
                   
                   dbc.Button(
                       [html.I(className="fas fa-check me-2"), "조정 처리"],
                       id="save-adjust-btn",
                       color="warning",
                       size="lg",
                       className="w-100"
                   ),
                   
                   # 메시지 영역
                   html.Div(id="adjust-message", className="mt-3")
               ])
           ])
       ]),
       
       # 조정 이력
       dbc.Card([
           dbc.CardHeader("최근 조정 이력"),
           dbc.CardBody([
               html.Div(id="adjust-history-table")
           ])
       ], className="mt-4")
   ])

def create_inventory_settings():
   """재고관리 설정"""
   return dbc.Card([
       dbc.CardHeader([
           html.H4([html.I(className="fas fa-cog me-2"), "재고관리 설정"])
       ]),
       dbc.CardBody([
           dbc.Accordion([
               dbc.AccordionItem([
                   html.H5("안전재고 설정", className="mb-3"),
                   dbc.Form([
                       dbc.Row([
                           dbc.Col([
                               dbc.Label("기본 안전재고 비율 (%)"),
                               dbc.Input(
                                   id="safety-stock-ratio",
                                   type="number",
                                   value="20",
                                   min="0",
                                   max="100"
                               ),
                               html.Small("평균 사용량 대비 안전재고 비율을 설정합니다.", className="text-muted")
                           ], md=6),
                           dbc.Col([
                               dbc.Label("알림 기준"),
                               dbc.Select(
                                   id="alert-criteria",
                                   options=[
                                       {"label": "안전재고 미만", "value": "below"},
                                       {"label": "안전재고 50% 미만", "value": "half"},
                                       {"label": "재고 없음", "value": "zero"}
                                   ],
                                   value="below"
                               ),
                               html.Small("재고 부족 알림을 받을 기준을 선택합니다.", className="text-muted")
                           ], md=6)
                       ], className="mb-3"),
                       
                       dbc.Row([
                           dbc.Col([
                               dbc.Label("자동 발주점"),
                               dbc.Switch(
                                   id="auto-order-point",
                                   value=False,
                                   label="사용"
                               ),
                               html.Small("안전재고 도달 시 자동으로 발주 요청을 생성합니다.", className="text-muted")
                           ])
                       ])
                   ])
               ], title="안전재고"),
               
               dbc.AccordionItem([
                   html.H5("재고 평가 방법", className="mb-3"),
                   dbc.RadioItems(
                       id="valuation-method",
                       options=[
                           {"label": "선입선출법 (FIFO)", "value": "fifo"},
                           {"label": "이동평균법", "value": "moving_avg"},
                           {"label": "총평균법", "value": "total_avg"}
                       ],
                       value="moving_avg"
                   ),
                   html.Hr(),
                   html.P("선택한 평가 방법에 따라 재고 단가가 계산됩니다.", className="text-muted")
               ], title="재고 평가"),
               
               dbc.AccordionItem([
                   html.H5("바코드 설정", className="mb-3"),
                   dbc.Form([
                       dbc.Row([
                           dbc.Col([
                               dbc.Checklist(
                                   id="barcode-options",
                                   options=[
                                       {"label": "바코드 사용", "value": "use_barcode"},
                                       {"label": "QR코드 사용", "value": "use_qr"},
                                       {"label": "자동 생성", "value": "auto_generate"}
                                   ],
                                   value=["use_barcode"]
                               )
                           ])
                       ], className="mb-3"),
                       
                       dbc.Row([
                           dbc.Col([
                               dbc.Label("바코드 형식"),
                               dbc.Select(
                                   id="barcode-format",
                                   options=[
                                       {"label": "Code 128", "value": "code128"},
                                       {"label": "Code 39", "value": "code39"},
                                       {"label": "EAN-13", "value": "ean13"},
                                       {"label": "QR Code", "value": "qr"}
                                   ],
                                   value="code128"
                               )
                           ], md=6),
                           dbc.Col([
                               dbc.Label("바코드 접두사"),
                               dbc.Input(
                                   id="barcode-prefix",
                                   placeholder="예: INV-",
                                   value="INV-"
                               )
                           ], md=6)
                       ])
                   ])
               ], title="바코드/QR코드"),
               
               dbc.AccordionItem([
                   html.H5("창고 관리", className="mb-3"),
                   dbc.Form([
                       dbc.Row([
                           dbc.Col([
                               dbc.Label("창고 목록"),
                               dbc.ListGroup([
                                   dbc.ListGroupItem([
                                       dbc.Row([
                                           dbc.Col("창고1 (WH1)", width=8),
                                           dbc.Col([
                                               dbc.Button(
                                                   html.I(className="fas fa-edit"),
                                                   size="sm",
                                                   color="primary",
                                                   className="me-1"
                                               ),
                                               dbc.Button(
                                                   html.I(className="fas fa-trash"),
                                                   size="sm",
                                                   color="danger"
                                               )
                                           ], width=4, className="text-end")
                                       ])
                                   ]),
                                   dbc.ListGroupItem([
                                       dbc.Row([
                                           dbc.Col("창고2 (WH2)", width=8),
                                           dbc.Col([
                                               dbc.Button(
                                                   html.I(className="fas fa-edit"),
                                                   size="sm",
                                                   color="primary",
                                                   className="me-1"
                                               ),
                                               dbc.Button(
                                                   html.I(className="fas fa-trash"),
                                                   size="sm",
                                                   color="danger"
                                               )
                                           ], width=4, className="text-end")
                                       ])
                                   ])
                               ]),
                               dbc.Button(
                                   [html.I(className="fas fa-plus me-2"), "창고 추가"],
                                   color="success",
                                   className="mt-2",
                                   size="sm"
                               )
                           ])
                       ])
                   ])
               ], title="창고 설정")
           ]),
           
           dbc.Row([
               dbc.Col([
                   dbc.Button(
                       [html.I(className="fas fa-save me-2"), "설정 저장"],
                       id="save-inv-settings-btn",
                       color="primary",
                       className="mt-3"
                   )
               ])
           ]),
           
           # 메시지 영역
           html.Div(id="inv-settings-message", className="mt-3")
       ])
   ])

def create_item_modal():
   """품목 추가/수정 모달"""
   return dbc.Modal([
       dbc.ModalHeader(dbc.ModalTitle("품목 등록")),
       dbc.ModalBody([
           dbc.Form([
               dbc.Row([
                   dbc.Col([
                       dbc.Label("품목코드", html_for="modal-item-code"),
                       dbc.Input(
                           id="modal-item-code",
                           placeholder="예: ITEM001",
                           required=True
                       )
                   ], md=6),
                   dbc.Col([
                       dbc.Label("품목명", html_for="modal-item-name"),
                       dbc.Input(
                           id="modal-item-name",
                           placeholder="예: 볼트 M10",
                           required=True
                       )
                   ], md=6)
               ], className="mb-3"),
               
               dbc.Row([
                   dbc.Col([
                       dbc.Label("분류", html_for="modal-category"),
                       dbc.Select(
                           id="modal-category",
                           options=[
                               {"label": "원자재", "value": "material"},
                               {"label": "부품", "value": "component"},
                               {"label": "제품", "value": "product"},
                               {"label": "소모품", "value": "consumable"}
                           ],
                           required=True
                       )
                   ], md=6),
                   dbc.Col([
                       dbc.Label("단위", html_for="modal-unit"),
                       dbc.Select(
                           id="modal-unit",
                           options=[
                               {"label": "EA (개)", "value": "EA"},
                               {"label": "BOX (박스)", "value": "BOX"},
                               {"label": "KG (킬로그램)", "value": "KG"},
                               {"label": "M (미터)", "value": "M"},
                               {"label": "L (리터)", "value": "L"}
                           ],
                           value="EA",
                           required=True
                       )
                   ], md=6)
               ], className="mb-3"),
               
               dbc.Row([
                   dbc.Col([
                       dbc.Label("안전재고", html_for="modal-safety-stock"),
                       dbc.Input(
                           id="modal-safety-stock",
                           type="number",
                           min=0,
                           value=0
                       )
                   ], md=6),
                   dbc.Col([
                       dbc.Label("단가", html_for="modal-unit-price"),
                       dbc.InputGroup([
                           dbc.InputGroupText("₩"),
                           dbc.Input(
                               id="modal-unit-price",
                               type="number",
                               min=0,
                               value=0
                           )
                       ])
                   ], md=6)
               ], className="mb-3"),
               
               dbc.Row([
                   dbc.Col([
                       dbc.Label("비고"),
                       dbc.Textarea(
                           id="modal-remarks",
                           rows=2,
                           placeholder="추가 정보를 입력하세요..."
                       )
                   ])
               ])
           ]),
           
           # 메시지 영역
           html.Div(id="item-modal-message", className="mt-3")
       ]),
       dbc.ModalFooter([
           dbc.Button(
               "취소",
               id="close-item-modal",
               className="ms-auto",
               n_clicks=0
           ),
           dbc.Button(
               [html.I(className="fas fa-save me-2"), "저장"],
               id="save-item-btn",
               color="primary",
               n_clicks=0
           )
       ])
   ], id="item-modal", is_open=False, size="lg")
