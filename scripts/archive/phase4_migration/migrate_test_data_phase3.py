"""
HR Management System - Test Data Migration Phase 3
Migrates relationship data from hr_test_data_complete_v2.xlsx to PostgreSQL
"""

import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql://hrm_user:hrm_secure_password_2024@localhost:6543/hrmanagement_db'

from app import create_app
from app.database import db
from sqlalchemy import text


def load_excel():
    """Load Excel file and return all sheets as dict"""
    excel_path = os.path.join(os.path.dirname(__file__), '..', '.dev_docs', 'sample', 'hr_test_data_complete_v2.xlsx')
    xl = pd.ExcelFile(excel_path)
    sheets = {}
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet_name)
        sheets[sheet_name] = df
    return sheets


def clean_value(val, default=''):
    """Clean NaN values"""
    if pd.isna(val):
        return default
    return val


def migrate_generic(sheets, sheet_name, table_name, column_map, fk_column='employee_id'):
    """Generic migration function for simple 1:N relationships"""
    df = sheets.get(sheet_name)
    if df is None:
        print(f"  {table_name}: No {sheet_name} sheet found")
        return 0

    count = 0
    for _, row in df.iterrows():
        data = {}
        for db_col, excel_col in column_map.items():
            if callable(excel_col):
                data[db_col] = excel_col(row)
            else:
                val = row.get(excel_col, '')
                if db_col in ['id', fk_column] and pd.notna(val):
                    data[db_col] = int(val)
                elif db_col.endswith('_date') and pd.notna(val):
                    data[db_col] = str(val)[:10] if val else None
                elif pd.isna(val):
                    continue
                else:
                    data[db_col] = val

        # Build INSERT
        if not data:
            continue

        columns = list(data.keys())
        placeholders = ', '.join([f':{k}' for k in columns])
        col_names = ', '.join(columns)

        try:
            sql = text(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})")
            db.session.execute(sql, data)
            count += 1
        except Exception as e:
            print(f"    Error inserting into {table_name}: {str(e)[:80]}")
            db.session.rollback()

    db.session.commit()
    return count


def migrate_salaries(sheets):
    """Migrate salaries table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'base_salary': 'base_salary',
        'position_allowance': 'position_allowance',
        'meal_allowance': 'meal_allowance',
        'transportation_allowance': 'transportation_allowance',
        'bonus_rate': 'bonus_rate',
        'effective_date': 'effective_date',
    }
    return migrate_generic(sheets, 'Salary', 'salaries', column_map)


def migrate_benefits(sheets):
    """Migrate benefits table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'annual_leave': 'annual_leave',
        'sick_leave': 'sick_leave',
        'health_checkup': 'health_checkup',
        'meal_support': 'meal_support',
        'commute_support': 'commute_support',
        'housing_support': 'housing_support',
        'education_support': 'education_support',
    }
    return migrate_generic(sheets, 'Benefit', 'benefits', column_map)


def migrate_insurances(sheets):
    """Migrate insurances table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'national_pension': 'national_pension',
        'health_insurance': 'health_insurance',
        'employment_insurance': 'employment_insurance',
        'industrial_accident': 'industrial_accident',
        'enrollment_date': 'enrollment_date',
    }
    return migrate_generic(sheets, 'Insurance', 'insurances', column_map)


def migrate_contracts(sheets):
    """Migrate contracts table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'contract_type': 'contract_type',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'working_hours': 'working_hours',
        'probation_period': 'probation_period',
        'contract_status': 'contract_status',
    }
    return migrate_generic(sheets, 'Contract', 'contracts', column_map)


def migrate_educations(sheets):
    """Migrate educations table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'school_name': 'school_name',
        'degree': 'degree',
        'major': 'major',
        'entrance_date': 'entrance_date',
        'graduation_date': 'graduation_date',
        'status': 'graduation_status',
    }
    return migrate_generic(sheets, 'Education', 'educations', column_map)


def migrate_careers(sheets):
    """Migrate careers table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'company_name': 'company_name',
        'department': 'department',
        'position': 'position',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'job_description': 'job_description',
        'reason_for_leaving': 'reason_for_leaving',
    }
    return migrate_generic(sheets, 'Career', 'careers', column_map)


