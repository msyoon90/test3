# File: /modules/purchase/callbacks.py

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


def register_purchase_callbacks(app):
    """구매관리 모듈 콜백 등록"""

    # 탭 콘텐츠 렌더링
    @app.callback(
        Output('purchase-tab-content', 'children'),
        Input('purchase-tabs', 'active_tab')
    )
    def render_purchase_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_po_management, create_receiving,
            create_supplier_management, create_purchase_analysis,
            create_purchase_settings
        )

        if active_tab == "po-management":
            return create_po_management()
        elif active_tab == "receiving":
            return create_receiving()
        elif active_tab == "supplier":
            return create_supplier_management()
        elif active_tab == "purchase-analysis":
            return create_purchase_analysis()
        elif active_tab == "purchase-settings":
            return create_purchase_settings()

    # 발주 현황 업데이트
    @app.callback(
        [Output('active-po-count', 'children'),
         Output('pending-delivery', 'children'),
         Output('urgent-po', 'children'),
         Output('monthly-purchase', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_po_summary(n):
        """발주 현황 요약 업데이트"""
        conn = sqlite3.connect('data/database.db')

        try:
            # 진행중 발주
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM purchase_orders
                           WHERE status IN ('draft', 'pending', 'approved', 'receiving')
                           """)
            active_po = cursor.fetchone()[0]

            # 입고 대기
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM receiving_schedule
                           WHERE status = 'pending'
                             AND scheduled_date >= date ('now')
                           """)
            pending = cursor.fetchone()[0]

            # 긴급 발주 (안전재고 미만 품목)
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM item_master
                           WHERE current_stock < safety_stock
                           """)
            urgent = cursor.fetchone()[0]

            # 이번달 구매액
            cursor.execute("""
                           SELECT COALESCE(SUM(total_amount), 0)
                           FROM purchase_orders
                           WHERE strftime('%Y-%m', po_date) = strftime('%Y-%m', 'now')
                           """)
            monthly = cursor.fetchone()[0]

            return (
                f"{active_po:,}",
                f"{pending:,}",
                f"{urgent:,}",
                f"₩{monthly:,.0f}"
            )

        except Exception as e:
            logger.error(f"발주 현황 조회 오류: {e}")
            return "0", "0", "0", "₩0"
        finally:
            conn.close()

    # 발주서 리스트 조회
    @app.callback(
        Output('po-list-table', 'children'),
        [Input('search-po-btn', 'n_clicks'),
         Input('new-po-btn', 'n_clicks')],
        [State('po-start-date', 'value'),
         State('po-end-date', 'value'),
         State('po-status-filter', 'value'),
         State('po-supplier-filter', 'value')]
    )
    def update_po_list(search_clicks, new_clicks, start_date, end_date, status, supplier):
        """발주서 리스트 업데이트"""
        conn = sqlite3.connect('data/database.db')

        query = """
                SELECT po.po_number, \
                       po.po_date, \
                       s.supplier_name, \
                       po.total_amount, \
                       po.status, \
                       po.delivery_date, \
                       u.username as created_by
                FROM purchase_orders po
                         LEFT JOIN supplier_master s ON po.supplier_code = s.supplier_code
                         LEFT JOIN users u ON po.created_by = u.id
                WHERE po.po_date BETWEEN ? AND ? \
                """
        params = [start_date, end_date]

        if status != 'all':
            query += " AND po.status = ?"
            params.append(status)

        if supplier != 'all':
            query += " AND po.supplier_code = ?"
            params.append(supplier)

        query += " ORDER BY po.po_date DESC, po.created_at DESC"

        try:
            df = pd.read_sql_query(query, conn, params=params)

            if df.empty:
                return html.Div("발주서가 없습니다.", className="text-center p-4")

            # 상태 한글화 및 색상
            status_mapping = {
                'draft': ('작성중', 'secondary'),
                'pending': ('승인대기', 'warning'),
                'approved': ('승인완료', 'success'),
                'receiving': ('입고중', 'info'),
                'completed': ('완료', 'primary'),
                'cancelled': ('취소', 'danger')
            }

            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("발주번호"),
                        html.Th("발주일"),
                        html.Th("거래처"),
                        html.Th("금액"),
                        html.Th("상태"),
                        html.Th("납기일"),
                        html.Th("작성자"),
                        html.Th("작업")
                    ])
                ])
            ]

            table_body = []
            for idx, row in df.iterrows():
                status_info = status_mapping.get(row['status'], ('알 수 없음', 'secondary'))
                status_badge = dbc.Badge(status_info[0], color=status_info[1])

                # 납기일 임박 체크
                if row['delivery_date'] and row['status'] in ['approved', 'receiving']:
                    delivery_date = datetime.strptime(row['delivery_date'], '%Y-%m-%d')
                    days_left = (delivery_date - datetime.now()).days
                    if days_left <= 2:
                        delivery_display = html.Span([
                            row['delivery_date'],
                            dbc.Badge(f"D-{days_left}", color="danger", className="ms-1")
                        ])
                    else:
                        delivery_display = row['delivery_date']
                else:
                    delivery_display = row['delivery_date'] or '-'

                table_body.append(
                    html.Tr([
                        html.Td(
                            html.A(
                                row['po_number'],
                                href="#",
                                id={"type": "po-link", "index": row['po_number']}
                            )
                        ),
                        html.Td(row['po_date']),
                        html.Td(row['supplier_name']),
                        html.Td(f"₩{row['total_amount']:,.0f}"),
                        html.Td(status_badge),
                        html.Td(delivery_display),
                        html.Td(row['created_by']),
                        html.Td(
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-eye"),
                                    id={"type": "view-po", "index": row['po_number']},
                                    color="info",
                                    size="sm",
                                    title="보기"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    id={"type": "edit-po", "index": row['po_number']},
                                    color="primary",
                                    size="sm",
                                    title="수정",
                                    disabled=row['status'] not in ['draft', 'pending']
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-trash"),
                                    id={"type": "delete-po", "index": row['po_number']},
                                    color="danger",
                                    size="sm",
                                    title="삭제",
                                    disabled=row['status'] not in ['draft']
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
            logger.error(f"발주서 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()

    # 자동 발주 제안
    @app.callback(
        Output('auto-po-suggestions', 'children'),
        [Input('auto-po-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')]
    )
    def update_auto_po_suggestions(n_clicks, n_intervals):
        """자동 발주 제안 업데이트"""
        conn = sqlite3.connect('data/database.db')

        try:
            # 발주가 필요한 품목 조회
            query = """
                    SELECT im.item_code, \
                           im.item_name, \
                           im.current_stock, \
                           im.safety_stock, \
                           im.unit, \
                           apr.supplier_code, \
                           sm.supplier_name, \
                           apr.order_qty, \
                           im.unit_price, \
                           sm.lead_time
                    FROM item_master im
                             LEFT JOIN auto_po_rules apr ON im.item_code = apr.item_code AND apr.is_active = 1
                             LEFT JOIN supplier_master sm ON apr.supplier_code = sm.supplier_code
                    WHERE im.current_stock < im.safety_stock
                    ORDER BY (im.safety_stock - im.current_stock) DESC LIMIT 10 \
                    """

            df = pd.read_sql_query(query, conn)

            if df.empty:
                return dbc.Alert(
                    "현재 자동 발주가 필요한 품목이 없습니다.",
                    color="info"
                )

            # 제안 카드 생성
            suggestions = []
            total_amount = 0

            for idx, row in df.iterrows():
                shortage = row['safety_stock'] - row['current_stock']
                order_qty = row['order_qty'] or shortage
                amount = order_qty * row['unit_price']
                total_amount += amount

                card = dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6(f"{row['item_code']} - {row['item_name']}"),
                                html.P([
                                    f"현재고: {row['current_stock']} / ",
                                    f"안전재고: {row['safety_stock']} ",
                                    dbc.Badge(f"부족: {shortage}", color="danger", className="ms-1")
                                ], className="mb-1"),
                                html.P([
                                    f"거래처: {row['supplier_name'] or '미지정'} | ",
                                    f"리드타임: {row['lead_time'] or 7}일"
                                ], className="text-muted small")
                            ], md=8),
                            dbc.Col([
                                html.Div([
                                    html.H6(f"발주 수량: {order_qty:,} {row['unit']}"),
                                    html.P(f"예상 금액: ₩{amount:,.0f}", className="mb-0")
                                ], className="text-end"),
                                dbc.Checkbox(
                                    id={"type": "auto-po-select", "index": row['item_code']},
                                    value=True,
                                    className="mt-2"
                                )
                            ], md=4)
                        ])
                    ])
                ], className="mb-2")

                suggestions.append(card)

            return html.Div([
                dbc.Alert([
                    html.I(className="fas fa-robot me-2"),
                    f"{len(df)}개 품목에 대한 자동 발주를 제안합니다. ",
                    f"예상 총 금액: ₩{total_amount:,.0f}"
                ], color="info"),
                html.Div(suggestions),
                dbc.Button(
                    [html.I(className="fas fa-check me-2"), "선택한 품목 발주서 생성"],
                    id="create-auto-po-btn",
                    color="primary",
                    className="w-100 mt-3"
                )
            ])

        except Exception as e:
            logger.error(f"자동 발주 제안 오류: {e}")
            return dbc.Alert("제안 생성 중 오류가 발생했습니다.", color="danger")
        finally:
            conn.close()

    # 입고 예정 조회
    @app.callback(
        Output('receiving-schedule-table', 'children'),
        [Input('refresh-receiving', 'n_clicks'),
         Input('receiving-date-filter', 'value')]
    )
    def update_receiving_schedule(n_clicks, filter_date):
        """입고 예정 테이블 업데이트"""
        conn = sqlite3.connect('data/database.db')

        query = """
                SELECT rs.id, \
                       rs.po_number, \
                       po.supplier_code, \
                       sm.supplier_name, \
                       rs.item_code, \
                       im.item_name, \
                       rs.expected_qty, \
                       rs.received_qty, \
                       rs.scheduled_date, \
                       rs.status
                FROM receiving_schedule rs
                         JOIN purchase_orders po ON rs.po_number = po.po_number
                         JOIN supplier_master sm ON po.supplier_code = sm.supplier_code
                         JOIN item_master im ON rs.item_code = im.item_code
                WHERE rs.scheduled_date = ?
                ORDER BY rs.scheduled_date, rs.po_number \
                """

        try:
            df = pd.read_sql_query(query, conn, params=[filter_date])

            if df.empty:
                return html.Div(
                    f"{filter_date}에 입고 예정인 품목이 없습니다.",
                    className="text-center p-4"
                )

            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("발주번호"),
                        html.Th("거래처"),
                        html.Th("품목"),
                        html.Th("예정수량"),
                        html.Th("입고수량"),
                        html.Th("상태"),
                        html.Th("작업")
                    ])
                ])
            ]

            table_body = []
            for idx, row in df.iterrows():
                # 상태 표시
                if row['status'] == 'completed':
                    status_badge = dbc.Badge("완료", color="success")
                elif row['received_qty'] > 0:
                    status_badge = dbc.Badge("부분입고", color="warning")
                else:
                    status_badge = dbc.Badge("대기", color="secondary")

                table_body.append(
                    html.Tr([
                        html.Td(row['po_number']),
                        html.Td(row['supplier_name']),
                        html.Td(f"{row['item_code']} - {row['item_name']}"),
                        html.Td(f"{row['expected_qty']:,}"),
                        html.Td(f"{row['received_qty']:,}"),
                        html.Td(status_badge),
                        html.Td(
                            dbc.Button(
                                [html.I(className="fas fa-check-circle me-2"), "검수"],
                                id={"type": "receive-btn", "index": row['id']},
                                color="primary",
                                size="sm",
                                disabled=row['status'] == 'completed'
                            )
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
            logger.error(f"입고 예정 조회 오류: {e}")
            return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
        finally:
            conn.close()

    # 발주서 모달 토글
    @app.callback(
        Output('po-modal', 'is_open'),
        [Input('new-po-btn', 'n_clicks'),
         Input('close-po-modal', 'n_clicks'),
         Input('save-po-btn', 'n_clicks')],
        [State('po-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_po_modal(new_clicks, close_clicks, save_clicks, is_open):
        """발주서 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open

    # 거래처 모달 토글
    @app.callback(
        Output('supplier-modal', 'is_open'),
        [Input('add-supplier-btn', 'n_clicks'),
         Input('close-supplier-modal', 'n_clicks'),
         Input('save-supplier-btn', 'n_clicks')],
        [State('supplier-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_supplier_modal(add_clicks, close_clicks, save_clicks, is_open):
        """거래처 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open

    # 구매 분석 차트 업데이트
    @app.callback(
        [Output('purchase-cost-trend', 'figure'),
         Output('category-purchase-pie', 'figure'),
         Output('top-suppliers-chart', 'figure'),
         Output('leadtime-analysis', 'figure')],
        Input('analysis-period', 'value')
    )
    def update_purchase_analysis(period):
        """구매 분석 차트 업데이트"""
        conn = sqlite3.connect('data/database.db')

        # 기간 설정
        if period == 'month':
            start_date = datetime.now().replace(day=1)
        elif period == 'quarter':
            month = datetime.now().month
            quarter_start = ((month - 1) // 3) * 3 + 1
            start_date = datetime.now().replace(month=quarter_start, day=1)
        elif period == 'half':
            start_date = datetime.now().replace(month=1 if datetime.now().month <= 6 else 7, day=1)
        else:  # year
            start_date = datetime.now().replace(month=1, day=1)

        try:
            # 1. 구매 비용 추이
            cost_query = """
                         SELECT
                             DATE (po_date) as date, SUM (total_amount) as amount
                         FROM purchase_orders
                         WHERE po_date >= ? AND status != 'cancelled'
                         GROUP BY DATE (po_date)
                         ORDER BY date \
                         """
            cost_df = pd.read_sql_query(cost_query, conn, params=[start_date.strftime('%Y-%m-%d')])

            cost_fig = go.Figure()
            cost_fig.add_trace(go.Scatter(
                x=cost_df['date'],
                y=cost_df['amount'],
                mode='lines+markers',
                name='구매금액',
                line=dict(color='#0066cc', width=3),
                fill='tozeroy'
            ))
            cost_fig.update_layout(
                title="일별 구매 금액 추이",
                xaxis_title="날짜",
                yaxis_title="금액 (원)",
                hovermode='x unified'
            )

            # 2. 카테고리별 구매 비중
            category_query = """
                             SELECT im.category, \
                                    SUM(pod.amount) as total_amount
                             FROM purchase_order_details pod
                                      JOIN purchase_orders po ON pod.po_number = po.po_number
                                      JOIN item_master im ON pod.item_code = im.item_code
                             WHERE po.po_date >= ? \
                               AND po.status != 'cancelled'
                             GROUP BY im.category \
                             """
            category_df = pd.read_sql_query(category_query, conn, params=[start_date.strftime('%Y-%m-%d')])

            category_fig = go.Figure()
            category_fig.add_trace(go.Pie(
                labels=category_df['category'],
                values=category_df['total_amount'],
                hole=0.4
            ))
            category_fig.update_layout(title="카테고리별 구매 비중")

            # 3. TOP 10 거래처
            supplier_query = """
                             SELECT sm.supplier_name, \
                                    COUNT(DISTINCT po.po_number) as order_count, \
                                    SUM(po.total_amount)         as total_amount
                             FROM purchase_orders po
                                      JOIN supplier_master sm ON po.supplier_code = sm.supplier_code
                             WHERE po.po_date >= ? \
                               AND po.status != 'cancelled'
                             GROUP BY sm.supplier_name
                             ORDER BY total_amount DESC
                                 LIMIT 10 \
                             """
            supplier_df = pd.read_sql_query(supplier_query, conn, params=[start_date.strftime('%Y-%m-%d')])

            supplier_fig = go.Figure()
            supplier_fig.add_trace(go.Bar(
                x=supplier_df['supplier_name'],
                y=supplier_df['total_amount'],
                text=supplier_df['total_amount'].apply(lambda x: f'₩{x:,.0f}'),
                textposition='auto',
                marker_color='#17a2b8'
            ))
            supplier_fig.update_layout(
                title="TOP 10 거래처 (구매금액 기준)",
                xaxis_title="거래처",
                yaxis_title="구매금액",
                xaxis_tickangle=-45
            )

            # 4. 리드타임 분석 (더미 데이터)
            leadtime_data = {
                '거래처': ['A사', 'B사', 'C사', 'D사', 'E사'],
                '평균 리드타임': [5, 7, 3, 10, 6],
                '실제 리드타임': [6, 8, 3, 12, 5]
            }
            leadtime_df = pd.DataFrame(leadtime_data)

            leadtime_fig = go.Figure()
            leadtime_fig.add_trace(go.Bar(
                x=leadtime_df['거래처'],
                y=leadtime_df['평균 리드타임'],
                name='계약 리드타임',
                marker_color='lightblue'
            ))
            leadtime_fig.add_trace(go.Bar(
                x=leadtime_df['거래처'],
                y=leadtime_df['실제 리드타임'],
                name='실제 리드타임',
                marker_color='#ff6b6b'
            ))
            leadtime_fig.update_layout(
                title="거래처별 리드타임 분석",
                xaxis_title="거래처",
                yaxis_title="일수",
                barmode='group'
            )

            return cost_fig, category_fig, supplier_fig, leadtime_fig

        except Exception as e:
            logger.error(f"구매 분석 오류: {e}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="데이터 조회 중 오류가 발생했습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig, empty_fig, empty_fig
        finally:
            conn.close()

    # 구매 설정 저장
    @app.callback(
        Output('purchase-settings-message', 'children'),
        Input('save-purchase-settings-btn', 'n_clicks'),
        [State('enable-auto-po', 'value'),
         State('reorder-calc-method', 'value'),
         State('po-notifications', 'value'),
         State('approval-limit-user', 'value'),
         State('approval-limit-admin', 'value'),
         State('default-leadtime', 'value'),
         State('default-payment-terms', 'value')],
        prevent_initial_call=True
    )
    def save_purchase_settings(n_clicks, auto_po, calc_method, notifications,
                               limit_user, limit_admin, leadtime, payment_terms):
        """구매 설정 저장"""
        try:
            settings = {
                'auto_po': {
                    'enabled': auto_po,
                    'calc_method': calc_method,
                    'notifications': notifications
                },
                'approval': {
                    'limit_user': limit_user,
                    'limit_admin': limit_admin
                },
                'defaults': {
                    'leadtime': leadtime,
                    'payment_terms': payment_terms
                }
            }

            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('purchase_settings', ?)
            """, (json.dumps(settings),))

            conn.commit()
            conn.close()

            logger.info("구매 설정 저장 완료")

            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "설정이 저장되었습니다!"],
                color="success",
                dismissable=True
            )

        except Exception as e:
            logger.error(f"구매 설정 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                # File: /modules/purchase/callbacks.py (계속)

                color="danger",
                dismissable=True
            )

    # 거래처 저장


@app.callback(
    Output('supplier-modal-message', 'children'),
    Input('save-supplier-btn', 'n_clicks'),
    [State('modal-supplier-code', 'value'),
     State('modal-supplier-name', 'value'),
     State('modal-business-no', 'value'),
     State('modal-ceo-name', 'value'),
     State('modal-contact-person', 'value'),
     State('modal-phone', 'value'),
     State('modal-email', 'value'),
     State('modal-address', 'value'),
     State('modal-payment-terms', 'value'),
     State('modal-leadtime', 'value'),
     State('modal-rating', 'value')],
    prevent_initial_call=True
)
def save_supplier(n_clicks, supplier_code, supplier_name, business_no,
                  ceo_name, contact_person, phone, email, address,
                  payment_terms, leadtime, rating):
    """거래처 저장"""
    if not all([supplier_code, supplier_name]):
        return dbc.Alert("거래처 코드와 거래처명은 필수입니다.", color="warning")

    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        cursor.execute("""
               INSERT OR REPLACE INTO supplier_master 
               (supplier_code, supplier_name, business_no, ceo_name, 
                contact_person, phone, email, address, payment_terms, 
                lead_time, rating, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
           """, (supplier_code, supplier_name, business_no, ceo_name,
                 contact_person, phone, email, address, payment_terms,
                 leadtime, rating))

        conn.commit()
        conn.close()

        logger.info(f"거래처 저장 완료: {supplier_code}")

        return dbc.Alert(
            [html.I(className="fas fa-check-circle me-2"), "거래처가 등록되었습니다!"],
            color="success"
        )

    except sqlite3.IntegrityError:
        return dbc.Alert("이미 존재하는 거래처 코드입니다.", color="danger")
    except Exception as e:
        logger.error(f"거래처 저장 실패: {e}")
        return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")


# 거래처 리스트 조회
@app.callback(
    Output('supplier-list-table', 'children'),
    [Input('filter-supplier-btn', 'n_clicks'),
     Input('save-supplier-btn', 'n_clicks')],
    [State('supplier-search', 'value'),
     State('supplier-rating-filter', 'value')]
)
def update_supplier_list(filter_clicks, save_clicks, search_value, rating_filter):
    """거래처 리스트 업데이트"""
    conn = sqlite3.connect('data/database.db')

    query = "SELECT * FROM supplier_master WHERE is_active = 1"
    params = []

    if search_value:
        query += " AND (supplier_name LIKE ? OR business_no LIKE ?)"
        params.extend([f"%{search_value}%", f"%{search_value}%"])

    if rating_filter != 'all':
        query += " AND rating = ?"
        params.append(rating_filter)

    query += " ORDER BY supplier_name"

    try:
        df = pd.read_sql_query(query, conn, params=params)

        if df.empty:
            return html.Div("등록된 거래처가 없습니다.", className="text-center p-4")

        # 테이블 생성
        table_header = [
            html.Thead([
                html.Tr([
                    html.Th("거래처코드"),
                    html.Th("거래처명"),
                    html.Th("담당자"),
                    html.Th("연락처"),
                    html.Th("결제조건"),
                    html.Th("리드타임"),
                    html.Th("등급"),
                    html.Th("작업")
                ])
            ])
        ]

        table_body = []
        for idx, row in df.iterrows():
            # 등급 표시
            rating_stars = "⭐" * int(row['rating'])

            # 결제조건 한글화
            payment_terms_map = {
                'CASH': '현금',
                'NET30': '30일',
                'NET60': '60일',
                'NET90': '90일'
            }
            payment_terms = payment_terms_map.get(row['payment_terms'], row['payment_terms'])

            table_body.append(
                html.Tr([
                    html.Td(row['supplier_code']),
                    html.Td(row['supplier_name']),
                    html.Td(row['contact_person'] or '-'),
                    html.Td(row['phone'] or '-'),
                    html.Td(payment_terms),
                    html.Td(f"{row['lead_time']}일"),
                    html.Td(rating_stars),
                    html.Td(
                        dbc.ButtonGroup([
                            dbc.Button(
                                html.I(className="fas fa-edit"),
                                id={"type": "edit-supplier", "index": row['supplier_code']},
                                color="primary",
                                size="sm"
                            ),
                            dbc.Button(
                                html.I(className="fas fa-chart-line"),
                                id={"type": "supplier-stats", "index": row['supplier_code']},
                                color="info",
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
        logger.error(f"거래처 조회 오류: {e}")
        return html.Div("조회 중 오류가 발생했습니다.", className="text-center p-4")
    finally:
        conn.close()


# 발주서 저장
@app.callback(
    Output('po-modal-message', 'children'),
    Input('save-po-btn', 'n_clicks'),
    [State('modal-po-number', 'value'),
     State('modal-po-date', 'value'),
     State('modal-supplier', 'value'),
     State('modal-delivery-date', 'value'),
     State('po-items-list', 'children'),
     State('po-total-amount', 'children'),
     State('modal-po-remarks', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def save_purchase_order(n_clicks, po_number, po_date, supplier, delivery_date,
                        items_list, total_amount, remarks, session_data):
    """발주서 저장"""
    if not all([po_number, po_date, supplier, delivery_date]):
        return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning")

    # items_list 파싱 필요 (실제 구현시)
    # total_amount 파싱 (₩ 제거)
    total_amount_value = float(total_amount.replace('₩', '').replace(',', ''))

    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # 발주번호 생성
        cursor.execute("SELECT COUNT(*) FROM purchase_orders WHERE po_date = ?", (po_date,))
        count = cursor.fetchone()[0]
        po_number = f"PO-{po_date.replace('-', '')}-{count + 1:03d}"

        # 사용자 ID
        user_id = session_data.get('user_id', 1) if session_data else 1

        # 발주서 헤더 저장
        cursor.execute("""
                       INSERT INTO purchase_orders
                       (po_number, po_date, supplier_code, delivery_date,
                        warehouse, total_amount, status, remarks, created_by)
                       VALUES (?, ?, ?, ?, 'wh1', ?, 'draft', ?, ?)
                       """, (po_number, po_date, supplier, delivery_date,
                             total_amount_value, remarks, user_id))

        # 발주 상세 저장 (실제 구현시 items_list에서 파싱)
        # 예시 데이터
        sample_items = [
            ('BOLT-M10', 100, 150, 15000),
            ('NUT-M10', 200, 80, 16000)
        ]

        for item in sample_items:
            cursor.execute("""
                           INSERT INTO purchase_order_details
                               (po_number, item_code, quantity, unit_price, amount)
                           VALUES (?, ?, ?, ?, ?)
                           """, (po_number, item[0], item[1], item[2], item[3]))

            # 입고 예정 등록
            cursor.execute("""
                           INSERT INTO receiving_schedule
                               (po_number, scheduled_date, item_code, expected_qty, status)
                           VALUES (?, ?, ?, ?, 'pending')
                           """, (po_number, delivery_date, item[0], item[1]))

        conn.commit()
        conn.close()

        logger.info(f"발주서 생성 완료: {po_number}")

        return dbc.Alert(
            [html.I(className="fas fa-check-circle me-2"),
             f"발주서 {po_number}가 생성되었습니다!"],
            color="success"
        )

    except Exception as e:
        logger.error(f"발주서 저장 실패: {e}")
        return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")


# 입고 검수 처리
@app.callback(
    Output('inspection-message', 'children'),
    Input('complete-inspection-btn', 'n_clicks'),
    [State('inspection-po-number', 'value'),
     State('inspection-date', 'value'),
     State('inspection-items', 'children'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def process_receiving_inspection(n_clicks, po_number, inspection_date,
                                 items_data, session_data):
    """입고 검수 처리"""
    if not po_number:
        return dbc.Alert("발주번호를 입력하세요.", color="warning")

    try:
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()

        # 검수자 ID
        inspector_id = session_data.get('user_id', 1) if session_data else 1

        # 발주 품목 조회
        cursor.execute("""
                       SELECT pod.item_code, pod.quantity, im.item_name
                       FROM purchase_order_details pod
                                JOIN item_master im ON pod.item_code = im.item_code
                       WHERE pod.po_number = ?
                       """, (po_number,))

        items = cursor.fetchall()

        if not items:
            return dbc.Alert("해당 발주번호를 찾을 수 없습니다.", color="danger")

        # 각 품목에 대해 검수 처리
        for item in items:
            item_code, expected_qty, item_name = item

            # 실제로는 UI에서 입력받은 수량 사용
            received_qty = expected_qty  # 임시로 전량 입고
            accepted_qty = received_qty
            rejected_qty = 0

            # 검수 기록
            cursor.execute("""
                           INSERT INTO receiving_inspection
                           (receiving_date, po_number, item_code, received_qty,
                            accepted_qty, rejected_qty, inspection_result, inspector_id)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                           """, (inspection_date, po_number, item_code, received_qty,
                                 accepted_qty, rejected_qty, '합격', inspector_id))

            # 재고 반영
            cursor.execute("""
                           UPDATE item_master
                           SET current_stock = current_stock + ?
                           WHERE item_code = ?
                           """, (accepted_qty, item_code))

            # 재고 이동 기록
            cursor.execute("""
                           INSERT INTO stock_movements
                           (movement_date, movement_type, item_code, quantity,
                            warehouse, remarks)
                           VALUES (?, 'IN_purchase', ?, ?, 'wh1', ?)
                           """, (inspection_date, item_code, accepted_qty,
                                 f'발주번호: {po_number}'))

            # 입고 예정 업데이트
            cursor.execute("""
                           UPDATE receiving_schedule
                           SET received_qty = received_qty + ?,
                               status       = CASE
                                                  WHEN received_qty + ? >= expected_qty THEN 'completed'
                                                  ELSE 'partial'
                                   END
                           WHERE po_number = ?
                             AND item_code = ?
                           """, (accepted_qty, accepted_qty, po_number, item_code))

        # 발주서 상태 업데이트
        cursor.execute("""
                       UPDATE purchase_orders
                       SET status = 'receiving'
                       WHERE po_number = ?
                       """, (po_number,))

        conn.commit()
        conn.close()

        logger.info(f"입고 검수 완료: {po_number}")

        return dbc.Alert(
            [html.I(className="fas fa-check-circle me-2"),
             f"발주번호 {po_number}의 입고 검수가 완료되었습니다!"],
            color="success",
            dismissable=True
        )

    except Exception as e:
        logger.error(f"입고 검수 처리 실패: {e}")
        return dbc.Alert(
            f"처리 중 오류가 발생했습니다: {str(e)}",
            color="danger",
            dismissable=True
        )


# 검수 이력 조회
@app.callback(
    Output('inspection-history', 'children'),
    [Input('complete-inspection-btn', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_inspection_history(n_clicks, n_intervals):
    """검수 이력 업데이트"""
    conn = sqlite3.connect('data/database.db')

    query = """
            SELECT ri.receiving_date, \
                   ri.po_number, \
                   ri.item_code, \
                   im.item_name, \
                   ri.received_qty, \
                   ri.accepted_qty, \
                   ri.rejected_qty, \
                   ri.inspection_result, \
                   u.username as inspector
            FROM receiving_inspection ri
                     JOIN item_master im ON ri.item_code = im.item_code
                     LEFT JOIN users u ON ri.inspector_id = u.id
            ORDER BY ri.created_at DESC LIMIT 10 \
            """

    try:
        df = pd.read_sql_query(query, conn)

        if df.empty:
            return html.Div("검수 이력이 없습니다.", className="text-center p-4")

        # 간단한 리스트 형태로 표시
        history_items = []
        for idx, row in df.iterrows():
            result_color = "success" if row['inspection_result'] == '합격' else "danger"

            history_items.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"{row['po_number']} - {row['item_name']}", className="mb-1"),
                        html.P([
                            f"입고: {row['received_qty']} / ",
                            f"합격: {row['accepted_qty']} / ",
                            f"불량: {row['rejected_qty']}",
                            dbc.Badge(row['inspection_result'], color=result_color, className="ms-2")
                        ], className="mb-0 small"),
                        html.P(f"{row['receiving_date']} - {row['inspector']}",
                               className="text-muted small mb-0")
                    ])
                ], className="mb-2")
            )

        return html.Div(history_items)

    except Exception as e:
        logger.error(f"검수 이력 조회 오류: {e}")
        return html.Div("이력 조회 중 오류가 발생했습니다.")
    finally:
        conn.close()
