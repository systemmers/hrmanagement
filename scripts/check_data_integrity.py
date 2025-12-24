"""
데이터 무결성 체크 스크립트

실행: python scripts/check_data_integrity.py

체크 항목:
1. organization_id가 NULL인 직원
2. company_id와 organization 소속이 불일치하는 User
3. root_organization_id가 NULL인 Company
4. employee_id가 존재하지 않는 Employee를 참조하는 User
"""
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database import db
from app.models import Company, Organization, Employee, User


def get_all_descendants(org_id):
    """조직의 모든 하위 조직 ID 수집"""
    result = [org_id]
    children = Organization.query.filter_by(parent_id=org_id).all()
    for child in children:
        result.extend(get_all_descendants(child.id))
    return result


def check_employees_without_organization():
    """1. organization_id가 NULL인 직원 체크"""
    print("\n" + "=" * 60)
    print("[체크 1] organization_id가 NULL인 직원")
    print("=" * 60)

    employees = Employee.query.filter(Employee.organization_id.is_(None)).all()

    if not employees:
        print("  문제 없음")
        return 0

    print(f"  발견된 문제: {len(employees)}건")
    for emp in employees:
        user = User.query.filter_by(employee_id=emp.id).first()
        print(f"  - Employee {emp.id}: {emp.name or '이름없음'}")
        if user:
            print(f"    User: {user.username} (company_id: {user.company_id})")
        print(f"    해결: UPDATE employees SET organization_id = (SELECT root_organization_id FROM companies WHERE id = {user.company_id if user else 'N/A'}) WHERE id = {emp.id};")

    return len(employees)


def check_company_root_organization():
    """2. root_organization_id가 NULL인 Company 체크"""
    print("\n" + "=" * 60)
    print("[체크 2] root_organization_id가 NULL인 Company")
    print("=" * 60)

    companies = Company.query.filter(Company.root_organization_id.is_(None)).all()

    if not companies:
        print("  문제 없음")
        return 0

    print(f"  발견된 문제: {len(companies)}건")
    for company in companies:
        print(f"  - Company {company.id}: {company.name}")
        print(f"    해결: root_organization_id 수동 설정 필요")

    return len(companies)


def check_user_company_organization_mismatch():
    """3. User의 company_id와 Employee의 organization_id 소속 불일치 체크"""
    print("\n" + "=" * 60)
    print("[체크 3] User company_id와 Employee organization 소속 불일치")
    print("=" * 60)

    # 회사별 조직 ID 매핑 구축
    company_org_map = {}
    for company in Company.query.all():
        if company.root_organization_id:
            org_ids = set(get_all_descendants(company.root_organization_id))
            company_org_map[company.id] = org_ids

    issues = []
    employee_sub_users = User.query.filter(
        User.account_type == 'employee_sub',
        User.employee_id.isnot(None)
    ).all()

    for user in employee_sub_users:
        emp = db.session.get(Employee, user.employee_id)
        if not emp:
            continue

        if not emp.organization_id:
            continue  # 체크 1에서 처리

        # User의 company_id에 해당하는 조직 ID 집합
        expected_org_ids = company_org_map.get(user.company_id, set())

        if emp.organization_id not in expected_org_ids:
            # 실제 소속 회사 찾기
            actual_company_id = None
            for cid, org_ids in company_org_map.items():
                if emp.organization_id in org_ids:
                    actual_company_id = cid
                    break

            issues.append({
                'user': user,
                'employee': emp,
                'expected_company': user.company_id,
                'actual_company': actual_company_id
            })

    if not issues:
        print("  문제 없음")
        return 0

    print(f"  발견된 문제: {len(issues)}건")
    for issue in issues:
        print(f"  - User {issue['user'].id} ({issue['user'].username})")
        print(f"    Employee: {issue['employee'].id} ({issue['employee'].name})")
        print(f"    User.company_id: {issue['expected_company']}, Employee 실제 소속: {issue['actual_company']}")

    return len(issues)


def check_orphan_user_employee_references():
    """4. 존재하지 않는 Employee를 참조하는 User 체크"""
    print("\n" + "=" * 60)
    print("[체크 4] 존재하지 않는 Employee를 참조하는 User")
    print("=" * 60)

    users = User.query.filter(User.employee_id.isnot(None)).all()
    issues = []

    for user in users:
        emp = db.session.get(Employee, user.employee_id)
        if not emp:
            issues.append(user)

    if not issues:
        print("  문제 없음")
        return 0

    print(f"  발견된 문제: {len(issues)}건")
    for user in issues:
        print(f"  - User {user.id} ({user.username}): employee_id={user.employee_id} (존재하지 않음)")

    return len(issues)


def main():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("데이터 무결성 체크 시작")
        print("=" * 60)

        total_issues = 0
        total_issues += check_employees_without_organization()
        total_issues += check_company_root_organization()
        total_issues += check_user_company_organization_mismatch()
        total_issues += check_orphan_user_employee_references()

        print("\n" + "=" * 60)
        print(f"체크 완료: 총 {total_issues}건의 문제 발견")
        print("=" * 60)

        return total_issues


if __name__ == '__main__':
    exit_code = main()
    sys.exit(0 if exit_code == 0 else 1)
