"""
Employee SQLAlchemy 모델

직원 기본 정보 및 확장 정보를 포함합니다.
"""
from app.database import db


class Employee(db.Model):
    """직원 모델"""
    __tablename__ = 'employees'

    # 기본 정보 (9개 필드)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(500), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    hire_date = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(200), nullable=True)

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
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'department': self.department,
            'position': self.position,
            'status': self.status,
            'hireDate': self.hire_date,
            'phone': self.phone,
            'email': self.email,
            'englishName': self.english_name,
            'chineseName': self.chinese_name,
            'birthDate': self.birth_date,
            'lunarBirth': self.lunar_birth,
            'gender': self.gender,
            'mobilePhone': self.mobile_phone,
            'homePhone': self.home_phone,
            'address': self.address,
            'detailedAddress': self.detailed_address,
            'postalCode': self.postal_code,
            'residentNumber': self.resident_number,
            'nationality': self.nationality,
            'bloodType': self.blood_type,
            'religion': self.religion,
            'hobby': self.hobby,
            'specialty': self.specialty,
            'disabilityInfo': self.disability_info,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            photo=data.get('photo'),
            department=data.get('department'),
            position=data.get('position'),
            status=data.get('status'),
            hire_date=data.get('hireDate'),
            phone=data.get('phone'),
            email=data.get('email'),
            english_name=data.get('englishName'),
            chinese_name=data.get('chineseName'),
            birth_date=data.get('birthDate'),
            lunar_birth=data.get('lunarBirth', False),
            gender=data.get('gender'),
            mobile_phone=data.get('mobilePhone'),
            home_phone=data.get('homePhone'),
            address=data.get('address'),
            detailed_address=data.get('detailedAddress'),
            postal_code=data.get('postalCode'),
            resident_number=data.get('residentNumber'),
            nationality=data.get('nationality'),
            blood_type=data.get('bloodType'),
            religion=data.get('religion'),
            hobby=data.get('hobby'),
            specialty=data.get('specialty'),
            disability_info=data.get('disabilityInfo'),
        )

    def __repr__(self):
        return f'<Employee {self.id}: {self.name}>'
