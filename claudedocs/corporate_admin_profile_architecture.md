# 법인 관리자 프로필 시스템 백엔드 아키텍처 설계

## 1. 개요

### 1.1 목적
법인 관리자(account_type='corporate', employee_id=None)를 위한 프로필 기능을 설계하여 기존 통합 프로필 시스템과 일관성 있게 통합합니다.

### 1.2 현재 상황
- 법인 관리자 계정은 프로필 접근 시 대시보드로 리다이렉트됨
- 위치: `app/blueprints/profile/decorators.py:57-61`
- 기존 어댑터: EmployeeProfileAdapter, PersonalProfileAdapter

### 1.3 설계 원칙
- 기존 어댑터 패턴 준수
- User/Company 모델 활용 (신규 모델 최소화)
- 점진적 롤아웃 지원
- 권한 체계와의 일관성 유지

---

## 2. 데이터 모델 설계

### 2.1 CorporateAdminProfile 모델

법인 관리자의 프로필 정보를 저장하는 경량 모델을 설계합니다.

```python
"""
CorporateAdminProfile 모델
법인 관리자의 프로필 정보 관리
"""
from datetime import datetime
from app.database import db


class CorporateAdminProfile(db.Model):
    """법인 관리자 프로필 모델"""
    __tablename__ = 'corporate_admin_profiles'

    # 기본 키
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 연결 정보
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        unique=True,
        index=True
    )
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False,
        index=True
    )

    # 기본 정보
    name = db.Column(db.String(100), nullable=False)
    english_name = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(50), nullable=True)  # 직책 (대표이사, CFO 등)

    # 연락처 정보
    mobile_phone = db.Column(db.String(20), nullable=True)
    office_phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)  # User.email과 별도 관리 가능

    # 프로필 사진
    photo = db.Column(db.String(300), nullable=True)

    # 추가 정보
    department = db.Column(db.String(100), nullable=True)  # 소속 부서
    bio = db.Column(db.Text, nullable=True)  # 간략한 소개

    # 메타 정보
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship(
        'User',
        backref=db.backref('admin_profile', uselist=False, lazy=True)
    )
    company = db.relationship(
        'Company',
        backref=db.backref('admin_profiles', lazy='dynamic')
    )

    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'name': self.name,
            'english_name': self.english_name,
            'position': self.position,
            'mobile_phone': self.mobile_phone,
            'office_phone': self.office_phone,
            'email': self.email,
            'photo': self.photo,
            'department': self.department,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            user_id=data.get('user_id'),
            company_id=data.get('company_id'),
            name=data.get('name'),
            english_name=data.get('english_name'),
            position=data.get('position'),
            mobile_phone=data.get('mobile_phone'),
            office_phone=data.get('office_phone'),
            email=data.get('email'),
            photo=data.get('photo'),
            department=data.get('department'),
            bio=data.get('bio'),
            is_active=data.get('is_active', True),
        )

    def __repr__(self):
        return f'<CorporateAdminProfile {self.name} - Company {self.company_id}>'
```

### 2.2 모델 관계 다이어그램

```
User (account_type='corporate')
  |
  | 1:1
  |
CorporateAdminProfile
  |
  | N:1
  |
Company
```

### 2.3 기존 모델과의 비교

| 필드 | Employee | PersonalProfile | CorporateAdminProfile |
|------|----------|-----------------|----------------------|
| 이름 | name | name | name |
| 영문명 | english_name | english_name | english_name |
| 직책/직급 | position | - | position |
| 휴대폰 | mobile_phone | mobile_phone | mobile_phone |
| 이메일 | email | email | email |
| 사진 | photo | photo | photo |
| 소속 | organization_id | - | company_id |
| 부서 | department | - | department |
| 사번 | employee_number | - | - |
| 생년월일 | birth_date | birth_date | - |
| 주소 | address | address | - |

