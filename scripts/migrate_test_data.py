"""
HR Management System - Test Data Migration Script
Migrates data from hr_test_data_complete_v2.xlsx to PostgreSQL
"""

import os
import sys
import pandas as pd
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add project root to path
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
        print(f"Loaded {sheet_name}: {len(df)} records")
    return sheets


def migrate_companies(sheets):
    """Migrate companies table"""
    print("\n=== Migrating Companies ===")
    df = sheets.get('Corporate', sheets.get('Companies'))
    if df is None:
        print("No Companies/Corporate sheet found!")
        return

    # Map logo files
    logo_map = {
        1: 'logo_a.png',
        2: 'logo_b.png',
        3: 'logo_c.png',
        4: 'logo_d.png',
        5: 'logo_e.png',
    }

    for _, row in df.iterrows():
        company_id = int(row.get('id', row.get('company_id', 0)))

        # Column mapping - match actual DB schema
        data = {
            'id': company_id,
            'name': row.get('company_name', row.get('name', '')),
            'business_number': row.get('business_number', ''),
            'representative': row.get('ceo', row.get('representative', '')),
            'address': row.get('address', ''),
            'phone': row.get('phone', ''),
            'fax': row.get('fax', ''),
            'email': row.get('email', ''),
            'website': row.get('website', ''),
            'establishment_date': str(row.get('founded_date', row.get('establishment_date', '')))[:10] if pd.notna(row.get('founded_date', row.get('establishment_date'))) else None,
            'business_type': row.get('business_type', row.get('industry', '')),
            'logo': logo_map.get(company_id, ''),
            'is_active': True,
            'is_verified': True,
            'plan_type': 'enterprise',
            'max_employees': 100,
            'created_at': datetime.now(),
        }

        # Clean None/NaN values
        clean_data = {}
        for k, v in data.items():
            if v is not None and not (isinstance(v, float) and pd.isna(v)):
                if v != '' or k in ['id', 'is_active', 'is_verified']:
                    clean_data[k] = v

        columns = list(clean_data.keys())
        placeholders = ', '.join([f':{k}' for k in columns])
        col_names = ', '.join(columns)

        sql = text(f"INSERT INTO companies ({col_names}) VALUES ({placeholders})")
        db.session.execute(sql, clean_data)

    db.session.commit()
    count = db.session.execute(text("SELECT COUNT(*) FROM companies")).scalar()
    print(f"Migrated companies: {count} records")


def migrate_organizations(sheets):
    """Migrate organizations table with company_id"""
    print("\n=== Migrating Organizations ===")
    df = sheets.get('Organization')
    if df is None:
        print("No Organization sheet found!")
        return

    for _, row in df.iterrows():
        org_id = int(row.get('id', 0))

        data = {
            'id': org_id,
            'name': row.get('name', ''),
            'code': row.get('code', ''),
            'org_type': row.get('org_type', ''),
            'parent_id': int(row.get('parent_id')) if pd.notna(row.get('parent_id')) else None,
            'company_id': int(row.get('company_id')) if pd.notna(row.get('company_id')) else None,
            'sort_order': int(row.get('sort_order', 0)) if pd.notna(row.get('sort_order')) else 0,
            'is_active': True,
            'created_at': datetime.now(),
        }

        # Insert without parent_id first
        columns = [k for k, v in data.items() if v is not None and v != '' and k != 'parent_id']
        values = {k: data[k] for k in columns}

        placeholders = ', '.join([f':{k}' for k in columns])
        col_names = ', '.join(columns)

        sql = text(f"INSERT INTO organizations ({col_names}) VALUES ({placeholders})")
        db.session.execute(sql, values)

    db.session.commit()

    # Now update parent_id
    print("Updating parent_id relationships...")
    for _, row in df.iterrows():
        org_id = int(row.get('id', 0))
        parent_id = int(row.get('parent_id')) if pd.notna(row.get('parent_id')) else None

        if parent_id:
            sql = text("UPDATE organizations SET parent_id = :parent_id WHERE id = :id")
            db.session.execute(sql, {'parent_id': parent_id, 'id': org_id})

    db.session.commit()
    count = db.session.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
    print(f"Migrated organizations: {count} records")


