"""
Phase 3-3: 데이터 마이그레이션 스크립트
personal_profiles 데이터 -> profiles 테이블 복사
employees 데이터 -> profiles 생성 및 연결
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from datetime import datetime


def migrate_personal_profiles_to_profiles():
    """personal_profiles -> profiles 데이터 복사"""
    print("=" * 60)
    print("Step 1: personal_profiles -> profiles 마이그레이션")
    print("=" * 60)

    # 직접 SQL로 데이터 복사 (가장 안전)
    sql = """
    INSERT INTO profiles (
        user_id, name, english_name, chinese_name, photo,
        birth_date, lunar_birth, gender,
        mobile_phone, home_phone, email,
        postal_code, address, detailed_address,
        resident_number, nationality,
        blood_type, religion, hobby, specialty, disability_info, marital_status,
        actual_postal_code, actual_address, actual_detailed_address,
        emergency_contact, emergency_relation,
        is_public, created_at, updated_at
    )
    SELECT
        user_id, name, english_name, chinese_name, photo,
        birth_date, lunar_birth, gender,
        mobile_phone, home_phone, email,
        postal_code, address, detailed_address,
        resident_number, nationality,
        blood_type, religion, hobby, specialty, disability_info, marital_status,
        actual_postal_code, actual_address, actual_detailed_address,
        emergency_contact, emergency_relation,
        is_public, created_at, updated_at
    FROM personal_profiles
    WHERE NOT EXISTS (
        SELECT 1 FROM profiles WHERE profiles.user_id = personal_profiles.user_id
    );
    """

    result = db.session.execute(db.text(sql))
    db.session.commit()
    print(f"  - personal_profiles에서 {result.rowcount}개 프로필 복사 완료")

    return result.rowcount


def migrate_employees_to_profiles():
    """employees 데이터 -> profiles 생성 및 연결"""
    print("\n" + "=" * 60)
    print("Step 2: employees -> profiles 생성 및 연결")
    print("=" * 60)

    # 아직 profile_id가 없는 employees에 대해 profiles 생성
    sql_insert = """
    INSERT INTO profiles (
        user_id, name, english_name, chinese_name, photo,
        birth_date, lunar_birth, gender,
        mobile_phone, home_phone, email,
        postal_code, address, detailed_address,
        resident_number, nationality,
        blood_type, religion, hobby, specialty, disability_info, marital_status,
        actual_postal_code, actual_address, actual_detailed_address,
        emergency_contact, emergency_relation,
        is_public, created_at
    )
    SELECT
        NULL as user_id,  -- employee는 user_id 없을 수 있음
        e.name, e.english_name, e.chinese_name, e.photo,
        e.birth_date, e.lunar_birth, e.gender,
        e.mobile_phone, e.home_phone, e.email,
        e.postal_code, e.address, e.detailed_address,
        e.resident_number, e.nationality,
        e.blood_type, e.religion, e.hobby, e.specialty, e.disability_info, e.marital_status,
        e.actual_postal_code, e.actual_address, e.actual_detailed_address,
        e.emergency_contact, e.emergency_relation,
        FALSE as is_public, NOW()
    FROM employees e
    WHERE e.profile_id IS NULL
    RETURNING id, name;
    """

    result = db.session.execute(db.text(sql_insert))
    new_profiles = result.fetchall()
    db.session.commit()
    print(f"  - {len(new_profiles)}개의 새 프로필 생성됨")

    # employees.profile_id 업데이트 (이름+이메일 매칭)
    sql_update = """
    UPDATE employees e
    SET profile_id = p.id
    FROM profiles p
    WHERE e.profile_id IS NULL
      AND e.name = p.name
      AND (e.email = p.email OR (e.email IS NULL AND p.email IS NULL))
      AND p.user_id IS NULL;
    """

    result = db.session.execute(db.text(sql_update))
    db.session.commit()
    print(f"  - {result.rowcount}개 직원-프로필 연결 완료")

    return len(new_profiles)


def verify_migration():
    """마이그레이션 결과 검증"""
    print("\n" + "=" * 60)
    print("Step 3: 마이그레이션 검증")
    print("=" * 60)

    # 전체 통계
    stats = {}

    # profiles 테이블 카운트
    result = db.session.execute(db.text("SELECT COUNT(*) FROM profiles"))
    stats['profiles_total'] = result.scalar()

    # personal_profiles 테이블 카운트
    result = db.session.execute(db.text("SELECT COUNT(*) FROM personal_profiles"))
    stats['personal_profiles_total'] = result.scalar()

    # employees 테이블 카운트
    result = db.session.execute(db.text("SELECT COUNT(*) FROM employees"))
    stats['employees_total'] = result.scalar()

    # profile_id가 있는 employees 카운트
    result = db.session.execute(db.text("SELECT COUNT(*) FROM employees WHERE profile_id IS NOT NULL"))
    stats['employees_with_profile'] = result.scalar()

    # profile_id가 없는 employees 카운트
    result = db.session.execute(db.text("SELECT COUNT(*) FROM employees WHERE profile_id IS NULL"))
    stats['employees_without_profile'] = result.scalar()

    # user_id가 있는 profiles 카운트 (개인 계정)
    result = db.session.execute(db.text("SELECT COUNT(*) FROM profiles WHERE user_id IS NOT NULL"))
    stats['profiles_with_user'] = result.scalar()

    print(f"""
  통계 결과:
  ----------------------------------------
  profiles 테이블 총 레코드:        {stats['profiles_total']}
  personal_profiles 테이블:         {stats['personal_profiles_total']}
  employees 테이블 총 레코드:       {stats['employees_total']}
  profile_id 연결된 직원:           {stats['employees_with_profile']}
  profile_id 미연결 직원:           {stats['employees_without_profile']}
  user_id 있는 profiles (개인):     {stats['profiles_with_user']}
  ----------------------------------------
    """)

    # 샘플 데이터 확인
    print("  샘플 프로필 데이터 (최근 5개):")
    result = db.session.execute(db.text("""
        SELECT id, name, email, user_id, created_at
        FROM profiles
        ORDER BY id DESC
        LIMIT 5
    """))
    for row in result:
        print(f"    - ID: {row.id}, 이름: {row.name}, 이메일: {row.email}, user_id: {row.user_id}")

    print("\n  샘플 직원-프로필 연결 (최근 5개):")
    result = db.session.execute(db.text("""
        SELECT e.id, e.name, e.profile_id, p.name as profile_name
        FROM employees e
        LEFT JOIN profiles p ON e.profile_id = p.id
        ORDER BY e.id DESC
        LIMIT 5
    """))
    for row in result:
        print(f"    - 직원 ID: {row.id}, 이름: {row.name}, profile_id: {row.profile_id}")

    return stats


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 60)
    print("  Phase 3-3: 데이터 마이그레이션 시작")
    print("=" * 60 + "\n")

    app = create_app()

    with app.app_context():
        try:
            # Step 1: personal_profiles -> profiles
            personal_count = migrate_personal_profiles_to_profiles()

            # Step 2: employees -> profiles 생성 및 연결
            employee_count = migrate_employees_to_profiles()

            # Step 3: 검증
            stats = verify_migration()

            print("\n" + "=" * 60)
            print("  마이그레이션 완료!")
            print("=" * 60)
            print(f"""
  요약:
  - personal_profiles에서 복사: {personal_count}개
  - employees에서 생성: {employee_count}개
  - 총 profiles: {stats['profiles_total']}개
  - 연결된 직원: {stats['employees_with_profile']}개
            """)

        except Exception as e:
            db.session.rollback()
            print(f"\n오류 발생: {e}")
            raise


if __name__ == '__main__':
    main()