설계 근거:
- 법인 관리자는 직원이 아니므로 Employee 모델 사용 부적합
- PersonalProfile보다 간소화된 정보만 필요
- Company와의 직접 연결로 법인 정보 접근 용이

---

## 3. 어댑터 설계

### 3.1 CorporateAdminProfileAdapter

기존 ProfileAdapter 인터페이스를 구현하는 새로운 어댑터를 설계합니다.

```python
"""
CorporateAdminProfileAdapter - 법인 관리자용 프로필 어댑터
"""
from typing import Dict, Any, List, Optional
from app.adapters.profile_adapter import ProfileAdapter


class CorporateAdminProfileAdapter(ProfileAdapter):
    """법인 관리자용 어댑터 (CorporateAdminProfile 모델 래핑)"""

    AVAILABLE_SECTIONS = [
        'basic',        # 기본 정보
        'company',      # 소속 법인 정보
    ]

    def __init__(self, admin_profile):
        """
        Args:
            admin_profile: CorporateAdminProfile 모델 인스턴스
        """
        self.admin_profile = admin_profile
        self.company = admin_profile.company

    def get_basic_info(self) -> Dict[str, Any]:
        """기본 개인정보 반환"""
        return {
            'id': self.admin_profile.id,
            'name': self.admin_profile.name,
            'english_name': self.admin_profile.english_name,
            'position': self.admin_profile.position,
            'mobile_phone': self.admin_profile.mobile_phone,
            'office_phone': self.admin_profile.office_phone,
            'email': self.admin_profile.email,
            'photo': self.admin_profile.photo,
            'department': self.admin_profile.department,
            'bio': self.admin_profile.bio,

            # 어댑터 인터페이스 호환용 필드 (None 반환)
            'birth_date': None,
            'gender': None,
            'address': None,
            'detailed_address': None,
            'postal_code': None,
            'employee_number': None,
            'nationality': None,
            'blood_type': None,
            'religion': None,
            'hobby': None,
            'specialty': None,
            'disability_info': None,
        }

    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """
        소속 법인 정보 반환 (법인 관리자 전용)
        Employee의 organization_info와 다른 구조
        """
        if not self.company:
            return None

        return {
            'company': self.company.to_dict(include_stats=True),
            'company_id': self.admin_profile.company_id,
            'position': self.admin_profile.position,
            'department': self.admin_profile.department,
            'role': 'admin',  # 법인 관리자 역할
        }

    # 법인 관리자는 지원하지 않는 정보 (None 반환)
    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        """계약 정보 반환 (법인 관리자는 미지원)"""
        return None

    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        """급여 정보 반환 (법인 관리자는 미지원)"""
        return None

    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        """복리후생 정보 반환 (법인 관리자는 미지원)"""
        return None

    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        """4대보험 정보 반환 (법인 관리자는 미지원)"""
        return None

    def get_education_list(self) -> List[Dict[str, Any]]:
        """학력 정보 목록 반환 (법인 관리자는 미지원)"""
        return []

    def get_career_list(self) -> List[Dict[str, Any]]:
        """경력 정보 목록 반환 (법인 관리자는 미지원)"""
        return []

    def get_certificate_list(self) -> List[Dict[str, Any]]:
        """자격증 목록 반환 (법인 관리자는 미지원)"""
        return []

    def get_language_list(self) -> List[Dict[str, Any]]:
        """언어능력 목록 반환 (법인 관리자는 미지원)"""
        return []

    def get_military_info(self) -> Optional[Dict[str, Any]]:
        """병역 정보 반환 (법인 관리자는 미지원)"""
        return None

    def is_corporate(self) -> bool:
        """법인 계정 여부 (항상 True)"""
        return True

    def is_corporate_admin(self) -> bool:
        """법인 관리자 여부 (항상 True)"""
        return True

    def get_available_sections(self) -> List[str]:
        """사용 가능한 섹션 목록"""
        return self.AVAILABLE_SECTIONS.copy()

    def get_profile_id(self) -> int:
        """프로필 ID (admin_profile.id)"""
        return self.admin_profile.id

    def get_display_name(self) -> str:
        """표시용 이름 (이름 + 직책)"""
        parts = [self.admin_profile.name]
        if self.admin_profile.position:
            parts.append(self.admin_profile.position)
        return ' '.join(parts)

    def get_photo_url(self) -> Optional[str]:
        """프로필 사진 URL"""
        return self.admin_profile.photo

    def get_user_id(self) -> int:
        """연결된 User ID"""
        return self.admin_profile.user_id

    def get_company(self):
        """소속 법인 객체 반환"""
        return self.company
```

