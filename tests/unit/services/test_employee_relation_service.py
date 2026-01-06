"""
EmployeeRelationService 단위 테스트

직원 관계형 데이터 서비스의 핵심 비즈니스 로직 테스트:
- 관계형 데이터 조회 (학력/경력/자격증 등)
- 첨부파일 관리
- 병역 정보 관리
- 관계형 데이터 수정
- 대시보드 데이터 조회
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from app.domains.employee.services.employee_relation_service import (
    EmployeeRelationService,
    employee_relation_service
)


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    repos = {
        'employee_repo': Mock(),
        'family_repo': Mock(),
        'education_repo': Mock(),
        'career_repo': Mock(),
        'certificate_repo': Mock(),
        'language_repo': Mock(),
        'military_repo': Mock(),
        'hr_project_repo': Mock(),
        'project_participation_repo': Mock(),
        'award_repo': Mock(),
        'attachment_repo': Mock(),
        'salary_repo': Mock(),
        'benefit_repo': Mock(),
        'contract_repo': Mock(),
        'salary_history_repo': Mock(),
        'promotion_repo': Mock(),
        'evaluation_repo': Mock(),
        'training_repo': Mock(),
        'attendance_repo': Mock(),
        'insurance_repo': Mock(),
        'asset_repo': Mock(),
        'salary_payment_repo': Mock(),
        'classification_repo': Mock()
    }

    patches = []
    for key, value in repos.items():
        patches.append(patch.object(extensions, key, value))

    with patch.multiple(extensions, **{k: v for k, v in repos.items()}):
        yield employee_relation_service


class TestEmployeeRelationServiceInit:
    """EmployeeRelationService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert employee_relation_service is not None
        assert isinstance(employee_relation_service, EmployeeRelationService)

    def test_service_has_repo_properties(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(employee_relation_service, 'employee_repo')
        assert hasattr(employee_relation_service, 'education_repo')
        assert hasattr(employee_relation_service, 'career_repo')


class TestEmployeeRelationServiceGetLists:
    """관계형 데이터 목록 조회 테스트"""

    def test_get_education_list(self, mock_repos):
        """학력 목록 조회"""
        mock_education = Mock()
        mock_education.to_dict.return_value = {'id': 1, 'school': '테스트대학교'}
        mock_repos.education_repo.find_by_employee_id.return_value = [mock_education]
        
        result = mock_repos.get_education_list(employee_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_repos.education_repo.find_by_employee_id.assert_called_once_with(1)

    def test_get_career_list(self, mock_repos):
        """경력 목록 조회"""
        mock_career = Mock()
        mock_career.to_dict.return_value = {'id': 1, 'company': '테스트회사'}
        mock_repos.career_repo.find_by_employee_id.return_value = [mock_career]
        
        result = mock_repos.get_career_list(employee_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_repos.career_repo.find_by_employee_id.assert_called_once_with(1)

    def test_get_certificate_list(self, mock_repos):
        """자격증 목록 조회"""
        mock_certificate = Mock()
        mock_certificate.to_dict.return_value = {'id': 1, 'name': '정보처리기사'}
        mock_repos.certificate_repo.find_by_employee_id.return_value = [mock_certificate]
        
        result = mock_repos.get_certificate_list(employee_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_family_list(self, mock_repos):
        """가족 목록 조회"""
        mock_family = Mock()
        mock_family.to_dict.return_value = {'id': 1, 'relation': '부'}
        mock_repos.family_repo.find_by_employee_id.return_value = [mock_family]
        
        result = mock_repos.get_family_list(employee_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_language_list(self, mock_repos):
        """어학 목록 조회"""
        mock_language = Mock()
        mock_language.to_dict.return_value = {'id': 1, 'language': '영어'}
        mock_repos.language_repo.find_by_employee_id.return_value = [mock_language]
        
        result = mock_repos.get_language_list(employee_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_military_info(self, mock_repos):
        """병역 정보 조회"""
        mock_military = Mock()
        mock_military.to_dict.return_value = {'id': 1, 'status': '군필'}
        mock_repos.military_repo.find_by_employee_id.return_value = mock_military
        
        result = mock_repos.get_military_info(employee_id=1)
        
        assert isinstance(result, dict)
        assert result['status'] == '군필'

    def test_get_military_info_none(self, mock_repos):
        """병역 정보 조회 - 없음"""
        mock_repos.military_repo.find_by_employee_id.return_value = None
        
        result = mock_repos.get_military_info(employee_id=1)
        
        assert result is None


class TestEmployeeRelationServiceGetInfo:
    """단일 정보 조회 테스트"""

    def test_get_salary_info(self, mock_repos):
        """급여 정보 조회"""
        mock_salary = Mock()
        mock_salary.to_dict.return_value = {'id': 1, 'base_salary': 3000000}
        mock_repos.salary_repo.find_by_employee_id.return_value = mock_salary
        
        result = mock_repos.get_salary_info(employee_id=1)
        
        assert isinstance(result, dict)
        assert result['base_salary'] == 3000000

    def test_get_benefit_info(self, mock_repos):
        """복리후생 정보 조회"""
        mock_benefit = Mock()
        mock_benefit.to_dict.return_value = {'id': 1, 'health_insurance': True}
        mock_repos.benefit_repo.find_by_employee_id.return_value = mock_benefit
        
        result = mock_repos.get_benefit_info(employee_id=1)
        
        assert isinstance(result, dict)
        assert result['health_insurance'] is True

    def test_get_contract_info(self, mock_repos):
        """계약 정보 조회"""
        mock_contract = Mock()
        mock_contract.to_dict.return_value = {'id': 1, 'contract_type': '정규직'}
        mock_repos.contract_repo.find_by_employee_id.return_value = mock_contract
        
        result = mock_repos.get_contract_info(employee_id=1)
        
        assert isinstance(result, dict)
        assert result['contract_type'] == '정규직'


class TestEmployeeRelationServiceAttachment:
    """첨부파일 관리 테스트"""

    def test_create_attachment(self, mock_repos):
        """첨부파일 생성"""
        attachment_data = {
            'employee_id': 1,
            'category': 'resume',
            'file_path': '/path/to/file.pdf'
        }
        mock_repos.attachment_repo.create.return_value = {'id': 1, **attachment_data}
        
        result = mock_repos.create_attachment(attachment_data)
        
        assert isinstance(result, dict)
        assert result['id'] == 1
        mock_repos.attachment_repo.create.assert_called_once_with(attachment_data)

    def test_get_attachment_by_id(self, mock_repos):
        """첨부파일 ID로 조회"""
        mock_attachment = Mock()
        mock_attachment.to_dict.return_value = {'id': 1, 'category': 'resume'}
        mock_repos.attachment_repo.find_by_id.return_value = mock_attachment
        
        result = mock_repos.get_attachment_by_id(attachment_id=1)
        
        assert isinstance(result, dict)
        assert result['id'] == 1

    def test_delete_attachment(self, mock_repos):
        """첨부파일 삭제"""
        mock_repos.attachment_repo.delete.return_value = True
        
        result = mock_repos.delete_attachment(attachment_id=1)
        
        assert result is True
        mock_repos.attachment_repo.delete.assert_called_once_with(1)

    def test_delete_attachment_by_category(self, mock_repos):
        """카테고리별 첨부파일 삭제"""
        mock_repos.attachment_repo.delete_by_category.return_value = True
        
        result = mock_repos.delete_attachment_by_category(employee_id=1, category='resume')
        
        assert result is True
        mock_repos.attachment_repo.delete_by_category.assert_called_once_with(1, 'resume')


class TestEmployeeRelationServiceMilitary:
    """병역 정보 관리 테스트"""

    def test_delete_military_info(self, mock_repos):
        """병역 정보 삭제"""
        mock_repos.military_repo.delete_by_employee_id.return_value = True
        
        result = mock_repos.delete_military_info(employee_id=1)
        
        assert result is True
        mock_repos.military_repo.delete_by_employee_id.assert_called_once_with(1)

    def test_create_military_info(self, mock_repos):
        """병역 정보 생성"""
        military_data = {
            'employee_id': 1,
            'military_status': '군필',
            'branch': '육군'
        }
        mock_military = Mock()
        mock_repos.military_repo.create.return_value = mock_military
        
        result = mock_repos.create_military_info(military_data)
        
        assert result is not None
        mock_repos.military_repo.create.assert_called_once()


class TestEmployeeRelationServiceUpdate:
    """관계형 데이터 수정 테스트"""

    def test_update_education(self, mock_repos):
        """학력 정보 수정"""
        with patch('app.services.employee.employee_relation_service.relation_updater') as mock_updater:
            mock_updater.update_with_commit.return_value = (True, None)
            
            form_data = {'education': [{'id': 1, 'school': '테스트대학교'}]}
            success, error = mock_repos.update_education(employee_id=1, form_data=form_data)
            
            assert success is True
            assert error is None

    def test_update_career(self, mock_repos):
        """경력 정보 수정"""
        with patch('app.services.employee.employee_relation_service.relation_updater') as mock_updater:
            mock_updater.update_with_commit.return_value = (True, None)
            
            form_data = {'career': [{'id': 1, 'company': '테스트회사'}]}
            success, error = mock_repos.update_career(employee_id=1, form_data=form_data)
            
            assert success is True
            assert error is None

    def test_update_certificate(self, mock_repos):
        """자격증 정보 수정"""
        with patch('app.services.employee.employee_relation_service.relation_updater') as mock_updater:
            mock_updater.update_with_commit.return_value = (True, None)
            
            form_data = {'certificate': [{'id': 1, 'name': '정보처리기사'}]}
            success, error = mock_repos.update_certificate(employee_id=1, form_data=form_data)
            
            assert success is True
            assert error is None


class TestEmployeeRelationServiceDashboard:
    """대시보드 데이터 조회 테스트"""

    def test_get_dashboard_data(self, mock_repos):
        """직원 대시보드 데이터 조회"""
        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.hire_date = '2020-01-01'
        mock_employee.status = 'active'
        mock_employee.department = '개발팀'
        mock_employee.position = '사원'
        mock_employee.educations = []
        mock_employee.careers = []
        mock_employee.certificates = []
        mock_employee.languages = []
        
        mock_repos.employee_repo.find_by_id.return_value = mock_employee
        
        result = mock_repos.get_dashboard_data(employee_id=1)
        
        assert isinstance(result, dict)
        assert 'employee' in result
        assert 'stats' in result
        assert 'work_info' in result
        assert result['employee'] == mock_employee

    def test_get_dashboard_data_not_found(self, mock_repos):
        """대시보드 데이터 조회 - 직원 없음"""
        mock_repos.employee_repo.find_by_id.return_value = None
        
        result = mock_repos.get_dashboard_data(employee_id=999)
        
        assert result is None

