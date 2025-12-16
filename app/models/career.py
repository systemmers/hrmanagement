"""
Career SQLAlchemy 모델

직원 경력 정보를 관리합니다.
"""
from app.database import db


class Career(db.Model):
    """경력 모델"""
    __tablename__ = 'careers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
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

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'company_name': self.company_name,
            'company': self.company_name,  # 템플릿: career.company
            'department': self.department,
            # 직급 체계
            'position': self.position,  # 직위
            'job_grade': self.job_grade,  # 직급
            'job_title': self.job_title,  # 직책
            'job_role': self.job_role,  # 직무
            'job_description': self.job_description,
            'duty': self.job_description,  # 템플릿: career.duty
            'start_date': self.start_date,
            'end_date': self.end_date,
            # 급여 체계
            'salary': self.salary,  # 연봉
            'salary_type': self.salary_type,  # 급여유형
            'monthly_salary': self.monthly_salary,  # 월급
            'pay_step': self.pay_step,  # 호봉
            'resignation_reason': self.resignation_reason,
            'is_current': self.is_current,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            company_name=data.get('companyName'),
            department=data.get('department'),
            # 직급 체계
            position=data.get('position'),  # 직위
            job_grade=data.get('jobGrade'),  # 직급
            job_title=data.get('jobTitle'),  # 직책
            job_role=data.get('jobRole'),  # 직무
            job_description=data.get('jobDescription'),
            start_date=data.get('startDate'),
            end_date=data.get('endDate'),
            # 급여 체계
            salary=data.get('salary'),  # 연봉
            salary_type=data.get('salaryType'),  # 급여유형
            monthly_salary=data.get('monthlySalary'),  # 월급
            pay_step=data.get('payStep'),  # 호봉
            resignation_reason=data.get('resignationReason'),
            is_current=data.get('isCurrent', False),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Career {self.id}: {self.company_name}>'
