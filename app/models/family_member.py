"""
FamilyMember SQLAlchemy 모델

직원 가족 정보를 관리합니다.
"""
from app.database import db


class FamilyMember(db.Model):
    """가족 모델"""
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    relation = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    is_cohabitant = db.Column(db.Boolean, default=False)
    is_dependent = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'relation': self.relation,
            'name': self.name,
            'birthDate': self.birth_date,
            'occupation': self.occupation,
            'contact': self.contact,
            'isCohabitant': self.is_cohabitant,
            'isDependent': self.is_dependent,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            relation=data.get('relation'),
            name=data.get('name'),
            birth_date=data.get('birthDate'),
            occupation=data.get('occupation'),
            contact=data.get('contact'),
            is_cohabitant=data.get('isCohabitant', False),
            is_dependent=data.get('isDependent', False),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<FamilyMember {self.id}: {self.name}>'
