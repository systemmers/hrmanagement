"""
AttachmentRepository 단위 테스트

첨부파일 CRUD 기능 테스트
"""
import pytest
from datetime import datetime
from app.domains.employee.repositories import AttachmentRepository
from app.domains.employee.models import Attachment
from app.domains.employee.models import Employee
from app.domains.company.models import Company


class TestAttachmentRepositoryInit:
    """AttachmentRepository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = AttachmentRepository()
        assert repo is not None
        assert repo.model_class == Attachment


class TestAttachmentRepositoryQuery:
    """첨부파일 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = AttachmentRepository()

    def test_get_by_category(self, session):
        """카테고리별 첨부파일 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(name='테스트', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()

        attachment1 = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume.pdf',
            file_path='/uploads/resume.pdf',
            upload_date=datetime.now()
        )
        attachment2 = Attachment(
            employee_id=employee.id,
            category='certificate',
            file_name='cert.pdf',
            file_path='/uploads/cert.pdf',
            upload_date=datetime.now()
        )
        session.add_all([attachment1, attachment2])
        session.commit()

        result = self.repo.get_by_category(employee.id, 'resume')

        assert len(result) == 1
        assert result[0]['file_name'] == 'resume.pdf'

    def test_get_by_file_type(self, session):
        """파일 유형별 첨부파일 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(name='테스트', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()

        attachment1 = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume.pdf',
            file_path='/uploads/resume.pdf',
            file_type='pdf',
            upload_date=datetime.now()
        )
        attachment2 = Attachment(
            employee_id=employee.id,
            category='photo',
            file_name='photo.jpg',
            file_path='/uploads/photo.jpg',
            file_type='image',
            upload_date=datetime.now()
        )
        session.add_all([attachment1, attachment2])
        session.commit()

        result = self.repo.get_by_file_type(employee.id, 'pdf')

        assert len(result) == 1
        assert result[0]['file_type'] == 'pdf'

    def test_get_one_by_category(self, session):
        """카테고리별 최신 첨부파일 1개 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(name='테스트', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()

        attachment1 = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume_old.pdf',
            file_path='/uploads/resume_old.pdf',
            upload_date=datetime(2024, 1, 1)
        )
        attachment2 = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume_new.pdf',
            file_path='/uploads/resume_new.pdf',
            upload_date=datetime(2025, 1, 1)
        )
        session.add_all([attachment1, attachment2])
        session.commit()

        result = self.repo.get_one_by_category(employee.id, 'resume')

        assert result is not None
        assert result['file_name'] == 'resume_new.pdf'

    def test_get_one_by_category_not_found(self, session):
        """카테고리별 첨부파일 조회 (없음)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(name='테스트', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()

        result = self.repo.get_one_by_category(employee.id, 'nonexistent')
        assert result is None


class TestAttachmentRepositoryDelete:
    """첨부파일 삭제 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = AttachmentRepository()

    def test_delete_by_category(self, session):
        """카테고리별 첨부파일 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(name='테스트', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()

        attachment1 = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume1.pdf',
            file_path='/uploads/resume1.pdf',
            upload_date=datetime.now()
        )
        attachment2 = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume2.pdf',
            file_path='/uploads/resume2.pdf',
            upload_date=datetime.now()
        )
        session.add_all([attachment1, attachment2])
        session.commit()

        result = self.repo.delete_by_category(employee.id, 'resume')

        assert result is True

        # 실제로 삭제되었는지 확인
        remaining = Attachment.query.filter_by(
            employee_id=employee.id,
            category='resume'
        ).all()
        assert len(remaining) == 0

    def test_delete_by_category_not_found(self, session):
        """존재하지 않는 카테고리 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        employee = Employee(name='테스트', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()

        result = self.repo.delete_by_category(employee.id, 'nonexistent')
        assert result is False

