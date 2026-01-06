"""
멀티테넌시 테스트 계정 생성 스크립트

생성 대상:
- 개인계정 3개
- 법인계정 2개
- 법인1 소속 직원계정 5개
- 법인2 소속 직원계정 3개
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database import db
from app.models.user import User
from app.models.company import Company
from app.domains.employee.models import Employee


def create_test_accounts():
    """테스트 계정 생성"""
    app = create_app()

    with app.app_context():
        results = {
            'personal': [],
            'corporate': [],
            'employee_sub': []
        }

        # 1. 개인계정 3개 생성
        print("\n[1] 개인계정 생성...")
        personal_accounts = [
            {'username': 'personal_user1', 'email': 'personal1@test.com', 'password': 'personal1234'},
            {'username': 'personal_user2', 'email': 'personal2@test.com', 'password': 'personal1234'},
            {'username': 'personal_user3', 'email': 'personal3@test.com', 'password': 'personal1234'},
        ]

        for acc in personal_accounts:
            existing = User.query.filter_by(email=acc['email']).first()
            if existing:
                print(f"  - {acc['username']}: 이미 존재 (건너뜀)")
                results['personal'].append({**acc, 'status': 'exists', 'id': existing.id})
                continue

            user = User(
                username=acc['username'],
                email=acc['email'],
                account_type=User.ACCOUNT_PERSONAL,
                role=User.ROLE_EMPLOYEE,
                is_active=True
            )
            user.set_password(acc['password'])
            db.session.add(user)
            db.session.flush()

            print(f"  + {acc['username']}: 생성 완료 (ID: {user.id})")
            results['personal'].append({**acc, 'status': 'created', 'id': user.id})

        # 2. 법인계정 2개 생성 (Company + User)
        print("\n[2] 법인계정 생성...")
        corporate_accounts = [
            {
                'company': {
                    'name': '테스트기업 A',
                    'business_number': '1234567890',
                    'representative': '홍길동'
                },
                'user': {
                    'username': 'corp_admin_a',
                    'email': 'corp_a@test.com',
                    'password': 'corp1234'
                }
            },
            {
                'company': {
                    'name': '테스트기업 B',
                    'business_number': '0987654321',
                    'representative': '김철수'
                },
                'user': {
                    'username': 'corp_admin_b',
                    'email': 'corp_b@test.com',
                    'password': 'corp1234'
                }
            }
        ]

        companies = []
        for corp in corporate_accounts:
            # Company 생성/확인
            existing_company = Company.query.filter_by(
                business_number=corp['company']['business_number']
            ).first()

            if existing_company:
                company = existing_company
                print(f"  - {corp['company']['name']}: Company 이미 존재 (ID: {company.id})")
            else:
                company = Company(
                    name=corp['company']['name'],
                    business_number=corp['company']['business_number'],
                    representative=corp['company']['representative'],
                    is_active=True
                )
                db.session.add(company)
                db.session.flush()
                print(f"  + {corp['company']['name']}: Company 생성 (ID: {company.id})")

            companies.append(company)

            # Corporate User 생성/확인
            existing_user = User.query.filter_by(email=corp['user']['email']).first()
            if existing_user:
                print(f"  - {corp['user']['username']}: User 이미 존재 (건너뜀)")
                results['corporate'].append({
                    **corp['user'],
                    'company_name': company.name,
                    'company_id': company.id,
                    'status': 'exists',
                    'id': existing_user.id
                })
                continue

            user = User(
                username=corp['user']['username'],
                email=corp['user']['email'],
                account_type=User.ACCOUNT_CORPORATE,
                role=User.ROLE_ADMIN,
                company_id=company.id,
                is_active=True
            )
            user.set_password(corp['user']['password'])
            db.session.add(user)
            db.session.flush()

            print(f"  + {corp['user']['username']}: User 생성 (ID: {user.id})")
            results['corporate'].append({
                **corp['user'],
                'company_name': company.name,
                'company_id': company.id,
                'status': 'created',
                'id': user.id
            })

        # 3. 법인1 소속 직원계정 5개
        print("\n[3] 법인1 소속 직원계정 생성...")
        company_a = companies[0]
        corp_admin_a = User.query.filter_by(email='corp_a@test.com').first()

        for i in range(1, 6):
            email = f'emp_a{i}@test.com'
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"  - emp_a{i}: 이미 존재 (건너뜀)")
                results['employee_sub'].append({
                    'username': f'emp_a{i}',
                    'email': email,
                    'password': 'emp1234',
                    'company_name': company_a.name,
                    'status': 'exists',
                    'id': existing.id
                })
                continue

            user = User(
                username=f'emp_a{i}',
                email=email,
                account_type=User.ACCOUNT_EMPLOYEE_SUB,
                role=User.ROLE_EMPLOYEE,
                company_id=company_a.id,
                parent_user_id=corp_admin_a.id if corp_admin_a else None,
                is_active=True
            )
            user.set_password('emp1234')
            db.session.add(user)
            db.session.flush()

            print(f"  + emp_a{i}: 생성 완료 (ID: {user.id})")
            results['employee_sub'].append({
                'username': f'emp_a{i}',
                'email': email,
                'password': 'emp1234',
                'company_name': company_a.name,
                'status': 'created',
                'id': user.id
            })

        # 4. 법인2 소속 직원계정 3개
        print("\n[4] 법인2 소속 직원계정 생성...")
        company_b = companies[1]
        corp_admin_b = User.query.filter_by(email='corp_b@test.com').first()

        for i in range(1, 4):
            email = f'emp_b{i}@test.com'
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"  - emp_b{i}: 이미 존재 (건너뜀)")
                results['employee_sub'].append({
                    'username': f'emp_b{i}',
                    'email': email,
                    'password': 'emp1234',
                    'company_name': company_b.name,
                    'status': 'exists',
                    'id': existing.id
                })
                continue

            user = User(
                username=f'emp_b{i}',
                email=email,
                account_type=User.ACCOUNT_EMPLOYEE_SUB,
                role=User.ROLE_EMPLOYEE,
                company_id=company_b.id,
                parent_user_id=corp_admin_b.id if corp_admin_b else None,
                is_active=True
            )
            user.set_password('emp1234')
            db.session.add(user)
            db.session.flush()

            print(f"  + emp_b{i}: 생성 완료 (ID: {user.id})")
            results['employee_sub'].append({
                'username': f'emp_b{i}',
                'email': email,
                'password': 'emp1234',
                'company_name': company_b.name,
                'status': 'created',
                'id': user.id
            })

        db.session.commit()
        print("\n[OK] 모든 계정 생성 완료!")

        return results


def verify_accounts():
    """생성된 계정 검증"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("계정 검증 결과")
        print("="*60)

        # 개인계정
        personal = User.query.filter_by(account_type=User.ACCOUNT_PERSONAL).all()
        print(f"\n[개인계정] 총 {len(personal)}개")
        for u in personal:
            print(f"  - {u.username} ({u.email}) | ID: {u.id}")

        # 법인계정
        corporate = User.query.filter_by(account_type=User.ACCOUNT_CORPORATE).all()
        print(f"\n[법인계정] 총 {len(corporate)}개")
        for u in corporate:
            company = u.company
            company_name = company.name if company else "미연결"
            print(f"  - {u.username} ({u.email}) | Company: {company_name} | ID: {u.id}")

        # 법인소속 직원계정
        employee_sub = User.query.filter_by(account_type=User.ACCOUNT_EMPLOYEE_SUB).all()
        print(f"\n[법인소속 직원계정] 총 {len(employee_sub)}개")
        for u in employee_sub:
            company = u.get_company()
            company_name = company.name if company else "미연결"
            parent = u.parent_user.username if u.parent_user else "없음"
            print(f"  - {u.username} ({u.email}) | Company: {company_name} | Parent: {parent}")

        # Company 목록
        companies = Company.query.all()
        print(f"\n[법인(Company)] 총 {len(companies)}개")
        for c in companies:
            user_count = User.query.filter_by(company_id=c.id).count()
            print(f"  - {c.name} (사업자번호: {c.business_number}) | 연결된 사용자: {user_count}명")

        print("\n" + "="*60)

        return {
            'personal_count': len(personal),
            'corporate_count': len(corporate),
            'employee_sub_count': len(employee_sub),
            'company_count': len(companies)
        }


if __name__ == '__main__':
    print("="*60)
    print("멀티테넌시 테스트 계정 생성")
    print("="*60)

    results = create_test_accounts()
    stats = verify_accounts()

    print("\n[요약]")
    print(f"  - 개인계정: {stats['personal_count']}개")
    print(f"  - 법인계정: {stats['corporate_count']}개")
    print(f"  - 법인소속 직원계정: {stats['employee_sub_count']}개")
    print(f"  - 법인(Company): {stats['company_count']}개")
