# modules/mes/callbacks.py - MES 모듈 콜백 함수

from dash import Input, Output, State, callback_context, ALL, MATCH, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

def register_mes_callbacks(app):
    """MES 모듈 콜백 등록"""
    
    # MES 탭 콘텐츠 렌더링
    @app.callback(
        Output('mes-tab-content', 'children'),
        Input('mes-tabs', 'active_tab')
    )
    def render_mes_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_work_input_form, create_status_view, 
            create_analysis_view, create_mes_settings
        )
        
        if active_tab == "work-input":
            return create_work_input_form()
        elif active_tab == "status-view":
            return create_status_view()
        elif active_tab == "analysis":
            return create_analysis_view()
        elif active_tab == "mes-settings":
            return create_mes_settings()
    
    # 달성률 실시간 계산
    @app.callback(
        [Output('achievement-rate', 'value'),
         Output('achievement-rate', 'color'),
         Output('achievement-text', 'children')],
        [Input('plan-qty', 'value'),
         Input('prod-qty', 'value')]
    )
    def update_achievement_rate(plan_qty, prod_qty):
        """달성률 업데이트"""
        if not plan_qty or plan_qty == 0:
            return 0, "secondary", "계획 수량을 입력하세요"
        
        rate = min((prod_qty or 0) / plan_qty * 100, 100)
        
        if rate >= 100:
            color = "success"
            text = f"목표 달성! ({rate:.1f}%)"
        elif rate >= 80:
            color = "warning"
            text = f"달성률: {rate:.1f}%"
        else:
            color = "danger"
            text = f"달성률: {rate:.1f}%"
        
        return rate, color, text
    
    # 작업 데이터 저장
    @app.callback(
        Output('work-input-message', 'children'),
        Input('save-work-btn', 'n_clicks'),
        [State('work-date', 'value'),
         State('lot-number', 'value'),
         State('process-select', 'value'),
         State('worker-select', 'value'),
         State('plan-qty', 'value'),
         State('prod-qty', 'value'),
         State('defect-qty', 'value')],
        prevent_initial_call=True
    )
    def save_work_data(n_clicks, work_date, lot_number, process, worker_id, 
                      plan_qty, prod_qty, defect_qty):
        """작업 데이터 저장"""
        if not all([work_date, lot_number, process, worker_id, plan_qty, prod_qty]):
            return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning", dismissable=True)
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO work_logs 
                (lot_number, work_date, process, worker_id, plan_qty, prod_qty, defect_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (lot_number, work_date, process, int(worker_id), 
                  plan_qty, prod_qty, defect_qty or 0))
            
            conn.commit()
            conn.close()
            
            logger.info(f"작업 데이터 저장 완료: LOT {lot_number}")
            
            return dbc.Alert(
                [
                    html.I(className="fas fa-check-circle me-2"),
                    "작업 데이터가 성공적으로 저장되었습니다!"
                ],
                color="success",
                dismissable=True,
                fade=True
            )
            
        except Exception as e:
            logger.error(f"작업 데이터 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                color="danger",
                dismissable=True
            )
    
    # 작업 입력 폼 초기화
    @app.callback(
        [Output('lot-number', 'value'),
         Output('plan-qty', 'value'),
         Output('prod-qty', 'value'),
         Output('defect-qty', 'value')],
        Input('reset-work-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_work_form(n_clicks):
        """작업 입력 폼 초기화"""
        lot_prefix = f"LOT-{datetime.now().strftime('%Y%m%d')}-"
        return lot_prefix, None, None, None
    
    # 현황 조회 및 차트 업데이트
    @app.callback(
        [Output('total-production', 'children'),
         Output('avg-achievement', 'children'),
         Output('defect-rate', 'children'),
         Output('work-count', 'children'),
         Output('daily-production-chart', 'figure'),
         Output('process-performance-chart', 'figure'),
         Output('work-logs-table', 'children')],
        [Input('search-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')],
        [State('search-start-date', 'value'),
         State('search-end-date', 'value'),
         State('search-process', 'value')]
    )
    def update_status_view(n_clicks, n_intervals, start_date, end_date, process):
        """현황 조회 업데이트"""
        from .layouts import get_work_logs, create_work_logs_table
        
        # 데이터 조회
        df = get_work_logs(start_date, end_date, process)
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return "0", "0%", "0%", "0", empty_fig, empty_fig, "조회된 데이터가 없습니다."
        
        # 통계 계산
        total_production = df['prod_qty'].sum()
        total_defects = df['defect_qty'].sum()
        work_count = len(df)
        
        # 달성률 계산
        df['achievement'] = df.apply(
            lambda row: (row['prod_qty'] / row['plan_qty'] * 100) if row['plan_qty'] > 0 else 0,
            axis=1
        )
        avg_achievement = df['achievement'].mean()
        
        # 불량률 계산
        defect_rate = (total_defects / total_production * 100) if total_production > 0 else 0
        
        # 일별 생산 추이 차트
        daily_df = df.groupby('work_date').agg({
            'prod_qty': 'sum',
            'defect_qty': 'sum'
        }).reset_index()
        
        daily_fig = go.Figure()
        daily_fig.add_trace(go.Scatter(
            x=daily_df['work_date'],
            y=daily_df['prod_qty'],
            mode='lines+markers',
            name='생산량',
            line=dict(color='#0066cc', width=3)
        ))
        daily_fig.add_trace(go.Scatter(
            x=daily_df['work_date'],
            y=daily_df['defect_qty'],
            mode='lines+markers',
            name='불량',
            line=dict(color='#dc3545', width=2)
        ))
        daily_fig.update_layout(
            title="일별 생산 추이",
            xaxis_title="날짜",
            yaxis_title="수량",
            hovermode='x unified'
        )
        
        # 공정별 실적 차트
        process_df = df.groupby('process').agg({
            'prod_qty': 'sum',
            'defect_qty': 'sum'
        }).reset_index()
        
        process_fig = go.Figure()
        process_fig.add_trace(go.Bar(
            x=process_df['process'],
            y=process_df['prod_qty'],
            name='생산량',
            marker_color='#0066cc'
        ))
        process_fig.add_trace(go.Bar(
            x=process_df['process'],
            y=process_df['defect_qty'],
            name='불량',
            marker_color='#dc3545'
        ))
        process_fig.update_layout(
            title="공정별 실적",
            xaxis_title="공정",
            yaxis_title="수량",
            barmode='group'
        )
        
        # 상세 테이블
        table = create_work_logs_table(df)
        
        return (
            f"{total_production:,}",
            f"{avg_achievement:.1f}%",
            f"{defect_rate:.1f}%",
            f"{work_count:,}",
            daily_fig,
            process_fig,
            table
        )
    
    # 분석 차트 업데이트
    @app.callback(
        [Output('productivity-analysis-chart', 'figure'),
         Output('hourly-analysis-chart', 'figure'),
         Output('worker-performance-chart', 'figure')],
        Input('interval-component', 'n_intervals')
    )
    def update_analysis_charts(n_intervals):
        """분석 차트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        # 최근 30일 데이터
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # 생산성 분석 차트
        productivity_query = """
            SELECT work_date, 
                   SUM(plan_qty) as total_plan,
                   SUM(prod_qty) as total_prod,
                   AVG(CAST(prod_qty AS FLOAT) / NULLIF(plan_qty, 0) * 100) as avg_achievement
            FROM work_logs
            WHERE work_date BETWEEN ? AND ?
            GROUP BY work_date
            ORDER BY work_date
        """
        productivity_df = pd.read_sql_query(
            productivity_query, 
            conn, 
            params=[start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        )
        
        productivity_fig = go.Figure()
        productivity_fig.add_trace(go.Bar(
            x=productivity_df['work_date'],
            y=productivity_df['total_plan'],
            name='계획',
            marker_color='lightblue'
        ))
        productivity_fig.add_trace(go.Bar(
            x=productivity_df['work_date'],
            y=productivity_df['total_prod'],
            name='실적',
            marker_color='#0066cc'
        ))
        productivity_fig.add_trace(go.Scatter(
            x=productivity_df['work_date'],
            y=productivity_df['avg_achievement'],
            name='달성률(%)',
            yaxis='y2',
            line=dict(color='#28a745', width=3)
        ))
        productivity_fig.update_layout(
            title="일별 생산성 분석 (최근 30일)",
            xaxis_title="날짜",
            yaxis_title="수량",
            yaxis2=dict(
                title="달성률(%)",
                overlaying='y',
                side='right',
                range=[0, 120]
            ),
            hovermode='x unified',
            barmode='group'
        )
        
        # 시간대별 분석 (더미 데이터 - 실제로는 시간 정보가 있어야 함)
        hours = list(range(8, 18))  # 8시~17시
        hourly_data = [100 + i*10 + (i%3)*20 for i in range(len(hours))]
        
        hourly_fig = go.Figure()
        hourly_fig.add_trace(go.Bar(
            x=hours,
            y=hourly_data,
            text=hourly_data,
            textposition='auto',
            marker_color='#17a2b8'
        ))
        hourly_fig.update_layout(
            title="시간대별 생산량",
            xaxis_title="시간",
            yaxis_title="생산량",
            xaxis=dict(
                tickmode='linear',
                tick0=8,
                dtick=1,
                ticksuffix='시'
            )
        )
        
        # 작업자별 실적
        worker_query = """
            SELECT u.username,
                   COUNT(w.id) as work_count,
                   SUM(w.prod_qty) as total_prod,
                   AVG(CAST(w.prod_qty AS FLOAT) / NULLIF(w.plan_qty, 0) * 100) as avg_achievement
            FROM work_logs w
            JOIN users u ON w.worker_id = u.id
            WHERE w.work_date BETWEEN ? AND ?
            GROUP BY u.username
            ORDER BY total_prod DESC
        """
        worker_df = pd.read_sql_query(
            worker_query,
            conn,
            params=[start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        )
        
        worker_fig = go.Figure()
        worker_fig.add_trace(go.Bar(
            x=worker_df['username'],
            y=worker_df['total_prod'],
            text=worker_df['total_prod'],
            textposition='auto',
            marker_color='#ffc107'
        ))
        worker_fig.update_layout(
            title="작업자별 생산 실적 (최근 30일)",
            xaxis_title="작업자",
            yaxis_title="총 생산량"
        )
        
        conn.close()
        
        return productivity_fig, hourly_fig, worker_fig
    
    # MES 설정 저장
    @app.callback(
        Output('save-mes-settings-btn', 'children'),
        Input('save-mes-settings-btn', 'n_clicks'),
        [State({'type': 'field-switch', 'field': ALL}, 'value'),
         State({'type': 'field-required', 'field': ALL}, 'value'),
         State({'type': 'field-default', 'field': ALL}, 'value'),
         State('notification-settings', 'value')],
        prevent_initial_call=True
    )
    def save_mes_settings(n_clicks, field_switches, field_required, field_defaults, notifications):
        """MES 설정 저장"""
        try:
            # 설정 데이터 구성
            settings = {
                'fields': {
                    'enabled': field_switches,
                    'required': field_required,
                    'defaults': field_defaults
                },
                'notifications': notifications
            }
            
            # 데이터베이스에 저장
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('mes_settings', ?)
            """, (json.dumps(settings),))
            
            conn.commit()
            conn.close()
            
            logger.info("MES 설정 저장 완료")
            
            return [
                html.I(className="fas fa-check me-2"),
                "설정이 저장되었습니다!"
            ]
            
        except Exception as e:
            logger.error(f"MES 설정 저장 실패: {e}")
            return [
                html.I(className="fas fa-times me-2"),
                "저장 실패"
            ]
