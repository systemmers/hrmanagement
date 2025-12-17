"""
ClassificationOption SQLAlchemy 모델

분류 옵션 (부서, 직급, 재직상태 등) 정보를 관리합니다.
법인별 커스텀 옵션을 지원합니다.
"""
from datetime import datetime
from app.database import db


class ClassificationOption(db.Model):
    """분류 옵션 모델"""
    __tablename__ = 'classification_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    value = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    # 법인별 커스텀 옵션 지원
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_system = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    company = db.relationship('Company', backref=db.backref('classification_options', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('category', 'value', name='uq_category_value'),
        db.Index('idx_classification_company_category', 'company_id', 'category'),
    )

    # Category constants
    CATEGORY_DEPARTMENT = 'department'
    CATEGORY_POSITION = 'position'
    CATEGORY_RANK = 'rank'
    CATEGORY_JOB_TITLE = 'job_title'
    CATEGORY_TEAM = 'team'
    CATEGORY_WORK_LOCATION = 'work_location'
    CATEGORY_JOB_ROLE = 'job_role'
    CATEGORY_JOB_GRADE = 'job_grade'
    CATEGORY_EMPLOYMENT_TYPE = 'employment_type'
    CATEGORY_STATUS = 'status'
    CATEGORY_PAY_TYPE = 'pay_type'
    CATEGORY_CONTRACT_TYPE = 'contract_type'
    CATEGORY_BANK = 'bank'
    CATEGORY_ASSET_TYPE = 'asset_type'
    CATEGORY_LANGUAGE = 'language'
    CATEGORY_LANGUAGE_LEVEL = 'language_level'
    CATEGORY_FAMILY_RELATION = 'family_relation'
    CATEGORY_ORG_UNIT = 'org_unit'

    VALID_CATEGORIES = [
        CATEGORY_DEPARTMENT, CATEGORY_POSITION, CATEGORY_RANK,
        CATEGORY_JOB_TITLE, CATEGORY_TEAM, CATEGORY_WORK_LOCATION,
        CATEGORY_JOB_ROLE, CATEGORY_JOB_GRADE, CATEGORY_ORG_UNIT,
        CATEGORY_EMPLOYMENT_TYPE, CATEGORY_STATUS, CATEGORY_PAY_TYPE,
        CATEGORY_CONTRACT_TYPE, CATEGORY_BANK, CATEGORY_ASSET_TYPE,
        CATEGORY_LANGUAGE, CATEGORY_LANGUAGE_LEVEL, CATEGORY_FAMILY_RELATION
    ]

    CATEGORY_LABELS = {
        CATEGORY_DEPARTMENT: '부서',
        CATEGORY_POSITION: '직급',
        CATEGORY_RANK: '직위',
        CATEGORY_JOB_TITLE: '직책',
        CATEGORY_TEAM: '팀',
        CATEGORY_WORK_LOCATION: '근무지',
        CATEGORY_JOB_ROLE: '직무',
        CATEGORY_JOB_GRADE: '호봉',
        CATEGORY_EMPLOYMENT_TYPE: '고용형태',
        CATEGORY_STATUS: '재직상태',
        CATEGORY_PAY_TYPE: '급여방식',
        CATEGORY_CONTRACT_TYPE: '계약유형',
        CATEGORY_BANK: '은행',
        CATEGORY_ASSET_TYPE: '자산유형',
        CATEGORY_LANGUAGE: '언어',
        CATEGORY_LANGUAGE_LEVEL: '언어수준',
        CATEGORY_FAMILY_RELATION: '가족관계',
        CATEGORY_ORG_UNIT: '조직단위',
    }

    # 탭 구분
    TAB_ORGANIZATION = [CATEGORY_DEPARTMENT, CATEGORY_POSITION, CATEGORY_RANK,
                        CATEGORY_JOB_TITLE, CATEGORY_TEAM, CATEGORY_WORK_LOCATION,
                        CATEGORY_JOB_ROLE, CATEGORY_JOB_GRADE, CATEGORY_ORG_UNIT]
    TAB_EMPLOYMENT = [CATEGORY_EMPLOYMENT_TYPE, CATEGORY_STATUS, CATEGORY_PAY_TYPE,
                      CATEGORY_CONTRACT_TYPE, CATEGORY_LANGUAGE, CATEGORY_LANGUAGE_LEVEL,
                      CATEGORY_FAMILY_RELATION]
    TAB_BASIC = [CATEGORY_BANK, CATEGORY_ASSET_TYPE]

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'category': self.category,
            'categoryLabel': self.CATEGORY_LABELS.get(self.category, self.category),
            'value': self.value,
            'label': self.label,
            'sortOrder': self.sort_order,
            'companyId': self.company_id,
            'isActive': self.is_active,
            'isSystem': self.is_system,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            category=data.get('category'),
            value=data.get('value'),
            label=data.get('label'),
            sort_order=data.get('sortOrder', 0),
            company_id=data.get('companyId'),
            is_active=data.get('isActive', True),
            is_system=data.get('isSystem', False),
        )

    @classmethod
    def get_category_label(cls, category):
        """카테고리 한글명 반환"""
        return cls.CATEGORY_LABELS.get(category, category)

    def __repr__(self):
        return f'<ClassificationOption {self.category}: {self.value}>'
