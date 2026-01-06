"""
Employee 관계 데이터 마이그레이션 스크립트

엑셀 데이터를 PostgreSQL DB로 마이그레이션합니다.
"""
import os
import sys
import pandas as pd
import numpy as np

# 프로젝트 루트 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 환경변수 설정
os.environ['DATABASE_URL'] = 'postgresql://hrm_user:hrm_secure_password_2024@localhost:6543/hrmanagement_db'

from app import create_app
from app.database import db
from sqlalchemy import text


def clean_value(val):
    """NaN, NaT 등을 None으로 변환"""
    if pd.isna(val) or val is np.nan:
        return None
    if isinstance(val, str) and val.strip() == '':
        return None
    return val


def clean_int(val):
    """정수값 정리"""
    val = clean_value(val)
    if val is None:
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def clean_float(val):
    """실수값 정리"""
    val = clean_value(val)
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def clean_bool(val):
    """불리언 값 정리"""
    val = clean_value(val)
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ('true', 'yes', '1', 'o', '예')
    return bool(val)


def migrate_table(df, table_name, column_mapping, value_processors=None):
    """범용 테이블 마이그레이션 함수"""
    if value_processors is None:
        value_processors = {}

    records = []
    for _, row in df.iterrows():
        record = {}
        for excel_col, db_col in column_mapping.items():
            val = row.get(excel_col)

            # 값 처리기가 있으면 적용
            if db_col in value_processors:
                val = value_processors[db_col](val)
            else:
                val = clean_value(val)

            record[db_col] = val
        records.append(record)

    return records


def migrate_educations(xlsx):
    """학력 데이터 마이그레이션"""
    from app.domains.employee.models import Education

    df = pd.read_excel(xlsx, sheet_name='Education')

    column_mapping = {
        'employee_id': 'employee_id',
        'school_type': 'school_type',
        'school_name': 'school_name',
        'major': 'major',
        'degree': 'degree',
        'admission_date': 'admission_date',
        'graduation_date': 'graduation_date',
        'graduation_status': 'graduation_status',
        'gpa': 'gpa',
        'location': 'location',
        'note': 'note'
    }

    count = 0
    for _, row in df.iterrows():
        edu = Education(
            employee_id=clean_int(row['employee_id']),
            school_type=clean_value(row.get('school_type')),
            school_name=clean_value(row.get('school_name')),
            major=clean_value(row.get('major')),
            degree=clean_value(row.get('degree')),
            admission_date=clean_value(row.get('admission_date')),
            graduation_date=clean_value(row.get('graduation_date')),
            graduation_status=clean_value(row.get('graduation_status')),
            gpa=clean_value(row.get('gpa')),
            location=clean_value(row.get('location')),
            note=clean_value(row.get('note'))
        )
        db.session.add(edu)
        count += 1

    db.session.commit()
    return count


def migrate_careers(xlsx):
    """경력 데이터 마이그레이션"""
    from app.domains.employee.models import Career

    df = pd.read_excel(xlsx, sheet_name='Career')

    count = 0
    for _, row in df.iterrows():
        career = Career(
            employee_id=clean_int(row['employee_id']),
            company_name=clean_value(row.get('company_name')),
            department=clean_value(row.get('department')),
            position=clean_value(row.get('position')),
            job_grade=clean_value(row.get('job_grade')),
            job_title=clean_value(row.get('job_title')),
            job_role=clean_value(row.get('job_role')),
            job_description=clean_value(row.get('job_description')),
            start_date=clean_value(row.get('start_date')),
            end_date=clean_value(row.get('end_date')),
            salary_type=clean_value(row.get('salary_type')),
            salary=clean_int(row.get('salary')),
            monthly_salary=clean_int(row.get('monthly_salary')),
            pay_step=clean_int(row.get('pay_step')) if row.get('pay_step') else None,
            resignation_reason=clean_value(row.get('resignation_reason')),
            is_current=clean_bool(row.get('is_current')),
            note=clean_value(row.get('note'))
        )
        db.session.add(career)
        count += 1

    db.session.commit()
    return count


