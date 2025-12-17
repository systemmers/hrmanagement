"""
법인 세팅 API Blueprint

법인별 조직구조, 패턴규칙, 노출설정 API를 제공합니다.
"""
import os
from flask import Blueprint, jsonify, request, session, send_file

from app.models import ClassificationOption
from app.services.file_storage_service import file_storage
from app.repositories import (
    ClassificationOptionsRepository,
    CompanySettingsRepository,
    NumberCategoryRepository,
    CompanyVisibilityRepository,
    CompanyDocumentRepository
)
from app.utils.decorators import corporate_admin_required, api_login_required

corporate_settings_api_bp = Blueprint('corporate_settings_api', __name__, url_prefix='/api/corporate')

# Repository instances
classification_repo = ClassificationOptionsRepository()
settings_repo = CompanySettingsRepository()
number_category_repo = NumberCategoryRepository()
visibility_repo = CompanyVisibilityRepository()
document_repo = CompanyDocumentRepository()


def get_company_id():
    """세션에서 company_id 조회"""
    return session.get('company_id')


# ===== 분류 옵션 (조직 구조) API =====

@corporate_settings_api_bp.route('/classifications', methods=['GET'])
@corporate_admin_required
def get_all_classifications():
    """모든 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    options = classification_repo.get_all_options(company_id)
    return jsonify(options)


@corporate_settings_api_bp.route('/classifications/organization', methods=['GET'])
@corporate_admin_required
def get_organization_classifications():
    """조직 구조 탭용 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    options = classification_repo.get_organization_options(company_id)
    return jsonify(options)


@corporate_settings_api_bp.route('/classifications/employment', methods=['GET'])
@corporate_admin_required
def get_employment_classifications():
    """고용 정책 탭용 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    options = classification_repo.get_employment_options(company_id)
    return jsonify(options)


@corporate_settings_api_bp.route('/classifications/<category>', methods=['GET'])
@corporate_admin_required
def get_classifications_by_category(category):
    """카테고리별 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    if category not in ClassificationOption.VALID_CATEGORIES:
        return jsonify({'error': '유효하지 않은 카테고리입니다.'}), 400

    options = classification_repo.get_by_category_for_company(category, company_id)
    return jsonify({
        'category': category,
        'categoryLabel': ClassificationOption.get_category_label(category),
        'options': options
    })


@corporate_settings_api_bp.route('/classifications/<category>', methods=['POST'])
@corporate_admin_required
def add_classification(category):
    """분류 옵션 추가"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    if category not in ClassificationOption.VALID_CATEGORIES:
        return jsonify({'error': '유효하지 않은 카테고리입니다.'}), 400

    data = request.get_json()
    value = data.get('value', '').strip()
    label = data.get('label', '').strip()

    if not value:
        return jsonify({'error': '값을 입력해주세요.'}), 400

    result = classification_repo.add_option_for_company(
        company_id=company_id,
        category=category,
        value=value,
        label=label or value
    )

    return jsonify(result), 201


@corporate_settings_api_bp.route('/classifications/<category>/<int:option_id>', methods=['PUT'])
@corporate_admin_required
def update_classification(category, option_id):
    """분류 옵션 수정"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    result = classification_repo.update_option(option_id, company_id, data)

    if not result:
        return jsonify({'error': '옵션을 찾을 수 없거나 수정할 수 없습니다.'}), 404

    return jsonify(result)


@corporate_settings_api_bp.route('/classifications/<category>/<int:option_id>', methods=['DELETE'])
@corporate_admin_required
def delete_classification(category, option_id):
    """분류 옵션 삭제"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    success = classification_repo.delete_option_for_company(option_id, company_id)

    if not success:
        return jsonify({'error': '옵션을 찾을 수 없거나 삭제할 수 없습니다.'}), 404

    return jsonify({'success': True, 'message': '옵션이 삭제되었습니다.'})


@corporate_settings_api_bp.route('/classifications/<category>/toggle', methods=['POST'])
@corporate_admin_required
def toggle_system_classification(category):
    """시스템 옵션 활성화/비활성화 토글"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    value = data.get('value')
    is_active = data.get('isActive', True)

    if not value:
        return jsonify({'error': '값을 입력해주세요.'}), 400

    result = classification_repo.toggle_system_option(company_id, category, value, is_active)

    return jsonify({'success': True, 'result': result})


# ===== 법인 설정 API =====

@corporate_settings_api_bp.route('/settings', methods=['GET'])
@corporate_admin_required
def get_settings():
    """법인 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = settings_repo.get_by_company(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/settings', methods=['PUT'])
@corporate_admin_required
def update_settings():
    """법인 설정 저장"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()

    # 키-값 쌍 저장
    results = settings_repo.set_bulk_settings(company_id, data)

    return jsonify({'success': True, 'updated': len(results)})


