"""
Profile Routes - 통합 프로필 라우트

법인 직원과 개인 계정의 프로필을 통합 처리하는 라우트
"""
from flask import render_template, g, jsonify

from app.blueprints.profile import profile_bp
from app.blueprints.profile.decorators import (
    unified_profile_required,
    corporate_only
)


@profile_bp.route('/')
@unified_profile_required
def view():
    """
    통합 프로필 조회

    법인 직원과 개인 계정 모두 동일한 템플릿 사용
    계정 유형에 따라 표시되는 섹션이 다름
    """
    adapter = g.profile

    context = {
        # 기본 정보 (공통)
        'basic_info': adapter.get_basic_info(),

        # 법인 전용 정보
        'organization_info': adapter.get_organization_info(),
        'contract_info': adapter.get_contract_info(),
        'salary_info': adapter.get_salary_info(),
        'benefit_info': adapter.get_benefit_info(),
        'insurance_info': adapter.get_insurance_info(),

        # 이력 정보 (공통)
        'education_list': adapter.get_education_list(),
        'career_list': adapter.get_career_list(),
        'certificate_list': adapter.get_certificate_list(),
        'language_list': adapter.get_language_list(),
        'military_info': adapter.get_military_info(),

        # 메타 정보
        'sections': adapter.get_available_sections(),
    }

    return render_template('profile/unified_profile.html', **context)


# TODO: unified_profile_edit.html 템플릿 구현 후 활성화
# @profile_bp.route('/edit')
# @unified_profile_required
# def edit():
#     """통합 프로필 수정 폼"""
#     adapter = g.profile
#     context = {
#         'basic_info': adapter.get_basic_info(),
#         'sections': adapter.get_available_sections(),
#     }
#     return render_template('profile/unified_profile_edit.html', **context)


@profile_bp.route('/section/<section_name>')
@unified_profile_required
def get_section(section_name):
    """
    섹션별 데이터 API

    특정 섹션의 데이터를 JSON으로 반환
    사용자가 접근 가능한 섹션만 반환

    Args:
        section_name: 섹션 이름 (basic, organization, etc.)

    Returns:
        JSON: 섹션 데이터 또는 에러 메시지
    """
    adapter = g.profile

    # 접근 권한 확인
    if section_name not in adapter.get_available_sections():
        return jsonify({
            'success': False,
            'error': '접근 권한이 없는 섹션입니다.'
        }), 403

    # 섹션별 데이터 매핑
    section_methods = {
        'basic': adapter.get_basic_info,
        'organization': adapter.get_organization_info,
        'contract': adapter.get_contract_info,
        'salary': adapter.get_salary_info,
        'benefit': adapter.get_benefit_info,
        'insurance': adapter.get_insurance_info,
        'education': adapter.get_education_list,
        'career': adapter.get_career_list,
        'certificate': adapter.get_certificate_list,
        'language': adapter.get_language_list,
        'military': adapter.get_military_info,
    }

    method = section_methods.get(section_name)
    if not method:
        return jsonify({
            'success': False,
            'error': '알 수 없는 섹션입니다.'
        }), 404

    try:
        data = method()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'데이터 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@profile_bp.route('/corporate/salary-history')
@corporate_only
def salary_history():
    """급여 이력 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_salary_history_list()
    })


@profile_bp.route('/corporate/promotions')
@corporate_only
def promotions():
    """승진 이력 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_promotion_list()
    })


@profile_bp.route('/corporate/evaluations')
@corporate_only
def evaluations():
    """평가 기록 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_evaluation_list()
    })


@profile_bp.route('/corporate/trainings')
@corporate_only
def trainings():
    """교육 이력 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_training_list()
    })


@profile_bp.route('/corporate/attendances')
@corporate_only
def attendances():
    """근태 기록 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_attendance_list()
    })


@profile_bp.route('/corporate/assets')
@corporate_only
def assets():
    """비품 목록 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_asset_list()
    })


@profile_bp.route('/corporate/family')
@corporate_only
def family():
    """가족 정보 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_family_list()
    })


@profile_bp.route('/projects')
@unified_profile_required
def projects():
    """프로젝트 목록 조회"""
    adapter = g.profile

    # 법인 직원만 프로젝트 정보 있음
    if not g.is_corporate:
        return jsonify({
            'success': True,
            'data': []
        })

    return jsonify({
        'success': True,
        'data': adapter.get_project_list()
    })


@profile_bp.route('/awards')
@unified_profile_required
def awards():
    """수상 이력 조회"""
    adapter = g.profile

    # 법인 직원만 수상 정보 있음
    if not g.is_corporate:
        return jsonify({
            'success': True,
            'data': []
        })

    return jsonify({
        'success': True,
        'data': adapter.get_award_list()
    })
