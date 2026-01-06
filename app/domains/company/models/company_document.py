"""
CompanyDocument SQLAlchemy 모델

법인 서류를 관리합니다.
근로계약서, 취업규칙, 급여규정 등 법인 문서를 저장합니다.

Phase 2 Migration: app/domains/company/models/로 이동
"""
from datetime import datetime
from app.database import db


class CompanyDocument(db.Model):
    """법인 서류 모델"""
    __tablename__ = 'company_documents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # required, payroll, welfare, security, other
    document_type = db.Column(db.String(100), nullable=False)  # 서류 유형 코드
    title = db.Column(db.String(200), nullable=False)  # 서류 제목
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)  # 파일 경로
    file_name = db.Column(db.String(200), nullable=True)  # 원본 파일명
    file_size = db.Column(db.Integer, nullable=True)  # 파일 크기
    file_type = db.Column(db.String(50), nullable=True)  # 파일 확장자
    version = db.Column(db.String(20), nullable=True)  # 버전
    is_required = db.Column(db.Boolean, nullable=False, default=False)  # 필수 서명 여부
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    visibility = db.Column(db.String(20), nullable=False, default='all')  # all, admin, manager
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)

    # AI 자동 세팅 관련 필드
    is_electronic = db.Column(db.Boolean, nullable=False, default=True)
    ai_processed = db.Column(db.Boolean, nullable=False, default=False)
    ai_detected_type = db.Column(db.String(100), nullable=True)
    ai_extracted_data = db.Column(db.JSON, nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)
    original_file_path = db.Column(db.String(500), nullable=True)

    # Relationships
    company = db.relationship('Company', backref=db.backref('documents', lazy='dynamic'))
    uploader = db.relationship('User', backref=db.backref('uploaded_documents', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_company_documents', 'company_id', 'category'),
    )

    # Category constants
    CAT_REQUIRED = 'required'
    CAT_PAYROLL = 'payroll'
    CAT_WELFARE = 'welfare'
    CAT_SECURITY = 'security'
    CAT_OTHER = 'other'

    VALID_CATEGORIES = [CAT_REQUIRED, CAT_PAYROLL, CAT_WELFARE, CAT_SECURITY, CAT_OTHER]

    CATEGORY_LABELS = {
        CAT_REQUIRED: '필수 서류',
        CAT_PAYROLL: '급여 관련',
        CAT_WELFARE: '복리후생',
        CAT_SECURITY: '보안/기타',
        CAT_OTHER: '기타',
    }

    # Document type constants
    DOC_EMPLOYMENT_CONTRACT = 'employment_contract'
    DOC_WORK_RULES = 'work_rules'
    DOC_PRIVACY_CONSENT = 'privacy_consent'
    DOC_CONFIDENTIALITY = 'confidentiality_agreement'
    DOC_IP_ASSIGNMENT = 'ip_assignment'
    DOC_SALARY_TABLE = 'salary_table'
    DOC_BONUS_POLICY = 'bonus_policy'
    DOC_ALLOWANCE_POLICY = 'allowance_policy'
    DOC_PAYROLL_SCHEDULE = 'payroll_schedule'
    DOC_WELFARE_POLICY = 'welfare_policy'
    DOC_LEAVE_POLICY = 'leave_policy'
    DOC_EDUCATION_SUPPORT = 'education_support'
    DOC_HEALTH_CHECKUP = 'health_checkup'
    DOC_SECURITY_POLICY = 'security_policy'
    DOC_CODE_OF_CONDUCT = 'code_of_conduct'
    DOC_HARASSMENT_POLICY = 'harassment_policy'
    DOC_EMERGENCY_MANUAL = 'emergency_manual'
    DOC_ORGANIZATION_CHART = 'organization_chart'
    DOC_COMPANY_HANDBOOK = 'company_handbook'
    DOC_IT_GUIDE = 'it_guide'
    DOC_CUSTOM = 'custom'

    DOCUMENT_TYPE_LABELS = {
        DOC_EMPLOYMENT_CONTRACT: '근로계약서',
        DOC_WORK_RULES: '취업규칙',
        DOC_PRIVACY_CONSENT: '개인정보 수집동의서',
        DOC_CONFIDENTIALITY: '비밀유지서약서',
        DOC_IP_ASSIGNMENT: '지식재산권 양도계약서',
        DOC_SALARY_TABLE: '연봉테이블',
        DOC_BONUS_POLICY: '상여금 지급규정',
        DOC_ALLOWANCE_POLICY: '수당 지급규정',
        DOC_PAYROLL_SCHEDULE: '급여지급일정표',
        DOC_WELFARE_POLICY: '복리후생규정',
        DOC_LEAVE_POLICY: '휴가규정',
        DOC_EDUCATION_SUPPORT: '교육지원정책',
        DOC_HEALTH_CHECKUP: '건강검진안내',
        DOC_SECURITY_POLICY: '정보보안규정',
        DOC_CODE_OF_CONDUCT: '윤리강령',
        DOC_HARASSMENT_POLICY: '직장내괴롭힘방지정책',
        DOC_EMERGENCY_MANUAL: '비상대응매뉴얼',
        DOC_ORGANIZATION_CHART: '조직도',
        DOC_COMPANY_HANDBOOK: '사원핸드북',
        DOC_IT_GUIDE: 'IT이용가이드',
        DOC_CUSTOM: '기타 서류',
    }

    # Category to document types mapping
    CATEGORY_DOCUMENT_TYPES = {
        CAT_REQUIRED: [DOC_EMPLOYMENT_CONTRACT, DOC_WORK_RULES, DOC_PRIVACY_CONSENT,
                       DOC_CONFIDENTIALITY, DOC_IP_ASSIGNMENT],
        CAT_PAYROLL: [DOC_SALARY_TABLE, DOC_BONUS_POLICY, DOC_ALLOWANCE_POLICY, DOC_PAYROLL_SCHEDULE],
        CAT_WELFARE: [DOC_WELFARE_POLICY, DOC_LEAVE_POLICY, DOC_EDUCATION_SUPPORT, DOC_HEALTH_CHECKUP],
        CAT_SECURITY: [DOC_SECURITY_POLICY, DOC_CODE_OF_CONDUCT, DOC_HARASSMENT_POLICY, DOC_EMERGENCY_MANUAL],
        CAT_OTHER: [DOC_ORGANIZATION_CHART, DOC_COMPANY_HANDBOOK, DOC_IT_GUIDE, DOC_CUSTOM],
    }

    # Visibility constants
    VIS_ALL = 'all'
    VIS_ADMIN = 'admin'
    VIS_MANAGER = 'manager'

    VALID_VISIBILITIES = [VIS_ALL, VIS_ADMIN, VIS_MANAGER]

    VISIBILITY_LABELS = {
        VIS_ALL: '전체',
        VIS_ADMIN: '관리자만',
        VIS_MANAGER: '관리자/매니저',
    }

    # AI confidence thresholds
    AI_CONFIDENCE_HIGH = 0.9
    AI_CONFIDENCE_MEDIUM = 0.7

    def is_expired(self):
        """만료 여부 확인"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def get_ai_confidence_level(self):
        """AI 신뢰도 레벨 반환"""
        if not self.ai_confidence:
            return None
        if self.ai_confidence >= self.AI_CONFIDENCE_HIGH:
            return 'high'
        elif self.ai_confidence >= self.AI_CONFIDENCE_MEDIUM:
            return 'medium'
        return 'low'

    def to_dict(self, include_ai=False):
        """딕셔너리 반환"""
        data = {
            'id': self.id,
            'companyId': self.company_id,
            'category': self.category,
            'categoryLabel': self.CATEGORY_LABELS.get(self.category, self.category),
            'documentType': self.document_type,
            'documentTypeLabel': self.DOCUMENT_TYPE_LABELS.get(self.document_type, self.document_type),
            'title': self.title,
            'description': self.description,
            'filePath': self.file_path,
            'fileName': self.file_name,
            'fileSize': self.file_size,
            'fileType': self.file_type,
            'version': self.version,
            'isRequired': self.is_required,
            'isActive': self.is_active,
            'visibility': self.visibility,
            'visibilityLabel': self.VISIBILITY_LABELS.get(self.visibility, self.visibility),
            'uploadedBy': self.uploaded_by,
            'uploadedAt': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'isExpired': self.is_expired(),
            'isElectronic': self.is_electronic,
        }

        if include_ai:
            data.update({
                'aiProcessed': self.ai_processed,
                'aiDetectedType': self.ai_detected_type,
                'aiExtractedData': self.ai_extracted_data,
                'aiConfidence': self.ai_confidence,
                'aiConfidenceLevel': self.get_ai_confidence_level(),
                'originalFilePath': self.original_file_path,
            })

        return data

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            company_id=data.get('companyId'),
            category=data.get('category', cls.CAT_OTHER),
            document_type=data.get('documentType', cls.DOC_CUSTOM),
            title=data.get('title'),
            description=data.get('description'),
            file_path=data.get('filePath'),
            file_name=data.get('fileName'),
            file_size=data.get('fileSize'),
            file_type=data.get('fileType'),
            version=data.get('version', 'v1.0'),
            is_required=data.get('isRequired', False),
            is_active=data.get('isActive', True),
            visibility=data.get('visibility', cls.VIS_ALL),
            uploaded_by=data.get('uploadedBy'),
            expires_at=data.get('expiresAt'),
            is_electronic=data.get('isElectronic', True),
        )

    @classmethod
    def get_category_label(cls, category):
        """카테고리 한글명 반환"""
        return cls.CATEGORY_LABELS.get(category, category)

    @classmethod
    def get_document_type_label(cls, doc_type):
        """서류 유형 한글명 반환"""
        return cls.DOCUMENT_TYPE_LABELS.get(doc_type, doc_type)

    def __repr__(self):
        return f'<CompanyDocument {self.title} ({self.document_type})>'
