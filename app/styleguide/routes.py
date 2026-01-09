"""
Styleguide Routes
스타일가이드 페이지 라우팅
"""
from flask import render_template, redirect, url_for
from . import styleguide_bp
from .config import NAVIGATION, STYLEGUIDE_META


@styleguide_bp.route('/')
def index():
    """스타일가이드 메인 페이지"""
    return render_template(
        'styleguide/index.html',
        navigation=NAVIGATION,
        meta=STYLEGUIDE_META,
        active='overview'
    )


@styleguide_bp.route('/foundation/')
def foundation_index():
    """Foundation 섹션 인덱스 - 첫 번째 항목으로 리다이렉트"""
    return redirect(url_for('styleguide.foundation', page='colors'))


@styleguide_bp.route('/foundation/<page>')
def foundation(page):
    """Foundation 섹션 (colors, typography, spacing, shadows)"""
    valid_pages = [item['id'] for item in NAVIGATION['foundation']['items']]
    if page not in valid_pages:
        return redirect(url_for('styleguide.foundation', page='colors'))

    return render_template(
        f'styleguide/foundation/{page}.html',
        navigation=NAVIGATION,
        meta=STYLEGUIDE_META,
        active=f'foundation-{page}',
        current_page=page
    )


@styleguide_bp.route('/components/')
def components_index():
    """Components 섹션 인덱스 - 첫 번째 항목으로 리다이렉트"""
    return redirect(url_for('styleguide.component', component='buttons'))


@styleguide_bp.route('/components/<component>')
def component(component):
    """컴포넌트 섹션"""
    valid_components = [item['id'] for item in NAVIGATION['components']['items']]
    if component not in valid_components:
        return redirect(url_for('styleguide.component', component='buttons'))

    return render_template(
        f'styleguide/components/{component}.html',
        navigation=NAVIGATION,
        meta=STYLEGUIDE_META,
        active=f'component-{component}',
        current_component=component
    )
