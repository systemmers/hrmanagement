"""
직원 상세/폼 조회 라우트

직원 상세 정보 조회 및 편집 폼 렌더링을 제공합니다.
Phase 8: 상수 모듈 적용
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session

from ...constants.session_keys import SessionKeys, UserRole, AccountType
from ...utils.decorators import login_required, manager_or_admin_required
from ...utils.object_helpers import safe_get
from ...services.employee_service import employee_service
from ...models.person_contract import PersonCorporateContract
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
        return render_template('profile/edit.html',
                               employee=None,
                               action='create',
                               is_corporate=True,
                               account_type=AccountType.CORPORATE,
                               page_mode='hr_card',
                               classification_options=classification_options)

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
        business_card_front = employee_service.get_attachment_by_category(employee_id, 'business_card_front')
        business_card_back = employee_service.get_attachment_by_category(employee_id, 'business_card_back')
        classification_options = employee_service.get_all_classification_options()

        from ...extensions import user_repo

        # 개인계약 존재 여부 확인 (개인정보 수정 제한용)
        # 개인계약을 먼저 조회하여 linked_user 결정에 활용
        company_id = session.get(SessionKeys.COMPANY_ID)
        has_person_contract = False
        person_contract = None

        if company_id:
            # 1차: employee_number로 approved 계약 조회
            if employee.employee_number:
                person_contract = PersonCorporateContract.query.filter_by(
                    employee_number=employee.employee_number,
                    company_id=company_id,
                    status=PersonCorporateContract.STATUS_APPROVED
                ).first()

            has_person_contract = person_contract is not None

        # 연결된 계정 조회 (계정정보 섹션용)
        # 개인계약이 있으면 person_user_id로 조회 (다중 법인 계약 지원)
        # 없으면 User.employee_id로 직접 조회 (법인 직접 생성 계정)
        if person_contract:
            linked_user = user_repo.get_model_by_id(person_contract.person_user_id)
        else:
            linked_user = user_repo.get_by_employee_id(employee_id)

        return render_template('profile/edit.html',
                               employee=employee,
                               action='update',
                               is_corporate=True,
                               account_type=AccountType.CORPORATE,
                               page_mode='hr_card',
                               attachment_list=attachment_list,
                               business_card_front=business_card_front,
                               business_card_back=business_card_back,
                               classification_options=classification_options,
                               language_list=list(employee.languages),
                               hr_project_list=list(employee.hr_projects),
                               project_participation_list=list(employee.project_participations),
                               salary=employee.salary,
                               insurance=employee.insurance,
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
    """전체 정보 페이지 렌더링 (관리자/매니저용)"""
    # 관계형 데이터 조회
    education_list = employee_service.get_education_list(employee_id)
    career_list = employee_service.get_career_list(employee_id)
    certificate_list = employee_service.get_certificate_list(employee_id)
    family_list = employee_service.get_family_list(employee_id)
    language_list = employee_service.get_language_list(employee_id)
    military = employee_service.get_military_info(employee_id)

    # 핵심 기능 데이터 조회
    salary = employee_service.get_salary_info(employee_id)
    benefit = employee_service.get_benefit_info(employee_id)
    contract = employee_service.get_contract_info(employee_id)
    salary_history_list = employee_service.get_salary_history_list(employee_id)

    # 인사평가 기능 데이터 조회
    promotion_list = employee_service.get_promotion_list(employee_id)
    evaluation_list = employee_service.get_evaluation_list(employee_id)
    training_list = employee_service.get_training_list(employee_id)
    attendance_summary = employee_service.get_attendance_summary(employee_id, 2025)

    # 부가 기능 데이터 조회
    insurance = employee_service.get_insurance_info(employee_id)
    hr_project_list = employee_service.get_hr_project_list(employee_id)
    project_participation_list = employee_service.get_project_participation_list(employee_id)
    award_list = employee_service.get_award_list(employee_id)
    asset_list = employee_service.get_asset_list(employee_id)

    # 급여 지급 이력 조회
    salary_payment_list = employee_service.get_salary_payment_list(employee_id)

    # 첨부파일 조회
    attachment_list = employee_service.get_attachment_list(employee_id)

    # 명함 이미지 조회
    business_card_front = employee_service.get_attachment_by_category(employee_id, 'business_card_front')
    business_card_back = employee_service.get_attachment_by_category(employee_id, 'business_card_back')

    from ...extensions import user_repo

    # 명함 편집 권한 체크
    can_edit_business_card = (
        session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN or
        (session.get(SessionKeys.USER_ROLE) == UserRole.EMPLOYEE and session.get(SessionKeys.EMPLOYEE_ID) == employee_id)
    )

    # 개인계약 조회 (동기화 버튼용 + 계정정보 섹션용)
    # 개인계약을 먼저 조회하여 linked_user 결정에 활용
    company_id = session.get(SessionKeys.COMPANY_ID)
    person_contract = None
    emp_number = safe_get(employee, 'employee_number')
    if company_id and emp_number:
        person_contract = PersonCorporateContract.query.filter_by(
            employee_number=emp_number,
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).first()

    # 연결된 계정 조회 (계정정보 섹션용)
    # 개인계약이 있으면 person_user_id로 조회 (다중 법인 계약 지원)
    # 없으면 User.employee_id로 직접 조회 (법인 직접 생성 계정)
    if person_contract:
        linked_user = user_repo.get_model_by_id(person_contract.person_user_id)
    else:
        linked_user = user_repo.get_by_employee_id(employee_id)

    return render_template('profile/detail.html',
                           employee=employee,
                           is_corporate=True,
                           account_type=AccountType.CORPORATE,
                           page_mode='hr_card',
                           education_list=education_list,
                           career_list=career_list,
                           certificate_list=certificate_list,
                           family_list=family_list,
                           language_list=language_list,
                           military=military,
                           salary=salary,
                           benefit=benefit,
                           contract=contract,
                           salary_history_list=salary_history_list,
                           promotion_list=promotion_list,
                           evaluation_list=evaluation_list,
                           training_list=training_list,
                           attendance_summary=attendance_summary,
                           insurance=insurance,
                           hr_project_list=hr_project_list,
                           project_participation_list=project_participation_list,
                           award_list=award_list,
                           asset_list=asset_list,
                           salary_payment_list=salary_payment_list,
                           attachment_list=attachment_list,
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           can_edit_business_card=can_edit_business_card,
                           person_contract=person_contract,
                           user=linked_user)