### 3.2 어댑터 비교 매트릭스

| 메서드 | Employee | Personal | CorporateAdmin |
|--------|----------|----------|----------------|
| get_basic_info() | 전체 | 전체 | 간소화 |
| get_organization_info() | Employee 조직 | None | Company 정보 |
| get_contract_info() | 지원 | None | None |
| get_salary_info() | 지원 | None | None |
| get_education_list() | 지원 | 지원 | None |
| is_corporate() | True | False | True |
| is_corporate_admin() | - | - | True |

---

## 4. 서비스 계층 설계

### 4.1 CorporateAdminProfileService

```python
"""
CorporateAdminProfileService - 법인 관리자 프로필 서비스
"""
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage

from app.database import db
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.models.user import User
from app.models.company import Company
from app.services.file_storage_service import FileStorageService


class CorporateAdminProfileService:
    """법인 관리자 프로필 관리 서비스"""

    @staticmethod
    def create_profile(user_id: int, data: Dict[str, Any]) -> CorporateAdminProfile:
        """
        법인 관리자 프로필 생성

        Args:
            user_id: User ID
            data: 프로필 데이터

        Returns:
            생성된 CorporateAdminProfile 인스턴스

        Raises:
            ValueError: 유효하지 않은 데이터
        """
        # 사용자 검증
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"사용자를 찾을 수 없습니다: {user_id}")

        if not user.is_corporate_account():
            raise ValueError("법인 계정만 관리자 프로필을 생성할 수 있습니다")

        if not user.company_id:
            raise ValueError("법인 정보가 연결되지 않았습니다")

        # 중복 프로필 확인
        existing = CorporateAdminProfile.query.filter_by(user_id=user_id).first()
        if existing:
            raise ValueError("이미 프로필이 존재합니다")

        # 프로필 생성
        data['user_id'] = user_id
        data['company_id'] = user.company_id

        # 기본값 설정
        if 'name' not in data:
            data['name'] = user.username
        if 'email' not in data:
            data['email'] = user.email

        profile = CorporateAdminProfile.from_dict(data)

        db.session.add(profile)
        db.session.commit()

        return profile

    @staticmethod
    def get_profile_by_user_id(user_id: int) -> Optional[CorporateAdminProfile]:
        """
        User ID로 프로필 조회

        Args:
            user_id: User ID

        Returns:
            CorporateAdminProfile 또는 None
        """
        return CorporateAdminProfile.query.filter_by(user_id=user_id).first()

    @staticmethod
    def update_profile(profile_id: int, data: Dict[str, Any]) -> CorporateAdminProfile:
        """
        프로필 정보 수정

        Args:
            profile_id: 프로필 ID
            data: 수정할 데이터

        Returns:
            수정된 CorporateAdminProfile

        Raises:
            ValueError: 유효하지 않은 데이터
        """
        profile = CorporateAdminProfile.query.get(profile_id)
        if not profile:
            raise ValueError(f"프로필을 찾을 수 없습니다: {profile_id}")

        # 수정 가능한 필드만 업데이트
        allowed_fields = [
            'name', 'english_name', 'position', 'mobile_phone',
            'office_phone', 'email', 'department', 'bio'
        ]

        for field in allowed_fields:
            if field in data:
                setattr(profile, field, data[field])

        db.session.commit()

        return profile

    @staticmethod
    def upload_photo(profile_id: int, file: FileStorage) -> str:
        """
        프로필 사진 업로드

        Args:
            profile_id: 프로필 ID
            file: 업로드할 파일

        Returns:
            업로드된 파일 URL

        Raises:
            ValueError: 유효하지 않은 파일
        """
        profile = CorporateAdminProfile.query.get(profile_id)
        if not profile:
            raise ValueError(f"프로필을 찾을 수 없습니다: {profile_id}")

        # 기존 사진 삭제
        if profile.photo:
            FileStorageService.delete_file(profile.photo)

        # 새 사진 업로드
        file_url = FileStorageService.upload_file(
            file,
            folder=f'profile/admin/{profile.user_id}'
        )

        profile.photo = file_url
        db.session.commit()

        return file_url

    @staticmethod
    def delete_profile(profile_id: int) -> None:
        """
        프로필 삭제 (비활성화)

        Args:
            profile_id: 프로필 ID
        """
        profile = CorporateAdminProfile.query.get(profile_id)
        if not profile:
            raise ValueError(f"프로필을 찾을 수 없습니다: {profile_id}")

        # 사진 삭제
        if profile.photo:
            FileStorageService.delete_file(profile.photo)

        # 소프트 삭제
        profile.is_active = False
        db.session.commit()

    @staticmethod
    def auto_create_from_user(user: User) -> CorporateAdminProfile:
        """
        User 정보로부터 자동 프로필 생성

        Args:
            user: User 인스턴스

        Returns:
            생성된 CorporateAdminProfile
        """
        data = {
            'name': user.username,
            'email': user.email,
            'position': '관리자' if user.is_admin() else None,
        }

        return CorporateAdminProfileService.create_profile(user.id, data)
```

