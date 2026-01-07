"""
User Domain: MyPage Blueprint

Phase 1 Migration: domains/user/blueprints/mypage.py
- Employee personal page features
- Company HR card (read-only view)
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

from app.shared.constants.session_keys import SessionKeys, AccountType
from app.shared.constants.status import ContractStatus, EmployeeStatus
from app.shared.utils.decorators import login_required
from app.domains.employee.services import employee_service
from app.domains.platform.services.system_setting_service import system_setting_service
from app.domains.contract.services import contract_service

mypage_bp = Blueprint('mypage', __name__, url_prefix='/my')


@mypage_bp.route('/company')
@login_required
def company_info():
    """Company HR Card

    Account type and contract/employee status branching:
    - personal: Redirect to company list
    - employee_sub (approved contract): Display HR card
    - employee_sub (pending contract): Contract waiting notice
    - employee_sub (pending_info): Redirect to profile completion
    - No employee_id: HR inquiry notice
    """
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)
    employee_id = session.get(SessionKeys.EMPLOYEE_ID)

    # 1. Personal account redirects to company list
    if account_type == AccountType.PERSONAL:
        return redirect(url_for('personal.company_card_list'))

    # 2. Check for missing employee_id
    if not employee_id:
        return render_template('mypage/no_employee_info.html')

    # 3. Fetch employee info
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        flash('직원 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 4. Contract-based access control (approved contract required)
    user_id = session.get(SessionKeys.USER_ID)
    company_id = session.get(SessionKeys.COMPANY_ID)

    if user_id and company_id:
        contract_status = contract_service.get_employee_contract_status(user_id, company_id)
        if contract_status != ContractStatus.APPROVED:
            return render_template('mypage/pending_contract.html', employee=employee)

    # 5. Check incomplete profile (pending_info -> redirect to profile completion)
    employee_status = employee.get('status')
    if employee_status == EmployeeStatus.PENDING_INFO:
        return redirect(url_for('profile.complete_profile'))

    # 6. Normal state: Display HR card

    # Fetch company info from SystemSetting
    company_data = system_setting_service.get_company_data()

    # Phase 24: Optimized with unified method (21 calls -> 1 call + business card)
    full_view_data = employee_service.get_employee_full_view_data(employee_id)

    # Business card data (not included in unified method)
    business_card_front = employee_service.get_attachment_by_category(employee_id, 'business_card_front')
    business_card_back = employee_service.get_attachment_by_category(employee_id, 'business_card_back')

    return render_template('mypage/company_info.html',
                           employee=employee,
                           company_info=company_data,
                           is_readonly=True,
                           page_mode='hr_card',
                           # Business card data (view only - employees cannot upload/delete)
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           can_edit_business_card=False,
                           **full_view_data)
