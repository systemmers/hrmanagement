"""
직원 상세/폼 조회 라우트

직원 상세 정보 조회 및 편집 폼 렌더링을 제공합니다.
Phase 8: 상수 모듈 적용
Phase 24: 레이어 분리 - 관계 필드 직접 접근 → Service 경유 조회
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session

from app.shared.constants.session_keys import SessionKeys, UserRole, AccountType
from app.shared.utils.decorators import login_required, manager_or_admin_required
from app.shared.utils.object_helpers import safe_get
from app.domains.employee.services import employee_service
from app.domains.contract.services.contract_service import contract_service
from app.domains.attachment.constants import AttachmentCategory
from .helpers import verify_employee_access


def register_detail_routes(bp: Blueprint):
    """상세/폼 조회 라우트를 Blueprint에 등록"""

    @bp.route('/employees/<int:employee_id>')
    @login_required
    def employee_detail(employee_id):
        """직원 상세 정보 (멀티테넌시 적용) - 통합 템플릿 사용"""
        user_role = session.get(SessionKeys.USER_ROLE)

        # Employee role은 본인 정보만 접근 가능
        if user_role == UserRole.EMPLOYEE:
            my_employee_id = session.get(SessionKeys.EMPLOYEE_ID)
            if my_employee_id != employee_id:
                flash('본인 정보만 열람할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_detail', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 접근 가능
        if user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        employee = employee_service.get_employee_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        # 모든 role에서 통합 템플릿 사용
        return _render_employee_full_view(employee_id, employee)

    @bp.route('/employees/new', methods=['GET'])
    @manager_or_admin_required
    def employee_new():
        """직원 등록 폼 - 통합 템플릿 사용 (인라인 편집 스타일)

        Phase 2: edit.html → detail.html (CREATE 모드)
        - 인라인 편집 UI로 통합
        - 필수 필드: 이름, 계정ID, 이메일
        """
        classification_options = employee_service.get_all_classification_options()
        return render_template('domains/user/profile/detail.html',
                               employee=None,
                               action='create',
                               is_corporate=True,
                               account_type=AccountType.CORPORATE,
                               page_mode='hr_card',
                               classification_options=classification_options,
                               # 템플릿 fallback 제거를 위해 빈 리스트 명시적 전달
                               education_list=[],
                               career_list=[],
                               certificate_list=[],
                               family_list=[],
                               language_list=[],
                               award_list=[],
                               military=None)

    # ========================================
    # 레거시 라우트 삭제 (2026-01-16)
    # - employee_edit(): 인라인 편집으로 대체
    # - employee_edit_basic(): 삭제
    # - employee_edit_history(): 삭제
    # ========================================


def _render_employee_full_view(employee_id, employee):
    """전체 정보 페이지 렌더링 (관리자/매니저용)

    Phase 24: 통합 메서드 사용으로 N+1 쿼리 최적화
    - 21개 개별 호출 → 1개 통합 호출 + 부가 조회
    """
    from app.domains.user.services.user_service import user_service

    # 통합 데이터 조회 (Phase 24: N+1 최적화)
    full_view_data = employee_service.get_employee_full_view_data(employee_id)

    # 명함 이미지 조회 (별도 조회 필요)
    business_card_front = employee_service.get_attachment_by_category(employee_id, AttachmentCategory.BUSINESS_CARD_FRONT)
    business_card_back = employee_service.get_attachment_by_category(employee_id, AttachmentCategory.BUSINESS_CARD_BACK)

    # 명함 편집 권한 체크
    can_edit_business_card = (
        session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN or
        (session.get(SessionKeys.USER_ROLE) == UserRole.EMPLOYEE and session.get(SessionKeys.EMPLOYEE_ID) == employee_id)
    )

    # 개인계약 조회 (동기화 버튼용 + 계정정보 섹션용)
    company_id = session.get(SessionKeys.COMPANY_ID)
    person_contract = None
    emp_number = safe_get(employee, 'employee_number')
    if company_id and emp_number:
        person_contract = contract_service.find_approved_contract(
            emp_number, company_id
        )

    # 연결된 계정 조회 (계정정보 섹션용)
    if person_contract:
        linked_user = user_service.get_model_by_id(person_contract.person_user_id)
    else:
        linked_user = user_service.find_by_employee_id(employee_id)

    return render_template('domains/user/profile/detail.html',
                           employee=employee,
                           is_corporate=True,
                           account_type=AccountType.CORPORATE,
                           page_mode='hr_card',
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           can_edit_business_card=can_edit_business_card,
                           person_contract=person_contract,
                           user=linked_user,
                           **full_view_data)
