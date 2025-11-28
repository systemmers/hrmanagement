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
    asset_type = db.Column(db.String(50), nullable=True)
    asset_name = db.Column(db.String(200), nullable=True)
    asset_code = db.Column(db.String(50), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    assignment_date = db.Column(db.String(20), nullable=True)
    return_date = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'assetType': self.asset_type,
            'assetName': self.asset_name,
            'assetCode': self.asset_code,
            'serialNumber': self.serial_number,
            'assignmentDate': self.assignment_date,
            'returnDate': self.return_date,
            'status': self.status,
            'condition': self.condition,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            asset_type=data.get('assetType'),
            asset_name=data.get('assetName'),
            asset_code=data.get('assetCode'),
            serial_number=data.get('serialNumber'),
            assignment_date=data.get('assignmentDate'),
            return_date=data.get('returnDate'),
            status=data.get('status'),
            condition=data.get('condition'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Asset {self.id}: {self.asset_name}>'
