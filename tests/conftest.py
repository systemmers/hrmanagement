"""
테스트 설정 및 공용 fixtures

pytest conftest.py - 모든 테스트에서 공유되는 fixtures 정의
"""
import pytest
from app import create_app
from app.database import db as _db
from app.models.user import User
from app.models.company import Company
from app.domains.employee.models import Employee
from app.models.person_contract import PersonCorporateContract


@pytest.fixture(scope='session')
def app():
    """Flask 애플리케이션 fixture (session scope)"""
    app = create_app('testing')

    # 애플리케이션 컨텍스트 푸시
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """데이터베이스 fixture (session scope)"""
    _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function')
def session(db, app):
    """데이터베이스 세션 fixture (function scope, 롤백)"""
    with app.app_context():
        # 새 세션 시작
        yield db.session

        # 테스트 후 롤백
        db.session.rollback()
        # 모든 테이블 데이터 삭제 (다음 테스트를 위해)
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def client(app):
    """Flask 테스트 클라이언트"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI 테스트 러너"""
    return app.test_cli_runner()


@pytest.fixture
def test_company(session):
    """테스트용 법인 fixture"""
    company = Company(
        name='테스트 법인',
        business_number='1234567890',
        representative='홍길동',
        business_type='서비스업',
        business_category='IT',
        address='서울시 강남구',
        phone='02-1234-5678'
    )
    session.add(company)
    session.commit()
    return company


@pytest.fixture
def test_user_personal(session):
    """테스트용 개인 계정 사용자 fixture"""
    user = User(
        username='testpersonal',
        email='personal@test.com',
        role=User.ROLE_EMPLOYEE,
        account_type=User.ACCOUNT_PERSONAL,
        is_active=True
    )
    user.set_password('test1234')
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def test_user_corporate(session, test_company):
    """테스트용 법인 계정 사용자 fixture"""
    user = User(
        username='testcorporate',
        email='corporate@test.com',
        role=User.ROLE_ADMIN,
        account_type=User.ACCOUNT_CORPORATE,
        company_id=test_company.id,
        is_active=True
    )
    user.set_password('admin1234')
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def test_employee(session, test_company):
    """테스트용 직원 fixture"""
    employee = Employee(
        employee_number='EMP001',
        name='테스트직원',
        department='개발팀',
        position='사원',
        status='active',
        company_id=test_company.id
    )
    session.add(employee)
    session.commit()
    return employee


@pytest.fixture
def auth_client_personal(client, test_user_personal):
    """개인 계정으로 인증된 테스트 클라이언트"""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user_personal.id
        sess['account_type'] = test_user_personal.account_type
    return client


@pytest.fixture
def auth_client_corporate(client, test_user_corporate):
    """법인 계정으로 인증된 테스트 클라이언트"""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user_corporate.id
        sess['account_type'] = test_user_corporate.account_type
    return client


@pytest.fixture
def test_contract_pending(session, test_user_personal, test_company):
    """테스트용 대기 중인 계약 fixture"""
    contract = PersonCorporateContract(
        person_user_id=test_user_personal.id,
        company_id=test_company.id,
        status='pending',
        contract_type='employment',
        position='사원',
        department='개발팀',
        requested_by='company'
    )
    session.add(contract)
    session.commit()
    return contract


@pytest.fixture
def test_contract_approved(session, test_user_personal, test_company):
    """테스트용 승인된 계약 fixture"""
    from datetime import datetime
    contract = PersonCorporateContract(
        person_user_id=test_user_personal.id,
        company_id=test_company.id,
        status='approved',
        contract_type='employment',
        position='사원',
        department='개발팀',
        requested_by='company',
        approved_at=datetime.utcnow(),
        employee_number='EMP_TEST001'
    )
    session.add(contract)
    session.commit()
    return contract


@pytest.fixture
def auth_client_personal_full(client, test_user_personal, test_company):
    """개인 계정으로 인증된 테스트 클라이언트 (세션 정보 풀셋)"""
    from app.shared.constants.session_keys import SessionKeys
    with client.session_transaction() as sess:
        sess[SessionKeys.USER_ID] = test_user_personal.id
        sess[SessionKeys.USERNAME] = test_user_personal.username
        sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
        sess[SessionKeys.USER_ROLE] = test_user_personal.role
    return client


@pytest.fixture
def auth_client_corporate_full(client, test_user_corporate, test_company):
    """법인 계정으로 인증된 테스트 클라이언트 (세션 정보 풀셋)"""
    from app.shared.constants.session_keys import SessionKeys
    with client.session_transaction() as sess:
        sess[SessionKeys.USER_ID] = test_user_corporate.id
        sess[SessionKeys.USERNAME] = test_user_corporate.username
        sess[SessionKeys.ACCOUNT_TYPE] = test_user_corporate.account_type
        sess[SessionKeys.COMPANY_ID] = test_company.id
        sess[SessionKeys.USER_ROLE] = test_user_corporate.role
    return client
