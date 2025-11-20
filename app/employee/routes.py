"""
직원 관리 라우트
직원 목록/등록/상세/수정/삭제
"""
import os
import imghdr
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.employee import employee_bp
from app.employee.forms import EmployeeForm
from app.models import Employee, Department, Position
from app import db


# 파일 업로드 상수
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """파일 확장자 검증"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(file):
    """이미지 파일 검증 (MIME 타입 및 크기)"""
    # 파일 크기 체크
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        return False, '파일 크기는 5MB를 초과할 수 없습니다.'

    # MIME 타입 검증 (실제 이미지 파일인지 확인)
    header = file.read(512)
    file.seek(0)
    format = imghdr.what(None, header)

    if not format or format not in ALLOWED_EXTENSIONS:
        return False, '허용되지 않는 파일 형식입니다. (PNG, JPG, GIF만 가능)'

    return True, None


@employee_bp.route('/')
@login_required
def index():
    """대시보드 - 직원 목록"""
    employees = Employee.query.order_by(Employee.created_at.desc()).all()

    # 통계 계산
    total_count = Employee.query.count()
    active_count = Employee.query.filter_by(status='active').count()
    warning_count = Employee.query.filter_by(status='warning').count()
    expired_count = Employee.query.filter_by(status='expired').count()

    return render_template(
        'employee/index.html',
        employees=employees,
        total_count=total_count,
        active_count=active_count,
        warning_count=warning_count,
        expired_count=expired_count
    )


@employee_bp.route('/employee/new', methods=['GET', 'POST'])
@login_required
def new():
    """직원 등록"""
    form = EmployeeForm()

    # 부서 및 직급 선택지 설정
    form.department_id.choices = [(0, '선택')] + \
        [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]
    form.position_id.choices = [(0, '선택')] + \
        [(p.id, p.name) for p in Position.query.order_by(Position.level).all()]

    if form.validate_on_submit():
        employee = Employee()
        form.populate_obj(employee)

        # 0이면 None으로 변경
        if employee.department_id == 0:
            employee.department_id = None
        if employee.position_id == 0:
            employee.position_id = None

        # 사진 업로드 처리
        if form.photo.data:
            file = form.photo.data
            if file.filename:
                # 파일 확장자 검증
                if not allowed_file(file.filename):
                    flash('허용되지 않는 파일 형식입니다. (PNG, JPG, GIF만 가능)', 'error')
                    return redirect(url_for('employee.new'))

                # 파일 크기 및 MIME 타입 검증
                is_valid, error_message = validate_image(file)
                if not is_valid:
                    flash(error_message, 'error')
                    return redirect(url_for('employee.new'))

                # 안전한 파일명 생성
                filename = secure_filename(file.filename)
                import uuid
                ext = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{ext}"

                # 업로드 디렉토리 생성
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'employees')
                os.makedirs(upload_dir, exist_ok=True)

                # 파일 저장
                filepath = os.path.join(upload_dir, unique_filename)
                file.save(filepath)

                # 상대 경로 저장
                employee.photo = f"employees/{unique_filename}"

        db.session.add(employee)
        db.session.commit()

        flash(f'{employee.name} 직원이 등록되었습니다.', 'success')
        return redirect(url_for('employee.detail', id=employee.id))

    return render_template('employee/register.html', form=form)


@employee_bp.route('/employee/<int:id>')
@login_required
def detail(id):
    """직원 상세"""
    employee = Employee.query.get_or_404(id)
    return render_template('employee/detail.html', employee=employee)


@employee_bp.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """직원 수정"""
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)

    # 부서 및 직급 선택지 설정
    form.department_id.choices = [(0, '선택')] + \
        [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]
    form.position_id.choices = [(0, '선택')] + \
        [(p.id, p.name) for p in Position.query.order_by(Position.level).all()]

    if form.validate_on_submit():
        form.populate_obj(employee)

        # 0이면 None으로 변경
        if employee.department_id == 0:
            employee.department_id = None
        if employee.position_id == 0:
            employee.position_id = None

        # 사진 업로드 처리
        if form.photo.data:
            file = form.photo.data
            if file.filename:
                # 파일 확장자 검증
                if not allowed_file(file.filename):
                    flash('허용되지 않는 파일 형식입니다. (PNG, JPG, GIF만 가능)', 'error')
                    return redirect(url_for('employee.edit', id=employee.id))

                # 파일 크기 및 MIME 타입 검증
                is_valid, error_message = validate_image(file)
                if not is_valid:
                    flash(error_message, 'error')
                    return redirect(url_for('employee.edit', id=employee.id))

                # 기존 사진 삭제
                if employee.photo:
                    old_photo = os.path.join(current_app.config['UPLOAD_FOLDER'], employee.photo)
                    if os.path.exists(old_photo):
                        os.remove(old_photo)

                # 안전한 파일명 생성
                filename = secure_filename(file.filename)
                import uuid
                ext = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{ext}"

                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'employees')
                os.makedirs(upload_dir, exist_ok=True)

                filepath = os.path.join(upload_dir, unique_filename)
                file.save(filepath)

                employee.photo = f"employees/{unique_filename}"

        db.session.commit()

        flash(f'{employee.name} 직원 정보가 수정되었습니다.', 'success')
        return redirect(url_for('employee.detail', id=employee.id))

    return render_template('employee/edit.html', form=form, employee=employee)


@employee_bp.route('/employee/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """직원 삭제"""
    employee = Employee.query.get_or_404(id)
    name = employee.name

    # 사진 파일 삭제
    if employee.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], employee.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(employee)
    db.session.commit()

    flash(f'{name} 직원이 삭제되었습니다.', 'info')
    return redirect(url_for('employee.index'))