def migrate_certificates(sheets):
    """Migrate certificates table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'name': 'certificate_name',
        'issuing_organization': 'issuing_organization',
        'issue_date': 'issue_date',
        'expiry_date': 'expiry_date',
        'certificate_number': 'certificate_number',
    }
    return migrate_generic(sheets, 'Certificate', 'certificates', column_map)


def migrate_languages(sheets):
    """Migrate languages table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'language': 'language',
        'proficiency': 'proficiency',
        'test_name': 'test_name',
        'score': 'score',
        'test_date': 'test_date',
    }
    return migrate_generic(sheets, 'Language', 'languages', column_map)


def migrate_family_members(sheets):
    """Migrate family_members table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'relation': 'relation',
        'name': 'name',
        'birth_date': 'birth_date',
        'occupation': 'occupation',
        'is_cohabitant': 'is_cohabitant',
        'is_dependent': 'is_dependent',
        'contact': 'contact',
    }
    return migrate_generic(sheets, 'FamilyMember', 'family_members', column_map)


def migrate_military_services(sheets):
    """Migrate military_services table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'service_type': 'service_type',
        'branch': 'branch',
        'rank': 'rank',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'discharge_type': 'discharge_type',
    }
    return migrate_generic(sheets, 'MilitaryService', 'military_services', column_map)


def migrate_promotions(sheets):
    """Migrate promotions table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'previous_position': 'previous_position',
        'new_position': 'new_position',
        'promotion_date': 'promotion_date',
        'promotion_type': 'promotion_type',
        'notes': 'notes',
    }
    return migrate_generic(sheets, 'Promotion', 'promotions', column_map)


def migrate_evaluations(sheets):
    """Migrate evaluations table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'evaluation_period': 'evaluation_period',
        'evaluation_date': 'evaluation_date',
        'evaluator': 'evaluator',
        'performance_score': 'performance_score',
        'attitude_score': 'attitude_score',
        'skill_score': 'skill_score',
        'overall_grade': 'overall_grade',
        'comments': 'comments',
    }
    return migrate_generic(sheets, 'Evaluation', 'evaluations', column_map)


def migrate_trainings(sheets):
    """Migrate trainings table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'training_name': 'training_name',
        'training_type': 'training_type',
        'provider': 'provider',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'hours': 'hours',
        'status': 'status',
        'certificate_issued': 'certificate_issued',
    }
    return migrate_generic(sheets, 'Training', 'trainings', column_map)


def migrate_attendances(sheets):
    """Migrate attendances table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'date': 'date',
        'check_in': 'check_in',
        'check_out': 'check_out',
        'status': 'status',
        'overtime_hours': 'overtime_hours',
        'notes': 'notes',
    }
    return migrate_generic(sheets, 'Attendance', 'attendances', column_map)


def migrate_hr_projects(sheets):
    """Migrate hr_projects table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'project_name': 'project_name',
        'role': 'role',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'description': 'description',
        'contribution': 'contribution',
    }
    return migrate_generic(sheets, 'HrProject', 'hr_projects', column_map)


def migrate_awards(sheets):
    """Migrate awards table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'award_name': 'award_name',
        'award_type': 'award_type',
        'award_date': 'award_date',
        'issuer': 'issuer',
        'description': 'description',
    }
    return migrate_generic(sheets, 'Award', 'awards', column_map)


def migrate_assets(sheets):
    """Migrate assets table"""
    column_map = {
        'id': 'id',
        'employee_id': 'employee_id',
        'asset_type': 'asset_type',
        'asset_name': 'asset_name',
        'serial_number': 'serial_number',
        'assigned_date': 'assigned_date',
        'return_date': 'return_date',
        'status': 'status',
    }
    return migrate_generic(sheets, 'Asset', 'assets', column_map)


