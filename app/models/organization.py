"""
Organization SQLAlchemy 모델

조직 구조(트리 구조)를 관리하는 모델입니다.
"""
from datetime import datetime
from app.database import db


class Organization(db.Model):
    """조직 모델 (트리 구조)"""
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=True)
    org_type = db.Column(db.String(50), nullable=False, default='department')
    # company, division, department, team, unit

    parent_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)

    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship for tree structure
    parent = db.relationship(
        'Organization',
        remote_side=[id],
        backref=db.backref('children', lazy='dynamic', order_by='Organization.sort_order')
    )

    # Relationship to manager (Employee)
    manager = db.relationship('Employee', backref=db.backref('managed_organizations', lazy='dynamic'))

    # Organization type constants
    TYPE_COMPANY = 'company'
    TYPE_DIVISION = 'division'
    TYPE_DEPARTMENT = 'department'
    TYPE_TEAM = 'team'
    TYPE_UNIT = 'unit'

    VALID_TYPES = [TYPE_COMPANY, TYPE_DIVISION, TYPE_DEPARTMENT, TYPE_TEAM, TYPE_UNIT]

    TYPE_LABELS = {
        TYPE_COMPANY: '회사',
        TYPE_DIVISION: '본부',
        TYPE_DEPARTMENT: '부서',
        TYPE_TEAM: '팀',
        TYPE_UNIT: '파트',
    }

    def get_type_label(self):
        """조직 유형 한글 라벨"""
        return self.TYPE_LABELS.get(self.org_type, self.org_type)

    def get_level(self):
        """조직 트리에서의 깊이 반환 (루트=0)"""
        level = 0
        current = self
        while current.parent_id:
            level += 1
            current = current.parent
            if level > 10:  # 무한 루프 방지
                break
        return level

    def get_ancestors(self):
        """상위 조직 목록 반환 (루트까지)"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
            if len(ancestors) > 10:  # 무한 루프 방지
                break
        return list(reversed(ancestors))

    def get_descendants(self):
        """하위 조직 목록 반환 (모든 자손)"""
        descendants = []

        def collect_children(org):
            for child in org.children.filter_by(is_active=True).order_by(Organization.sort_order):
                descendants.append(child)
                collect_children(child)

        collect_children(self)
        return descendants

    def get_path(self):
        """루트부터 현재 조직까지의 경로 문자열"""
        ancestors = self.get_ancestors()
        path_parts = [a.name for a in ancestors] + [self.name]
        return ' > '.join(path_parts)

    def get_full_code(self):
        """전체 코드 경로 (상위 코드 포함)"""
        ancestors = self.get_ancestors()
        codes = [a.code for a in ancestors if a.code] + [self.code] if self.code else []
        return '-'.join(codes) if codes else None

    def to_dict(self, include_children=False, include_path=False):
        """딕셔너리 변환"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'org_type': self.org_type,
            'org_type_label': self.get_type_label(),
            'parent_id': self.parent_id,
            'manager_id': self.manager_id,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'description': self.description,
            'level': self.get_level(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_path:
            data['path'] = self.get_path()
            data['full_code'] = self.get_full_code()

        if include_children:
            data['children'] = [
                child.to_dict(include_children=True)
                for child in self.children.filter_by(is_active=True).order_by(Organization.sort_order)
            ]

        # Manager info
        if self.manager:
            data['manager'] = {
                'id': self.manager.id,
                'name': self.manager.name,
                'position': self.manager.position
            }

        return data

    def to_tree_node(self):
        """트리 구조용 노드 데이터"""
        return {
            'id': self.id,
            'text': self.name,
            'type': self.org_type,
            'parent': self.parent_id if self.parent_id else '#',
            'children': self.children.filter_by(is_active=True).count() > 0,
            'data': {
                'code': self.code,
                'manager_id': self.manager_id,
            }
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            name=data.get('name'),
            code=data.get('code'),
            org_type=data.get('org_type', cls.TYPE_DEPARTMENT),
            parent_id=data.get('parent_id'),
            manager_id=data.get('manager_id'),
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True),
            description=data.get('description'),
        )

    def __repr__(self):
        return f'<Organization {self.name} ({self.org_type})>'
