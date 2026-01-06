"""
법인 서류 API

법인 서류 CRUD 및 파일 업로드/다운로드 API를 제공합니다.
Phase 2.4: API 응답 표준화 (2025-12-29)
"""
import os

from flask import request, session, send_file

from app.blueprints.corporate_settings import corporate_settings_api_bp
from app.blueprints.corporate_settings.helpers import get_company_id
from app.shared.constants.session_keys import SessionKeys
from app.services.file_storage_service import file_storage
from app.services.corporate_settings_service import corporate_settings_service
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden, api_not_found
from app.shared.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/documents', methods=['GET'])
@corporate_admin_required
def get_documents():
    """법인 서류 목록 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    documents = corporate_settings_service.get_documents(company_id)
    statistics = corporate_settings_service.get_document_statistics(company_id)

    return api_success({
        'documents': documents,
        'statistics': statistics
    })


@corporate_settings_api_bp.route('/documents/<category>', methods=['GET'])
@corporate_admin_required
def get_documents_by_category(category):
    """카테고리별 법인 서류 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    documents = corporate_settings_service.get_documents_by_category(company_id, category)
    return api_success({
        'category': category,
        'documents': documents
    })


@corporate_settings_api_bp.route('/documents', methods=['POST'])
@corporate_admin_required
def create_document():
    """법인 서류 등록"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    data['companyId'] = company_id
    data['uploadedBy'] = session.get(SessionKeys.USER_ID)

    if not data.get('title'):
        return api_error('서류 제목은 필수입니다.')

    result = corporate_settings_service.create_document(data)
    return api_success(result, status_code=201)


@corporate_settings_api_bp.route('/documents/<int:document_id>', methods=['PUT'])
@corporate_admin_required
def update_document(document_id):
    """법인 서류 수정"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    result = corporate_settings_service.update_document(document_id, data)

    if not result:
        return api_not_found('서류')

    return api_success(result)


@corporate_settings_api_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@corporate_admin_required
def delete_document(document_id):
    """법인 서류 삭제"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    success = corporate_settings_service.delete_document(document_id)

    if not success:
        return api_not_found('서류')

    return api_success(message='서류가 삭제되었습니다.')


@corporate_settings_api_bp.route('/documents/statistics', methods=['GET'])
@corporate_admin_required
def get_document_statistics():
    """법인 서류 통계 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    statistics = corporate_settings_service.get_document_statistics(company_id)
    return api_success(statistics)


@corporate_settings_api_bp.route('/documents/expiring', methods=['GET'])
@corporate_admin_required
def get_expiring_documents():
    """만료 예정 서류 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    days = request.args.get('days', 30, type=int)
    documents = corporate_settings_service.get_expiring_documents(company_id, days)
    return api_success(documents)


@corporate_settings_api_bp.route('/documents/upload', methods=['POST'])
@corporate_admin_required
def upload_document():
    """법인 서류 업로드 (파일 포함)"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 파일 검증
    if 'file' not in request.files:
        return api_error('파일이 없습니다.')

    file = request.files['file']
    if file.filename == '':
        return api_error('파일명이 없습니다.')

    # 파일 유효성 검사
    is_valid, error_msg = file_storage.validate_document_file(file)
    if not is_valid:
        return api_error(error_msg)

    # 필수 필드 검증
    title = request.form.get('title', '').strip()
    if not title:
        return api_error('서류 제목은 필수입니다.')

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
        'uploadedBy': session.get(SessionKeys.USER_ID)
    }

    # DB에 저장
    result = corporate_settings_service.create_document(data)
    return api_success(result, status_code=201)


@corporate_settings_api_bp.route('/documents/<int:document_id>/download', methods=['GET'])
@corporate_admin_required
def download_document(document_id):
    """법인 서류 다운로드"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 문서 조회
    doc = corporate_settings_service.get_document_by_id(document_id, company_id)
    if not doc:
        return api_not_found('서류')

    file_path = doc.get('filePath')
    if not file_path:
        return api_not_found('파일')

    # 웹 경로를 절대 경로로 변환
    if file_path.startswith('/static/'):
        from flask import current_app
        full_path = os.path.join(current_app.root_path, file_path.lstrip('/'))
    else:
        full_path = file_path

    if not os.path.exists(full_path):
        return api_not_found('파일')

    return send_file(
        full_path,
        as_attachment=True,
        download_name=doc.get('fileName', 'document')
    )
