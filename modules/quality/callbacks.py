# File: modules/quality/callbacks.py
# 품질관리 모듈 콜백 함수 - V1.1 신규

from dash import Input, Output, State, callback_context, ALL, MATCH, dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)

def register_quality_callbacks(app):
    """품질관리 모듈 콜백 등록"""
    
    # 탭 콘텐츠 렌더링
    @app.callback(
        Output('quality-tab-content', 'children'),
        Input('quality-tabs', 'active_tab')
    )
    def render_quality_tab_content(active_tab):
        """활성 탭에 따른 콘텐츠 렌더링"""
        from .layouts import (
            create_inspection_management, create_defect_management,
            create_spc_dashboard, create_certificate_management,
            create_quality_analysis, create_quality_settings
        )
        
        if active_tab == "inspection":
            return create_inspection_management()
        elif active_tab == "defect":
            return create_defect_management()
        elif active_tab == "spc":
            return create_spc_dashboard()
        elif active_tab == "certificate":
            return create_certificate_management()
        elif active_tab == "quality-analysis":
            return create_quality_analysis()
        elif active_tab == "quality-settings":
            return create_quality_settings()
    
    # 검사 현황 업데이트
    @app.callback(
        [Output('today-inspections', 'children'),
         Output('pass-rate', 'children'),
         Output('defect-rate', 'children'),
         Output('calibration-due', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_inspection_summary(n):
        """검사 현황 요약 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            cursor = conn.cursor()
            
            # 오늘 검사
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT id FROM incoming_inspection WHERE inspection_date = ?
                    UNION ALL
                    SELECT id FROM process_inspection WHERE inspection_date = ?
                    UNION ALL
                    SELECT id FROM final_inspection WHERE inspection_date = ?
                )
            """, (today, today, today))
            today_inspections = cursor.fetchone()[0]
            
            # 이번 주 합격률
            week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT 
                    SUM(passed_qty) * 100.0 / NULLIF(SUM(sample_qty), 0) as pass_rate
                FROM (
                    SELECT sample_qty, passed_qty FROM incoming_inspection WHERE inspection_date >= ?
                    UNION ALL
                    SELECT sample_qty, passed_qty FROM process_inspection WHERE inspection_date >= ?
                    UNION ALL
                    SELECT sample_qty, passed_qty FROM final_inspection WHERE inspection_date >= ?
                )
            """, (week_start, week_start, week_start))
            pass_rate_result = cursor.fetchone()[0]
            pass_rate = pass_rate_result if pass_rate_result else 0
            
            # 불량률
            defect_rate = 100 - pass_rate if pass_rate > 0 else 0
            
            # 교정 예정 장비
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_equipment 
                WHERE next_calibration_date <= date('now', '+30 days')
                AND status = 'active'
            """)
            calibration_due = cursor.fetchone()[0]
            
            return (
                f"{today_inspections:,}",
                f"{pass_rate:.1f}%",
                f"{defect_rate:.1f}%",
                f"{calibration_due:,}"
            )
            
        except Exception as e:
            logger.error(f"검사 현황 조회 오류: {e}")
            return "0", "0%", "0%", "0"
        finally:
            conn.close()
    
    # 검사 리스트 업데이트
    @app.callback(
        Output('inspection-list', 'children'),
        [Input('inspection-type-tabs', 'active_tab'),
         Input('interval-component', 'n_intervals')]
    )
    def update_inspection_list(inspection_type, n):
        """검사 리스트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            if inspection_type == "incoming":
                query = """
                    SELECT i.inspection_no,
                           i.inspection_date,
                           i.item_code,
                           im.item_name,
                           i.received_qty,
                           i.sample_qty,
                           i.passed_qty,
                           i.inspection_result,
                           u.username as inspector
                    FROM incoming_inspection i
                    LEFT JOIN item_master im ON i.item_code = im.item_code
                    LEFT JOIN users u ON i.inspector_id = u.id
                    ORDER BY i.inspection_date DESC
                    LIMIT 50
                """
            elif inspection_type == "process":
                query = """
                    SELECT i.inspection_no,
                           i.inspection_date,
                           i.item_code,
                           im.item_name,
                           i.production_qty as received_qty,
                           i.sample_qty,
                           i.passed_qty,
                           i.inspection_result,
                           u.username as inspector
                    FROM process_inspection i
                    LEFT JOIN item_master im ON i.item_code = im.item_code
                    LEFT JOIN users u ON i.inspector_id = u.id
                    ORDER BY i.inspection_date DESC
                    LIMIT 50
                """
            else:  # final
                query = """
                    SELECT i.inspection_no,
                           i.inspection_date,
                           i.product_code as item_code,
                           i.product_code as item_name,
                           i.inspection_qty as received_qty,
                           i.sample_qty,
                           i.passed_qty,
                           i.inspection_result,
                           u.username as inspector
                    FROM final_inspection i
                    LEFT JOIN users u ON i.inspector_id = u.id
                    ORDER BY i.inspection_date DESC
                    LIMIT 50
                """
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return html.Div("검사 이력이 없습니다.", className="text-center p-4")
            
            # 검사 결과 색상
            result_colors = {
                'pass': 'success',
                'fail': 'danger',
                'conditional': 'warning',
                'rework': 'info'
            }
            
            # 테이블 생성
            table_header = [
                html.Thead([
                    html.Tr([
                        html.Th("검사번호"),
                        html.Th("검사일자"),
                        html.Th("품목코드"),
                        html.Th("품목명"),
                        html.Th("검사수량"),
                        html.Th("샘플수"),
                        html.Th("합격수"),
                        html.Th("결과"),
                        html.Th("검사자")
                    ])
                ])
            ]
            
            table_body = []
            for idx, row in df.iterrows():
                # 합격률 계산
                if row['sample_qty'] > 0:
                    pass_rate = (row['passed_qty'] / row['sample_qty']) * 100
                    pass_rate_badge = dbc.Badge(f"{pass_rate:.1f}%", color="info", className="ms-1")
                else:
                    pass_rate_badge = ""
                
                table_body.append(
                    html.Tr([
                        html.Td(row['inspection_no']),
                        html.Td(row['inspection_date']),
                        html.Td(row['item_code']),
                        html.Td(row['item_name']),
                        html.Td(f"{row['received_qty']:,}"),
                        html.Td(f"{row['sample_qty']:,}"),
                        html.Td(f"{row['passed_qty']:,}"),
                        html.Td([
                            dbc.Badge(
                                row['inspection_result'].upper(),
                                color=result_colors.get(row['inspection_result'], 'secondary')
                            ),
                            pass_rate_badge
                        ]),
                        html.Td(row['inspector'] or '-')
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
            logger.error(f"검사 리스트 조회 오류: {e}")
            return html.Div(f"조회 중 오류가 발생했습니다: {str(e)}", className="text-center p-4")
        finally:
            conn.close()
    
    # 일별 검사 현황 차트
    @app.callback(
        Output('daily-inspection-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_daily_inspection_chart(n):
        """일별 검사 현황 차트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            # 최근 30일 데이터
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            query = """
                SELECT 
                    inspection_date,
                    inspection_type,
                    COUNT(*) as count
                FROM (
                    SELECT inspection_date, 'incoming' as inspection_type FROM incoming_inspection
                    WHERE inspection_date BETWEEN ? AND ?
                    UNION ALL
                    SELECT inspection_date, 'process' as inspection_type FROM process_inspection
                    WHERE inspection_date BETWEEN ? AND ?
                    UNION ALL
                    SELECT inspection_date, 'final' as inspection_type FROM final_inspection
                    WHERE inspection_date BETWEEN ? AND ?
                )
                GROUP BY inspection_date, inspection_type
                ORDER BY inspection_date
            """
            
            params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')] * 3
            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="데이터가 없습니다",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            else:
                # 피벗 테이블 생성
                pivot_df = df.pivot(index='inspection_date', columns='inspection_type', values='count').fillna(0)
                
                fig = go.Figure()
                
                type_names = {
                    'incoming': '입고검사',
                    'process': '공정검사',
                    'final': '출하검사'
                }
                
                colors = {
                    'incoming': '#0066cc',
                    'process': '#28a745',
                    'final': '#ffc107'
                }
                
                for col in pivot_df.columns:
                    fig.add_trace(go.Bar(
                        x=pivot_df.index,
                        y=pivot_df[col],
                        name=type_names.get(col, col),
                        marker_color=colors.get(col, '#666')
                    ))
                
                fig.update_layout(
                    title="일별 검사 현황",
                    xaxis_title="날짜",
                    yaxis_title="검사 건수",
                    barmode='stack'
                )
            
            return fig
            
        except Exception as e:
            logger.error(f"일별 검사 차트 조회 오류: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"오류: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        finally:
            conn.close()
    
    # 검사 유형별 합격률 차트
    @app.callback(
        Output('inspection-pass-rate-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_pass_rate_chart(n):
        """검사 유형별 합격률 차트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            # 최근 30일 데이터
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            data = []
            
            # 입고검사
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    'incoming' as type,
                    SUM(passed_qty) * 100.0 / NULLIF(SUM(sample_qty), 0) as pass_rate,
                    COUNT(*) as count
                FROM incoming_inspection
                WHERE inspection_date >= ?
            """, (start_date,))
            result = cursor.fetchone()
            if result[1]:
                data.append({
                    'type': '입고검사',
                    'pass_rate': result[1],
                    'count': result[2]
                })
            
            # 공정검사
            cursor.execute("""
                SELECT 
                    'process' as type,
                    SUM(passed_qty) * 100.0 / NULLIF(SUM(sample_qty), 0) as pass_rate,
                    COUNT(*) as count
                FROM process_inspection
                WHERE inspection_date >= ?
            """, (start_date,))
            result = cursor.fetchone()
            if result[1]:
                data.append({
                    'type': '공정검사',
                    'pass_rate': result[1],
                    'count': result[2]
                })
            
            # 출하검사
            cursor.execute("""
                SELECT 
                    'final' as type,
                    SUM(passed_qty) * 100.0 / NULLIF(SUM(sample_qty), 0) as pass_rate,
                    COUNT(*) as count
                FROM final_inspection
                WHERE inspection_date >= ?
            """, (start_date,))
            result = cursor.fetchone()
            if result[1]:
                data.append({
                    'type': '출하검사',
                    'pass_rate': result[1],
                    'count': result[2]
                })
            
            if data:
                df = pd.DataFrame(data)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['type'],
                    y=df['pass_rate'],
                    text=df['pass_rate'].apply(lambda x: f'{x:.1f}%'),
                    textposition='auto',
                    marker_color=['#0066cc', '#28a745', '#ffc107']
                ))
                
                # 목표선 추가
                fig.add_hline(y=98, line_dash="dash", line_color="red",
                            annotation_text="목표: 98%")
                
                fig.update_layout(
                    title="검사 유형별 합격률 (최근 30일)",
                    xaxis_title="검사 유형",
                    yaxis_title="합격률 (%)",
                    yaxis_range=[0, 105]
                )
            else:
                fig = go.Figure()
                fig.add_annotation(
                    text="데이터가 없습니다",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            return fig
            
        except Exception as e:
            logger.error(f"합격률 차트 조회 오류: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"오류: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        finally:
            conn.close()
    
    # 불량 현황 업데이트
    @app.callback(
        [Output('monthly-defects', 'children'),
         Output('critical-defects', 'children'),
         Output('open-defects', 'children'),
         Output('closed-defects', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_defect_summary(n):
        """불량 현황 요약 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            cursor = conn.cursor()
            
            # 이번 달 불량
            cursor.execute("""
                SELECT COUNT(*) FROM defect_history 
                WHERE strftime('%Y-%m', defect_date) = strftime('%Y-%m', 'now')
            """)
            monthly_defects = cursor.fetchone()[0]
            
            # 중대 불량 (severity_level = 1)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM defect_history dh
                JOIN defect_types dt ON dh.defect_code = dt.defect_code
                WHERE dt.severity_level = 1
                AND dh.status != 'closed'
            """)
            critical_defects = cursor.fetchone()[0]
            
            # 처리 중
            cursor.execute("""
                SELECT COUNT(*) FROM defect_history 
                WHERE status IN ('open', 'in_progress')
            """)
            open_defects = cursor.fetchone()[0]
            
            # 완료
            cursor.execute("""
                SELECT COUNT(*) FROM defect_history 
                WHERE status = 'closed'
                AND strftime('%Y-%m', closed_date) = strftime('%Y-%m', 'now')
            """)
            closed_defects = cursor.fetchone()[0]
            
            return (
                f"{monthly_defects:,}",
                f"{critical_defects:,}",
                f"{open_defects:,}",
                f"{closed_defects:,}"
            )
            
        except Exception as e:
            logger.error(f"불량 현황 조회 오류: {e}")
            return "0", "0", "0", "0"
        finally:
            conn.close()
    
    # SPC 차트 업데이트
    @app.callback(
        [Output('xbar-chart', 'figure'),
         Output('r-chart', 'figure'),
         Output('cp-value', 'children'),
         Output('cpk-value', 'children'),
         Output('normality-test-chart', 'figure')],
        [Input('spc-process-select', 'value'),
         Input('spc-item-select', 'value'),
         Input('spc-characteristic-select', 'value'),
         Input('spc-period-select', 'value')]
    )
    def update_spc_charts(process, item, characteristic, period):
        """SPC 차트 업데이트"""
        # 더미 데이터 생성 (실제로는 DB에서 조회)
        np.random.seed(42)
        
        # 샘플 데이터 생성
        n_samples = 25
        sample_size = 5
        target = 10.0
        std_dev = 0.1
        
        # X-bar 차트 데이터
        samples = []
        for i in range(n_samples):
            sample = np.random.normal(target, std_dev, sample_size)
            samples.append(sample)
        
        samples_array = np.array(samples)
        x_bar = samples_array.mean(axis=1)
        r_values = samples_array.max(axis=1) - samples_array.min(axis=1)
        
        # 관리한계 계산
        x_bar_mean = x_bar.mean()
        r_mean = r_values.mean()
        
        # A2, D3, D4 상수 (n=5일 때)
        A2 = 0.577
        D3 = 0
        D4 = 2.114
        
        x_bar_ucl = x_bar_mean + A2 * r_mean
        x_bar_lcl = x_bar_mean - A2 * r_mean
        r_ucl = D4 * r_mean
        r_lcl = D3 * r_mean
        
        # X-bar 차트
        xbar_fig = go.Figure()
        xbar_fig.add_trace(go.Scatter(
            x=list(range(1, n_samples+1)),
            y=x_bar,
            mode='lines+markers',
            name='X-bar',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        
        # 관리한계선
        xbar_fig.add_hline(y=x_bar_ucl, line_dash="dash", line_color="red",
                          annotation_text=f"UCL: {x_bar_ucl:.3f}")
        xbar_fig.add_hline(y=x_bar_mean, line_dash="solid", line_color="green",
                          annotation_text=f"CL: {x_bar_mean:.3f}")
        xbar_fig.add_hline(y=x_bar_lcl, line_dash="dash", line_color="red",
                          annotation_text=f"LCL: {x_bar_lcl:.3f}")
        
        xbar_fig.update_layout(
            title="X-bar 관리도",
            xaxis_title="샘플 번호",
            yaxis_title="평균값"
        )
        
        # R 차트
        r_fig = go.Figure()
        r_fig.add_trace(go.Scatter(
            x=list(range(1, n_samples+1)),
            y=r_values,
            mode='lines+markers',
            name='R',
            line=dict(color='purple', width=2),
            marker=dict(size=8)
        ))
        
        r_fig.add_hline(y=r_ucl, line_dash="dash", line_color="red",
                       annotation_text=f"UCL: {r_ucl:.3f}")
        r_fig.add_hline(y=r_mean, line_dash="solid", line_color="green",
                       annotation_text=f"CL: {r_mean:.3f}")
        r_fig.add_hline(y=r_lcl, line_dash="dash", line_color="red",
                       annotation_text=f"LCL: {r_lcl:.3f}")
        
        r_fig.update_layout(
            title="R 관리도",
            xaxis_title="샘플 번호",
            yaxis_title="범위(R)"
        )
        
        # 공정능력지수 계산
        usl = target + 0.3  # 상한 규격
        lsl = target - 0.3  # 하한 규격
        
        all_data = samples_array.flatten()
        process_std = all_data.std()
        process_mean = all_data.mean()
        
        cp = (usl - lsl) / (6 * process_std)
        cpu = (usl - process_mean) / (3 * process_std)
        cpl = (process_mean - lsl) / (3 * process_std)
        cpk = min(cpu, cpl)
        
        cp_color = "success" if cp >= 1.33 else "warning" if cp >= 1.0 else "danger"
        cpk_color = "success" if cpk >= 1.33 else "warning" if cpk >= 1.0 else "danger"
        
        # 정규성 검정 차트
        norm_fig = go.Figure()
        norm_fig.add_trace(go.Histogram(
            x=all_data,
            nbinsx=20,
            name='실제 분포',
            histnorm='probability density'
        ))
        
        # 정규분포 곡선
        x_range = np.linspace(all_data.min(), all_data.max(), 100)
        norm_pdf = (1/np.sqrt(2*np.pi*process_std**2)) * np.exp(-(x_range-process_mean)**2/(2*process_std**2))
        
        norm_fig.add_trace(go.Scatter(
            x=x_range,
            y=norm_pdf,
            mode='lines',
            name='정규분포',
            line=dict(color='red', width=2)
        ))
        
        norm_fig.update_layout(
            title="정규성 검정",
            xaxis_title="측정값",
            yaxis_title="확률밀도"
        )
        
        return (
            xbar_fig,
            r_fig,
            html.Span(f"{cp:.2f}", className=f"text-{cp_color}"),
            html.Span(f"{cpk:.2f}", className=f"text-{cpk_color}"),
            norm_fig
        )
    
    # 불량 파레토 차트
    @app.callback(
        Output('defect-pareto-chart', 'figure'),
        [Input('defect-start-date', 'value'),
         Input('defect-end-date', 'value')]
    )
    def update_defect_pareto(start_date, end_date):
        """불량 파레토 차트 업데이트"""
        conn = sqlite3.connect('data/database.db')
        
        try:
            query = """
                SELECT 
                    dt.defect_name,
                    COUNT(*) as count,
                    SUM(dh.defect_qty) as total_qty
                FROM defect_history dh
                JOIN defect_types dt ON dh.defect_code = dt.defect_code
                WHERE dh.defect_date BETWEEN ? AND ?
                GROUP BY dt.defect_name
                ORDER BY total_qty DESC
            """
            
            df = pd.read_sql_query(query, conn, params=[start_date, end_date])
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="해당 기간에 불량 데이터가 없습니다",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            else:
                # 누적 비율 계산
                df['cumulative_percent'] = (df['total_qty'].cumsum() / df['total_qty'].sum()) * 100
                
                fig = go.Figure()
                
                # 막대 그래프
                fig.add_trace(go.Bar(
                    x=df['defect_name'],
                    y=df['total_qty'],
                    name='불량 수량',
                    marker_color='lightblue',
                    yaxis='y'
                ))
                
                # 누적 곡선
                fig.add_trace(go.Scatter(
                    x=df['defect_name'],
                    y=df['cumulative_percent'],
                    name='누적 비율',
                    line=dict(color='red', width=2),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
                
                # 80% 기준선
                fig.add_hline(y=80, line_dash="dash", line_color="green",
                            annotation_text="80%", yaxis='y2')
                
                fig.update_layout(
                    title="불량 유형별 파레토 차트",
                    xaxis_title="불량 유형",
                    yaxis=dict(title="불량 수량", side='left'),
                    yaxis2=dict(title="누적 비율 (%)", side='right', overlaying='y', range=[0, 105])
                )
            
            return fig
            
        except Exception as e:
            logger.error(f"파레토 차트 조회 오류: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"오류: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        finally:
            conn.close()
    
    # 검사 모달 토글
    @app.callback(
        Output('inspection-modal', 'is_open'),
        [Input('new-inspection-btn', 'n_clicks'),
         Input('close-inspection-modal', 'n_clicks'),
         Input('save-inspection-btn', 'n_clicks')],
        [State('inspection-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_inspection_modal(new_clicks, close_clicks, save_clicks, is_open):
        """검사 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 불량 모달 토글
    @app.callback(
        Output('defect-modal', 'is_open'),
        [Input('new-defect-btn', 'n_clicks'),
         Input('close-defect-modal', 'n_clicks'),
         Input('save-defect-btn', 'n_clicks')],
        [State('defect-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_defect_modal(new_clicks, close_clicks, save_clicks, is_open):
        """불량 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 성적서 모달 토글
    @app.callback(
        Output('certificate-modal', 'is_open'),
        [Input('new-certificate-btn', 'n_clicks'),
         Input('close-certificate-modal', 'n_clicks'),
         Input('save-certificate-btn', 'n_clicks')],
        [State('certificate-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_certificate_modal(new_clicks, close_clicks, save_clicks, is_open):
        """성적서 모달 토글"""
        ctx = callback_context
        if ctx.triggered:
            return not is_open
        return is_open
    
    # 검사 저장
    @app.callback(
        Output('inspection-modal-message', 'children'),
        Input('save-inspection-btn', 'n_clicks'),
        [State('modal-inspection-type', 'value'),
         State('modal-inspection-date', 'value'),
         State('modal-inspection-item', 'value'),
         State('modal-lot-number', 'value'),
         State('modal-inspection-qty', 'value'),
         State('modal-sample-qty', 'value'),
         State('modal-pass-qty', 'value'),
         State('modal-inspection-result', 'value'),
         State('modal-inspection-remarks', 'value'),
         State('session-store', 'data')],
        prevent_initial_call=True
    )
    def save_inspection(n_clicks, inspection_type, inspection_date, item_code,
                       lot_number, inspection_qty, sample_qty, pass_qty,
                       result, remarks, session_data):
        """검사 데이터 저장"""
        if not all([inspection_date, item_code, inspection_qty, sample_qty, pass_qty]):
            return dbc.Alert("모든 필수 항목을 입력하세요.", color="warning")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 검사번호 생성
            prefix = {
                'incoming': 'INC',
                'process': 'PRC',
                'final': 'FIN'
            }.get(inspection_type, 'INS')
            
            cursor.execute(f"""
                SELECT COUNT(*) FROM {inspection_type}_inspection 
                WHERE inspection_date = ?
            """, (inspection_date,))
            count = cursor.fetchone()[0]
            inspection_no = f"{prefix}-{inspection_date.replace('-', '')}-{count+1:04d}"
            
            # 사용자 ID
            user_id = session_data.get('user_id', 1) if session_data else 1
            
            # 불량 수량 계산
            failed_qty = int(sample_qty) - int(pass_qty)
            
            # 데이터 저장
            if inspection_type == 'incoming':
                cursor.execute("""
                    INSERT INTO incoming_inspection
                    (inspection_no, inspection_date, item_code, lot_number,
                     received_qty, sample_qty, passed_qty, failed_qty,
                     inspection_result, inspector_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (inspection_no, inspection_date, item_code, lot_number,
                      inspection_qty, sample_qty, pass_qty, failed_qty,
                      result, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"검사 데이터 저장 완료: {inspection_no}")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"),
                 f"검사 번호 {inspection_no}가 등록되었습니다!"],
                color="success"
            )
            
        except Exception as e:
            logger.error(f"검사 저장 실패: {e}")
            return dbc.Alert(f"저장 중 오류가 발생했습니다: {str(e)}", color="danger")
    
    # 품질관리 설정 저장
    @app.callback(
        Output('quality-settings-message', 'children'),
        Input('save-quality-settings-btn', 'n_clicks'),
        [State('default-sampling-rate', 'value'),
         State('reinspection-criteria', 'value'),
         State('auto-approval-switch', 'value'),
         State('defect-notification-switch', 'value'),
         State('spc-rules', 'value'),
         State('target-cpk', 'value'),
         State('min-sample-size', 'value'),
         State('certificate-template', 'value'),
         State('auto-cert-number', 'value'),
         State('digital-signature', 'value')],
        prevent_initial_call=True
    )
    def save_quality_settings(n_clicks, sampling_rate, reinspection, auto_approval,
                            defect_notification, spc_rules, target_cpk, min_sample,
                            cert_template, auto_cert_no, digital_signature):
        """품질관리 설정 저장"""
        try:
            settings = {
                'inspection': {
                    'default_sampling_rate': sampling_rate,
                    'reinspection_criteria': reinspection,
                    'auto_approval': auto_approval,
                    'defect_notification': defect_notification
                },
                'spc': {
                    'rules': spc_rules,
                    'target_cpk': target_cpk,
                    'min_sample_size': min_sample
                },
                'certificate': {
                    'template': cert_template,
                    'auto_number': auto_cert_no,
                    'digital_signature': digital_signature
                }
            }
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value)
                VALUES ('quality_settings', ?)
            """, (json.dumps(settings),))
            
            conn.commit()
            conn.close()
            
            logger.info("품질관리 설정 저장 완료")
            
            return dbc.Alert(
                [html.I(className="fas fa-check-circle me-2"), "설정이 저장되었습니다!"],
                color="success",
                dismissable=True
            )
            
        except Exception as e:
            logger.error(f"품질관리 설정 저장 실패: {e}")
            return dbc.Alert(
                f"저장 중 오류가 발생했습니다: {str(e)}",
                color="danger",
                dismissable=True
            )
    
    # 품질 트렌드 차트
    @app.callback(
        Output('quality-trend-chart', 'figure'),
        Input('quality-analysis-period', 'value')
    )
    def update_quality_trend(period):
        """품질 트렌드 차트 업데이트"""
        # 더미 데이터 생성
        if period == 'daily':
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            x_title = "일자"
        elif period == 'weekly':
            dates = pd.date_range(end=datetime.now(), periods=12, freq='W')
            x_title = "주차"
        elif period == 'monthly':
            dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
            x_title = "월"
        else:  # yearly
            dates = pd.date_range(end=datetime.now(), periods=3, freq='Y')
            x_title = "연도"
        
        # 더미 데이터
        np.random.seed(42)
        defect_rate = np.random.uniform(0.5, 3.0, len(dates))
        pass_rate = 100 - defect_rate
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=pass_rate,
            mode='lines+markers',
            name='합격률',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=defect_rate,
            mode='lines+markers',
            name='불량률',
            line=dict(color='red', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        # 목표선
        fig.add_hline(y=98, line_dash="dash", line_color="blue",
                     annotation_text="목표 합격률: 98%")
        
        fig.update_layout(
            title=f"품질 트렌드 ({period})",
            xaxis_title=x_title,
            yaxis=dict(title="합격률 (%)", side='left', range=[95, 100]),
            yaxis2=dict(title="불량률 (%)", side='right', overlaying='y', range=[0, 5]),
            hovermode='x unified'
        )
        
        return fig
    
    # 품질 비용 분석 차트
    @app.callback(
        Output('quality-cost-chart', 'figure'),
        Input('quality-analysis-period', 'value')
    )
    def update_quality_cost(period):
        """품질 비용 분석 차트"""
        # 더미 데이터
        categories = ['예방비용', '평가비용', '내부실패비용', '외부실패비용']
        values = [500000, 300000, 200000, 100000]
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=categories,
            values=values,
            hole=0.4,
            marker_colors=['#0066cc', '#28a745', '#ffc107', '#dc3545']
        ))
        
        fig.update_layout(
            title="품질 비용 구성",
            annotations=[{
                'text': f'총 비용<br>₩{sum(values):,.0f}',
                'x': 0.5, 'y': 0.5,
                'font_size': 20,
                'showarrow': False
            }]
        )
        
        return fig
    
    # 공급업체별 품질 차트
    @app.callback(
        Output('supplier-quality-chart', 'figure'),
        Input('quality-analysis-period', 'value')
    )
    def update_supplier_quality(period):
        """공급업체별 품질 현황"""
        # 더미 데이터
        suppliers = ['공급업체A', '공급업체B', '공급업체C', '공급업체D', '공급업체E']
        pass_rates = [99.2, 98.5, 97.8, 99.5, 96.5]
        inspection_counts = [120, 85, 95, 110, 75]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=suppliers,
            y=pass_rates,
            name='합격률 (%)',
            marker_color='lightblue',
            text=[f'{rate:.1f}%' for rate in pass_rates],
            textposition='auto',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=suppliers,
            y=inspection_counts,
            name='검사 건수',
            line=dict(color='red', width=2),
            marker=dict(size=10),
            yaxis='y2'
        ))
        
        # 목표선
        fig.add_hline(y=98, line_dash="dash", line_color="green",
                     annotation_text="목표: 98%", yaxis='y')
        
        fig.update_layout(
            title="공급업체별 품질 현황",
            xaxis_title="공급업체",
            yaxis=dict(title="합격률 (%)", side='left', range=[94, 100]),
            yaxis2=dict(title="검사 건수", side='right', overlaying='y'),
            hovermode='x unified'
        )
        
        return fig
