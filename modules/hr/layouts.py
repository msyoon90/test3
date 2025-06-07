# modules/hr/layouts.py - 인사관리 모듈 레이아웃

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_hr_layout():
    """인사관리 모듈 메인 레이아웃"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-users me-2"), "인사관리 시스템"]),
                html.Hr()
            ])
        ]),
        
        # 탭 메뉴
        dbc.Tabs([
            dbc.Tab(label="대시보드", tab_id="hr-dashboard"),
            dbc.Tab(label="직원 관리", tab_id="employee-management"),
            dbc.Tab(label="근태 관리", tab_id="attendance-management"),
            dbc.Tab(label="급여 관리", tab_id="payroll-management"),
            dbc.Tab(label="휴가 관리", tab_id="leave-management"),
            dbc.Tab(label="조직도", tab_id="organization-chart"),
            dbc.Tab(label="인사 평가", tab_id="performance-evaluation"),
            dbc.Tab(label="교육 훈련", tab_id="training-management"),
            dbc.Tab(label="설정", tab_id="hr-settings")
        ], id="hr-tabs", active_tab="hr-dashboard"),
        
        html.Div(id="hr-tab-content", className="mt-4"),
        
        # 모달들
        create_employee_modal(),
        create_attendance_modal(),
        create_leave_modal(),
        create_payroll_modal(),
        
        # 다운로드 컴포넌트
        dcc.Download(id="download-hr-data")
    ], fluid=True, className="py-4")

def create_hr_dashboard():
    """인사 대시보드"""
    return html.Div([
        # 핵심 지표
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-users fa-2x text-primary mb-2"),
                        ], className="text-center"),
                        html.H6("총 직원수", className="text-muted text-center"),
                        html.H3("0", id="total-employees", className="text-center"),
                        html.P("명", className="text-muted mb-0 text-center")
                    ])
                ], color="primary", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-user-check fa-2x text-success mb-2"),
                        ], className="text-center"),
                        html.H6("출근 인원", className="text-muted text-center"),
                        html.H3("0", id="present-employees", className="text-center"),
                        html.P("명", className="text-muted mb-0 text-center")
                    ])
                ], color="success", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-plane fa-2x text-info mb-2"),
                        ], className="text-center"),
                        html.H6("휴가 중", className="text-muted text-center"),
                        html.H3("0", id="on-leave-employees", className="text-center"),
                        html.P("명", className="text-muted mb-0 text-center")
                    ])
                ], color="info", outline=True)
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-briefcase fa-2x text-warning mb-2"),
                        ], className="text-center"),
                        html.H6("신규 입사", className="text-muted text-center"),
                        html.H3("0", id="new-employees", className="text-center"),
                        html.P("명 (이번달)", className="text-muted mb-0 text-center")
                    ])
                ], color="warning", outline=True)
            ], md=3)
        ], className="mb-4"),
        
        # 차트 영역
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("부서별 인원 현황"),
                    dbc.CardBody([
                        dcc.Graph(id="dept-employee-chart")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("월별 근태 현황"),
                    dbc.CardBody([
                        dcc.Graph(id="monthly-attendance-chart")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # 최근 활동
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("오늘의 일정"),
                        dbc.Badge("3", color="primary", className="ms-2")
                    ]),
                    dbc.CardBody([
                        html.Div(id="today-hr-schedule")
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("인사 알림"),
                        dbc.Badge("5", color="danger", className="ms-2")
                    ]),
                    dbc.CardBody([
                        html.Div(id="hr-notifications")
                    ])
                ])
            ], md=6)
        ])
    ])

def create_employee_management():
    """직원 관리"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4("직원 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-user-plus me-2"), "신규 등록"],
                        id="new-employee-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-file-excel me-2"), "Excel 업로드"],
                        id="upload-employees-btn",
                        color="success",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "내보내기"],
                        id="export-employees-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 검색 필터
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(
                                id="search-employee",
                                placeholder="이름, 사번으로 검색..."
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Select(
                            id="filter-department",
                            options=[
                                {"label": "전체 부서", "value": "all"},
                                {"label": "경영지원부", "value": "management"},
                                {"label": "생산부", "value": "production"},
                                {"label": "품질관리부", "value": "quality"},
                                {"label": "영업부", "value": "sales"},
                                {"label": "연구개발부", "value": "rnd"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Select(
                            id="filter-status",
                            options=[
                                {"label": "재직중", "value": "active"},
                                {"label": "휴직중", "value": "leave"},
                                {"label": "퇴직", "value": "resigned"},
                                {"label": "전체", "value": "all"}
                            ],
                            value="active"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-sync me-2"), "새로고침"],
                            id="refresh-employees-btn",
                            color="secondary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 직원 목록 테이블
                html.Div(id="employee-list-table")
            ])
        ])
    ])

