# File: modules/quality/layouts.py
# 품질관리 모듈 레이아웃 - V1.1 신규

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_quality_layout():
    """품질관리 모듈 메인 레이아웃"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-clipboard-check me-2"), "품질관리 시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="검사 관리", tab_id="inspection"),
            dbc.Tab(label="불량 관리", tab_id="defect"),
            dbc.Tab(label="SPC", tab_id="spc"),
            dbc.Tab(label="성적서", tab_id="certificate"),
            dbc.Tab(label="분석", tab_id="quality-analysis"),
            dbc.Tab(label="설정", tab_id="quality-settings")
        ], id="quality-tabs", active_tab="inspection"),
        
        html.Div(id="quality-tab-content", className="mt-4"),
        
        # 모달들
        create_inspection_modal(),
        create_defect_modal(),
        create_certificate_modal(),
        
        # 다운로드 컴포넌트
        dcc.Download(id="download-quality-data")
    ], fluid=True, className="py-4")

def create_inspection_management():
    """검사 관리 화면"""
    return html.Div([
       # 검사 현황 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-clipboard-list fa-2x text-primary mb-2"),
                        ], className="text-center"),
                        html.H6("오늘 검사", className="text-muted text-center"),
                        html.H3("0", id="quality-today-inspections", className="text-center"),  # ID 변경
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
                        html.H6("합격률", className="text-muted text-center"),
                        html.H3("0%", id="quality-pass-rate", className="text-center"),  # ID 변경
                        html.P("이번 주", className="text-muted mb-0 text-center")
                    ])
                ], color="success", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-exclamation-triangle fa-2x text-warning mb-2"),
                        ], className="text-center"),
                        html.H6("불량률", className="text-muted text-center"),
                        html.H3("0%", id="quality-defect-rate", className="text-center text-warning"),  # ID 변경
                        html.P("이번 주", className="text-muted mb-0 text-center")
                    ])
                ], color="warning", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-tools fa-2x text-info mb-2"),
                        ], className="text-center"),
                        html.H6("교정 예정", className="text-muted text-center"),
                        html.H3("0", id="quality-calibration-due", className="text-center"),  # ID 변경
                        html.P("장비", className="text-muted mb-0 text-center")
                    ])
                ], color="info", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 검사 유형 선택
        dbc.Card([
            dbc.CardHeader([
                html.H4("검사 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "검사 등록"],
                        id="new-inspection-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-cog me-2"), "검사 기준"],
                        id="inspection-standard-btn",
                        color="secondary",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 검사 유형 탭
                dbc.Tabs([
                    dbc.Tab(label="입고 검사", tab_id="incoming"),
                    dbc.Tab(label="공정 검사", tab_id="process"),
                    dbc.Tab(label="출하 검사", tab_id="final")
                ], id="inspection-type-tabs", active_tab="incoming", className="mb-3"),
                
                # 검사 리스트
                html.Div(id="inspection-list")
            ])
        ]),
        
        # 검사 현황 차트
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("일별 검사 현황"),
                    dbc.CardBody([
                        dcc.Graph(id="daily-inspection-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("검사 유형별 합격률"),
                    dbc.CardBody([
                        dcc.Graph(id="inspection-pass-rate-chart")
                    ])
                ])
            ], md=6)
        ], className="mt-4")
    ])

def create_defect_management():
    """불량 관리 화면"""
    return html.Div([
        # 불량 현황 요약
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("이번 달 불량"),
                    dbc.CardBody([
                        html.H3("0", id="quality-monthly-defects", className="text-danger"),  # ID 변경
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("중대 불량"),
                    dbc.CardBody([
                        html.H3("0", id="quality-critical-defects", className="text-danger"),  # ID 변경
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("처리 중"),
                    dbc.CardBody([
                        html.H3("0", id="quality-open-defects", className="text-warning"),  # ID 변경
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("완료"),
                    dbc.CardBody([
                        html.H3("0", id="quality-closed-defects", className="text-success"),  # ID 변경
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 불량 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("불량 이력 관리"),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "불량 등록"],
                    id="new-defect-btn",
                    color="danger",
                    size="sm",
                    className="float-end"
                )
            ]),
            dbc.CardBody([
                # 검색 필터
                dbc.Row([
                    dbc.Col([
                        dbc.Label("기간"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="defect-start-date",
                                type="date",
                                value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="defect-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("불량 유형"),
                        dbc.Select(
                            id="defect-type-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "외관", "value": "appearance"},
                                {"label": "치수", "value": "dimension"},
                                {"label": "기능", "value": "function"},
                                {"label": "재료", "value": "material"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("상태"),
                        dbc.Select(
                            id="defect-status-filter",
                            options=[
                                {"label": "전체", "value": "all"},
                                {"label": "처리중", "value": "open"},
                                {"label": "진행중", "value": "in_progress"},
                                {"label": "완료", "value": "closed"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-defects-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 불량 리스트
                html.Div(id="defect-list-table")
            ])
        ]),
        
        # 불량 분석 차트
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("불량 유형별 파레토 차트"),
                    dbc.CardBody([
                        dcc.Graph(id="defect-pareto-chart")
                    ])
                ])
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("불량 원인 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="defect-cause-chart")
                    ])
                ])
            ], md=4)
        ], className="mt-4")
    ])

def create_spc_dashboard():
    """SPC (통계적 공정 관리) 대시보드"""
    return html.Div([
        # SPC 설정
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("공정 선택"),
                        dbc.Select(
                            id="spc-process-select",
                            options=[
                                {"label": "가공 공정", "value": "machining"},
                                {"label": "조립 공정", "value": "assembly"},
                                {"label": "검사 공정", "value": "inspection"}
                            ],
                            value="machining"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("품목"),
                        dbc.Select(
                            id="spc-item-select",
                            options=[],
                            placeholder="품목 선택..."
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("측정 특성"),
                        dbc.Select(
                            id="spc-characteristic-select",
                            options=[
                                {"label": "길이", "value": "length"},
                                {"label": "폭", "value": "width"},
                                {"label": "두께", "value": "thickness"},
                                {"label": "경도", "value": "hardness"}
                            ],
                            value="length"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("기간"),
                        dbc.Select(
                            id="spc-period-select",
                            options=[
                                {"label": "오늘", "value": "today"},
                                {"label": "이번 주", "value": "week"},
                                {"label": "이번 달", "value": "month"}
                            ],
                            value="week"
                        )
                    ], md=3)
                ])
            ])
        ], className="mb-4"),
        
        # SPC 차트
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("X-bar 관리도"),
                        dbc.Badge("UCL: 10.5 | CL: 10.0 | LCL: 9.5", color="info", className="ms-2")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="xbar-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("R 관리도"),
                        dbc.Badge("UCL: 0.5 | CL: 0.25 | LCL: 0", color="info", className="ms-2")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="r-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 공정 능력 지수
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("공정 능력 분석"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Cp", className="text-muted"),
                                html.H3("1.33", id="cp-value", className="text-success"),
                                html.P("공정능력지수", className="text-muted small")
                            ], md=3),
                            dbc.Col([
                                html.H6("Cpk", className="text-muted"),
                                html.H3("1.25", id="cpk-value", className="text-success"),
                                html.P("공정능력지수(편향)", className="text-muted small")
                            ], md=3),
                            dbc.Col([
                                html.H6("Pp", className="text-muted"),
                                html.H3("1.28", id="pp-value", className="text-warning"),
                                html.P("공정성능지수", className="text-muted small")
                            ], md=3),
                            dbc.Col([
                                html.H6("Ppk", className="text-muted"),
                                html.H3("1.22", id="ppk-value", className="text-warning"),
                                html.P("공정성능지수(편향)", className="text-muted small")
                            ], md=3)
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("정규성 검정"),
                    dbc.CardBody([
                        dcc.Graph(id="normality-test-chart")
                    ])
                ])
            ], md=6)
        ])
    ])

def create_certificate_management():
    """성적서 관리 화면"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4([html.I(className="fas fa-certificate me-2"), "품질 성적서 관리"]),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "성적서 발행"],
                        id="new-certificate-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-file-pdf me-2"), "PDF 출력"],
                        id="print-certificate-btn",
                        color="danger",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 검색 필터
                dbc.Row([
                    dbc.Col([
                        dbc.Label("발행일자"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="cert-start-date",
                                type="date",
                                value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="cert-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("고객"),
                        dbc.Select(
                            id="cert-customer-filter",
                            options=[{"label": "전체", "value": "all"}],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("제품"),
                        dbc.Select(
                            id="cert-product-filter",
                            options=[{"label": "전체", "value": "all"}],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-certificates-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 성적서 리스트
                html.Div(id="certificate-list-table")
            ])
        ])
    ])

def create_quality_analysis():
    """품질 분석 화면"""
    return html.Div([
        # 분석 기간 설정
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("분석 기간"),
                        dbc.RadioItems(
                            id="quality-analysis-period",
                            options=[
                                {"label": "일별", "value": "daily"},
                                {"label": "주별", "value": "weekly"},
                                {"label": "월별", "value": "monthly"},
                                {"label": "연간", "value": "yearly"}
                            ],
                            value="monthly",
                            inline=True
                        )
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # 품질 지표
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("품질 트렌드"),
                    dbc.CardBody([
                        dcc.Graph(id="quality-trend-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("품질 비용 분석"),
                    dbc.CardBody([
                        dcc.Graph(id="quality-cost-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 공급업체별 품질
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("공급업체별 품질 현황"),
                    dbc.CardBody([
                        dcc.Graph(id="supplier-quality-chart")
                    ])
                ])
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("품질 KPI"),
                    dbc.CardBody([
                        html.Div([
                            dbc.ListGroup([
                                dbc.ListGroupItem([
                                    html.Div([
                                        html.H6("목표 불량률", className="mb-0"),
                                        html.Small("2.0%", className="text-muted")
                                    ], className="d-flex justify-content-between")
                                ]),
                                dbc.ListGroupItem([
                                    html.Div([
                                        html.H6("실제 불량률", className="mb-0"),
                                        html.Small("1.8%", className="text-success")
                                    ], className="d-flex justify-content-between")
                                ]),
                                dbc.ListGroupItem([
                                    html.Div([
                                        html.H6("고객 클레임", className="mb-0"),
                                        html.Small("0건", className="text-success")
                                    ], className="d-flex justify-content-between")
                                ]),
                                dbc.ListGroupItem([
                                    html.Div([
                                        html.H6("공정 능력 지수", className="mb-0"),
                                        html.Small("1.33", className="text-info")
                                    ], className="d-flex justify-content-between")
                                ])
                            ])
                        ])
                    ])
                ])
            ], md=4)
        ])
    ])

