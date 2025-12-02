# Phase 0: SQLite -> PostgreSQL Migration Guide

## Overview

This document describes the migration process from SQLite to PostgreSQL for the HR Management system.

**Migration Status**: Ready for Execution
**Created**: 2025-12-02
**Author**: Claude Code

---

## Prerequisites

### System Requirements
- Docker Desktop installed and running
- Python 3.10+ with venv
- At least 2GB free disk space
- Network access for Docker image download

### Verification Commands
```powershell
# Check Docker
docker --version

# Check Python
python --version

# Check pip
pip --version
```

---

## Migration Steps

### Step 1: Backup Current SQLite Database

```powershell
# Create backup directory
mkdir D:\projects\hrmanagement\backups

# Copy SQLite database
copy D:\projects\hrmanagement\instance\hrmanagement.db D:\projects\hrmanagement\backups\hrmanagement_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

### Step 2: Install Dependencies

```powershell
# Activate virtual environment
cd D:\projects\hrmanagement
.\venv\Scripts\activate

# Install new dependencies
pip install -r requirements.txt
```

### Step 3: Start PostgreSQL Container

```powershell
cd D:\projects\hrmanagement

# Start PostgreSQL (first time will download image)
docker-compose up -d

# Verify container is running
docker-compose ps

# Check logs for any errors
docker-compose logs db
```

**Expected Output:**
```
NAME                 IMAGE         STATUS          PORTS
hrmanagement_db      postgres:15   Up (healthy)    0.0.0.0:5432->5432/tcp
hrmanagement_pgadmin dpage/pgadmin4 Up             0.0.0.0:5050->80/tcp
```

### Step 4: Apply Database Schema

```powershell
# Apply Alembic migrations
alembic upgrade head

# Verify tables created
docker exec hrmanagement_db psql -U hrm_user -d hrmanagement_db -c "\dt"
```

### Step 5: Migrate Data from SQLite

```powershell
# Run migration script
python scripts/migration/migrate_sqlite_to_postgres.py
```

**Expected Output:**
```
=== SQLite -> PostgreSQL Migration ===
Source: instance/hrmanagement.db
Target: localhost:5432/hrmanagement_db

--- Migrating tables ---
  [OK] organizations: X rows migrated
  [OK] employees: X rows migrated
  [OK] users: X rows migrated
  ...

--- Migration Verification ---
  [OK] All row counts match

Migration Summary
  Total rows migrated: XXX
  Verification: PASSED
```

### Step 6: Verify Migration

```powershell
# Run verification script
python scripts/migration/verify_migration.py
```

### Step 7: Test Application

```powershell
# Start Flask application
python run.py

# Open browser and test:
# - Login with admin: company@example.com / admin1234
# - Login with employee: testuser@example.com / test1234
# - Navigate through all pages
# - Create/Edit/Delete test records
```

---

## Connection Details

### PostgreSQL Database
| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 5432 |
| Database | hrmanagement_db |
| Username | hrm_user |
| Password | hrm_secure_password_2024 |

### pgAdmin Web Interface
| Property | Value |
|----------|-------|
| URL | http://localhost:5050 |
| Email | admin@hrmanagement.local |
| Password | admin1234 |

---

## Rollback Procedure

If migration fails and you need to revert to SQLite:

```powershell
# Run rollback script
python scripts/migration/rollback_to_sqlite.py --confirm

# Or manually edit .env:
# Comment out: DATABASE_URL=postgresql://...
# Uncomment: DATABASE_URL=sqlite:///instance/hrmanagement.db
```

---

## Troubleshooting

### Docker Container Won't Start
```powershell
# Check if port 5432 is in use
netstat -ano | findstr "5432"

# Stop conflicting service or change port in docker-compose.yml
```

### Connection Refused
```powershell
# Wait for container to be healthy
docker-compose ps

# Check container logs
docker-compose logs db
```

### Migration Script Fails
```powershell
# Check PostgreSQL is accessible
docker exec hrmanagement_db psql -U hrm_user -d hrmanagement_db -c "SELECT 1"

# Check .env has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

### Alembic Revision Error
```powershell
# If tables already exist, stamp the current revision
alembic stamp 20251202_000000
```

---

## Post-Migration Checklist

- [ ] SQLite database backed up
- [ ] Docker containers running (db, pgadmin)
- [ ] Alembic migrations applied
- [ ] Data migrated from SQLite
- [ ] Verification script passed
- [ ] Application login tested (admin)
- [ ] Application login tested (employee)
- [ ] CRUD operations tested
- [ ] All existing functionality verified

---

## Files Created/Modified

### New Files
- `docker-compose.yml` - PostgreSQL and pgAdmin containers
- `alembic.ini` - Alembic configuration
- `migrations/env.py` - Alembic environment
- `migrations/script.py.mako` - Migration template
- `migrations/versions/20251202_000000_initial_schema.py` - Initial schema
- `scripts/init-db/01-init.sql` - PostgreSQL initialization
- `scripts/migration/migrate_sqlite_to_postgres.py` - Data migration
- `scripts/migration/verify_migration.py` - Verification script
- `scripts/migration/rollback_to_sqlite.py` - Rollback script

### Modified Files
- `.env` - Added DATABASE_URL for PostgreSQL
- `.env.example` - Updated with PostgreSQL example
- `requirements.txt` - Added psycopg2-binary and alembic

---

## Next Steps

After successful migration:

1. **Phase 1**: Implement Company model for corporate accounts
2. Update `platform_conversion_plan.md` progress tracking
3. Consider enabling PostgreSQL features:
   - Row-Level Security for multi-tenancy
   - pg_trgm for fuzzy text search
   - uuid-ossp for UUID primary keys (future)
