"""
직원 섹션 인라인 편집 API

Phase 0.4: 섹션별 PATCH API
- 정적 섹션 (personal, organization, contract, salary, benefit, attendance, account)
- 동적 섹션 (families, educations, careers, certificates, languages, awards 등)

API 엔드포인트:
- PATCH /api/employees/<id>/sections/<section> - 정적 섹션 수정
- GET /api/employees/<id>/<relation> - 동적 섹션 목록
- POST /api/employees/<id>/<relation> - 동적 섹션 항목 추가
- PATCH /api/employees/<id>/<relation>/<item_id> - 동적 섹션 항목 수정
- DELETE /api/employees/<id>/<relation>/<item_id> - 동적 섹션 항목 삭제
"""
from flask import Blueprint, request, session

from app.shared.constants.session_keys import SessionKeys, UserRole, AccountType
from app.shared.utils.decorators import api_login_required
from app.shared.utils.api_helpers import (
    api_success, api_error, api_not_found, api_forbidden, api_server_error,
    api_validation_error
)
from app.shared.utils.transaction import atomic_transaction
from app.domains.employee.services import employee_service, inline_edit_service, validation_service


# ========================================
# 정적 섹션 설정
# ========================================

STATIC_SECTIONS = {
    'personal': {
        'name': '개인 기본정보',
        'update_method': 'update_personal_info'
    },
    'organization': {
        'name': '소속정보',
        'update_method': 'update_organization_info'
    },
    'contract': {
        'name': '계약정보',
        'update_method': 'update_contract_info',
        'readonly_fields': ['contract_type', 'contract_start', 'contract_end']
    },
    'salary': {
        'name': '급여정보',
        'update_method': 'update_salary_info'
    },
    'benefit': {
        'name': '연차 및 복리후생',
        'update_method': 'update_benefit_info'
    },
    'attendance': {
        'name': '근태현황',
        'update_method': 'update_attendance_info'
    },
    'account': {
        'name': '계정정보',
        'update_method': 'update_account_info'
    }
}

# ========================================
# 동적 섹션 (릴레이션) 설정
# ========================================

