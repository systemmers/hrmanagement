"""
RequiredDocument API 라우트

법인별 필수 서류 관리 API를 제공합니다.
Phase 4.1: 필수 서류 설정 기능 추가

- GET /api/required-documents/<company_id> - 필수 서류 목록 조회
- POST /api/required-documents - 필수 서류 생성
- PUT /api/required-documents/<id> - 필수 서류 수정
- DELETE /api/required-documents/<id> - 필수 서류 삭제
- PATCH /api/required-documents/<company_id>/order - 순서 변경
- PATCH /api/required-documents/<id>/activate - 활성화
- PATCH /api/required-documents/<id>/deactivate - 비활성화
- GET /api/required-documents/<company_id>/check/<owner_type>/<owner_id> - 제출 현황 확인
"""
from flask import request, current_app

from app.shared.utils.decorators import api_login_required, corporate_admin_required
from app.shared.utils.transaction import atomic_transaction
from app.shared.utils.api_helpers import (
    api_success, api_error, api_not_found, api_server_error
)
from app.domains.attachment.services import required_document_service
from . import attachment_bp


# ========================================
# 필수 서류 목록 조회 API
# ========================================

@attachment_bp.route('/api/required-documents/<int:company_id>', methods=['GET'])
@api_login_required
def get_required_documents(company_id):
    """
    법인별 필수 서류 목록 조회 API

    Args:
        company_id: 법인 ID

    Query Params:
        active_only: 활성화된 항목만 조회 (기본값: true)
        category: 카테고리 필터
        linked_entity_type: 연결 엔티티 타입 필터

    Returns:
        필수 서류 목록
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        category = request.args.get('category')
        linked_entity_type = request.args.get('linked_entity_type')

        # 필터 조건에 따른 조회
        if category:
            documents = required_document_service.get_by_category(company_id, category)
        elif linked_entity_type:
            documents = required_document_service.get_by_linked_entity(company_id, linked_entity_type)
        else:
            documents = required_document_service.get_by_company(company_id, active_only)

        return api_success({'documents': documents})

    except Exception as e:
        current_app.logger.error(f'필수 서류 목록 조회 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 개별 필수 서류 상세 조회 API
# ========================================

@attachment_bp.route('/api/required-documents/detail/<int:doc_id>', methods=['GET'])
@api_login_required
def get_required_document_detail(doc_id):
    """
    필수 서류 상세 조회 API

    Args:
        doc_id: 필수 서류 ID

    Returns:
        필수 서류 상세 정보
    """
    try:
        document = required_document_service.get_by_id(doc_id)
        if not document:
            return api_not_found('필수 서류')

        return api_success(document)

    except Exception as e:
        current_app.logger.error(f'필수 서류 상세 조회 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 제출 서류만 조회 API
# ========================================

@attachment_bp.route('/api/required-documents/<int:company_id>/required', methods=['GET'])
@api_login_required
def get_required_only_documents(company_id):
    """
    법인별 필수 제출 서류만 조회 API

    Args:
        company_id: 법인 ID

    Returns:
        필수 제출 서류 목록
    """
    try:
        documents = required_document_service.get_required_by_company(company_id)
        return api_success({'documents': documents})

    except Exception as e:
        current_app.logger.error(f'필수 제출 서류 조회 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 생성 API
# ========================================

@attachment_bp.route('/api/required-documents', methods=['POST'])
@api_login_required
@corporate_admin_required
def create_required_document():
    """
    필수 서류 생성 API

    Body:
        {
            "company_id": 1,
            "name": "졸업증명서",
            "category": "education",
            "description": "최종학력 졸업증명서",
            "is_required": true,
            "linked_entity_type": "education"
        }

    Returns:
        생성된 필수 서류 정보
    """
    try:
        data = request.get_json()
        if not data:
            return api_error('요청 본문이 없습니다.')

        # 필수 필드 검증
        if not data.get('company_id'):
            return api_error('company_id는 필수입니다.')
        if not data.get('name'):
            return api_error('name은 필수입니다.')

        # 생성
        document = required_document_service.create(data)
        return api_success({
            'document': document
        }, message='필수 서류가 생성되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 생성 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 수정 API
# ========================================

@attachment_bp.route('/api/required-documents/<int:doc_id>', methods=['PUT'])
@api_login_required
@corporate_admin_required
def update_required_document(doc_id):
    """
    필수 서류 수정 API

    Args:
        doc_id: 필수 서류 ID

    Body:
        {
            "name": "수정된 서류명",
            "category": "education",
            "description": "수정된 설명",
            "is_required": false,
            "linked_entity_type": "education",
            "is_active": true
        }

    Returns:
        수정된 필수 서류 정보
    """
    try:
        data = request.get_json()
        if not data:
            return api_error('요청 본문이 없습니다.')

        document = required_document_service.update(doc_id, data)
        if not document:
            return api_not_found('필수 서류')

        return api_success({
            'document': document
        }, message='필수 서류가 수정되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 수정 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 삭제 API
# ========================================

@attachment_bp.route('/api/required-documents/<int:doc_id>', methods=['DELETE'])
@api_login_required
@corporate_admin_required
def delete_required_document(doc_id):
    """
    필수 서류 삭제 API

    Args:
        doc_id: 필수 서류 ID

    Returns:
        삭제 성공 메시지
    """
    try:
        success = required_document_service.delete(doc_id)
        if not success:
            return api_not_found('필수 서류')

        return api_success(message='필수 서류가 삭제되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 삭제 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 순서 변경 API (구 버전 - company_id 경로 방식)
# ========================================

@attachment_bp.route('/api/required-documents/<int:company_id>/order', methods=['PATCH'])
@api_login_required
@corporate_admin_required
def reorder_required_documents(company_id):
    """
    필수 서류 순서 변경 API

    Args:
        company_id: 법인 ID

    Body:
        {
            "order": [3, 1, 2]  // 서류 ID 순서
        }

    Returns:
        성공 메시지
    """
    try:
        data = request.get_json()
        if not data:
            return api_error('요청 본문이 없습니다.')

        order = data.get('order', [])
        if not isinstance(order, list):
            return api_error('order는 배열이어야 합니다.')

        with atomic_transaction():
            required_document_service.reorder(company_id, order, commit=False)

        return api_success(message='순서가 변경되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 순서 변경 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 순서 변경 API (신규 버전 - body에 orders 배열 방식)
# ========================================

@attachment_bp.route('/api/required-documents/reorder', methods=['PATCH'])
@api_login_required
@corporate_admin_required
def reorder_required_documents_v2():
    """
    필수 서류 순서 변경 API (신규 버전)

    Body:
        {
            "orders": [{"id": 1, "order": 1}, {"id": 2, "order": 2}]
        }

    Returns:
        성공 메시지
    """
    try:
        data = request.get_json()
        if not data:
            return api_error('요청 본문이 없습니다.')

        orders = data.get('orders', [])
        if not isinstance(orders, list):
            return api_error('orders는 배열이어야 합니다.')

        with atomic_transaction():
            required_document_service.reorder_by_items(orders, commit=False)

        return api_success(message='순서가 변경되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 순서 변경 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 활성화/비활성화 API
# ========================================

@attachment_bp.route('/api/required-documents/<int:doc_id>/activate', methods=['PATCH'])
@api_login_required
@corporate_admin_required
def activate_required_document(doc_id):
    """
    필수 서류 활성화 API

    Args:
        doc_id: 필수 서류 ID

    Returns:
        성공 메시지
    """
    try:
        success = required_document_service.activate(doc_id)
        if not success:
            return api_not_found('필수 서류')

        return api_success(message='필수 서류가 활성화되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 활성화 실패: {e}')
        return api_server_error(str(e))


@attachment_bp.route('/api/required-documents/<int:doc_id>/deactivate', methods=['PATCH'])
@api_login_required
@corporate_admin_required
def deactivate_required_document(doc_id):
    """
    필수 서류 비활성화 API

    Args:
        doc_id: 필수 서류 ID

    Returns:
        성공 메시지
    """
    try:
        success = required_document_service.deactivate(doc_id)
        if not success:
            return api_not_found('필수 서류')

        return api_success(message='필수 서류가 비활성화되었습니다.')

    except Exception as e:
        current_app.logger.error(f'필수 서류 비활성화 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 필수 서류 제출 현황 확인 API
# ========================================

@attachment_bp.route('/api/required-documents/<int:company_id>/check/<owner_type>/<int:owner_id>', methods=['GET'])
@api_login_required
def check_document_completion(company_id, owner_type, owner_id):
    """
    필수 서류 제출 현황 확인 API

    Args:
        company_id: 법인 ID
        owner_type: 소유자 타입 (employee, profile)
        owner_id: 소유자 ID

    Returns:
        {
            "total": 전체 필수 서류 수,
            "submitted": 제출된 서류 수,
            "missing": 미제출 서류 목록,
            "completed": 제출 완료 여부
        }
    """
    try:
        result = required_document_service.check_completion(
            company_id, owner_type, owner_id
        )
        return api_success(result)

    except Exception as e:
        current_app.logger.error(f'필수 서류 제출 현황 확인 실패: {e}')
        return api_server_error(str(e))
