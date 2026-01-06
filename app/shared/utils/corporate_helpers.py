"""
법인 회원가입 헬퍼 모듈

법인 회원가입 로직을 분할하여 단일 책임 원칙을 준수합니다.
Phase 6: 백엔드 리팩토링
Phase 31: 컨벤션 준수 - Repository 패턴 적용
"""
from dataclasses import dataclass
from typing import List, Optional

from app.database import db
from app.models.company import Company
from app.models.organization import Organization
from app.repositories.company_repository import company_repository
from app.shared.utils.transaction import atomic_transaction


# 지연 초기화용
_user_repo = None


def _get_user_repo():
    """지연 초기화된 User Repository"""
    global _user_repo
    if _user_repo is None:
        from app.repositories.user_repository import user_repository
        _user_repo = user_repository
    return _user_repo


@dataclass
class RegistrationData:
    """법인 회원가입 데이터"""
    # 법인 정보
    company_name: str
    business_number: str
    representative: str
    business_type: str
    business_category: str
    phone: str
    email: str
    address: str
    address_detail: str
    postal_code: str

    # 관리자 정보
    admin_username: str
    admin_email: str
    admin_password: str
    admin_password_confirm: str

    def to_template_context(self) -> dict:
        """템플릿 렌더링용 컨텍스트 반환"""
        return {
            'company_name': self.company_name,
            'business_number': self.business_number,
            'representative': self.representative,
            'business_type': self.business_type,
            'business_category': self.business_category,
            'phone': self.phone,
            'company_email': self.email,
            'address': self.address,
            'address_detail': self.address_detail,
            'postal_code': self.postal_code,
            'admin_username': self.admin_username,
            'admin_email': self.admin_email
        }


def extract_registration_data(form) -> RegistrationData:
    """
    폼에서 회원가입 데이터 추출

    Args:
        form: Flask request.form

    Returns:
        RegistrationData: 추출된 데이터
    """
    return RegistrationData(
        company_name=form.get('company_name', '').strip(),
        business_number=form.get('business_number', '').strip(),
        representative=form.get('representative', '').strip(),
        business_type=form.get('business_type', '').strip(),
        business_category=form.get('business_category', '').strip(),
        phone=form.get('phone', '').strip(),
        email=form.get('company_email', '').strip(),
        address=form.get('address', '').strip(),
        address_detail=form.get('address_detail', '').strip(),
        postal_code=form.get('postal_code', '').strip(),
        admin_username=form.get('admin_username', '').strip(),
        admin_email=form.get('admin_email', '').strip(),
        admin_password=form.get('admin_password', ''),
        admin_password_confirm=form.get('admin_password_confirm', '')
    )


def validate_registration(data: RegistrationData) -> List[str]:
    """
    회원가입 데이터 유효성 검증

    Args:
        data: 회원가입 데이터

    Returns:
        List[str]: 에러 메시지 목록 (비어있으면 유효함)
    """
    errors = []

    # 필수 입력 검증
    if not data.company_name:
        errors.append('법인명을 입력해주세요.')
    if not data.business_number:
        errors.append('사업자등록번호를 입력해주세요.')
    if not data.representative:
        errors.append('대표자명을 입력해주세요.')
    if not data.admin_username:
        errors.append('관리자 아이디를 입력해주세요.')
    if not data.admin_email:
        errors.append('관리자 이메일을 입력해주세요.')
    if not data.admin_password:
        errors.append('비밀번호를 입력해주세요.')
    if data.admin_password != data.admin_password_confirm:
        errors.append('비밀번호가 일치하지 않습니다.')
    if len(data.admin_password) < 8:
        errors.append('비밀번호는 최소 8자 이상이어야 합니다.')

    # 사업자등록번호 중복 확인
    if data.business_number and company_repository.exists_by_business_number(data.business_number):
        errors.append('이미 등록된 사업자등록번호입니다.')

    # Phase 31: Repository 패턴 적용
    user_repo = _get_user_repo()
    if data.admin_username and user_repo.find_by_username(data.admin_username):
        errors.append('이미 사용 중인 아이디입니다.')
    if data.admin_email and user_repo.find_by_email(data.admin_email):
        errors.append('이미 사용 중인 이메일입니다.')

    return errors


def create_company_entities(data: RegistrationData) -> Optional[str]:
    """
    법인 관련 엔티티 생성 (조직, 회사, 관리자)

    Args:
        data: 회원가입 데이터

    Returns:
        Optional[str]: 에러 메시지 (성공 시 None)
    """
    try:
        with atomic_transaction():
            # 루트 조직 생성
            root_org = Organization(
                name=data.company_name,
                org_type=Organization.TYPE_COMPANY,
                is_active=True,
                description=f'{data.company_name} 루트 조직'
            )
            db.session.add(root_org)
            db.session.flush()

            # 법인 생성
            company = Company(
                name=data.company_name,
                business_number=data.business_number.replace('-', ''),
                representative=data.representative,
                business_type=data.business_type,
                business_category=data.business_category,
                phone=data.phone,
                email=data.email,
                address=data.address,
                address_detail=data.address_detail,
                postal_code=data.postal_code,
                root_organization_id=root_org.id,
                is_active=True,
                plan_type=Company.PLAN_FREE,
                max_employees=Company.PLAN_MAX_EMPLOYEES[Company.PLAN_FREE]
            )
            db.session.add(company)
            db.session.flush()

            # 관리자 계정 생성
            admin_user = User(
                username=data.admin_username,
                email=data.admin_email,
                role=User.ROLE_ADMIN,
                account_type=User.ACCOUNT_CORPORATE,
                company_id=company.id,
                is_active=True
            )
            admin_user.set_password(data.admin_password)
            db.session.add(admin_user)

        return None

    except Exception as e:
        return f'회원가입 중 오류가 발생했습니다: {str(e)}'
