"""
마이페이지 Blueprint

일반 직원(employee role)의 개인 페이지 기능을 제공합니다.
- 회사 인사카드 (회사 정보 읽기 전용)
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash

from ..utils.decorators import login_required
from ..extensions import employee_repo, system_setting_repo

mypage_bp = Blueprint('mypage', __name__, url_prefix='/my')


@mypage_bp.route('/company')
@login_required
def company_info():
    """회사 인사카드 (소속 조직 정보)

    직원이 등록된 회사의 정보를 읽기 전용으로 표시합니다.
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
    company_info = {}
    company_keys = [
        'company.name', 'company.name_en', 'company.ceo_name',
        'company.business_number', 'company.corporate_number',
        'company.address', 'company.phone', 'company.fax',
        'company.website', 'company.established_date', 'company.logo_url'
    ]

    for key in company_keys:
        setting = system_setting_repo.get_by_key(key)
        if setting:
            # key에서 'company.' 접두어 제거
            field_name = key.replace('company.', '')
            company_info[field_name] = setting.get('value', '') if isinstance(setting, dict) else setting.value

    return render_template('mypage/company_info.html',
                           employee=employee,
                           company_info=company_info)