def create_attendance_management():
    """근태 관리"""
    return html.Div([
        # 오늘의 근태 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("정상 출근", className="text-muted"),
                        html.H3("0", id="normal-attendance", className="text-success"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("지각", className="text-muted"),
                        html.H3("0", id="late-attendance", className="text-warning"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("조퇴", className="text-muted"),
                        html.H3("0", id="early-leave", className="text-info"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("결근", className="text-muted"),
                        html.H3("0", id="absent", className="text-danger"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("휴가", className="text-muted"),
                        html.H3("0", id="on-vacation", className="text-primary"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("출장", className="text-muted"),
                        html.H3("0", id="business-trip", className="text-secondary"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=2)
        ], className="mb-4"),
        
        # 근태 입력/조회
        dbc.Card([
            dbc.CardHeader([
                html.H4("근태 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-clock me-2"), "출퇴근 기록"],
                        id="attendance-record-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-calendar-check me-2"), "일괄 처리"],
                        id="batch-attendance-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 조회 조건
                dbc.Row([
                    dbc.Col([
                        dbc.Label("기간"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="attendance-start-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            ),
                            dbc.InputGroupText("~"),
                            dbc.Input(
                                id="attendance-end-date",
                                type="date",
                                value=datetime.now().strftime('%Y-%m-%d')
                            )
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Label("부서"),
                        dbc.Select(
                            id="attendance-dept-filter",
                            options=[
                                {"label": "전체", "value": "all"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("직원"),
                        dbc.Input(
                            id="attendance-employee-search",
                            placeholder="이름 또는 사번"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "조회"],
                            id="search-attendance-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=2)
                ], className="mb-3"),
                
                # 근태 현황 테이블
                html.Div(id="attendance-table")
            ])
        ])
    ])

def create_payroll_management():
    """급여 관리"""
    return html.Div([
        # 급여 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("이번달 급여 총액"),
                    dbc.CardBody([
                        html.H3("₩0", id="total-payroll", className="text-primary"),
                        html.P("전월 대비: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("평균 급여"),
                    dbc.CardBody([
                        html.H3("₩0", id="average-salary", className="text-info"),
                        html.P("정규직 기준", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("4대보험료"),
                    dbc.CardBody([
                        html.H3("₩0", id="insurance-total", className="text-warning"),
                        html.P("회사 부담금", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("소득세"),
                    dbc.CardBody([
                        html.H3("₩0", id="income-tax-total", className="text-danger"),
                        html.P("원천징수 총액", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 급여 계산/명세서
        dbc.Card([
            dbc.CardHeader([
                html.H4("급여 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-calculator me-2"), "급여 계산"],
                        id="calculate-payroll-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-file-invoice-dollar me-2"), "명세서 발행"],
                        id="issue-payslip-btn",
                        color="success",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-bank me-2"), "이체 파일"],
                        id="bank-transfer-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 급여 계산 기준
                dbc.Row([
                    dbc.Col([
                        dbc.Label("급여 년월"),
                        dbc.InputGroup([
                            dbc.Select(
                                id="payroll-year",
                                options=[
                                    {"label": "2024년", "value": "2024"},
                                    {"label": "2025년", "value": "2025"}
                                ],
                                value="2025"
                            ),
                            dbc.Select(
                                id="payroll-month",
                                options=[
                                    {"label": f"{i}월", "value": str(i)}
                                    for i in range(1, 13)
                                ],
                                value=str(datetime.now().month)
                            )
                        ])
                    ], md=3),
                    dbc.Col([
                        dbc.Label("급여일"),
                        dbc.Input(
                            id="payroll-date",
                            type="date",
                            value=datetime.now().replace(day=25).strftime('%Y-%m-%d')
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("대상"),
                        dbc.Select(
                            id="payroll-target",
                            options=[
                                {"label": "전체 직원", "value": "all"},
                                {"label": "정규직", "value": "regular"},
                                {"label": "계약직", "value": "contract"},
                                {"label": "일용직", "value": "daily"}
                            ],
                            value="all"
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("　"),
                        dbc.Button(
                            [html.I(className="fas fa-play me-2"), "실행"],
                            id="run-payroll-btn",
                            color="primary",
                            className="w-100"
                        )
                    ], md=3)
                ], className="mb-3"),
                
                # 급여 명세 리스트
                html.Div(id="payroll-list")
            ])
        ])
    ])

def create_leave_management():
    """휴가 관리"""
    return html.Div([
        # 휴가 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("휴가 신청", className="text-muted"),
                        html.H3("0", id="leave-requests", className="text-warning"),
                        html.P("건 (승인 대기)", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("오늘 휴가자", className="text-muted"),
                        html.H3("0", id="today-leaves", className="text-info"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("연차 소진율", className="text-muted"),
                        html.H3("0%", id="leave-usage-rate", className="text-primary"),
                        html.P("전사 평균", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("미사용 연차", className="text-muted"),
                        html.H3("0", id="unused-leaves", className="text-danger"),
                        html.P("일 (전사 합계)", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 휴가 신청/승인
        dbc.Card([
            dbc.CardHeader([
                html.H4("휴가 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-calendar-plus me-2"), "휴가 신청"],
                        id="new-leave-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-check-double me-2"), "일괄 승인"],
                        id="batch-approve-leave-btn",
                        color="success",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                dbc.Tabs([
                    dbc.Tab(label="휴가 신청 목록", tab_id="leave-requests-tab"),
                    dbc.Tab(label="휴가 현황", tab_id="leave-status-tab"),
                    dbc.Tab(label="연차 관리", tab_id="annual-leave-tab")
                ], id="leave-tabs", active_tab="leave-requests-tab"),
                
                html.Div(id="leave-content", className="mt-3")
            ])
        ])
    ])

def create_organization_chart():
    """조직도"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4("조직도"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-print me-2"), "인쇄"],
                        id="print-org-chart-btn",
                        color="secondary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "다운로드"],
                        id="download-org-chart-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                # 조직도 뷰 옵션
                dbc.Row([
                    dbc.Col([
                        dbc.RadioItems(
                            id="org-chart-view",
                            options=[
                                {"label": "계층도", "value": "hierarchy"},
                                {"label": "부서별", "value": "department"},
                                {"label": "직급별", "value": "position"}
                            ],
                            value="hierarchy",
                            inline=True
                        )
                    ], className="mb-3")
                ]),
                
                # 조직도 표시 영역
                html.Div(id="organization-chart-display")
            ])
        ])
    ])

def create_performance_evaluation():
    """인사 평가"""
    return html.Div([
        # 평가 진행 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("평가 대상자", className="text-muted"),
                        html.H3("0", id="evaluation-targets", className="text-primary"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("평가 완료", className="text-muted"),
                        html.H3("0", id="evaluation-completed", className="text-success"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("진행률", className="text-muted"),
                        html.H3("0%", id="evaluation-progress", className="text-info"),
                        dbc.Progress(value=0, id="evaluation-progress-bar", className="mt-2")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("평균 점수", className="text-muted"),
                        html.H3("0", id="average-score", className="text-warning"),
                        html.P("점 / 100점", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 평가 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("인사 평가"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "평가 생성"],
                        id="new-evaluation-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-chart-bar me-2"), "결과 분석"],
                        id="analyze-evaluation-btn",
                        color="info",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                html.Div(id="evaluation-content")
            ])
        ])
    ])

def create_training_management():
    """교육 훈련"""
    return html.Div([
        # 교육 현황
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("이번달 교육 일정"),
                    dbc.CardBody([
                        html.H3("0", id="monthly-training-count", className="text-primary"),
                        html.P("건", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("교육 이수율"),
                    dbc.CardBody([
                        html.H3("0%", id="training-completion-rate", className="text-success"),
                        html.P("필수 교육 기준", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("교육 예산"),
                    dbc.CardBody([
                        html.H3("₩0", id="training-budget", className="text-info"),
                        html.P("집행률: 0%", className="text-muted mb-0")
                    ])
                ])
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("미이수자"),
                    dbc.CardBody([
                        html.H3("0", id="training-incomplete", className="text-danger"),
                        html.P("명", className="text-muted mb-0")
                    ])
                ])
            ], md=3)
        ], className="mb-4"),
        
        # 교육 프로그램 관리
        dbc.Card([
            dbc.CardHeader([
                html.H4("교육 훈련 관리"),
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-graduation-cap me-2"), "교육 등록"],
                        id="new-training-btn",
                        color="primary",
                        size="sm"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-users me-2"), "수강 신청"],
                        id="training-enrollment-btn",
                        color="success",
                        size="sm"
                    )
                ], className="float-end")
            ]),
            dbc.CardBody([
                html.Div(id="training-list")
            ])
        ])
    ])

def create_hr_settings():
    """인사 설정"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([html.I(className="fas fa-cog me-2"), "인사 설정"])
        ]),
        dbc.CardBody([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.H5("근무 시간 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("기본 출근 시간"),
                                dbc.Input(
                                    id="work-start-time",
                                    type="time",
                                    value="09:00"
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("기본 퇴근 시간"),
                                dbc.Input(
                                    id="work-end-time",
                                    type="time",
                                    value="18:00"
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("점심 시간"),
                                dbc.Input(
                                    id="lunch-duration",
                                    type="number",
                                    value=60,
                                    min=30,
                                    max=120
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("주간 근무일"),
                                dbc.Input(
                                    id="work-days",
                                    type="number",
                                    value=5,
                                    min=4,
                                    max=6
                                )
                            ], md=3)
                        ])
                    ])
                ], title="근무 시간"),
                
                dbc.AccordionItem([
                    html.H5("급여 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("급여일"),
                                dbc.Select(
                                    id="pay-day",
                                    options=[
                                        {"label": f"{i}일", "value": str(i)}
                                        for i in range(1, 32)
                                    ],
                                    value="25"
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("소득세율"),
                                dbc.Input(
                                    id="income-tax-rate",
                                    type="number",
                                    value=3.3,
                                    min=0,
                                    max=100,
                                    step=0.1
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("주휴수당"),
                                dbc.Switch(
                                    id="weekly-holiday-pay",
                                    value=True,
                                    label="지급"
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("상여금 지급"),
                                dbc.Select(
                                    id="bonus-frequency",
                                    options=[
                                        {"label": "없음", "value": "none"},
                                        {"label": "분기별", "value": "quarterly"},
                                        {"label": "반기별", "value": "semi-annual"},
                                        {"label": "연 1회", "value": "annual"}
                                    ],
                                    value="quarterly"
                                )
                            ], md=3)
                        ], className="mb-3"),
                        
                        html.H6("4대보험 요율", className="mt-3 mb-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("건강보험"),
                                dbc.Input(
                                    id="health-insurance-rate",
                                    type="number",
                                    value=3.43,
                                    step=0.01
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("국민연금"),
                                dbc.Input(
                                    id="pension-rate",
                                    type="number",
                                    value=4.5,
                                    step=0.01
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("고용보험"),
                                dbc.Input(
                                    id="employment-insurance-rate",
                                    type="number",
                                    value=0.8,
                                    step=0.01
                                )
                            ], md=3),
                            dbc.Col([
                                dbc.Label("산재보험"),
                                dbc.Input(
                                    id="accident-insurance-rate",
                                    type="number",
                                    value=0.7,
                                    step=0.01
                                )
                            ], md=3)
                        ])
                    ])
                ], title="급여"),
                
                dbc.AccordionItem([
                    html.H5("휴가 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("연차 기본 일수"),
                                dbc.Input(
                                    id="annual-leave-days",
                                    type="number",
                                    value=15,
                                    min=11,
                                    max=25
                                )
                            ], md=4),
                            dbc.Col([
                                dbc.Label("병가 일수"),
                                dbc.Input(
                                    id="sick-leave-days",
                                    type="number",
                                    value=10,
                                    min=0,
                                    max=30
                                )
                            ], md=4),
                            dbc.Col([
                                dbc.Label("경조사 휴가"),
                                dbc.Input(
                                    id="special-leave-days",
                                    type="number",
                                    value=5,
                                    min=0,
                                    max=10
                                )
                            ], md=4)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("연차 촉진 시작"),
                                dbc.Select(
                                    id="leave-promotion-start",
                                    options=[
                                        {"label": f"{i}월", "value": str(i)}
                                        for i in range(1, 13)
                                    ],
                                    value="10"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("미사용 연차 처리"),
                                dbc.RadioItems(
                                    id="unused-leave-policy",
                                    options=[
                                        {"label": "수당 지급", "value": "compensate"},
                                        {"label": "이월", "value": "carryover"},
                                        {"label": "소멸", "value": "expire"}
                                    ],
                                    value="compensate"
                                )
                            ], md=6)
                        ])
                    ])
                ], title="휴가"),
                
                dbc.AccordionItem([
                    html.H5("평가 설정", className="mb-3"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("평가 주기"),
                                dbc.Select(
                                    id="evaluation-frequency",
                                    options=[
                                        {"label": "연 1회", "value": "annual"},
                                        {"label": "반기별", "value": "semi-annual"},
                                        {"label": "분기별", "value": "quarterly"}
                                    ],
                                    value="annual"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("평가 방식"),
                                dbc.Checklist(
                                    id="evaluation-methods",
                                    options=[
                                        {"label": "상사 평가", "value": "supervisor"},
                                        {"label": "동료 평가", "value": "peer"},
                                        {"label": "본인 평가", "value": "self"},
                                        {"label": "부하 평가", "value": "subordinate"}
                                    ],
                                    value=["supervisor", "self"]
                                )
                            ], md=6)
                        ])
                    ])
                ], title="인사 평가")
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-save me-2"), "설정 저장"],
                        id="save-hr-settings-btn",
                        color="primary",
                        className="mt-3"
                    )
                ])
            ]),
            
            html.Div(id="hr-settings-message", className="mt-3")
        ])
    ])

