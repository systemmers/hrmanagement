"""
PersonalCareer SQLAlchemy 모델

개인 경력 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalCareer(db.Model):
    """개인 경력 정보"""
    __tablename__ = 'personal_careers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    company_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    responsibilities = db.Column(db.Text, nullable=True)
    achievements = db.Column(db.Text, nullable=True)
    reason_for_leaving = db.Column(db.String(500), nullable=True)
    job_grade = db.Column(db.String(50), nullable=True)
    job_role = db.Column(db.String(100), nullable=True)
    salary_type = db.Column(db.String(50), nullable=True)  # 연봉제, 월급제, 시급제, 호봉제
    salary = db.Column(db.Integer, nullable=True)  # 연봉
    monthly_salary = db.Column(db.Integer, nullable=True)  # 월급
    pay_step = db.Column(db.Integer, nullable=True)  # 호봉

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company': self.company_name,  # 템플릿 호환 필드
            'department': self.department,
            'position': self.position,
            'job_title': self.job_title,
            'job_grade': self.job_grade,
            'job_role': self.job_role,
            'duty': self.responsibilities,  # 템플릿 호환 필드
            'job_description': self.responsibilities,  # 템플릿 호환 필드
            'salary_type': self.salary_type,
            'salary': self.salary,
            'monthly_salary': self.monthly_salary,
            'pay_step': self.pay_step,
            'start_date': self.start_date,
            'end_date': self.end_date if self.end_date else ('재직중' if self.is_current else None),
            'is_current': self.is_current,
            'responsibilities': self.responsibilities,
            'achievements': self.achievements,
            'reason_for_leaving': self.reason_for_leaving,
            'resignation_reason': self.reason_for_leaving,  # Employee 호환 alias
            'note': self.responsibilities,  # Employee 호환 alias (note 필드 없음, responsibilities로 대체)
            'notes': self.responsibilities,  # Employee 호환 alias
        }

    def __repr__(self):
        return f'<PersonalCareer {self.id}: {self.company_name}>'
