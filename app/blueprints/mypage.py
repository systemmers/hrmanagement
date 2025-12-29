"""
마이페이지 Blueprint

일반 직원(employee role)의 개인 페이지 기능을 제공합니다.
- 회사 인사카드 (소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 인사기록 전체)
Phase 8: 상수 모듈 적용
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

from ..constants.session_keys import SessionKeys, AccountType
from ..constants.status import ContractStatus, EmployeeStatus
from ..utils.decorators import login_required
from ..services.employee_service import employee_service
from ..services.system_setting_service import system_setting_service
from ..services import contract_service

mypage_bp = Blueprint('mypage', __name__, url_prefix='/my')


@mypage_bp.route('/company')
@login_required
def company_info():
    """회사 인사카드

    계정 유형 및 계약/직원 상태별 분기 처리:
    - personal: 회사 목록으로 리다이렉트
    - employee_sub (승인된 계약 있음): 인사카드 표시
    - employee_sub (계약 미승인): 계약 대기 안내
    - employee_sub (pending_info): 프로필 완성 리다이렉트
    - employee_id 없음: HR 문의 안내
    """
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)
    employee_id = session.get(SessionKeys.EMPLOYEE_ID)

    # 1. personal 계정은 회사 목록으로 리다이렉트
    if account_type == AccountType.PERSONAL:
        return redirect(url_for('personal.company_card_list'))

    # 2. employee_id 없음 체크
    if not employee_id:
        return render_template('mypage/no_employee_info.html')

    # 3. 직원 정보 조회
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        flash('직원 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 4. 계약 기반 접근 제어 (status와 무관하게 승인된 계약 필수)
    user_id = session.get(SessionKeys.USER_ID)
    company_id = session.get(SessionKeys.COMPANY_ID)

    if user_id and company_id:
        contract_status = contract_service.get_employee_contract_status(user_id, company_id)
        if contract_status != ContractStatus.APPROVED:
            return render_template('mypage/pending_contract.html', employee=employee)

    # 5. 프로필 미완성 체크 (pending_info → 프로필 완성 페이지로)
    employee_status = employee.get('status')
    if employee_status == EmployeeStatus.PENDING_INFO:
        return redirect(url_for('profile.complete_profile'))

    # 6. 정상 상태: 인사카드 표시

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
