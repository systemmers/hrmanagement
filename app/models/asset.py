"""
Asset SQLAlchemy 모델

직원 자산 배정 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Asset(DictSerializableMixin, db.Model):
    """자산 배정 모델"""
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    issue_date = db.Column(db.String(20), nullable=True)
    item_name = db.Column(db.String(200), nullable=True)
    model = db.Column(db.String(200), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Asset {self.id}: {self.item_name}>'
