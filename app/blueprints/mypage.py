"""
마이페이지 Blueprint

일반 직원(employee role)의 개인 페이지 기능을 제공합니다.
- 회사 인사카드 (소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 인사기록 전체)
Phase 8: 상수 모듈 적용
Phase 24: 통합 메서드 사용으로 N+1 쿼리 최적화
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

from ..shared.constants.session_keys import SessionKeys, AccountType
from ..shared.constants.status import ContractStatus, EmployeeStatus
from ..shared.utils.decorators import login_required
from app.domains.employee.services import employee_service
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

    # Phase 24: 통합 메서드 사용으로 N+1 쿼리 최적화
    # 21개 개별 호출 → 1개 통합 호출 + 명함 조회
    full_view_data = employee_service.get_employee_full_view_data(employee_id)

    # 명함 데이터 조회 (통합 메서드에 포함되지 않음)
    business_card_front = employee_service.get_attachment_by_category(employee_id, 'business_card_front')
    business_card_back = employee_service.get_attachment_by_category(employee_id, 'business_card_back')

    return render_template('mypage/company_info.html',
                           employee=employee,
                           company_info=company_data,
                           is_readonly=True,
                           page_mode='hr_card',
                           # 명함 데이터 (조회 전용 - 직원은 업로드/삭제 불가)
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           can_edit_business_card=False,
                           **full_view_data)