def migrate_certificates(xlsx):
    """자격증 데이터 마이그레이션"""
    from app.domains.employee.models import Certificate

    df = pd.read_excel(xlsx, sheet_name='Certificate')

    count = 0
    for _, row in df.iterrows():
        cert = Certificate(
            employee_id=clean_int(row['employee_id']),
            certificate_name=clean_value(row.get('certificate_name')),
            issuing_organization=clean_value(row.get('issuing_organization')),
            certificate_number=clean_value(row.get('certificate_number')),
            acquisition_date=clean_value(row.get('acquisition_date')),
            expiry_date=clean_value(row.get('expiry_date')),
            grade=clean_value(row.get('grade')),
            note=clean_value(row.get('note'))
        )
        db.session.add(cert)
        count += 1

    db.session.commit()
    return count


def migrate_languages(xlsx):
    """어학 데이터 마이그레이션"""
    from app.domains.employee.models import Language

    df = pd.read_excel(xlsx, sheet_name='Language')

    count = 0
    for _, row in df.iterrows():
        lang = Language(
            employee_id=clean_int(row['employee_id']),
            language_name=clean_value(row.get('language_name')),
            exam_name=clean_value(row.get('exam_name')),
            score=clean_value(row.get('score')),
            level=clean_value(row.get('level')),
            acquisition_date=clean_value(row.get('acquisition_date')),
            expiry_date=clean_value(row.get('expiry_date')),
            note=clean_value(row.get('note'))
        )
        db.session.add(lang)
        count += 1

    db.session.commit()
    return count


def migrate_military_services(xlsx):
    """병역 데이터 마이그레이션"""
    from app.domains.employee.models import MilitaryService

    df = pd.read_excel(xlsx, sheet_name='MilitaryService')

    count = 0
    for _, row in df.iterrows():
        military = MilitaryService(
            employee_id=clean_int(row['employee_id']),
            military_status=clean_value(row.get('military_status')),
            service_type=clean_value(row.get('service_type')),
            branch=clean_value(row.get('branch')),
            rank=clean_value(row.get('rank')),
            enlistment_date=clean_value(row.get('enlistment_date')),
            discharge_date=clean_value(row.get('discharge_date')),
            discharge_reason=clean_value(row.get('discharge_reason')),
            exemption_reason=clean_value(row.get('exemption_reason')),
            note=clean_value(row.get('note'))
        )
        db.session.add(military)
        count += 1

    db.session.commit()
    return count


def migrate_salaries(xlsx):
    """급여 데이터 마이그레이션"""
    from app.domains.employee.models import Salary

    df = pd.read_excel(xlsx, sheet_name='Salary')

    count = 0
    for _, row in df.iterrows():
        salary = Salary(
            employee_id=clean_int(row['employee_id']),
            salary_type=clean_value(row.get('salary_type')),
            base_salary=clean_int(row.get('base_salary')),
            position_allowance=clean_int(row.get('position_allowance')),
            meal_allowance=clean_int(row.get('meal_allowance')),
            transportation_allowance=clean_int(row.get('transportation_allowance')),
            total_salary=clean_int(row.get('total_salary')),
            payment_day=clean_int(row.get('payment_day')) or 25,
            payment_method=clean_value(row.get('payment_method')),
            bank_account=clean_value(row.get('bank_account')),
            note=clean_value(row.get('note')),
            annual_salary=clean_int(row.get('annual_salary')),
            monthly_salary=clean_int(row.get('monthly_salary')),
            hourly_wage=clean_int(row.get('hourly_wage')),
            overtime_hours=clean_int(row.get('overtime_hours')),
            night_hours=clean_int(row.get('night_hours')),
            holiday_days=clean_int(row.get('holiday_days')),
            overtime_allowance=clean_int(row.get('overtime_allowance')),
            night_allowance=clean_int(row.get('night_allowance')),
            holiday_allowance=clean_int(row.get('holiday_allowance'))
        )
        db.session.add(salary)
        count += 1

    db.session.commit()
    return count


