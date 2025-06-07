# api/__init__.py

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_api_app(config):
    """API 애플리케이션 생성"""
    app = Flask(__name__)
    
    # 설정
    app.config['JWT_SECRET_KEY'] = config['authentication']['jwt_secret_key']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config['authentication']['jwt_access_token_expires']
    
    # CORS 설정
    CORS(app, origins=config['api']['cors_origins'])
    
    # JWT 설정
    jwt = JWTManager(app)
    
    # API 설정
    api = Api(app)
    
    # 라우트 등록
    from .routes import register_routes
    register_routes(api)
    
    return app, api
