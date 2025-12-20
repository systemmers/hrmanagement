# Phase 4 Migration Scripts (Archived)

**Archive Date**: 2025-12-20
**Status**: Completed and Archived

## Overview

These scripts were used for the Phase 4 Unified Profile migration.
All migrations have been successfully completed and verified.

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `migrate_to_profiles.py` | personal_profiles -> profiles, employees -> profiles 연결 | Completed |
| `migrate_personal_relations.py` | Personal 계정 이력 데이터 마이그레이션 | Completed |
| `migrate_employee_relations.py` | Employee 이력 데이터 마이그레이션 | Completed |
| `migrate_test_data.py` | 테스트 데이터 초기 마이그레이션 | Completed |
| `migrate_test_data_phase3.py` | Phase 3 관계 데이터 마이그레이션 | Completed |

## Migration Results

- `personal_profiles`: 10 records -> `profiles` (with user_id)
- `employees`: 50 records -> linked to `profiles` (via profile_id)
- Total `profiles`: 60 records

## Security Note

These scripts contain hardcoded DATABASE_URL for development purposes.
Do NOT use in production without proper environment variable handling.

## Rerun Safety

All scripts use `WHERE NOT EXISTS` or similar patterns to prevent duplicate data.
They can be safely re-run if needed, but this is not recommended.