---

## 5. 라우트 설계

### 5.1 데코레이터 수정

기존 `unified_profile_required` 데코레이터를 수정하여 법인 관리자 지원:

```python
# app/blueprints/profile/decorators.py

def unified_profile_required(f):
    """
    통합 프로필 인증 데코레이터 (법인 관리자 지원 추가)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        employee_id = session.get('employee_id')
        account_type = session.get('account_type')

        # 인증 확인
        if not user_id and not employee_id:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))

        # 법인 직원 어댑터 (employee_id가 있는 경우)
        if employee_id:
            employee = Employee.query.get(employee_id)
            if not employee:
                flash('직원 정보를 찾을 수 없습니다.', 'error')
                session.pop('employee_id', None)
                return redirect(url_for('auth.login'))

            g.profile = EmployeeProfileAdapter(employee)
            g.is_corporate = True
            g.is_corporate_admin = False
            g.employee = employee

        # 법인 관리자 어댑터 (employee_id 없이 account_type이 corporate인 경우)
        elif account_type == 'corporate':
            # CorporateAdminProfile 조회
            from app.models.corporate_admin_profile import CorporateAdminProfile
            from app.adapters.profile_adapter import CorporateAdminProfileAdapter
            from app.services.corporate_admin_profile_service import CorporateAdminProfileService

            admin_profile = CorporateAdminProfileService.get_profile_by_user_id(user_id)

            # 프로필이 없으면 자동 생성 (선택적)
            if not admin_profile:
                user = User.query.get(user_id)
                if user and user.is_corporate_account():
                    admin_profile = CorporateAdminProfileService.auto_create_from_user(user)
                else:
                    flash('법인 관리자 프로필을 생성할 수 없습니다.', 'error')
                    return redirect(url_for('main.index'))

            g.profile = CorporateAdminProfileAdapter(admin_profile)
            g.is_corporate = True
            g.is_corporate_admin = True
            g.admin_profile = admin_profile

        # 개인 계정 어댑터
        else:
            profile = PersonalProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                flash('프로필을 먼저 생성해주세요.', 'info')
                return redirect(url_for('personal.profile'))

            g.profile = PersonalProfileAdapter(profile)
            g.is_corporate = False
            g.is_corporate_admin = False
            g.personal_profile = profile

        return f(*args, **kwargs)
    return decorated_function
```

