"""
Salary SQLAlchemy 모델

직원 급여 정보를 관리합니다. (1:1 관계)
"""
from app.database import db


class Salary(db.Model):
    """급여 모델 (1:1)"""
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    salary_type = db.Column(db.String(50), nullable=True)
    base_salary = db.Column(db.Integer, default=0)
    position_allowance = db.Column(db.Integer, default=0)
    meal_allowance = db.Column(db.Integer, default=0)
    transportation_allowance = db.Column(db.Integer, default=0)
    total_salary = db.Column(db.Integer, default=0)
    payment_day = db.Column(db.Integer, default=25)
    payment_method = db.Column(db.String(50), nullable=True)
    bank_account = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'salary_type': self.salary_type,
            'base_salary': self.base_salary,
            'position_allowance': self.position_allowance,
            'meal_allowance': self.meal_allowance,
            'transportation_allowance': self.transportation_allowance,
            'total_salary': self.total_salary,
            'payment_day': self.payment_day,
            'payment_method': self.payment_method,
            'bank_account': self.bank_account,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성 (snake_case 지원)"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            salary_type=data.get('salary_type') or data.get('salaryType'),
            base_salary=data.get('base_salary') or data.get('baseSalary', 0),
            position_allowance=data.get('position_allowance') or data.get('positionAllowance', 0),
            meal_allowance=data.get('meal_allowance') or data.get('mealAllowance', 0),
            transportation_allowance=data.get('transportation_allowance') or data.get('transportationAllowance', 0),
            total_salary=data.get('total_salary') or data.get('totalSalary', 0),
            payment_day=data.get('payment_day') or data.get('paymentDay', 25),
            payment_method=data.get('payment_method') or data.get('paymentMethod'),
            bank_account=data.get('bank_account') or data.get('bankAccount'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Salary {self.id}: {self.employee_id}>'