# 모달 생성 함수들

def create_employee_modal():
    """직원 등록/수정 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("직원 정보")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        html.H5("기본 정보", className="mb-3")
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("사번"),
                        dbc.Input(id="employee-id", disabled=True)
                    ], md=4),
                    dbc.Col([
                        dbc.Label("이름 *"),
                        dbc.Input(id="employee-name", required=True)
                    ], md=4),
                    dbc.Col([
                        dbc.Label("영문명"),
                        dbc.Input(id="employee-name-en")
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("주민번호 *"),
                        dbc.InputGroup([
                            dbc.Input(id="resident-no-1", maxLength=6),
                            dbc.InputGroupText("-"),
                            dbc.Input(id="resident-no-2", maxLength=7, type="password")
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Label("성별"),
                        dbc.RadioItems(
                            id="employee-gender",
                            options=[
                                {"label": "남", "value": "M"},
                                {"label": "여", "value": "F"}
                            ],
                            inline=True
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("생년월일"),
                        dbc.Input(id="birth-date", type="date")
                    ], md=3)
                ], className="mb-3"),
                
                html.Hr(),
                html.H5("회사 정보", className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("부서 *"),
                        dbc.Select(
                            id="employee-department",
                            options=[
                                {"label": "경영지원부", "value": "management"},
                                {"label": "생산부", "value": "production"},
                                {"label": "품질관리부", "value": "quality"},
                                {"label": "영업부", "value": "sales"},
                                {"label": "연구개발부", "value": "rnd"}
                            ]
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("직급 *"),
                        dbc.Select(
                            id="employee-position",
                            options=[
                                {"label": "사원", "value": "staff"},
                                {"label": "주임", "value": "senior"},
                                {"label": "대리", "value": "assistant"},
                                {"label": "과장", "value": "manager"},
                                {"label": "차장", "value": "deputy"},
                                {"label": "부장", "value": "general"},
                                {"label": "이사", "value": "director"}
                            ]
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("입사일 *"),
                        dbc.Input(id="join-date", type="date")
                    ], md=4)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("고용형태"),
                        dbc.Select(
                            id="employment-type",
                            options=[
                                {"label": "정규직", "value": "regular"},
                                {"label": "계약직", "value": "contract"},
                                {"label": "파트타임", "value": "parttime"},
                                {"label": "인턴", "value": "intern"}
                            ],
                            value="regular"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("재직상태"),
                        dbc.Select(
                            id="employment-status",
                            options=[
                                {"label": "재직", "value": "active"},
                                {"label": "휴직", "value": "leave"},
                                {"label": "퇴직", "value": "resigned"}
                            ],
                            value="active"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("기본급"),
                        dbc.Input(
                            id="base-salary",
                            type="number",
                            placeholder="원"
                        )
                    ], md=4)
                ], className="mb-3"),
                
                html.Hr(),
                html.H5("연락처", className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("휴대폰 *"),
                        dbc.Input(id="mobile-phone", placeholder="010-0000-0000")
                    ], md=6),
                    dbc.Col([
                        dbc.Label("이메일"),
                        dbc.Input(id="employee-email", type="email")
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("주소"),
                        dbc.Input(id="employee-address", placeholder="주소 입력")
                    ])
                ], className="mb-3")
            ]),
            
            html.Div(id="employee-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-employee-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-employee-btn",
                color="primary"
            )
        ])
    ], id="employee-modal", size="lg", is_open=False)

def create_attendance_modal():
    """근태 입력 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("출퇴근 기록")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("날짜"),
                        dbc.Input(
                            id="attendance-date",
                            type="date",
                            value=datetime.now().strftime('%Y-%m-%d')
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("직원"),
                        dbc.Select(
                            id="attendance-employee",
                            options=[]
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("출근 시간"),
                        dbc.Input(
                            id="check-in-time",
                            type="time",
                            value="09:00"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("퇴근 시간"),
                        dbc.Input(
                            id="check-out-time",
                            type="time",
                            value="18:00"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("근태 구분"),
                        dbc.Select(
                            id="attendance-type",
                            options=[
                                {"label": "정상", "value": "normal"},
                                {"label": "지각", "value": "late"},
                                {"label": "조퇴", "value": "early"},
                                {"label": "결근", "value": "absent"},
                                {"label": "휴가", "value": "leave"},
                                {"label": "출장", "value": "business"}
                            ],
                            value="normal"
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("비고"),
                        dbc.Textarea(
                            id="attendance-remarks",
                            rows=3
                        )
                    ])
                ])
            ]),
            
            html.Div(id="attendance-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-attendance-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-save me-2"), "저장"],
                id="save-attendance-btn",
                color="primary"
            )
        ])
    ], id="attendance-modal", is_open=False)

