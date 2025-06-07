# api/routes.py - API 라우트 정의

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3
import pandas as pd
from datetime import datetime
import logging

from .auth import Login, CurrentUser, UserList, check_permission

logger = logging.getLogger(__name__)

# MES API
class ProductionList(Resource):
    """생산 실적 목록 API"""
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_date', type=str, default=None)
        parser.add_argument('end_date', type=str, default=None)
        parser.add_argument('limit', type=int, default=100)
        args = parser.parse_args()
        
        try:
            conn = sqlite3.connect('data/database.db')
            
            query = "SELECT * FROM work_logs WHERE 1=1"
            params = []
            
            if args['start_date']:
                query += " AND work_date >= ?"
                params.append(args['start_date'])
            
            if args['end_date']:
                query += " AND work_date <= ?"
                params.append(args['end_date'])
            
            query += " ORDER BY work_date DESC, created_at DESC LIMIT ?"
            params.append(args['limit'])
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return {
                'data': df.to_dict('records'),
                'total': len(df)
            }, 200
            
        except Exception as e:
            logger.error(f"Get production list error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def post(self):
        """생산 실적 등록"""
        parser = reqparse.RequestParser()
        parser.add_argument('lot_number', required=True)
        parser.add_argument('work_date', required=True)
        parser.add_argument('process', required=True)
        parser.add_argument('plan_qty', type=int, required=True)
        parser.add_argument('prod_qty', type=int, required=True)
        parser.add_argument('defect_qty', type=int, default=0)
        args = parser.parse_args()
        
        current_user = get_jwt_identity()
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO work_logs 
                (lot_number, work_date, process, worker_id, 
                 plan_qty, prod_qty, defect_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (args['lot_number'], args['work_date'], args['process'],
                  current_user['user_id'], args['plan_qty'], 
                  args['prod_qty'], args['defect_qty']))
            
            work_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'message': 'Production record created',
                'id': work_id
            }, 201
            
        except Exception as e:
            logger.error(f"Create production record error: {e}")
            return {'message': 'Internal server error'}, 500

# 재고 API
class InventoryList(Resource):
    """재고 현황 API"""
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('category', type=str, default=None)
        parser.add_argument('low_stock', type=bool, default=False)
        args = parser.parse_args()
        
        try:
            conn = sqlite3.connect('data/database.db')
            
            query = "SELECT * FROM item_master WHERE 1=1"
            params = []
            
            if args['category']:
                query += " AND category = ?"
                params.append(args['category'])
            
            if args['low_stock']:
                query += " AND current_stock < safety_stock"
            
            query += " ORDER BY item_code"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return {
                'data': df.to_dict('records'),
                'total': len(df)
            }, 200
            
        except Exception as e:
            logger.error(f"Get inventory list error: {e}")
            return {'message': 'Internal server error'}, 500

class StockMovement(Resource):
    """재고 이동 API"""
    @jwt_required()
    def post(self):
