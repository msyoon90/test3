# File: /modules/accounting/callbacks.py

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

def register_accounting_callbacks(app):
    """회계관리 모듈 콜백 등록"""
    
    # 탭 콘텐츠 렌더링
    @app.callback(
        Output('accounting-tab-content', 'children'),
        Input('accounting-tabs', 'active_tab')
    )
    def render_accounting_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_voucher_management, create_sales_purchase,
            create_financial_statements, create_cost_management,
            create_budget_management, create_fixed_assets,
            create_accounting_analysis, create_accounting_settings
        )
        
        if active_tab == "voucher-management":
            return create_voucher_management()
        elif active_tab == "sales-purchase":
            return create_sales_purchase()
        elif active_tab == "financial-statements":
            return create_financial_statements()
        elif active_tab == "cost-management":
            return create_cost_management()
        elif active_tab == "budget-management":
            return create_budget_management()
        elif active_tab == "fixed-assets":
            return create_fixed_assets()
        elif active_tab == "accounting-analysis":
            return create_accounting_analysis()
        elif active_tab == "accounting-settings":
            return create_accounting_settings()
    
    # 전표 현황 업데이트
    @app.callback(
        [Output('today-vouchers', 'children'),
         Output('pending-vouchers', 'children'),
         Output('unbalanced-vouchers', 'children'),
         Output('monthly-vouchers', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_voucher_summary(n):
        """전표 현황 요약 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            # 오늘 전표
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM journal_header 
                WHERE voucher_date = ?
            """, (today,))
            today_count = cursor.fetchone()[0]
            
            # 승인 대기
            cursor.execute("""
                SELECT COUNT(*) FROM journal_header 
                WHERE status = 'pending'
            """)
            pending_count = cursor.fetchone()[0]
            
            # 차대 불일치 (실제로는 상세 테이블과 조인 필요)
            cursor.execute("""
                SELECT COUNT(*) FROM journal_header 
                WHERE total_debit != total_credit
            """)
            unbalanced_count = cursor.fetchone()[0]
            
            # 이번달 전표
            cursor.execute("""
                SELECT COUNT(*) FROM journal_header 
                WHERE voucher_date >= ?
            """, (month_start,))
            monthly_count = cursor.fetchone()[0]
            
            return (
                f"{today_count:,}",
                f"{pending_count:,}",
                f"{unbalanced_count:,}",
                f"{monthly_count:,}"
            )
            
        except Exception as e:
            logger.error(f"전표 현황 조회 오류: {e}")
            return "0", "0", "0", "0"
        finally:
            conn.close()
    
    # 전표 리스트 조회
    @app.callback(
        Output('voucher-list-table', 'children'),
        [Input('search-voucher-btn', 'n_clicks')],
        [State('voucher-start-date', 'value'),
         State('voucher-end-date', 'value'),
         State('voucher-type-filter', 'value'),
         State('voucher-status-filter', 'value')]
    )
    def update_voucher_list(n_clicks, start_date, end_date, v_type, status):
        """전표 리스트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT 
                voucher_no,
                voucher_date,
                voucher_type,
                description,
                total_debit,
                total_credit,
                status,
                created_at
            FROM journal_header
            WHERE voucher_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if v_type != 'all':
            query += " AND voucher_type = ?"
            params.append(v_type)
        
        if status != 'all':
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY voucher_date DESC, voucher_no DESC"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                return html.Div("전표가 없습니다.", className="text-center p-4")
            
            # 전표 유형 한글화
            type_mapping = {
                'receipt': '입금',
                'payment': '출금',
                'transfer': '대체',
                'sales': '매출',
                'purchase': '매입'
            }
            
            # 상태 한글화
            status_mapping = {
                'draft': ('작성중', 'secondary'),
                'pending': ('승인대기', 'warning'),
                'approved': ('승인완료', 'success'),
                'cancelled': ('취소', 'danger')
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("전표번호"),
                        html.Th("전표일자"),
                        html.Th("유형"),
                        html.Th("적요"),
                        html.Th("차변"),
                        html.Th("대변"),
                        html.Th("상태"),
                        html.Th("작업")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                v_type_kr = type_mapping.get(row['voucher_type'], row['voucher_type'])
                status_info = status_mapping.get(row['status'], ('알수없음', 'secondary'))
                
                # 차대 일치 여부
                balance_check = ""
                if row['total_debit'] != row['total_credit']:
                    balance_check = dbc.Badge("불일치", color="danger", className="ms-1")
                
                table_body.append(
                    html.Tr([
                        html.Td(row['voucher_no']),
                        html.Td(row['voucher_date']),
                        html.Td(v_type_kr),
                        html.Td(row['description'] or '-'),
                        html.Td(f"₩{row['total_debit']:,.0f}"),
                        html.Td(f"₩{row['total_credit']:,.0f}"),
                        html.Td([
                            dbc.Badge(status_info[0], color=status_info[1]),
                            balance_check
                        ]),
                        html.Td(
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-eye"),
                                    id={"type": "view-voucher", "index": row['voucher_no']},
                                    color="info",
                                    size="sm"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    id={"type": "edit-voucher", "index": row['voucher_no']},
                                    color="primary",
                                    size="sm",
                                    disabled=row['status'] != 'draft'
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-check"),
                                    id={"type": "approve-voucher", "index": row['voucher_no']},
                                    color="success",
                                    size="sm",
                                    disabled=row['status'] != 'pending'
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
            logger.error(f"전표 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 매출/매입 현황 업데이트 - ID 변경
    @app.callback(
        [Output('accounting-monthly-sales', 'children'),
         Output('accounting-monthly-purchase', 'children'),
         Output('accounting-gross-profit', 'children'),
         Output('accounting-vat-amount', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_sales_purchase_summary(n):
        """매출/매입 현황 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            # 이번달 매출
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(supply_amount), 0)
                FROM tax_invoice
                WHERE invoice_type = 'sales'
                AND invoice_date >= ?
            """, (month_start,))
            monthly_sales = cursor.fetchone()[0]
            
            # 이번달 매입
            cursor.execute("""
                SELECT COALESCE(SUM(supply_amount), 0)
                FROM tax_invoice
                WHERE invoice_type = 'purchase'
                AND invoice_date >= ?
            """, (month_start,))
            monthly_purchase = cursor.fetchone()[0]
            
            # 매출총이익
            gross_profit = monthly_sales - monthly_purchase
            profit_rate = (gross_profit / monthly_sales * 100) if monthly_sales > 0 else 0
            
            # 부가세
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN invoice_type = 'sales' 
                        THEN tax_amount ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN invoice_type = 'purchase' 
                        THEN tax_amount ELSE 0 END), 0)
                FROM tax_invoice
                WHERE invoice_date >= ?
            """, (month_start,))
            vat_amount = cursor.fetchone()[0]
            
            return (
                f"₩{monthly_sales:,.0f}",
                f"₩{monthly_purchase:,.0f}",
                f"₩{gross_profit:,.0f}",
                f"₩{vat_amount:,.0f}"
            )
            
        except Exception as e:
            logger.error(f"매출/매입 현황 조회 오류: {e}")
            return "₩0", "₩0", "₩0", "₩0"
        finally:
            conn.close()
    
    # 전표 모달 토글
    @app.callback(
        Output('voucher-modal', 'is_open'),
        [Input('new-general-voucher-btn', 'n_clicks'),
         Input('new-sales-voucher-btn', 'n_clicks'),
         Input('new-purchase-voucher-btn', 'n_clicks'),
         Input('close-voucher-modal', 'n_clicks'),
         Input('save-voucher-btn', 'n_clicks')],
        [State('voucher-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_voucher_modal(n1, n2, n3, n4, n5, is_open):
        """전표 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 세금계산서 모달 토글
    @app.callback(
        Output('tax-invoice-modal', 'is_open'),
        [Input('new-tax-invoice-btn', 'n_clicks'),
         Input('close-invoice-modal', 'n_clicks'),
         Input('issue-invoice-btn', 'n_clicks')],
        [State('tax-invoice-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_invoice_modal(n1, n2, n3, is_open):
        """세금계산서 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 전표 저장
    @app.callback(
        Output('voucher-modal-message', 'children'),
        Input('save-voucher-btn', 'n_clicks'),
        [State('modal-voucher-date', 'value'),
         State('modal-voucher-type', 'value'),
         State('modal-voucher-desc', 'value'),
         State('session-store', 'data')],
        prevent_initial_call=True
    )
    def save_voucher(n_clicks, v_date, v_type, desc, session_data):
        """전표 저장"""
        if not all([v_date, v_type]):
            return dbc.Alert("필수 항목을 입력하세요.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 전표번호 생성
            cursor.execute("""
                SELECT COUNT(*) FROM journal_header 
                WHERE voucher_date = ?
            """, (v_date,))
            count = cursor.fetchone()[0]
            voucher_no = f"JV-{v_date.replace('-', '')}-{count+1:04d}"
            
            # 사용자 ID
            user_id = session_data.get('user_id', 1) if session_data else 1
            
            # 전표 헤더 저장
            cursor.execute("""
                INSERT INTO journal_header
                (voucher_no, voucher_date, voucher_type, description,
                 total_debit, total_credit, status, created_by)
                VALUES (?, ?, ?, ?, 0, 0, 'draft', ?)
            """, (voucher_no, v_date, v_type, desc, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"전표 생성 완료: {voucher_no}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"),
                 f"전표 {voucher_no}가 생성되었습니다!"],
                color="success"
            )
            
        except Exception as e:
            logger.error(f"전표 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
    
    # 회계 설정 저장
    @app.callback(
        Output('acc-settings-message', 'children'),
        Input('save-acc-settings-btn', 'n_clicks'),
        [State('fiscal-year-start', 'value'),
         State('depreciation-method', 'value'),
         State('vat-period', 'value'),
         State('e-tax-invoice', 'value'),
         State('voucher-approval-auth', 'value')],
        prevent_initial_call=True
    )
    def save_accounting_settings(n_clicks, fiscal_start, dep_method, 
                               vat_period, e_tax, approval_auth):
        """회계 설정 저장"""
        try:
            settings = {
                'fiscal': {
                    'year_start': fiscal_start,
                    'depreciation_method': dep_method
                },
                'tax': {
                    'vat_period': vat_period,
                    'e_tax_invoice': e_tax
                },
                'auth': {
                    'voucher_approval': approval_auth
                }
            }
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('accounting_settings', ?)
            """, (json.dumps(settings),))
            
            conn.commit()
            conn.close()
            
            logger.info("회계 설정 저장 완료")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "설정이 저장되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"회계 설정 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                color="danger",
                dismissable=True
            )
