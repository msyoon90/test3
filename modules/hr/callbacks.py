# modules/hr/callbacks.py - 인사관리 모듈 콜백

from dash import Input, Output, State, callback_context, ALL, MATCH, dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

def register_hr_callbacks(app):
    """인사관리 모듈 콜백 등록"""
    
    # 탭 콘텐츠 렌더링
    @app.callback(
        Output('hr-tab-content', 'children'),
        Input('hr-tabs', 'active_tab')
    )
    def render_hr_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_hr_dashboard, create_employee_management,
            create_attendance_management, create_payroll_management,
            create_leave_management, create_organization_chart,
            create_performance_evaluation, create_training_management,
            create_hr_settings
        )
        
        if active_tab == "hr-dashboard":
            return create_hr_dashboard()
        elif active_tab == "employee-management":
            return create_employee_management()
        elif active_tab == "attendance-management":
            return create_attendance_management()
        elif active_tab == "payroll-management":
            return create_payroll_management()
        elif active_tab == "leave-management":
            return create_leave_management()
        elif active_tab == "organization-chart":
            return create_organization_chart()
        elif active_tab == "performance-evaluation":
            return create_performance_evaluation()
        elif active_tab == "training-management":
            return create_training_management()
        elif active_tab == "hr-settings":
            return create_hr_settings()
    
    # 대시보드 핵심 지표 업데이트
    @app.callback(
        [Output('total-employees', 'children'),
         Output('present-employees', 'children'),
         Output('on-leave-employees', 'children'),
         Output('new-employees', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_hr_dashboard_metrics(n):
        """HR 대시보드 지표 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            # 총 직원수
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM employees 
                WHERE employment_status = 'active'
            """)
            total_employees = cursor.fetchone()[0]
            
            # 출근 인원
            cursor.execute("""
                SELECT COUNT(DISTINCT employee_id) 
                FROM attendance 
                WHERE attendance_date = ? 
                AND attendance_type IN ('normal', 'late', 'early')
            """, (today,))
            present = cursor.fetchone()[0]
            
            # 휴가 중
            cursor.execute("""
                SELECT COUNT(DISTINCT employee_id)
                FROM leave_requests
                WHERE ? BETWEEN start_date AND end_date
                AND status = 'approved'
            """, (today,))
            on_leave = cursor.fetchone()[0]
            
            # 신규 입사 (이번달)
            cursor.execute("""
                SELECT COUNT(*) FROM employees
                WHERE join_date >= ?
                AND employment_status = 'active'
            """, (month_start,))
            new_employees = cursor.fetchone()[0]
            
            return (
                f"{total_employees:,}",
                f"{present:,}",
                f"{on_leave:,}",
                f"{new_employees:,}"
            )
            
        except Exception as e:
            logger.error(f"HR 대시보드 지표 조회 오류: {e}")
            return "0", "0", "0", "0"
        finally:
            conn.close()
    
    # 부서별 인원 차트
    @app.callback(
        Output('dept-employee-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_dept_employee_chart(n):
        """부서별 인원 현황 차트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            query = """
                SELECT department, COUNT(*) as count
                FROM employees
                WHERE employment_status = 'active'
                GROUP BY department
            """
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return px.pie(values=[1], names=['데이터 없음'])
            
            # 부서명 한글화
            dept_mapping = {
                'management': '경영지원부',
                'production': '생산부',
                'quality': '품질관리부',
                'sales': '영업부',
                'rnd': '연구개발부'
            }
            df['department'] = df['department'].map(dept_mapping)
            
            fig = px.pie(
                df, 
                values='count', 
                names='department',
                title='부서별 인원 분포',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label+value'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"부서별 인원 차트 오류: {e}")
            return px.pie(values=[1], names=['오류'])
        finally:
            conn.close()
    
    # 월별 근태 현황 차트
    @app.callback(
        Output('monthly-attendance-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_monthly_attendance_chart(n):
        """월별 근태 현황 차트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            # 최근 6개월 데이터
            query = """
                SELECT 
                    strftime('%Y-%m', attendance_date) as month,
                    attendance_type,
                    COUNT(*) as count
                FROM attendance
                WHERE attendance_date >= date('now', '-6 months')
                GROUP BY month, attendance_type
                ORDER BY month
            """
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return go.Figure()
            
            # 근태 유형 한글화
            type_mapping = {
                'normal': '정상',
                'late': '지각',
                'early': '조퇴',
                'absent': '결근',
                'leave': '휴가',
                'business': '출장'
            }
            df['attendance_type'] = df['attendance_type'].map(type_mapping)
            
            fig = px.bar(
                df,
                x='month',
                y='count',
                color='attendance_type',
                title='월별 근태 현황',
                labels={'month': '월', 'count': '건수', 'attendance_type': '구분'}
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"월별 근태 차트 오류: {e}")
            return go.Figure()
        finally:
            conn.close()
    
    # 오늘의 일정
    @app.callback(
        Output('today-hr-schedule', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_today_schedule(n):
        """오늘의 HR 일정"""
        today = datetime.now()
        
        schedules = []
        
        # 급여일 체크
        if today.day == 25:
            schedules.append(
                dbc.Alert([
                    html.I(className="fas fa-money-check-alt me-2"),
                    "오늘은 급여 지급일입니다."
                ], color="success", className="mb-2")
            )
        
        # 교육 일정
        conn = sqlite3.connect('data/database.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT program_name, location
                FROM training_programs
                WHERE ? BETWEEN start_date AND end_date
                AND status != 'cancelled'
            """, (today.strftime('%Y-%m-%d'),))
            
            trainings = cursor.fetchall()
            for training in trainings:
                schedules.append(
                    dbc.Alert([
                        html.I(className="fas fa-graduation-cap me-2"),
                        f"{training[0]} ({training[1] or '미정'})"
                    ], color="info", className="mb-2")
                )
        except:
            pass
        finally:
            conn.close()
        
        if not schedules:
            schedules = [html.P("오늘 예정된 일정이 없습니다.", className="text-muted")]
        
        return schedules
    
    # HR 알림
    @app.callback(
        Output('hr-notifications', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_hr_notifications(n):
        """HR 알림"""
        notifications = []
        
        conn = sqlite3.connect('data/database.db')
        try:
            cursor = conn.cursor()
            
            # 휴가 승인 대기
            cursor.execute("""
                SELECT COUNT(*) FROM leave_requests
                WHERE status = 'pending'
            """)
            pending_leaves = cursor.fetchone()[0]
            
            if pending_leaves > 0:
                notifications.append(
                    dbc.Alert([
                        html.I(className="fas fa-calendar-check me-2"),
                        f"{pending_leaves}건의 휴가 신청이 승인 대기 중입니다."
                    ], color="warning", className="mb-2")
                )
            
            # 계약 만료 예정
            cursor.execute("""
                SELECT COUNT(*) FROM employment_contracts
                WHERE end_date BETWEEN date('now') AND date('now', '+30 days')
                AND status = 'active'
            """)
            expiring_contracts = cursor.fetchone()[0]
            
            if expiring_contracts > 0:
                notifications.append(
                    dbc.Alert([
                        html.I(className="fas fa-file-contract me-2"),
                        f"{expiring_contracts}명의 계약이 30일 내 만료됩니다."
                    ], color="info", className="mb-2")
                )
            
            # 교육 미이수자
            cursor.execute("""
                SELECT COUNT(DISTINCT e.employee_id)
                FROM employees e
                WHERE e.employment_status = 'active'
                AND NOT EXISTS (
                    SELECT 1 FROM training_history th
                    JOIN training_programs tp ON th.program_id = tp.program_id
                    WHERE th.employee_id = e.employee_id
                    AND tp.program_type = 'mandatory'
                    AND th.status = 'completed'
                    AND strftime('%Y', th.completion_date) = strftime('%Y', 'now')
                )
            """)
            incomplete_training = cursor.fetchone()[0]
            
            if incomplete_training > 0:
                notifications.append(
                    dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"{incomplete_training}명이 필수 교육을 미이수했습니다."
                    ], color="danger", className="mb-2")
                )
            
        except Exception as e:
            logger.error(f"HR 알림 조회 오류: {e}")
        finally:
            conn.close()
        
        if not notifications:
            notifications = [html.P("새로운 알림이 없습니다.", className="text-muted")]
        
        return notifications
    
    # 직원 목록 조회
    @app.callback(
        Output('employee-list-table', 'children'),
        [Input('refresh-employees-btn', 'n_clicks'),
         Input('search-employee', 'value'),
         Input('filter-department', 'value'),
         Input('filter-status', 'value')]
    )
    def update_employee_list(n_clicks, search_term, dept_filter, status_filter):
        """직원 목록 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT 
                employee_id,
                name,
                department,
                position,
                join_date,
                mobile_phone,
                email,
                employment_status
            FROM employees
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR employee_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if dept_filter != 'all':
            query += " AND department = ?"
            params.append(dept_filter)
        
        if status_filter != 'all':
            query += " AND employment_status = ?"
            params.append(status_filter)
        
        query += " ORDER BY employee_id"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                return html.Div("직원이 없습니다.", className="text-center p-4")
            
            # 매핑
            dept_mapping = {
                'management': '경영지원부',
                'production': '생산부',
                'quality': '품질관리부',
                'sales': '영업부',
                'rnd': '연구개발부'
            }
            
            position_mapping = {
                'staff': '사원',
                'senior': '주임',
                'assistant': '대리',
                'manager': '과장',
                'deputy': '차장',
                'general': '부장',
                'director': '이사'
            }
            
            status_mapping = {
                'active': ('재직', 'success'),
                'leave': ('휴직', 'warning'),
                'resigned': ('퇴직', 'secondary')
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("사번"),
                        html.Th("이름"),
                        html.Th("부서"),
                        html.Th("직급"),
                        html.Th("입사일"),
                        html.Th("연락처"),
                        html.Th("상태"),
                        html.Th("작업")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                dept_kr = dept_mapping.get(row['department'], row['department'])
                position_kr = position_mapping.get(row['position'], row['position'])
                status_info = status_mapping.get(row['employment_status'], ('알수없음', 'secondary'))
                
                table_body.append(
                    html.Tr([
                        html.Td(row['employee_id']),
                        html.Td(row['name']),
                        html.Td(dept_kr),
                        html.Td(position_kr),
                        html.Td(row['join_date']),
                        html.Td([
                            html.Div(row['mobile_phone'] or '-'),
                            html.Small(row['email'] or '-', className="text-muted")
                        ]),
                        html.Td(
                            dbc.Badge(status_info[0], color=status_info[1])
                        ),
                        html.Td(
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-eye"),
                                    id={"type": "view-employee", "index": row['employee_id']},
                                    color="info",
                                    size="sm"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    id={"type": "edit-employee", "index": row['employee_id']},
                                    color="primary",
                                    size="sm"
                                )
                            ])
                        )
                    ])
                )
            
            return dbc.Table(
                table_header + [html.Tbody(table_body)],
                striped=True,
                bordered=True,
                hover=True,
                responsive=True
            )
            
        except Exception as e:
            logger.error(f"직원 목록 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 직원 모달 토글
    @app.callback(
        Output('employee-modal', 'is_open'),
        [Input('new-employee-btn', 'n_clicks'),
         Input('close-employee-modal', 'n_clicks'),
         Input('save-employee-btn', 'n_clicks')],
        [State('employee-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_employee_modal(n1, n2, n3, is_open):
        """직원 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 직원 저장
    @app.callback(
        Output('employee-modal-message', 'children'),
        Input('save-employee-btn', 'n_clicks'),
        [State('employee-name', 'value'),
         State('employee-department', 'value'),
         State('employee-position', 'value'),
         State('join-date', 'value'),
         State('mobile-phone', 'value'),
         State('employee-email', 'value'),
         State('base-salary', 'value'),
         State('session-store', 'data')],
        prevent_initial_call=True
    )
    def save_employee(n_clicks, name, dept, position, join_date, 
                     phone, email, salary, session_data):
        """직원 정보 저장"""
        if not all([name, dept, position, join_date]):
            return dbc.Alert("필수 항목을 입력하세요.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 사번 생성 (연도 + 순번)
            year = datetime.now().strftime('%Y')
            cursor.execute("""
                SELECT COUNT(*) FROM employees 
                WHERE employee_id LIKE ?
            """, (f"{year}%",))
            count = cursor.fetchone()[0]
            employee_id = f"{year}{count+1:04d}"
            
            # 직원 정보 저장
            cursor.execute("""
                INSERT INTO employees
                (employee_id, name, department, position, join_date,
                 mobile_phone, email, base_salary, employment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (employee_id, name, dept, position, join_date,
                  phone, email, salary or 0))
            
            conn.commit()
            conn.close()
            
            logger.info(f"직원 등록 완료: {employee_id} - {name}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"),
                 f"직원 {name}({employee_id})이(가) 등록되었습니다!"],
                color="success"
            )
            
        except Exception as e:
            logger.error(f"직원 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
    
    # 근태 현황 업데이트
    @app.callback(
        [Output('normal-attendance', 'children'),
         Output('late-attendance', 'children'),
         Output('early-leave', 'children'),
         Output('absent', 'children'),
         Output('on-vacation', 'children'),
         Output('business-trip', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_attendance_summary(n):
        """오늘의 근태 현황"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 근태 유형별 집계
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    attendance_type,
                    COUNT(*) as count
                FROM attendance
                WHERE attendance_date = ?
                GROUP BY attendance_type
            """, (today,))
            
            results = cursor.fetchall()
            attendance_dict = {row[0]: row[1] for row in results}
            
            return (
                str(attendance_dict.get('normal', 0)),
                str(attendance_dict.get('late', 0)),
                str(attendance_dict.get('early', 0)),
                str(attendance_dict.get('absent', 0)),
                str(attendance_dict.get('leave', 0)),
                str(attendance_dict.get('business', 0))
            )
            
        except Exception as e:
            logger.error(f"근태 현황 조회 오류: {e}")
            return "0", "0", "0", "0", "0", "0"
        finally:
            conn.close()
    
    # 근태 조회
    @app.callback(
        Output('attendance-table', 'children'),
        Input('search-attendance-btn', 'n_clicks'),
        [State('attendance-start-date', 'value'),
         State('attendance-end-date', 'value'),
         State('attendance-dept-filter', 'value'),
         State('attendance-employee-search', 'value')]
    )
    def search_attendance(n_clicks, start_date, end_date, dept, employee_search):
        """근태 현황 조회"""
        if not n_clicks:
            return html.Div("조회 버튼을 클릭하세요.", className="text-center p-4")
        
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT 
                a.attendance_date,
                e.employee_id,
                e.name,
                e.department,
                a.check_in_time,
                a.check_out_time,
                a.attendance_type,
                a.overtime_hours
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.attendance_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if dept != 'all':
            query += " AND e.department = ?"
            params.append(dept)
        
        if employee_search:
            query += " AND (e.name LIKE ? OR e.employee_id LIKE ?)"
            params.extend([f"%{employee_search}%", f"%{employee_search}%"])
        
        query += " ORDER BY a.attendance_date DESC, e.employee_id"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                return html.Div("조회 결과가 없습니다.", className="text-center p-4")
            
            # 매핑
            dept_mapping = {
                'management': '경영지원부',
                'production': '생산부',
                'quality': '품질관리부',
                'sales': '영업부',
                'rnd': '연구개발부'
            }
            
            type_mapping = {
                'normal': ('정상', 'success'),
                'late': ('지각', 'warning'),
                'early': ('조퇴', 'info'),
                'absent': ('결근', 'danger'),
                'leave': ('휴가', 'primary'),
                'business': ('출장', 'secondary')
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("날짜"),
                        html.Th("사번"),
                        html.Th("이름"),
                        html.Th("부서"),
                        html.Th("출근"),
                        html.Th("퇴근"),
                        html.Th("구분"),
                        html.Th("초과근무")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                dept_kr = dept_mapping.get(row['department'], row['department'])
                type_info = type_mapping.get(row['attendance_type'], ('기타', 'secondary'))
                
                overtime_display = f"{row['overtime_hours']}H" if row['overtime_hours'] > 0 else "-"
                
                table_body.append(
                    html.Tr([
                        html.Td(row['attendance_date']),
                        html.Td(row['employee_id']),
                        html.Td(row['name']),
                        html.Td(dept_kr),
                        html.Td(row['check_in_time'] or '-'),
                        html.Td(row['check_out_time'] or '-'),
                        html.Td(dbc.Badge(type_info[0], color=type_info[1])),
                        html.Td(overtime_display)
                    ])
                )
            
            return dbc.Table(
                table_header + [html.Tbody(table_body)],
                striped=True,
                bordered=True,
                hover=True,
                responsive=True
            )
            
        except Exception as e:
            logger.error(f"근태 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 근태 모달 토글
    @app.callback(
        Output('attendance-modal', 'is_open'),
        [Input('attendance-record-btn', 'n_clicks'),
         Input('close-attendance-modal', 'n_clicks'),
         Input('save-attendance-btn', 'n_clicks')],
        [State('attendance-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_attendance_modal(n1, n2, n3, is_open):
        """근태 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 급여 총액 업데이트
    @app.callback(
        [Output('total-payroll', 'children'),
         Output('average-salary', 'children'),
         Output('insurance-total', 'children'),
         Output('income-tax-total', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_payroll_summary(n):
        """급여 현황 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            current_month = datetime.now().strftime('%Y-%m')
            
            # 이번달 급여 총액
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(gross_salary) as total,
                    AVG(gross_salary) as average,
                    SUM(insurance_company) as insurance,
                    SUM(income_tax) as tax
                FROM payroll
                WHERE strftime('%Y-%m', CAST(pay_year AS TEXT) || '-' || 
                      CASE WHEN pay_month < 10 THEN '0' ELSE '' END || 
                      CAST(pay_month AS TEXT)) = ?
            """, (current_month,))
            
            result = cursor.fetchone()
            
            if result and result[0]:
                return (
                    f"₩{result[0]:,.0f}",
                    f"₩{result[1]:,.0f}",
                    f"₩{result[2]:,.0f}",
                    f"₩{result[3]:,.0f}"
                )
            else:
                # 직원 기본급으로 예상 계산
                cursor.execute("""
                    SELECT 
                        SUM(base_salary) as total,
                        AVG(base_salary) as average
                    FROM employees
                    WHERE employment_status = 'active'
                """)
                
                emp_result = cursor.fetchone()
                if emp_result and emp_result[0]:
                    total = emp_result[0]
                    avg = emp_result[1]
                    insurance = total * 0.09  # 회사 부담 약 9%
                    tax = total * 0.033  # 소득세 약 3.3%
                    
                    return (
                        f"₩{total:,.0f}",
                        f"₩{avg:,.0f}",
                        f"₩{insurance:,.0f}",
                        f"₩{tax:,.0f}"
                    )
                
            return "₩0", "₩0", "₩0", "₩0"
            
        except Exception as e:
            logger.error(f"급여 현황 조회 오류: {e}")
            return "₩0", "₩0", "₩0", "₩0"
        finally:
            conn.close()
    
    # 급여 계산
    @app.callback(
        Output('payroll-list', 'children'),
        Input('run-payroll-btn', 'n_clicks'),
        [State('payroll-year', 'value'),
         State('payroll-month', 'value'),
         State('payroll-date', 'value'),
         State('payroll-target', 'value')]
    )
    def calculate_payroll(n_clicks, year, month, pay_date, target):
        """급여 계산 실행"""
        if not n_clicks:
            return html.Div("급여 계산을 실행하려면 '실행' 버튼을 클릭하세요.", className="text-center p-4")
        
        conn = sqlite3.connect('data/database.db')
        
        try:
            cursor = conn.cursor()
            
            # 대상 직원 조회
            query = "SELECT * FROM employees WHERE employment_status = 'active'"
            if target != 'all':
                query += f" AND employment_type = '{target}'"
            
            employees = pd.read_sql_query(query, conn)
            
            if employees.empty:
                return html.Div("급여 계산 대상 직원이 없습니다.", className="text-center p-4")
            
            payroll_data = []
            
            for idx, emp in employees.iterrows():
                # 기본급
                base_salary = emp['base_salary']
                
                # 초과근무 수당 계산
                cursor.execute("""
                    SELECT SUM(overtime_hours) 
                    FROM attendance
                    WHERE employee_id = ? 
                    AND strftime('%Y-%m', attendance_date) = ?
                """, (emp['employee_id'], f"{year}-{month:02d}"))
                
                overtime_hours = cursor.fetchone()[0] or 0
                overtime_pay = (base_salary / 209) * overtime_hours * 1.5
                
                # 총 지급액
                gross_salary = base_salary + overtime_pay
                
                # 공제 항목
                income_tax = gross_salary * 0.033
                health_insurance = gross_salary * 0.0343
                pension = gross_salary * 0.045
                employment_insurance = gross_salary * 0.008
                
                total_deductions = income_tax + health_insurance + pension + employment_insurance
                net_salary = gross_salary - total_deductions
                
                payroll_data.append({
                    'employee_id': emp['employee_id'],
                    'name': emp['name'],
                    'department': emp['department'],
                    'base_salary': base_salary,
                    'overtime_pay': overtime_pay,
                    'gross_salary': gross_salary,
                    'deductions': total_deductions,
                    'net_salary': net_salary
                })
            
            # 급여 명세 테이블
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("사번"),
                        html.Th("이름"),
                        html.Th("부서"),
                        html.Th("기본급"),
                        html.Th("초과수당"),
                        html.Th("총지급액"),
                        html.Th("공제액"),
                        html.Th("실지급액")
                    ])
                ])
            ]
            
            dept_mapping = {
                'management': '경영지원부',
                'production': '생산부',
                'quality': '품질관리부',
                'sales': '영업부',
                'rnd': '연구개발부'
            }
            
            table_body = []
            for emp in payroll_data:
                dept_kr = dept_mapping.get(emp['department'], emp['department'])
                
                table_body.append(
                    html.Tr([
                        html.Td(emp['employee_id']),
                        html.Td(emp['name']),
                        html.Td(dept_kr),
                        html.Td(f"₩{emp['base_salary']:,.0f}"),
                        html.Td(f"₩{emp['overtime_pay']:,.0f}"),
                        html.Td(f"₩{emp['gross_salary']:,.0f}"),
                        html.Td(f"₩{emp['deductions']:,.0f}"),
                        html.Td(f"₩{emp['net_salary']:,.0f}", className="fw-bold")
                    ])
                )
            
            # 합계
            total_gross = sum(emp['gross_salary'] for emp in payroll_data)
            total_net = sum(emp['net_salary'] for emp in payroll_data)
            
            table_body.append(
                html.Tr([
                    html.Td("합계", colSpan=5, className="text-end fw-bold"),
                    html.Td(f"₩{total_gross:,.0f}", className="fw-bold"),
                    html.Td(""),
                    html.Td(f"₩{total_net:,.0f}", className="fw-bold")
                ])
            )
            
            return [
                dbc.Alert(
                    f"{len(payroll_data)}명의 급여가 계산되었습니다.",
                    color="success",
                    className="mb-3"
                ),
                dbc.Table(
                    table_header + [html.Tbody(table_body)],
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True
                )
            ]
            
        except Exception as e:
            logger.error(f"급여 계산 오류: {e}")
            return dbc.Alert(f"급여 계산 중 오류가 발생했습니다: {str(e)}", color="danger")
        finally:
            conn.close()
    
    # 휴가 현황 업데이트
    @app.callback(
        [Output('leave-requests', 'children'),
         Output('today-leaves', 'children'),
         Output('leave-usage-rate', 'children'),
         Output('unused-leaves', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_leave_summary(n):
        """휴가 현황 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_year = datetime.now().year
            
            cursor = conn.cursor()
            
            # 휴가 신청 대기
            cursor.execute("""
                SELECT COUNT(*) FROM leave_requests
                WHERE status = 'pending'
            """)
            pending = cursor.fetchone()[0]
            
            # 오늘 휴가자
            cursor.execute("""
                SELECT COUNT(*) FROM leave_requests
                WHERE ? BETWEEN start_date AND end_date
                AND status = 'approved'
            """, (today,))
            today_leaves = cursor.fetchone()[0]
            
            # 연차 사용률
            cursor.execute("""
                SELECT 
                    AVG(CAST(used_days AS FLOAT) / CAST(total_days AS FLOAT) * 100)
                FROM annual_leave
                WHERE year = ?
            """, (current_year,))
            usage_rate = cursor.fetchone()[0] or 0
            
            # 미사용 연차
            cursor.execute("""
                SELECT SUM(remaining_days)
                FROM annual_leave
                WHERE year = ?
            """, (current_year,))
            unused = cursor.fetchone()[0] or 0
            
            return (
                str(pending),
                str(today_leaves),
                f"{usage_rate:.1f}%",
                f"{unused:.0f}"
            )
            
        except Exception as e:
            logger.error(f"휴가 현황 조회 오류: {e}")
            return "0", "0", "0%", "0"
        finally:
            conn.close()
    
    # 휴가 콘텐츠
    @app.callback(
        Output('leave-content', 'children'),
        Input('leave-tabs', 'active_tab')
    )
    def render_leave_content(active_tab):
        """휴가 탭 콘텐츠"""
        if active_tab == 'leave-requests-tab':
            return create_leave_requests_list()
        elif active_tab == 'leave-status-tab':
            return create_leave_status()
        elif active_tab == 'annual-leave-tab':
            return create_annual_leave_management()
        return html.Div()
    
    # 휴가 모달 토글
    @app.callback(
        Output('leave-modal', 'is_open'),
        [Input('new-leave-btn', 'n_clicks'),
         Input('close-leave-modal', 'n_clicks'),
         Input('submit-leave-btn', 'n_clicks')],
        [State('leave-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_leave_modal(n1, n2, n3, is_open):
        """휴가 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 조직도 표시
    @app.callback(
        Output('organization-chart-display', 'children'),
        Input('org-chart-view', 'value')
    )
    def display_organization_chart(view_type):
        """조직도 표시"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            if view_type == 'hierarchy':
                # 계층도
                return create_hierarchy_chart(conn)
            elif view_type == 'department':
                # 부서별
                return create_department_chart(conn)
            elif view_type == 'position':
                # 직급별
                return create_position_chart(conn)
                
        except Exception as e:
            logger.error(f"조직도 표시 오류: {e}")
            return html.Div("조직도를 표시할 수 없습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # HR 설정 저장
    @app.callback(
        Output('hr-settings-message', 'children'),
        Input('save-hr-settings-btn', 'n_clicks'),
        [State('work-start-time', 'value'),
         State('work-end-time', 'value'),
         State('lunch-duration', 'value'),
         State('pay-day', 'value'),
         State('income-tax-rate', 'value'),
         State('annual-leave-days', 'value')],
        prevent_initial_call=True
    )
    def save_hr_settings(n_clicks, start_time, end_time, lunch,
                        pay_day, tax_rate, annual_leave):
        """HR 설정 저장"""
        try:
            settings = {
                'work_hours': {
                    'start': start_time,
                    'end': end_time,
                    'lunch_duration': lunch
                },
                'payroll': {
                    'pay_day': pay_day,
                    'tax_rate': tax_rate
                },
                'leave': {
                    'annual_days': annual_leave
                }
            }
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('hr_settings', ?)
            """, (json.dumps(settings),))
            
            conn.commit()
            conn.close()
            
            logger.info("HR 설정 저장 완료")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "설정이 저장되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"HR 설정 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                color="danger",
                dismissable=True
            )

# 헬퍼 함수들

def create_leave_requests_list():
    """휴가 신청 목록"""
    conn = sqlite3.connect('data/database.db')
    
    try:
        query = """
            SELECT 
                lr.request_id,
                lr.employee_id,
                e.name,
                e.department,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.leave_days,
                lr.reason,
                lr.status
            FROM leave_requests lr
            JOIN employees e ON lr.employee_id = e.employee_id
            WHERE lr.status = 'pending'
            ORDER BY lr.created_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return html.Div("승인 대기 중인 휴가 신청이 없습니다.", className="text-center p-4")
        
        # 테이블 생성
        table_rows = []
        for idx, row in df.iterrows():
            table_rows.append(
                html.Tr([
                    html.Td(row['name']),
                    html.Td(row['leave_type']),
                    html.Td(f"{row['start_date']} ~ {row['end_date']}"),
                    html.Td(f"{row['leave_days']}일"),
                    html.Td(row['reason']),
                    html.Td(
                        dbc.ButtonGroup([
                            dbc.Button("승인", color="success", size="sm",
                                     id={"type": "approve-leave", "index": row['request_id']}),
                            dbc.Button("반려", color="danger", size="sm",
                                     id={"type": "reject-leave", "index": row['request_id']})
                        ])
                    )
                ])
            )
        
        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("신청자"),
                    html.Th("휴가 종류"),
                    html.Th("기간"),
                    html.Th("일수"),
                    html.Th("사유"),
                    html.Th("작업")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, bordered=True, hover=True, responsive=True)
        
    except Exception as e:
        logger.error(f"휴가 신청 목록 조회 오류: {e}")
        return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
    finally:
        conn.close()

def create_leave_status():
    """휴가 현황"""
    return html.Div("휴가 현황 페이지", className="text-center p-4")

def create_annual_leave_management():
    """연차 관리"""
    return html.Div("연차 관리 페이지", className="text-center p-4")

def create_hierarchy_chart(conn):
    """계층도"""
    return html.Div("조직 계층도", className="text-center p-4")

def create_department_chart(conn):
    """부서별 조직도"""
    return html.Div("부서별 조직도", className="text-center p-4")

def create_position_chart(conn):
    """직급별 조직도"""
    return html.Div("직급별 조직도", className="text-center p-4")
