# File: modules/sales/callbacks.py
# 영업관리 모듈 콜백 함수 - V1.0 신규

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

logger = logging.getLogger(__name__)

def register_sales_callbacks(app):
    """영업관리 모듈 콜백 등록"""
    
    # 탭 콘텐츠 렌더링
    @app.callback(
        Output('sales-tab-content', 'children'),
        Input('sales-tabs', 'active_tab')
    )
    def render_sales_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_quotation_management, create_order_management,
            create_customer_management, create_sales_analysis,
            create_crm, create_sales_settings
        )
        
        if active_tab == "quotation":
            return create_quotation_management()
        elif active_tab == "order":
            return create_order_management()
        elif active_tab == "customer":
            return create_customer_management()
        elif active_tab == "sales-analysis":
            return create_sales_analysis()
        elif active_tab == "crm":
            return create_crm()
        elif active_tab == "sales-settings":
            return create_sales_settings()
    
    # 견적 현황 업데이트
    @app.callback(
        [Output('active-quotes', 'children'),
         Output('conversion-rate', 'children'),
         Output('pending-quotes', 'children'),
         Output('monthly-quotes', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_quote_summary(n):
        """견적 현황 요약 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            cursor = conn.cursor()
            
            # 진행중 견적
            cursor.execute("""
                SELECT COUNT(*) FROM quotations 
                WHERE status IN ('draft', 'sent', 'reviewing')
            """)
            active_quotes = cursor.fetchone()[0]
            
            # 수주 전환율 (최근 30일)
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(*), 0) as conversion_rate
                FROM quotations 
                WHERE quote_date >= date('now', '-30 days')
            """)
            conversion_result = cursor.fetchone()[0]
            conversion_rate = conversion_result if conversion_result else 0
            
            # 응답 대기 견적
            cursor.execute("""
                SELECT COUNT(*) FROM quotations 
                WHERE status = 'sent' 
                AND validity_date >= date('now')
            """)
            pending_quotes = cursor.fetchone()[0]
            
            # 이번달 견적액
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM quotations 
                WHERE strftime('%Y-%m', quote_date) = strftime('%Y-%m', 'now')
            """)
            monthly_quotes = cursor.fetchone()[0]
            
            return (
                f"{active_quotes:,}",
                f"{conversion_rate:.1f}%",
                f"{pending_quotes:,}",
                f"₩{monthly_quotes:,.0f}"
            )
            
        except Exception as e:
            logger.error(f"견적 현황 조회 오류: {e}")
            return "0", "0%", "0", "₩0"
        finally:
            conn.close()
    
    # 견적서 리스트 조회
    @app.callback(
        Output('quotation-list-table', 'children'),
        [Input('search-quotes-btn', 'n_clicks')],
        [State('quote-start-date', 'value'),
         State('quote-end-date', 'value'),
         State('quote-status-filter', 'value'),
         State('quote-customer-filter', 'value')]
    )
    def update_quotation_list(n_clicks, start_date, end_date, status, customer):
        """견적서 리스트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT q.quote_number,
                   q.quote_date,
                   c.customer_name,
                   q.total_amount,
                   q.status,
                   q.validity_date,
                   u.username as created_by
            FROM quotations q
            LEFT JOIN customers c ON q.customer_code = c.customer_code
            LEFT JOIN users u ON q.created_by = u.id
            WHERE q.quote_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if status != 'all':
            query += " AND q.status = ?"
            params.append(status)
        
        if customer != 'all':
            query += " AND q.customer_code = ?"
            params.append(customer)
        
        query += " ORDER BY q.quote_date DESC, q.created_at DESC"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                return html.Div("견적서가 없습니다.", className="text-center p-4")
            
            # 상태 한글화 및 색상
            status_mapping = {
                'draft': ('작성중', 'secondary'),
                'sent': ('발송완료', 'info'),
                'reviewing': ('고객검토', 'warning'),
                'won': ('수주확정', 'success'),
                'lost': ('수주실패', 'danger'),
                'expired': ('만료', 'dark')
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("견적번호"),
                        html.Th("견적일자"),
                        html.Th("고객명"),
                        html.Th("견적금액"),
                        html.Th("상태"),
                        html.Th("유효기간"),
                        html.Th("작성자"),
                        html.Th("작업")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                status_info = status_mapping.get(row['status'], ('알 수 없음', 'secondary'))
                status_badge = dbc.Badge(status_info[0], color=status_info[1])
                
                # 유효기간 체크
                if row['validity_date'] and row['status'] in ['sent', 'reviewing']:
                    validity_date = datetime.strptime(row['validity_date'], '%Y-%m-%d')
                    days_left = (validity_date - datetime.now()).days
                    if days_left <= 3:
                        validity_display = html.Span([
                            row['validity_date'],
                            dbc.Badge(f"D-{days_left}", color="danger", className="ms-1")
                        ])
                    else:
                        validity_display = row['validity_date']
                else:
                    validity_display = row['validity_date'] or '-'
                
                table_body.append(
                    html.Tr([
                        html.Td(
                            html.A(
                                row['quote_number'],
                                href="#",
                                id={"type": "quote-link", "index": row['quote_number']}
                            )
                        ),
                        html.Td(row['quote_date']),
                        html.Td(row['customer_name']),
                        html.Td(f"₩{row['total_amount']:,.0f}"),
                        html.Td(status_badge),
                        html.Td(validity_display),
                        html.Td(row['created_by']),
                        html.Td(
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-eye"),
                                    id={"type": "view-quote", "index": row['quote_number']},
                                    color="info",
                                    size="sm",
                                    title="보기"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    id={"type": "edit-quote", "index": row['quote_number']},
                                    color="primary",
                                    size="sm",
                                    title="수정",
                                    disabled=row['status'] not in ['draft']
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-handshake"),
                                    id={"type": "convert-quote", "index": row['quote_number']},
                                    color="success",
                                    size="sm",
                                    title="수주 전환",
                                    disabled=row['status'] != 'reviewing'
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
            logger.error(f"견적서 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 수주 현황 업데이트
    @app.callback(
        [Output('monthly-orders', 'children'),
         Output('active-orders', 'children'),
         Output('pending-delivery-orders', 'children'),
         Output('completed-orders', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_order_summary(n):
        """수주 현황 요약 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            cursor = conn.cursor()
            
            # 이번달 수주액
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales_orders 
                WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')
            """)
            monthly_orders = cursor.fetchone()[0]
            
            # 진행중 수주
            cursor.execute("""
                SELECT COUNT(*) FROM sales_orders 
                WHERE status IN ('received', 'confirmed', 'in_production')
            """)
            active_orders = cursor.fetchone()[0]
            
            # 배송 예정
            cursor.execute("""
                SELECT COUNT(*) FROM sales_orders 
                WHERE status = 'ready_for_delivery'
                OR (delivery_date <= date('now', '+7 days') AND status = 'in_production')
            """)
            pending_delivery = cursor.fetchone()[0]
            
            # 완료
            cursor.execute("""
                SELECT COUNT(*) FROM sales_orders 
                WHERE status = 'completed'
                AND strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')
            """)
            completed_orders = cursor.fetchone()[0]
            
            return (
                f"₩{monthly_orders:,.0f}",
                f"{active_orders:,}",
                f"{pending_delivery:,}",
                f"{completed_orders:,}"
            )
            
        except Exception as e:
            logger.error(f"수주 현황 조회 오류: {e}")
            return "₩0", "0", "0", "0"
        finally:
            conn.close()
    
    # 고객 리스트 조회
    @app.callback(
        Output('customer-list-table', 'children'),
        [Input('filter-customer-btn', 'n_clicks'),
         Input('save-customer-btn', 'n_clicks')],
        [State('customer-search', 'value'),
         State('customer-grade-filter', 'value')]
    )
    def update_customer_list(filter_clicks, save_clicks, search_value, grade_filter):
        """고객 리스트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT c.customer_code,
                   c.customer_name,
                   c.contact_person,
                   c.phone,
                   c.email,
                   c.grade,
                   c.payment_terms,
                   COALESCE(s.total_sales, 0) as total_sales,
                   COALESCE(s.order_count, 0) as order_count
            FROM customers c
            LEFT JOIN (
                SELECT customer_code,
                       SUM(total_amount) as total_sales,
                       COUNT(*) as order_count
                FROM sales_orders
                WHERE order_date >= date('now', '-365 days')
                GROUP BY customer_code
            ) s ON c.customer_code = s.customer_code
            WHERE c.is_active = 1
        """
        params = []
        
        if search_value:
            query += " AND (c.customer_name LIKE ? OR c.business_no LIKE ?)"
            params.extend([f"%{search_value}%", f"%{search_value}%"])
        
        if grade_filter != 'all':
            query += " AND c.grade = ?"
            params.append(grade_filter)
        
        query += " ORDER BY s.total_sales DESC, c.customer_name"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                return html.Div("등록된 고객이 없습니다.", className="text-center p-4")
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("고객코드"),
                        html.Th("고객명"),
                        html.Th("담당자"),
                        html.Th("연락처"),
                        html.Th("등급"),
                        html.Th("연간매출"),
                        html.Th("거래횟수"),
                        html.Th("작업")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                # 등급별 색상
                grade_colors = {
                    'VIP': 'danger',
                    'Gold': 'warning',
                    'Silver': 'info',
                    'Bronze': 'secondary'
                }
                grade_badge = dbc.Badge(
                    row['grade'], 
                    color=grade_colors.get(row['grade'], 'secondary')
                )
                
                table_body.append(
                    html.Tr([
                        html.Td(row['customer_code']),
                        html.Td(row['customer_name']),
                        html.Td(row['contact_person'] or '-'),
                        html.Td(row['phone'] or '-'),
                        html.Td(grade_badge),
                        html.Td(f"₩{row['total_sales']:,.0f}"),
                        html.Td(f"{row['order_count']:,}"),
                        html.Td(
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-eye"),
                                    id={"type": "view-customer", "index": row['customer_code']},
                                    color="info",
                                    size="sm"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    id={"type": "edit-customer", "index": row['customer_code']},
                                    color="primary",
                                    size="sm"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-chart-line"),
                                    id={"type": "customer-history", "index": row['customer_code']},
                                    color="success",
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
            logger.error(f"고객 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 영업 분석 차트 업데이트
    @app.callback(
        [Output('sales-performance-chart', 'figure'),
         Output('sales-pipeline-chart', 'figure'),
         Output('salesperson-performance-chart', 'figure'),
         Output('product-sales-chart', 'figure')],
        Input('sales-analysis-period', 'value')
    )
    def update_sales_analysis(period):
        """영업 분석 차트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        # 기간 설정
        if period == 'month':
            start_date = datetime.now().replace(day=1)
            date_format = '%Y-%m-%d'
            group_by = "DATE(order_date)"
        elif period == 'quarter':
            month = datetime.now().month
            quarter_start = ((month - 1) // 3) * 3 + 1
            start_date = datetime.now().replace(month=quarter_start, day=1)
            date_format = '%Y-%m'
            group_by = "strftime('%Y-%m', order_date)"
        elif period == 'half':
            start_date = datetime.now().replace(month=1 if datetime.now().month <= 6 else 7, day=1)
            date_format = '%Y-%m'
            group_by = "strftime('%Y-%m', order_date)"
        else:  # year
            start_date = datetime.now().replace(month=1, day=1)
            date_format = '%Y-%m'
            group_by = "strftime('%Y-%m', order_date)"
        
        try:
            # 1. 매출 성과 차트
            performance_query = f"""
                SELECT {group_by} as period,
                       SUM(total_amount) as sales,
                       COUNT(*) as order_count
                FROM sales_orders
                WHERE order_date >= ? AND status != 'cancelled'
                GROUP BY {group_by}
                ORDER BY period
            """
            performance_df = pd.read_sql_query(
                performance_query, 
                conn, 
                params=[start_date.strftime('%Y-%m-%d')]
            )
            
            performance_fig = go.Figure()
            performance_fig.add_trace(go.Bar(
                x=performance_df['period'],
                y=performance_df['sales'],
                name='매출액',
                marker_color='#0066cc',
                text=performance_df['sales'].apply(lambda x: f'₩{x:,.0f}'),
                textposition='auto'
            ))
            performance_fig.update_layout(
                title="매출 성과",
                xaxis_title="기간",
                yaxis_title="매출액 (원)"
            )
            
            # 2. 영업 파이프라인 차트
            pipeline_query = """
                SELECT status,
                       COUNT(*) as count,
                       SUM(total_amount) as amount
                FROM quotations q
                WHERE quote_date >= ?
                GROUP BY status
            """
            pipeline_df = pd.read_sql_query(
                pipeline_query,
                conn,
                params=[start_date.strftime('%Y-%m-%d')]
            )
            
            pipeline_fig = go.Figure()
            pipeline_fig.add_trace(go.Funnel(
                y=pipeline_df['status'],
                x=pipeline_df['count'],
                textinfo="value+percent initial"
            ))
            pipeline_fig.update_layout(title="영업 파이프라인")
            
            # 3. 영업사원별 실적 (더미 데이터)
            salesperson_data = {
                '영업사원': ['김영업', '이세일즈', '박마케팅', '최고객'],
                '매출액': [50000000, 45000000, 38000000, 42000000],
                '건수': [15, 12, 10, 13]
            }
            salesperson_df = pd.DataFrame(salesperson_data)
            
            salesperson_fig = go.Figure()
            salesperson_fig.add_trace(go.Bar(
                x=salesperson_df['영업사원'],
                y=salesperson_df['매출액'],
                name='매출액',
                marker_color='#28a745',
                text=salesperson_df['매출액'].apply(lambda x: f'₩{x:,.0f}'),
                textposition='auto'
            ))
            salesperson_fig.update_layout(
                title="영업사원별 실적",
                xaxis_title="영업사원",
                yaxis_title="매출액 (원)"
            )
            
            # 4. 제품별 매출 (더미 데이터)
            product_data = {
                '제품': ['제품A', '제품B', '제품C', '제품D', '제품E'],
                '매출액': [80000000, 65000000, 45000000, 35000000, 25000000]
            }
            product_df = pd.DataFrame(product_data)
            
            product_fig = go.Figure()
            product_fig.add_trace(go.Pie(
                labels=product_df['제품'],
                values=product_df['매출액'],
                hole=0.4
            ))
            product_fig.update_layout(title="제품별 매출 비중")
            
            return performance_fig, pipeline_fig, salesperson_fig, product_fig
            
        except Exception as e:
            logger.error(f"영업 분석 오류: {e}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="데이터 조회 중 오류가 발생했습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig, empty_fig, empty_fig
        finally:
            conn.close()
    
    # 견적서 모달 토글
    @app.callback(
        Output('quotation-modal', 'is_open'),
        [Input('new-quote-btn', 'n_clicks'),
         Input('close-quote-modal', 'n_clicks'),
         Input('save-quote-btn', 'n_clicks')],
        [State('quotation-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_quotation_modal(new_clicks, close_clicks, save_clicks, is_open):
        """견적서 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 수주 모달 토글
    @app.callback(
        Output('order-modal', 'is_open'),
        [Input('new-order-btn', 'n_clicks'),
         Input('close-order-modal', 'n_clicks'),
         Input('save-order-btn', 'n_clicks')],
        [State('order-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_order_modal(new_clicks, close_clicks, save_clicks, is_open):
        """수주 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 고객 모달 토글
    @app.callback(
        Output('customer-modal', 'is_open'),
        [Input('add-customer-btn', 'n_clicks'),
         Input('close-customer-modal', 'n_clicks'),
         Input('save-customer-btn', 'n_clicks')],
        [State('customer-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_customer_modal(add_clicks, close_clicks, save_clicks, is_open):
        """고객 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 견적서 저장
    @app.callback(
        Output('quote-modal-message', 'children'),
        Input('save-quote-btn', 'n_clicks'),
        [State('modal-quote-date', 'value'),
         State('modal-quote-customer', 'value'),
         State('modal-quote-validity', 'value'),
         State('quote-total-amount', 'children'),
         State('modal-quote-notes', 'value'),
         State('session-store', 'data')],
        prevent_initial_call=True
    )
    def save_quotation(n_clicks, quote_date, customer, validity_date, 
                      total_amount, notes, session_data):
        """견적서 저장"""
        if not all([quote_date, customer, validity_date]):
            return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 견적번호 생성
            cursor.execute("SELECT COUNT(*) FROM quotations WHERE quote_date = ?", (quote_date,))
            count = cursor.fetchone()[0]
            quote_number = f"QT-{quote_date.replace('-', '')}-{count+1:04d}"
            
            # 총액 파싱
            total_amount_value = float(total_amount.replace('₩', '').replace(',', '')) if total_amount != '₩0' else 0
            
            # 사용자 ID
            user_id = session_data.get('user_id', 1) if session_data else 1
            
            # 견적서 저장
            cursor.execute("""
                INSERT INTO quotations
                (quote_number, quote_date, customer_code, validity_date,
                 total_amount, status, notes, created_by)
                VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
            """, (quote_number, quote_date, customer, validity_date,
                  total_amount_value, notes, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"견적서 생성 완료: {quote_number}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"),
                 f"견적서 {quote_number}가 생성되었습니다!"],
                color="success"
            )
            
        except Exception as e:
            logger.error(f"견적서 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
    
    # 수주 저장
    @app.callback(
        Output('order-modal-message', 'children'),
        Input('save-order-btn', 'n_clicks'),
        [State('modal-order-date', 'value'),
         State('modal-order-customer', 'value'),
         State('modal-delivery-date', 'value'),
         State('modal-related-quote', 'value'),
         State('modal-order-status', 'value'),
         State('session-store', 'data')],
        prevent_initial_call=True
    )
    def save_sales_order(n_clicks, order_date, customer, delivery_date,
                        related_quote, status, session_data):
        """수주 저장"""
        if not all([order_date, customer, delivery_date]):
            return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 수주번호 생성
            cursor.execute("SELECT COUNT(*) FROM sales_orders WHERE order_date = ?", (order_date,))
            count = cursor.fetchone()[0]
            order_number = f"SO-{order_date.replace('-', '')}-{count+1:04d}"
            
            # 사용자 ID
            user_id = session_data.get('user_id', 1) if session_data else 1
            
            # 견적서에서 전환하는 경우 금액 가져오기
            total_amount = 0
            if related_quote != 'none':
                cursor.execute("SELECT total_amount FROM quotations WHERE quote_number = ?", (related_quote,))
                quote_result = cursor.fetchone()
                if quote_result:
                    total_amount = quote_result[0]
                    # 견적서 상태를 수주 확정으로 변경
                    cursor.execute("UPDATE quotations SET status = 'won' WHERE quote_number = ?", (related_quote,))
            
            # 수주 저장
            cursor.execute("""
                INSERT INTO sales_orders
                (order_number, order_date, customer_code, delivery_date,
                 total_amount, status, quote_number, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_number, order_date, customer, delivery_date,
                  total_amount, status, related_quote if related_quote != 'none' else None, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"수주 생성 완료: {order_number}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"),
                 f"수주 {order_number}가 생성되었습니다!"],
                color="success"
            )
            
        except Exception as e:
            logger.error(f"수주 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
    
    # 고객 저장
    @app.callback(
        Output('customer-modal-message', 'children'),
        Input('save-customer-btn', 'n_clicks'),
        [State('modal-customer-code', 'value'),
         State('modal-customer-name', 'value'),
         State('modal-customer-business-no', 'value'),
         State('modal-customer-ceo', 'value'),
         State('modal-customer-contact', 'value'),
         State('modal-customer-phone', 'value'),
         State('modal-customer-email', 'value'),
         State('modal-customer-address', 'value'),
         State('modal-customer-grade', 'value'),
         State('modal-customer-payment-terms', 'value')],
        prevent_initial_call=True
    )
    def save_customer(n_clicks, customer_code, customer_name, business_no,
                     ceo_name, contact_person, phone, email, address,
                     grade, payment_terms):
        """고객 저장"""
        if not all([customer_code, customer_name]):
            return dbc.Alert("고객 코드와 고객명은 필수입니다.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO customers
                (customer_code, customer_name, business_no, ceo_name,
                 contact_person, phone, email, address, grade,
                 payment_terms, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (customer_code, customer_name, business_no, ceo_name,
                  contact_person, phone, email, address, grade, payment_terms))
            
            conn.commit()
            conn.close()
            
            logger.info(f"고객 저장 완료: {customer_code}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "고객이 등록되었습니다!"],
                color="success"
            )
            
        except sqlite3.IntegrityError:
            return dbc.Alert("이미 존재하는 고객 코드입니다.", color="danger")
        except Exception as e:
            logger.error(f"고객 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
    
    # 영업관리 설정 저장
    @app.callback(
        Output('sales-settings-message', 'children'),
        Input('save-sales-settings-btn', 'n_clicks'),
        [State('quote-validity-days', 'value'),
         State('default-discount-rate', 'value'),
         State('auto-quote-number', 'value'),
         State('quote-template', 'value'),
         State('sales-notifications', 'value'),
         State('vip-threshold', 'value'),
         State('gold-threshold', 'value'),
         State('silver-threshold', 'value')],
        prevent_initial_call=True
    )
    def save_sales_settings(n_clicks, validity_days, discount_rate, auto_number,
                           template, notifications, vip_threshold, gold_threshold,
                           silver_threshold):
        """영업관리 설정 저장"""
        try:
            settings = {
                'quote': {
                    'validity_days': validity_days,
                    'default_discount_rate': discount_rate,
                    'auto_number': auto_number,
                    'template': template
                },
                'notifications': notifications,
                'customer_grades': {
                    'vip_threshold': vip_threshold,
                    'gold_threshold': gold_threshold,
                    'silver_threshold': silver_threshold
                }
            }
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('sales_settings', ?)
            """, (json.dumps(settings),))
            
            conn.commit()
            conn.close()
            
            logger.info("영업관리 설정 저장 완료")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "설정이 저장되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"영업관리 설정 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                color="danger",
                dismissable=True
            )
    
    # CRM 활동 업데이트
    @app.callback(
        [Output('today-activities', 'children'),
         Output('week-meetings', 'children'),
         Output('pending-followup', 'children'),
         Output('hot-leads', 'children'),
         Output('activity-list', 'children'),
         Output('opportunity-list', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_crm_dashboard(n):
        """CRM 대시보드 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            cursor = conn.cursor()
            
            # 오늘 활동
            cursor.execute("""
                SELECT COUNT(*) FROM sales_activities 
                WHERE activity_date = date('now')
            """)
            today_activities = cursor.fetchone()[0]
            
            # 이번주 미팅
            cursor.execute("""
                SELECT COUNT(*) FROM sales_activities 
                WHERE activity_type = 'meeting'
                AND activity_date BETWEEN date('now', 'weekday 0', '-6 days') 
                AND date('now', 'weekday 0')
            """)
            week_meetings = cursor.fetchone()[0]
            
            # 팔로업 대기 (더미 데이터)
            pending_followup = 5
            
            # Hot 리드 (더미 데이터)
            hot_leads = 3
            
            # 최근 활동 리스트
            activities = [
                dbc.Card([
                    dbc.CardBody([
                        html.H6("고객 미팅 - ABC(주)", className="mb-1"),
                        html.P("제품 데모 및 견적 논의", className="mb-1 small"),
                        html.P("2시간 전", className="text-muted small mb-0")
                    ])
                ], className="mb-2"),
                dbc.Card([
                    dbc.CardBody([
                        html.H6("견적서 발송 - XYZ 코퍼레이션", className="mb-1"),
                        html.P("QT-20250606-0001 발송 완료", className="mb-1 small"),
                        html.P("1일 전", className="text-muted small mb-0")
                    ])
                ], className="mb-2")
            ]
            
            # 영업 기회 리스트
            opportunities = [
                dbc.Card([
                    dbc.CardBody([
                        html.H6("신규 ERP 도입", className="mb-1"),
                        html.P("ABC(주) - ₩50,000,000", className="mb-1 small"),
                        dbc.Badge("Hot", color="danger", className="me-1"),
                        dbc.Badge("80%", color="success")
                    ])
                ], className="mb-2"),
                dbc.Card([
                    dbc.CardBody([
                        html.H6("설비 업그레이드", className="mb-1"),
                        html.P("DEF 산업 - ₩30,000,000", className="mb-1 small"),
                        dbc.Badge("Warm", color="warning", className="me-1"),
                        dbc.Badge("60%", color="info")
                    ])
                ], className="mb-2")
            ]
            
            return (
                f"{today_activities:,}",
                f"{week_meetings:,}",
                f"{pending_followup:,}",
                f"{hot_leads:,}",
                activities,
                opportunities
            )
            
        except Exception as e:
            logger.error(f"CRM 대시보드 조회 오류: {e}")
            return "0", "0", "0", "0", [], []
        finally:
            conn.close()
    
    # 월별 견적 추이 차트
    @app.callback(
        [Output('monthly-quote-trend', 'figure'),
         Output('quote-status-pie', 'figure')],
        Input('interval-component', 'n_intervals')
    )
    def update_quote_charts(n):
        """견적 관련 차트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            # 월별 견적 추이 (최근 6개월)
            trend_query = """
                SELECT strftime('%Y-%m', quote_date) as month,
                       COUNT(*) as quote_count,
                       SUM(total_amount) as total_amount
                FROM quotations
                WHERE quote_date >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', quote_date)
                ORDER BY month
            """
            trend_df = pd.read_sql_query(trend_query, conn)
            
            trend_fig = go.Figure()
            trend_fig.add_trace(go.Bar(
                x=trend_df['month'],
                y=trend_df['total_amount'],
                name='견적금액',
                marker_color='#0066cc',
                text=trend_df['total_amount'].apply(lambda x: f'₩{x:,.0f}'),
                textposition='auto'
            ))
            trend_fig.update_layout(
                title="월별 견적 금액 추이",
                xaxis_title="월",
                yaxis_title="견적금액 (원)"
            )
            
            # 견적 상태별 분포
            status_query = """
                SELECT status, COUNT(*) as count
                FROM quotations
                WHERE quote_date >= date('now', '-90 days')
                GROUP BY status
            """
            status_df = pd.read_sql_query(status_query, conn)
            
            status_labels = {
                'draft': '작성중',
                'sent': '발송완료',
                'reviewing': '고객검토',
                'won': '수주확정',
                'lost': '수주실패',
                'expired': '만료'
            }
            
            status_df['status_kr'] = status_df['status'].map(status_labels)
            
            status_fig = go.Figure()
            status_fig.add_trace(go.Pie(
                labels=status_df['status_kr'],
                values=status_df['count'],
                hole=0.4
            ))
            status_fig.update_layout(title="견적 상태별 분포 (최근 3개월)")
            
            return trend_fig, status_fig
            
        except Exception as e:
            logger.error(f"견적 차트 조회 오류: {e}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig
        finally:
            conn.close()
    
    # 매출 예측 차트
    @app.callback(
        Output('sales-forecast-chart', 'figure'),
        Input('sales-analysis-period', 'value')
    )
    def update_sales_forecast(period):
        """매출 예측 차트 (AI 기반 더미 데이터)"""
        # 실제 매출 데이터 (더미)
        months = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06']
        actual_sales = [150000000, 180000000, 165000000, 200000000, 175000000, 190000000]
        
        # 예측 데이터 (더미)
        forecast_months = ['2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12']
        forecast_sales = [210000000, 195000000, 220000000, 205000000, 230000000, 240000000]
        
        fig = go.Figure()
        
        # 실제 매출
        fig.add_trace(go.Scatter(
            x=months,
            y=actual_sales,
            mode='lines+markers',
            name='실제 매출',
            line=dict(color='#0066cc', width=3),
            marker=dict(size=8)
        ))
        
        # 예측 매출
        fig.add_trace(go.Scatter(
            x=forecast_months,
            y=forecast_sales,
            mode='lines+markers',
            name='예측 매출',
            line=dict(color='#ff6b6b', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        # 신뢰구간 (더미)
        upper_bound = [x * 1.1 for x in forecast_sales]
        lower_bound = [x * 0.9 for x in forecast_sales]
        
        fig.add_trace(go.Scatter(
            x=forecast_months + forecast_months[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(255, 107, 107, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='신뢰구간 (90%)'
        ))
        
        fig.update_layout(
            title="매출 예측 (AI 기반)",
            xaxis_title="월",
            yaxis_title="매출액 (원)",
            hovermode='x unified'
        )
        
        return fig
