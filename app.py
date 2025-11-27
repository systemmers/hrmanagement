"""
인사카드 관리 시스템 Flask 애플리케이션
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import config
from models import (
    Employee, EmployeeRepository, ClassificationOptionsRepository,
    EducationRepository, CareerRepository, CertificateRepository,
    FamilyMemberRepository, LanguageRepository, MilitaryServiceRepository,
    SalaryRepository, BenefitRepository, ContractRepository, SalaryHistoryRepository,
    PromotionRepository, EvaluationRepository, TrainingRepository, AttendanceRepository,
    InsuranceRepository, ProjectRepository, AwardRepository, AssetRepository,
    SalaryPaymentRepository, AttachmentRepository
)
import os

app = Flask(__name__)
app.config.from_object(config['development'])

# 직원 저장소 초기화 (기본 + 확장 데이터 병합)
employee_repo = EmployeeRepository(
    app.config['EMPLOYEES_JSON'],
    app.config['EMPLOYEES_EXTENDED_JSON']
)
# 분류 옵션 저장소 초기화
classification_repo = ClassificationOptionsRepository(app.config['CLASSIFICATION_OPTIONS_JSON'])

# 관계형 데이터 저장소 초기화
education_repo = EducationRepository(app.config['EDUCATION_JSON'])
career_repo = CareerRepository(app.config['CAREERS_JSON'])
certificate_repo = CertificateRepository(app.config['CERTIFICATES_JSON'])
family_repo = FamilyMemberRepository(app.config['FAMILY_MEMBERS_JSON'])
language_repo = LanguageRepository(app.config['LANGUAGES_JSON'])
military_repo = MilitaryServiceRepository(app.config['MILITARY_JSON'])

# Phase 2: 핵심 기능 저장소 초기화
salary_repo = SalaryRepository(app.config['SALARIES_JSON'])
benefit_repo = BenefitRepository(app.config['BENEFITS_JSON'])
contract_repo = ContractRepository(app.config['CONTRACTS_JSON'])
salary_history_repo = SalaryHistoryRepository(app.config['SALARY_HISTORY_JSON'])

# Phase 3: 인사평가 기능 저장소 초기화
promotion_repo = PromotionRepository(app.config['PROMOTIONS_JSON'])
evaluation_repo = EvaluationRepository(app.config['EVALUATIONS_JSON'])
training_repo = TrainingRepository(app.config['TRAININGS_JSON'])
attendance_repo = AttendanceRepository(app.config['ATTENDANCE_JSON'])

# Phase 4: 부가 기능 저장소 초기화
insurance_repo = InsuranceRepository(app.config['INSURANCES_JSON'])
project_repo = ProjectRepository(app.config['PROJECTS_JSON'])
award_repo = AwardRepository(app.config['AWARDS_JSON'])
asset_repo = AssetRepository(app.config['ASSETS_JSON'])

# Phase 5: 급여 지급 이력 저장소 초기화
salary_payment_repo = SalaryPaymentRepository(app.config['SALARY_PAYMENTS_JSON'])

# Phase 6: 첨부파일 저장소 초기화
attachment_repo = AttachmentRepository(app.config['ATTACHMENTS_JSON'])


@app.route('/')
def index():
    """대시보드 - 통계 및 정보"""
    stats = employee_repo.get_statistics()
    dept_stats = employee_repo.get_department_statistics()
    recent_employees = employee_repo.get_recent_employees(limit=5)
    classification_options = classification_repo.get_all()
    return render_template('index.html', 
                         stats=stats, 
                         dept_stats=dept_stats, 
                         recent_employees=recent_employees,
                         classification_options=classification_options)


@app.route('/employees')
def employee_list():
    """직원 목록"""
    # 필터 파라미터 추출
    departments = request.args.getlist('department')
    positions = request.args.getlist('position')
    statuses = request.args.getlist('status')
    
    # 단일 값도 지원 (하위 호환성)
    department = request.args.get('department', None)
    position = request.args.get('position', None)
    status = request.args.get('status', None)
    
    # 다중 필터 적용
    if departments or positions or statuses:
        employees = employee_repo.filter_employees(
            departments=departments if departments else None,
            positions=positions if positions else None,
            statuses=statuses if statuses else None
        )
    elif department or position or status:
        employees = employee_repo.filter_employees(
            department=department,
            position=position,
            status=status
        )
    else:
        employees = employee_repo.get_all()
    
    # 분류 옵션 전달
    classification_options = classification_repo.get_all()
    return render_template('employee_list.html', 
                         employees=employees, 
                         classification_options=classification_options)


@app.route('/employees/<int:employee_id>')
def employee_detail(employee_id):
    """직원 상세 정보"""
    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('index'))

    # 관계형 데이터 조회
    education_list = education_repo.get_by_employee_id(employee_id)
    career_list = career_repo.get_by_employee_id(employee_id)
    certificate_list = certificate_repo.get_by_employee_id(employee_id)
    family_list = family_repo.get_by_employee_id(employee_id)
    language_list = language_repo.get_by_employee_id(employee_id)
    military = military_repo.get_by_employee_id(employee_id)

    # Phase 2: 핵심 기능 데이터 조회
    salary = salary_repo.get_by_employee_id(employee_id)
    benefit = benefit_repo.get_by_employee_id(employee_id)
    contract = contract_repo.get_by_employee_id(employee_id)
    salary_history_list = salary_history_repo.get_by_employee_id(employee_id)

    # Phase 3: 인사평가 기능 데이터 조회
    promotion_list = promotion_repo.get_by_employee_id(employee_id)
    evaluation_list = evaluation_repo.get_by_employee_id(employee_id)
    training_list = training_repo.get_by_employee_id(employee_id)
    attendance_summary = attendance_repo.get_summary_by_employee(employee_id, 2025)

    # Phase 4: 부가 기능 데이터 조회
    insurance = insurance_repo.get_by_employee_id(employee_id)
    project_list = project_repo.get_by_employee_id(employee_id)
    award_list = award_repo.get_by_employee_id(employee_id)
    asset_list = asset_repo.get_by_employee_id(employee_id)

    # Phase 5: 급여 지급 이력 조회
    salary_payment_list = salary_payment_repo.get_by_employee_id(employee_id)

    # Phase 6: 첨부파일 조회
    attachment_list = attachment_repo.get_by_employee_id(employee_id)

    return render_template('employee_detail.html',
                           employee=employee,
                           education_list=education_list,
                           career_list=career_list,
                           certificate_list=certificate_list,
                           family_list=family_list,
                           language_list=language_list,
                           military=military,
                           salary=salary,
                           benefit=benefit,
                           contract=contract,
                           salary_history_list=salary_history_list,
                           promotion_list=promotion_list,
                           evaluation_list=evaluation_list,
                           training_list=training_list,
                           attendance_summary=attendance_summary,
                           insurance=insurance,
                           project_list=project_list,
                           award_list=award_list,
                           asset_list=asset_list,
                           salary_payment_list=salary_payment_list,
                           attachment_list=attachment_list)


@app.route('/employees/new', methods=['GET'])
def employee_new():
    """직원 등록 폼"""
    return render_template('employee_form.html', employee=None, action='create')


@app.route('/employees', methods=['POST'])
def employee_create():
    """직원 등록 처리"""
    try:
        employee = Employee(
            id=0,  # 자동 생성
            name=request.form.get('name', ''),
            photo=request.form.get('photo', 'https://i.pravatar.cc/150'),
            department=request.form.get('department', ''),
            position=request.form.get('position', ''),
            status=request.form.get('status', 'active'),
            hireDate=request.form.get('hireDate', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', '')
        )
        
        created_employee = employee_repo.create(employee)
        flash(f'{created_employee.name} 직원이 등록되었습니다.', 'success')
        return redirect(url_for('employee_detail', employee_id=created_employee.id))
    
    except Exception as e:
        flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employee_new'))


@app.route('/employees/<int:employee_id>/edit', methods=['GET'])
def employee_edit(employee_id):
    """직원 수정 폼"""
    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('index'))

    # Phase 6: 첨부파일 조회
    attachment_list = attachment_repo.get_by_employee_id(employee_id)

    return render_template('employee_form.html',
                           employee=employee,
                           action='update',
                           attachment_list=attachment_list)


@app.route('/employees/<int:employee_id>/update', methods=['POST'])
def employee_update(employee_id):
    """직원 수정 처리"""
    try:
        employee = Employee(
            id=employee_id,
            name=request.form.get('name', ''),
            photo=request.form.get('photo', 'https://i.pravatar.cc/150'),
            department=request.form.get('department', ''),
            position=request.form.get('position', ''),
            status=request.form.get('status', 'active'),
            hireDate=request.form.get('hireDate', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', '')
        )
        
        updated_employee = employee_repo.update(employee_id, employee)
        if updated_employee:
            flash(f'{updated_employee.name} 직원 정보가 수정되었습니다.', 'success')
            return redirect(url_for('employee_detail', employee_id=employee_id))
        else:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'직원 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employee_edit', employee_id=employee_id))


@app.route('/employees/<int:employee_id>/delete', methods=['POST'])
def employee_delete(employee_id):
    """직원 삭제 처리"""
    try:
        employee = employee_repo.get_by_id(employee_id)
        if employee:
            if employee_repo.delete(employee_id):
                flash(f'{employee.name} 직원이 삭제되었습니다.', 'success')
            else:
                flash('직원 삭제에 실패했습니다.', 'error')
        else:
            flash('직원을 찾을 수 없습니다.', 'error')
    
    except Exception as e:
        flash(f'직원 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/search')
def search():
    """직원 검색"""
    query = request.args.get('q', '')
    status_filter = request.args.get('status', '')
    department_filter = request.args.get('department', '')
    position_filter = request.args.get('position', '')
    
    # 필터 적용
    if status_filter or department_filter or position_filter:
        employees = employee_repo.filter_employees(
            department=department_filter if department_filter else None,
            position=position_filter if position_filter else None,
            status=status_filter if status_filter else None
        )
    elif query:
        employees = employee_repo.search(query)
    else:
        employees = employee_repo.get_all()
    
    stats = employee_repo.get_statistics()
    
    # AJAX 요청인 경우 JSON 반환
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'employees': [emp.to_dict() for emp in employees],
            'stats': stats
        })
    
    stats = employee_repo.get_statistics()
    dept_stats = employee_repo.get_department_statistics()
    recent_employees = employee_repo.get_recent_employees(limit=5)
    classification_options = classification_repo.get_all()
    return render_template('index.html', 
                         employees=employees, 
                         stats=stats, 
                         dept_stats=dept_stats, 
                         recent_employees=recent_employees, 
                         search_query=query,
                         classification_options=classification_options)


@app.errorhandler(404)
def not_found_error(error):
    """404 에러 핸들러"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return render_template('500.html'), 500


