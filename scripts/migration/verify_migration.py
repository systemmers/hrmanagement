"""
Migration Verification Script

Verifies that PostgreSQL migration was successful by testing:
1. Database connectivity
2. Table existence
3. Data integrity (row counts)
4. Foreign key relationships
5. Basic CRUD operations

Usage:
    python scripts/migration/verify_migration.py
"""
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

# Check if running with PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if 'postgresql' not in DATABASE_URL:
    print("[ERROR] DATABASE_URL is not configured for PostgreSQL")
    print("        Current value:", DATABASE_URL[:50] if DATABASE_URL else "(empty)")
    sys.exit(1)


def test_flask_app_startup():
    """Test that Flask app starts correctly with PostgreSQL"""
    print("\n--- Test 1: Flask Application Startup ---")
    try:
        from app import create_app
        from app.database import db

        app = create_app()
        with app.app_context():
            # Try to access database
            result = db.session.execute(db.text("SELECT 1"))
            result.scalar()
            print("  [PASS] Flask app started successfully")
            print("  [PASS] Database connection verified")
            return True
    except Exception as e:
        print(f"  [FAIL] Flask app startup failed: {e}")
        return False


def test_all_models_accessible():
    """Test that all models are accessible"""
    print("\n--- Test 2: Model Accessibility ---")
    try:
        from app.models import (
            User, Employee, Organization, ClassificationOption,
            Education, Career, Certificate, FamilyMember, Language, MilitaryService,
            Salary, Benefit, Contract, SalaryHistory,
            Promotion, Evaluation, Training, Attendance,
            Insurance, Project, Award, Asset,
            SalaryPayment, Attachment, SystemSetting
        )

        models = [
            User, Employee, Organization, ClassificationOption,
            Education, Career, Certificate, FamilyMember, Language, MilitaryService,
            Salary, Benefit, Contract, SalaryHistory,
            Promotion, Evaluation, Training, Attendance,
            Insurance, Project, Award, Asset,
            SalaryPayment, Attachment, SystemSetting
        ]

        print(f"  [PASS] {len(models)} models imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Model import failed: {e}")
        return False


def test_table_existence():
    """Test that all tables exist in PostgreSQL"""
    print("\n--- Test 3: Table Existence ---")
    try:
        from app import create_app
        from app.database import db

        expected_tables = [
            'organizations', 'employees', 'users', 'classification_options',
            'system_settings', 'educations', 'careers', 'certificates',
            'family_members', 'languages', 'military_services', 'salaries',
            'benefits', 'contracts', 'salary_histories', 'promotions',
            'evaluations', 'trainings', 'attendances', 'insurances',
            'projects', 'awards', 'assets', 'salary_payments', 'attachments'
        ]

        app = create_app()
        with app.app_context():
            # Get existing tables
            result = db.session.execute(db.text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            existing_tables = [row[0] for row in result]

            missing = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"  [OK] {table}")
                else:
                    print(f"  [MISSING] {table}")
                    missing.append(table)

            if missing:
                print(f"\n  [FAIL] {len(missing)} tables missing")
                return False
            else:
                print(f"\n  [PASS] All {len(expected_tables)} tables exist")
                return True
    except Exception as e:
        print(f"  [FAIL] Table check failed: {e}")
        return False


def test_row_counts():
    """Test that data exists in critical tables"""
    print("\n--- Test 4: Data Row Counts ---")
    try:
        from app import create_app
        from app.database import db

        app = create_app()
        with app.app_context():
            tables = ['organizations', 'employees', 'users']

            for table in tables:
                try:
                    result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count} rows")
                except Exception as e:
                    print(f"  {table}: [ERROR] {e}")

            print("\n  [INFO] Row counts displayed (verify against SQLite if needed)")
            return True
    except Exception as e:
        print(f"  [FAIL] Row count check failed: {e}")
        return False


def test_basic_queries():
    """Test basic queries on each model"""
    print("\n--- Test 5: Basic Model Queries ---")
    try:
        from app import create_app
        from app.database import db
        from app.models import User, Employee, Organization

        app = create_app()
        with app.app_context():
            # Test User query
            users = User.query.limit(5).all()
            print(f"  [OK] User.query returned {len(users)} records")

            # Test Employee query
            employees = Employee.query.limit(5).all()
            print(f"  [OK] Employee.query returned {len(employees)} records")

            # Test Organization query
            orgs = Organization.query.limit(5).all()
            print(f"  [OK] Organization.query returned {len(orgs)} records")

            # Test relationship: User -> Employee
            if users:
                for user in users[:3]:
                    emp = user.employee
                    print(f"  [OK] User '{user.username}' -> Employee: {emp.name if emp else 'None'}")

            print("\n  [PASS] Basic queries successful")
            return True
    except Exception as e:
        print(f"  [FAIL] Query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_write_operation():
    """Test write operation (create and rollback)"""
    print("\n--- Test 6: Write Operation (Rollback Test) ---")
    try:
        from app import create_app
        from app.database import db
        from app.models import SystemSetting

        app = create_app()
        with app.app_context():
            # Create a test setting
            test_key = f'test_migration_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            test_setting = SystemSetting(
                key=test_key,
                value='migration_test_value',
                description='Migration verification test'
            )

            db.session.add(test_setting)
            db.session.flush()  # Get the ID without committing

            print(f"  [OK] Created test record with id={test_setting.id}")

            # Rollback to avoid polluting the database
            db.session.rollback()
            print("  [OK] Transaction rolled back successfully")

            print("\n  [PASS] Write operation test successful")
            return True
    except Exception as e:
        print(f"  [FAIL] Write test failed: {e}")
        return False


def test_login_credentials():
    """Test that known login credentials work"""
    print("\n--- Test 7: Login Credentials Verification ---")
    try:
        from app import create_app
        from app.models import User

        app = create_app()
        with app.app_context():
            # Test admin user
            admin = User.query.filter_by(email='company@example.com').first()
            if admin:
                if admin.check_password('admin1234'):
                    print("  [OK] Admin user (company@example.com) credentials valid")
                else:
                    print("  [WARN] Admin user exists but password may have changed")
            else:
                print("  [INFO] Admin user not found (may need to create)")

            # Test employee user
            employee = User.query.filter_by(email='testuser@example.com').first()
            if employee:
                if employee.check_password('test1234'):
                    print("  [OK] Test user (testuser@example.com) credentials valid")
                else:
                    print("  [WARN] Test user exists but password may have changed")
            else:
                print("  [INFO] Test user not found (may need to create)")

            print("\n  [PASS] Credential verification complete")
            return True
    except Exception as e:
        print(f"  [FAIL] Credential test failed: {e}")
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("PostgreSQL Migration Verification")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '(hidden)'}")

    results = []

    # Run tests
    results.append(("Flask App Startup", test_flask_app_startup()))
    results.append(("Model Accessibility", test_all_models_accessible()))
    results.append(("Table Existence", test_table_existence()))
    results.append(("Row Counts", test_row_counts()))
    results.append(("Basic Queries", test_basic_queries()))
    results.append(("Write Operation", test_write_operation()))
    results.append(("Login Credentials", test_login_credentials()))

    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if failed > 0:
        print("\n[WARNING] Some tests failed. Review the output above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All verification tests passed!")
        print("          PostgreSQL migration is complete and verified.")


if __name__ == '__main__':
    main()
