"""
사번 자동생성 유틸리티 테스트

사번 생성, 검증, 중복 확인 기능 테스트
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from app.shared.utils.employee_number import (
    get_employee_number_config,
    generate_employee_number,
    is_valid_employee_number,
    is_employee_number_exists
)
from app.domains.employee.models import Employee


class TestEmployeeNumberConfig:
    """사번 설정 테스트"""

    def test_default_config(self):
        """기본 설정 반환"""
        with patch('app.extensions.system_setting_repo', None):
            config = get_employee_number_config()

            assert config['prefix'] == 'EMP'
            assert config['separator'] == '-'
            assert config['include_year'] is True
            assert config['sequence_digits'] == 4
            assert config['auto_generate'] is True

    def test_config_from_repo(self):
        """시스템 설정에서 사번 설정 조회"""
        mock_repo = Mock()
        mock_repo.get_employee_number_config.return_value = {
            'prefix': 'STAFF',
            'separator': '_',
            'include_year': False,
            'sequence_digits': 5,
            'auto_generate': True,
        }

        with patch('app.extensions.system_setting_repo', mock_repo):
            config = get_employee_number_config()

            assert config['prefix'] == 'STAFF'
            assert config['separator'] == '_'
            assert config['include_year'] is False
            assert config['sequence_digits'] == 5


class TestGenerateEmployeeNumber:
    """사번 생성 테스트"""

    def test_generate_first_number(self, session):
        """첫 사번 생성 (연도 포함)"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config, \
             patch('app.shared.utils.employee_number.datetime') as mock_dt:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }
            mock_dt.now.return_value = datetime(2025, 1, 1)

            result = generate_employee_number()

            assert result == 'EMP-2025-0001'

    def test_generate_number_without_year(self, session):
        """사번 생성 (연도 미포함)"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': False,
                'sequence_digits': 4
            }

            result = generate_employee_number()

            assert result.startswith('EMP-')
            assert len(result.split('-')) == 2

    def test_generate_next_number(self, session):
        """다음 사번 생성"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config, \
             patch('app.shared.utils.employee_number.datetime') as mock_dt:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }
            mock_dt.now.return_value = datetime(2025, 1, 1)

            # 기존 사번 추가
            from app.models import Company
            company = Company(name='테스트회사', business_number='1234567890', representative='대표')
            session.add(company)
            session.commit()

            employee = Employee(
                name='테스트',
                employee_number='EMP-2025-0001',
                company_id=company.id
            )
            session.add(employee)
            session.commit()

            result = generate_employee_number()

            assert result == 'EMP-2025-0002'


class TestValidateEmployeeNumber:
    """사번 검증 테스트"""

    def test_valid_number_with_year(self):
        """유효한 사번 (연도 포함)"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }

            assert is_valid_employee_number('EMP-2025-0001') is True

    def test_valid_number_without_year(self):
        """유효한 사번 (연도 미포함)"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': False,
                'sequence_digits': 4
            }

            assert is_valid_employee_number('EMP-0001') is True

    def test_invalid_empty(self):
        """빈 사번"""
        assert is_valid_employee_number('') is False
        assert is_valid_employee_number(None) is False

    def test_invalid_prefix(self):
        """잘못된 접두사"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }

            assert is_valid_employee_number('STAFF-2025-0001') is False

    def test_invalid_year(self):
        """잘못된 연도"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }

            assert is_valid_employee_number('EMP-1999-0001') is False
            assert is_valid_employee_number('EMP-2101-0001') is False
            assert is_valid_employee_number('EMP-ABCD-0001') is False

    def test_invalid_sequence(self):
        """잘못된 순번"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }

            assert is_valid_employee_number('EMP-2025-0000') is False
            assert is_valid_employee_number('EMP-2025-10000') is False
            assert is_valid_employee_number('EMP-2025-ABCD') is False

    def test_invalid_format(self):
        """잘못된 형식"""
        with patch('app.shared.utils.employee_number.get_employee_number_config') as mock_config:
            mock_config.return_value = {
                'prefix': 'EMP',
                'separator': '-',
                'include_year': True,
                'sequence_digits': 4
            }

            assert is_valid_employee_number('EMP-2025') is False
            assert is_valid_employee_number('EMP-2025-0001-EXTRA') is False
            assert is_valid_employee_number('EMP_2025_0001') is False


class TestEmployeeNumberExists:
    """사번 중복 확인 테스트"""

    def test_number_not_exists(self, session):
        """사번이 존재하지 않음"""
        result = is_employee_number_exists('EMP-2025-9999')
        assert result is False

    def test_number_exists(self, session):
        """사번이 존재함"""
        from app.models import Company

        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(
            name='테스트',
            employee_number='EMP-2025-0001',
            company_id=company.id
        )
        session.add(employee)
        session.commit()

        result = is_employee_number_exists('EMP-2025-0001')
        assert result is True

    def test_number_exists_exclude_self(self, session):
        """사번 존재 확인 (본인 제외)"""
        from app.models import Company

        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(
            name='테스트',
            employee_number='EMP-2025-0001',
            company_id=company.id
        )
        session.add(employee)
        session.commit()

        # 본인 ID 제외하면 중복 아님
        result = is_employee_number_exists('EMP-2025-0001', exclude_id=employee.id)
        assert result is False

        # 다른 ID 제외하면 여전히 중복
        result = is_employee_number_exists('EMP-2025-0001', exclude_id=999)
        assert result is True