# 분류 옵션 관리 API
@app.route('/api/classification-options', methods=['GET'])
def get_classification_options():
    """분류 옵션 조회"""
    options = classification_repo.get_all()
    return jsonify(options)


@app.route('/api/classification-options/departments', methods=['POST'])
def add_department():
    """부서 추가"""
    data = request.get_json()
    department = data.get('department', '').strip()
    
    if not department:
        return jsonify({'error': '부서명이 필요합니다.'}), 400
    
    if classification_repo.add_department(department):
        return jsonify({'success': True, 'message': f'{department} 부서가 추가되었습니다.'}), 201
    else:
        return jsonify({'error': '이미 존재하는 부서입니다.'}), 400


@app.route('/api/classification-options/departments/<old_department>', methods=['PUT'])
def update_department(old_department):
    """부서 수정"""
    data = request.get_json()
    new_department = data.get('department', '').strip()
    
    if not new_department:
        return jsonify({'error': '새 부서명이 필요합니다.'}), 400
    
    if classification_repo.update_department(old_department, new_department):
        return jsonify({'success': True, 'message': f'부서가 {new_department}로 변경되었습니다.'}), 200
    else:
        return jsonify({'error': '부서를 찾을 수 없습니다.'}), 404


@app.route('/api/classification-options/departments/<department>', methods=['DELETE'])
def delete_department(department):
    """부서 삭제"""
    if classification_repo.delete_department(department):
        return jsonify({'success': True, 'message': f'{department} 부서가 삭제되었습니다.'}), 200
    else:
        return jsonify({'error': '부서를 찾을 수 없습니다.'}), 404


