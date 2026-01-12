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
        """직원 등록 폼 - 통합 템플릿 사용"""
        classification_options = employee_service.get_all_classification_options()
        return render_template('domains/user/profile/edit.html',
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

    @bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
    @login_required
    def employee_edit(employee_id):
        """직원 수정 폼 (멀티테넌시 적용)"""
        user_role = session.get(SessionKeys.USER_ROLE)

        # Employee role은 본인 정보만 수정 가능
        if user_role == UserRole.EMPLOYEE:
            my_employee_id = session.get(SessionKeys.EMPLOYEE_ID)
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 수정 가능
        if user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        employee = employee_service.get_employee_model_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        attachment_list = employee_service.get_attachment_list(employee_id)
        business_card_front = employee_service.get_attachment_by_category(employee_id, AttachmentCategory.BUSINESS_CARD_FRONT)
        business_card_back = employee_service.get_attachment_by_category(employee_id, AttachmentCategory.BUSINESS_CARD_BACK)
        classification_options = employee_service.get_all_classification_options()

        from app.domains.user.services.user_service import user_service

        # 개인계약 존재 여부 확인 (개인정보 수정 제한용)
        # 개인계약을 먼저 조회하여 linked_user 결정에 활용
        company_id = session.get(SessionKeys.COMPANY_ID)
        has_person_contract = False
        person_contract = None

        if company_id:
            # 1차: employee_number로 계약 조회 (approved/terminated/expired 모두 포함)
            # 계약 이력이 있는 직원은 영구적으로 필드 잠금 유지
            if employee.employee_number:
                person_contract = contract_service.find_contract_with_history(
                    employee.employee_number, company_id
                )

            has_person_contract = person_contract is not None

        # 연결된 계정 조회 (계정정보 섹션용)
        # 개인계약이 있으면 person_user_id로 조회 (다중 법인 계약 지원)
        # 없으면 User.employee_id로 직접 조회 (법인 직접 생성 계정)
        if person_contract:
            linked_user = user_service.get_model_by_id(person_contract.person_user_id)
        else:
            linked_user = user_service.find_by_employee_id(employee_id)

        # 관계형 데이터 조회 (Service 레이어 경유 - Phase 24 레이어 분리)
        education_list = employee_service.get_education_list(employee_id)
        career_list = employee_service.get_career_list(employee_id)
        certificate_list = employee_service.get_certificate_list(employee_id)
        family_list = employee_service.get_family_list(employee_id)
        language_list = employee_service.get_language_list(employee_id)
        hr_project_list = employee_service.get_hr_project_list(employee_id)
        project_participation_list = employee_service.get_project_participation_list(employee_id)
        award_list = employee_service.get_award_list(employee_id)
        salary = employee_service.get_salary_info(employee_id)
        insurance = employee_service.get_insurance_info(employee_id)
        military = employee_service.get_military_info(employee_id)

        return render_template('domains/user/profile/edit.html',
                               employee=employee,
                               action='update',
                               is_corporate=True,
                               account_type=AccountType.CORPORATE,
                               page_mode='hr_card',
                               attachment_list=attachment_list,
                               business_card_front=business_card_front,
                               business_card_back=business_card_back,
                               classification_options=classification_options,
                               education_list=education_list,
                               career_list=career_list,
                               certificate_list=certificate_list,
                               family_list=family_list,
                               language_list=language_list,
                               hr_project_list=hr_project_list,
                               project_participation_list=project_participation_list,
                               award_list=award_list,
                               salary=salary,
                               insurance=insurance,
                               military=military,
                               has_person_contract=has_person_contract,
                               person_contract=person_contract,
                               user=linked_user)

    # ========================================
    # 레거시 리다이렉트 라우트
    # ========================================

    @bp.route('/employees/<int:employee_id>/edit/basic', methods=['GET'])
    @login_required
    def employee_edit_basic(employee_id):
        """기본정보 전용 수정 폼 - 통합 템플릿으로 리다이렉트"""
        return redirect(url_for('employees.employee_edit', employee_id=employee_id))

    @bp.route('/employees/<int:employee_id>/edit/history', methods=['GET'])
    @login_required
    def employee_edit_history(employee_id):
        """이력정보 전용 수정 폼 - 통합 템플릿으로 리다이렉트"""
        return redirect(url_for('employees.employee_edit', employee_id=employee_id))


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
