"""
마이페이지 Blueprint

일반 직원(employee role)의 개인 페이지 기능을 제공합니다.
- 회사 인사카드 (소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 인사기록 전체)
Phase 8: 상수 모듈 적용
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

from ..constants.session_keys import SessionKeys
from ..utils.decorators import login_required
from ..services.employee_service import employee_service
from ..services.system_setting_service import system_setting_service

mypage_bp = Blueprint('mypage', __name__, url_prefix='/my')


@mypage_bp.route('/company')
@login_required
def company_info():
    """회사 인사카드

    직원의 회사 관련 전체 인사정보를 표시합니다:
    - 소속정보, 계약정보, 급여정보, 복리후생, 4대보험
    - 인사기록: 근로계약/연봉, 인사이동/고과, 근태/비품
    """
    employee_id = session.get(SessionKeys.EMPLOYEE_ID)

    # employee_id가 없는 경우 (계정과 직원이 연결되지 않음)
    if not employee_id:
        flash('계정에 연결된 직원 정보가 없습니다.', 'warning')
        return redirect(url_for('main.index'))

    # 직원 정보 조회
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        flash('직원 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 회사 정보 조회 (SystemSetting에서)
    company_data = system_setting_service.get_company_data()

    # 급여 및 복리후생 데이터 조회
    salary = employee_service.get_salary_info(employee_id)
    benefit = employee_service.get_benefit_info(employee_id)
    contract = employee_service.get_contract_info(employee_id)
    insurance = employee_service.get_insurance_info(employee_id)

    # 인사기록 데이터 조회
    salary_history_list = employee_service.get_salary_history_list(employee_id)
    salary_payment_list = employee_service.get_salary_payment_list(employee_id)
    promotion_list = employee_service.get_promotion_list(employee_id)
    evaluation_list = employee_service.get_evaluation_list(employee_id)
    training_list = employee_service.get_training_list(employee_id)
    attendance_summary = employee_service.get_attendance_summary(employee_id, 2025)
    asset_list = employee_service.get_asset_list(employee_id)

    # 이력 및 경력 데이터 조회 (파셜 통합용)
    education_list = employee_service.get_education_list(employee_id)
    career_list = employee_service.get_career_list(employee_id)
    certificate_list = employee_service.get_certificate_list(employee_id)
    family_list = employee_service.get_family_list(employee_id)
    language_list = employee_service.get_language_list(employee_id)
    military = employee_service.get_military_info(employee_id)
    hr_project_list = employee_service.get_hr_project_list(employee_id)
    project_participation_list = employee_service.get_project_participation_list(employee_id)
    award_list = employee_service.get_award_list(employee_id)

    # 명함 데이터 조회 (조회 전용)
    business_card_front = employee_service.get_attachment_by_category(employee_id, 'business_card_front')
    business_card_back = employee_service.get_attachment_by_category(employee_id, 'business_card_back')

    # 첨부파일 목록 조회 (인사카드에서는 조회만 가능)
    attachment_list = employee_service.get_attachment_list(employee_id)

    return render_template('mypage/company_info.html',
                           employee=employee,
                           company_info=company_data,
                           salary=salary,
                           benefit=benefit,
                           contract=contract,
                           insurance=insurance,
                           salary_history_list=salary_history_list,
                           salary_payment_list=salary_payment_list,
                           promotion_list=promotion_list,
                           evaluation_list=evaluation_list,
                           training_list=training_list,
                           attendance_summary=attendance_summary,
                           asset_list=asset_list,
                           # 이력 및 경력 데이터 (파셜 통합용)
                           education_list=education_list,
                           career_list=career_list,
                           certificate_list=certificate_list,
                           family_list=family_list,
                           language_list=language_list,
                           military=military,
                           hr_project_list=hr_project_list,
                           project_participation_list=project_participation_list,
                           award_list=award_list,
                           is_readonly=True,
                           page_mode='hr_card',
                           # 명함 데이터 (조회 전용 - 직원은 업로드/삭제 불가)
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           can_edit_business_card=False,
                           # 첨부파일 (조회 전용)
                           attachment_list=attachment_list)