@app.route('/api/classification-options/positions', methods=['POST'])
def add_position():
    """직급 추가"""
    data = request.get_json()
    position = data.get('position', '').strip()
    
    if not position:
        return jsonify({'error': '직급명이 필요합니다.'}), 400
    
    if classification_repo.add_position(position):
        return jsonify({'success': True, 'message': f'{position} 직급이 추가되었습니다.'}), 201
    else:
        return jsonify({'error': '이미 존재하는 직급입니다.'}), 400


@app.route('/api/classification-options/positions/<old_position>', methods=['PUT'])
def update_position(old_position):
    """직급 수정"""
    data = request.get_json()
    new_position = data.get('position', '').strip()
    
    if not new_position:
        return jsonify({'error': '새 직급명이 필요합니다.'}), 400
    
    if classification_repo.update_position(old_position, new_position):
        return jsonify({'success': True, 'message': f'직급이 {new_position}로 변경되었습니다.'}), 200
    else:
        return jsonify({'error': '직급을 찾을 수 없습니다.'}), 404


@app.route('/api/classification-options/positions/<position>', methods=['DELETE'])
def delete_position(position):
    """직급 삭제"""
    if classification_repo.delete_position(position):
        return jsonify({'success': True, 'message': f'{position} 직급이 삭제되었습니다.'}), 200
    else:
        return jsonify({'error': '직급을 찾을 수 없습니다.'}), 404


