"""
계약 관리 Blueprint

개인-법인 계약 관계를 관리합니다.
- 개인 측면: 계약 목록 조회, 계약 승인 거절
- 법인 측면: 계약 요청, 계약 승인 거절, 계약 관리

Phase 6: 백엔드 리팩토링 - contract_helpers 적용
Phase 7: Service 레이어 적용 - ContractService 도입
Phase 8: 상수 모듈 적용
"""
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for

from app.shared.constants.field_options import FieldOptions
from app.shared.constants.session_keys import SessionKeys
from app.domains.contract.services import contract_service
from app.shared.utils.decorators import (
    login_required,
    personal_account_required,
    corporate_account_required,
    personal_or_employee_account_required
)
from app.shared.utils.contract_helpers import (
    get_contract_context,
    contract_party_required,
    approve_reject_permission_required
)
from app.shared.utils.api_helpers import api_success, api_error, api_not_found, api_forbidden

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')


# ===== 개인/직원 계정용 라우트 (21번 원칙) =====

@contracts_bp.route('/my')
@login_required
@personal_or_employee_account_required
def my_contracts():
    """내 계약 목록 (개인/직원 계정)

    21번 원칙: personal, employee_sub 계정 모두 지원
    """
    user_id = session.get(SessionKeys.USER_ID)
    contracts = contract_service.get_personal_contracts(user_id)
    stats = contract_service.get_personal_statistics(user_id)

    return render_template(
        'contracts/my_contracts.html',
        contracts=contracts,
        stats=stats
    )


@contracts_bp.route('/pending')
@login_required
@personal_or_employee_account_required
def pending_contracts():
    """대기 중인 계약 요청 (개인/직원 계정)

    21번 원칙: personal, employee_sub 계정 모두 지원
    """
    user_id = session.get(SessionKeys.USER_ID)
    contracts = contract_service.get_personal_pending_contracts(user_id)

    return render_template(
        'contracts/pending_contracts.html',
        contracts=contracts
    )


@contracts_bp.route('/<int:contract_id>')
@login_required
def contract_detail(contract_id):
    """계약 상세 조회"""
    contract = contract_service.get_contract_by_id(contract_id)
    if not contract:
        flash('계약을 찾을 수 없습니다.', 'error')
        return redirect(url_for('contracts.my_contracts'))

    # 권한 확인: 계약 당사자만 접근 가능
    ctx = get_contract_context()
    is_person, is_company = ctx.get_party_status(contract)

    if not is_person and not is_company:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 데이터 공유 설정 조회
    sharing_settings = contract_service.get_sharing_settings(contract_id)

    return render_template(
        'contracts/contract_detail.html',
        contract=contract,
        sharing_settings=sharing_settings,
        is_person=is_person,
        is_company=is_company
    )


# ===== 법인 계정용 라우트 =====

@contracts_bp.route('/company')
@login_required
@corporate_account_required
def company_contracts():
    """법인 계약 목록"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보가 없습니다.', 'error')
        return redirect(url_for('main.index'))

    contracts = contract_service.get_company_contracts(company_id)
    stats = contract_service.get_company_statistics(company_id)

    return render_template(
        'contracts/company_contracts.html',
        contracts=contracts,
        stats=stats,
        field_options=FieldOptions
    )


@contracts_bp.route('/company/pending')
@login_required
@corporate_account_required
def company_pending():
    """법인 대기 중인 요청"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보가 없습니다.', 'error')
        return redirect(url_for('main.index'))

    contracts = contract_service.get_company_pending_contracts(company_id)

    return render_template(
        'contracts/company_pending.html',
        contracts=contracts
    )


@contracts_bp.route('/request', methods=['GET', 'POST'])
@login_required
@corporate_account_required
def request_contract():
    """계약 요청 (법인 -> 개인/직원)

    통합 계약 요청 페이지:
    - 개인계정 (personal) 중 계약 미체결
    - 직원계정 (employee_sub) 중 pending_contract 상태
    """
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보가 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        from app.shared.utils.date_helpers import parse_form_date

        # 선택된 대상의 user_id로 계약 요청
        target_user_id = request.form.get('target_user_id', type=int)
        contract_type = request.form.get('contract_type', 'employment')
        position = request.form.get('position')
        department = request.form.get('department')
        notes = request.form.get('notes')

        # Phase 24: 날짜 파싱 헬퍼 사용 (DRY 원칙)
        contract_start_date = parse_form_date(request.form.get('contract_start_date'))
        contract_end_date = parse_form_date(request.form.get('contract_end_date'))

        if not target_user_id:
            flash('계약 대상을 선택해주세요.', 'error')
            return redirect(url_for('contracts.request_contract'))

        # user_id로 계약 요청 생성
        result = contract_service.create_employee_contract_request(
            employee_user_id=target_user_id,
            company_id=company_id,
            contract_type=contract_type,
            position=position,
            department=department,
            notes=notes,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date
        )

        if result:
            flash('계약 요청이 전송되었습니다.', 'success')
            return redirect(url_for('contracts.company_contracts'))
        else:
            flash(result.message, 'error')
            return redirect(url_for('contracts.request_contract'))

    # GET: 계약 요청 가능한 대상 목록 조회
    eligible_targets = contract_service.get_contract_eligible_targets(company_id)

    return render_template(
        'contracts/request_contract.html',
        personal_accounts=eligible_targets['personal_accounts'],
        employee_accounts=eligible_targets['employee_accounts']
    )