### 5.2 라우트 추가

법인 관리자 전용 라우트:

```python
# app/blueprints/profile/routes.py

@profile_bp.route('/admin/edit', methods=['GET', 'POST'])
@unified_profile_required
def admin_edit():
    """
    법인 관리자 프로필 수정

    법인 관리자만 접근 가능
    """
    if not g.is_corporate_admin:
        flash('법인 관리자만 접근 가능합니다.', 'warning')
        return redirect(url_for('profile.view'))

    from app.services.corporate_admin_profile_service import CorporateAdminProfileService

    if request.method == 'POST':
        try:
            data = {
                'name': request.form.get('name'),
                'english_name': request.form.get('english_name'),
                'position': request.form.get('position'),
                'mobile_phone': request.form.get('mobile_phone'),
                'office_phone': request.form.get('office_phone'),
                'email': request.form.get('email'),
                'department': request.form.get('department'),
                'bio': request.form.get('bio'),
            }

            CorporateAdminProfileService.update_profile(g.admin_profile.id, data)
            flash('프로필이 수정되었습니다.', 'success')
            return redirect(url_for('profile.view'))

        except Exception as e:
            flash(f'프로필 수정 실패: {str(e)}', 'error')

    return render_template('profile/admin_edit.html', profile=g.admin_profile)


@profile_bp.route('/admin/photo', methods=['POST'])
@unified_profile_required
def admin_upload_photo():
    """법인 관리자 프로필 사진 업로드"""
    if not g.is_corporate_admin:
        return jsonify({'success': False, 'error': '권한이 없습니다'}), 403

    from app.services.corporate_admin_profile_service import CorporateAdminProfileService

    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': '파일이 없습니다'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다'}), 400

    try:
        file_url = CorporateAdminProfileService.upload_photo(g.admin_profile.id, file)
        return jsonify({'success': True, 'photo_url': file_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### 5.3 API 엔드포인트 설계

| 엔드포인트 | 메서드 | 설명 | 권한 |
|-----------|--------|------|------|
| `/profile/` | GET | 통합 프로필 조회 (관리자 포함) | 인증된 사용자 |
| `/profile/admin/edit` | GET, POST | 관리자 프로필 수정 | 법인 관리자 |
| `/profile/admin/photo` | POST | 프로필 사진 업로드 | 법인 관리자 |
| `/profile/section/basic` | GET | 기본 정보 JSON | 인증된 사용자 |
| `/profile/section/company` | GET | 법인 정보 JSON (관리자용) | 법인 관리자 |

---

## 6. 마이그레이션 전략

### 6.1 데이터베이스 마이그레이션

```python
"""
마이그레이션: 법인 관리자 프로필 테이블 생성
Revision ID: xxxx_create_corporate_admin_profiles
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'corporate_admin_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('english_name', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=50), nullable=True),
        sa.Column('mobile_phone', sa.String(length=20), nullable=True),
        sa.Column('office_phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('photo', sa.String(length=300), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    )

    op.create_index('ix_corporate_admin_profiles_user_id', 'corporate_admin_profiles', ['user_id'], unique=True)
    op.create_index('ix_corporate_admin_profiles_company_id', 'corporate_admin_profiles', ['company_id'], unique=False)


def downgrade():
    op.drop_index('ix_corporate_admin_profiles_company_id', table_name='corporate_admin_profiles')
    op.drop_index('ix_corporate_admin_profiles_user_id', table_name='corporate_admin_profiles')
    op.drop_table('corporate_admin_profiles')
```

### 6.2 기존 데이터 마이그레이션

```python
"""
데이터 마이그레이션: 기존 법인 관리자에 프로필 자동 생성
"""
from app.models.user import User
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.services.corporate_admin_profile_service import CorporateAdminProfileService
from app.database import db


def migrate_existing_corporate_admins():
    """
    기존 법인 관리자 계정에 프로필 자동 생성
    """
    # account_type='corporate' && employee_id=None 사용자 조회
    corporate_admins = User.query.filter(
        User.account_type == User.ACCOUNT_CORPORATE,
        User.employee_id.is_(None),
        User.is_active == True
    ).all()

    created_count = 0
    error_count = 0

    for user in corporate_admins:
        try:
            # 이미 프로필이 있는지 확인
            existing = CorporateAdminProfile.query.filter_by(user_id=user.id).first()
            if existing:
                continue

            # 자동 생성
            CorporateAdminProfileService.auto_create_from_user(user)
            created_count += 1

        except Exception as e:
            print(f"Error creating profile for user {user.id}: {e}")
            error_count += 1

    print(f"Migration complete: {created_count} profiles created, {error_count} errors")
```

### 6.3 점진적 롤아웃 계획

**Phase 1: 인프라 준비**
- 모델 및 마이그레이션 배포
- 서비스 계층 구현
- 어댑터 구현

**Phase 2: 기능 플래그 활성화**
```python
# config.py
ENABLE_CORPORATE_ADMIN_PROFILE = os.environ.get('ENABLE_CORPORATE_ADMIN_PROFILE', 'false').lower() == 'true'
```

**Phase 3: 데이터 마이그레이션**
- 기존 법인 관리자 계정에 프로필 자동 생성
- 검증 및 오류 처리

**Phase 4: UI 배포**
- 프로필 조회/수정 템플릿
- 사진 업로드 기능
- 사용자 피드백 수집

**Phase 5: 안정화 및 정식 출시**
- 기능 플래그 제거
- 전체 사용자 활성화

---

## 7. 권한 체계

### 7.1 접근 권한 매트릭스

| 기능 | Personal | Employee | Corporate Admin |
|-----|----------|----------|-----------------|
| 기본 프로필 조회 | 본인만 | 본인만 | 본인만 |
| 기본 프로필 수정 | 본인만 | 본인만 | 본인만 |
| 법인 정보 조회 | - | 읽기 전용 | 읽기/쓰기 |
| 직원 목록 조회 | - | 제한적 | 전체 |
| 직원 프로필 조회 | - | 제한적 | 전체 |

### 7.2 권한 검증 헬퍼

```python
# app/blueprints/profile/permissions.py

def can_edit_profile(profile_adapter):
    """프로필 수정 권한 확인"""
    user_id = session.get('user_id')

    if hasattr(profile_adapter, 'is_corporate_admin') and profile_adapter.is_corporate_admin():
        return profile_adapter.get_user_id() == user_id

    if hasattr(profile_adapter, 'get_user_id'):
        return profile_adapter.get_user_id() == user_id

    return False


def can_view_company_info(profile_adapter):
    """법인 정보 조회 권한 확인"""
    return profile_adapter.is_corporate() or profile_adapter.is_corporate_admin()
```

---

## 8. 테스트 전략

### 8.1 단위 테스트

```python
# tests/unit/test_corporate_admin_profile.py

import pytest
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.services.corporate_admin_profile_service import CorporateAdminProfileService
from app.adapters.profile_adapter import CorporateAdminProfileAdapter


class TestCorporateAdminProfile:
    """CorporateAdminProfile 모델 테스트"""

    def test_create_profile(self, db_session, corporate_user, company):
        """프로필 생성 테스트"""
        data = {
            'name': '홍길동',
            'position': '대표이사',
            'mobile_phone': '010-1234-5678',
            'email': 'admin@company.com'
        }

        profile = CorporateAdminProfileService.create_profile(corporate_user.id, data)

        assert profile.id is not None
        assert profile.user_id == corporate_user.id
        assert profile.company_id == corporate_user.company_id
        assert profile.name == '홍길동'
        assert profile.position == '대표이사'

    def test_duplicate_profile_error(self, db_session, corporate_user):
        """중복 프로필 생성 오류 테스트"""
        data = {'name': '홍길동'}

        # 첫 번째 생성 성공
        CorporateAdminProfileService.create_profile(corporate_user.id, data)

        # 두 번째 생성 실패
        with pytest.raises(ValueError, match="이미 프로필이 존재합니다"):
            CorporateAdminProfileService.create_profile(corporate_user.id, data)

    def test_update_profile(self, db_session, admin_profile):
        """프로필 수정 테스트"""
        update_data = {
            'position': 'CEO',
            'mobile_phone': '010-9999-9999'
        }

        updated = CorporateAdminProfileService.update_profile(admin_profile.id, update_data)

        assert updated.position == 'CEO'
        assert updated.mobile_phone == '010-9999-9999'


class TestCorporateAdminProfileAdapter:
    """CorporateAdminProfileAdapter 테스트"""

    def test_adapter_basic_info(self, admin_profile):
        """기본 정보 조회 테스트"""
        adapter = CorporateAdminProfileAdapter(admin_profile)

        basic_info = adapter.get_basic_info()

        assert basic_info['name'] == admin_profile.name
        assert basic_info['position'] == admin_profile.position
        assert basic_info['employee_number'] is None  # 관리자는 사번 없음

    def test_adapter_organization_info(self, admin_profile, company):
        """법인 정보 조회 테스트"""
        adapter = CorporateAdminProfileAdapter(admin_profile)

        org_info = adapter.get_organization_info()

        assert org_info is not None
        assert org_info['company_id'] == company.id
        assert org_info['role'] == 'admin'

    def test_adapter_unsupported_sections(self, admin_profile):
        """미지원 섹션 테스트"""
        adapter = CorporateAdminProfileAdapter(admin_profile)

        assert adapter.get_contract_info() is None
        assert adapter.get_salary_info() is None
        assert adapter.get_education_list() == []

    def test_available_sections(self, admin_profile):
        """사용 가능한 섹션 목록 테스트"""
        adapter = CorporateAdminProfileAdapter(admin_profile)

        sections = adapter.get_available_sections()

        assert 'basic' in sections
        assert 'company' in sections
        assert 'salary' not in sections  # 관리자는 미지원
```

### 8.2 통합 테스트

```python
# tests/integration/test_profile_routes.py

class TestProfileRoutesWithCorporateAdmin:
    """법인 관리자 프로필 라우트 통합 테스트"""

    def test_corporate_admin_profile_view(self, client, corporate_admin_user):
        """법인 관리자 프로필 조회 테스트"""
        # 로그인
        with client.session_transaction() as sess:
            sess['user_id'] = corporate_admin_user.id
            sess['account_type'] = 'corporate'

        # 프로필 조회
        response = client.get('/profile/')

        assert response.status_code == 200
        assert b'name' in response.data  # 프로필 정보 포함

    def test_corporate_admin_profile_edit(self, client, corporate_admin_user, admin_profile):
        """법인 관리자 프로필 수정 테스트"""
        with client.session_transaction() as sess:
            sess['user_id'] = corporate_admin_user.id
            sess['account_type'] = 'corporate'

        # 프로필 수정
        response = client.post('/profile/admin/edit', data={
            'name': '수정된이름',
            'position': 'CEO',
        })

        assert response.status_code == 302  # 리다이렉트

        # 수정 확인
        from app.models.corporate_admin_profile import CorporateAdminProfile
        updated = CorporateAdminProfile.query.get(admin_profile.id)
        assert updated.name == '수정된이름'
        assert updated.position == 'CEO'
```

---

## 9. 보안 고려사항

### 9.1 인증 및 권한

- User ID와 account_type 세션 검증
- 프로필 소유자만 수정 가능
- company_id 일치 확인

### 9.2 데이터 검증

```python
# 입력 검증 예시
def validate_profile_data(data):
    """프로필 데이터 유효성 검증"""
    errors = []

    if not data.get('name') or len(data['name']) < 2:
        errors.append('이름은 2자 이상이어야 합니다')

    if data.get('mobile_phone'):
        if not re.match(r'^01[0-9]-\d{4}-\d{4}$', data['mobile_phone']):
            errors.append('휴대폰 번호 형식이 올바르지 않습니다')

    if data.get('email'):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            errors.append('이메일 형식이 올바르지 않습니다')

    return errors
```

### 9.3 파일 업로드 보안

- 파일 타입 검증 (이미지만 허용)
- 파일 크기 제한 (5MB)
- 안전한 파일명 처리
- 바이러스 스캔 (선택적)

---

## 10. 성능 최적화

### 10.1 쿼리 최적화

```python
# 관계 eager loading
admin_profile = CorporateAdminProfile.query.options(
    db.joinedload('company'),
    db.joinedload('user')
).filter_by(user_id=user_id).first()
```

### 10.2 캐싱 전략

```python
from flask_caching import Cache

cache = Cache()

@cache.memoize(timeout=300)  # 5분 캐시
def get_admin_profile_cached(user_id):
    return CorporateAdminProfileService.get_profile_by_user_id(user_id)
```

---

## 11. 모니터링 및 로깅

### 11.1 감사 로그

```python
from app.services.audit_service import AuditService

# 프로필 수정 시 감사 로그 기록
AuditService.log_admin_profile_update(
    user_id=user_id,
    profile_id=profile.id,
    changes=changes,
    ip_address=request.remote_addr
)
```

### 11.2 메트릭 수집

- 프로필 생성/수정 횟수
- 평균 응답 시간
- 오류 발생률

---

## 12. 결론

### 12.1 구현 우선순위

**높음 (P0)**
1. 모델 및 마이그레이션
2. 서비스 계층
3. 어댑터 구현
4. 데코레이터 수정

**중간 (P1)**
5. 라우트 및 API
6. 기본 UI 템플릿
7. 단위 테스트

**낮음 (P2)**
8. 고급 UI 기능
9. 캐싱 및 최적화
10. 통합 테스트

### 12.2 기대 효과

- 법인 관리자 사용자 경험 개선
- 기존 프로필 시스템과 일관성 유지
- 확장 가능한 아키텍처 구조
- 점진적 롤아웃으로 리스크 최소화

### 12.3 다음 단계

1. 설계 검토 및 피드백 수렴
2. 구현 스프린트 계획 수립
3. 개발 환경에서 POC 구현
4. 단위 테스트 및 통합 테스트
5. 스테이징 환경 배포
6. 프로덕션 점진적 롤아웃

---

## 부록

### A. 파일 구조

```
app/
├── models/
│   └── corporate_admin_profile.py          # 신규
├── adapters/
│   └── profile_adapter.py                  # 수정 (CorporateAdminProfileAdapter 추가)
├── services/
│   └── corporate_admin_profile_service.py  # 신규
├── blueprints/
│   └── profile/
│       ├── decorators.py                   # 수정
│       └── routes.py                       # 수정
└── templates/
    └── profile/
        └── admin_edit.html                 # 신규

migrations/
└── versions/
    └── xxxx_create_corporate_admin_profiles.py  # 신규

tests/
├── unit/
│   └── test_corporate_admin_profile.py     # 신규
└── integration/
    └── test_profile_routes.py              # 수정
```

### B. 환경 변수

```bash
# .env
ENABLE_CORPORATE_ADMIN_PROFILE=true
PROFILE_PHOTO_MAX_SIZE=5242880  # 5MB
PROFILE_PHOTO_ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
```

### C. 참고 문서

- 기존 프로필 어댑터 패턴: `app/adapters/profile_adapter.py`
- User 모델 구조: `app/models/user.py`
- Company 모델 구조: `app/models/company.py`
- 통합 프로필 라우트: `app/blueprints/profile/routes.py`