@corporate_settings_api_bp.route('/settings/<key>', methods=['GET'])
@corporate_admin_required
def get_setting(key):
    """단일 설정값 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    value = settings_repo.get_setting(company_id, key)
    return jsonify({'key': key, 'value': value})


@corporate_settings_api_bp.route('/settings/<key>', methods=['PUT'])
@corporate_admin_required
def set_setting(key):
    """단일 설정값 저장"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    value = data.get('value')

    result = settings_repo.set_setting(company_id, key, value)
    return jsonify(result)


@corporate_settings_api_bp.route('/settings/employee-number', methods=['GET'])
@corporate_admin_required
def get_employee_number_settings():
    """사번 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = settings_repo.get_employee_number_settings(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/settings/payroll', methods=['GET'])
@corporate_admin_required
def get_payroll_settings():
    """급여 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = settings_repo.get_payroll_settings(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/settings/initialize', methods=['POST'])
@corporate_admin_required
def initialize_settings():
    """기본 설정값 초기화"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    results = settings_repo.initialize_defaults(company_id)
    return jsonify({'success': True, 'initialized': len(results)})


# ===== 번호 카테고리 API =====

@corporate_settings_api_bp.route('/number-categories', methods=['GET'])
@corporate_admin_required
def get_number_categories():
    """번호 분류코드 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    type_filter = request.args.get('type')
    categories = number_category_repo.get_by_company(company_id, type_filter)
    return jsonify(categories)


@corporate_settings_api_bp.route('/number-categories/employee', methods=['GET'])
@corporate_admin_required
def get_employee_number_categories():
    """사번 분류코드 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    categories = number_category_repo.get_employee_categories(company_id)
    return jsonify(categories)


@corporate_settings_api_bp.route('/number-categories/asset', methods=['GET'])
@corporate_admin_required
def get_asset_number_categories():
    """자산번호 분류코드 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    categories = number_category_repo.get_asset_categories(company_id)
    return jsonify(categories)


@corporate_settings_api_bp.route('/number-categories', methods=['POST'])
@corporate_admin_required
def create_number_category():
    """번호 분류코드 생성"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    type_code = data.get('type')
    code = data.get('code', '').strip()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not type_code or not code or not name:
        return jsonify({'error': '타입, 코드, 이름은 필수입니다.'}), 400

    result = number_category_repo.create_category(
        company_id=company_id,
        type_code=type_code,
        code=code,
        name=name,
        description=description
    )

    return jsonify(result), 201


@corporate_settings_api_bp.route('/number-categories/<int:category_id>', methods=['PUT'])
@corporate_admin_required
def update_number_category(category_id):
    """번호 분류코드 수정"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    result = number_category_repo.update_category(category_id, company_id, data)

    if not result:
        return jsonify({'error': '분류코드를 찾을 수 없습니다.'}), 404

    return jsonify(result)


@corporate_settings_api_bp.route('/number-categories/<int:category_id>', methods=['DELETE'])
@corporate_admin_required
def delete_number_category(category_id):
    """번호 분류코드 삭제"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    success = number_category_repo.delete_category(category_id, company_id)

    if not success:
        return jsonify({'error': '분류코드를 찾을 수 없거나 사용중인 번호가 있습니다.'}), 400

    return jsonify({'success': True, 'message': '분류코드가 삭제되었습니다.'})


@corporate_settings_api_bp.route('/number-categories/<int:category_id>/preview', methods=['GET'])
@corporate_admin_required
def preview_next_number(category_id):
    """다음 번호 미리보기"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    company_code = settings_repo.get_setting(company_id, 'company_code') or ''
    separator = settings_repo.get_setting(company_id, 'employee_number.separator') or '-'
    digits = settings_repo.get_setting(company_id, 'employee_number.digits') or 6

    preview = number_category_repo.preview_next_number(
        category_id, company_code, separator, int(digits)
    )

    return jsonify({'preview': preview})


@corporate_settings_api_bp.route('/number-categories/initialize-assets', methods=['POST'])
@corporate_admin_required
def initialize_asset_categories():
    """기본 자산 분류코드 초기화"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    results = number_category_repo.initialize_default_asset_categories(company_id)
    return jsonify({'success': True, 'initialized': len(results)})


# ===== 노출 설정 API =====

@corporate_settings_api_bp.route('/visibility', methods=['GET'])
@corporate_admin_required
def get_visibility_settings():
    """노출 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = visibility_repo.get_or_create(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/visibility', methods=['PUT'])
@corporate_admin_required
def update_visibility_settings():
    """노출 설정 저장"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    result = visibility_repo.update_settings(company_id, data)

    return jsonify(result)


@corporate_settings_api_bp.route('/visibility/reset', methods=['POST'])
@corporate_admin_required
def reset_visibility_settings():
    """노출 설정 기본값 초기화"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    result = visibility_repo.reset_to_defaults(company_id)
    return jsonify(result)


# ===== 법인 서류 API =====

@corporate_settings_api_bp.route('/documents', methods=['GET'])
@corporate_admin_required
def get_documents():
    """법인 서류 목록 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    documents = document_repo.get_by_company(company_id)
    statistics = document_repo.get_statistics(company_id)

    return jsonify({
        'documents': documents,
        'statistics': statistics
    })


@corporate_settings_api_bp.route('/documents/<category>', methods=['GET'])
@corporate_admin_required
def get_documents_by_category(category):
    """카테고리별 법인 서류 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    documents = document_repo.get_by_category(company_id, category)
    return jsonify({
        'category': category,
        'documents': documents
    })


@corporate_settings_api_bp.route('/documents', methods=['POST'])
@corporate_admin_required
def create_document():
    """법인 서류 등록"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    data['companyId'] = company_id
    data['uploadedBy'] = session.get('user_id')

    if not data.get('title'):
        return jsonify({'error': '서류 제목은 필수입니다.'}), 400

    result = document_repo.create(data)
    return jsonify(result), 201


@corporate_settings_api_bp.route('/documents/<int:document_id>', methods=['PUT'])
@corporate_admin_required
def update_document(document_id):
    """법인 서류 수정"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    result = document_repo.update(document_id, data)

    if not result:
        return jsonify({'error': '서류를 찾을 수 없습니다.'}), 404

    return jsonify(result)


@corporate_settings_api_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@corporate_admin_required
def delete_document(document_id):
    """법인 서류 삭제"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    success = document_repo.delete(document_id)

    if not success:
        return jsonify({'error': '서류를 찾을 수 없습니다.'}), 404

    return jsonify({'success': True, 'message': '서류가 삭제되었습니다.'})


@corporate_settings_api_bp.route('/documents/statistics', methods=['GET'])
@corporate_admin_required
def get_document_statistics():
    """법인 서류 통계 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    statistics = document_repo.get_statistics(company_id)
    return jsonify(statistics)


@corporate_settings_api_bp.route('/documents/expiring', methods=['GET'])
@corporate_admin_required
def get_expiring_documents():
    """만료 예정 서류 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    days = request.args.get('days', 30, type=int)
    documents = document_repo.get_expiring_documents(company_id, days)
    return jsonify(documents)


@corporate_settings_api_bp.route('/documents/upload', methods=['POST'])
@corporate_admin_required
def upload_document():
    """법인 서류 업로드 (파일 포함)"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    # 파일 검증
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일명이 없습니다.'}), 400

    # 파일 유효성 검사
    is_valid, error_msg = file_storage.validate_document_file(file)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    # 필수 필드 검증
    title = request.form.get('title', '').strip()
    if not title:
        return jsonify({'error': '서류 제목은 필수입니다.'}), 400

    # 파일 저장
    full_path, web_path, file_size, saved_filename = file_storage.save_company_document(
        file, company_id, prefix='doc'
    )

    # 파일 확장자 추출
    file_ext = file_storage.get_file_extension(file.filename)

    # 메타데이터 준비
    data = {
        'companyId': company_id,
        'title': title,
        'category': request.form.get('category', 'other'),
        'documentType': request.form.get('documentType', 'custom'),
        'description': request.form.get('description', ''),
        'expiresAt': request.form.get('expiresAt') or None,
        'isRequired': request.form.get('isRequired') == 'true',
        'fileName': file.filename,  # 원본 파일명
        'filePath': web_path,  # 웹 경로
        'fileSize': file_size,
        'fileType': file_ext,
        'uploadedBy': session.get('user_id')
    }

    # DB에 저장
    result = document_repo.create(data)
    return jsonify(result), 201


@corporate_settings_api_bp.route('/documents/<int:document_id>/download', methods=['GET'])
@corporate_admin_required
def download_document(document_id):
    """법인 서류 다운로드"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    # 문서 조회
    doc = document_repo.get_by_id(document_id, company_id)
    if not doc:
        return jsonify({'error': '서류를 찾을 수 없습니다.'}), 404

    file_path = doc.get('filePath')
    if not file_path:
        return jsonify({'error': '파일이 존재하지 않습니다.'}), 404

    # 웹 경로를 절대 경로로 변환
    if file_path.startswith('/static/'):
        from flask import current_app
        full_path = os.path.join(current_app.root_path, file_path.lstrip('/'))
    else:
        full_path = file_path

    if not os.path.exists(full_path):
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

    return send_file(
        full_path,
        as_attachment=True,
        download_name=doc.get('fileName', 'document')
    )
