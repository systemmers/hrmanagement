"""
Employee Account Service

직원 등록 시 계정 연동을 처리합니다.
- 직원 + 계정 동시 생성 (21번 원칙: 계약은 별도 프로세스)
- 계정수 = 직원수 정합성 유지
- 계정 유효성 검증

Phase 1 (Part A): 직원 등록 + 계정 생성
Phase 2 (Part B): 계약 프로세스 확장 (별도 구현)
"""
import secrets
import string
from typing import Dict, Optional, Tuple, List

from app.database import db
from app.models import Employee, User
from app.extensions import employee_repo, user_repo
from app.utils.tenant import get_current_organization_id


class EmployeeAccountService:
    """직원-계정 연동 서비스"""

    # 비밀번호 생성 설정
    PASSWORD_LENGTH = 12
    PASSWORD_CHARS = string.ascii_letters + string.digits + "!@#$%"

    def __init__(self):
        self.employee_repo = employee_repo
        self.user_repo = user_repo

    # ========================================
    # 직원 + 계정 생성 (Part A)
    # ========================================

    def create_employee_with_account(
        self,
        employee_data: Dict,
        account_data: Dict,
        company_id: int,
        admin_user_id: int
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """직원 + 계정 동시 생성

        21번 원칙: 계약은 별도 프로세스로 처리 (Part B)

        Args:
            employee_data: 직원 정보 (name, department, position 등)
            account_data: 계정 정보 (username, email, password, role)
            company_id: 법인 ID
            admin_user_id: 생성 요청한 관리자 ID

        Returns:
            Tuple[성공여부, 결과정보, 에러메시지]
        """
        try:
            # 1. 계정 정보 검증
            validation_error = self._validate_account_data(
                account_data.get('username'),
                account_data.get('email')
            )
            if validation_error:
                return False, None, validation_error

            # 2. Employee 생성
            employee = self._create_employee(employee_data, company_id)
            db.session.flush()  # employee.id 확보

            # 3. User 생성 (account_type='employee_sub')
            user = self._create_user(
                account_data=account_data,
                employee_id=employee.id,
                company_id=company_id,
                parent_user_id=admin_user_id
            )
            db.session.flush()

            db.session.commit()

            return True, {
                'employee_id': employee.id,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'message': '직원 및 계정이 생성되었습니다. 계약은 별도로 요청해주세요.'
            }, None

        except Exception as e:
            db.session.rollback()
            return False, None, f"생성 실패: {str(e)}"

    def create_account_only(
        self,
        account_data: Dict,
        minimal_employee_data: Dict,
        company_id: int,
        admin_user_id: int
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """간편 등록: 계정 + 최소 직원 정보만 생성

        직원이 로그인 후 나머지 정보를 입력하는 방식

        Args:
            account_data: 계정 정보 (username, email, password, role)
            minimal_employee_data: 최소 직원 정보 (name만 필수)
            company_id: 법인 ID
            admin_user_id: 생성 요청한 관리자 ID

        Returns:
            Tuple[성공여부, 결과정보, 에러메시지]
        """
        try:
            # 1. 계정 정보 검증
            validation_error = self._validate_account_data(
                account_data.get('username'),
                account_data.get('email')
            )
            if validation_error:
                return False, None, validation_error

            # 2. Company의 root_organization_id 조회
            from app.models.company import Company
            company = Company.query.get(company_id)
            if not company:
                return False, None, "법인 정보를 찾을 수 없습니다."

            # 3. 최소 Employee 생성 (company_id + organization_id 포함)
            employee = Employee(
                name=minimal_employee_data.get('name', ''),
                email=account_data.get('email', ''),
                company_id=company_id,  # 법인 소속 설정
                organization_id=company.root_organization_id,  # 조직 트리 연결
                status='pending_info'  # 정보 입력 대기 상태
            )
            db.session.add(employee)
            db.session.flush()

            # 3. User 생성
            user = self._create_user(
                account_data=account_data,
                employee_id=employee.id,
                company_id=company_id,
                parent_user_id=admin_user_id
            )
            db.session.flush()

            db.session.commit()

            return True, {
                'employee_id': employee.id,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'status': 'pending_info',
                'message': '계정이 생성되었습니다. 직원이 로그인하여 정보를 입력해야 합니다.'
            }, None

        except Exception as e:
            db.session.rollback()
            return False, None, f"생성 실패: {str(e)}"

    # ========================================
    # 계정 관리
    # ========================================

    def deactivate_employee_account(
        self,
        employee_id: int,
        reason: str,
        deactivated_by: int
    ) -> Tuple[bool, Optional[str]]:
        """직원 계정 비활성화

        Args:
            employee_id: 직원 ID
            reason: 비활성화 사유
            deactivated_by: 비활성화 요청자 ID

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            # Employee 조회
            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            # User 조회 (employee_id로)
            user = User.query.filter_by(employee_id=employee_id).first()
            if user:
                user.is_active = False

            # Employee 상태 변경
            employee.status = 'inactive'

            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def reactivate_employee_account(
        self,
        employee_id: int,
        reactivated_by: int
    ) -> Tuple[bool, Optional[str]]:
        """직원 계정 재활성화

        Args:
            employee_id: 직원 ID
            reactivated_by: 재활성화 요청자 ID

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            user = User.query.filter_by(employee_id=employee_id).first()
            if user:
                user.is_active = True

            employee.status = 'active'

            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # ========================================
    # 검증
    # ========================================

    def validate_account_data(
        self,
        username: str,
        email: str,
        exclude_user_id: int = None
    ) -> Dict:
        """계정 정보 검증 (API용)

        Args:
            username: 사용자명
            email: 이메일
            exclude_user_id: 중복 체크에서 제외할 사용자 ID (수정 시)

        Returns:
            {'valid': bool, 'errors': {...}}
        """
        errors = {}

        # username 검증
        if not username or len(username) < 4:
            errors['username'] = '사용자명은 4자 이상이어야 합니다.'
        elif not username.isalnum():
            errors['username'] = '사용자명은 영문과 숫자만 사용할 수 있습니다.'
        else:
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != exclude_user_id:
                errors['username'] = '이미 사용 중인 사용자명입니다.'

        # email 검증
        if not email or '@' not in email:
            errors['email'] = '올바른 이메일 형식이 아닙니다.'
        else:
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != exclude_user_id:
                errors['email'] = '이미 사용 중인 이메일입니다.'

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def generate_password(self) -> str:
        """안전한 초기 비밀번호 생성

        Returns:
            생성된 비밀번호
        """
        return ''.join(
            secrets.choice(self.PASSWORD_CHARS)
            for _ in range(self.PASSWORD_LENGTH)
        )

    def get_employees_without_account(self, company_id: int) -> List[Dict]:
        """계정이 없는 직원 목록 조회

        Args:
            company_id: 법인 ID

        Returns:
            계정 없는 직원 목록
        """
        employees = Employee.query.filter_by(company_id=company_id).all()
        result = []

        for emp in employees:
            user = User.query.filter_by(employee_id=emp.id).first()
            if not user:
                result.append({
                    'id': emp.id,
                    'name': emp.name,
                    'department': emp.department,
                    'position': emp.position,
                    'email': emp.email
                })

        return result

    # ========================================
    # Private 메서드
    # ========================================

    def _validate_account_data(self, username: str, email: str) -> Optional[str]:
        """계정 정보 내부 검증

        Returns:
            에러 메시지 (없으면 None)
        """
        if not username or len(username) < 4:
            return "사용자명은 4자 이상이어야 합니다."

        if not email or '@' not in email:
            return "올바른 이메일 형식이 아닙니다."

        # 중복 체크
        if User.query.filter_by(username=username).first():
            return "이미 사용 중인 사용자명입니다."

        if User.query.filter_by(email=email).first():
            return "이미 사용 중인 이메일입니다."

        return None

    def _create_employee(self, employee_data: Dict, company_id: int) -> Employee:
        """Employee 객체 생성

        Args:
            employee_data: 직원 정보
            company_id: 법인 ID (User 연결용, Employee는 organization_id 사용)

        Returns:
            생성된 Employee 객체
        """
        # organization_id가 없으면 company의 root_organization_id 사용
        organization_id = employee_data.get('organization_id')
        if not organization_id:
            from app.models.company import Company
            company = Company.query.get(company_id)
            if company and company.root_organization_id:
                organization_id = company.root_organization_id

        employee = Employee(
            company_id=company_id,  # 명시적 설정 (손실 방지)
            name=employee_data.get('name', ''),
            photo=employee_data.get('photo') or '/static/images/face/face_01_m.png',
            department=employee_data.get('department', ''),
            position=employee_data.get('position', ''),
            status=employee_data.get('status', 'active'),
            hire_date=employee_data.get('hire_date', ''),
            phone=employee_data.get('phone', ''),
            email=employee_data.get('email', ''),
            organization_id=organization_id,
            employee_number=employee_data.get('employee_number'),
            team=employee_data.get('team'),
            job_title=employee_data.get('job_title'),
            work_location=employee_data.get('work_location'),
            internal_phone=employee_data.get('internal_phone'),
            company_email=employee_data.get('company_email'),
            english_name=employee_data.get('english_name'),
            birth_date=employee_data.get('birth_date'),
            gender=employee_data.get('gender'),
            address=employee_data.get('address'),
            detailed_address=employee_data.get('detailed_address'),
            postal_code=employee_data.get('postal_code'),
            resident_number=employee_data.get('resident_number'),
            mobile_phone=employee_data.get('mobile_phone'),
            home_phone=employee_data.get('home_phone'),
            nationality=employee_data.get('nationality'),
            blood_type=employee_data.get('blood_type'),
            religion=employee_data.get('religion'),
            hobby=employee_data.get('hobby'),
            specialty=employee_data.get('specialty'),
        )
        db.session.add(employee)
        return employee

    def _create_user(
        self,
        account_data: Dict,
        employee_id: int,
        company_id: int,
        parent_user_id: int
    ) -> User:
        """User 객체 생성

        Args:
            account_data: 계정 정보
            employee_id: 연결할 직원 ID
            company_id: 법인 ID
            parent_user_id: 부모 사용자 ID (법인 관리자)

        Returns:
            생성된 User 객체
        """
        user = User(
            username=account_data.get('username'),
            email=account_data.get('email'),
            role=account_data.get('role', User.ROLE_EMPLOYEE),
            account_type=User.ACCOUNT_EMPLOYEE_SUB,
            employee_id=employee_id,
            company_id=company_id,
            parent_user_id=parent_user_id,
            is_active=True
        )

        # 비밀번호 설정
        password = account_data.get('password') or self.generate_password()
        user.set_password(password)

        db.session.add(user)
        return user


# 싱글톤 인스턴스
employee_account_service = EmployeeAccountService()