def migrate_benefits(xlsx):
    """복리후생 데이터 마이그레이션"""
    from app.domains.employee.models import Benefit

    df = pd.read_excel(xlsx, sheet_name='Benefit')

    count = 0
    for _, row in df.iterrows():
        benefit = Benefit(
            employee_id=clean_int(row['employee_id']),
            year=clean_int(row.get('year')),
            annual_leave_granted=clean_int(row.get('annual_leave_granted')),
            annual_leave_used=clean_int(row.get('annual_leave_used')),
            annual_leave_remaining=clean_int(row.get('annual_leave_remaining')),
            severance_type=clean_value(row.get('severance_type')),
            severance_method=clean_value(row.get('severance_method')),
            note=clean_value(row.get('note'))
        )
        db.session.add(benefit)
        count += 1

    db.session.commit()
    return count


def migrate_insurances(xlsx):
    """보험 데이터 마이그레이션"""
    from app.domains.employee.models import Insurance

    df = pd.read_excel(xlsx, sheet_name='Insurance')

    count = 0
    for _, row in df.iterrows():
        insurance = Insurance(
            employee_id=clean_int(row['employee_id']),
            national_pension=clean_bool(row.get('national_pension')),
            health_insurance=clean_bool(row.get('health_insurance')),
            employment_insurance=clean_bool(row.get('employment_insurance')),
            industrial_accident=clean_bool(row.get('industrial_accident')),
            national_pension_rate=clean_float(row.get('national_pension_rate')) or 4.5,
            health_insurance_rate=clean_float(row.get('health_insurance_rate')) or 3.545,
            long_term_care_rate=clean_float(row.get('long_term_care_rate')) or 0.9182,
            employment_insurance_rate=clean_float(row.get('employment_insurance_rate')) or 0.9,
            note=clean_value(row.get('note'))
        )
        db.session.add(insurance)
        count += 1

    db.session.commit()
    return count


def migrate_contracts(xlsx):
    """계약 데이터 마이그레이션"""
    from app.domains.employee.models import Contract

    df = pd.read_excel(xlsx, sheet_name='Contract')

    count = 0
    for _, row in df.iterrows():
        contract = Contract(
            employee_id=clean_int(row['employee_id']),
            contract_date=clean_value(row.get('contract_date')),
            contract_type=clean_value(row.get('contract_type')),
            contract_period=clean_value(row.get('contract_period')),
            employee_type=clean_value(row.get('employee_type')),
            work_type=clean_value(row.get('work_type')),
            note=clean_value(row.get('note'))
        )
        db.session.add(contract)
        count += 1

    db.session.commit()
    return count


def migrate_promotions(xlsx):
    """인사이동 데이터 마이그레이션"""
    from app.domains.employee.models import Promotion

    df = pd.read_excel(xlsx, sheet_name='Promotion')

    count = 0
    for _, row in df.iterrows():
        promotion = Promotion(
            employee_id=clean_int(row['employee_id']),
            effective_date=clean_value(row.get('effective_date')),
            promotion_type=clean_value(row.get('promotion_type')),
            from_department=clean_value(row.get('from_department')),
            to_department=clean_value(row.get('to_department')),
            from_position=clean_value(row.get('from_position')),
            to_position=clean_value(row.get('to_position')),
            job_role=clean_value(row.get('job_role')),
            reason=clean_value(row.get('reason')),
            note=clean_value(row.get('note'))
        )
        db.session.add(promotion)
        count += 1

    db.session.commit()
    return count


