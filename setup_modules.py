import os

def create_callback_files():
    """각 모듈의 callbacks.py 파일 생성"""
    
    modules = {
        'mes': '''from dash import Input, Output, State
import logging

logger = logging.getLogger(__name__)

def register_mes_callbacks(app):
    """MES 모듈 콜백 등록"""
    pass
''',
        'inventory': '''from dash import Input, Output, State
import logging

logger = logging.getLogger(__name__)

def register_inventory_callbacks(app):
    """재고관리 모듈 콜백 등록"""
    pass
''',
        'purchase': '''from dash import Input, Output, State
import logging

logger = logging.getLogger(__name__)

def register_purchase_callbacks(app):
    """구매관리 모듈 콜백 등록"""
    pass
'''
    }
    
    for module, content in modules.items():
        dir_path = f'modules/{module}'
        os.makedirs(dir_path, exist_ok=True)
        
        # __init__.py 생성
        init_path = f'{dir_path}/__init__.py'
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(f'from .layouts import create_{module}_layout\n')
                f.write(f'from .callbacks import register_{module}_callbacks\n\n')
                f.write(f"__all__ = ['create_{module}_layout', 'register_{module}_callbacks']\n")
            print(f"✅ {init_path} 생성")
        
        # callbacks.py 생성
        callbacks_path = f'{dir_path}/callbacks.py'
        with open(callbacks_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {callbacks_path} 생성")
        
        # layouts.py 생성 (없으면)
        layouts_path = f'{dir_path}/layouts.py'
        if not os.path.exists(layouts_path):
            with open(layouts_path, 'w', encoding='utf-8') as f:
                f.write(f'''import dash_bootstrap_components as dbc
from dash import html

def create_{module}_layout():
    """레이아웃 생성"""
    return dbc.Container([
        html.H1("{module.upper()} 모듈"),
        html.P("모듈이 정상적으로 로드되었습니다."),
        html.Div(id="{module}-tab-content")
    ])
''')
            print(f"✅ {layouts_path} 생성")

if __name__ == "__main__":
    print("🔧 모듈 파일 생성 시작...")
    create_callback_files()
    print("\n✅ 완료! 이제 py app.py를 실행하세요.")