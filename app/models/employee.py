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
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case + hireDate 호환)"""
        return {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'department': self.department,
            'position': self.position,
            'status': self.status,
            'hire_date': self.hire_date,
            'hireDate': self.hire_date,  # 템플릿 호환용
            'phone': self.phone,
            'email': self.email,
            'organization_id': self.organization_id,
            'organization': self.organization.to_dict() if self.organization else None,
            'name_en': self.english_name,  # 템플릿: employee.name_en
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
            'rrn': self.resident_number,  # 템플릿: employee.rrn
            'nationality': self.nationality,
            'blood_type': self.blood_type,
            'religion': self.religion,
            'hobby': self.hobby,
            'specialty': self.specialty,
            'disability_info': self.disability_info,
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
        )

    def __repr__(self):
        return f'<Employee {self.id}: {self.name}>'
