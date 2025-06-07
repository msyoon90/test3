# api/auth.py - API 인증 및 권한 관리

from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import sqlite3
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

class Login(Resource):
    """로그인 API"""
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('password', required=True, help='Password is required')
        args = parser.parse_args()
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 사용자 확인
            cursor.execute("""
                SELECT id, username, role FROM users 
                WHERE username = ? AND password = ?
            """, (args['username'], args['password']))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # JWT 토큰 생성
                access_token = create_access_token(
                    identity={
                        'user_id': user[0],
                        'username': user[1],
                        'role': user[2]
                    }
                )
                
                return {
                    'access_token': access_token,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'role': user[2]
                    }
                }, 200
            else:
                return {'message': 'Invalid username or password'}, 401
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'message': 'Internal server error'}, 500

class CurrentUser(Resource):
    """현재 사용자 정보 API"""
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {
            'user': current_user
        }, 200

class UserList(Resource):
    """사용자 목록 API"""
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        
        # 관리자만 접근 가능
        if current_user['role'] != 'admin':
            return {'message': 'Access denied'}, 403
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, created_at 
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'created_at': row[3]
                })
            
            conn.close()
            
            return {'users': users}, 200
            
        except Exception as e:
            logger.error(f"Get users error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def post(self):
        """새 사용자 생성"""
        current_user = get_jwt_identity()
        
        # 관리자만 접근 가능
        if current_user['role'] != 'admin':
            return {'message': 'Access denied'}, 403
        
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role', default='user')
        args = parser.parse_args()
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 중복 확인
            cursor.execute("SELECT id FROM users WHERE username = ?", (args['username'],))
            if cursor.fetchone():
                return {'message': 'Username already exists'}, 400
            
            # 사용자 생성
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (args['username'], args['password'], args['role']))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'message': 'User created successfully',
                'user': {
                    'id': user_id,
                    'username': args['username'],
                    'role': args['role']
                }
            }, 201
            
        except Exception as e:
            logger.error(f"Create user error: {e}")
            return {'message': 'Internal server error'}, 500

def check_permission(required_role):
    """권한 확인 데코레이터"""
    def decorator(f):
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            
            # role 체크
            role_hierarchy = {
                'admin': 3,
                'manager': 2,
                'user': 1,
                'guest': 0
            }
            
            if role_hierarchy.get(current_user['role'], 0) < role_hierarchy.get(required_role, 0):
                return {'message': 'Insufficient permissions'}, 403
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    return decorator# api/auth.py - API 인증 및 권한 관리

from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import sqlite3
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

class Login(Resource):
    """로그인 API"""
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('password', required=True, help='Password is required')
        args = parser.parse_args()
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 사용자 확인
            cursor.execute("""
                SELECT id, username, role FROM users 
                WHERE username = ? AND password = ?
            """, (args['username'], args['password']))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # JWT 토큰 생성
                access_token = create_access_token(
                    identity={
                        'user_id': user[0],
                        'username': user[1],
                        'role': user[2]
                    }
                )
                
                return {
                    'access_token': access_token,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'role': user[2]
                    }
                }, 200
            else:
                return {'message': 'Invalid username or password'}, 401
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'message': 'Internal server error'}, 500

class CurrentUser(Resource):
    """현재 사용자 정보 API"""
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {
            'user': current_user
        }, 200

class UserList(Resource):
    """사용자 목록 API"""
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        
        # 관리자만 접근 가능
        if current_user['role'] != 'admin':
            return {'message': 'Access denied'}, 403
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, created_at 
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'created_at': row[3]
                })
            
            conn.close()
            
            return {'users': users}, 200
            
        except Exception as e:
            logger.error(f"Get users error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def post(self):
        """새 사용자 생성"""
        current_user = get_jwt_identity()
        
        # 관리자만 접근 가능
        if current_user['role'] != 'admin':
            return {'message': 'Access denied'}, 403
        
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        parser.add_argument('role', default='user')
        args = parser.parse_args()
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 중복 확인
            cursor.execute("SELECT id FROM users WHERE username = ?", (args['username'],))
            if cursor.fetchone():
                return {'message': 'Username already exists'}, 400
            
            # 사용자 생성
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (args['username'], args['password'], args['role']))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'message': 'User created successfully',
                'user': {
                    'id': user_id,
                    'username': args['username'],
                    'role': args['role']
                }
            }, 201
            
        except Exception as e:
            logger.error(f"Create user error: {e}")
            return {'message': 'Internal server error'}, 500

def check_permission(required_role):
    """권한 확인 데코레이터"""
    def decorator(f):
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            
            # role 체크
            role_hierarchy = {
                'admin': 3,
                'manager': 2,
                'user': 1,
                'guest': 0
            }
            
            if role_hierarchy.get(current_user['role'], 0) < role_hierarchy.get(required_role, 0):
                return {'message': 'Insufficient permissions'}, 403
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    return decorator
