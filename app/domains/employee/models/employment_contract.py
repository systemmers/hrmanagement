"""
EmploymentContract SQLAlchemy 모델

직원 근로계약 이력을 관리합니다.
Phase 14: 인라인 편집 시스템 지원
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class EmploymentContract(DictSerializableMixin, db.Model):
    """근로계약 이력 모델"""
    __tablename__ = 'employment_contracts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    contract_date = db.Column(db.Date, nullable=True)
    contract_type = db.Column(db.String(50), nullable=True)  # 정규직, 계약직, 파견직, 인턴
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    employee_type = db.Column(db.String(50), nullable=True)  # 직원구분
    work_type = db.Column(db.String(50), nullable=True)  # 전일제, 시간제, 교대제
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<EmploymentContract {self.id}: {self.employee_id}>'
