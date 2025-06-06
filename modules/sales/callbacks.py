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
