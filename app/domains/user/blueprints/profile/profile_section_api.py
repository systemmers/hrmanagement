"""
Profile Section API - 개인 계정 인라인 편집 API

/api/profiles/{id}/sections/{section} 엔드포인트를 제공합니다.
employee_section_api.py와 동일한 패턴으로 개인 계정의 인라인 편집을 지원합니다.

Phase 1: 개인 계정 인라인 편집 API 구현
- 정적 섹션: personal, military
- 동적 섹션: educations, careers, certificates, languages
"""
from flask import Blueprint, request, session, g
from app.shared.utils.decorators import api_login_required
from app.shared.utils.api_helpers import api_success, api_error, api_not_found, api_forbidden, api_server_error
from app.shared.utils.transaction import atomic_transaction
from app.shared.constants.session_keys import SessionKeys, AccountType
from app.domains.user.services.personal_service import personal_service
from app.domains.employee.services.profile_relation_service import profile_relation_service


# Blueprint 정의
profile_section_api_bp = Blueprint('profile_section_api', __name__, url_prefix='/api/profiles')


# ========================================
# 섹션 설정
# ========================================

# 프론트엔드 필드명 → 모델 필드명 매핑
# NOTE: hobby, specialty는 모델과 동일한 이름을 사용하므로 매핑 불필요
FIELD_NAME_MAPPING = {
    # 기본 정보 (Phase 0.7: is_lunar_birth는 이제 DB 필드명과 동일)
    # 'is_lunar_birth': 'is_lunar_birth',  # 동일하므로 매핑 불필요
    'resident_registration_number': 'resident_number',
    'zipcode': 'postal_code',
    # 비상연락처
    'emergency_contact_relationship': 'emergency_relation',
    # 주소
    'registered_address': 'address',
    'registered_address_detail': 'detailed_address',
    'actual_address_detail': 'actual_detailed_address',
    # camelCase → snake_case 매핑 (프론트엔드 호환)
    'phone': 'mobile_phone',  # 템플릿 input name="phone"
    'mobilePhone': 'mobile_phone',
    'homePhone': 'home_phone',
    'englishName': 'english_name',
    'chineseName': 'chinese_name',
    'foreignName': 'foreign_name',
    'maritalStatus': 'marital_status',
    'birthDate': 'birth_date',
    'isLunarBirth': 'is_lunar_birth',
    'emergencyContact': 'emergency_contact',
    'emergencyRelation': 'emergency_relation',
    'bankName': 'bank_name',
    'accountNumber': 'account_number',
    'accountHolder': 'account_holder',
    'disabilityInfo': 'disability_info',
    'detailedAddress': 'detailed_address',
    'actualPostalCode': 'actual_postal_code',
    'actualAddress': 'actual_address',
    'actualDetailedAddress': 'actual_detailed_address',
    'postalCode': 'postal_code',
    'residentNumber': 'resident_number',
    'residentRegistrationNumber': 'resident_number',
}

# 정적 섹션 (info-table)
STATIC_SECTIONS = {
    'personal': {
        'name': '개인 기본정보',
        'fields': [
            # 기본 정보
            'name', 'english_name', 'chinese_name', 'foreign_name',
            'birth_date', 'is_lunar_birth', 'gender', 'nationality',
            'resident_registration_number', 'zipcode',
            # 결혼/연락처
            'marital_status', 'mobile_phone', 'home_phone', 'email',
            'emergency_contact', 'emergency_contact_relationship',
            # 계좌/취미 (모델 필드명: hobby, specialty)
            'bank_name', 'account_number', 'account_holder',
            'hobby', 'specialty', 'disability_info',
            # 주소
            'registered_address', 'registered_address_detail',
            'actual_address', 'actual_address_detail'
            # NOTE: 'age'는 계산된 속성(computed property)이므로 제외
        ]
    },
    'military': {
        'name': '병역정보',
        'fields': [
            'military_status', 'military_branch', 'military_rank',
            'military_start_date', 'military_end_date',
            'military_specialty', 'military_exemption_reason'
        ]
    }
}

# 동적 섹션 (테이블 - CRUD)
DYNAMIC_SECTIONS = {
    'educations': {
        'name': '학력정보',
        'service_methods': {
            'list': 'get_educations',
            'add': 'add_education',
            'delete': 'delete_education',
            'delete_all': 'delete_all_educations'
        }
    },
    'careers': {
        'name': '경력정보',
        'service_methods': {
            'list': 'get_careers',
            'add': 'add_career',
            'delete': 'delete_career',
            'delete_all': 'delete_all_careers'
        }
    },
    'certificates': {
        'name': '자격증',
        'service_methods': {
            'list': 'get_certificates',
            'add': 'add_certificate',
            'delete': 'delete_certificate',
            'delete_all': 'delete_all_certificates'
        }
    },
    'languages': {
        'name': '언어능력',
        'service_methods': {
            'list': 'get_languages',
            'add': 'add_language',
            'delete': 'delete_language',
            'delete_all': 'delete_all_languages'
        }
    },
    'military': {
        'name': '병역정보',
        'service_methods': {
            'list': 'get_military_list',
            'add': 'add_military',
            'delete': 'delete_military',
            'delete_all': 'delete_all_military'
        }
    }
}


