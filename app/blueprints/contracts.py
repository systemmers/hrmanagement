"""
계약 관리 Blueprint

개인-법인 계약 관계를 관리합니다.
- 개인 측면: 계약 목록 조회, 계약 승인 거절
- 법인 측면: 계약 요청, 계약 승인 거절, 계약 관리
"""
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for

from ..extensions import person_contract_repo, user_repo
from ..database import db
from ..models.company import Company
from ..models.user import User
from ..models.person_contract import PersonCorporateContract
from ..utils.decorators import login_required, personal_account_required, corporate_account_required

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')


# ===== 개인 계정용 라우트 =====

@contracts_bp.route('/my')
@login_required
@personal_account_required
def my_contracts():
    """내 계약 목록 (개인 계정)"""
    user_id = session.get('user_id')
    contracts = person_contract_repo.get_by_person_user_id(user_id)
    stats = person_contract_repo.get_statistics_by_person(user_id)

    return render_template(
        'contracts/my_contracts.html',
        contracts=contracts,
        stats=stats
    )


@contracts_bp.route('/pending')
@login_required
@personal_account_required
def pending_contracts():
    """대기 중인 계약 요청 (개인 계정)"""
    user_id = session.get('user_id')
    contracts = person_contract_repo.get_pending_contracts_by_person(user_id)

    return render_template(
        'contracts/pending_contracts.html',
        contracts=contracts
    )


@contracts_bp.route('/<int:contract_id>')
@login_required
def contract_detail(contract_id):
    """계약 상세 조회"""
    contract = person_contract_repo.get_by_id(contract_id)
    if not contract:
        flash('계약을 찾을 수 없습니다.', 'error')
        return redirect(url_for('contracts.my_contracts'))

    # 권한 확인: 계약 당사자만 접근 가능
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    company_id = session.get('company_id')

    is_person = contract['person_user_id'] == user_id
    is_company = account_type == 'corporate' and contract['company_id'] == company_id

    if not is_person and not is_company:
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 데이터 공유 설정 조회
    sharing_settings = person_contract_repo.get_sharing_settings(contract_id)

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
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보가 없습니다.', 'error')
        return redirect(url_for('main.index'))

    contracts = person_contract_repo.get_by_company_id(company_id)
    stats = person_contract_repo.get_statistics_by_company(company_id)

    return render_template(
        'contracts/company_contracts.html',
        contracts=contracts,
        stats=stats
    )


