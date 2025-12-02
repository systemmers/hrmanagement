"""
템플릿 컨텍스트 프로세서

모든 템플릿에서 사용 가능한 전역 변수와 함수를 제공합니다.
"""
from flask import session

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
                # TODO: 매니저의 부서 직원인지 확인
                return True
            return session.get('employee_id') == employee_id

        return dict(
            has_role=has_role,
            has_any_role=has_any_role,
            can_edit_employee=can_edit_employee
        )
