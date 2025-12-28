"""
REST API Blueprint

FieldRegistry API를 제공합니다.
Phase 2: Service 계층 표준화
Phase 6: FieldRegistry API 추가
"""
from flask import Blueprint, jsonify, request, session

from ..constants.field_registry import FieldRegistry
from ..constants.session_keys import SessionKeys
from ..utils.decorators import login_required

api_bp = Blueprint('api', __name__)


# ===== Field Registry API =====

@api_bp.route('/fields/sections', methods=['GET'])
@login_required
def get_all_field_sections():
    """
    모든 필드 섹션 메타데이터 조회

    Query Params:
        account_type: 계정 타입 (personal/corporate/employee_sub)
        domain: 도메인명 (profile/employee 등)

    Returns:
        {
            "sections": [...],
            "accountType": "corporate"
        }
    """
    # 계정 타입 결정 (쿼리 파라미터 우선, 없으면 세션에서)
    account_type = request.args.get('account_type') or session.get(SessionKeys.ACCOUNT_TYPE)
    domain = request.args.get('domain')

    if domain:
        # 도메인별 섹션 조회
        sections = FieldRegistry.get_sections_by_domain(domain)
    else:
        # 모든 섹션 조회
        sections = FieldRegistry.get_all_sections()

    # 계정 타입별 가시성 필터링 및 변환
    result_sections = []
    for section in sections:
        if account_type and not section.is_visible_for(account_type):
            continue
        result_sections.append(
            FieldRegistry.get_js_config(section.id, account_type)
        )

    return jsonify({
        'sections': result_sections,
        'accountType': account_type,
        'domain': domain,
    })


@api_bp.route('/fields/sections/<section_id>', methods=['GET'])
@login_required
def get_field_section(section_id):
    """
    특정 필드 섹션 메타데이터 조회

    Args:
        section_id: 섹션 ID

    Query Params:
        account_type: 계정 타입 (필터링용)

    Returns:
        섹션 메타데이터 JSON
    """
    account_type = request.args.get('account_type') or session.get(SessionKeys.ACCOUNT_TYPE)

    section = FieldRegistry.get_section(section_id)
    if not section:
        return jsonify({'error': f'Section not found: {section_id}'}), 404

    # 계정 타입별 가시성 체크
    if account_type and not section.is_visible_for(account_type):
        return jsonify({'error': 'Section not accessible for this account type'}), 403

    return jsonify({
        'section': FieldRegistry.get_js_config(section_id, account_type),
        'accountType': account_type,
    })


@api_bp.route('/fields/domains', methods=['GET'])
@login_required
def get_all_domains():
    """
    등록된 모든 도메인 목록 조회

    Returns:
        {"domains": ["profile", "employee", ...]}
    """
    return jsonify({
        'domains': FieldRegistry.get_all_domains()
    })