# ========================================
# 헬퍼 함수
# ========================================

def _map_field_names(data: dict) -> dict:
    """
    프론트엔드 필드명을 모델 필드명으로 변환

    Args:
        data: 프론트엔드에서 전송된 데이터

    Returns:
        모델 필드명으로 변환된 데이터
    """
    mapped_data = {}
    for key, value in data.items():
        # 매핑 테이블에 있으면 변환, 없으면 그대로 사용
        model_field = FIELD_NAME_MAPPING.get(key, key)
        mapped_data[model_field] = value
    return mapped_data


def _verify_profile_access(profile_id: int) -> tuple:
    """
    프로필 접근 권한 확인

    Returns:
        (success, error_response, profile)
    """
    user_id = session.get(SessionKeys.USER_ID)
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)

    if not user_id:
        return False, api_forbidden('로그인이 필요합니다.'), None

    # personal 계정만 허용
    if account_type != AccountType.PERSONAL:
        return False, api_forbidden('개인 계정만 접근할 수 있습니다.'), None

    # 프로필 소유권 확인
    user, profile = personal_service.get_user_with_profile(user_id)

    if not profile:
        return False, api_not_found('프로필'), None

    if profile.id != profile_id:
        return False, api_forbidden('접근 권한이 없습니다.'), None

    return True, None, profile


# ========================================
# 정적 섹션 API - PATCH (부분 수정)
# ========================================

@profile_section_api_bp.route('/<int:profile_id>/sections/<section_name>', methods=['PATCH'])
@api_login_required
def update_static_section(profile_id: int, section_name: str):
    """
    정적 섹션 부분 수정

    Args:
        profile_id: 프로필 ID
        section_name: 섹션 이름 (personal, military)

    Request Body:
        JSON 형식의 수정할 필드들

    Returns:
        성공: {"success": true, "data": {...}, "message": "..."}
        실패: {"success": false, "error": "..."}
    """
    # 권한 확인
    success, error, profile = _verify_profile_access(profile_id)
    if not success:
        return error

    # 섹션 유효성 확인
    if section_name not in STATIC_SECTIONS:
        return api_not_found(f'섹션 ({section_name})')

    section_config = STATIC_SECTIONS[section_name]
    data = request.get_json()

    if not data:
        return api_error('수정할 데이터가 없습니다.')

    # BUG-001/003 수정: 매핑 먼저, 필터링 나중
    # 1. 먼저 필드명 매핑 수행 (camelCase → snake_case)
    mapped_data = _map_field_names(data)

    # 2. 매핑된 데이터에서 허용 필드만 필터링
    allowed_fields = set(section_config['fields'])
    filtered_data = {k: v for k, v in mapped_data.items() if k in allowed_fields}

    if not filtered_data:
        return api_error('수정 가능한 필드가 없습니다.')

    try:
        user_id = session.get(SessionKeys.USER_ID)

        if section_name == 'personal':
            # 개인 기본정보 수정 (이미 매핑된 데이터 사용)
            result = personal_service.update_profile(user_id, filtered_data)
            if not result.success:
                return api_error(result.message)
            return api_success({
                'data': result.data,
                'message': f'{section_config["name"]} 저장 완료'
            })

        elif section_name == 'military':
            # 병역정보 수정 (upsert)
            result = personal_service.save_military(profile_id, filtered_data)
            return api_success({
                'data': result,
                'message': f'{section_config["name"]} 저장 완료'
            })

    except Exception as e:
        return api_server_error(f'저장 중 오류: {str(e)}')


# ========================================
# 동적 섹션 API - GET (목록 조회)
# ========================================

@profile_section_api_bp.route('/<int:profile_id>/sections/<section_name>', methods=['GET'])
@api_login_required
def get_dynamic_section(profile_id: int, section_name: str):
    """
    동적 섹션 목록 조회

    Args:
        profile_id: 프로필 ID
        section_name: 섹션 이름 (educations, careers, certificates, languages, military)

    Returns:
        성공: {"success": true, "data": [...]}
        실패: {"success": false, "error": "..."}
    """
    # 권한 확인
    success, error, profile = _verify_profile_access(profile_id)
    if not success:
        return error

    # 섹션 유효성 확인
    if section_name not in DYNAMIC_SECTIONS:
        return api_not_found(f'섹션 ({section_name})')

    section_config = DYNAMIC_SECTIONS[section_name]
    list_method = section_config['service_methods']['list']

    try:
        # 서비스 메서드 호출
        method = getattr(personal_service, list_method, None)
        if not method:
            return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {list_method}')

        data = method(profile_id)
        return api_success({'data': data})

    except Exception as e:
        return api_server_error(f'조회 중 오류: {str(e)}')


# ========================================
# 동적 섹션 API - POST (항목 추가)
# ========================================