def create_quality_settings():
    """품질관리 설정"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-cog me-2"), "품질관리 설정"])
        ]),
        dbc.CardBody([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5("검사 기준 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("기본 샘플링 비율 (%)"),
                                dbc.Input(
                                    id="default-sampling-rate",
                                    type="number",
                                    value="10",
                                    min="1",
                                    max="100"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("재검사 기준"),
                                dbc.Select(
                                    id="reinspection-criteria",
                                    options=[
                                        {"label": "불량률 5% 초과", "value": "5"},
                                        {"label": "불량률 3% 초과", "value": "3"},
                                        {"label": "중대 불량 발생시", "value": "critical"}
                                    ],
                                    value="5"
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("검사 결과 자동 승인"),
                                dbc.Switch(
                                    id="auto-approval-switch",
                                    value=False,
                                    label="사용"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("불량 자동 알림"),
                                dbc.Switch(
                                    id="defect-notification-switch",
                                    value=True,
                                    label="사용"
                                )
                            ], md=6)
                        ])
                    ])
                ], title="검사 설정"),
                
                dbc.AccordionItem([
                    html.H5("SPC 관리 기준", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("관리도 규칙"),
                                dbc.Checklist(
                                    id="spc-rules",
                                    options=[
                                        {"label": "1점이 관리한계 벗어남", "value": "rule1"},
                                        {"label": "연속 7점이 중심선 한쪽", "value": "rule2"},
                                        {"label": "연속 6점이 증가/감소", "value": "rule3"},
                                        {"label": "연속 14점이 교대로 상하", "value": "rule4"}
                                    ],
                                    value=["rule1", "rule2"]
                                )
                            ])
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("목표 Cpk"),
                                dbc.Input(
                                    id="target-cpk",
                                    type="number",
                                    value="1.33",
                                    step="0.01"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("최소 샘플 수"),
                                dbc.Input(
                                    id="min-sample-size",
                                    type="number",
                                    value="25"
                                )
                            ], md=6)
                        ])
                    ])
                ], title="SPC 설정"),
                
                dbc.AccordionItem([
                    html.H5("성적서 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("성적서 템플릿"),
                                dbc.Select(
                                    id="certificate-template",
                                    options=[
                                        {"label": "표준 템플릿", "value": "standard"},
                                        {"label": "상세 템플릿", "value": "detailed"},
                                        {"label": "고객사 양식", "value": "custom"}
                                    ],
                                    value="standard"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("자동 번호 생성"),
                                dbc.Switch(
                                    id="auto-cert-number",
                                    value=True,
                                    label="사용"
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("전자 서명"),
                                dbc.Switch(
                                    id="digital-signature",
                                    value=False,
                                    label="사용"
                                )
                            ])
                        ])
                    ])
                ], title="성적서 설정")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "설정 저장"],
                        id="save-quality-settings-btn",
                        color="primary",
                        className="mt-3"
                    )
                ])
            ]),
            
            html.Div(id="quality-settings-message", className="mt-3")
        ])
    ])

def create_inspection_modal():
    """검사 등록 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("검사 등록")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("검사 유형"),
                        dbc.Select(
                            id="modal-inspection-type",
                            options=[
                                {"label": "입고 검사", "value": "incoming"},
                                {"label": "공정 검사", "value": "process"},
                                {"label": "출하 검사", "value": "final"}
                            ],
                            value="incoming"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("검사일자"),
                        dbc.Input(
                            id="modal-inspection-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("품목"),
                        dbc.Select(
                            id="modal-inspection-item",
                            options=[],
                            placeholder="품목 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("LOT 번호"),
                        dbc.Input(
                            id="modal-lot-number",
                            placeholder="LOT 번호 입력"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("수량"),
                        dbc.Input(
                            id="modal-inspection-qty",
                            type="number",
                            placeholder="검사 수량"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("샘플 수"),
                        dbc.Input(
                            id="modal-sample-qty",
                            type="number",
                            placeholder="샘플 수"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("합격 수"),
                        dbc.Input(
                            id="modal-pass-qty",
                            type="number",
                            placeholder="합격 수량"
                        )
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("검사 결과"),
                        dbc.Select(
                            id="modal-inspection-result",
                            options=[
                                {"label": "합격", "value": "pass"},
                                {"label": "불합격", "value": "fail"},
                                {"label": "조건부 합격", "value": "conditional"}
                            ],
                            value="pass"
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("비고"),
                        dbc.Textarea(
                            id="modal-inspection-remarks",
                            rows=3
                        )
                    ])
                ])
            ]),
            
            html.Div(id="inspection-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-inspection-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-inspection-btn",
                color="primary"
            )
        ])
    ], id="inspection-modal", size="lg", is_open=False)