def migrate_users(sheets):
    """Migrate all user types"""
    print("\n=== Migrating Users ===")

    password_hash = generate_password_hash('test1234')
    user_id = 1

    # 1. Corporate accounts (5)
    df = sheets.get('CorporateAccount')
    if df is not None:
        for _, row in df.iterrows():
            data = {
                'id': user_id,
                'username': row.get('user_id', ''),
                'email': row.get('email', ''),
                'password_hash': password_hash,
                'role': row.get('role', 'admin'),
                'account_type': 'corporate',
                'company_id': int(row.get('company_id')) if pd.notna(row.get('company_id')) else None,
                'is_active': True,
                'created_at': datetime.now(),
            }

            columns = [k for k, v in data.items() if v is not None and v != '']
            values = {k: data[k] for k in columns}

            placeholders = ', '.join([f':{k}' for k in columns])
            col_names = ', '.join(columns)

            sql = text(f"INSERT INTO users ({col_names}) VALUES ({placeholders})")
            db.session.execute(sql, values)
            user_id += 1

        print(f"  Corporate accounts: {len(df)} records")

    # 2. Employee accounts (50) - these will be linked to employees later
    df = sheets.get('EmployeeAccount')
    employee_user_map = {}  # employee_id -> user_id

    if df is not None:
        for _, row in df.iterrows():
            emp_id = int(row.get('employee_id')) if pd.notna(row.get('employee_id')) else None

            data = {
                'id': user_id,
                'username': row.get('user_id', ''),
                'email': row.get('email', ''),
                'password_hash': password_hash,
                'role': row.get('role', 'employee'),
                'account_type': 'employee_sub',
                'company_id': int(row.get('company_id')) if pd.notna(row.get('company_id')) else None,
                'is_active': True,
                'created_at': datetime.now(),
            }

            columns = [k for k, v in data.items() if v is not None and v != '']
            values = {k: data[k] for k in columns}

            placeholders = ', '.join([f':{k}' for k in columns])
            col_names = ', '.join(columns)

            sql = text(f"INSERT INTO users ({col_names}) VALUES ({placeholders})")
            db.session.execute(sql, values)

            if emp_id:
                employee_user_map[emp_id] = user_id

            user_id += 1

        print(f"  Employee accounts: {len(df)} records")

    # 3. Personal accounts (10)
    df = sheets.get('PersonalAccount')
    personal_user_map = {}  # personal_id -> user_id

    if df is not None:
        for _, row in df.iterrows():
            personal_id = int(row.get('id')) if pd.notna(row.get('id')) else None

            data = {
                'id': user_id,
                'username': row.get('user_id', ''),
                'email': row.get('email', ''),
                'password_hash': password_hash,
                'role': 'user',
                'account_type': 'personal',
                'is_active': True,
                'created_at': datetime.now(),
            }

            columns = [k for k, v in data.items() if v is not None and v != '']
            values = {k: data[k] for k in columns}

            placeholders = ', '.join([f':{k}' for k in columns])
            col_names = ', '.join(columns)

            sql = text(f"INSERT INTO users ({col_names}) VALUES ({placeholders})")
            db.session.execute(sql, values)

            if personal_id:
                personal_user_map[personal_id] = user_id

            user_id += 1

        print(f"  Personal accounts: {len(df)} records")

    db.session.commit()
    count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
    print(f"Total users migrated: {count} records")

    return employee_user_map, personal_user_map


def migrate_employees(sheets, employee_user_map):
    """Migrate employees table"""
    print("\n=== Migrating Employees ===")
    df = sheets.get('Employee')
    if df is None:
        print("No Employee sheet found!")
        return

    for _, row in df.iterrows():
        emp_id = int(row.get('id', 0))

        # Photo mapping: employee ID -> pic file
        photo_name = f"pic_{emp_id:02d}.png" if emp_id <= 50 else None

        data = {
            'id': emp_id,
            'employee_number': row.get('employee_number', ''),
            'name': row.get('name', ''),
            'english_name': row.get('english_name', ''),
            'chinese_name': row.get('chinese_name', ''),
            'photo': photo_name,
            'department': row.get('department', ''),
            'position': row.get('position', ''),
            'job_title': row.get('job_title', ''),
            'job_grade': row.get('job_grade', ''),
            'job_role': row.get('job_role', ''),
            'team': row.get('team', ''),
            'status': row.get('status', 'active'),
            'hire_date': str(row.get('hire_date', ''))[:10] if pd.notna(row.get('hire_date')) else None,
            'phone': row.get('phone', ''),
            'email': row.get('email', ''),
            'organization_id': int(row.get('organization_id')) if pd.notna(row.get('organization_id')) else None,
            'work_location': row.get('work_location', ''),
            'internal_phone': row.get('internal_phone', ''),
            'company_email': row.get('company_email', ''),
            'birth_date': str(row.get('birth_date', ''))[:10] if pd.notna(row.get('birth_date')) else None,
            'lunar_birth': bool(row.get('lunar_birth', False)) if pd.notna(row.get('lunar_birth')) else False,
            'gender': row.get('gender', ''),
            'mobile_phone': row.get('mobile_phone', ''),
            'home_phone': row.get('home_phone', ''),
            'address': row.get('address', ''),
            'detailed_address': row.get('detailed_address', ''),
            'postal_code': str(row.get('postal_code', '')) if pd.notna(row.get('postal_code')) else '',
            'resident_number': row.get('resident_number', ''),
            'nationality': row.get('nationality', ''),
            'blood_type': row.get('blood_type', ''),
            'religion': row.get('religion', ''),
            'hobby': row.get('hobby', ''),
            'specialty': row.get('specialty', ''),
            'marital_status': row.get('marital_status', ''),
            'actual_postal_code': str(row.get('actual_postal_code', '')) if pd.notna(row.get('actual_postal_code')) else '',
            'actual_address': row.get('actual_address', ''),
            'actual_detailed_address': row.get('actual_detailed_address', ''),
            'emergency_contact': row.get('emergency_contact', ''),
            'emergency_relation': row.get('emergency_relation', ''),
        }

        # Clean data - convert NaN to None/empty
        for key, val in data.items():
            if pd.isna(val):
                data[key] = None if key in ['organization_id', 'lunar_birth'] else ''

        columns = [k for k, v in data.items() if v is not None]
        values = {k: data[k] for k in columns}

        placeholders = ', '.join([f':{k}' for k in columns])
        col_names = ', '.join(columns)

        sql = text(f"INSERT INTO employees ({col_names}) VALUES ({placeholders})")
        db.session.execute(sql, values)

    db.session.commit()

    # Link employees to users
    print("Linking employees to users...")
    for emp_id, user_id in employee_user_map.items():
        sql = text("UPDATE users SET employee_id = :emp_id WHERE id = :user_id")
        db.session.execute(sql, {'emp_id': emp_id, 'user_id': user_id})

    db.session.commit()
    count = db.session.execute(text("SELECT COUNT(*) FROM employees")).scalar()
    print(f"Migrated employees: {count} records")


