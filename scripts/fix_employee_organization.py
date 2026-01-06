"""
Employee organization_id 마이그레이션 스크립트

기존 Employee 레코드에 organization_id를 할당합니다.
사용자 결정: 모든 기존 직원을 테스트기업(주) (Company ID=1, root_organization_id=7)에 할당

실행 방법:
    python scripts/fix_employee_organization.py

기능:
    1. 현재 Employee organization_id 상태 확인
    2. 지정된 organization_id로 마이그레이션
    3. 마이그레이션 결과 검증
"""
import sys
import os

# 프로젝트 루트를 path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from app import create_app
from app.database import db
from app.domains.employee.models import Employee
from app.models.company import Company


def check_current_state():
    """현재 Employee organization_id 상태 확인"""
    print("\n[1/4] 현재 상태 확인")
    print("-" * 50)

    total = Employee.query.count()
    null_count = Employee.query.filter(Employee.organization_id.is_(None)).count()
    assigned_count = Employee.query.filter(Employee.organization_id.isnot(None)).count()

    print(f"  전체 Employee 수: {total}")
    print(f"  organization_id NULL: {null_count}")
    print(f"  organization_id 할당됨: {assigned_count}")

    if null_count == 0:
        print("  -> 모든 Employee에 organization_id가 이미 할당되어 있습니다.")
        return False

    return True


def verify_target_company():
    """대상 회사(테스트기업(주)) 확인"""
    print("\n[2/4] 대상 회사 확인")
    print("-" * 50)

    # Company ID=1 (테스트기업(주))
    company = Company.query.get(1)
    if not company:
        print("  [ERROR] Company ID=1 을 찾을 수 없습니다.")
        return None

    print(f"  회사명: {company.name}")
    print(f"  Company ID: {company.id}")
    print(f"  root_organization_id: {company.root_organization_id}")

    if not company.root_organization_id:
        print("  [ERROR] root_organization_id가 설정되지 않았습니다.")
        return None

    return company.root_organization_id


def migrate_employees(organization_id: int):
    """Employee 레코드에 organization_id 할당"""
    print("\n[3/4] 마이그레이션 실행")
    print("-" * 50)

    # NULL인 Employee 조회
    employees = Employee.query.filter(Employee.organization_id.is_(None)).all()

    if not employees:
        print("  마이그레이션할 Employee가 없습니다.")
        return 0

    migrated_count = 0
    for emp in employees:
        print(f"  - Employee ID {emp.id} ({emp.name}): organization_id = {organization_id}")
        emp.organization_id = organization_id
        migrated_count += 1

    db.session.commit()
    print(f"\n  총 {migrated_count}건 마이그레이션 완료")

    return migrated_count


def verify_migration():
    """마이그레이션 결과 검증"""
    print("\n[4/4] 마이그레이션 검증")
    print("-" * 50)

    total = Employee.query.count()
    null_count = Employee.query.filter(Employee.organization_id.is_(None)).count()
    assigned_count = Employee.query.filter(Employee.organization_id.isnot(None)).count()

    print(f"  전체 Employee 수: {total}")
    print(f"  organization_id NULL: {null_count}")
    print(f"  organization_id 할당됨: {assigned_count}")

    if null_count == 0:
        print("\n  [SUCCESS] 모든 Employee에 organization_id가 할당되었습니다.")
        return True
    else:
        print(f"\n  [WARNING] {null_count}건의 Employee에 organization_id가 없습니다.")
        return False


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Employee organization_id 마이그레이션")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # 1. 현재 상태 확인
        if not check_current_state():
            print("\n마이그레이션이 필요하지 않습니다.")
            return

        # 2. 대상 회사 확인
        organization_id = verify_target_company()
        if not organization_id:
            print("\n[ERROR] 마이그레이션을 진행할 수 없습니다.")
            return

        # 3. 사용자 확인
        print(f"\n모든 NULL organization_id Employee를 organization_id={organization_id}로 할당합니다.")
        confirm = input("계속하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            print("마이그레이션이 취소되었습니다.")
            return

        # 4. 마이그레이션 실행
        migrated = migrate_employees(organization_id)

        # 5. 결과 검증
        verify_migration()

        print("\n" + "=" * 60)
        print("마이그레이션 완료")
        print("=" * 60)


def run_auto():
    """자동 실행 (확인 없이)"""
    print("=" * 60)
    print("Employee organization_id 마이그레이션 (자동 모드)")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        if not check_current_state():
            print("\n마이그레이션이 필요하지 않습니다.")
            return True

        organization_id = verify_target_company()
        if not organization_id:
            print("\n[ERROR] 마이그레이션을 진행할 수 없습니다.")
            return False

        migrate_employees(organization_id)
        success = verify_migration()

        print("\n" + "=" * 60)
        print("마이그레이션 완료" if success else "마이그레이션 실패")
        print("=" * 60)

        return success


if __name__ == '__main__':
    # --auto 플래그로 확인 없이 실행
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        run_auto()
    else:
        main()
