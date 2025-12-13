"""
Employee SQLAlchemy 모델

직원 기본 정보 및 확장 정보를 포함합니다.
"""
from app.database import db


class Employee(db.Model):
    """직원 모델"""
    __tablename__ = 'employees'

    # 기본 정보 (10개 필드)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_number = db.Column(db.String(20), unique=True, nullable=True)  # 사번 (EMP-YYYY-NNNN)
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

    # 소속 정보 추가 필드
    team = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
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
    blood_type = db.Column(db.String(10), nullable=True)
    religion = db.Column(db.String(50), nullable=True)
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
    projects = db.relationship('Project', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
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

    def to_dict(self):
        """딕셔너리 반환 (snake_case 통일)"""
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
            'organization': self.organization.to_dict() if self.organization else None,
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
            'blood_type': self.blood_type,
            'religion': self.religion,
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
            'job_title': self.job_title,
            'work_location': self.work_location,
            'internal_phone': self.internal_phone,
            'company_email': self.company_email,
            'employee_number': self.employee_number,
        }

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
            job_title=data.get('job_title') or data.get('jobTitle'),
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
            blood_type=data.get('blood_type') or data.get('bloodType'),
            religion=data.get('religion'),
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
        )

    def __repr__(self):
        return f'<Employee {self.id}: {self.name}>'