def migrate_personal_profiles(sheets, personal_user_map):
    """Migrate personal_profiles table"""
    print("\n=== Migrating Personal Profiles ===")
    df = sheets.get('PersonalProfile', sheets.get('Personal'))
    if df is None:
        print("No PersonalProfile/Personal sheet found!")
        return

    for _, row in df.iterrows():
        profile_id = int(row.get('id', 0))
        user_id = personal_user_map.get(profile_id)

        # Photo mapping: personal ID -> pic file (use same as employee photos)
        photo_name = f"pic_{profile_id:02d}.png" if profile_id <= 10 else None

        data = {
            'id': profile_id,
            'user_id': user_id,
            'name': row.get('name', ''),
            'english_name': row.get('english_name', ''),
            'chinese_name': row.get('chinese_name', ''),
            'photo': photo_name,
            'birth_date': str(row.get('birth_date', ''))[:10] if pd.notna(row.get('birth_date')) else None,
            'lunar_birth': bool(row.get('lunar_birth', False)) if pd.notna(row.get('lunar_birth')) else False,
            'gender': row.get('gender', ''),
            'email': row.get('email', ''),
            'mobile_phone': row.get('mobile_phone', row.get('phone', '')),
            'home_phone': row.get('home_phone', ''),
            'address': row.get('address', ''),
            'detailed_address': row.get('detailed_address', ''),
            'postal_code': str(row.get('postal_code', '')) if pd.notna(row.get('postal_code')) else '',
            'resident_number': row.get('resident_number', ''),
            'nationality': row.get('nationality', '대한민국'),
            'blood_type': row.get('blood_type', ''),
            'religion': row.get('religion', ''),
            'hobby': row.get('hobby', ''),
            'specialty': row.get('specialty', ''),
            'marital_status': row.get('marital_status', ''),
            'actual_postal_code': str(row.get('actual_postal_code', '')) if pd.notna(row.get('actual_postal_code')) else '',
            'actual_address': row.get('actual_address', ''),
            'actual_detailed_address': row.get('actual_detailed_address', ''),
            'emergency_contact': row.get('emergency_contact', ''),
            'emergency_relation': row.get('emergency_relation', ''),
            'created_at': datetime.now(),
        }

        # Clean data
        for key, val in data.items():
            if pd.isna(val):
                data[key] = None if key in ['user_id', 'lunar_birth'] else ''

        columns = [k for k, v in data.items() if v is not None]
        values = {k: data[k] for k in columns}

        placeholders = ', '.join([f':{k}' for k in columns])
        col_names = ', '.join(columns)

        sql = text(f"INSERT INTO personal_profiles ({col_names}) VALUES ({placeholders})")
        db.session.execute(sql, values)

    db.session.commit()
    count = db.session.execute(text("SELECT COUNT(*) FROM personal_profiles")).scalar()
    print(f"Migrated personal_profiles: {count} records")


def main():
    print("=" * 60)
    print("HR Management System - Test Data Migration")
    print("=" * 60)

    app = create_app()
    with app.app_context():
        # Load Excel data
        print("\nLoading Excel data...")
        sheets = load_excel()

        # Phase 2: Core data migration
        migrate_companies(sheets)
        migrate_organizations(sheets)
        employee_user_map, personal_user_map = migrate_users(sheets)
        migrate_employees(sheets, employee_user_map)
        migrate_personal_profiles(sheets, personal_user_map)

        # Final verification
        print("\n" + "=" * 60)
        print("PHASE 2 COMPLETE - Core Data Migration Summary")
        print("=" * 60)

        tables = ['companies', 'organizations', 'users', 'employees', 'personal_profiles']
        for table in tables:
            count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count} records")


if __name__ == '__main__':
    main()
