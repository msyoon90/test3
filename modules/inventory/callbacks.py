# File: /modules/inventory/callbacks.py
# 재고관리 모듈 콜백 함수 - 전체 코드

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
import io
import base64

logger = logging.getLogger(__name__)

def register_inventory_callbacks(app):
    """재고관리 모듈 콜백 등록"""
    
    # 재고관리 탭 콘텐츠 렌더링
    @app.callback(
        Output('inventory-tab-content', 'children'),
        Input('inventory-tabs', 'active_tab')
    )
    def render_inventory_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_item_master, create_stock_inout, 
            create_stock_status, create_stock_adjust,
            create_inventory_settings
        )
        
        if active_tab == "item-master":
            return create_item_master()
        elif active_tab == "stock-inout":
            return create_stock_inout()
        elif active_tab == "stock-status":
            return create_stock_status()
        elif active_tab == "stock-adjust":
            return create_stock_adjust()
        elif active_tab == "inv-settings":
            return create_inventory_settings()
    
    # 품목 마스터 테이블 업데이트
    @app.callback(
        Output('item-master-table', 'children'),
        [Input('filter-items-btn', 'n_clicks'),
         Input('item-search', 'value'),
         Input('item-category', 'value')]
    )
    def update_item_master_table(n_clicks, search_value, category):
        """품목 마스터 테이블 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = "SELECT * FROM item_master WHERE 1=1"
        params = []
        
        if search_value:
            query += " AND (item_code LIKE ? OR item_name LIKE ?)"
            params.extend([f"%{search_value}%", f"%{search_value}%"])
        
        if category and category != "all":
            query += " AND category = ?"
            params.append(category)
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                return html.Div("등록된 품목이 없습니다.", className="text-center p-4")
            
            # 재고 상태 컬럼 추가
            df['stock_status'] = df.apply(
                lambda row: '부족' if row['current_stock'] < row['safety_stock'] 
                else '과잉' if row['current_stock'] > row['safety_stock'] * 2 
                else '정상', axis=1
            )
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("품목코드"),
                        html.Th("품목명"),
                        html.Th("분류"),
                        html.Th("단위"),
                        html.Th("안전재고"),
                        html.Th("현재고"),
                        html.Th("상태"),
                        html.Th("작업")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                status_badge = dbc.Badge(
                    row['stock_status'],
                    color="danger" if row['stock_status'] == '부족' 
                    else "warning" if row['stock_status'] == '과잉' 
                    else "success"
                )
                
                table_body.append(
                    html.Tr([
                        html.Td(row['item_code']),
                        html.Td(row['item_name']),
                        html.Td(row['category']),
                        html.Td(row['unit']),
                        html.Td(f"{row['safety_stock']:,}"),
                        html.Td(f"{row['current_stock']:,}"),
                        html.Td(status_badge),
                        html.Td([
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    id={"type": "edit-item", "index": row['item_code']},
                                    color="primary",
                                    size="sm"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-trash"),
                                    id={"type": "delete-item", "index": row['item_code']},
                                    color="danger",
                                    size="sm"
                                )
                            ])
                        ])
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
            logger.error(f"품목 조회 오류: {e}")
            return html.Div("품목 조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 입고용 품목 검색
    @app.callback(
        [Output('in-item-code', 'value'),
         Output('in-unit', 'value'),
         Output('in-item-display', 'children')],
        Input('search-in-item-btn', 'n_clicks'),
        State('in-item-search', 'value'),
        prevent_initial_call=True
    )
    def search_item_for_in(n_clicks, search_value):
        """입고용 품목 검색"""
        if not search_value:
            return "", "EA", dbc.Alert("품목을 검색하세요", color="warning")
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_code, item_name, unit, current_stock
            FROM item_master 
            WHERE item_code LIKE ? OR item_name LIKE ?
            LIMIT 1
        """, (f"%{search_value}%", f"%{search_value}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            display = dbc.Alert(
                [
                    html.B(f"{result[1]}"),
                    html.Br(),
                    f"현재고: {result[3]:,} {result[2]}"
                ],
                color="info"
            )
            return result[0], result[2], display
        
        return "", "EA", dbc.Alert("품목을 찾을 수 없습니다", color="danger")
    
    # 출고용 품목 검색
    @app.callback(
        [Output('out-item-code', 'value'),
         Output('out-unit', 'value'),
         Output('out-item-display', 'children')],
        Input('search-out-item-btn', 'n_clicks'),
        State('out-item-search', 'value'),
        prevent_initial_call=True
    )
    def search_item_for_out(n_clicks, search_value):
        """출고용 품목 검색"""
        if not search_value:
            return "", "EA", dbc.Alert("품목을 검색하세요", color="warning")
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_code, item_name, unit, current_stock
            FROM item_master 
            WHERE item_code LIKE ? OR item_name LIKE ?
            LIMIT 1
        """, (f"%{search_value}%", f"%{search_value}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            display = dbc.Alert(
                [
                    html.B(f"{result[1]}"),
                    html.Br(),
                    f"현재고: {result[3]:,} {result[2]}"
                ],
                color="info"
            )
            return result[0], result[2], display
        
        return "", "EA", dbc.Alert("품목을 찾을 수 없습니다", color="danger")
    
    # 입고 처리
    @app.callback(
        Output('in-message', 'children'),
        Input('save-in-btn', 'n_clicks'),
        [State('in-date', 'value'),
         State('in-type', 'value'),
         State('in-item-code', 'value'),
         State('in-qty', 'value'),
         State('in-warehouse', 'value'),
         State('in-remarks', 'value')],
        prevent_initial_call=True
    )
    def process_stock_in(n_clicks, in_date, in_type, item_code, qty, warehouse, remarks):
        """입고 처리"""
        if not all([in_date, in_type, item_code, qty, warehouse]):
            return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning", dismissable=True)
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 재고 이동 기록
            cursor.execute("""
                INSERT INTO stock_movements 
                (movement_date, movement_type, item_code, quantity, warehouse, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (in_date, f"IN_{in_type}", item_code, qty, warehouse, remarks))
            
            # 현재 재고 업데이트
            cursor.execute("""
                UPDATE item_master 
                SET current_stock = current_stock + ?
                WHERE item_code = ?
            """, (qty, item_code))
            
            conn.commit()
            conn.close()
            
            logger.info(f"입고 처리 완료: {item_code}, 수량: {qty}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "입고 처리가 완료되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"입고 처리 실패: {e}")
            return dbc.Alert(f"처리 중 오류가 발생했습니다: {str(e)}", color="danger", dismissable=True)
    
    # 출고 처리
    @app.callback(
        Output('out-message', 'children'),
        Input('save-out-btn', 'n_clicks'),
        [State('out-date', 'value'),
         State('out-type', 'value'),
         State('out-item-code', 'value'),
         State('out-qty', 'value'),
         State('out-warehouse', 'value'),
         State('out-remarks', 'value')],
        prevent_initial_call=True
    )
    def process_stock_out(n_clicks, out_date, out_type, item_code, qty, warehouse, remarks):
        """출고 처리"""
        if not all([out_date, out_type, item_code, qty, warehouse]):
            return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning", dismissable=True)
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 현재 재고 확인
            cursor.execute("SELECT current_stock FROM item_master WHERE item_code = ?", (item_code,))
            current_stock = cursor.fetchone()
            
            if not current_stock or current_stock[0] < qty:
                return dbc.Alert("재고가 부족합니다.", color="danger", dismissable=True)
            
            # 재고 이동 기록
            cursor.execute("""
                INSERT INTO stock_movements 
                (movement_date, movement_type, item_code, quantity, warehouse, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (out_date, f"OUT_{out_type}", item_code, -qty, warehouse, remarks))
            
            # 현재 재고 업데이트
            cursor.execute("""
                UPDATE item_master 
                SET current_stock = current_stock - ?
                WHERE item_code = ?
            """, (qty, item_code))
            
            conn.commit()
            conn.close()
            
            logger.info(f"출고 처리 완료: {item_code}, 수량: {qty}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "출고 처리가 완료되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"출고 처리 실패: {e}")
            return dbc.Alert(f"처리 중 오류가 발생했습니다: {str(e)}", color="danger", dismissable=True)
    
    # 입출고 이력 테이블 업데이트
    @app.callback(
        Output('inout-history-table', 'children'),
        [Input('refresh-inout-history', 'n_clicks'),
         Input('save-in-btn', 'n_clicks'),
         Input('save-out-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')]
    )
    def update_inout_history(refresh_clicks, in_clicks, out_clicks, n_intervals):
        """입출고 이력 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT 
                sm.movement_date,
                sm.movement_type,
                sm.item_code,
                im.item_name,
                sm.quantity,
                sm.warehouse,
                sm.remarks,
                sm.created_at
            FROM stock_movements sm
            JOIN item_master im ON sm.item_code = im.item_code
            ORDER BY sm.created_at DESC
            LIMIT 20
        """
        
        try:
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return html.Div("입출고 이력이 없습니다.", className="text-center p-4")
            
            # 타입 한글화 및 색상 설정
            type_mapping = {
                'IN_purchase': ('구매입고', 'success'),
                'IN_production': ('생산입고', 'success'),
                'IN_return': ('반품입고', 'info'),
                'IN_other': ('기타입고', 'secondary'),
                'OUT_production': ('생산출고', 'danger'),
                'OUT_sales': ('판매출고', 'danger'),
                'OUT_disposal': ('폐기출고', 'warning'),
                'OUT_other': ('기타출고', 'secondary')
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("일자"),
                        html.Th("구분"),
                        html.Th("품목코드"),
                        html.Th("품목명"),
                        html.Th("수량"),
                        html.Th("창고"),
                        html.Th("비고")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                type_info = type_mapping.get(row['movement_type'], ('기타', 'secondary'))
                type_badge = dbc.Badge(type_info[0], color=type_info[1])
                
                qty_display = f"{abs(row['quantity']):,}"
                if row['quantity'] < 0:
                    qty_display = f"-{qty_display}"
                
                table_body.append(
                    html.Tr([
                        html.Td(row['movement_date']),
                        html.Td(type_badge),
                        html.Td(row['item_code']),
                        html.Td(row['item_name']),
                        html.Td(qty_display, className="text-end"),
                        html.Td(row['warehouse']),
                        html.Td(row['remarks'] or '-')
                    ])
                )
            
            return dbc.Table(
                table_header + [html.Tbody(table_body)],
                striped=True,
                bordered=True,
                hover=True,
                responsive=True,
                size="sm"
            )
            
        except Exception as e:
            logger.error(f"입출고 이력 조회 오류: {e}")
            return html.Div("이력 조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # 재고 현황 업데이트
    @app.callback(
        [Output('total-items', 'children'),
         Output('total-stock-value', 'children'),
         Output('shortage-items', 'children'),
         Output('excess-items', 'children'),
         Output('stock-status-table', 'children'),
         Output('stock-trend-chart', 'figure'),
         Output('warehouse-stock-chart', 'figure')],
        [Input('search-stock-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')],
        [State('stock-warehouse-filter', 'value'),
         State('stock-status-filter', 'value')]
    )
    def update_stock_status(n_clicks, n_intervals, warehouse, status_filter):
        """재고 현황 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            # 전체 품목 수
            total_items_query = "SELECT COUNT(DISTINCT item_code) FROM item_master"
            total_items = pd.read_sql_query(total_items_query, conn).iloc[0, 0]
            
            # 총 재고금액
            total_value_query = "SELECT SUM(current_stock * unit_price) FROM item_master"
            total_value = pd.read_sql_query(total_value_query, conn).iloc[0, 0] or 0
            
            # 부족/과잉 품목
            shortage_query = "SELECT COUNT(*) FROM item_master WHERE current_stock < safety_stock"
            shortage_items = pd.read_sql_query(shortage_query, conn).iloc[0, 0]
            
            excess_query = "SELECT COUNT(*) FROM item_master WHERE current_stock > safety_stock * 2"
            excess_items = pd.read_sql_query(excess_query, conn).iloc[0, 0]
            
            # 재고 테이블
            stock_query = """
                SELECT item_code, item_name, category, unit, 
                       current_stock, safety_stock, unit_price,
                       current_stock * unit_price as stock_value,
                       CASE 
                           WHEN current_stock < safety_stock THEN '부족'
                           WHEN current_stock > safety_stock * 2 THEN '과잉'
                           ELSE '정상'
                       END as status
                FROM item_master
                WHERE 1=1
            """
            
            if status_filter and status_filter != 'all':
                if status_filter == 'shortage':
                    stock_query += " AND current_stock < safety_stock"
                elif status_filter == 'excess':
                    stock_query += " AND current_stock > safety_stock * 2"
                elif status_filter == 'normal':
                    stock_query += " AND current_stock >= safety_stock AND current_stock <= safety_stock * 2"
            
            stock_df = pd.read_sql_query(stock_query, conn)
            
            # 테이블 생성
            if not stock_df.empty:
                table_header = [
                    html.Thead([
                        html.Tr([
                            html.Th("품목코드"),
                            html.Th("품목명"),
                            html.Th("분류"),
                            html.Th("현재고"),
                            html.Th("안전재고"),
                            html.Th("상태"),
                            html.Th("재고금액")
                        ])
                    ])
                ]
                
                table_body = []
                for idx, row in stock_df.iterrows():
                    status_color = "danger" if row['status'] == '부족' else "warning" if row['status'] == '과잉' else "success"
                    status_badge = dbc.Badge(row['status'], color=status_color)
                    
                    # 재고 비율 표시
                    stock_ratio = (row['current_stock'] / row['safety_stock'] * 100) if row['safety_stock'] > 0 else 0
                    
                    table_body.append(
                        html.Tr([
                            html.Td(row['item_code']),
                            html.Td(row['item_name']),
                            html.Td(row['category']),
                            html.Td(f"{row['current_stock']:,} {row['unit']}"),
                            html.Td(f"{row['safety_stock']:,} {row['unit']}"),
                            html.Td([
                                status_badge,
                                html.Small(f" ({stock_ratio:.0f}%)", className="text-muted ms-1")
                            ]),
                            html.Td(f"₩{row['stock_value']:,.0f}", className="text-end")
                        ])
                    )
                
                stock_table = dbc.Table(
                    table_header + [html.Tbody(table_body)],
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True
                )
            else:
                stock_table = html.Div("재고 데이터가 없습니다.", className="text-center p-4")
            
            # 재고 추이 차트 (최근 30일)
            trend_query = """
                SELECT 
                    movement_date,
                    SUM(CASE WHEN quantity > 0 THEN quantity ELSE 0 END) as in_qty,
                    SUM(CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END) as out_qty
                FROM stock_movements
                WHERE movement_date >= date('now', '-30 days')
                GROUP BY movement_date
                ORDER BY movement_date
            """
            trend_df = pd.read_sql_query(trend_query, conn)
            
            trend_fig = go.Figure()
            if not trend_df.empty:
                # 입고 추이
                trend_fig.add_trace(go.Scatter(
                    x=trend_df['movement_date'],
                    y=trend_df['in_qty'],
                    mode='lines+markers',
                    name='입고',
                    line=dict(color='#28a745', width=3),
                    fill='tozeroy'
                ))
                # 출고 추이
                trend_fig.add_trace(go.Scatter(
                    x=trend_df['movement_date'],
                    y=trend_df['out_qty'],
                    mode='lines+markers',
                    name='출고',
                    line=dict(color='#dc3545', width=3),
                    fill='tozeroy'
                ))
                
                trend_fig.update_layout(
                    title="최근 30일 입출고 추이",
                    xaxis_title="날짜",
                    yaxis_title="수량",
                    hovermode='x unified',
                    showlegend=True
                )
            else:
                trend_fig.add_annotation(
                    text="데이터가 없습니다",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                trend_fig.update_layout(title="최근 30일 입출고 추이")
            
            # 창고별 재고 차트 (실제 데이터가 있다면)
            warehouse_query = """
                SELECT 
                    '창고1' as warehouse,
                    SUM(CASE WHEN warehouse = 'wh1' THEN quantity ELSE 0 END) as stock
                FROM stock_movements
                UNION ALL
                SELECT 
                    '창고2' as warehouse,
                    SUM(CASE WHEN warehouse = 'wh2' THEN quantity ELSE 0 END) as stock
                FROM stock_movements
            """
            warehouse_df = pd.read_sql_query(warehouse_query, conn)
            
            warehouse_fig = go.Figure()
            warehouse_fig.add_trace(go.Bar(
                x=warehouse_df['warehouse'],
                y=warehouse_df['stock'],
                marker_color=['#0066cc', '#17a2b8'],
                text=warehouse_df['stock'],
                textposition='auto'
            ))
            warehouse_fig.update_layout(
                title="창고별 재고 현황",
                xaxis_title="창고",
                yaxis_title="재고량",
                showlegend=False
            )
            
            return (
                f"{total_items:,}",
                f"₩{total_value:,.0f}",
                f"{shortage_items:,}",
                f"{excess_items:,}",
                stock_table,
                trend_fig,
                warehouse_fig
            )
            
        except Exception as e:
            logger.error(f"재고 현황 조회 실패: {e}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="오류가 발생했습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return "0", "₩0", "0", "0", "오류가 발생했습니다.", empty_fig, empty_fig
        
        finally:
            conn.close()
    
    # 재고 조정용 품목 검색
    @app.callback(
        [Output('adjust-item-code', 'value'),
         Output('current-stock', 'value'),
         Output('adjust-item-display', 'children')],
        Input('search-adjust-item-btn', 'n_clicks'),
        State('adjust-item-search', 'value'),
        prevent_initial_call=True
    )
    def search_item_for_adjust(n_clicks, search_value):
        """재고 조정용 품목 검색"""
        if not search_value:
            return "", 0, dbc.Alert("품목을 검색하세요", color="warning")
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_code, item_name, unit, current_stock
            FROM item_master 
            WHERE item_code LIKE ? OR item_name LIKE ?
            LIMIT 1
        """, (f"%{search_value}%", f"%{search_value}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            display = dbc.Alert(
                [
                    html.B(f"{result[1]}"),
                    html.Br(),
                    f"현재고: {result[3]:,} {result[2]}"
                ],
                color="info"
            )
            return result[0], result[3], display
        
        return "", 0, dbc.Alert("품목을 찾을 수 없습니다", color="danger")
    
    # 재고 조정 처리
    @app.callback(
        [Output('adjust-diff', 'value'),
         Output('adjust-message', 'children')],
        [Input('adjusted-stock', 'value'),
         Input('save-adjust-btn', 'n_clicks')],
        [State('current-stock', 'value'),
         State('adjust-date', 'value'),
         State('adjust-type', 'value'),
         State('adjust-item-code', 'value'),
         State('adjust-reason', 'value')],
        prevent_initial_call=True
    )
    def process_stock_adjust(adjusted_stock, n_clicks, current_stock, 
                           adjust_date, adjust_type, item_code, reason):
        """재고 조정 처리"""
        ctx = callback_context
        
        # 차이 계산
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'adjusted-stock':
            if adjusted_stock is not None and current_stock is not None:
                diff = adjusted_stock - current_stock
                return diff, dash.no_update
            return 0, dash.no_update
        
        # 저장 처리
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'save-adjust-btn':
            if not all([adjust_date, adjust_type, item_code, adjusted_stock is not None, reason]):
                return dash.no_update, dbc.Alert("모든 필수 항목을 입력하세요.", color="warning")
            
            try:
                conn = sqlite3.connect('data/database.db')
                cursor = conn.cursor()
                
                diff = adjusted_stock - current_stock
                
                # 조정 기록
                cursor.execute("""
                    INSERT INTO stock_adjustments
                    (adjustment_date, item_code, adjustment_type, 
                     before_qty, after_qty, difference, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (adjust_date, item_code, adjust_type, 
                      current_stock, adjusted_stock, diff, reason))
                
                # 재고 업데이트
                cursor.execute("""
                    UPDATE item_master 
                    SET current_stock = ?
                    WHERE item_code = ?
                """, (adjusted_stock, item_code))
                
                # 재고 이동 기록에도 추가
                cursor.execute("""
                    INSERT INTO stock_movements
                    (movement_date, movement_type, item_code, quantity, warehouse, remarks)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (adjust_date, f"ADJUST_{adjust_type}", item_code, diff, 'wh1', f"재고조정: {reason}"))
                
                conn.commit()
                conn.close()
                
                logger.info(f"재고 조정 완료: {item_code}, 차이: {diff}")
                
                return dash.no_update, dbc.Alert(
                    [html.I(className="fas fa-check-circle me-2"), "재고 조정이 완료되었습니다!"],
                    color="success",
                    dismissable=True
                )
                
            except Exception as e:
                logger.error(f"재고 조정 실패: {e}")
                return dash.no_update, dbc.Alert(
                    f"처리 중 오류가 발생했습니다: {str(e)}", 
                    color="danger", 
                    dismissable=True
                )
        
        return dash.no_update, dash.no_update
    
    # 조정 이력 테이블 업데이트
    @app.callback(
        Output('adjust-history-table', 'children'),
        [Input('save-adjust-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')]
    )
    def update_adjust_history(n_clicks, n_intervals):
        """조정 이력 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT 
                sa.adjustment_date,
                sa.item_code,
                im.item_name,
                sa.adjustment_type,
                sa.before_qty,
                sa.after_qty,
                sa.difference,
                sa.reason,
                sa.created_at
            FROM stock_adjustments sa
            JOIN item_master im ON sa.item_code = im.item_code
            ORDER BY sa.created_at DESC
            LIMIT 10
        """
        
        try:
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return html.Div("조정 이력이 없습니다.", className="text-center p-4")
            
            # 조정 유형 한글화
            type_mapping = {
                'inventory': '실사조정',
                'loss': '손실처리',
                'system': '시스템오류',
                'other': '기타'
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("조정일"),
                        html.Th("품목"),
                        html.Th("유형"),
                        html.Th("조정 전"),
                        html.Th("조정 후"),
                        html.Th("차이"),
                        html.Th("사유")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                adjust_type = type_mapping.get(row['adjustment_type'], row['adjustment_type'])
                
                # 차이 표시 (증가는 파란색, 감소는 빨간색)
                diff_color = "text-primary" if row['difference'] > 0 else "text-danger" if row['difference'] < 0 else ""
                diff_display = f"{row['difference']:+,}" if row['difference'] != 0 else "0"
                
                table_body.append(
                    html.Tr([
                        html.Td(row['adjustment_date']),
                        html.Td(f"{row['item_code']} - {row['item_name']}"),
                        html.Td(adjust_type),
                        html.Td(f"{row['before_qty']:,}"),
                        html.Td(f"{row['after_qty']:,}"),
                        html.Td(diff_display, className=diff_color),
                        html.Td(row['reason'])
                    ])
                )
            
            return dbc.Table(
                table_header + [html.Tbody(table_body)],
                striped=True,
                bordered=True,
                hover=True,
                responsive=True,
                size="sm"
            )
            
        except Exception as e:
            logger.error(f"조정 이력 조회 오류: {e}")
            return html.Div("이력 조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()
    
    # Excel 다운로드
    @app.callback(
        Output('download-dataframe-xlsx', 'data'),
        Input('export-stock-excel', 'n_clicks'),
        prevent_initial_call=True
    )
    def export_stock_to_excel(n_clicks):
        """재고 현황 Excel 다운로드"""
        conn = sqlite3.connect('data/database.db')
        
        query = """
            SELECT 
                item_code as '품목코드',
                item_name as '품목명',
                category as '분류',
                unit as '단위',
                current_stock as '현재고',
                safety_stock as '안전재고',
                unit_price as '단가',
                current_stock * unit_price as '재고금액',
                CASE 
                    WHEN current_stock < safety_stock THEN '부족'
                    WHEN current_stock > safety_stock * 2 THEN '과잉'
                    ELSE '정상'
                END as '재고상태'
            FROM item_master
            ORDER BY item_code
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Excel 파일명
        filename = f"재고현황_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return dcc.send_data_frame(df.to_excel, filename, index=False)
    
    # 재고 설정 저장
    @app.callback(
        Output('inv-settings-message', 'children'),
        Input('save-inv-settings-btn', 'n_clicks'),
        [State('safety-stock-ratio', 'value'),
         State('alert-criteria', 'value'),
         State('valuation-method', 'value'),
         State('barcode-options', 'value')],
        prevent_initial_call=True
    )
    def save_inventory_settings(n_clicks, safety_ratio, alert_criteria, 
                              valuation_method, barcode_options):
        """재고 설정 저장"""
        try:
            settings = {
                'safety_stock_ratio': safety_ratio,
                'alert_criteria': alert_criteria,
                'valuation_method': valuation_method,
                'barcode_options': barcode_options
            }
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('inventory_settings', ?)
            """, (json.dumps(settings),))
            
            conn.commit()
            conn.close()
            
            logger.info("재고 설정 저장 완료")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "설정이 저장되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"재고 설정 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                color="danger",
                dismissable=True
            )
    
    # 품목 추가 모달 토글
    @app.callback(
        Output('item-modal', 'is_open'),
        [Input('add-item-btn', 'n_clicks'),
         Input('close-item-modal', 'n_clicks'),
         Input('save-item-btn', 'n_clicks')],
        [State('item-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_item_modal(n1, n2, n3, is_open):
        """품목 추가 모달 토글"""
        if n1 or n2 or n3:
            return not is_open
        return is_open
    
    # 품목 저장
    @app.callback(
        Output('item-modal-message', 'children'),
        Input('save-item-btn', 'n_clicks'),
        [State('modal-item-code', 'value'),
         State('modal-item-name', 'value'),
         State('modal-category', 'value'),
         State('modal-unit', 'value'),
         State('modal-safety-stock', 'value'),
         State('modal-unit-price', 'value')],
        prevent_initial_call=True
    )
    def save_item(n_clicks, item_code, item_name, category, unit, safety_stock, unit_price):
        """품목 저장"""
        if not all([item_code, item_name, category, unit]):
            return dbc.Alert("필수 항목을 모두 입력하세요.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO item_master 
                (item_code, item_name, category, unit, safety_stock, current_stock, unit_price)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (item_code, item_name, category, unit, safety_stock or 0, unit_price or 0))
            
            conn.commit()
            conn.close()
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "품목이 등록되었습니다!"],
                color="success"
            )
            
        except sqlite3.IntegrityError:
            return dbc.Alert("이미 존재하는 품목코드입니다.", color="danger")
        except Exception as e:
            logger.error(f"품목 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