def migrate_evaluations(xlsx):
    """인사평가 데이터 마이그레이션"""
    from app.domains.employee.models import Evaluation

    df = pd.read_excel(xlsx, sheet_name='Evaluation')

    count = 0
    for _, row in df.iterrows():
        evaluation = Evaluation(
            employee_id=clean_int(row['employee_id']),
            year=clean_int(row.get('year')),
            q1_grade=clean_value(row.get('q1_grade')),
            q2_grade=clean_value(row.get('q2_grade')),
            q3_grade=clean_value(row.get('q3_grade')),
            q4_grade=clean_value(row.get('q4_grade')),
            overall_grade=clean_value(row.get('overall_grade')),
            salary_negotiation=clean_value(row.get('salary_negotiation')),
            note=clean_value(row.get('note'))
        )
        db.session.add(evaluation)
        count += 1

    db.session.commit()
    return count


def migrate_trainings(xlsx):
    """교육이력 데이터 마이그레이션"""
    from app.domains.employee.models import Training

    df = pd.read_excel(xlsx, sheet_name='Training')

    count = 0
    for _, row in df.iterrows():
        training = Training(
            employee_id=clean_int(row['employee_id']),
            training_date=clean_value(row.get('training_date')),
            training_name=clean_value(row.get('training_name')),
            institution=clean_value(row.get('institution')),
            hours=clean_int(row.get('hours')),
            completion_status=clean_value(row.get('completion_status')),
            note=clean_value(row.get('note'))
        )
        db.session.add(training)
        count += 1

    db.session.commit()
    return count


def migrate_attendances(xlsx):
    """근태 데이터 마이그레이션"""
    from app.domains.employee.models import Attendance

    df = pd.read_excel(xlsx, sheet_name='Attendance')

    count = 0
    for _, row in df.iterrows():
        attendance = Attendance(
            employee_id=clean_int(row['employee_id']),
            year=clean_int(row.get('year')),
            month=clean_int(row.get('month')),
            work_days=clean_int(row.get('work_days')),
            absent_days=clean_int(row.get('absent_days')),
            late_count=clean_int(row.get('late_count')),
            early_leave_count=clean_int(row.get('early_leave_count')),
            annual_leave_used=clean_int(row.get('annual_leave_used')),
            note=clean_value(row.get('note'))
        )
        db.session.add(attendance)
        count += 1

    db.session.commit()
    return count


def migrate_hr_projects(xlsx):
    """인사이력 프로젝트 데이터 마이그레이션"""
    from app.domains.employee.models import HrProject

    df = pd.read_excel(xlsx, sheet_name='HrProject')

    count = 0
    for _, row in df.iterrows():
        project = HrProject(
            employee_id=clean_int(row['employee_id']),
            project_name=clean_value(row.get('project_name')),
            start_date=clean_value(row.get('start_date')),
            end_date=clean_value(row.get('end_date')),
            duration=clean_value(row.get('duration')),
            role=clean_value(row.get('role')),
            duty=clean_value(row.get('duty')),
            client=clean_value(row.get('client')),
            note=clean_value(row.get('note'))
        )
        db.session.add(project)
        count += 1

    db.session.commit()
    return count


def migrate_awards(xlsx):
    """수상 데이터 마이그레이션"""
    from app.domains.employee.models import Award

    df = pd.read_excel(xlsx, sheet_name='Award')

    count = 0
    for _, row in df.iterrows():
        award = Award(
            employee_id=clean_int(row['employee_id']),
            award_date=clean_value(row.get('award_date')),
            award_name=clean_value(row.get('award_name')),
            institution=clean_value(row.get('institution')),
            note=clean_value(row.get('note'))
        )
        db.session.add(award)
        count += 1

    db.session.commit()
    return count


def migrate_assets(xlsx):
    """자산배정 데이터 마이그레이션"""
    from app.domains.employee.models import Asset

    df = pd.read_excel(xlsx, sheet_name='Asset')

    count = 0
    for _, row in df.iterrows():
        asset = Asset(
            employee_id=clean_int(row['employee_id']),
            issue_date=clean_value(row.get('issue_date')),
            item_name=clean_value(row.get('item_name')),
            model=clean_value(row.get('model')),
            serial_number=clean_value(row.get('serial_number')),
            status=clean_value(row.get('status')),
            note=clean_value(row.get('note'))
        )
        db.session.add(asset)
        count += 1

    db.session.commit()
    return count


