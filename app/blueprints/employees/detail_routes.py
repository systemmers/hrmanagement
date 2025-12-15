"""
직원 상세/폼 조회 라우트

직원 상세 정보 조회 및 편집 폼 렌더링을 제공합니다.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session

from ...utils.decorators import login_required, manager_or_admin_required
from ...extensions import (
    employee_repo, classification_repo,
    education_repo, career_repo, certificate_repo,
    family_repo, language_repo, military_repo,
    salary_repo, benefit_repo, contract_repo, salary_history_repo,
    promotion_repo, evaluation_repo, training_repo, attendance_repo,
    insurance_repo, hr_project_repo, project_participation_repo, award_repo, asset_repo,
    salary_payment_repo, attachment_repo
)
from .helpers import verify_employee_access


def register_detail_routes(bp: Blueprint):
    """상세/폼 조회 라우트를 Blueprint에 등록"""

    @bp.route('/employees/<int:employee_id>')
    @login_required
    def employee_detail(employee_id):
        """직원 상세 정보 (멀티테넌시 적용) - 통합 템플릿 사용"""
        user_role = session.get('user_role')

        # Employee role은 본인 정보만 접근 가능
        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 열람할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_detail', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 접근 가능
        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        employee = employee_repo.get_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        # 모든 role에서 통합 템플릿 사용
        return _render_employee_full_view(employee_id, employee)

    @bp.route('/employees/new', methods=['GET'])
    @manager_or_admin_required
    def employee_new():
        """직원 등록 폼 - 통합 템플릿 사용"""
        classification_options = classification_repo.get_all_options()
        return render_template('profile/edit.html',
                               employee=None,
                               action='create',
                               is_corporate=True,
                               account_type='corporate',
                               page_mode='hr_card',
                               classification_options=classification_options)

    @bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
    @login_required
    def employee_edit(employee_id):
        """직원 수정 폼 (멀티테넌시 적용)"""
        user_role = session.get('user_role')

        # Employee role은 본인 정보만 수정 가능
        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 수정 가능
        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        employee = employee_repo.get_model_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        attachment_list = attachment_repo.get_by_employee_id(employee_id)
        business_card_front = attachment_repo.get_one_by_category(employee_id, 'business_card_front')
        business_card_back = attachment_repo.get_one_by_category(employee_id, 'business_card_back')
        classification_options = classification_repo.get_all_options()

        return render_template('profile/edit.html',
                               employee=employee,
                               action='update',
                               is_corporate=True,
                               account_type='corporate',
                               page_mode='hr_card',
                               attachment_list=attachment_list,
                               business_card_front=business_card_front,
                               business_card_back=business_card_back,
                               classification_options=classification_options,
                               language_list=list(employee.languages),
                               hr_project_list=list(employee.hr_projects),
                               project_participation_list=list(employee.project_participations),
                               salary=employee.salary,
                               insurance=employee.insurance)

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
    education_list = education_repo.get_by_employee_id(employee_id)
    career_list = career_repo.get_by_employee_id(employee_id)
    certificate_list = certificate_repo.get_by_employee_id(employee_id)
    family_list = family_repo.get_by_employee_id(employee_id)
    language_list = language_repo.get_by_employee_id(employee_id)
    military = military_repo.get_by_employee_id(employee_id)

    # 핵심 기능 데이터 조회
    salary = salary_repo.get_by_employee_id(employee_id)
    benefit = benefit_repo.get_by_employee_id(employee_id)
    contract = contract_repo.get_by_employee_id(employee_id)
    salary_history_list = salary_history_repo.get_by_employee_id(employee_id)

    # 인사평가 기능 데이터 조회
    promotion_list = promotion_repo.get_by_employee_id(employee_id)
    evaluation_list = evaluation_repo.get_by_employee_id(employee_id)
    training_list = training_repo.get_by_employee_id(employee_id)
    attendance_summary = attendance_repo.get_summary_by_employee(employee_id, 2025)

    # 부가 기능 데이터 조회
    insurance = insurance_repo.get_by_employee_id(employee_id)
    hr_project_list = hr_project_repo.get_by_employee_id(employee_id)
    project_participation_list = project_participation_repo.get_by_employee_id(employee_id)
    award_list = award_repo.get_by_employee_id(employee_id)
    asset_list = asset_repo.get_by_employee_id(employee_id)

    # 급여 지급 이력 조회
    salary_payment_list = salary_payment_repo.get_by_employee_id(employee_id)

    # 첨부파일 조회
    attachment_list = attachment_repo.get_by_employee_id(employee_id)

    # 명함 이미지 조회
    business_card_front = attachment_repo.get_one_by_category(employee_id, 'business_card_front')
    business_card_back = attachment_repo.get_one_by_category(employee_id, 'business_card_back')

    # 명함 편집 권한 체크
    can_edit_business_card = (
        session.get('user_role') == 'admin' or
        (session.get('user_role') == 'employee' and session.get('employee_id') == employee_id)
    )

    return render_template('profile/detail.html',
                           employee=employee,
                           is_corporate=True,
                           account_type='corporate',
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
                           can_edit_business_card=can_edit_business_card)
