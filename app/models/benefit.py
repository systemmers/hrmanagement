"""
Benefit SQLAlchemy 모델

직원 복리후생 정보를 관리합니다. (1:1 관계)
"""
from app.database import db


class Benefit(db.Model):
    """복리후생 모델 (1:1)"""
    __tablename__ = 'benefits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    annual_leave = db.Column(db.Integer, default=0)
    used_leave = db.Column(db.Integer, default=0)
    remaining_leave = db.Column(db.Integer, default=0)
    sick_leave = db.Column(db.Integer, default=0)
    special_leave = db.Column(db.Integer, default=0)
    health_checkup = db.Column(db.Boolean, default=False)
    group_insurance = db.Column(db.Boolean, default=False)
    meal_support = db.Column(db.Boolean, default=False)
    housing_support = db.Column(db.Boolean, default=False)
    education_support = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'annualLeave': self.annual_leave,
            'usedLeave': self.used_leave,
            'remainingLeave': self.remaining_leave,
            'sickLeave': self.sick_leave,
            'specialLeave': self.special_leave,
            'healthCheckup': self.health_checkup,
            'groupInsurance': self.group_insurance,
            'mealSupport': self.meal_support,
            'housingSupport': self.housing_support,
            'educationSupport': self.education_support,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            annual_leave=data.get('annualLeave', 0),
            used_leave=data.get('usedLeave', 0),
            remaining_leave=data.get('remainingLeave', 0),
            sick_leave=data.get('sickLeave', 0),
            special_leave=data.get('specialLeave', 0),
            health_checkup=data.get('healthCheckup', False),
            group_insurance=data.get('groupInsurance', False),
            meal_support=data.get('mealSupport', False),
            housing_support=data.get('housingSupport', False),
            education_support=data.get('educationSupport', False),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Benefit {self.id}: {self.employee_id}>'
