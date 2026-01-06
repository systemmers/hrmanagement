"""
Company Model 테스트

Company 모델의 메서드 테스트:
- to_dict()
- from_dict()
- verify() 메서드
"""
import pytest

from app.models import Company


class TestCompanyModel:
    """Company 모델 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session

    @pytest.mark.unit
    def test_to_dict(self, session):
        """to_dict() 메서드 테스트"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동'
        )
        session.add(company)
        session.commit()

        result = company.to_dict()

        assert isinstance(result, dict)
        assert result['name'] == '테스트법인'
        assert result['business_number'] == '1234567890'
        assert result['id'] == company.id

    @pytest.mark.unit
    def test_from_dict(self, session):
        """from_dict() 메서드 테스트"""
        data = {
            'name': '새법인',
            'business_number': '9876543210',
            'representative': '김철수',
            'business_type': '서비스업'
        }

        company = Company.from_dict(data)
        session.add(company)
        session.commit()

        assert company.name == '새법인'
        assert company.business_number == '9876543210'
        assert company.representative == '김철수'

    @pytest.mark.unit
    def test_verify(self, session):
        """법인 인증 메서드 테스트"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동',
            is_verified=False
        )
        session.add(company)
        session.commit()

        company.verify()
        session.commit()

        assert company.is_verified is True

