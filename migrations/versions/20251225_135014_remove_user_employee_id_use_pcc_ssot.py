"""remove_user_employee_id_use_pcc_ssot

User-Employee 관계를 PersonCorporateContract 기반 SSOT로 전환합니다.

변경 내용:
1. User.employee_id 데이터를 PersonCorporateContract로 마이그레이션
2. users.employee_id 컬럼 삭제
3. 성능 인덱스 추가

Revision ID: 10fe4aba3d57
Revises: remove_snapshot_cols
Create Date: 2025-12-25 13:50:14.295063+09:00

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '10fe4aba3d57'
down_revision: Union[str, None] = 'remove_snapshot_cols'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    User.employee_id를 PersonCorporateContract SSOT로 마이그레이션 후 컬럼 삭제
    """
    conn = op.get_bind()

    # Step 1: User.employee_id가 있지만 PersonCorporateContract가 없는 경우 생성
    print("Step 1: User.employee_id 데이터를 PersonCorporateContract로 마이그레이션...")

    # 마이그레이션 필요한 데이터 조회
    missing_contracts = conn.execute(text("""
        SELECT u.id as user_id, u.employee_id, e.company_id
        FROM users u
        JOIN employees e ON u.employee_id = e.id
        WHERE u.employee_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM person_corporate_contracts pcc
            WHERE pcc.person_user_id = u.id
            AND pcc.company_id = e.company_id
            AND pcc.status = 'approved'
        )
    """)).fetchall()

    print(f"  마이그레이션 필요한 레코드: {len(missing_contracts)}개")

    # PersonCorporateContract 레코드 생성
    for row in missing_contracts:
        user_id, employee_id, company_id = row
        conn.execute(text("""
            INSERT INTO person_corporate_contracts
            (person_user_id, company_id, status, contract_type, requested_by,
             requested_at, approved_at, created_at, updated_at)
            VALUES
            (:user_id, :company_id, 'approved', 'employment', 'company',
             :now, :now, :now, :now)
        """), {
            'user_id': user_id,
            'company_id': company_id,
            'now': datetime.utcnow()
        })
        print(f"  PersonCorporateContract 생성: User {user_id} -> Company {company_id}")

    # Step 2: 백업 테이블 생성 (롤백용)
    print("\nStep 2: 백업 테이블 생성...")
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS _user_employee_backup AS
        SELECT id, employee_id FROM users WHERE employee_id IS NOT NULL
    """))
    backup_count = conn.execute(text("SELECT COUNT(*) FROM _user_employee_backup")).scalar()
    print(f"  백업된 레코드: {backup_count}개")

    # Step 3: 외래 키 제약조건 삭제
    print("\nStep 3: 외래 키 제약조건 삭제...")
    op.drop_constraint('users_employee_id_fkey', 'users', type_='foreignkey')
    print("  users_employee_id_fkey 삭제 완료")

    # Step 4: employee_id 컬럼 삭제
    print("\nStep 4: employee_id 컬럼 삭제...")
    op.drop_column('users', 'employee_id')
    print("  users.employee_id 컬럼 삭제 완료")

    # Step 5: 성능 인덱스 추가
    print("\nStep 5: 성능 인덱스 추가...")
    op.create_index(
        'idx_pcc_person_user_company_status',
        'person_corporate_contracts',
        ['person_user_id', 'company_id', 'status']
    )
    print("  idx_pcc_person_user_company_status 인덱스 생성 완료")

    print("\n마이그레이션 완료: User-Employee 관계가 PersonCorporateContract SSOT로 전환됨")


def downgrade() -> None:
    """
    employee_id 컬럼 복원 및 데이터 복구
    """
    conn = op.get_bind()

    # Step 1: 인덱스 삭제
    print("Step 1: 성능 인덱스 삭제...")
    op.drop_index('idx_pcc_person_user_company_status', 'person_corporate_contracts')
    print("  idx_pcc_person_user_company_status 인덱스 삭제 완료")

    # Step 2: employee_id 컬럼 추가
    print("\nStep 2: employee_id 컬럼 추가...")
    op.add_column('users', sa.Column('employee_id', sa.Integer(), nullable=True))
    print("  users.employee_id 컬럼 추가 완료")

    # Step 3: 백업 테이블에서 데이터 복원
    print("\nStep 3: 백업 데이터 복원...")
    backup_exists = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = '_user_employee_backup'
        )
    """)).scalar()

    if backup_exists:
        conn.execute(text("""
            UPDATE users u
            SET employee_id = b.employee_id
            FROM _user_employee_backup b
            WHERE u.id = b.id
        """))
        restored_count = conn.execute(text(
            "SELECT COUNT(*) FROM users WHERE employee_id IS NOT NULL"
        )).scalar()
        print(f"  복원된 레코드: {restored_count}개")

        # 백업 테이블 삭제
        conn.execute(text("DROP TABLE IF EXISTS _user_employee_backup"))
        print("  백업 테이블 삭제 완료")
    else:
        print("  경고: 백업 테이블이 없습니다. PersonCorporateContract에서 복원 시도...")
        # PersonCorporateContract에서 최선 노력으로 복원
        conn.execute(text("""
            UPDATE users u
            SET employee_id = (
                SELECT e.id
                FROM employees e
                JOIN person_corporate_contracts pcc ON pcc.company_id = e.company_id
                WHERE pcc.person_user_id = u.id
                AND pcc.status = 'approved'
                LIMIT 1
            )
            WHERE u.account_type = 'employee_sub'
        """))

    # Step 4: 외래 키 제약조건 복원
    print("\nStep 4: 외래 키 제약조건 복원...")
    op.create_foreign_key(
        'users_employee_id_fkey',
        'users',
        'employees',
        ['employee_id'],
        ['id']
    )
    print("  users_employee_id_fkey 복원 완료")

    print("\n롤백 완료: User.employee_id 컬럼 복원됨")
