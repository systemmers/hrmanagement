"""
Personal 관계 데이터 마이그레이션 스크립트

엑셀 데이터를 PostgreSQL DB로 마이그레이션합니다.
"""
import os
import sys
import pandas as pd
import numpy as np

# 프로젝트 루트 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 환경변수 설정
os.environ['DATABASE_URL'] = 'postgresql://hrm_user:hrm_secure_password_2024@localhost:6543/hrmanagement_db'

from app import create_app
from app.database import db
from sqlalchemy import text


def clean_value(val):
    """NaN, NaT 등을 None으로 변환"""
    if pd.isna(val) or val is np.nan:
        return None
    if isinstance(val, str) and val.strip() == '':
        return None
    return val


def clean_int(val):
    """정수값 정리"""
    val = clean_value(val)
    if val is None:
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def migrate_personal_educations(xlsx):
    """개인 학력 데이터 마이그레이션"""
    # DEPRECATED: PersonalEducation merged into Education

    df = pd.read_excel(xlsx, sheet_name='PersonalEducation')

    count = 0
    for _, row in df.iterrows():
        edu = PersonalEducation(
            profile_id=clean_int(row['profile_id']),
            school_type=clean_value(row.get('school_type')),
            school_name=clean_value(row.get('school_name')),
            major=clean_value(row.get('major')),
            degree=clean_value(row.get('degree')),
            admission_date=clean_value(row.get('admission_date')),
            graduation_date=clean_value(row.get('graduation_date')),
            status=clean_value(row.get('graduation_status')),  # graduation_status -> status
            gpa=clean_value(row.get('gpa')),
            notes=clean_value(row.get('note'))  # note -> notes
        )
        db.session.add(edu)
        count += 1

    db.session.commit()
    return count


def main():
    """메인 실행 함수"""
    app = create_app()

    with app.app_context():
        xlsx_path = '.dev_docs/sample/hr_test_data_complete_v2.xlsx'
        xlsx = pd.ExcelFile(xlsx_path)

        print("=" * 50)
        print("Personal 관계 데이터 마이그레이션 시작")
        print("=" * 50)

        migrations = [
            ('PersonalEducation (개인학력)', migrate_personal_educations),
        ]

        results = []
        for name, func in migrations:
            try:
                count = func(xlsx)
                print(f"  {name}: {count}건 마이그레이션 완료")
                results.append((name, count, 'SUCCESS'))
            except Exception as e:
                print(f"  {name}: 오류 - {str(e)}")
                results.append((name, 0, f'ERROR: {str(e)[:50]}'))
                db.session.rollback()

        print("=" * 50)
        print("마이그레이션 결과 요약")
        print("=" * 50)
        total = 0
        for name, count, status in results:
            print(f"  {name}: {count}건 ({status})")
            if status == 'SUCCESS':
                total += count
        print(f"\n총 {total}건 마이그레이션 완료")


if __name__ == '__main__':
    main()
