"""Initial schema migration from SQLite to PostgreSQL

Revision ID: 20251202_000000
Revises:
Create Date: 2025-12-02 00:00:00.000000

This migration creates all tables for the HR Management system.
It is designed to be compatible with both SQLite and PostgreSQL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251202_000000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organizations table (self-referential for tree structure)
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), unique=True, nullable=True),
        sa.Column('org_type', sa.String(50), nullable=False, server_default='department'),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),  # FK added later
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_organizations_parent_id', 'organizations', ['parent_id'])
    op.create_index('ix_organizations_org_type', 'organizations', ['org_type'])

    # Employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_number', sa.String(20), unique=True, nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('name_cn', sa.String(100), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('nationality', sa.String(50), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('address_detail', sa.String(255), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('emergency_contact', sa.String(100), nullable=True),
        sa.Column('emergency_phone', sa.String(20), nullable=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('position', sa.String(50), nullable=True),
        sa.Column('rank', sa.String(50), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('resignation_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('profile_image', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_employees_name', 'employees', ['name'])
    op.create_index('ix_employees_organization_id', 'employees', ['organization_id'])
    op.create_index('ix_employees_status', 'employees', ['status'])

    # Add FK from organizations.manager_id to employees.id
    op.create_foreign_key(
        'fk_organizations_manager_id',
        'organizations', 'employees',
        ['manager_id'], ['id']
    )

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(256), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='employee'),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Classification Options table
    op.create_table(
        'classification_options',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_classification_options_category', 'classification_options', ['category'])
    op.create_unique_constraint('uq_classification_options_category_code', 'classification_options', ['category', 'code'])

    # System Settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_system_settings_key', 'system_settings', ['key'])

    # Education table
    op.create_table(
        'educations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('school_name', sa.String(100), nullable=False),
        sa.Column('degree', sa.String(50), nullable=True),
        sa.Column('major', sa.String(100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_graduated', sa.Boolean(), server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_educations_employee_id', 'educations', ['employee_id'])

    # Careers table
    op.create_table(
        'careers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_name', sa.String(100), nullable=False),
        sa.Column('position', sa.String(50), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_careers_employee_id', 'careers', ['employee_id'])

    # Certificates table
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('issuing_organization', sa.String(100), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('certificate_number', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_certificates_employee_id', 'certificates', ['employee_id'])

    # Family Members table
    op.create_table(
        'family_members',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('occupation', sa.String(100), nullable=True),
        sa.Column('is_dependent', sa.Boolean(), server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_family_members_employee_id', 'family_members', ['employee_id'])

    # Languages table
    op.create_table(
        'languages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('language', sa.String(50), nullable=False),
        sa.Column('proficiency', sa.String(50), nullable=True),
        sa.Column('test_name', sa.String(100), nullable=True),
        sa.Column('test_score', sa.String(50), nullable=True),
        sa.Column('test_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_languages_employee_id', 'languages', ['employee_id'])

    # Military Service table
    op.create_table(
        'military_services',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_type', sa.String(50), nullable=True),
        sa.Column('branch', sa.String(50), nullable=True),
        sa.Column('rank', sa.String(50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('discharge_type', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_military_services_employee_id', 'military_services', ['employee_id'])

    # Salaries table
    op.create_table(
        'salaries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('base_salary', sa.Numeric(15, 2), nullable=True),
        sa.Column('allowances', sa.Numeric(15, 2), nullable=True),
        sa.Column('deductions', sa.Numeric(15, 2), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_salaries_employee_id', 'salaries', ['employee_id'])

    # Benefits table
    op.create_table(
        'benefits',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('benefit_type', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_benefits_employee_id', 'benefits', ['employee_id'])

    # Contracts table
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contract_type', sa.String(50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('salary', sa.Numeric(15, 2), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('document_path', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_contracts_employee_id', 'contracts', ['employee_id'])

    # Salary History table
    op.create_table(
        'salary_histories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('previous_salary', sa.Numeric(15, 2), nullable=True),
        sa.Column('new_salary', sa.Numeric(15, 2), nullable=True),
        sa.Column('change_type', sa.String(50), nullable=True),
        sa.Column('change_date', sa.Date(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_salary_histories_employee_id', 'salary_histories', ['employee_id'])

    # Promotions table
    op.create_table(
        'promotions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('previous_position', sa.String(50), nullable=True),
        sa.Column('new_position', sa.String(50), nullable=True),
        sa.Column('previous_rank', sa.String(50), nullable=True),
        sa.Column('new_rank', sa.String(50), nullable=True),
        sa.Column('promotion_date', sa.Date(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_promotions_employee_id', 'promotions', ['employee_id'])

    # Evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluation_period', sa.String(50), nullable=True),
        sa.Column('evaluator_id', sa.Integer(), nullable=True),
        sa.Column('score', sa.Numeric(5, 2), nullable=True),
        sa.Column('grade', sa.String(10), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('evaluation_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_evaluations_employee_id', 'evaluations', ['employee_id'])

    # Trainings table
    op.create_table(
        'trainings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('training_name', sa.String(100), nullable=False),
        sa.Column('training_type', sa.String(50), nullable=True),
        sa.Column('provider', sa.String(100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('hours', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Numeric(15, 2), nullable=True),
        sa.Column('result', sa.String(50), nullable=True),
        sa.Column('certificate_issued', sa.Boolean(), server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_trainings_employee_id', 'trainings', ['employee_id'])

    # Attendance table
    op.create_table(
        'attendances',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in', sa.Time(), nullable=True),
        sa.Column('check_out', sa.Time(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('work_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('overtime_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_attendances_employee_id', 'attendances', ['employee_id'])
    op.create_index('ix_attendances_date', 'attendances', ['date'])

    # Insurances table
    op.create_table(
        'insurances',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insurance_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(100), nullable=True),
        sa.Column('policy_number', sa.String(50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('premium', sa.Numeric(15, 2), nullable=True),
        sa.Column('coverage_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_insurances_employee_id', 'insurances', ['employee_id'])

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_projects_employee_id', 'projects', ['employee_id'])

    # Awards table
    op.create_table(
        'awards',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('award_name', sa.String(100), nullable=False),
        sa.Column('award_type', sa.String(50), nullable=True),
        sa.Column('award_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_awards_employee_id', 'awards', ['employee_id'])

    # Assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_name', sa.String(100), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=True),
        sa.Column('serial_number', sa.String(100), nullable=True),
        sa.Column('assigned_date', sa.Date(), nullable=True),
        sa.Column('return_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_assets_employee_id', 'assets', ['employee_id'])

    # Salary Payments table
    op.create_table(
        'salary_payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_period', sa.String(20), nullable=True),
        sa.Column('base_salary', sa.Numeric(15, 2), nullable=True),
        sa.Column('allowances', sa.Numeric(15, 2), nullable=True),
        sa.Column('deductions', sa.Numeric(15, 2), nullable=True),
        sa.Column('net_salary', sa.Numeric(15, 2), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_salary_payments_employee_id', 'salary_payments', ['employee_id'])
    op.create_index('ix_salary_payments_payment_date', 'salary_payments', ['payment_date'])

    # Attachments table
    op.create_table(
        'attachments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_attachments_employee_id', 'attachments', ['employee_id'])
    op.create_index('ix_attachments_category', 'attachments', ['category'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('attachments')
    op.drop_table('salary_payments')
    op.drop_table('assets')
    op.drop_table('awards')
    op.drop_table('projects')
    op.drop_table('insurances')
    op.drop_table('attendances')
    op.drop_table('trainings')
    op.drop_table('evaluations')
    op.drop_table('promotions')
    op.drop_table('salary_histories')
    op.drop_table('contracts')
    op.drop_table('benefits')
    op.drop_table('salaries')
    op.drop_table('military_services')
    op.drop_table('languages')
    op.drop_table('family_members')
    op.drop_table('certificates')
    op.drop_table('careers')
    op.drop_table('educations')
    op.drop_table('system_settings')
    op.drop_table('classification_options')
    op.drop_table('users')
    op.drop_foreign_key('fk_organizations_manager_id', 'organizations')
    op.drop_table('employees')
    op.drop_table('organizations')