# ===== API 엔드포인트 =====

@contracts_bp.route('/api/<int:contract_id>/approve', methods=['POST'])
@login_required
@approve_reject_permission_required
def api_approve_contract(contract, contract_id):
    """계약 승인 API"""
    user_id = session.get(SessionKeys.USER_ID)

    result = contract_service.approve_contract(contract_id, user_id)
    if result:
        return api_success(result.data)
    return api_error(result.message)


@contracts_bp.route('/api/<int:contract_id>/reject', methods=['POST'])
@login_required
@approve_reject_permission_required
def api_reject_contract(contract, contract_id):
    """계약 거절 API"""
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json() or {}
    reason = data.get('reason')

    result = contract_service.reject_contract(contract_id, user_id, reason)
    if result:
        return api_success(result.data)
    return api_error(result.message)


@contracts_bp.route('/api/<int:contract_id>/terminate', methods=['POST'])
@login_required
@contract_party_required
def api_terminate_contract(contract, contract_id):
    """계약 종료 API"""
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json() or {}
    reason = data.get('reason')

    result = contract_service.terminate_contract(contract_id, user_id, reason)
    if result:
        return api_success(result.data)
    return api_error(result.message)


@contracts_bp.route('/api/<int:contract_id>/sharing-settings', methods=['GET', 'PUT'])
@login_required
def api_sharing_settings(contract_id):
    """데이터 공유 설정 API"""
    ctx = get_contract_context()

    contract = contract_service.get_contract_model_by_id(contract_id)
    if not contract:
        return api_not_found('계약')

    # 권한 확인: 개인만 공유 설정 변경 가능
    if contract.person_user_id != ctx.user_id:
        return api_forbidden()

    if request.method == 'GET':
        settings = contract_service.get_sharing_settings(contract_id)
        return api_success(settings)

    # PUT: 설정 업데이트
    data = request.get_json() or {}

    result = contract_service.update_sharing_settings(contract_id, data)
    if result:
        return api_success(result.data)
    return api_error(result.message)


@contracts_bp.route('/api/<int:contract_id>/sync-logs')
@login_required
@contract_party_required
def api_sync_logs(contract, contract_id):
    """동기화 로그 조회 API"""
    limit = request.args.get('limit', 50, type=int)
    logs = contract_service.get_sync_logs(contract_id, limit)

    return api_success(logs)


@contracts_bp.route('/api/search')
@login_required
@corporate_account_required
def api_search_contracts():
    """계약 검색 API (법인용)"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        return api_error('법인 정보가 없습니다.')

    status = request.args.get('status')
    contract_type = request.args.get('contract_type')
    search_term = request.args.get('q')

    contracts = contract_service.search_contracts(
        company_id=company_id,
        status=status,
        contract_type=contract_type,
        search_term=search_term
    )

    return api_success(contracts)


@contracts_bp.route('/api/stats/company')
@login_required
@corporate_account_required
def api_company_stats():
    """법인 계약 통계 API"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        return api_error('법인 정보가 없습니다.')

    stats = contract_service.get_company_statistics(company_id)
    return api_success(stats)


@contracts_bp.route('/api/stats/personal')
@login_required
@personal_or_employee_account_required
def api_personal_stats():
    """개인/직원 계약 통계 API (21번 원칙)"""
    user_id = session.get(SessionKeys.USER_ID)
    stats = contract_service.get_personal_statistics(user_id)
    return api_success(stats)


# ===== 21번 원칙: 직원 계약 요청 API =====

@contracts_bp.route('/api/employee/<int:user_id>/request', methods=['POST'])
@login_required
@corporate_account_required
def api_request_employee_contract(user_id):
    """직원에게 계약 요청 API (21번 원칙)

    직원 목록에서 계약 요청 버튼 클릭 시 호출
    """
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        return api_error('법인 정보가 없습니다.')

    data = request.get_json() or {}
    contract_type = data.get('contract_type', 'employment')
    position = data.get('position')
    department = data.get('department')
    notes = data.get('notes')

    result = contract_service.create_employee_contract_request(
        employee_user_id=user_id,
        company_id=company_id,
        contract_type=contract_type,
        position=position,
        department=department,
        notes=notes
    )

    if result:
        return api_success(result.data, message='계약 요청이 전송되었습니다.')
    return api_error(result.message)
