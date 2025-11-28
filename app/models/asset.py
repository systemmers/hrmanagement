"""
Asset SQLAlchemy 모델

직원 자산 배정 정보를 관리합니다.
"""
from app.database import db


class Asset(db.Model):
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

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'issue_date': self.issue_date,
            'item_name': self.item_name,
            'model': self.model,
            'serial_number': self.serial_number,
            'status': self.status,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            issue_date=data.get('issue_date') or data.get('issueDate'),
            item_name=data.get('item_name') or data.get('itemName'),
            model=data.get('model'),
            serial_number=data.get('serial_number') or data.get('serialNumber'),
            status=data.get('status'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Asset {self.id}: {self.item_name}>'
