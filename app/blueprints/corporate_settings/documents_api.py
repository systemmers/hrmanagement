"""
법인 서류 API

법인 서류 CRUD 및 파일 업로드/다운로드 API를 제공합니다.
"""
import os

from flask import jsonify, request, session, send_file

from app.blueprints.corporate_settings import corporate_settings_api_bp
from app.blueprints.corporate_settings.helpers import get_company_id
from app.constants.session_keys import SessionKeys
from app.services.file_storage_service import file_storage
from app.services.corporate_settings_service import corporate_settings_service
from app.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/documents', methods=['GET'])
@corporate_admin_required
def get_documents():
    """법인 서류 목록 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    documents = corporate_settings_service.get_documents(company_id)
    statistics = corporate_settings_service.get_document_statistics(company_id)

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

    documents = corporate_settings_service.get_documents_by_category(company_id, category)
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
    data['uploadedBy'] = session.get(SessionKeys.USER_ID)

    if not data.get('title'):
        return jsonify({'error': '서류 제목은 필수입니다.'}), 400

    result = corporate_settings_service.create_document(data)
    return jsonify(result), 201


@corporate_settings_api_bp.route('/documents/<int:document_id>', methods=['PUT'])
@corporate_admin_required
def update_document(document_id):
    """법인 서류 수정"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    result = corporate_settings_service.update_document(document_id, data)

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

    success = corporate_settings_service.delete_document(document_id)

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

    statistics = corporate_settings_service.get_document_statistics(company_id)
    return jsonify(statistics)


@corporate_settings_api_bp.route('/documents/expiring', methods=['GET'])
@corporate_admin_required
def get_expiring_documents():
    """만료 예정 서류 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    days = request.args.get('days', 30, type=int)
    documents = corporate_settings_service.get_expiring_documents(company_id, days)
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
        'uploadedBy': session.get(SessionKeys.USER_ID)
    }

    # DB에 저장
    result = corporate_settings_service.create_document(data)
    return jsonify(result), 201


@corporate_settings_api_bp.route('/documents/<int:document_id>/download', methods=['GET'])
@corporate_admin_required
def download_document(document_id):
    """법인 서류 다운로드"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    # 문서 조회
    doc = corporate_settings_service.get_document_by_id(document_id, company_id)
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
