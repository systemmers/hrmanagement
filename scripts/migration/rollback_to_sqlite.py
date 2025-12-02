"""
Rollback Script: PostgreSQL -> SQLite

This script provides rollback capability if PostgreSQL migration fails.
It restores the SQLite configuration without touching the data.

Usage:
    python scripts/migration/rollback_to_sqlite.py [--confirm]

WARNING: This will modify .env to use SQLite database.
         Make sure you have a backup of your SQLite database.
"""
import os
import sys
import shutil
from datetime import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(PROJECT_ROOT, '.env')
SQLITE_DB = os.path.join(PROJECT_ROOT, 'instance', 'hrmanagement.db')


def backup_env_file():
    """Create backup of current .env file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{ENV_FILE}.backup_{timestamp}"
    shutil.copy(ENV_FILE, backup_path)
    print(f"  [OK] Created .env backup: {backup_path}")
    return backup_path


def rollback_env_file():
    """Modify .env to use SQLite instead of PostgreSQL"""
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Comment out PostgreSQL line and uncomment SQLite line
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        if line.startswith('DATABASE_URL=postgresql://'):
            # Comment out PostgreSQL
            new_lines.append('# ' + line + '  # Disabled for rollback')
        elif line.strip() == '# DATABASE_URL=sqlite:///instance/hrmanagement.db':
            # Uncomment SQLite
            new_lines.append('DATABASE_URL=sqlite:///instance/hrmanagement.db')
        else:
            new_lines.append(line)

    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print("  [OK] .env modified to use SQLite")


def verify_sqlite_database():
    """Verify SQLite database exists and is accessible"""
    if not os.path.exists(SQLITE_DB):
        print(f"  [ERROR] SQLite database not found: {SQLITE_DB}")
        return False

    try:
        import sqlite3
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            print(f"  [OK] SQLite database verified: {SQLITE_DB}")
            return True
        else:
            print("  [WARN] SQLite database exists but appears empty")
            return True
    except Exception as e:
        print(f"  [ERROR] SQLite verification failed: {e}")
        return False


def main():
    print("=" * 60)
    print("PostgreSQL -> SQLite Rollback")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for --confirm flag
    if '--confirm' not in sys.argv:
        print("\n[WARNING] This script will modify your .env file to use SQLite.")
        print("          Run with --confirm to proceed.")
        print("\nUsage: python scripts/migration/rollback_to_sqlite.py --confirm")
        sys.exit(0)

    # Step 1: Verify SQLite database exists
    print("\n--- Step 1: Verify SQLite Database ---")
    if not verify_sqlite_database():
        print("\n[ABORT] Cannot rollback without SQLite database")
        sys.exit(1)

    # Step 2: Backup current .env
    print("\n--- Step 2: Backup .env ---")
    backup_path = backup_env_file()

    # Step 3: Modify .env
    print("\n--- Step 3: Modify .env ---")
    rollback_env_file()

    # Step 4: Verify Flask app starts with SQLite
    print("\n--- Step 4: Verify Flask App ---")
    try:
        # Reload environment
        from dotenv import load_dotenv
        load_dotenv(override=True)

        from app import create_app
        app = create_app()
        with app.app_context():
            from app.database import db
            db.session.execute(db.text("SELECT 1"))
            print("  [OK] Flask app starts correctly with SQLite")
    except Exception as e:
        print(f"  [ERROR] Flask app failed: {e}")
        print(f"\n[RECOVERY] Restore .env from backup: {backup_path}")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 60)
    print("Rollback Complete")
    print("=" * 60)
    print(f"  .env backup: {backup_path}")
    print("  Database: SQLite")
    print("  Status: SUCCESS")
    print("\nYou can now restart your Flask application.")


if __name__ == '__main__':
    main()
