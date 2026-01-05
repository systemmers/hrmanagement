"""
Attachment SQLAlchemy 모델

직원 첨부파일 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Attachment(DictSerializableMixin, db.Model):
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

    def __repr__(self):
        return f'<Attachment {self.id}: {self.file_name}>'