DYNAMIC_SECTIONS = {
    # 이력 정보 - Phase 8-13
    'families': {
        'name': '가족정보',
        'list_method': 'get_family_list',
        'get_method': 'get_family_by_id',
        'create_method': 'create_family',
        'update_method': 'update_family',
        'delete_method': 'delete_family',
        'protected': True  # 개인계약 연동 보호
    },
    'educations': {
        'name': '학력정보',
        'list_method': 'get_education_list',
        'get_method': 'get_education_by_id',
        'create_method': 'create_education',
        'update_method': 'update_education',
        'delete_method': 'delete_education',
        'protected': True
    },
    'careers': {
        'name': '경력정보',
        'list_method': 'get_career_list',
        'get_method': 'get_career_by_id',
        'create_method': 'create_career',
        'update_method': 'update_career',
        'delete_method': 'delete_career',
        'protected': True
    },
    'certificates': {
        'name': '자격증',
        'list_method': 'get_certificate_list',
        'get_method': 'get_certificate_by_id',
        'create_method': 'create_certificate',
        'update_method': 'update_certificate',
        'delete_method': 'delete_certificate',
        'protected': True
    },
    'languages': {
        'name': '언어능력',
        'list_method': 'get_language_list',
        'get_method': 'get_language_by_id',
        'create_method': 'create_language',
        'update_method': 'update_language',
        'delete_method': 'delete_language',
        'protected': True
    },
    'awards': {
        'name': '수상내역',
        'list_method': 'get_award_list',
        'get_method': 'get_award_by_id',
        'create_method': 'create_award',
        'update_method': 'update_award',
        'delete_method': 'delete_award',
        'protected': True
    },
    'projects': {
        'name': '프로젝트 참여',
        'list_method': 'get_project_list',
        'get_method': 'get_project_by_id',
        'create_method': 'create_project',
        'update_method': 'update_project',
        'delete_method': 'delete_project',
        'protected': False
    },
    # HR 릴레이션 - Phase 14-21
    'employment-contracts': {
        'name': '근로계약 이력',
        'list_method': 'get_employment_contract_list',
        'get_method': 'get_employment_contract_by_id',
        'create_method': 'create_employment_contract',
        'update_method': 'update_employment_contract',
        'delete_method': 'delete_employment_contract',
        'protected': False
    },
    'salary-histories': {
        'name': '연봉계약 이력',
        'list_method': 'get_salary_history_list',
        'get_method': 'get_salary_history_by_id',
        'create_method': 'create_salary_history',
        'update_method': 'update_salary_history',
        'delete_method': 'delete_salary_history',
        'protected': False
    },
    'salary-payments': {
        'name': '급여 지급 이력',
        'list_method': 'get_salary_payment_list',
        'get_method': 'get_salary_payment_by_id',
        'create_method': 'create_salary_payment',
        'update_method': 'update_salary_payment',
        'delete_method': 'delete_salary_payment',
        'protected': False
    },
    'promotions': {
        'name': '인사이동/승진',
        'list_method': 'get_promotion_list',
        'get_method': 'get_promotion_by_id',
        'create_method': 'create_promotion',
        'update_method': 'update_promotion',
        'delete_method': 'delete_promotion',
        'protected': False
    },
    'evaluations': {
        'name': '인사고과',
        'list_method': 'get_evaluation_list',
        'get_method': 'get_evaluation_by_id',
        'create_method': 'create_evaluation',
        'update_method': 'update_evaluation',
        'delete_method': 'delete_evaluation',
        'protected': False
    },
    'trainings': {
        'name': '교육훈련',
        'list_method': 'get_training_list',
        'get_method': 'get_training_by_id',
        'create_method': 'create_training',
        'update_method': 'update_training',
        'delete_method': 'delete_training',
        'protected': False
    },
    'hr-projects': {
        'name': 'HR 프로젝트',
        'list_method': 'get_hr_project_list',
        'get_method': 'get_hr_project_by_id',
        'create_method': 'create_hr_project',
        'update_method': 'update_hr_project',
        'delete_method': 'delete_hr_project',
        'protected': False
    },
    'assets': {
        'name': '비품지급',
        'list_method': 'get_asset_list',
        'get_method': 'get_asset_by_id',
        'create_method': 'create_asset',
        'update_method': 'update_asset',
        'delete_method': 'delete_asset',
        'protected': False
    }
}

# 개인계약 연동 보호 섹션
PROTECTED_SECTIONS = [key for key, config in DYNAMIC_SECTIONS.items() if config.get('protected')]


