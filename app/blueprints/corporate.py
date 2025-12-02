"""
법인 계정 Blueprint

법인 회원가입, 법인 정보 관리, 법인 대시보드를 처리합니다.
Phase 1: Company 모델 구현의 일부입니다.
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

from app.database import db
from app.models.company import Company
from app.models.user import User
from app.models.organization import Organization
from app.repositories.company_repository import company_repository

corporate_bp = Blueprint('corporate', __name__, url_prefix='/corporate')


def corporate_login_required(f):
    """법인 계정 로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('account_type') != User.ACCOUNT_CORPORATE:
            flash('법인 계정으로 로그인해주세요.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def corporate_admin_required(f):
    """법인 관리자 권한 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('account_type') != User.ACCOUNT_CORPORATE:
            flash('법인 계정으로 로그인해주세요.', 'error')
            return redirect(url_for('main.index'))
        if session.get('user_role') not in [User.ROLE_ADMIN, User.ROLE_MANAGER]:
            flash('관리자 권한이 필요합니다.', 'error')
            return redirect(url_for('corporate.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@corporate_bp.route('/register', methods=['GET', 'POST'])
def register():
    """법인 회원가입"""
    # 이미 로그인된 경우
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 법인 정보
        company_name = request.form.get('company_name', '').strip()
        business_number = request.form.get('business_number', '').strip()
        representative = request.form.get('representative', '').strip()
        business_type = request.form.get('business_type', '').strip()
        business_category = request.form.get('business_category', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('company_email', '').strip()
        address = request.form.get('address', '').strip()
        address_detail = request.form.get('address_detail', '').strip()
        postal_code = request.form.get('postal_code', '').strip()

        # 관리자 계정 정보
        admin_username = request.form.get('admin_username', '').strip()
        admin_email = request.form.get('admin_email', '').strip()
        admin_password = request.form.get('admin_password', '')
        admin_password_confirm = request.form.get('admin_password_confirm', '')

        # 필수 입력 검증
        errors = []
        if not company_name:
            errors.append('법인명을 입력해주세요.')
        if not business_number:
            errors.append('사업자등록번호를 입력해주세요.')
        if not representative:
            errors.append('대표자명을 입력해주세요.')
        if not admin_username:
            errors.append('관리자 아이디를 입력해주세요.')
        if not admin_email:
            errors.append('관리자 이메일을 입력해주세요.')
        if not admin_password:
            errors.append('비밀번호를 입력해주세요.')
        if admin_password != admin_password_confirm:
            errors.append('비밀번호가 일치하지 않습니다.')
        if len(admin_password) < 8:
            errors.append('비밀번호는 최소 8자 이상이어야 합니다.')

        # 사업자등록번호 중복 확인
        if company_repository.exists_by_business_number(business_number):
            errors.append('이미 등록된 사업자등록번호입니다.')

        # 아이디/이메일 중복 확인
        if User.query.filter_by(username=admin_username).first():
            errors.append('이미 사용 중인 아이디입니다.')
        if User.query.filter_by(email=admin_email).first():
            errors.append('이미 사용 중인 이메일입니다.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('corporate/register.html',
                                   company_name=company_name,
                                   business_number=business_number,
                                   representative=representative,
                                   business_type=business_type,
                                   business_category=business_category,
                                   phone=phone,
                                   company_email=email,
                                   address=address,
                                   address_detail=address_detail,
                                   postal_code=postal_code,
                                   admin_username=admin_username,
                                   admin_email=admin_email)

        try:
            # 루트 조직 생성
            root_org = Organization(
                name=company_name,
                org_type=Organization.TYPE_COMPANY,
                is_active=True,
                description=f'{company_name} 루트 조직'
            )
            db.session.add(root_org)
            db.session.flush()

            # 법인 생성
            company = Company(
                name=company_name,
                business_number=business_number.replace('-', ''),
                representative=representative,
                business_type=business_type,
                business_category=business_category,
                phone=phone,
                email=email,
                address=address,
                address_detail=address_detail,
                postal_code=postal_code,
                root_organization_id=root_org.id,
                is_active=True,
                plan_type=Company.PLAN_FREE,
                max_employees=Company.PLAN_MAX_EMPLOYEES[Company.PLAN_FREE]
            )
            db.session.add(company)
            db.session.flush()

            # 관리자 계정 생성
            admin_user = User(
                username=admin_username,
                email=admin_email,
                role=User.ROLE_ADMIN,
                account_type=User.ACCOUNT_CORPORATE,
                company_id=company.id,
                is_active=True
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)

            db.session.commit()

            flash('법인 회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'회원가입 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('corporate/register.html',
                                   company_name=company_name,
                                   business_number=business_number,
                                   representative=representative,
                                   business_type=business_type,
                                   business_category=business_category,
                                   phone=phone,
                                   company_email=email,
                                   address=address,
                                   address_detail=address_detail,
                                   postal_code=postal_code,
                                   admin_username=admin_username,
                                   admin_email=admin_email)

    return render_template('corporate/register.html')


@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    """법인 대시보드"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_repository.get_with_stats(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    return render_template('corporate/dashboard.html', company=company)


@corporate_bp.route('/settings', methods=['GET', 'POST'])
@corporate_admin_required
def settings():
    """법인 정보 설정"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = Company.query.get(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 법인 정보 수정
        company.name = request.form.get('company_name', company.name).strip()
        company.representative = request.form.get('representative', company.representative).strip()
        company.business_type = request.form.get('business_type', '').strip() or None
        company.business_category = request.form.get('business_category', '').strip() or None
        company.phone = request.form.get('phone', '').strip() or None
        company.email = request.form.get('company_email', '').strip() or None
        company.website = request.form.get('website', '').strip() or None
        company.address = request.form.get('address', '').strip() or None
        company.address_detail = request.form.get('address_detail', '').strip() or None
        company.postal_code = request.form.get('postal_code', '').strip() or None

        try:
            db.session.commit()
            flash('법인 정보가 수정되었습니다.', 'success')
            return redirect(url_for('corporate.settings'))
        except Exception as e:
            db.session.rollback()
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')

    return render_template('corporate/settings.html', company=company)


@corporate_bp.route('/users')
@corporate_admin_required
def users():
    """법인 사용자 관리"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = Company.query.get(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 법인에 속한 사용자 목록
    users = User.query.filter_by(company_id=company_id).all()

    return render_template('corporate/users.html', company=company, users=users)


@corporate_bp.route('/users/add', methods=['GET', 'POST'])
@corporate_admin_required
def add_user():
    """법인 하위 사용자 추가"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = Company.query.get(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 직원 추가 가능 여부 확인
    if not company.can_add_employee():
        flash(f'현재 플랜에서는 최대 {company.max_employees}명까지 등록 가능합니다.', 'error')
        return redirect(url_for('corporate.users'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', User.ROLE_EMPLOYEE)

        # 입력 검증
        errors = []
        if not username:
            errors.append('아이디를 입력해주세요.')
        if not email:
            errors.append('이메일을 입력해주세요.')
        if not password:
            errors.append('비밀번호를 입력해주세요.')
        if len(password) < 8:
            errors.append('비밀번호는 최소 8자 이상이어야 합니다.')
        if User.query.filter_by(username=username).first():
            errors.append('이미 사용 중인 아이디입니다.')
        if User.query.filter_by(email=email).first():
            errors.append('이미 사용 중인 이메일입니다.')
        if role not in User.VALID_ROLES:
            errors.append('유효하지 않은 역할입니다.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('corporate/add_user.html',
                                   company=company,
                                   username=username,
                                   email=email,
                                   role=role)

        try:
            new_user = User(
                username=username,
                email=email,
                role=role,
                account_type=User.ACCOUNT_EMPLOYEE_SUB,
                company_id=company_id,
                parent_user_id=session.get('user_id'),
                is_active=True
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash(f'사용자 {username}이(가) 추가되었습니다.', 'success')
            return redirect(url_for('corporate.users'))

        except Exception as e:
            db.session.rollback()
            flash(f'사용자 추가 중 오류가 발생했습니다: {str(e)}', 'error')

    return render_template('corporate/add_user.html', company=company)


# API 엔드포인트

@corporate_bp.route('/api/check-business-number')
def check_business_number():
    """사업자등록번호 중복 확인 API"""
    business_number = request.args.get('business_number', '')
    if not business_number:
        return jsonify({'error': '사업자등록번호를 입력해주세요.'}), 400

    exists = company_repository.exists_by_business_number(business_number)
    return jsonify({'exists': exists, 'available': not exists})


@corporate_bp.route('/api/company/<int:company_id>')
@corporate_login_required
def get_company(company_id):
    """법인 정보 조회 API"""
    # 자신의 법인 정보만 조회 가능
    if session.get('company_id') != company_id:
        return jsonify({'error': '접근 권한이 없습니다.'}), 403

    company = company_repository.get_with_stats(company_id)
    if not company:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 404

    return jsonify(company)
