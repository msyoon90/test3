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
                           u.