def create_leave_modal():
    """휴가 신청 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("휴가 신청")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("신청자"),
                        dbc.Select(
                            id="leave-employee",
                            options=[]
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("휴가 종류"),
                        dbc.Select(
                            id="leave-type",
                            options=[
                                {"label": "연차", "value": "annual"},
                                {"label": "반차(오전)", "value": "half_am"},
                                {"label": "반차(오후)", "value": "half_pm"},
                                {"label": "병가", "value": "sick"},
                                {"label": "경조사", "value": "special"},
                                {"label": "공가", "value": "official"},
                                {"label": "무급휴가", "value": "unpaid"}
                            ]
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("시작일"),
                        dbc.Input(
                            id="leave-start-date",
                            type="date"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("종료일"),
                        dbc.Input(
                            id="leave-end-date",
                            type="date"
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("사용 일수"),
                        dbc.Input(
                            id="leave-days",
                            type="number",
                            value=1,
                            min=0.5,
                            step=0.5,
                            disabled=True
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("잔여 연차"),
                        dbc.Input(
                            id="remaining-leaves",
                            type="number",
                            disabled=True
                        )
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("사유"),
                        dbc.Textarea(
                            id="leave-reason",
                            rows=3,
                            placeholder="휴가 사유를 입력하세요"
                        )
                    ])
                ])
            ]),
            
            html.Div(id="leave-modal-message", className="mt-3")
        ]),
        dbc.ModalFooter([
            dbc.Button("취소", id="close-leave-modal", className="ms-auto"),
            dbc.Button(
                [html.I(className="fas fa-paper-plane me-2"), "신청"],
                id="submit-leave-btn",
                color="primary"
            )
        ])
    ], id="leave-modal", is_open=False)

def create_payroll_modal():
    """급여 명세서 모달"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("급여 명세서")),
        dbc.ModalBody([
            html.Div(id="payslip-content")
        ]),
        dbc.ModalFooter([
            dbc.Button(
                [html.I(className="fas fa-print me-2"), "인쇄"],
                id="print-payslip-btn",
                color="secondary"
            ),
            dbc.Button(
                [html.I(className="fas fa-download me-2"), "다운로드"],
                id="download-payslip-btn",
                color="info"
            ),
            dbc.Button("닫기", id="close-payroll-modal", className="ms-auto")
        ])
    ], id="payroll-modal", size="lg", is_open=False)