@app.route('/api/classification-options/statuses', methods=['POST'])
def add_status():
    """상태 추가"""
    data = request.get_json()
    value = data.get('value', '').strip()
    label = data.get('label', '').strip()
    
    if not value or not label:
        return jsonify({'error': '상태 값과 라벨이 필요합니다.'}), 400
    
    if classification_repo.add_status(value, label):
        return jsonify({'success': True, 'message': f'{label} 상태가 추가되었습니다.'}), 201
    else:
        return jsonify({'error': '이미 존재하는 상태입니다.'}), 400


@app.route('/api/classification-options/statuses/<old_value>', methods=['PUT'])
def update_status(old_value):
    """상태 수정"""
    data = request.get_json()
    new_value = data.get('value', '').strip()
    new_label = data.get('label', '').strip()
    
    if not new_value or not new_label:
        return jsonify({'error': '새 상태 값과 라벨이 필요합니다.'}), 400
    
    if classification_repo.update_status(old_value, new_value, new_label):
        return jsonify({'success': True, 'message': f'상태가 {new_label}로 변경되었습니다.'}), 200
    else:
        return jsonify({'error': '상태를 찾을 수 없습니다.'}), 404


@app.route('/api/classification-options/statuses/<value>', methods=['DELETE'])
def delete_status(value):
    """상태 삭제"""
    if classification_repo.delete_status(value):
        return jsonify({'success': True, 'message': '상태가 삭제되었습니다.'}), 200
    else:
        return jsonify({'error': '상태를 찾을 수 없습니다.'}), 404


@app.route('/classification-options')
def classification_options_page():
    """분류 옵션 관리 페이지"""
    options = classification_repo.get_all()
    return render_template('classification_options.html', classification_options=options)


