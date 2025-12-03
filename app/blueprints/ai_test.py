"""
AI 테스트 Blueprint
- 문서 분석 프로토타입 테스트 페이지
- Provider 비교 테스트
- AI 설정 확인
"""
from flask import Blueprint, render_template, request, jsonify, current_app
import os

from ..utils.decorators import login_required, admin_required

ai_test_bp = Blueprint('ai_test', __name__, url_prefix='/ai-test')


@ai_test_bp.route('/')
@login_required
def index():
    """AI 문서 분석 테스트 메인 페이지"""
    sample_files = get_sample_files()
    providers = get_available_providers()
    return render_template('ai_test/index.html',
                          sample_files=sample_files,
                          providers=providers)


@ai_test_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """문서 분석 실행"""
    file = request.files.get('file')
    sample_file = request.form.get('sample_file')
    provider = request.form.get('provider', 'gemini')
    document_type = request.form.get('document_type', 'auto_detect')

    # 파일 경로 결정
    if file and file.filename:
        # 업로드된 파일 저장
        file_path = save_uploaded_file(file)
    elif sample_file:
        # 샘플 파일 사용
        file_path = get_sample_file_path(sample_file)
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': f'샘플 파일을 찾을 수 없습니다: {sample_file}'}), 400
    else:
        return jsonify({'error': '파일을 선택해주세요'}), 400

    try:
        # AI 분석 실행
        from ..services.ai_service import AIService
        result = AIService.analyze(
            file_path=file_path,
            provider_name=provider,
            document_type=document_type
        )
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({
            'error': str(e),
            'provider': provider,
            'document_type': document_type
        }), 500


@ai_test_bp.route('/compare')
@login_required
def compare():
    """Provider 비교 테스트 페이지"""
    sample_files = get_sample_files()
    providers = get_available_providers()
    return render_template('ai_test/compare.html',
                          sample_files=sample_files,
                          providers=providers)


@ai_test_bp.route('/compare/run', methods=['POST'])
@login_required
def run_compare():
    """여러 Provider로 동시 분석 비교"""
    file = request.files.get('file')
    sample_file = request.form.get('sample_file')

    # 파일 경로 결정
    if file and file.filename:
        file_path = save_uploaded_file(file)
    elif sample_file:
        file_path = get_sample_file_path(sample_file)
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': f'샘플 파일을 찾을 수 없습니다: {sample_file}'}), 400
    else:
        return jsonify({'error': '파일을 선택해주세요'}), 400

    results = {}

    try:
        from ..services.ai_service import AIService
        available_providers = AIService.get_available_providers()

        for provider_name in available_providers:
            try:
                result = AIService.analyze(file_path, provider_name)
                results[provider_name] = {
                    'success': True,
                    'data': result.to_dict()
                }
            except Exception as e:
                results[provider_name] = {
                    'success': False,
                    'error': str(e)
                }
    except ImportError:
        # AI Service가 아직 구현되지 않은 경우
        results['error'] = 'AI Service가 아직 구현되지 않았습니다.'

    return jsonify(results)


@ai_test_bp.route('/settings')
@admin_required
def settings():
    """AI 설정 페이지"""
    config = {
        'gemini_api_key': bool(current_app.config.get('GEMINI_API_KEY')),
        'gemini_api_key_preview': mask_api_key(current_app.config.get('GEMINI_API_KEY', '')),
        'google_project_id': current_app.config.get('GOOGLE_PROJECT_ID', '미설정'),
        'google_location': current_app.config.get('GOOGLE_LOCATION', 'asia-northeast3'),
        'google_credentials': bool(current_app.config.get('GOOGLE_APPLICATION_CREDENTIALS')),
        'documentai_processor': bool(current_app.config.get('DOCUMENTAI_PROCESSOR_ID')),
    }

    # 사용 가능한 Provider 목록
    try:
        from ..services.ai_service import AIService
        providers = list(AIService.get_available_providers().keys())
    except ImportError:
        providers = []

    return render_template('ai_test/settings.html',
                          config=config,
                          providers=providers)


# 헬퍼 함수들
def get_sample_files():
    """data/db_files/ 샘플 파일 목록"""
    sample_dir = os.path.join(current_app.root_path, '..', 'data', 'db_files')
    if os.path.exists(sample_dir):
        files = []
        for f in os.listdir(sample_dir):
            if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif')):
                files.append({
                    'name': f,
                    'path': os.path.join(sample_dir, f),
                    'size': os.path.getsize(os.path.join(sample_dir, f))
                })
        return sorted(files, key=lambda x: x['name'])
    return []


def get_sample_file_path(filename):
    """샘플 파일 전체 경로 반환"""
    sample_dir = os.path.join(current_app.root_path, '..', 'data', 'db_files')
    return os.path.join(sample_dir, filename)


def get_available_providers():
    """사용 가능한 AI Provider 목록"""
    try:
        from ..services.ai_service import AIService
        return list(AIService.get_available_providers().keys())
    except ImportError:
        # AI Service가 아직 구현되지 않은 경우 기본값
        return ['gemini', 'vertex_ai', 'document_ai']


def save_uploaded_file(file):
    """업로드된 파일 저장"""
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # 안전한 파일명 생성
    from werkzeug.utils import secure_filename
    import uuid

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    file.save(file_path)
    return file_path


def mask_api_key(api_key):
    """API 키 마스킹"""
    if not api_key:
        return '미설정'
    if len(api_key) <= 8:
        return '*' * len(api_key)
    return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
