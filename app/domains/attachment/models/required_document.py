"""
RequiredDocument SQLAlchemy 모델

법인별 필수 서류 목록을 관리합니다.
Phase 4.1: 필수 서류 설정 기능 추가
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class RequiredDocument(DictSerializableMixin, db.Model):
    """필수 서류 모델 (법인별 설정)"""
    __tablename__ = 'required_documents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 법인 참조
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False,
        index=True,
        comment='법인 ID'
    )

    # 서류 정보
    name = db.Column(
        db.String(100),
        nullable=False,
        comment='서류명 (예: 주민등록등본, 졸업증명서)'
    )
    category = db.Column(
        db.String(50),
        nullable=True,
        index=True,
        comment='서류 분류 (예: 신분증명, 학력증명, 경력증명)'
    )
    description = db.Column(
        db.Text,
        nullable=True,
        comment='서류 설명 또는 안내'
    )

    # 필수 여부 및 순서
    is_required = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment='필수 제출 여부'
    )
    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment='표시 순서'
    )

    # 연결 대상 엔티티 (옵션)
    # 특정 항목(학력, 경력 등)에 연결된 증빙 서류인 경우
    linked_entity_type = db.Column(
        db.String(50),
        nullable=True,
        index=True,
        comment='연결 엔티티 타입 (education, career, certificate 등)'
    )

    # 활성화 여부
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment='활성화 여부 (비활성화 시 목록에서 숨김)'
    )

    # 생성/수정 일시
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        comment='생성 일시'
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        comment='수정 일시'
    )

    # 관계
    company = db.relationship(
        'Company',
        backref=db.backref('required_documents', lazy='dynamic')
    )

    def __repr__(self):
        return f'<RequiredDocument {self.id}: {self.name} (company_id={self.company_id})>'

    @classmethod
    def get_by_company(cls, company_id: int, active_only: bool = True):
        """법인별 필수 서류 목록 조회"""
        query = cls.query.filter_by(company_id=company_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.display_order).all()

    @classmethod
    def get_required_by_company(cls, company_id: int):
        """법인별 필수 서류만 조회"""
        return cls.query.filter_by(
            company_id=company_id,
            is_required=True,
            is_active=True
        ).order_by(cls.display_order).all()

    @classmethod
    def get_by_category(cls, company_id: int, category: str):
        """카테고리별 필수 서류 조회"""
        return cls.query.filter_by(
            company_id=company_id,
            category=category,
            is_active=True
        ).order_by(cls.display_order).all()

    @classmethod
    def get_by_linked_entity(cls, company_id: int, entity_type: str):
        """연결 엔티티별 필수 서류 조회"""
        return cls.query.filter_by(
            company_id=company_id,
            linked_entity_type=entity_type,
            is_active=True
        ).order_by(cls.display_order).all()