def migrate_salary_histories(xlsx):
    """연봉계약이력 데이터 마이그레이션"""
    from app.domains.employee.models import SalaryHistory

    df = pd.read_excel(xlsx, sheet_name='SalaryHistory')

    count = 0
    for _, row in df.iterrows():
        history = SalaryHistory(
            employee_id=clean_int(row['employee_id']),
            contract_year=clean_int(row.get('contract_year')),
            annual_salary=clean_int(row.get('annual_salary')),
            bonus=clean_int(row.get('bonus')),
            total_amount=clean_int(row.get('total_amount')),
            contract_period=clean_value(row.get('contract_period')),
            note=clean_value(row.get('note'))
        )
        db.session.add(history)
        count += 1

    db.session.commit()
    return count


def migrate_salary_payments(xlsx):
    """급여지급이력 데이터 마이그레이션"""
    from app.domains.employee.models import SalaryPayment

    df = pd.read_excel(xlsx, sheet_name='SalaryPayment')

    count = 0
    for _, row in df.iterrows():
        payment = SalaryPayment(
            employee_id=clean_int(row['employee_id']),
            payment_date=clean_value(row.get('payment_date')),
            payment_period=clean_value(row.get('payment_period')),
            base_salary=clean_int(row.get('base_salary')),
            allowances=clean_int(row.get('allowances')),
            gross_pay=clean_int(row.get('gross_pay')),
            insurance=clean_int(row.get('insurance')),
            income_tax=clean_int(row.get('income_tax')),
            total_deduction=clean_int(row.get('total_deduction')),
            net_pay=clean_int(row.get('net_pay')),
            note=clean_value(row.get('note'))
        )
        db.session.add(payment)
        count += 1

    db.session.commit()
    return count


def main():
    """메인 실행 함수"""
    app = create_app()

    with app.app_context():
        xlsx_path = '.dev_docs/sample/hr_test_data_complete_v2.xlsx'
        xlsx = pd.ExcelFile(xlsx_path)

        print("=" * 50)
        print("Employee 관계 데이터 마이그레이션 시작")
        print("=" * 50)

        migrations = [
            ('Education (학력)', migrate_educations),
            ('Career (경력)', migrate_careers),
            ('Certificate (자격증)', migrate_certificates),
            ('Language (어학)', migrate_languages),
            ('MilitaryService (병역)', migrate_military_services),
            ('Salary (급여)', migrate_salaries),
            ('Benefit (복리후생)', migrate_benefits),
            ('Insurance (보험)', migrate_insurances),
            ('Contract (계약)', migrate_contracts),
            ('Promotion (인사이동)', migrate_promotions),
            ('Evaluation (인사평가)', migrate_evaluations),
            ('Training (교육이력)', migrate_trainings),
            ('Attendance (근태)', migrate_attendances),
            ('HrProject (프로젝트)', migrate_hr_projects),
            ('Award (수상)', migrate_awards),
            ('Asset (자산)', migrate_assets),
            ('SalaryHistory (연봉이력)', migrate_salary_histories),
            ('SalaryPayment (급여지급)', migrate_salary_payments),
        ]

        results = []
        for name, func in migrations:
            try:
                count = func(xlsx)
                print(f"  {name}: {count}건 마이그레이션 완료")
                results.append((name, count, 'SUCCESS'))
            except Exception as e:
                print(f"  {name}: 오류 - {str(e)}")
                results.append((name, 0, f'ERROR: {str(e)[:50]}'))
                db.session.rollback()

        print("=" * 50)
        print("마이그레이션 결과 요약")
        print("=" * 50)
        total = 0
        for name, count, status in results:
            print(f"  {name}: {count}건 ({status})")
            if status == 'SUCCESS':
                total += count
        print(f"\n총 {total}건 마이그레이션 완료")


if __name__ == '__main__':
    main()
