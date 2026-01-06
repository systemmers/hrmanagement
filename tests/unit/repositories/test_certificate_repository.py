"""
CertificateRepository 단위 테스트
"""
import pytest
from app.repositories.certificate_repository import CertificateRepository
from app.models.certificate import Certificate


class TestCertificateRepository:
    """CertificateRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CertificateRepository()

    @pytest.mark.unit
    def test_create_certificate(self, session, test_employee):
        """자격증 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'certificate_name': '정보처리기사',
            'issuing_organization': '한국산업인력공단'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['certificate_name'] == '정보처리기사'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_employee_id(self, session, test_employee):
        """직원 ID로 자격증 조회"""
        certificate = Certificate(
            employee_id=test_employee.id,
            certificate_name='정보처리기사'
        )
        session.add(certificate)
        session.commit()

        result = self.repo.find_by_employee_id(test_employee.id)

        assert len(result) >= 1
        assert any(c.certificate_name == '정보처리기사' for c in result)

