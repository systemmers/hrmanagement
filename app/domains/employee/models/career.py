"""
Career SQLAlchemy 모델

직원 경력 정보를 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from .mixins import DictSerializableMixin


class Career(DictSerializableMixin, db.Model):
    """경력 모델"""
    __tablename__ = 'careers'

    # ====================================
    # Mixin 설정
    # ====================================

    __dict_aliases__ = {
        'company': 'company_name',             # 템플릿: career.company
        'duty': 'job_description',             # 템플릿: career.duty
        'reason_for_leaving': 'resignation_reason',  # Personal 호환
        'notes': 'note',                       # Personal 호환
        'responsibilities': 'job_description', # Personal 호환
    }

    __dict_computed__ = {
        'achievements': lambda self: None,     # Personal 호환 필드
    }


    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
    company_name = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(100), nullable=True)

    # 직급 체계
    position = db.Column(db.String(100), nullable=True)  # 직위 (서열: 사원, 대리, 과장, 부장)
    job_grade = db.Column(db.String(50), nullable=True)  # 직급 (역량 레벨: L3, 2호봉, Senior)
    job_title = db.Column(db.String(100), nullable=True)  # 직책 (책임자 역할: 팀장, 본부장, CFO)
    job_role = db.Column(db.String(100), nullable=True)  # 직무 (수행 업무: 인사기획, 회계관리)
    job_description = db.Column(db.Text, nullable=True)  # 담당업무 상세

    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)

    # 급여 체계
    salary = db.Column(db.Integer, nullable=True)  # 연봉 (원)
    salary_type = db.Column(db.String(20), nullable=True)  # 급여유형 (연봉제/월급제/시급제/호봉제)
    monthly_salary = db.Column(db.Integer, nullable=True)  # 월급 (원)
    pay_step = db.Column(db.Integer, nullable=True)  # 호봉 (급여 단계 1~50)

    resignation_reason = db.Column(db.String(500), nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Career {self.id}: {self.company_name}>'
