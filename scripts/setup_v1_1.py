# File: scripts/setup_v1_1.py
# Smart MES-ERP V1.1 설정 스크립트

import os
import sys
import sqlite3
import yaml
import shutil
from datetime import datetime

print("=" * 60)
print("Smart MES-ERP V1.1 설정 스크립트")
print("=" * 60)
print()

# 프로젝트 루트 디렉토리로 이동
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("1. 모듈 디렉토리 생성 중...")

# 품질관리 모듈 디렉토리 생성
quality_dirs = [
    'modules/quality',
    'modules/quality/templates',
    'modules/quality/static'
]

for dir_path in quality_dirs:
    os.makedirs(dir_path, exist_ok=True)
    print(f"   ✅ {dir_path} 생성")

# __init__.py 파일 생성
init_content = '''"""
품질관리 모듈
Quality Management Module for Smart MES-ERP V1.1
"""

__version__ = "1.1.0"
__author__ = "Smart Factory Team"
'''

with open('modules/quality/__init__.py', 'w', encoding='utf-8') as f:
    f.write(init_content)
print("   ✅ __init__.py 생성")

print("\n2. 데이터베이스 테이블 생성 중...")

# 품질관리 테이블 생성
try:
    from create_quality_tables import create_quality_tables
    create_quality_tables()
except Exception as e:
    print(f"   ⚠️  테이블 생성 중 오류: {e}")
    print("   create_quality_tables.py를 먼저 실행하세요.")

print("\n3. 설정 파일 업데이트 중...")

# config.yaml 업데이트
config_path = 'config.yaml'
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 버전 업데이트
    config['system']['version'] = '1.1.0'
    
    # 품질관리 모듈 추가
    if 'modules' not in config:
        config['modules'] = {}
    config['modules']['quality'] = True
    
    # 품질관리 설정 추가
    config['quality'] = {
        'default_sampling_rate': 10,
        'target_defect_rate': 2.0,
        'spc_rules': ['rule1', 'rule2'],
        'calibration_reminder_days': 30
    }
    
    # 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    print("   ✅ config.yaml 업데이트 완료")
else:
    print("   ⚠️  config.yaml 파일을 찾을 수 없습니다.")

print("\n4. 샘플 데이터 생성 중...")

# 샘플 검사 데이터 추가
conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()

try:
    # 샘플 입고 검사 데이터
    sample_inspections = [
        ('INC-20250607-0001', '2025-06-07', 'PO-20250607-0001', 'ITEM001', 'LOT-001', 
         100, 10, 10, 0, 'pass', None, None, 1),
        ('INC-20250607-0002', '2025-06-07', 'PO-20250607-0002', 'ITEM002', 'LOT-002', 
         200, 20, 19, 1, 'pass', 'D002', '외관 불량 1개 발견', 1),
        ('INC-20250606-0001', '2025-06-06', 'PO-20250606-0001', 'ITEM003', 'LOT-003', 
         150, 15, 14, 1, 'conditional', 'D001', '치수 불량 1개, 조건부 합격', 1)
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO incoming_inspection
        (inspection_no, inspection_date, po_number, item_code, lot_number,
         received_qty, sample_qty, passed_qty, failed_qty, inspection_result,
         defect_type, defect_description, inspector_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_inspections)
    
    # 샘플 불량 이력 데이터
    sample_defects = [
        ('incoming', 'INC-20250607-0002', '2025-06-07', 'ITEM002', 'D002', 
         1, 5.0, '표면 스크래치', '재작업 실시', '표면 처리 공정 개선', '품질팀', 'closed', '2025-06-07'),
        ('process', 'PRC-20250606-0001', '2025-06-06', 'ITEM001', 'D001', 
         2, 2.0, '가공 공차 초과', '재가공', '공구 교체 주기 단축', '생산팀', 'in_progress', None)
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO defect_history
        (inspection_type, inspection_no, defect_date, item_code, defect_code,
         defect_qty, defect_rate, cause_analysis, corrective_action,
         preventive_action, responsible_dept, status, closed_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_defects)
    
    conn.commit()
    print("   ✅ 샘플 데이터 생성 완료")
    
except Exception as e:
    print(f"   ⚠️  샘플 데이터 생성 중 오류: {e}")
    conn.rollback()

conn.close()

print("\n5. 파일 권한 설정 중...")

# 디렉토리 권한 설정
dirs_to_check = ['data', 'logs', 'backups', 'modules/quality']
for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        try:
            os.chmod(dir_path, 0o755)
            print(f"   ✅ {dir_path} 권한 설정")
        except:
            print(f"   ⚠️  {dir_path} 권한 설정 실패")

print("\n6. 종속성 패키지 확인...")

required_packages = [
    'dash==2.14.0',
    'dash-bootstrap-components==1.5.0',
    'plotly==5.17.0',
    'pandas==2.0.3',
    'numpy==1.24.3',
    'scipy==1.10.1',  # SPC 분석용 추가
    'PyYAML==6.0.1'
]

print("   필요한 패키지:")
for package in required_packages:
    print(f"   - {package}")

print("\n   다음 명령으로 설치하세요:")
print("   pip install -r requirements.txt")

print("\n7. app.py 업데이트 안내")
print("=" * 60)
print("app.py 파일에 다음 코드를 추가해야 합니다:")
print()
print("1) 네비게이션 바에 품질관리 메뉴 추가:")
print('   dbc.NavItem(dbc.NavLink("품질관리", href="/quality", id="nav-quality")) if config["modules"]["quality"] else None,')
print()
print("2) 페이지 라우팅에 추가:")
print("   elif pathname == '/quality':")
print("       try:")
print("           from modules.quality.layouts import create_quality_layout")
print("           return create_quality_layout()")
print("       except ImportError as e:")
print('           logger.error(f"품질관리 모듈 로드 실패: {e}")')
print('           return error_layout("품질관리", e)')
print()
print("3) 콜백 등록 추가:")
print("   try:")
print("       from modules.quality.callbacks import register_quality_callbacks")
print("       register_quality_callbacks(app)")
print("   except ImportError:")
print('       logger.warning("품질관리 모듈 콜백을 불러올 수 없습니다.")')
print()
print("4) 설정 페이지에 품질관리 모듈 스위치 추가")
print("=" * 60)

print("\n✅ V1.1 설정 완료!")
print("\n다음 단계:")
print("1. pip install scipy==1.10.1  # SPC 분석용 패키지 설치")
print("2. app.py 파일 수동 업데이트")
print("3. python app.py 실행")
print("\n버전: V1.0 → V1.1")
print("추가된 기능: 품질관리 모듈 (검사, 불량, SPC, 성적서)")
