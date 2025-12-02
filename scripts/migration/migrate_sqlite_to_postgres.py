"""
SQLite -> PostgreSQL Data Migration Script

This script migrates all data from SQLite database to PostgreSQL.

Usage:
    1. Ensure Docker PostgreSQL is running: docker-compose up -d
    2. Install dependencies: pip install -r requirements.txt
    3. Run migration: python scripts/migration/migrate_sqlite_to_postgres.py

Prerequisites:
    - SQLite database exists at instance/hrmanagement.db
    - PostgreSQL container is running and accessible
    - Alembic migrations have been applied (alembic upgrade head)
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from psycopg2.extras import execute_values

# Configuration
SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'instance', 'hrmanagement.db'
)

# Parse PostgreSQL URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Table migration order (respecting foreign key dependencies)
TABLE_ORDER = [
    'organizations',
    'employees',
    'users',
    'classification_options',
    'system_settings',
    'educations',
    'careers',
    'certificates',
    'family_members',
    'languages',
    'military_services',
    'salaries',
    'benefits',
    'contracts',
    'salary_histories',
    'promotions',
    'evaluations',
    'trainings',
    'attendances',
    'insurances',
    'projects',
    'awards',
    'assets',
    'salary_payments',
    'attachments',
]


def parse_postgres_url(url):
    """Parse PostgreSQL URL into connection parameters"""
    # Format: postgresql://user:password@host:port/database
    url = url.replace('postgresql://', '')
    user_pass, host_db = url.split('@')
    user, password = user_pass.split(':')
    host_port, database = host_db.split('/')

    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = '5432'

    return {
        'host': host,
        'port': int(port),
        'database': database,
        'user': user,
        'password': password
    }


def get_sqlite_tables(sqlite_conn):
    """Get list of tables in SQLite database"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]


def get_table_columns(sqlite_conn, table_name):
    """Get column names for a table"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def migrate_table(sqlite_conn, pg_conn, table_name, dry_run=False):
    """Migrate a single table from SQLite to PostgreSQL"""
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    # Check if table exists in SQLite
    sqlite_tables = get_sqlite_tables(sqlite_conn)
    if table_name not in sqlite_tables:
        print(f"  [SKIP] Table '{table_name}' not found in SQLite")
        return 0

    # Get data from SQLite
    sqlite_cur.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cur.fetchall()

    if not rows:
        print(f"  [SKIP] Table '{table_name}' is empty")
        return 0

    # Get column names
    columns = get_table_columns(sqlite_conn, table_name)

    if dry_run:
        print(f"  [DRY-RUN] Would migrate {len(rows)} rows from '{table_name}'")
        return len(rows)

    # Disable triggers temporarily for faster insert
    pg_cur.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL")

    # Clear existing data
    pg_cur.execute(f"DELETE FROM {table_name}")

    # Build INSERT statement
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)
    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    # Insert data
    for row in rows:
        # Convert None values and handle type conversions
        converted_row = []
        for val in row:
            if val is None:
                converted_row.append(None)
            elif isinstance(val, bytes):
                converted_row.append(val.decode('utf-8', errors='replace'))
            else:
                converted_row.append(val)

        try:
            pg_cur.execute(insert_sql, converted_row)
        except Exception as e:
            print(f"  [ERROR] Failed to insert row in '{table_name}': {e}")
            print(f"          Row: {converted_row[:3]}...")  # Print first 3 columns
            raise

    # Re-enable triggers
    pg_cur.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL")

    pg_conn.commit()
    return len(rows)


def sync_sequences(pg_conn):
    """Synchronize PostgreSQL sequences after data migration"""
    pg_cur = pg_conn.cursor()

    # Get all tables with id column
    pg_cur.execute("""
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'id'
        AND table_schema = 'public'
    """)
    tables = [row[0] for row in pg_cur.fetchall()]

    for table in tables:
        try:
            # Check if sequence exists
            pg_cur.execute(f"""
                SELECT pg_get_serial_sequence('{table}', 'id')
            """)
            sequence = pg_cur.fetchone()[0]

            if sequence:
                # Get max id
                pg_cur.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
                max_id = pg_cur.fetchone()[0]

                # Set sequence value
                pg_cur.execute(f"SELECT setval('{sequence}', {max_id + 1}, false)")
                print(f"  [SEQ] {table}: sequence set to {max_id + 1}")
        except Exception as e:
            print(f"  [WARN] Could not sync sequence for '{table}': {e}")

    pg_conn.commit()


def verify_migration(sqlite_conn, pg_conn):
    """Verify that migration was successful by comparing row counts"""
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    print("\n=== Migration Verification ===")

    all_match = True
    for table in TABLE_ORDER:
        # Check if table exists in SQLite
        sqlite_tables = get_sqlite_tables(sqlite_conn)
        if table not in sqlite_tables:
            continue

        # SQLite count
        sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_count = sqlite_cur.fetchone()[0]

        # PostgreSQL count
        try:
            pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cur.fetchone()[0]
        except Exception:
            pg_count = 'N/A'

        match = sqlite_count == pg_count
        status = "[OK]" if match else "[MISMATCH]"
        print(f"  {status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")

        if not match:
            all_match = False

    return all_match


def main():
    """Main migration function"""
    print("=" * 60)
    print("SQLite -> PostgreSQL Migration")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Validate configuration
    if not os.path.exists(SQLITE_PATH):
        print(f"\n[ERROR] SQLite database not found: {SQLITE_PATH}")
        sys.exit(1)

    if not DATABASE_URL:
        print("\n[ERROR] DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"\nSource: {SQLITE_PATH}")
    print(f"Target: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

    # Connect to databases
    print("\n--- Connecting to databases ---")

    try:
        sqlite_conn = sqlite3.connect(SQLITE_PATH)
        print("  [OK] Connected to SQLite")
    except Exception as e:
        print(f"  [ERROR] SQLite connection failed: {e}")
        sys.exit(1)

    try:
        pg_params = parse_postgres_url(DATABASE_URL)
        pg_conn = psycopg2.connect(**pg_params)
        print("  [OK] Connected to PostgreSQL")
    except Exception as e:
        print(f"  [ERROR] PostgreSQL connection failed: {e}")
        print("         Make sure Docker container is running: docker-compose up -d")
        sys.exit(1)

    # Migrate tables
    print("\n--- Migrating tables ---")

    total_rows = 0
    for table in TABLE_ORDER:
        try:
            count = migrate_table(sqlite_conn, pg_conn, table)
            if count > 0:
                print(f"  [OK] {table}: {count} rows migrated")
                total_rows += count
        except Exception as e:
            print(f"  [ERROR] Failed to migrate '{table}': {e}")
            pg_conn.rollback()
            # Continue with other tables

    # Sync sequences
    print("\n--- Synchronizing sequences ---")
    sync_sequences(pg_conn)

    # Verify migration
    success = verify_migration(sqlite_conn, pg_conn)

    # Cleanup
    sqlite_conn.close()
    pg_conn.close()

    # Summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"  Total rows migrated: {total_rows}")
    print(f"  Verification: {'PASSED' if success else 'FAILED - Please check mismatches'}")
    print(f"  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
