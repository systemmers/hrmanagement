"""
마이페이지 Blueprint

일반 직원(employee role)의 개인 페이지 기능을 제공합니다.
- 회사 인사카드 (소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 인사기록 전체)
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

from ..utils.decorators import login_required
from ..extensions import (
    employee_repo, system_setting_repo,
    salary_repo, benefit_repo, contract_repo, salary_history_repo,
    promotion_repo, evaluation_repo, training_repo, attendance_repo,
    insurance_repo, asset_repo, salary_payment_repo,
    # 파셜 통합을 위한 추가 레포지토리
    education_repo, career_repo, certificate_repo, family_repo,
    language_repo, military_repo, project_repo, award_repo
)

mypage_bp = Blueprint('mypage', __name__, url_prefix='/my')


@mypage_bp.route('/company')
@login_required
def company_info():
    """회사 인사카드

    직원의 회사 관련 전체 인사정보를 표시합니다:
    - 소속정보, 계약정보, 급여정보, 복리후생, 4대보험
    - 인사기록: 근로계약/연봉, 인사이동/고과, 근태/비품
    """
    employee_id = session.get('employee_id')

    # employee_id가 없는 경우 (계정과 직원이 연결되지 않음)
    if not employee_id:
        flash('계정에 연결된 직원 정보가 없습니다.', 'warning')
        return redirect(url_for('main.index'))

    # 직원 정보 조회
    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 회사 정보 조회 (SystemSetting에서)
    company_data = {}
    company_keys = [
        'company.name', 'company.name_en', 'company.ceo_name',
        'company.business_number', 'company.corporate_number',
        'company.address', 'company.phone', 'company.fax',
        'company.website', 'company.established_date', 'company.logo_url'
    ]

    for key in company_keys:
        setting = system_setting_repo.get_by_key(key)
        if setting:
            field_name = key.replace('company.', '')
            company_data[field_name] = setting.get('value', '') if isinstance(setting, dict) else setting.value

    # 급여 및 복리후생 데이터 조회
    salary = salary_repo.get_by_employee_id(employee_id)
    benefit = benefit_repo.get_by_employee_id(employee_id)
    contract = contract_repo.get_by_employee_id(employee_id)
    insurance = insurance_repo.get_by_employee_id(employee_id)

    # 인사기록 데이터 조회
    salary_history_list = salary_history_repo.get_by_employee_id(employee_id)
    salary_payment_list = salary_payment_repo.get_by_employee_id(employee_id)
    promotion_list = promotion_repo.get_by_employee_id(employee_id)
    evaluation_list = evaluation_repo.get_by_employee_id(employee_id)
    training_list = training_repo.get_by_employee_id(employee_id)
    attendance_summary = attendance_repo.get_summary_by_employee(employee_id, 2025)
    asset_list = asset_repo.get_by_employee_id(employee_id)

    # 이력 및 경력 데이터 조회 (파셜 통합용)
    education_list = education_repo.get_by_employee_id(employee_id)
    career_list = career_repo.get_by_employee_id(employee_id)
    certificate_list = certificate_repo.get_by_employee_id(employee_id)
    family_list = family_repo.get_by_employee_id(employee_id)
    language_list = language_repo.get_by_employee_id(employee_id)
    military = military_repo.get_by_employee_id(employee_id)
    project_list = project_repo.get_by_employee_id(employee_id)
    award_list = award_repo.get_by_employee_id(employee_id)

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
                           project_list=project_list,
                           award_list=award_list,
                           is_readonly=True,
                           page_mode='hr_card')