def create_defect_modal():
    """불량 등록 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("불량 등록")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("불량 발생일"),
                        dbc.Input(
                            id="modal-defect-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("검사 번호"),
                        dbc.Input(
                            id="modal-defect-inspection-no",
                            placeholder="관련 검사 번호"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("품목"),
                        dbc.Select(
                            id="modal-defect-item",
                            options=[],
                            placeholder="품목 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("불량 유형"),
                        dbc.Select(
                            id="modal-defect-type",
                            options=[],
                            placeholder="불량 유형 선택..."
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("불량 수량"),
                        dbc.Input(
                            id="modal-defect-qty",
                            type="number",
                            placeholder="불량 수량"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("심각도"),
                        dbc.Select(
                            id="modal-defect-severity",
                            options=[
                                {"label": "Critical", "value": "1"},
                                {"label": "Major", "value": "2"},
                                {"label": "Minor", "value": "3"}
                            ],
                            value="3"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("원인 분석"),
                        dbc.Textarea(
                            id="modal-cause-analysis",
                            rows=3,
                            placeholder="불량 원인을 상세히 기술하세요..."
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("개선 조치"),
                        dbc.Textarea(
                            id="modal-corrective-action",
                            rows=3,
                            placeholder="개선 조치 사항을 기술하세요..."
                        )
                    ])
                ])
            ]),
            
            html.Div(id="defect-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-defect-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-defect-btn",
                color="primary"
            )
        ])
    ], id="defect-modal", size="lg", is_open=False)

def create_certificate_modal():
    """성적서 발행 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("품질 성적서 발행")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("성적서 번호"),
                        dbc.Input(
                            id="modal-certificate-no",
                            value=f"QC-{datetime.now().strftime('%Y%m%d')}-",
                            disabled=True
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("발행일자"),
                        dbc.Input(
                            id="modal-certificate-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("고객"),
                        dbc.Select(
                            id="modal-certificate-customer",
                            options=[],
                            placeholder="고객 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("수주번호"),
                        dbc.Select(
                            id="modal-certificate-order",
                            options=[],
                            placeholder="수주번호 선택..."
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("제품"),
                        dbc.Select(
                            id="modal-certificate-product",
                            options=[],
                            placeholder="제품 선택..."
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("LOT 번호"),
                        dbc.Input(
                            id="modal-certificate-lot",
                            placeholder="LOT 번호"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                html.Hr(),
                html.H6("검사 항목"),
                
                # 검사 항목 테이블
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("검사 항목"),
                            html.Th("규격"),
                            html.Th("측정값"),
                            html.Th("판정")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td("외관"),
                            html.Td("이상 없음"),
                            html.Td("양호"),
                            html.Td(dbc.Badge("합격", color="success"))
                        ]),
                        html.Tr([
                            html.Td("치수"),
                            html.Td("10.0±0.1"),
                            html.Td("10.02"),
                            html.Td(dbc.Badge("합격", color="success"))
                        ])
                    ])
                ], bordered=True, striped=True, size="sm"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("종합 판정"),
                        dbc.Select(
                            id="modal-certificate-result",
                            options=[
                                {"label": "합격", "value": "pass"},
                                {"label": "불합격", "value": "fail"}
                            ],
                            value="pass"
                        )
                    ])
                ])
            ]),
            
            html.Div(id="certificate-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-certificate-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-certificate-btn",
                color="primary"
            )
        ])
    ], id="certificate-modal", size="xl", is_open=False)
