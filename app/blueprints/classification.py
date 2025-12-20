"""
분류 옵션 관리 Blueprint

분류 옵션 관리 페이지를 제공합니다.
Phase 2: Service 계층 표준화
"""
from flask import Blueprint, render_template

from ..services.classification_service import classification_service
from ..utils.decorators import login_required

classification_bp = Blueprint('classification', __name__)


@classification_bp.route('/classification-options')
@login_required
def classification_options_page():
    """분류 옵션 관리 페이지"""
    options = classification_service.get_all()
    return render_template('admin/classification_options.html', classification_options=options)
