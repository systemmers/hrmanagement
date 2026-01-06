"""
직원 폼 추출 및 관계형 데이터 업데이트 테스트

form_extractors와 relation_updaters 모듈 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

from app.blueprints.employees.form_extractors import (
    extract_employee_from_form,
    extract_basic_fields_from_form,
    extract_education_list,
    extract_career_list,
    extract_certificate_list,
    extract_family_list,
    extract_language_list
)


class TestExtractEmployeeFromForm:
    """직원 폼 추출 테스트"""

    def test_extract_employee_full(self):
        """전체 직원 정보 추출 테스트"""
        form_data = {
            'name': '홍길동',
            'department': '개발팀',
            'position': '대리',
            'status': 'active',
            'phone': '010-1234-5678',
            'email': 'test@example.com'
        }
        
        employee = extract_employee_from_form(form_data, 0)
        
        assert employee.name == '홍길동'
        assert employee.department == '개발팀'
        assert employee.position == '대리'
        assert employee.status == 'active'
        assert employee.phone == '010-1234-5678'
        assert employee.email == 'test@example.com'

    def test_extract_employee_minimal(self):
        """최소 직원 정보 추출 테스트"""
        form_data = {
            'name': '김철수'
        }
        
        employee = extract_employee_from_form(form_data, 0)
        
        assert employee.name == '김철수'
        assert employee.department == ''

    def test_extract_employee_with_id(self):
        """ID를 포함한 직원 정보 추출 테스트"""
        form_data = {
            'name': '홍길동'
        }
        
        employee = extract_employee_from_form(form_data, 123)
        
        assert employee.id == 123
        assert employee.name == '홍길동'


class TestExtractBasicFields:
    """기본 필드 추출 테스트"""

    def test_extract_basic_fields_full(self):
        """전체 기본 필드 추출 테스트"""
        form_data = {
            'name': '홍길동',
            'phone': '010-1234-5678',
            'email': 'test@example.com',
            'department': '개발팀',
            'position': '대리'
        }
        
        result = extract_basic_fields_from_form(form_data)
        
        assert result['name'] == '홍길동'
        assert 'phone' in result or 'email' in result

    def test_extract_basic_fields_empty(self):
        """빈 폼 데이터 테스트"""
        form_data = {}
        
        result = extract_basic_fields_from_form(form_data)
        
        assert isinstance(result, dict)
        assert result.get('name') == ''


class TestExtractEducationList:
    """학력 목록 추출 테스트"""

    def test_extract_education_list_full(self):
        """학력 목록 추출 테스트"""
        form_data = {
            'education_school_name[]': ['서울대학교'],
            'education_major[]': ['컴퓨터공학'],
            'education_degree[]': ['학사'],
            'education_school_type[]': ['대학교'],
            'education_graduation_year[]': ['2019']
        }
        
        result = extract_education_list(form_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['school_name'] == '서울대학교'
        assert result[0]['major'] == '컴퓨터공학'

    def test_extract_education_list_empty(self):
        """빈 학력 목록 테스트"""
        form_data = {}
        
        result = extract_education_list(form_data)
        
        assert isinstance(result, list)


class TestExtractCareerList:
    """경력 목록 추출 테스트"""

    def test_extract_career_list_full(self):
        """경력 목록 추출 테스트"""
        form_data = {
            'career_company_name[]': ['ABC Company'],
            'career_position[]': ['선임'],
            'career_start_date[]': ['2020-01-01'],
            'career_end_date[]': ['2022-12-31']
        }
        
        result = extract_career_list(form_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['company_name'] == 'ABC Company'


class TestExtractCertificateList:
    """자격증 목록 추출 테스트"""

    def test_extract_certificate_list_full(self):
        """자격증 목록 추출 테스트"""
        form_data = {
            'certificate_name[]': ['정보처리기사'],
            'certificate_number[]': ['ABC-1234'],
            'certificate_issuing_organization[]': ['한국산업인력공단'],
            'certificate_acquisition_date[]': ['2020-06-30']
        }
        
        result = extract_certificate_list(form_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['certificate_name'] == '정보처리기사'


class TestExtractFamilyList:
    """가족 정보 목록 추출 테스트"""

    def test_extract_family_list_full(self):
        """가족 정보 목록 추출 테스트"""
        form_data = {
            'family_relation[]': ['배우자'],
            'family_name[]': ['김영희'],
            'family_birth_date[]': ['1990-05-15'],
            'family_is_cohabitant[]': ['동거']
        }
        
        result = extract_family_list(form_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == '김영희'


class TestExtractLanguageList:
    """언어 능력 목록 추출 테스트"""

    def test_extract_language_list_full(self):
        """언어 능력 목록 추출 테스트"""
        form_data = {
            'language_language[]': ['영어'],
            'language_level[]': ['고급'],
            'language_test_name[]': ['TOEIC'],
            'language_score[]': ['900']
        }
        
        result = extract_language_list(form_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['language_name'] == '영어'

