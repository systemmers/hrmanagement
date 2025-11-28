"""
JSON to SQLite 마이그레이션 스크립트

기존 JSON 파일의 데이터를 SQLite 데이터베이스로 마이그레이션합니다.
"""
import json
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.database import db
from app.models import (
    Employee, Education, Career, Certificate, FamilyMember,
    Language, MilitaryService, Salary, Benefit, Contract,
    SalaryHistory, Promotion, Evaluation, Training, Attendance,
    Insurance, Project, Award, Asset, SalaryPayment, Attachment,
    ClassificationOption
)


def load_json(file_path):
    """JSON 파일 로드"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def migrate_employees(app):
    """직원 데이터 마이그레이션"""
    print("  - employees.json 마이그레이션...")
    employees_data = load_json(app.config['EMPLOYEES_JSON'])
    extended_path = app.config.get('EMPLOYEES_EXTENDED_JSON', '')
    extended_data = load_json(extended_path) if extended_path else []

    # 확장 데이터를 ID로 인덱싱
    extended_map = {e.get('id'): e for e in extended_data}

    count = 0
    for emp in employees_data:
        emp_id = emp.get('id')
        # 확장 데이터 병합
        if emp_id in extended_map:
            emp.update(extended_map[emp_id])

        # Employee 객체 직접 생성 (JSON 필드명이 camelCase)
        employee = Employee(
            id=emp.get('id'),
            name=emp.get('name'),
            photo=emp.get('photo'),
            department=emp.get('department'),
            position=emp.get('position'),
            status=emp.get('status'),
            hire_date=emp.get('hireDate'),
            phone=emp.get('phone'),
            email=emp.get('email'),
            english_name=emp.get('englishName'),
            chinese_name=emp.get('chineseName'),
            birth_date=emp.get('birthDate'),
            lunar_birth=emp.get('lunarBirth', False),
            gender=emp.get('gender'),
            mobile_phone=emp.get('mobilePhone'),
            home_phone=emp.get('homePhone'),
            address=emp.get('address'),
            detailed_address=emp.get('detailedAddress'),
            postal_code=emp.get('postalCode'),
            resident_number=emp.get('residentNumber'),
            nationality=emp.get('nationality'),
            blood_type=emp.get('bloodType'),
            religion=emp.get('religion'),
            hobby=emp.get('hobby'),
            specialty=emp.get('specialty'),
            disability_info=emp.get('disabilityInfo'),
        )
        db.session.add(employee)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_education(app):
    """학력 데이터 마이그레이션"""
    print("  - education.json 마이그레이션...")
    data = load_json(app.config.get('EDUCATION_JSON', ''))
    count = 0

    for item in data:
        record = Education(
            employee_id=item.get('employee_id'),
            school_type=item.get('school_type'),
            school_name=item.get('school'),  # JSON은 'school'
            major=item.get('major'),
            degree=item.get('degree'),
            admission_date=item.get('admission_date'),
            graduation_date=item.get('graduation_year'),  # JSON은 'graduation_year'
            graduation_status=item.get('graduation_status'),
            location=item.get('location'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_career(app):
    """경력 데이터 마이그레이션"""
    print("  - careers.json 마이그레이션...")
    data = load_json(app.config.get('CAREERS_JSON', ''))
    count = 0

    for item in data:
        record = Career(
            employee_id=item.get('employee_id'),
            company_name=item.get('company'),  # JSON은 'company'
            department=item.get('department'),
            position=item.get('position'),
            job_description=item.get('job_description'),
            start_date=item.get('start_date'),
            end_date=item.get('end_date'),
            resignation_reason=item.get('resignation_reason'),
            is_current=item.get('is_current', False),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_certificate(app):
    """자격증 데이터 마이그레이션"""
    print("  - certificates.json 마이그레이션...")
    data = load_json(app.config.get('CERTIFICATES_JSON', ''))
    count = 0

    for item in data:
        record = Certificate(
            employee_id=item.get('employee_id'),
            certificate_name=item.get('name'),  # JSON은 'name'
            issuing_organization=item.get('issuer'),  # JSON은 'issuer'
            certificate_number=item.get('certificate_number'),
            acquisition_date=item.get('issue_date'),  # JSON은 'issue_date'
            expiry_date=item.get('expiry_date'),
            grade=item.get('grade'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_family_member(app):
    """가족 데이터 마이그레이션"""
    print("  - family_members.json 마이그레이션...")
    data = load_json(app.config.get('FAMILY_MEMBERS_JSON', ''))
    count = 0

    for item in data:
        record = FamilyMember(
            employee_id=item.get('employee_id'),
            relation=item.get('relation'),
            name=item.get('name'),
            birth_date=item.get('birth_date'),
            occupation=item.get('occupation'),
            contact=item.get('contact'),
            is_cohabitant=item.get('is_cohabitant', False),
            is_dependent=item.get('is_dependent', False),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_language(app):
    """어학 데이터 마이그레이션"""
    print("  - languages.json 마이그레이션...")
    data = load_json(app.config.get('LANGUAGES_JSON', ''))
    count = 0

    for item in data:
        record = Language(
            employee_id=item.get('employee_id'),
            language_name=item.get('language'),  # JSON은 'language'
            exam_name=item.get('test_name'),  # JSON은 'test_name'
            score=item.get('score'),
            level=item.get('level'),
            acquisition_date=item.get('test_date'),  # JSON은 'test_date'
            expiry_date=item.get('expiry_date'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_military_service(app):
    """병역 데이터 마이그레이션"""
    print("  - military.json 마이그레이션...")
    data = load_json(app.config.get('MILITARY_JSON', ''))
    count = 0

    for item in data:
        record = MilitaryService(
            employee_id=item.get('employee_id'),
            military_status=item.get('military_status'),
            service_type=item.get('service_type'),
            branch=item.get('branch'),
            rank=item.get('rank'),
            enlistment_date=item.get('enlistment_date'),
            discharge_date=item.get('discharge_date'),
            discharge_reason=item.get('discharge_reason'),
            exemption_reason=item.get('exemption_reason'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_salary(app):
    """급여 데이터 마이그레이션 (1:1)"""
    print("  - salaries.json 마이그레이션...")
    data = load_json(app.config.get('SALARIES_JSON', ''))
    count = 0

    for item in data:
        record = Salary(
            employee_id=item.get('employee_id'),
            salary_type=item.get('salary_type'),
            base_salary=item.get('base_salary', 0),
            position_allowance=item.get('position_allowance', 0),
            meal_allowance=item.get('meal_allowance', 0),
            transportation_allowance=item.get('transportation_allowance', 0),
            total_salary=item.get('total_salary', 0),
            payment_day=item.get('payment_day', 25),
            payment_method=item.get('payment_method'),
            bank_account=item.get('bank_account'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_benefit(app):
    """복리후생 데이터 마이그레이션 (1:1)"""
    print("  - benefits.json 마이그레이션...")
    data = load_json(app.config.get('BENEFITS_JSON', ''))
    count = 0

    for item in data:
        record = Benefit(
            employee_id=item.get('employee_id'),
            year=item.get('year'),
            annual_leave_granted=item.get('annual_leave_granted', 0),
            annual_leave_used=item.get('annual_leave_used', 0),
            annual_leave_remaining=item.get('annual_leave_remaining', 0),
            severance_type=item.get('severance_type'),
            severance_method=item.get('severance_method'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_contract(app):
    """계약 데이터 마이그레이션 (1:1)"""
    print("  - contracts.json 마이그레이션...")
    data = load_json(app.config.get('CONTRACTS_JSON', ''))
    count = 0

    for item in data:
        record = Contract(
            employee_id=item.get('employee_id'),
            contract_date=item.get('contract_date'),
            contract_type=item.get('contract_type'),
            contract_period=item.get('contract_period'),
            employee_type=item.get('employee_type'),
            work_type=item.get('work_type'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_insurance(app):
    """보험 데이터 마이그레이션 (1:1)"""
    print("  - insurances.json 마이그레이션...")
    data = load_json(app.config.get('INSURANCES_JSON', ''))
    count = 0

    for item in data:
        record = Insurance(
            employee_id=item.get('employee_id'),
            national_pension=item.get('national_pension', True),
            health_insurance=item.get('health_insurance', True),
            employment_insurance=item.get('employment_insurance', True),
            industrial_accident=item.get('industrial_accident', True),
            national_pension_rate=item.get('national_pension_rate', 4.5),
            health_insurance_rate=item.get('health_insurance_rate', 3.545),
            long_term_care_rate=item.get('long_term_care_rate', 0.9182),
            employment_insurance_rate=item.get('employment_insurance_rate', 0.9),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_salary_history(app):
    """연봉 계약 이력 마이그레이션"""
    print("  - salary_history.json 마이그레이션...")
    data = load_json(app.config.get('SALARY_HISTORY_JSON', ''))
    count = 0

    for item in data:
        record = SalaryHistory(
            employee_id=item.get('employee_id'),
            contract_year=item.get('contract_year'),
            annual_salary=item.get('annual_salary', 0),
            bonus=item.get('bonus', 0),
            total_amount=item.get('total_amount', 0),
            contract_period=item.get('contract_period'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_promotion(app):
    """발령/인사이동 마이그레이션"""
    print("  - promotions.json 마이그레이션...")
    data = load_json(app.config.get('PROMOTIONS_JSON', ''))
    count = 0

    for item in data:
        record = Promotion(
            employee_id=item.get('employee_id'),
            effective_date=item.get('effective_date'),
            promotion_type=item.get('promotion_type'),
            from_department=item.get('from_department'),
            to_department=item.get('to_department'),
            from_position=item.get('from_position'),
            to_position=item.get('to_position'),
            job_role=item.get('job_role'),
            reason=item.get('reason'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_evaluation(app):
    """인사평가 마이그레이션"""
    print("  - evaluations.json 마이그레이션...")
    data = load_json(app.config.get('EVALUATIONS_JSON', ''))
    count = 0

    for item in data:
        record = Evaluation(
            employee_id=item.get('employee_id'),
            year=item.get('year'),
            q1_grade=item.get('q1_grade'),
            q2_grade=item.get('q2_grade'),
            q3_grade=item.get('q3_grade'),
            q4_grade=item.get('q4_grade'),
            overall_grade=item.get('overall_grade'),
            salary_negotiation=item.get('salary_negotiation'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_training(app):
    """교육 이력 마이그레이션"""
    print("  - trainings.json 마이그레이션...")
    data = load_json(app.config.get('TRAININGS_JSON', ''))
    count = 0

    for item in data:
        record = Training(
            employee_id=item.get('employee_id'),
            training_date=item.get('training_date'),
            training_name=item.get('training_name'),
            institution=item.get('institution'),
            hours=item.get('hours', 0),
            completion_status=item.get('completion_status'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_attendance(app):
    """근태 마이그레이션 (월별)"""
    print("  - attendance.json 마이그레이션...")
    data = load_json(app.config.get('ATTENDANCE_JSON', ''))
    count = 0

    for item in data:
        record = Attendance(
            employee_id=item.get('employee_id'),
            year=item.get('year'),
            month=item.get('month'),
            work_days=item.get('work_days', 0),
            absent_days=item.get('absent_days', 0),
            late_count=item.get('late_count', 0),
            early_leave_count=item.get('early_leave_count', 0),
            annual_leave_used=item.get('annual_leave_used', 0),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_project(app):
    """프로젝트 마이그레이션"""
    print("  - projects.json 마이그레이션...")
    data = load_json(app.config.get('PROJECTS_JSON', ''))
    count = 0

    for item in data:
        record = Project(
            employee_id=item.get('employee_id'),
            project_name=item.get('project_name'),
            start_date=item.get('start_date'),
            end_date=item.get('end_date'),
            duration=item.get('duration'),
            role=item.get('role'),
            duty=item.get('duty'),
            client=item.get('client'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_award(app):
    """수상 마이그레이션"""
    print("  - awards.json 마이그레이션...")
    data = load_json(app.config.get('AWARDS_JSON', ''))
    count = 0

    for item in data:
        record = Award(
            employee_id=item.get('employee_id'),
            award_date=item.get('award_date'),
            award_name=item.get('award_name'),
            institution=item.get('institution'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_asset(app):
    """자산 마이그레이션"""
    print("  - assets.json 마이그레이션...")
    data = load_json(app.config.get('ASSETS_JSON', ''))
    count = 0

    for item in data:
        record = Asset(
            employee_id=item.get('employee_id'),
            issue_date=item.get('issue_date'),
            item_name=item.get('item_name'),
            model=item.get('model'),
            serial_number=item.get('serial_number'),
            status=item.get('status'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_salary_payment(app):
    """급여 지급 마이그레이션"""
    print("  - salary_payments.json 마이그레이션...")
    data = load_json(app.config.get('SALARY_PAYMENTS_JSON', ''))
    count = 0

    for item in data:
        record = SalaryPayment(
            employee_id=item.get('employee_id'),
            payment_date=item.get('payment_date'),
            payment_period=item.get('payment_period'),
            base_salary=item.get('base_salary', 0),
            allowances=item.get('allowances', 0),
            gross_pay=item.get('gross_pay', 0),
            insurance=item.get('insurance', 0),
            income_tax=item.get('income_tax', 0),
            total_deduction=item.get('total_deduction', 0),
            net_pay=item.get('net_pay', 0),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_attachment(app):
    """첨부파일 마이그레이션"""
    print("  - attachments.json 마이그레이션...")
    data = load_json(app.config.get('ATTACHMENTS_JSON', ''))
    count = 0

    for item in data:
        record = Attachment(
            employee_id=item.get('employee_id'),
            file_name=item.get('file_name'),
            file_path=item.get('file_path'),
            file_type=item.get('file_type'),
            file_size=item.get('file_size', 0),
            category=item.get('category'),
            upload_date=item.get('upload_date'),
            note=item.get('note'),
        )
        db.session.add(record)
        count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def migrate_classification_options(app):
    """분류 옵션 마이그레이션"""
    print("  - classification_options.json 마이그레이션...")
    data = load_json(app.config['CLASSIFICATION_OPTIONS_JSON'])

    count = 0
    category_mapping = {
        'departments': 'department',
        'positions': 'position',
        'statuses': 'status'
    }

    for category_key, category_name in category_mapping.items():
        items = data.get(category_key, [])

        for i, item in enumerate(items):
            if isinstance(item, dict):
                value = item.get('value', '')
                label = item.get('label', value)
            else:
                value = str(item)
                label = str(item)

            option = ClassificationOption(
                category=category_name,
                value=value,
                label=label,
                sort_order=i
            )
            db.session.add(option)
            count += 1

    db.session.commit()
    print(f"    {count}건 완료")
    return count


def main():
    """메인 마이그레이션 함수"""
    print("=" * 60)
    print("JSON -> SQLite 데이터 마이그레이션 시작")
    print("=" * 60)

    app = create_app('development')

    with app.app_context():
        # 기존 테이블 삭제 후 재생성
        print("\n1. 데이터베이스 테이블 재생성...")
        db.drop_all()
        db.create_all()
        print("   완료")

        # 마이그레이션 실행
        print("\n2. 데이터 마이그레이션...")
        total = 0

        # 직원 데이터 (먼저 마이그레이션 - FK 참조용)
        total += migrate_employees(app)

        # 분류 옵션
        total += migrate_classification_options(app)

        # Phase 1 관계형 데이터
        total += migrate_education(app)
        total += migrate_career(app)
        total += migrate_certificate(app)
        total += migrate_family_member(app)
        total += migrate_language(app)
        total += migrate_military_service(app)

        # Phase 1 1:1 관계 데이터
        total += migrate_salary(app)
        total += migrate_benefit(app)
        total += migrate_contract(app)
        total += migrate_insurance(app)

        # Phase 2-6 데이터
        total += migrate_salary_history(app)
        total += migrate_promotion(app)
        total += migrate_evaluation(app)
        total += migrate_training(app)
        total += migrate_attendance(app)
        total += migrate_project(app)
        total += migrate_award(app)
        total += migrate_asset(app)
        total += migrate_salary_payment(app)
        total += migrate_attachment(app)

        print("\n" + "=" * 60)
        print(f"마이그레이션 완료! 총 {total}건의 레코드 마이그레이션됨")
        print("=" * 60)

        # 검증
        print("\n3. 마이그레이션 검증...")
        print(f"   - 직원 수: {Employee.query.count()}")
        print(f"   - 학력 수: {Education.query.count()}")
        print(f"   - 경력 수: {Career.query.count()}")
        print(f"   - 자격증 수: {Certificate.query.count()}")
        print(f"   - 가족 수: {FamilyMember.query.count()}")
        print(f"   - 어학 수: {Language.query.count()}")
        print(f"   - 병역 수: {MilitaryService.query.count()}")
        print(f"   - 급여정보 수: {Salary.query.count()}")
        print(f"   - 복리후생 수: {Benefit.query.count()}")
        print(f"   - 계약정보 수: {Contract.query.count()}")
        print(f"   - 보험정보 수: {Insurance.query.count()}")
        print(f"   - 연봉이력 수: {SalaryHistory.query.count()}")
        print(f"   - 발령이력 수: {Promotion.query.count()}")
        print(f"   - 평가이력 수: {Evaluation.query.count()}")
        print(f"   - 교육이력 수: {Training.query.count()}")
        print(f"   - 근태정보 수: {Attendance.query.count()}")
        print(f"   - 프로젝트 수: {Project.query.count()}")
        print(f"   - 수상이력 수: {Award.query.count()}")
        print(f"   - 자산배정 수: {Asset.query.count()}")
        print(f"   - 급여지급 수: {SalaryPayment.query.count()}")
        print(f"   - 첨부파일 수: {Attachment.query.count()}")
        print(f"   - 분류옵션 수: {ClassificationOption.query.count()}")


if __name__ == '__main__':
    main()