def migrate_personal_educations(sheets):
    """Migrate personal_educations table"""
    column_map = {
        'id': 'id',
        'profile_id': 'profile_id',
        'school_name': 'school_name',
        'degree': 'degree',
        'major': 'major',
        'entrance_date': 'entrance_date',
        'graduation_date': 'graduation_date',
        'status': 'graduation_status',
    }
    return migrate_generic(sheets, 'PersonalEducation', 'personal_educations', column_map, 'profile_id')


def migrate_personal_careers(sheets):
    """Migrate personal_careers table"""
    column_map = {
        'id': 'id',
        'profile_id': 'profile_id',
        'company_name': 'company_name',
        'department': 'department',
        'position': 'position',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'job_title': 'job_title',
        'responsibilities': 'responsibilities',
        'reason_for_leaving': 'reason_for_leaving',
    }
    return migrate_generic(sheets, 'PersonalCareer', 'personal_careers', column_map, 'profile_id')


def migrate_personal_certificates(sheets):
    """Migrate personal_certificates table"""
    column_map = {
        'id': 'id',
        'profile_id': 'profile_id',
        'name': 'certificate_name',
        'issuing_organization': 'issuing_organization',
        'issue_date': 'issue_date',
        'expiry_date': 'expiry_date',
        'certificate_number': 'certificate_number',
    }
    return migrate_generic(sheets, 'PersonalCertificate', 'personal_certificates', column_map, 'profile_id')


def migrate_personal_languages(sheets):
    """Migrate personal_languages table"""
    column_map = {
        'id': 'id',
        'profile_id': 'profile_id',
        'language': 'language',
        'proficiency': 'proficiency',
        'test_name': 'test_name',
        'score': 'score',
        'test_date': 'test_date',
    }
    return migrate_generic(sheets, 'PersonalLanguage', 'personal_languages', column_map, 'profile_id')


def migrate_personal_families(sheets):
    """Migrate personal_families table"""
    column_map = {
        'id': 'id',
        'profile_id': 'profile_id',
        'relation': 'relation',
        'name': 'name',
        'birth_date': 'birth_date',
        'occupation': 'occupation',
        'is_cohabitant': 'is_cohabitant',
        'is_dependent': 'is_dependent',
        'contact': 'contact',
    }
    return migrate_generic(sheets, 'PersonalFamily', 'personal_families', column_map, 'profile_id')


def main():
    print("=" * 60)
    print("HR Management System - Phase 3 Migration")
    print("=" * 60)

    app = create_app()
    with app.app_context():
        sheets = load_excel()

        print("\n=== Employee Related Data ===")
        migrations = [
            ('salaries', migrate_salaries),
            ('benefits', migrate_benefits),
            ('insurances', migrate_insurances),
            ('contracts', migrate_contracts),
            ('educations', migrate_educations),
            ('careers', migrate_careers),
            ('certificates', migrate_certificates),
            ('languages', migrate_languages),
            ('family_members', migrate_family_members),
            ('military_services', migrate_military_services),
            ('promotions', migrate_promotions),
            ('evaluations', migrate_evaluations),
            ('trainings', migrate_trainings),
            ('attendances', migrate_attendances),
            ('hr_projects', migrate_hr_projects),
            ('awards', migrate_awards),
            ('assets', migrate_assets),
        ]

        for table, func in migrations:
            count = func(sheets)
            print(f"  {table}: {count} records")

        print("\n=== Personal Related Data ===")
        personal_migrations = [
            ('personal_educations', migrate_personal_educations),
            ('personal_careers', migrate_personal_careers),
            ('personal_certificates', migrate_personal_certificates),
            ('personal_languages', migrate_personal_languages),
            ('personal_families', migrate_personal_families),
        ]

        for table, func in personal_migrations:
            count = func(sheets)
            print(f"  {table}: {count} records")

        print("\n" + "=" * 60)
        print("PHASE 3 COMPLETE")
        print("=" * 60)


if __name__ == '__main__':
    main()
