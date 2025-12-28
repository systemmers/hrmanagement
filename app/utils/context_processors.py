"""
템플릿 컨텍스트 프로세서

모든 템플릿에서 사용 가능한 전역 변수와 함수를 제공합니다.
Phase 8: 상수 모듈 적용
Phase 8.1: FieldRegistry 통합 - 템플릿 헬퍼 추가
"""
from flask import session, g

from ..constants.session_keys import SessionKeys, UserRole
from ..constants.field_registry import FieldRegistry
from ..constants.field_options import FieldOptions
from ..extensions import user_repo


def register_context_processors(app):
    """컨텍스트 프로세서 등록"""

    @app.context_processor
    def inject_current_user():
        """현재 로그인한 사용자 정보를 템플릿에 주입"""
        current_user = None
        is_authenticated = False

        user_id = session.get(SessionKeys.USER_ID)
        if user_id and user_repo:
            # 세션에서 기본 정보 가져오기 (DB 조회 최소화)
            current_user = {
                'id': user_id,
                'username': session.get(SessionKeys.USERNAME),
                'role': session.get(SessionKeys.USER_ROLE),
                'employee_id': session.get(SessionKeys.EMPLOYEE_ID),
                'is_admin': session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN,
                'is_manager': session.get(SessionKeys.USER_ROLE) == UserRole.MANAGER,
                'account_type': session.get(SessionKeys.ACCOUNT_TYPE),  # Phase 2: 계정 유형
            }
            is_authenticated = True

        return dict(
            current_user=current_user,
            is_authenticated=is_authenticated
        )

    @app.context_processor
    def inject_auth_helpers():
        """인증 관련 헬퍼 함수를 템플릿에 주입"""

        def has_role(role):
            """현재 사용자가 특정 역할을 가지고 있는지 확인"""
            return session.get(SessionKeys.USER_ROLE) == role

        def has_any_role(*roles):
            """현재 사용자가 특정 역할 중 하나를 가지고 있는지 확인"""
            return session.get(SessionKeys.USER_ROLE) in roles

        def can_edit_employee(employee_id):
            """특정 직원 정보를 수정할 수 있는지 확인"""
            if session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN:
                return True
            if session.get(SessionKeys.USER_ROLE) == UserRole.MANAGER:
                # 매니저의 부서 직원인지 확인
                manager_employee_id = session.get(SessionKeys.EMPLOYEE_ID)
                if manager_employee_id:
                    from ..models.employee import Employee
                    manager_employee = Employee.query.get(manager_employee_id)
                    target_employee = Employee.query.get(employee_id)
                    if manager_employee and target_employee:
                        return manager_employee.department == target_employee.department
                return False
            return session.get(SessionKeys.EMPLOYEE_ID) == employee_id

        return dict(
            has_role=has_role,
            has_any_role=has_any_role,
            can_edit_employee=can_edit_employee
        )

    @app.context_processor
    def inject_profile_context():
        """통합 프로필 관련 컨텍스트를 템플릿에 주입"""
        context = {
            'is_corporate': getattr(g, 'is_corporate', False),
            'profile': getattr(g, 'profile', None),
            'available_sections': [],
            'profile_name': '',
            'profile_photo': None,
        }

        profile = context['profile']
        if profile:
            try:
                context.update({
                    'available_sections': profile.get_available_sections(),
                    'profile_name': profile.get_display_name(),
                    'profile_photo': profile.get_photo_url(),
                })
            except Exception:
                pass

        return context

    @app.context_processor
    def inject_section_helpers():
        """섹션 관련 헬퍼 함수를 템플릿에 주입"""

        def is_section_available(section_name):
            """특정 섹션이 현재 사용자에게 가능한지 확인"""
            profile = getattr(g, 'profile', None)
            if not profile:
                return False
            return section_name in profile.get_available_sections()

        def get_section_icon(section_name):
            """섹션별 아이콘 클래스 반환"""
            icons = {
                'basic': 'fa-user',
                'organization': 'fa-building',
                'contract': 'fa-file-contract',
                'salary': 'fa-won-sign',
                'benefit': 'fa-umbrella-beach',
                'insurance': 'fa-shield-alt',
                'education': 'fa-graduation-cap',
                'career': 'fa-briefcase',
                'certificate': 'fa-certificate',
                'language': 'fa-language',
                'military': 'fa-medal',
                'employment_contract': 'fa-file-signature',
                'personnel_movement': 'fa-arrow-up',
                'attendance_assets': 'fa-calendar-check',
            }
            return icons.get(section_name, 'fa-info-circle')

        def get_section_title(section_name):
            """섹션별 제목 반환"""
            titles = {
                'basic': '개인 기본정보',
                'organization': '소속정보',
                'contract': '계약정보',
                'salary': '급여정보',
                'benefit': '연차 및 복리후생',
                'insurance': '4대보험',
                'education': '학력정보',
                'career': '경력정보',
                'certificate': '자격증 및 면허',
                'language': '언어능력',
                'military': '병역/프로젝트/수상',
                'employment_contract': '근로계약 및 연봉',
                'personnel_movement': '인사이동 및 고과',
                'attendance_assets': '근태 및 비품',
            }
            return titles.get(section_name, section_name)

        return dict(
            is_section_available=is_section_available,
            get_section_icon=get_section_icon,
            get_section_title=get_section_title
        )

    @app.context_processor
    def inject_field_registry_helpers():
        """
        FieldRegistry 관련 헬퍼 함수를 템플릿에 주입

        Phase 8.1: FieldRegistry 통합
        _field_renderer.html 매크로에서 사용
        """

        def get_section(section_id):
            """섹션 ID로 SectionDefinition 조회"""
            section = FieldRegistry.get_section(section_id)
            if section:
                return section.to_dict()
            return None

        def get_sections_by_domain(domain):
            """도메인에 속한 모든 섹션 조회"""
            sections = FieldRegistry.get_sections_by_domain(domain)
            return [s.to_dict() for s in sections]

        def get_field_options(field):
            """
            필드의 옵션 목록 반환

            옵션 우선순위:
            1. 직접 정의된 options
            2. ClassificationOption 참조 (options_category)
            3. 빈 리스트
            """
            # 직접 정의된 옵션이 있으면 사용
            if field.get('options'):
                return field['options']

            return []

        def is_field_visible(field, account_type):
            """필드가 특정 계정 타입에서 표시되는지 확인"""
            visibility = field.get('visibility', 'all')

            if visibility == 'all':
                return True
            if visibility == 'personal':
                return account_type == 'personal'
            if visibility == 'corporate':
                return account_type in ('corporate', 'employee_sub')
            if visibility == 'employee_sub':
                return account_type == 'employee_sub'
            if visibility == 'personal_and_employee':
                return account_type in ('personal', 'employee_sub')
            if visibility == 'corporate_only':
                return account_type == 'corporate'

            return True

        def is_section_visible(section, account_type):
            """섹션이 특정 계정 타입에서 표시되는지 확인"""
            visibility = section.get('visibility', 'all')

            if visibility == 'all':
                return True
            if visibility == 'personal':
                return account_type == 'personal'
            if visibility == 'corporate':
                return account_type in ('corporate', 'employee_sub')
            if visibility == 'employee_sub':
                return account_type == 'employee_sub'
            if visibility == 'personal_and_employee':
                return account_type in ('personal', 'employee_sub')
            if visibility == 'corporate_only':
                return account_type == 'corporate'

            return True

        def get_ordered_field_names(section_id, account_type=None):
            """섹션의 정렬된 필드명 목록 반환"""
            return FieldRegistry.get_ordered_names(section_id, account_type)

        return dict(
            get_section=get_section,
            get_sections_by_domain=get_sections_by_domain,
            get_field_options=get_field_options,
            is_field_visible=is_field_visible,
            is_section_visible=is_section_visible,
            get_ordered_field_names=get_ordered_field_names
        )

    @app.context_processor
    def inject_field_option_constants():
        """
        FieldOptions 상수를 템플릿에 주입 (SSOT 원칙)

        템플릿에서 사용 예:
        {% for opt in GENDER_OPTIONS %}
            <option value="{{ opt.value }}" ...>{{ opt.label }}</option>
        {% endfor %}
        """
        return FieldOptions.get_all()
