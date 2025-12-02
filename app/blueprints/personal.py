"""
개인 계정 Blueprint

개인 회원가입, 프로필 관리, 개인 대시보드를 처리합니다.
Phase 2: 개인-법인 분리 아키텍처의 일부입니다.
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

from app.database import db
from app.models.user import User
from app.models.personal_profile import (
    PersonalProfile, PersonalEducation, PersonalCareer,
    PersonalCertificate, PersonalLanguage, PersonalMilitaryService
)

personal_bp = Blueprint('personal', __name__, url_prefix='/personal')


def personal_login_required(f):
    """개인 계정 로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('account_type') != User.ACCOUNT_PERSONAL:
            flash('개인 계정으로 로그인해주세요.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@personal_bp.route('/register', methods=['GET', 'POST'])
def register():
    """개인 회원가입"""
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 계정 정보
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # 프로필 정보
        name = request.form.get('name', '').strip()
        mobile_phone = request.form.get('mobile_phone', '').strip()

        # 필수 입력 검증
        errors = []
        if not username:
            errors.append('아이디를 입력해주세요.')
        if not email:
            errors.append('이메일을 입력해주세요.')
        if not password:
            errors.append('비밀번호를 입력해주세요.')
        if password != password_confirm:
            errors.append('비밀번호가 일치하지 않습니다.')
        if len(password) < 8:
            errors.append('비밀번호는 최소 8자 이상이어야 합니다.')
        if not name:
            errors.append('이름을 입력해주세요.')

        # 아이디/이메일 중복 확인
        if User.query.filter_by(username=username).first():
            errors.append('이미 사용 중인 아이디입니다.')
        if User.query.filter_by(email=email).first():
            errors.append('이미 사용 중인 이메일입니다.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('personal/register.html',
                                   username=username,
                                   email=email,
                                   name=name,
                                   mobile_phone=mobile_phone)

        try:
            # 사용자 계정 생성
            user = User(
                username=username,
                email=email,
                role=User.ROLE_EMPLOYEE,
                account_type=User.ACCOUNT_PERSONAL,
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # 개인 프로필 생성
            profile = PersonalProfile(
                user_id=user.id,
                name=name,
                email=email,
                mobile_phone=mobile_phone
            )
            db.session.add(profile)

            db.session.commit()

            flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'회원가입 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('personal/register.html',
                                   username=username,
                                   email=email,
                                   name=name,
                                   mobile_phone=mobile_phone)

    return render_template('personal/register.html')


@personal_bp.route('/dashboard')
@personal_login_required
def dashboard():
    """개인 대시보드"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    profile = PersonalProfile.query.filter_by(user_id=user_id).first()

    # 프로필이 없으면 생성 안내
    if not profile:
        flash('프로필을 먼저 작성해주세요.', 'info')
        return redirect(url_for('personal.profile_edit'))

    # 통계 정보
    stats = {
        'education_count': profile.educations.count() if profile.educations else 0,
        'career_count': profile.careers.count() if profile.careers else 0,
        'certificate_count': profile.certificates.count() if profile.certificates else 0,
        'language_count': profile.languages.count() if profile.languages else 0,
        'has_military': profile.military_service is not None
    }

    return render_template('personal/dashboard.html',
                           user=user,
                           profile=profile,
                           stats=stats)


@personal_bp.route('/profile')
@personal_login_required
def profile():
    """프로필 조회"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash('프로필을 먼저 작성해주세요.', 'info')
        return redirect(url_for('personal.profile_edit'))

    return render_template('personal/profile.html',
                           user=user,
                           profile=profile)


@personal_bp.route('/profile/edit', methods=['GET', 'POST'])
@personal_login_required
def profile_edit():
    """프로필 수정"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()

    # 프로필이 없으면 새로 생성
    if not profile:
        profile = PersonalProfile(user_id=user_id, name=user.username)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        # 기본 정보
        profile.name = request.form.get('name', profile.name).strip()
        profile.english_name = request.form.get('english_name', '').strip() or None
        profile.chinese_name = request.form.get('chinese_name', '').strip() or None
        profile.birth_date = request.form.get('birth_date', '').strip() or None
        profile.lunar_birth = request.form.get('lunar_birth') == 'true'
        profile.gender = request.form.get('gender', '').strip() or None

        # 연락처 정보
        profile.mobile_phone = request.form.get('mobile_phone', '').strip() or None
        profile.home_phone = request.form.get('home_phone', '').strip() or None
        profile.email = request.form.get('email', '').strip() or None

        # 주소 정보
        profile.postal_code = request.form.get('postal_code', '').strip() or None
        profile.address = request.form.get('address', '').strip() or None
        profile.detailed_address = request.form.get('detailed_address', '').strip() or None

        # 기타 정보
        profile.nationality = request.form.get('nationality', '').strip() or None
        profile.blood_type = request.form.get('blood_type', '').strip() or None
        profile.religion = request.form.get('religion', '').strip() or None
        profile.hobby = request.form.get('hobby', '').strip() or None
        profile.specialty = request.form.get('specialty', '').strip() or None

        # 공개 설정
        profile.is_public = request.form.get('is_public') == 'true'

        try:
            db.session.commit()
            flash('프로필이 수정되었습니다.', 'success')
            return redirect(url_for('personal.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')

    return render_template('personal/profile_edit.html',
                           user=user,
                           profile=profile)


# ============================================================
# 학력 관리 API
# ============================================================

@personal_bp.route('/education', methods=['GET'])
@personal_login_required
def education_list():
    """학력 목록 조회"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    educations = [edu.to_dict() for edu in profile.educations.all()]
    return jsonify({'educations': educations})


@personal_bp.route('/education', methods=['POST'])
@personal_login_required
def education_add():
    """학력 추가"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    data = request.get_json()
    education = PersonalEducation(
        profile_id=profile.id,
        school_type=data.get('school_type'),
        school_name=data.get('school_name'),
        major=data.get('major'),
        degree=data.get('degree'),
        admission_date=data.get('admission_date'),
        graduation_date=data.get('graduation_date'),
        status=data.get('status'),
        gpa=data.get('gpa'),
        notes=data.get('notes')
    )
    db.session.add(education)
    db.session.commit()

    return jsonify({'success': True, 'education': education.to_dict()})


@personal_bp.route('/education/<int:education_id>', methods=['DELETE'])
@personal_login_required
def education_delete(education_id):
    """학력 삭제"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    education = PersonalEducation.query.filter_by(
        id=education_id, profile_id=profile.id
    ).first()
    if not education:
        return jsonify({'error': '학력 정보를 찾을 수 없습니다.'}), 404

    db.session.delete(education)
    db.session.commit()

    return jsonify({'success': True})