@contracts_bp.route('/company/pending')
@login_required
@corporate_account_required
def company_pending():
    """법인 대기 중인 요청"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보가 없습니다.', 'error')
        return redirect(url_for('main.index'))

    contracts = person_contract_repo.get_pending_contracts_by_company(company_id)

    return render_template(
        'contracts/company_pending.html',
        contracts=contracts
    )


@contracts_bp.route('/request', methods=['GET', 'POST'])
@login_required
@corporate_account_required
def request_contract():
    """계약 요청 (법인 -> 개인)"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보가 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        person_email = request.form.get('person_email')
        contract_type = request.form.get('contract_type', 'employment')
        position = request.form.get('position')
        department = request.form.get('department')
        notes = request.form.get('notes')

        # 개인 사용자 조회
        person_user = User.query.filter_by(
            email=person_email,
            account_type='personal'
        ).first()

        if not person_user:
            flash('해당 이메일의 개인 계정을 찾을 수 없습니다.', 'error')
            return redirect(url_for('contracts.request_contract'))

        try:
            contract = person_contract_repo.create_contract_request(
                person_user_id=person_user.id,
                company_id=company_id,
                requested_by='company',
                contract_type=contract_type,
                position=position,
                department=department,
                notes=notes
            )
            flash('계약 요청이 전송되었습니다.', 'success')
            return redirect(url_for('contracts.company_contracts'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('contracts.request_contract'))

    return render_template('contracts/request_contract.html')


# ===== API 엔드포인트 =====

@contracts_bp.route('/api/<int:contract_id>/approve', methods=['POST'])
@login_required
def api_approve_contract(contract_id):
    """계약 승인 API"""
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    company_id = session.get('company_id')

    contract = person_contract_repo.get_model_by_id(contract_id)
    if not contract:
        return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

    # 권한 확인
    if contract.requested_by == 'company':
        # 기업에서 요청한 경우 개인이 승인
        if contract.person_user_id != user_id:
            return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    else:
        # 개인이 요청한 경우 기업이 승인
        if account_type != 'corporate' or contract.company_id != company_id:
            return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    try:
        result = person_contract_repo.approve_contract(contract_id, user_id)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@contracts_bp.route('/api/<int:contract_id>/reject', methods=['POST'])
@login_required
def api_reject_contract(contract_id):
    """계약 거절 API"""
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    company_id = session.get('company_id')

    contract = person_contract_repo.get_model_by_id(contract_id)
    if not contract:
        return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

    # 권한 확인
    if contract.requested_by == 'company':
        if contract.person_user_id != user_id:
            return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    else:
        if account_type != 'corporate' or contract.company_id != company_id:
            return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    data = request.get_json() or {}
    reason = data.get('reason')

    try:
        result = person_contract_repo.reject_contract(contract_id, user_id, reason)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@contracts_bp.route('/api/<int:contract_id>/terminate', methods=['POST'])
@login_required
def api_terminate_contract(contract_id):
    """계약 종료 API"""
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    company_id = session.get('company_id')

    contract = person_contract_repo.get_model_by_id(contract_id)
    if not contract:
        return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

    # 권한 확인: 양쪽 모두 종료 가능
    is_person = contract.person_user_id == user_id
    is_company = account_type == 'corporate' and contract.company_id == company_id

    if not is_person and not is_company:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    data = request.get_json() or {}
    reason = data.get('reason')

    try:
        result = person_contract_repo.terminate_contract(contract_id, user_id, reason)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@contracts_bp.route('/api/<int:contract_id>/sharing-settings', methods=['GET', 'PUT'])
@login_required
def api_sharing_settings(contract_id):
    """데이터 공유 설정 API"""
    user_id = session.get('user_id')

    contract = person_contract_repo.get_model_by_id(contract_id)
    if not contract:
        return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

    # 권한 확인: 개인만 공유 설정 변경 가능
    if contract.person_user_id != user_id:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    if request.method == 'GET':
        settings = person_contract_repo.get_sharing_settings(contract_id)
        return jsonify({'success': True, 'data': settings})

    # PUT: 설정 업데이트
    data = request.get_json() or {}

    try:
        result = person_contract_repo.update_sharing_settings(contract_id, data)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@contracts_bp.route('/api/<int:contract_id>/sync-logs')
@login_required
def api_sync_logs(contract_id):
    """동기화 로그 조회 API"""
    user_id = session.get('user_id')
    account_type = session.get('account_type')
    company_id = session.get('company_id')

    contract = person_contract_repo.get_model_by_id(contract_id)
    if not contract:
        return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

    # 권한 확인
    is_person = contract.person_user_id == user_id
    is_company = account_type == 'corporate' and contract.company_id == company_id

    if not is_person and not is_company:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    limit = request.args.get('limit', 50, type=int)
    logs = person_contract_repo.get_sync_logs(contract_id, limit)

    return jsonify({'success': True, 'data': logs})


@contracts_bp.route('/api/search')
@login_required
@corporate_account_required
def api_search_contracts():
    """계약 검색 API (법인용)"""
    company_id = session.get('company_id')
    if not company_id:
        return jsonify({'success': False, 'message': '법인 정보가 없습니다.'}), 400

    status = request.args.get('status')
    contract_type = request.args.get('contract_type')
    search_term = request.args.get('q')

    contracts = person_contract_repo.search_contracts(
        company_id=company_id,
        status=status,
        contract_type=contract_type,
        search_term=search_term
    )

    return jsonify({'success': True, 'data': contracts})


@contracts_bp.route('/api/stats/company')
@login_required
@corporate_account_required
def api_company_stats():
    """법인 계약 통계 API"""
    company_id = session.get('company_id')
    if not company_id:
        return jsonify({'success': False, 'message': '법인 정보가 없습니다.'}), 400

    stats = person_contract_repo.get_statistics_by_company(company_id)
    return jsonify({'success': True, 'data': stats})


@contracts_bp.route('/api/stats/personal')
@login_required
@personal_account_required
def api_personal_stats():
    """개인 계약 통계 API"""
    user_id = session.get('user_id')
    stats = person_contract_repo.get_statistics_by_person(user_id)
    return jsonify({'success': True, 'data': stats})
