"""
CompanyVisibilitySettings SQLAlchemy 모델

법인별 정보 노출 설정을 관리합니다.
급여, 평가, 조직도, 연락처 등의 공개 범위를 설정합니다.

Phase 2 Migration: app/domains/company/models/로 이동
"""
from datetime import datetime
from app.database import db


class CompanyVisibilitySettings(db.Model):
    """법인 노출 설정 모델"""
    __tablename__ = 'company_visibility_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True)
    salary_visibility = db.Column(db.String(20), nullable=False, default='self_only')
    evaluation_visibility = db.Column(db.String(20), nullable=False, default='self_only')
    org_chart_visibility = db.Column(db.String(20), nullable=False, default='all')
    contact_visibility = db.Column(db.String(20), nullable=False, default='team')
    document_visibility = db.Column(db.String(20), nullable=False, default='all')
    show_salary_to_managers = db.Column(db.Boolean, nullable=False, default=False)
    show_evaluation_to_managers = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = db.relationship('Company', backref=db.backref('visibility_settings', uselist=False))

    __table_args__ = (
        db.UniqueConstraint('company_id', name='uq_company_visibility'),
    )

    # Visibility constants
    VIS_SELF_ONLY = 'self_only'
    VIS_TEAM = 'team'
    VIS_DEPARTMENT = 'department'
    VIS_ALL = 'all'
    VIS_MANAGERS_ONLY = 'managers_only'
    VIS_EMPLOYEES_ONLY = 'employees_only'
    VIS_HIDDEN = 'hidden'

    VALID_VISIBILITIES = [VIS_SELF_ONLY, VIS_TEAM, VIS_DEPARTMENT, VIS_ALL,
                          VIS_MANAGERS_ONLY, VIS_EMPLOYEES_ONLY, VIS_HIDDEN]

    VISIBILITY_LABELS = {
        VIS_SELF_ONLY: '본인만',
        VIS_TEAM: '같은 팀',
        VIS_DEPARTMENT: '같은 부서',
        VIS_ALL: '전체',
        VIS_MANAGERS_ONLY: '관리자만',
        VIS_EMPLOYEES_ONLY: '직원만',
        VIS_HIDDEN: '비공개',
    }

    # Default settings
    DEFAULTS = {
        'salary_visibility': VIS_SELF_ONLY,
        'evaluation_visibility': VIS_SELF_ONLY,
        'org_chart_visibility': VIS_ALL,
        'contact_visibility': VIS_TEAM,
        'document_visibility': VIS_ALL,
        'show_salary_to_managers': False,
        'show_evaluation_to_managers': True,
    }

    def can_view_salary(self, viewer_employee, target_employee):
        """급여 정보 조회 권한 확인"""
        # 본인
        if viewer_employee.id == target_employee.id:
            return True

        # 관리자 권한 (show_salary_to_managers 설정 시)
        if self.show_salary_to_managers and viewer_employee.is_manager():
            return True

        return self._check_visibility(self.salary_visibility, viewer_employee, target_employee)

    def can_view_evaluation(self, viewer_employee, target_employee):
        """평가 정보 조회 권한 확인"""
        # 본인
        if viewer_employee.id == target_employee.id:
            return True

        # 관리자 권한
        if self.show_evaluation_to_managers and viewer_employee.is_manager():
            return True

        return self._check_visibility(self.evaluation_visibility, viewer_employee, target_employee)

    def can_view_contact(self, viewer_employee, target_employee):
        """연락처 조회 권한 확인"""
        # 본인
        if viewer_employee.id == target_employee.id:
            return True

        return self._check_visibility(self.contact_visibility, viewer_employee, target_employee)

    def _check_visibility(self, visibility_level, viewer, target):
        """공통 visibility 레벨 확인"""
        if visibility_level == self.VIS_ALL:
            return True
        elif visibility_level == self.VIS_SELF_ONLY:
            return False
        elif visibility_level == self.VIS_TEAM:
            return viewer.team == target.team if viewer.team else False
        elif visibility_level == self.VIS_DEPARTMENT:
            return viewer.department == target.department if viewer.department else False
        elif visibility_level == self.VIS_HIDDEN:
            return False
        return False

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'companyId': self.company_id,
            'salaryVisibility': self.salary_visibility,
            'salaryVisibilityLabel': self.VISIBILITY_LABELS.get(self.salary_visibility, self.salary_visibility),
            'evaluationVisibility': self.evaluation_visibility,
            'evaluationVisibilityLabel': self.VISIBILITY_LABELS.get(self.evaluation_visibility, self.evaluation_visibility),
            'orgChartVisibility': self.org_chart_visibility,
            'orgChartVisibilityLabel': self.VISIBILITY_LABELS.get(self.org_chart_visibility, self.org_chart_visibility),
            'contactVisibility': self.contact_visibility,
            'contactVisibilityLabel': self.VISIBILITY_LABELS.get(self.contact_visibility, self.contact_visibility),
            'documentVisibility': self.document_visibility,
            'documentVisibilityLabel': self.VISIBILITY_LABELS.get(self.document_visibility, self.document_visibility),
            'showSalaryToManagers': self.show_salary_to_managers,
            'showEvaluationToManagers': self.show_evaluation_to_managers,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            company_id=data.get('companyId'),
            salary_visibility=data.get('salaryVisibility', cls.DEFAULTS['salary_visibility']),
            evaluation_visibility=data.get('evaluationVisibility', cls.DEFAULTS['evaluation_visibility']),
            org_chart_visibility=data.get('orgChartVisibility', cls.DEFAULTS['org_chart_visibility']),
            contact_visibility=data.get('contactVisibility', cls.DEFAULTS['contact_visibility']),
            document_visibility=data.get('documentVisibility', cls.DEFAULTS['document_visibility']),
            show_salary_to_managers=data.get('showSalaryToManagers', cls.DEFAULTS['show_salary_to_managers']),
            show_evaluation_to_managers=data.get('showEvaluationToManagers', cls.DEFAULTS['show_evaluation_to_managers']),
        )

    @classmethod
    def get_visibility_label(cls, visibility):
        """visibility 한글명 반환"""
        return cls.VISIBILITY_LABELS.get(visibility, visibility)

    @classmethod
    def get_default_settings(cls, company_id):
        """기본 설정으로 새 인스턴스 생성"""
        return cls(
            company_id=company_id,
            **cls.DEFAULTS
        )

    def __repr__(self):
        return f'<CompanyVisibilitySettings company_id={self.company_id}>'