@app.context_processor
def utility_processor():
    """템플릿 유틸리티 함수"""
    from datetime import datetime, date

    def format_phone(phone):
        """전화번호 포맷팅"""
        return phone

    def get_status_badge_class(status):
        """상태 배지 CSS 클래스"""
        status_classes = {
            'active': 'badge-success',
            'warning': 'badge-warning',
            'expired': 'badge-danger'
        }
        return status_classes.get(status, 'badge-secondary')

    def get_status_text(status):
        """상태 텍스트"""
        status_texts = {
            'active': '정상',
            'warning': '대기',
            'expired': '만료'
        }
        return status_texts.get(status, status)

    def calculate_tenure(hire_date):
        """근속연수 계산 (입사일 기준)"""
        if not hire_date:
            return '정보 없음'

        try:
            if isinstance(hire_date, str):
                hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
            elif isinstance(hire_date, datetime):
                hire_date = hire_date.date()

            today = date.today()
            years = today.year - hire_date.year
            months = today.month - hire_date.month

            if today.day < hire_date.day:
                months -= 1

            if months < 0:
                years -= 1
                months += 12

            if years > 0 and months > 0:
                return f'{years}년 {months}개월'
            elif years > 0:
                return f'{years}년'
            elif months > 0:
                return f'{months}개월'
            else:
                return '1개월 미만'
        except (ValueError, TypeError):
            return '정보 없음'

    def format_date(date_value, format_str='%Y-%m-%d'):
        """날짜 포맷팅"""
        if not date_value:
            return '정보 없음'

        try:
            if isinstance(date_value, str):
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
            elif isinstance(date_value, (datetime, date)):
                date_obj = date_value
            else:
                return str(date_value)

            return date_obj.strftime(format_str)
        except (ValueError, TypeError):
            return str(date_value)

    def format_currency(amount):
        """금액 포맷팅 (천 단위 콤마)"""
        if amount is None:
            return '정보 없음'

        try:
            return f'{int(amount):,}원'
        except (ValueError, TypeError):
            return str(amount)

    def get_degree_label(degree):
        """학위 레이블 변환"""
        labels = {
            'bachelor': '학사',
            'master': '석사',
            'doctor': '박사',
            'associate': '전문학사',
            'high_school': '고졸'
        }
        return labels.get(degree, degree or '정보 없음')

    def get_level_label(level):
        """언어 수준 레이블 변환"""
        labels = {
            'advanced': '상급',
            'intermediate': '중급',
            'beginner': '초급',
            'native': '원어민'
        }
        return labels.get(level, level or '정보 없음')

    def get_relation_label(relation):
        """가족 관계 레이블 변환"""
        labels = {
            'spouse': '배우자',
            'child': '자녀',
            'parent': '부모',
            'sibling': '형제자매',
            'grandparent': '조부모',
            'other': '기타'
        }
        return labels.get(relation, relation or '정보 없음')

    def get_military_status_label(status):
        """병역 상태 레이블 변환"""
        labels = {
            'completed': '군필',
            'exempted': '면제',
            'serving': '복무중',
            'not_applicable': '해당없음'
        }
        return labels.get(status, status or '정보 없음')

    def get_branch_label(branch):
        """군 구분 레이블 변환"""
        labels = {
            'army': '육군',
            'navy': '해군',
            'airforce': '공군',
            'marine': '해병대',
            'auxiliary': '보충역'
        }
        return labels.get(branch, branch or '정보 없음')

    def get_gender_label(gender):
        """성별 레이블 변환"""
        labels = {
            'male': '남성',
            'female': '여성'
        }
        return labels.get(gender, gender or '정보 없음')

    def get_employment_type_label(emp_type):
        """고용형태 레이블 변환"""
        labels = {
            'regular': '정규직',
            'contract': '계약직',
            'parttime': '파트타임',
            'intern': '인턴'
        }
        return labels.get(emp_type, emp_type or '정보 없음')

    return {
        'format_phone': format_phone,
        'get_status_badge_class': get_status_badge_class,
        'get_status_text': get_status_text,
        'calculate_tenure': calculate_tenure,
        'format_date': format_date,
        'format_currency': format_currency,
        'get_degree_label': get_degree_label,
        'get_level_label': get_level_label,
        'get_relation_label': get_relation_label,
        'get_military_status_label': get_military_status_label,
        'get_branch_label': get_branch_label,
        'get_gender_label': get_gender_label,
        'get_employment_type_label': get_employment_type_label
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

