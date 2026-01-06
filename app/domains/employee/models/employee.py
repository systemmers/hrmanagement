"""
Employee SQLAlchemy 모델

직원 기본 정보 및 확장 정보를 포함합니다.
Phase 4: 통합 프로필 연결
Phase 9: FieldRegistry 기반 to_dict() 정렬
Phase 23: resigned 상태 자동 처리 (resignation_date, PCC.status)
"""
from collections import OrderedDict
from datetime import datetime, date
from typing import Optional

from sqlalchemy import event

from app.database import db
from app.shared.constants.status import ContractStatus


class Employee(db.Model):
    """직원 모델"""
    __tablename__ = 'employees'

    # 기본 정보 (10개 필드)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_number = db.Column(db.String(20), unique=True, nullable=True)  # 사번 (EMP-YYYY-NNNN)

    # 통합 프로필 연결 (Phase 4)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)

    # 퇴사 관련 필드
    resignation_date = db.Column(db.Date, nullable=True)  # 퇴직일
    data_retention_until = db.Column(db.Date, nullable=True)  # 데이터 보관 만료일
    probation_end = db.Column(db.Date, nullable=True)  # 수습종료일
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(500), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    hire_date = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(200), nullable=True)

    # 조직 연결
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    organization = db.relationship(
        'Organization',
        foreign_keys=[organization_id],
        backref=db.backref('employees', lazy='dynamic')
    )

    # 회사 연결 (직접 참조)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)

    # 소속 정보 추가 필드
    team = db.Column(db.String(100), nullable=True)
    # 직급 체계 (Career 모델과 일관성 유지)
    # position: 직위 (서열 - 사원, 대리, 과장, 부장) - 기본정보에 이미 존재
    job_grade = db.Column(db.String(50), nullable=True)  # 직급 (역량 레벨 - L3, 2호봉, Senior)
    job_title = db.Column(db.String(100), nullable=True)  # 직책 (책임자 역할 - 팀장, 본부장, CFO)
    job_role = db.Column(db.String(100), nullable=True)  # 직무 (수행 업무 - 인사기획, 회계관리)
    work_location = db.Column(db.String(200), nullable=True)
    internal_phone = db.Column(db.String(50), nullable=True)
    company_email = db.Column(db.String(200), nullable=True)

    # 확장 정보 (17개 필드)
    english_name = db.Column(db.String(100), nullable=True)
    chinese_name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.String(20), nullable=True)
    lunar_birth = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(10), nullable=True)
    mobile_phone = db.Column(db.String(50), nullable=True)
    home_phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    detailed_address = db.Column(db.String(500), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    resident_number = db.Column(db.String(20), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    # blood_type, religion 삭제됨 (Phase 28 마이그레이션)
    hobby = db.Column(db.String(200), nullable=True)
    specialty = db.Column(db.String(200), nullable=True)
    disability_info = db.Column(db.Text, nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)  # 결혼여부: single, married, divorced, widowed

    # 실제 거주 주소 (주민등록상 주소와 분리)
    actual_postal_code = db.Column(db.String(20), nullable=True)
    actual_address = db.Column(db.String(500), nullable=True)
    actual_detailed_address = db.Column(db.String(500), nullable=True)

    # 비상연락처
    emergency_contact = db.Column(db.String(50), nullable=True)
    emergency_relation = db.Column(db.String(50), nullable=True)

    # 1:N 관계
    educations = db.relationship('Education', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    careers = db.relationship('Career', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    family_members = db.relationship('FamilyMember', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    languages = db.relationship('Language', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    salary_histories = db.relationship('SalaryHistory', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    promotions = db.relationship('Promotion', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    evaluations = db.relationship('Evaluation', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    trainings = db.relationship('Training', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    hr_projects = db.relationship('HrProject', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    project_participations = db.relationship('ProjectParticipation', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    awards = db.relationship('Award', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    assets = db.relationship('Asset', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    salary_payments = db.relationship('SalaryPayment', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='employee', lazy='dynamic', cascade='all, delete-orphan')

    # 1:1 관계
    military_service = db.relationship('MilitaryService', backref='employee', uselist=False, cascade='all, delete-orphan')
    salary = db.relationship('Salary', backref='employee', uselist=False, cascade='all, delete-orphan')
    benefit = db.relationship('Benefit', backref='employee', uselist=False, cascade='all, delete-orphan')
    contract = db.relationship('Contract', backref='employee', uselist=False, cascade='all, delete-orphan')
    insurance = db.relationship('Insurance', backref='employee', uselist=False, cascade='all, delete-orphan')

    # 통합 프로필 관계 (Phase 4)
    profile = db.relationship(
        'Profile',
        backref=db.backref('employees', lazy='dynamic'),
        foreign_keys=[profile_id]
    )

    # 템플릿 호환성 프로퍼티 (employment_type -> contract.employee_type)
    @property
    def employment_type(self):
        """템플릿 호환성: employment_type -> contract.employee_type"""
        return self.contract.employee_type if self.contract else None

    def _collect_raw_data(self) -> dict:
        """원시 필드 데이터 수집 (내부용)"""
        return {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'department': self.department,
            'position': self.position,
            'status': self.status,
            'hire_date': self.hire_date,
            'phone': self.phone,
            'email': self.email,
            'organization_id': self.organization_id,
            'english_name': self.english_name,
            'chinese_name': self.chinese_name,
            'birth_date': self.birth_date,
            'lunar_birth': self.lunar_birth,
            'gender': self.gender,
            'mobile_phone': self.mobile_phone,
            'home_phone': self.home_phone,
            'address': self.address,
            'detailed_address': self.detailed_address,
            'postal_code': self.postal_code,
            'resident_number': self.resident_number,
            'nationality': self.nationality,
            # blood_type, religion 삭제됨 (Phase 28)
            'hobby': self.hobby,
            'specialty': self.specialty,
            'disability_info': self.disability_info,
            'marital_status': self.marital_status,
            # 실제 거주 주소
            'actual_postal_code': self.actual_postal_code,
            'actual_address': self.actual_address,
            'actual_detailed_address': self.actual_detailed_address,
            # 비상연락처
            'emergency_contact': self.emergency_contact,
            'emergency_relation': self.emergency_relation,
            # 소속 정보 추가 필드
            'team': self.team,
            # 직급 체계
            'job_grade': self.job_grade,
            'job_title': self.job_title,
            'job_role': self.job_role,
            'work_location': self.work_location,
            'internal_phone': self.internal_phone,
            'company_email': self.company_email,
            'employee_number': self.employee_number,
            # 통합 프로필 (Phase 4)
            'profile_id': self.profile_id,
            'resignation_date': self.resignation_date.isoformat() if self.resignation_date else None,
            'data_retention_until': self.data_retention_until.isoformat() if self.data_retention_until else None,
            'probation_end': self.probation_end.isoformat() if self.probation_end else None,
        }

    def to_dict(self, ordered: bool = False, account_type: Optional[str] = None) -> dict:
        """딕셔너리 반환 (Phase 9: FieldRegistry 기반 정렬 지원)

        Args:
            ordered: True면 FieldRegistry 순서 적용, False면 기존 방식
            account_type: 가시성 필터링용 계정 타입

        Returns:
            직원 정보 딕셔너리
        """
        raw = self._collect_raw_data()

        # 기존 방식 (하위 호환성)
        if not ordered:
            raw['organization'] = self.organization.to_dict() if self.organization else None
            return raw

        # Phase 9: FieldRegistry 기반 정렬
        from app.shared.constants.field_registry import FieldRegistry

        result = OrderedDict()
        result['id'] = raw.pop('id')

        # 섹션별 정렬 적용
        section_ids = ['personal_basic', 'contact', 'address', 'actual_address',
                       'personal_extended', 'organization', 'contract']
        for section_id in section_ids:
            section_data = FieldRegistry.to_ordered_dict(section_id, raw, account_type)
            for key, value in section_data.items():
                if key in raw:
                    result[key] = raw.pop(key)

        # 조직 정보 추가
        result['organization'] = self.organization.to_dict() if self.organization else None

        # 나머지 필드 추가 (정의되지 않은 필드들)
        for key, value in raw.items():
            result[key] = value

        return dict(result)

    @classmethod
    def from_dict(cls, data):
        """camelCase/snake_case 딕셔너리에서 모델 생성"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            photo=data.get('photo'),
            department=data.get('department'),
            position=data.get('position'),
            status=data.get('status'),
            hire_date=data.get('hire_date') or data.get('hireDate'),
            phone=data.get('phone'),
            email=data.get('email'),
            # 조직 연결
            organization_id=data.get('organization_id') or data.get('organizationId'),
            # 소속정보 추가 필드
            employee_number=data.get('employee_number') or data.get('employeeNumber'),
            team=data.get('team'),
            # 직급 체계
            job_grade=data.get('job_grade') or data.get('jobGrade'),
            job_title=data.get('job_title') or data.get('jobTitle'),
            job_role=data.get('job_role') or data.get('jobRole'),
            work_location=data.get('work_location') or data.get('workLocation'),
            internal_phone=data.get('internal_phone') or data.get('internalPhone'),
            company_email=data.get('company_email') or data.get('companyEmail'),
            # 개인정보
            english_name=data.get('english_name') or data.get('englishName'),
            chinese_name=data.get('chinese_name') or data.get('chineseName'),
            birth_date=data.get('birth_date') or data.get('birthDate'),
            lunar_birth=data.get('lunar_birth') or data.get('lunarBirth', False),
            gender=data.get('gender'),
            mobile_phone=data.get('mobile_phone') or data.get('mobilePhone'),
            home_phone=data.get('home_phone') or data.get('homePhone'),
            address=data.get('address'),
            detailed_address=data.get('detailed_address') or data.get('detailedAddress'),
            postal_code=data.get('postal_code') or data.get('postalCode'),
            resident_number=data.get('resident_number') or data.get('residentNumber'),
            nationality=data.get('nationality'),
            # blood_type, religion 삭제됨 (Phase 28)
            hobby=data.get('hobby'),
            specialty=data.get('specialty'),
            disability_info=data.get('disability_info') or data.get('disabilityInfo'),
            marital_status=data.get('marital_status') or data.get('maritalStatus'),
            # 실제 거주 주소
            actual_postal_code=data.get('actual_postal_code') or data.get('actualPostalCode'),
            actual_address=data.get('actual_address') or data.get('actualAddress'),
            actual_detailed_address=data.get('actual_detailed_address') or data.get('actualDetailedAddress'),
            # 비상연락처
            emergency_contact=data.get('emergency_contact') or data.get('emergencyContact'),
            emergency_relation=data.get('emergency_relation') or data.get('emergencyRelation'),
            # 수습종료일
            probation_end=data.get('probation_end') or data.get('probationEnd'),
        )

    def __repr__(self):
        return f'<Employee {self.id}: {self.name}>'


# ===== SQLAlchemy Event Listeners (Phase 23) =====

@event.listens_for(Employee.status, 'set')
def on_employee_status_change(target, value, oldvalue, initiator):
    """Employee.status 변경 시 자동 처리

    Phase 23 데이터 정합성 규칙:
    1. resigned 전환 시 resignation_date 자동 설정 (없을 경우)
    2. resigned 전환 시 연결된 PCC.status → terminated 전환
    """
    # 같은 값이면 무시
    if value == oldvalue:
        return

    # resigned 상태로 전환될 때
    if value == 'resigned':
        # 1. resignation_date 자동 설정
        if not target.resignation_date:
            target.resignation_date = date.today()

        # 2. 연결된 PCC.status → terminated 전환
        # 주의: 순환 import 방지를 위해 함수 내에서 import
        _update_pcc_status_to_terminated(target)


def _update_pcc_status_to_terminated(employee: Employee):
    """Employee의 연결된 PCC를 terminated로 전환

    Args:
        employee: 퇴사 처리된 Employee 객체
    """
    if not employee.employee_number:
        return

    # 순환 import 방지
    from app.models.person_contract import PersonCorporateContract

    # employee_number로 approved 상태인 PCC 조회
    contracts = PersonCorporateContract.query.filter_by(
        employee_number=employee.employee_number,
        status=ContractStatus.APPROVED
    ).all()

    for contract in contracts:
        contract.status = ContractStatus.TERMINATED
        contract.terminated_at = datetime.utcnow()