@profile_section_api_bp.route('/<int:profile_id>/sections/<section_name>', methods=['POST'])
@api_login_required
def add_dynamic_item(profile_id: int, section_name: str):
    """
    동적 섹션 항목 추가

    Args:
        profile_id: 프로필 ID
        section_name: 섹션 이름 (educations, careers, certificates, languages, military)

    Request Body:
        JSON 형식의 추가할 데이터

    Returns:
        성공: {"success": true, "data": {...}, "message": "..."}
        실패: {"success": false, "error": "..."}
    """
    # 권한 확인
    success, error, profile = _verify_profile_access(profile_id)
    if not success:
        return error

    # 섹션 유효성 확인
    if section_name not in DYNAMIC_SECTIONS:
        return api_not_found(f'섹션 ({section_name})')

    section_config = DYNAMIC_SECTIONS[section_name]
    add_method = section_config['service_methods']['add']
    data = request.get_json()

    if not data:
        return api_error('추가할 데이터가 없습니다.')

    try:
        # 서비스 메서드 호출
        method = getattr(personal_service, add_method, None)
        if not method:
            return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {add_method}')

        result = method(profile_id, data)
        return api_success({
            'data': result,
            'message': f'{section_config["name"]} 추가 완료'
        }), 201

    except Exception as e:
        return api_server_error(f'추가 중 오류: {str(e)}')


# ========================================
# 동적 섹션 API - DELETE (항목 삭제)
# ========================================

@profile_section_api_bp.route('/<int:profile_id>/sections/<section_name>/<int:item_id>', methods=['DELETE'])
@api_login_required
def delete_dynamic_item(profile_id: int, section_name: str, item_id: int):
    """
    동적 섹션 항목 삭제

    Args:
        profile_id: 프로필 ID
        section_name: 섹션 이름 (educations, careers, certificates, languages, military)
        item_id: 삭제할 항목 ID

    Returns:
        성공: {"success": true, "message": "..."}
        실패: {"success": false, "error": "..."}
    """
    # 권한 확인
    success, error, profile = _verify_profile_access(profile_id)
    if not success:
        return error

    # 섹션 유효성 확인
    if section_name not in DYNAMIC_SECTIONS:
        return api_not_found(f'섹션 ({section_name})')

    section_config = DYNAMIC_SECTIONS[section_name]
    delete_method = section_config['service_methods']['delete']

    try:
        # 서비스 메서드 호출
        method = getattr(personal_service, delete_method, None)
        if not method:
            return api_server_error(f'서비스 메서드를 찾을 수 없습니다: {delete_method}')

        result = method(item_id, profile_id)

        if result:
            return api_success({
                'message': f'{section_config["name"]} 삭제 완료'
            })
        else:
            return api_error('삭제할 항목을 찾을 수 없거나 권한이 없습니다.')

    except Exception as e:
        return api_server_error(f'삭제 중 오류: {str(e)}')


# ========================================
# 동적 섹션 API - PATCH (항목 수정)
# ========================================

@profile_section_api_bp.route('/<int:profile_id>/sections/<section_name>/<int:item_id>', methods=['PATCH'])
@api_login_required
def update_dynamic_item(profile_id: int, section_name: str, item_id: int):
    """
    동적 섹션 항목 수정

    Args:
        profile_id: 프로필 ID
        section_name: 섹션 이름 (educations, careers, certificates, languages, military)
        item_id: 수정할 항목 ID

    Request Body:
        JSON 형식의 수정할 필드들

    Returns:
        성공: {"success": true, "data": {...}, "message": "..."}
        실패: {"success": false, "error": "..."}
    """
    # 권한 확인
    success, error, profile = _verify_profile_access(profile_id)
    if not success:
        return error

    # 섹션 유효성 확인
    if section_name not in DYNAMIC_SECTIONS:
        return api_not_found(f'섹션 ({section_name})')

    section_config = DYNAMIC_SECTIONS[section_name]
    data = request.get_json()

    if not data:
        return api_error('수정할 데이터가 없습니다.')

    try:
        # profile_relation_service의 update 메서드 사용
        # section_name에서 단수형 추출 (educations -> education)
        relation_type = section_name.rstrip('s') if section_name.endswith('s') else section_name
        if section_name == 'military':
            relation_type = 'military'

        # profile_relation_service를 통한 업데이트
        update_method = getattr(profile_relation_service, f'update_{relation_type}', None)

        if update_method:
            result = update_method(item_id, data, profile_id, 'profile')
            if result:
                return api_success({
                    'data': result,
                    'message': f'{section_config["name"]} 수정 완료'
                })
            else:
                return api_error('수정할 항목을 찾을 수 없거나 권한이 없습니다.')
        else:
            # Fallback: 삭제 후 재추가 (update 메서드가 없는 경우)
            delete_method = section_config['service_methods']['delete']
            add_method = section_config['service_methods']['add']

            del_func = getattr(personal_service, delete_method, None)
            add_func = getattr(personal_service, add_method, None)

            if del_func and add_func:
                with atomic_transaction():
                    del_func(item_id, profile_id)
                    result = add_func(profile_id, data)

                return api_success({
                    'data': result,
                    'message': f'{section_config["name"]} 수정 완료'
                })
            else:
                return api_server_error('업데이트 메서드를 찾을 수 없습니다.')

    except Exception as e:
        return api_server_error(f'수정 중 오류: {str(e)}')
