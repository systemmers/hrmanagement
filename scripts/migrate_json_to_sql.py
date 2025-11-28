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


def camel_to_snake(name):
    """camelCase를 snake_case로 변환"""
    result = []
    for char in name:
        if char.isupper():
            result.append('_')
            result.append(char.lower())
        else:
            result.append(char)
    return ''.join(result).lstrip('_')


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


def migrate_generic(app, json_key, model_class, field_mapping=None, name=''):
    """
    범용 마이그레이션 함수

    Args:
        json_key: config의 JSON 파일 경로 키
        model_class: SQLAlchemy 모델 클래스
        field_mapping: JSON 필드명 -> 모델 필드명 매핑 (optional)
        name: 로그 출력용 이름
    """
    print(f"  - {json_key} 마이그레이션...")
    file_path = app.config.get(json_key)
    if not file_path:
        print(f"    설정 없음, 건너뜀")
        return 0

    data = load_json(file_path)
    if not data:
        print(f"    데이터 없음")
        return 0

    count = 0
    for item in data:
        # 필드 매핑 적용
        mapped_item = {}
        for json_key_name, value in item.items():
            if field_mapping and json_key_name in field_mapping:
                model_key = field_mapping[json_key_name]
            else:
                model_key = json_key_name
            mapped_item[model_key] = value

        # 모델 인스턴스 생성
        try:
            record = model_class(**mapped_item)
            db.session.add(record)
            count += 1
        except Exception as e:
            print(f"    경고: {item} - {e}")
            continue

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

        # 관계형 데이터 (커스텀 매핑 필요)
        total += migrate_education(app)
        total += migrate_career(app)
        total += migrate_certificate(app)
        total += migrate_family_member(app)
        total += migrate_language(app)
        total += migrate_military_service(app)

        # 1:1 관계 데이터 (JSON과 모델 필드가 대응)
        total += migrate_generic(app, 'SALARIES_JSON', Salary, name='salaries')
        total += migrate_generic(app, 'BENEFITS_JSON', Benefit, name='benefits')
        total += migrate_generic(app, 'CONTRACTS_JSON', Contract, name='contracts')
        total += migrate_generic(app, 'INSURANCES_JSON', Insurance, name='insurances')

        # Phase 2-6 데이터
        total += migrate_generic(app, 'SALARY_HISTORY_JSON', SalaryHistory, name='salary_history')
        total += migrate_generic(app, 'PROMOTIONS_JSON', Promotion, name='promotions')
        total += migrate_generic(app, 'EVALUATIONS_JSON', Evaluation, name='evaluations')
        total += migrate_generic(app, 'TRAININGS_JSON', Training, name='trainings')
        total += migrate_generic(app, 'ATTENDANCE_JSON', Attendance, name='attendance')
        total += migrate_generic(app, 'PROJECTS_JSON', Project, name='projects')
        total += migrate_generic(app, 'AWARDS_JSON', Award, name='awards')
        total += migrate_generic(app, 'ASSETS_JSON', Asset, name='assets')
        total += migrate_generic(app, 'SALARY_PAYMENTS_JSON', SalaryPayment, name='salary_payments')
        total += migrate_generic(app, 'ATTACHMENTS_JSON', Attachment, name='attachments')

        print("\n" + "=" * 60)
        print(f"마이그레이션 완료! 총 {total}건의 레코드 마이그레이션됨")
        print("=" * 60)

        # 검증
        print("\n3. 마이그레이션 검증...")
        print(f"   - 직원 수: {Employee.query.count()}")
        print(f"   - 학력 수: {Education.query.count()}")
        print(f"   - 경력 수: {Career.query.count()}")
        print(f"   - 자격증 수: {Certificate.query.count()}")
        print(f"   - 분류 옵션 수: {ClassificationOption.query.count()}")


if __name__ == '__main__':
    main()
