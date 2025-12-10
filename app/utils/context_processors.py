"""
템플릿 컨텍스트 프로세서

모든 템플릿에서 사용 가능한 전역 변수와 함수를 제공합니다.
"""
from flask import session, g

from ..extensions import user_repo


def register_context_processors(app):
    """컨텍스트 프로세서 등록"""

    @app.context_processor
    def inject_current_user():
        """현재 로그인한 사용자 정보를 템플릿에 주입"""
        current_user = None
        is_authenticated = False

        user_id = session.get('user_id')
        if user_id and user_repo:
            # 세션에서 기본 정보 가져오기 (DB 조회 최소화)
            current_user = {
                'id': user_id,
                'username': session.get('username'),
                'role': session.get('user_role'),
                'employee_id': session.get('employee_id'),
                'is_admin': session.get('user_role') == 'admin',
                'is_manager': session.get('user_role') == 'manager',
                'account_type': session.get('account_type'),  # Phase 2: 계정 유형
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
            return session.get('user_role') == role

        def has_any_role(*roles):
            """현재 사용자가 특정 역할 중 하나를 가지고 있는지 확인"""
            return session.get('user_role') in roles

        def can_edit_employee(employee_id):
            """특정 직원 정보를 수정할 수 있는지 확인"""
            if session.get('user_role') == 'admin':
                return True
            if session.get('user_role') == 'manager':
                # 매니저의 부서 직원인지 확인
                manager_employee_id = session.get('employee_id')
                if manager_employee_id:
                    from ..models.employee import Employee
                    manager_employee = Employee.query.get(manager_employee_id)
                    target_employee = Employee.query.get(employee_id)
                    if manager_employee and target_employee:
                        return manager_employee.department == target_employee.department
                return False
            return session.get('employee_id') == employee_id

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
