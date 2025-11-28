"""
Attachment SQLAlchemy 모델

직원 첨부파일 정보를 관리합니다.
"""
from app.database import db


class Attachment(db.Model):
    """첨부파일 모델"""
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    file_name = db.Column(db.String(500), nullable=True)
    file_path = db.Column(db.String(1000), nullable=True)
    file_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), nullable=True)
    upload_date = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'category': self.category,
            'upload_date': self.upload_date,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            file_name=data.get('file_name') or data.get('fileName'),
            file_path=data.get('file_path') or data.get('filePath'),
            file_type=data.get('file_type') or data.get('fileType'),
            file_size=data.get('file_size') or data.get('fileSize', 0),
            category=data.get('category'),
            upload_date=data.get('upload_date') or data.get('uploadDate'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Attachment {self.id}: {self.file_name}>'
