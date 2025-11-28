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
    base_salary = db.Column(db.Integer, default=0)
    position_allowance = db.Column(db.Integer, default=0)
    meal_allowance = db.Column(db.Integer, default=0)
    transport_allowance = db.Column(db.Integer, default=0)
    overtime_allowance = db.Column(db.Integer, default=0)
    bonus = db.Column(db.Integer, default=0)
    national_pension = db.Column(db.Integer, default=0)
    health_insurance = db.Column(db.Integer, default=0)
    employment_insurance = db.Column(db.Integer, default=0)
    income_tax = db.Column(db.Integer, default=0)
    local_income_tax = db.Column(db.Integer, default=0)
    bank_name = db.Column(db.String(100), nullable=True)
    account_number = db.Column(db.String(100), nullable=True)
    account_holder = db.Column(db.String(100), nullable=True)
    effective_date = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'baseSalary': self.base_salary,
            'positionAllowance': self.position_allowance,
            'mealAllowance': self.meal_allowance,
            'transportAllowance': self.transport_allowance,
            'overtimeAllowance': self.overtime_allowance,
            'bonus': self.bonus,
            'nationalPension': self.national_pension,
            'healthInsurance': self.health_insurance,
            'employmentInsurance': self.employment_insurance,
            'incomeTax': self.income_tax,
            'localIncomeTax': self.local_income_tax,
            'bankName': self.bank_name,
            'accountNumber': self.account_number,
            'accountHolder': self.account_holder,
            'effectiveDate': self.effective_date,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            base_salary=data.get('baseSalary', 0),
            position_allowance=data.get('positionAllowance', 0),
            meal_allowance=data.get('mealAllowance', 0),
            transport_allowance=data.get('transportAllowance', 0),
            overtime_allowance=data.get('overtimeAllowance', 0),
            bonus=data.get('bonus', 0),
            national_pension=data.get('nationalPension', 0),
            health_insurance=data.get('healthInsurance', 0),
            employment_insurance=data.get('employmentInsurance', 0),
            income_tax=data.get('incomeTax', 0),
            local_income_tax=data.get('localIncomeTax', 0),
            bank_name=data.get('bankName'),
            account_number=data.get('accountNumber'),
            account_holder=data.get('accountHolder'),
            effective_date=data.get('effectiveDate'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Salary {self.id}: {self.employee_id}>'
