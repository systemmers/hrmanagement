"""
계약 관련 헬퍼 모듈

계약 세션 및 권한 관련 중복 로직을 통합합니다.
Phase 6: 백엔드 리팩토링
"""
from dataclasses import dataclass
from functools import wraps
from typing import Optional, Tuple
from flask import session, jsonify, g


@dataclass
class ContractContext:
    """계약 컨텍스트 정보"""
    user_id: Optional[int]
    account_type: Optional[str]
    company_id: Optional[int]

    @property
    def is_personal(self) -> bool:
        """개인 계정 여부"""
        return self.account_type == 'personal'

    @property
    def is_corporate(self) -> bool:
        """법인 계정 여부"""
        return self.account_type == 'corporate'

    def is_contract_party(self, contract) -> bool:
        """
        계약 당사자 여부 확인

        Args:
            contract: 계약 모델 또는 딕셔너리

        Returns:
            bool: 개인 또는 법인 당사자 여부
        """
        is_person, is_company = self.get_party_status(contract)
        return is_person or is_company

    def get_party_status(self, contract) -> Tuple[bool, bool]:
        """
        계약 당사자 상태 조회

        Args:
            contract: 계약 모델 또는 딕셔너리

        Returns:
            Tuple[bool, bool]: (개인 당사자 여부, 법인 당사자 여부)
        """
        # 딕셔너리인 경우
        if isinstance(contract, dict):
            person_user_id = contract.get('person_user_id')
            contract_company_id = contract.get('company_id')
        else:
            # 모델인 경우
            person_user_id = contract.person_user_id
            contract_company_id = contract.company_id

        is_person = person_user_id == self.user_id
        is_company = self.is_corporate and contract_company_id == self.company_id

        return is_person, is_company

    def can_approve_or_reject(self, contract) -> bool:
        """
        계약 승인/거절 권한 확인

        Args:
            contract: 계약 모델

        Returns:
            bool: 승인/거절 가능 여부
        """
        if hasattr(contract, 'requested_by'):
            if contract.requested_by == 'company':
                # 법인 요청 -> 개인이 승인/거절
                return contract.person_user_id == self.user_id
            else:
                # 개인 요청 -> 법인이 승인/거절
                return self.is_corporate and contract.company_id == self.company_id
        return False


def get_contract_context() -> ContractContext:
    """
    현재 세션의 계약 컨텍스트 조회

    요청 스코프에서 캐싱하여 중복 조회를 방지합니다.

    Returns:
        ContractContext: 현재 사용자의 계약 컨텍스트
    """
    if hasattr(g, '_contract_context'):
        return g._contract_context

    context = ContractContext(
        user_id=session.get('user_id'),
        account_type=session.get('account_type'),
        company_id=session.get('company_id')
    )
    g._contract_context = context
    return context


def check_contract_party(contract) -> Optional[Tuple]:
    """
    계약 당사자 확인 (API용)

    Args:
        contract: 계약 모델 또는 딕셔너리

    Returns:
        None: 권한 있음
        Tuple: (json_response, status_code) 권한 없을시 JSON 응답
    """
    ctx = get_contract_context()
    if not ctx.is_contract_party(contract):
        return (jsonify({'success': False, 'message': '권한이 없습니다.'}), 403)
    return None


def check_approve_reject_permission(contract) -> Optional[Tuple]:
    """
    계약 승인/거절 권한 확인 (API용)

    Args:
        contract: 계약 모델

    Returns:
        None: 권한 있음
        Tuple: (json_response, status_code) 권한 없을시 JSON 응답
    """
    ctx = get_contract_context()
    if not ctx.can_approve_or_reject(contract):
        return (jsonify({'success': False, 'message': '권한이 없습니다.'}), 403)
    return None


def contract_party_required(f):
    """
    계약 당사자 필수 데코레이터

    contract_id를 URL 파라미터로 받는 함수에서 사용합니다.
    계약 모델을 함수의 첫 번째 인자로 전달합니다.

    사용 예:
        @contract_party_required
        def api_sync_logs(contract, contract_id):
            ...
    """
    @wraps(f)
    def decorated_function(contract_id, *args, **kwargs):
        from ..extensions import person_contract_repo

        contract = person_contract_repo.get_model_by_id(contract_id)
        if not contract:
            return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

        party_check = check_contract_party(contract)
        if party_check:
            return party_check

        return f(contract, contract_id, *args, **kwargs)
    return decorated_function


def approve_reject_permission_required(f):
    """
    계약 승인/거절 권한 필수 데코레이터

    contract_id를 URL 파라미터로 받는 함수에서 사용합니다.
    계약 모델을 함수의 첫 번째 인자로 전달합니다.

    사용 예:
        @approve_reject_permission_required
        def api_approve_contract(contract, contract_id):
            ...
    """
    @wraps(f)
    def decorated_function(contract_id, *args, **kwargs):
        from ..extensions import person_contract_repo

        contract = person_contract_repo.get_model_by_id(contract_id)
        if not contract:
            return jsonify({'success': False, 'message': '계약을 찾을 수 없습니다.'}), 404

        permission_check = check_approve_reject_permission(contract)
        if permission_check:
            return permission_check

        return f(contract, contract_id, *args, **kwargs)
    return decorated_function
