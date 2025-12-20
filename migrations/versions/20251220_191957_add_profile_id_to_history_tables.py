"""add_profile_id_to_history_tables

Profile 통합 마이그레이션:
1. 이력 테이블에 profile_id 컬럼 추가
2. Employee 데이터에 profile_id 설정
3. Personal 데이터를 기존 테이블로 마이그레이션

Revision ID: e6f7dc2bfa1d
Revises: a1b2c3d4e5f6
Create Date: 2025-12-20 19:19:57.701828+09:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e6f7dc2bfa1d'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # Step 0: 시퀀스 값 수정 및 employee_id를 nullable로 변경
    # ============================================
    tables = ['educations', 'careers', 'certificates', 'languages',
              'military_services', 'family_members', 'awards', 'project_participations']

    # 시퀀스 값을 현재 max(id) + 1로 리셋
    for table in tables:
        op.execute(f"SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)")

    for table in tables:
        op.alter_column(table, 'employee_id', existing_type=sa.Integer(), nullable=True)

    # ============================================
    # Step 1: 이력 테이블에 profile_id 컬럼 추가
    # ============================================

    # educations
    op.add_column('educations', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_educations_profile', 'educations', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_educations_profile_id', 'educations', ['profile_id'])

    # careers
    op.add_column('careers', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_careers_profile', 'careers', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_careers_profile_id', 'careers', ['profile_id'])

    # certificates
    op.add_column('certificates', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_certificates_profile', 'certificates', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_certificates_profile_id', 'certificates', ['profile_id'])

    # languages
    op.add_column('languages', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_languages_profile', 'languages', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_languages_profile_id', 'languages', ['profile_id'])

    # military_services
    op.add_column('military_services', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_military_services_profile', 'military_services', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_military_services_profile_id', 'military_services', ['profile_id'])

    # family_members
    op.add_column('family_members', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_family_members_profile', 'family_members', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_family_members_profile_id', 'family_members', ['profile_id'])

    # awards
    op.add_column('awards', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_awards_profile', 'awards', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_awards_profile_id', 'awards', ['profile_id'])

    # project_participations
    op.add_column('project_participations', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_project_participations_profile', 'project_participations', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_project_participations_profile_id', 'project_participations', ['profile_id'])

    # ============================================
    # Step 2: Employee 데이터에 profile_id 설정
    # ============================================
    op.execute('''
        UPDATE educations
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = educations.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    op.execute('''
        UPDATE careers
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = careers.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    op.execute('''
        UPDATE certificates
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = certificates.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    op.execute('''
        UPDATE languages
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = languages.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    op.execute('''
        UPDATE military_services
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = military_services.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    op.execute('''
        UPDATE family_members
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = family_members.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    op.execute('''
        UPDATE awards
        SET profile_id = (SELECT profile_id FROM employees WHERE employees.id = awards.employee_id)
        WHERE employee_id IS NOT NULL
    ''')

    # ============================================
    # Step 3: Personal 데이터 마이그레이션
    # ============================================

    # personal_educations -> educations
    # Personal: school_name, school_type, major, degree, admission_date, graduation_date, status, gpa, notes
    # Employee: school_name, school_type, major, degree, admission_date, graduation_date, graduation_status, gpa, note
    op.execute('''
        INSERT INTO educations (profile_id, school_name, school_type, major, degree, admission_date, graduation_date, graduation_status, gpa, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pe.school_name, pe.school_type, pe.major, pe.degree, pe.admission_date, pe.graduation_date, pe.status, pe.gpa, pe.notes
        FROM personal_educations pe
        JOIN personal_profiles pp ON pp.id = pe.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_careers -> careers
    # Personal: company_name, department, position, job_grade, job_title, job_role, responsibilities, start_date, end_date, salary, salary_type, monthly_salary, pay_step, reason_for_leaving, is_current
    # Employee: company_name, department, position, job_grade, job_title, job_role, job_description, start_date, end_date, salary, salary_type, monthly_salary, pay_step, resignation_reason, is_current, note
    op.execute('''
        INSERT INTO careers (profile_id, company_name, department, position, job_grade, job_title, job_role, job_description, start_date, end_date, salary, salary_type, monthly_salary, pay_step, resignation_reason, is_current, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pc.company_name, pc.department, pc.position, pc.job_grade, pc.job_title, pc.job_role, pc.responsibilities, pc.start_date, pc.end_date, pc.salary, pc.salary_type, pc.monthly_salary, pc.pay_step, pc.reason_for_leaving, pc.is_current, pc.responsibilities
        FROM personal_careers pc
        JOIN personal_profiles pp ON pp.id = pc.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_certificates -> certificates
    # Personal: name, issuing_organization, issue_date, expiry_date, certificate_number, grade, notes
    # Employee: certificate_name, issuing_organization, acquisition_date, expiry_date, certificate_number, grade, note
    op.execute('''
        INSERT INTO certificates (profile_id, certificate_name, issuing_organization, acquisition_date, expiry_date, certificate_number, grade, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pc.name, pc.issuing_organization, pc.issue_date, pc.expiry_date, pc.certificate_number, pc.grade, pc.notes
        FROM personal_certificates pc
        JOIN personal_profiles pp ON pp.id = pc.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_languages -> languages
    # Personal: language, proficiency, test_name, score, test_date, notes
    # Employee: language_name, level, exam_name, score, acquisition_date, note
    op.execute('''
        INSERT INTO languages (profile_id, language_name, level, exam_name, score, acquisition_date, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pl.language, pl.proficiency, pl.test_name, pl.score, pl.test_date, pl.notes
        FROM personal_languages pl
        JOIN personal_profiles pp ON pp.id = pl.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_military_services -> military_services
    # Personal: service_type, branch, rank, start_date, end_date, specialty, duty, notes
    # Employee: military_status, service_type, branch, rank, enlistment_date, discharge_date, note
    op.execute('''
        INSERT INTO military_services (profile_id, military_status, service_type, branch, rank, enlistment_date, discharge_date, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pm.service_type, pm.specialty, pm.branch, pm.rank, pm.start_date, pm.end_date, pm.notes
        FROM personal_military_services pm
        JOIN personal_profiles pp ON pp.id = pm.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_families -> family_members
    # Personal: relation, name, birth_date, occupation, contact, is_cohabitant, is_dependent, notes
    # Employee: relation, name, birth_date, occupation, contact, is_cohabitant, is_dependent, note
    op.execute('''
        INSERT INTO family_members (profile_id, relation, name, birth_date, occupation, contact, is_cohabitant, is_dependent, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pf.relation, pf.name, pf.birth_date, pf.occupation, pf.contact, pf.is_cohabitant, pf.is_dependent, pf.notes
        FROM personal_families pf
        JOIN personal_profiles pp ON pp.id = pf.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_awards -> awards
    # Personal: award_name, award_date, institution, description, notes
    # Employee: award_name, award_date, institution, note (description + notes combined)
    op.execute('''
        INSERT INTO awards (profile_id, award_name, award_date, institution, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            pa.award_name, pa.award_date, pa.institution,
            CASE
                WHEN pa.description IS NOT NULL AND pa.notes IS NOT NULL THEN pa.description || ' | ' || pa.notes
                WHEN pa.description IS NOT NULL THEN pa.description
                ELSE pa.notes
            END
        FROM personal_awards pa
        JOIN personal_profiles pp ON pp.id = pa.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')

    # personal_project_participations -> project_participations
    # Personal: project_name, start_date, end_date, duration, role, duty, client, note
    # Employee: project_name, start_date, end_date, duration, role, duty, client, note
    op.execute('''
        INSERT INTO project_participations (profile_id, project_name, start_date, end_date, duration, role, duty, client, note)
        SELECT
            (SELECT p.id FROM profiles p WHERE p.user_id = pp.user_id),
            ppp.project_name, ppp.start_date, ppp.end_date, ppp.duration, ppp.role, ppp.duty, ppp.client, ppp.note
        FROM personal_project_participations ppp
        JOIN personal_profiles pp ON pp.id = ppp.profile_id
        WHERE EXISTS (
            SELECT 1 FROM profiles p WHERE p.user_id = pp.user_id
        )
    ''')


def downgrade() -> None:
    # profile_id 컬럼 및 인덱스, 외래키 제거
    tables = ['educations', 'careers', 'certificates', 'languages',
              'military_services', 'family_members', 'awards', 'project_participations']

    # Personal 데이터 삭제 (employee_id가 NULL인 레코드)
    for table in tables:
        op.execute(f'DELETE FROM {table} WHERE employee_id IS NULL')

    for table in tables:
        op.drop_index(f'ix_{table}_profile_id', table_name=table)
        op.drop_constraint(f'fk_{table}_profile', table, type_='foreignkey')
        op.drop_column(table, 'profile_id')

    # employee_id를 NOT NULL로 복원
    for table in tables:
        op.alter_column(table, 'employee_id', existing_type=sa.Integer(), nullable=False)