# ============================================================
# 경력 관리 API
# ============================================================

@personal_bp.route('/career', methods=['GET'])
@personal_login_required
def career_list():
    """경력 목록 조회"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    careers = [career.to_dict() for career in profile.careers.all()]
    return jsonify({'careers': careers})


@personal_bp.route('/career', methods=['POST'])
@personal_login_required
def career_add():
    """경력 추가"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    data = request.get_json()
    career = PersonalCareer(
        profile_id=profile.id,
        company_name=data.get('company_name'),
        department=data.get('department'),
        position=data.get('position'),
        job_title=data.get('job_title'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        is_current=data.get('is_current', False),
        responsibilities=data.get('responsibilities'),
        achievements=data.get('achievements'),
        reason_for_leaving=data.get('reason_for_leaving')
    )
    db.session.add(career)
    db.session.commit()

    return jsonify({'success': True, 'career': career.to_dict()})


@personal_bp.route('/career/<int:career_id>', methods=['DELETE'])
@personal_login_required
def career_delete(career_id):
    """경력 삭제"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    career = PersonalCareer.query.filter_by(
        id=career_id, profile_id=profile.id
    ).first()
    if not career:
        return jsonify({'error': '경력 정보를 찾을 수 없습니다.'}), 404

    db.session.delete(career)
    db.session.commit()

    return jsonify({'success': True})


# ============================================================
# 자격증 관리 API
# ============================================================

@personal_bp.route('/certificate', methods=['GET'])
@personal_login_required
def certificate_list():
    """자격증 목록 조회"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    certificates = [cert.to_dict() for cert in profile.certificates.all()]
    return jsonify({'certificates': certificates})


@personal_bp.route('/certificate', methods=['POST'])
@personal_login_required
def certificate_add():
    """자격증 추가"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    data = request.get_json()
    certificate = PersonalCertificate(
        profile_id=profile.id,
        name=data.get('name'),
        issuing_organization=data.get('issuing_organization'),
        issue_date=data.get('issue_date'),
        expiry_date=data.get('expiry_date'),
        certificate_number=data.get('certificate_number'),
        grade=data.get('grade'),
        notes=data.get('notes')
    )
    db.session.add(certificate)
    db.session.commit()

    return jsonify({'success': True, 'certificate': certificate.to_dict()})


@personal_bp.route('/certificate/<int:certificate_id>', methods=['DELETE'])
@personal_login_required
def certificate_delete(certificate_id):
    """자격증 삭제"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    certificate = PersonalCertificate.query.filter_by(
        id=certificate_id, profile_id=profile.id
    ).first()
    if not certificate:
        return jsonify({'error': '자격증 정보를 찾을 수 없습니다.'}), 404

    db.session.delete(certificate)
    db.session.commit()

    return jsonify({'success': True})


