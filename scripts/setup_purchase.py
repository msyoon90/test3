# File: scripts/setup_purchase.py

import os
import sys

# 현재 스크립트의 디렉토리
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Python 경로에 부모 디렉토리 추가
sys.path.insert(0, parent_dir)

print("🚀 구매관리 모듈 설정 시작...\n")

# 1. 데이터베이스 초기화
print("1. 데이터베이스 초기화 중...")
try:
    from init_all_database import init_all_tables
    init_all_tables()
except Exception as e:
    print(f"❌ 데이터베이스 초기화 실패: {e}")
    sys.exit(1)

# 2. 구매관리 샘플 데이터 추가
print("\n2. 구매관리 샘플 데이터 추가 중...")
try:
    from add_purchase_sample_data import add_purchase_sample_data
    os.chdir(current_dir)  # scripts 디렉토리에서 실행
    add_purchase_sample_data()
except Exception as e:
    print(f"❌ 샘플 데이터 추가 실패: {e}")

print("\n✅ 구매관리 모듈 설정 완료!")
print("\n💡 이제 다음 명령으로 앱을 실행하세요:")
print("   cd ..")
print("   python app.py")