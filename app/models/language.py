"""
Language SQLAlchemy 모델

직원 어학 능력 정보를 관리합니다.
"""
from app.database import db


class Language(db.Model):
    """어학 모델"""
    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    language_name = db.Column(db.String(100), nullable=True)
    exam_name = db.Column(db.String(100), nullable=True)
    score = db.Column(db.String(50), nullable=True)
    level = db.Column(db.String(50), nullable=True)
    acquisition_date = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'language_name': self.language_name,
            'exam_name': self.exam_name,
            'score': self.score,
            'level': self.level,
            'acquisition_date': self.acquisition_date,
            'expiry_date': self.expiry_date,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            language_name=data.get('languageName'),
            exam_name=data.get('examName'),
            score=data.get('score'),
            level=data.get('level'),
            acquisition_date=data.get('acquisitionDate'),
            expiry_date=data.get('expiryDate'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Language {self.id}: {self.language_name}>'
