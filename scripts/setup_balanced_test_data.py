"""
테스트 데이터 균형화 통합 스크립트

기능:
1. 법인별 Employee 데이터 균형화 (balance_test_data.py)
2. employee_sub 계정 - Employee 연결 (link_employee_user.py)
3. 실행 전/후 상태 리포트

실행 방법:
    python scripts/setup_balanced_test_data.py
    python scripts/setup_balanced_test_data.py --dry-run    # 미리보기
    python scripts/setup_balanced_test_data.py --status     # 상태만 출력
    python scripts/setup_balanced_test_data.py --link-only  # 연결만 실행
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database import db
from app.domains.user.models import User
from app.domains.employee.models import Employee
from app.domains.company.models import Company


def show_comprehensive_status():
    """전체 상태 리포트 출력"""
    print("\n" + "=" * 70)
    print("데이터베이스 현황 리포트")
    print("=" * 70)

    # 1. Company별 Employee 현황
    print("\n[1] Company별 Employee 현황")
    print("-" * 50)

    companies = Company.query.all()
    total_employees = 0
    for company in companies:
        if company.root_organization_id:
            emp_count = Employee.query.filter_by(
                organization_id=company.root_organization_id
            ).count()
        else:
            emp_count = 0
        total_employees += emp_count
        print(f"  {company.name}")
        print(f"    - Company ID: {company.id}")
        print(f"    - root_organization_id: {company.root_organization_id}")
        print(f"    - Employee 수: {emp_count}명")

    print(f"\n  총 Employee: {total_employees}명")

    # 2. User 계정 현황
    print("\n[2] User 계정 현황")
    print("-" * 50)

    personal = User.query.filter_by(account_type=User.ACCOUNT_PERSONAL).count()
    corporate = User.query.filter_by(account_type=User.ACCOUNT_CORPORATE).count()
    employee_sub = User.query.filter_by(account_type=User.ACCOUNT_EMPLOYEE_SUB).count()

    print(f"  - Personal 계정: {personal}개")
    print(f"  - Corporate 계정: {corporate}개")
    print(f"  - Employee Sub 계정: {employee_sub}개")
    print(f"  - 총 User: {personal + corporate + employee_sub}명")

    # 3. Employee-User 연결 현황
    print("\n[3] Employee-User 연결 현황")
    print("-" * 50)

    all_sub = User.query.filter_by(account_type=User.ACCOUNT_EMPLOYEE_SUB).all()
    linked = [u for u in all_sub if u.employee_id is not None]
    unlinked = [u for u in all_sub if u.employee_id is None]

    print(f"  - Employee 연결됨: {len(linked)}개")
    print(f"  - Employee 미연결: {len(unlinked)}개")

    if unlinked:
        print("\n  [미연결 계정 상세]")
        for u in unlinked:
            company = u.get_company()
            company_name = company.name if company else "Company 미연결"
            print(f"    - {u.username} (Company: {company_name})")

    # 4. 문제 진단
    print("\n[4] 문제 진단")
    print("-" * 50)

    issues = []

    # 데이터 불균형 체크
    for company in companies:
        if company.root_organization_id:
            emp_count = Employee.query.filter_by(
                organization_id=company.root_organization_id
            ).count()
            if emp_count == 0:
                issues.append(f"  - {company.name}: Employee 0명 (데이터 불균형)")

    # 미연결 계정 체크
    if unlinked:
        issues.append(f"  - employee_sub 미연결: {len(unlinked)}개 (로그인 시 로그아웃)")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("  (문제 없음)")

    print("\n" + "=" * 70)


def run_balance_test_data(dry_run=False):
    """법인별 Employee 데이터 균형화 실행"""
    print("\n" + "=" * 70)
    print("Phase 1: 법인별 Employee 데이터 균형화")
    print("=" * 70)

    # balance_test_data.py의 로직 임포트 및 실행
    from scripts.balance_test_data import (
        create_employees_for_company,
        get_next_employee_number,
        show_current_status
    )

    company_2 = Company.query.get(2)  # (주)테스트기업
    company_3 = Company.query.get(3)  # 테스트기업 B

    if not company_2 or not company_3:
        print("[ERROR] Company 2 또는 3이 존재하지 않습니다.")
        return False

    # 이미 Employee가 있는지 확인
    if company_2.root_organization_id:
        existing_2 = Employee.query.filter_by(
            organization_id=company_2.root_organization_id
        ).count()
    else:
        existing_2 = 0

    if company_3.root_organization_id:
        existing_3 = Employee.query.filter_by(
            organization_id=company_3.root_organization_id
        ).count()
    else:
        existing_3 = 0

    if existing_2 >= 5 and existing_3 >= 5:
        print(f"\n[SKIP] 이미 충분한 Employee가 있습니다.")
        print(f"  - {company_2.name}: {existing_2}명")
        print(f"  - {company_3.name}: {existing_3}명")
        return True

    start_number = get_next_employee_number()
    created_count = 0

    # (주)테스트기업: 5명 생성 (없는 경우만)
    if existing_2 < 5:
        to_create = 5 - existing_2
        emp_list = create_employees_for_company(
            company_2, count=to_create, male_count=to_create // 2,
            start_number=start_number, dry_run=dry_run
        )
        created_count += len(emp_list)
        start_number += len(emp_list)

    # 테스트기업 B: 5명 생성 (없는 경우만)
    if existing_3 < 5:
        to_create = 5 - existing_3
        emp_list = create_employees_for_company(
            company_3, count=to_create, male_count=(to_create + 1) // 2,
            start_number=start_number, dry_run=dry_run
        )
        created_count += len(emp_list)

    if not dry_run and created_count > 0:
        db.session.commit()

    print(f"\n[OK] Phase 1 완료: {created_count}명 생성")
    return True


def run_link_employee_user(dry_run=False):
    """employee_sub 계정 - Employee 연결 실행"""
    print("\n" + "=" * 70)
    print("Phase 2: employee_sub 계정 - Employee 연결")
    print("=" * 70)

    from scripts.link_employee_user import (
        get_unlinked_employee_sub_accounts,
        create_employee_for_user,
        get_next_employee_number
    )

    unlinked_users = get_unlinked_employee_sub_accounts()

    if not unlinked_users:
        print("\n[SKIP] 모든 employee_sub 계정이 이미 연결되어 있습니다.")
        return True

    print(f"\n{len(unlinked_users)}개 계정 연결 작업 시작...")

    start_number = get_next_employee_number()
    emp_number = start_number
    linked_count = 0

    for user in unlinked_users:
        company = user.get_company()
        if not company or not company.root_organization_id:
            print(f"  [SKIP] {user.username}: Company/Organization 없음")
            continue

        org_id = company.root_organization_id
        employee = create_employee_for_user(user, org_id, emp_number, dry_run)

        if not dry_run:
            user.employee_id = employee.id

        print(f"  + {user.username} -> {employee.name} (ID: {employee.id if not dry_run else 'NEW'})")

        emp_number += 1
        linked_count += 1

    if not dry_run and linked_count > 0:
        db.session.commit()

    print(f"\n[OK] Phase 2 완료: {linked_count}개 계정 연결")
    return True


def main():
    """메인 실행 함수"""
    dry_run = '--dry-run' in sys.argv
    status_only = '--status' in sys.argv
    link_only = '--link-only' in sys.argv

    print("=" * 70)
    print("테스트 데이터 균형화 통합 스크립트")
    print("=" * 70)

    if dry_run:
        print("[DRY RUN 모드 - 실제 데이터 변경 없음]")

    app = create_app()

    with app.app_context():
        # 상태만 출력
        if status_only:
            show_comprehensive_status()
            return

        # 실행 전 상태
        print("\n[실행 전 상태]")
        show_comprehensive_status()

        # Phase 1: 데이터 균형화 (--link-only가 아닌 경우)
        if not link_only:
            run_balance_test_data(dry_run)

        # Phase 2: Employee-User 연결
        run_link_employee_user(dry_run)

        # 실행 후 상태
        if not dry_run:
            print("\n[실행 후 상태]")
            show_comprehensive_status()

        print("\n[완료]")
        if dry_run:
            print("DRY RUN 모드였습니다. 실제 실행하려면 --dry-run 없이 실행하세요.")
        else:
            print("모든 작업이 완료되었습니다.")


if __name__ == '__main__':
    main()
