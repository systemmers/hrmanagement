"""
조직유형 설정 모델

회사별로 조직유형(본부, 부, 팀 등)을 커스터마이징할 수 있도록 합니다.
기본 7단계 조직유형을 제공하며, 라벨 수정 및 활성화/비활성화가 가능합니다.

Phase 4: 조직유형 설정 기능
"""
from datetime import datetime
from app.database import db


class OrganizationTypeConfig(db.Model):
    """조직유형 설정 (회사별 커스터마이징)"""
    __tablename__ = 'organization_type_configs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    type_code = db.Column(db.String(50), nullable=False)
    type_label_ko = db.Column(db.String(50), nullable=False)  # 한글명
    type_label_en = db.Column(db.String(50), nullable=True)   # 영문명
    level = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(50), default='fa-folder')
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 기본 7단계 (한글명, 영문명 포함)
    DEFAULT_TYPES = [
        {'code': 'headquarters', 'label_ko': '본부', 'label_en': 'Headquarters', 'level': 1, 'icon': 'fa-building'},
        {'code': 'division', 'label_ko': '부', 'label_en': 'Division', 'level': 2, 'icon': 'fa-layer-group'},
        {'code': 'team', 'label_ko': '팀', 'label_en': 'Team', 'level': 3, 'icon': 'fa-users'},
        {'code': 'section', 'label_ko': '소', 'label_en': 'Section', 'level': 4, 'icon': 'fa-user-friends'},
        {'code': 'department', 'label_ko': '과', 'label_en': 'Department', 'level': 5, 'icon': 'fa-sitemap'},
        {'code': 'office', 'label_ko': '실', 'label_en': 'Office', 'level': 6, 'icon': 'fa-door-open'},
        {'code': 'part', 'label_ko': '파트', 'label_en': 'Part', 'level': 7, 'icon': 'fa-puzzle-piece'},
    ]

    # 기존 org_type과의 매핑 (하위 호환성)
    LEGACY_TYPE_MAPPING = {
        'company': None,  # 회사는 조직유형 설정 대상 아님
        'division': 'headquarters',  # 기존 division -> 본부
        'department': 'team',  # 기존 department -> 팀
        'team': 'section',  # 기존 team -> 소
        'unit': 'part',  # 기존 unit -> 파트
    }

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('company_id', 'type_code', name='uq_company_type_code'),
    )

    # Relationship
    company = db.relationship('Company', backref=db.backref('organization_type_configs', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'type_code': self.type_code,
            'type_label_ko': self.type_label_ko,
            'type_label_en': self.type_label_en,
            'type_label': self.type_label_ko,  # 하위 호환성
            'level': self.level,
            'icon': self.icon,
            'sort_order': self.sort_order,
        }

    @classmethod
    def create_defaults_for_company(cls, company_id: int):
        """회사에 기본 조직유형 생성"""
        configs = []
        for idx, type_def in enumerate(cls.DEFAULT_TYPES):
            config = cls(
                company_id=company_id,
                type_code=type_def['code'],
                type_label_ko=type_def['label_ko'],
                type_label_en=type_def['label_en'],
                level=type_def['level'],
                icon=type_def['icon'],
                sort_order=idx
            )
            configs.append(config)
        return configs

    def __repr__(self):
        return f'<OrganizationTypeConfig {self.type_code}: {self.type_label_ko}>'