def register_section_api_routes(bp: Blueprint):
    """섹션 API 라우트를 Blueprint에 등록"""

    # ========================================
    # 권한 검사 헬퍼
    # ========================================

    def _check_employee_access(employee_id: int) -> tuple:
        """
        직원 접근 권한 확인

        Returns:
            (employee, error_response): employee 또는 에러 응답
        """
        employee = employee_service.get_employee_by_id(employee_id)
        if not employee:
            return None, api_not_found('직원')

        account_type = session.get(SessionKeys.ACCOUNT_TYPE)
        user_role = session.get(SessionKeys.USER_ROLE)
        company_id = session.get(SessionKeys.COMPANY_ID)
        current_employee_id = session.get(SessionKeys.EMPLOYEE_ID)

        # employee_sub: 본인만 접근 가능
        if account_type == AccountType.EMPLOYEE_SUB:
            if current_employee_id != employee_id:
                return None, api_forbidden('본인의 정보만 수정할 수 있습니다.')
            return employee, None

        # corporate: 자사 직원만 접근 가능
        if account_type == AccountType.CORPORATE:
            if employee.get('company_id') != company_id:
                return None, api_forbidden('자사 직원의 정보만 수정할 수 있습니다.')

            # manager/admin만 수정 가능
            if user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
                return None, api_forbidden('관리자만 수정할 수 있습니다.')

            return employee, None

        # personal: employee 엔드포인트 접근 불가
        return None, api_forbidden('접근 권한이 없습니다.')

    def _is_section_protected(employee_id: int, section: str) -> bool:
        """
        개인계약 연동으로 보호된 섹션인지 확인

        개인계약이 승인된 직원의 경우 법인에서 이력 정보 수정 불가
        """
        if section not in PROTECTED_SECTIONS:
            return False

        account_type = session.get(SessionKeys.ACCOUNT_TYPE)

        # employee_sub는 본인 데이터 수정 가능
        if account_type == AccountType.EMPLOYEE_SUB:
            return False

        # corporate에서 수정 시도 시 개인계약 확인
        from app.domains.user.services import user_employee_link_service
        company_id = session.get(SessionKeys.COMPANY_ID)

        return user_employee_link_service.has_approved_personal_contract(
            employee_id, company_id
        )

    # ========================================
    # 정적 섹션 API
    # ========================================

    @bp.route('/api/employees/<int:employee_id>/sections/<section>', methods=['PATCH'])
    @api_login_required
    def update_section(employee_id: int, section: str):
        """
        정적 섹션 PATCH API

        요청: { "field1": "value1", "field2": "value2" }
        응답: { "success": true, "data": {...}, "message": "저장되었습니다." }
        """
        # 섹션 유효성 확인
        config = STATIC_SECTIONS.get(section)
        if not config:
            return api_error(f'알 수 없는 섹션입니다: {section}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        try:
            data = request.get_json()
            if not data:
                return api_error('요청 데이터가 없습니다.', status_code=400)

            # readonly 필드 제거
            readonly_fields = config.get('readonly_fields', [])
            for field in readonly_fields:
                data.pop(field, None)

            # 유효성 검사
            validation_errors = validation_service.validate_section(section, data)
            if validation_errors:
                return api_validation_error(validation_errors)

            # inline_edit_service 사용하여 업데이트
            result = inline_edit_service.update_section(employee_id, section, data)

            if not result.success:
                # 에러 코드에 따른 HTTP 상태 코드 매핑
                status_map = {
                    'NOT_FOUND': 404,
                    'FORBIDDEN': 403,
                    'VALIDATION_ERROR': 422,
                    'INVALID_SECTION': 400,
                }
                status_code = status_map.get(result.error_code, 422)
                return api_error(result.message, status_code=status_code)

            return api_success(
                data=result.data,
                message=result.message or f'{config["name"]}이(가) 저장되었습니다.'
            )

        except Exception as e:
            return api_server_error(str(e))

    # ========================================
    # 동적 섹션 (릴레이션) API
    # ========================================

    @bp.route('/api/employees/<int:employee_id>/sections/<relation>', methods=['GET'])
    @api_login_required
    def get_relation_list(employee_id: int, relation: str):
        """동적 섹션 목록 조회"""
        config = DYNAMIC_SECTIONS.get(relation)
        if not config:
            return api_error(f'알 수 없는 릴레이션입니다: {relation}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        try:
            list_method = getattr(employee_service.relation_service, config['list_method'], None)
            if not list_method:
                return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {config["list_method"]}')

            items = list_method(employee_id)
            return api_success({relation: items})

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/sections/<relation>', methods=['POST'])
    @api_login_required
    def create_relation_item(employee_id: int, relation: str):
        """동적 섹션 항목 추가"""
        config = DYNAMIC_SECTIONS.get(relation)
        if not config:
            return api_error(f'알 수 없는 릴레이션입니다: {relation}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        # 보호 섹션 확인
        if _is_section_protected(employee_id, relation):
            return api_forbidden(
                f'{config["name"]}은(는) 개인계약 연동으로 보호되어 수정할 수 없습니다.'
            )

        try:
            data = request.get_json()
            if not data:
                return api_error('요청 데이터가 없습니다.', status_code=400)

            create_method = getattr(employee_service.relation_service, config['create_method'], None)
            if not create_method:
                return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {config["create_method"]}')

            with atomic_transaction():
                result = create_method(employee_id, data, commit=False)

            return api_success(
                data=result,
                message=f'{config["name"]}이(가) 추가되었습니다.',
                status_code=201
            )

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/sections/<relation>/<int:item_id>', methods=['GET'])
    @api_login_required
    def get_relation_item(employee_id: int, relation: str, item_id: int):
        """동적 섹션 항목 단건 조회"""
        config = DYNAMIC_SECTIONS.get(relation)
        if not config:
            return api_error(f'알 수 없는 릴레이션입니다: {relation}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        try:
            get_method = getattr(employee_service.relation_service, config['get_method'], None)
            if not get_method:
                return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {config["get_method"]}')

            item = get_method(item_id, employee_id)
            if not item:
                return api_not_found(config['name'])

            return api_success(data=item)

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/sections/<relation>/<int:item_id>', methods=['PATCH'])
    @api_login_required
    def update_relation_item(employee_id: int, relation: str, item_id: int):
        """동적 섹션 항목 수정"""
        config = DYNAMIC_SECTIONS.get(relation)
        if not config:
            return api_error(f'알 수 없는 릴레이션입니다: {relation}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        # 보호 섹션 확인
        if _is_section_protected(employee_id, relation):
            return api_forbidden(
                f'{config["name"]}은(는) 개인계약 연동으로 보호되어 수정할 수 없습니다.'
            )

        try:
            data = request.get_json()
            if not data:
                return api_error('요청 데이터가 없습니다.', status_code=400)

            update_method = getattr(employee_service.relation_service, config['update_method'], None)
            if not update_method:
                return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {config["update_method"]}')

            with atomic_transaction():
                success, error_msg = update_method(item_id, data, employee_id, commit=False)

            if not success:
                return api_error(error_msg or '수정에 실패했습니다.', status_code=422)

            return api_success(message=f'{config["name"]}이(가) 수정되었습니다.')

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/sections/<relation>/<int:item_id>', methods=['DELETE'])
    @api_login_required
    def delete_relation_item(employee_id: int, relation: str, item_id: int):
        """동적 섹션 항목 삭제"""
        config = DYNAMIC_SECTIONS.get(relation)
        if not config:
            return api_error(f'알 수 없는 릴레이션입니다: {relation}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        # 보호 섹션 확인
        if _is_section_protected(employee_id, relation):
            return api_forbidden(
                f'{config["name"]}은(는) 개인계약 연동으로 보호되어 삭제할 수 없습니다.'
            )

        try:
            delete_method = getattr(employee_service.relation_service, config['delete_method'], None)
            if not delete_method:
                return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {config["delete_method"]}')

            with atomic_transaction():
                success = delete_method(item_id, employee_id, commit=False)

            if not success:
                return api_not_found(config['name'])

            return api_success(message=f'{config["name"]}이(가) 삭제되었습니다.')

        except Exception as e:
            return api_server_error(str(e))

    # ========================================
    # 순서 변경 API (드래그 앤 드롭)
    # ========================================

    @bp.route('/api/employees/<int:employee_id>/sections/<relation>/order', methods=['PATCH'])
    @api_login_required
    def update_relation_order(employee_id: int, relation: str):
        """동적 섹션 항목 순서 변경"""
        config = DYNAMIC_SECTIONS.get(relation)
        if not config:
            return api_error(f'알 수 없는 릴레이션입니다: {relation}', status_code=400)

        # 권한 확인
        employee, error = _check_employee_access(employee_id)
        if error:
            return error

        # 보호 섹션 확인
        if _is_section_protected(employee_id, relation):
            return api_forbidden(
                f'{config["name"]}은(는) 개인계약 연동으로 보호되어 수정할 수 없습니다.'
            )

        try:
            data = request.get_json()
            if not data or 'order' not in data:
                return api_error('order 데이터가 필요합니다.', status_code=400)

            # order: [id1, id2, id3, ...] 순서대로 정렬
            order_list = data['order']
            if not isinstance(order_list, list):
                return api_error('order는 배열이어야 합니다.', status_code=400)

            # 순서 업데이트 메서드 호출 (있는 경우)
            order_method_name = f'update_{relation.replace("-", "_")}_order'
            order_method = getattr(employee_service.relation_service, order_method_name, None)

            if not order_method:
                return api_error('순서 변경이 지원되지 않는 섹션입니다.', status_code=400)

            with atomic_transaction():
                success = order_method(employee_id, order_list, commit=False)

            if not success:
                return api_error('순서 변경에 실패했습니다.', status_code=422)

            return api_success(message=f'{config["name"]} 순서가 변경되었습니다.')

        except Exception as e:
            return api_server_error(str(e))