# ============================================================
# 어학 관리 API
# ============================================================

@personal_bp.route('/language', methods=['GET'])
@personal_login_required
def language_list():
    """어학 목록 조회"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    languages = [lang.to_dict() for lang in profile.languages.all()]
    return jsonify({'languages': languages})


@personal_bp.route('/language', methods=['POST'])
@personal_login_required
def language_add():
    """어학 추가"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    data = request.get_json()
    language = PersonalLanguage(
        profile_id=profile.id,
        language=data.get('language'),
        proficiency=data.get('proficiency'),
        test_name=data.get('test_name'),
        score=data.get('score'),
        test_date=data.get('test_date'),
        notes=data.get('notes')
    )
    db.session.add(language)
    db.session.commit()

    return jsonify({'success': True, 'language': language.to_dict()})


@personal_bp.route('/language/<int:language_id>', methods=['DELETE'])
@personal_login_required
def language_delete(language_id):
    """어학 삭제"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    language = PersonalLanguage.query.filter_by(
        id=language_id, profile_id=profile.id
    ).first()
    if not language:
        return jsonify({'error': '어학 정보를 찾을 수 없습니다.'}), 404

    db.session.delete(language)
    db.session.commit()

    return jsonify({'success': True})


# ============================================================
# 병역 관리 API
# ============================================================

@personal_bp.route('/military', methods=['GET'])
@personal_login_required
def military_get():
    """병역 정보 조회"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    military = profile.military_service
    if not military:
        return jsonify({'military': None})

    return jsonify({'military': military.to_dict()})


@personal_bp.route('/military', methods=['POST'])
@personal_login_required
def military_save():
    """병역 정보 저장/수정"""
    user_id = session.get('user_id')
    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404

    data = request.get_json()

    # 기존 병역 정보가 있으면 수정, 없으면 생성
    military = profile.military_service
    if not military:
        military = PersonalMilitaryService(profile_id=profile.id)
        db.session.add(military)

    military.service_type = data.get('service_type')
    military.branch = data.get('branch')
    military.rank = data.get('rank')
    military.start_date = data.get('start_date')
    military.end_date = data.get('end_date')
    military.discharge_type = data.get('discharge_type')
    military.specialty = data.get('specialty')
    military.notes = data.get('notes')

    db.session.commit()

    return jsonify({'success': True, 'military': military.to_dict()})
