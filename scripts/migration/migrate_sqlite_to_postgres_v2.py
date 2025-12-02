"""
SQLite -> PostgreSQL Data Migration Script (v2)

Enhanced version with:
- Automatic boolean type conversion (SQLite integer 0/1 -> PostgreSQL boolean)
- Dynamic column detection from PostgreSQL schema
- Better error handling and recovery

Usage:
    python scripts/migration/migrate_sqlite_to_postgres_v2.py
"""
import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from psycopg2 import sql

SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'instance', 'hrmanagement.db'
)

DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Tables in dependency order
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
    """Parse PostgreSQL URL"""
    url = url.replace('postgresql://', '')
    user_pass, host_db = url.split('@')
    user, password = user_pass.split(':')
    host_port, database = host_db.split('/')
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = '5432'
    return {'host': host, 'port': int(port), 'database': database, 'user': user, 'password': password}


def get_sqlite_tables(conn):
    """Get SQLite tables"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'alembic_%'")
    return [row[0] for row in cursor.fetchall()]


def get_sqlite_columns(conn, table):
    """Get SQLite column names for a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def get_pg_columns(conn, table):
    """Get PostgreSQL column names and types"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (table,))
    return {row[0]: row[1] for row in cursor.fetchall()}


def convert_value(value, pg_type):
    """Convert SQLite value to PostgreSQL compatible type"""
    if value is None:
        return None

    # Boolean conversion
    if pg_type == 'boolean':
        if isinstance(value, int):
            return value == 1
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)

    # Bytes to string
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')

    return value


def migrate_table(sqlite_conn, pg_conn, table_name):
    """Migrate a single table with type conversion"""
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    # Check table exists in SQLite
    sqlite_tables = get_sqlite_tables(sqlite_conn)
    if table_name not in sqlite_tables:
        print(f"  [SKIP] Table '{table_name}' not in SQLite")
        return 0

    # Get column info
    sqlite_columns = get_sqlite_columns(sqlite_conn, table_name)
    pg_columns = get_pg_columns(pg_conn, table_name)

    if not pg_columns:
        print(f"  [SKIP] Table '{table_name}' not in PostgreSQL")
        return 0

    # Find common columns
    common_columns = [col for col in sqlite_columns if col in pg_columns]

    if not common_columns:
        print(f"  [SKIP] No common columns for '{table_name}'")
        return 0

    # Get SQLite data
    sqlite_cur.execute(f"SELECT {', '.join(common_columns)} FROM {table_name}")
    rows = sqlite_cur.fetchall()

    if not rows:
        print(f"  [SKIP] Table '{table_name}' is empty")
        return 0

    # Disable triggers for faster insert
    pg_cur.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL")

    # Clear existing data
    pg_cur.execute(f"DELETE FROM {table_name}")

    # Prepare INSERT statement
    placeholders = ', '.join(['%s'] * len(common_columns))
    column_names = ', '.join(common_columns)
    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    # Insert with type conversion
    success_count = 0
    for row in rows:
        converted_row = []
        for i, col in enumerate(common_columns):
            pg_type = pg_columns.get(col, 'text')
            converted_row.append(convert_value(row[i], pg_type))

        try:
            pg_cur.execute(insert_sql, converted_row)
            success_count += 1
        except Exception as e:
            print(f"  [WARN] Row insert failed in '{table_name}': {str(e)[:100]}")

    # Re-enable triggers
    pg_cur.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL")

    pg_conn.commit()
    return success_count


def sync_sequences(pg_conn):
    """Sync PostgreSQL sequences"""
    pg_cur = pg_conn.cursor()

    pg_cur.execute("""
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'id' AND table_schema = 'public'
    """)
    tables = [row[0] for row in pg_cur.fetchall()]

    for table in tables:
        try:
            pg_cur.execute(f"SELECT pg_get_serial_sequence('{table}', 'id')")
            sequence = pg_cur.fetchone()[0]
            if sequence:
                pg_cur.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
                max_id = pg_cur.fetchone()[0]
                pg_cur.execute(f"SELECT setval('{sequence}', {max_id + 1}, false)")
                print(f"  [SEQ] {table}: {max_id + 1}")
        except Exception as e:
            pass

    pg_conn.commit()


def verify_migration(sqlite_conn, pg_conn):
    """Verify migration"""
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    print("\n=== Migration Verification ===")

    all_match = True
    for table in TABLE_ORDER:
        sqlite_tables = get_sqlite_tables(sqlite_conn)
        if table not in sqlite_tables:
            continue

        sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_count = sqlite_cur.fetchone()[0]

        try:
            pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cur.fetchone()[0]
        except:
            pg_count = 'N/A'

        match = sqlite_count == pg_count
        status = "[OK]" if match else "[MISMATCH]"
        print(f"  {status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")

        if not match and pg_count != 'N/A':
            all_match = False

    return all_match


def main():
    print("=" * 60)
    print("SQLite -> PostgreSQL Migration (v2)")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not os.path.exists(SQLITE_PATH):
        print(f"\n[ERROR] SQLite database not found: {SQLITE_PATH}")
        sys.exit(1)

    if not DATABASE_URL:
        print("\n[ERROR] DATABASE_URL not set")
        sys.exit(1)

    print(f"\nSource: {SQLITE_PATH}")
    print(f"Target: {DATABASE_URL.split('@')[1]}")

    print("\n--- Connecting ---")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    print("  [OK] SQLite")

    pg_params = parse_postgres_url(DATABASE_URL)
    pg_conn = psycopg2.connect(**pg_params)
    print("  [OK] PostgreSQL")

    print("\n--- Migrating tables ---")
    total = 0
    for table in TABLE_ORDER:
        try:
            count = migrate_table(sqlite_conn, pg_conn, table)
            if count > 0:
                print(f"  [OK] {table}: {count} rows")
                total += count
        except Exception as e:
            print(f"  [ERROR] {table}: {str(e)[:80]}")
            pg_conn.rollback()

    print("\n--- Synchronizing sequences ---")
    sync_sequences(pg_conn)

    success = verify_migration(sqlite_conn, pg_conn)

    sqlite_conn.close()
    pg_conn.close()

    print("\n" + "=" * 60)
    print(f"Total rows: {total}")
    print(f"Status: {'SUCCESS' if success else 'PARTIAL - Some tables may need manual review'}")
    print("=" * 60)


if __name__ == '__main__':
    main()
