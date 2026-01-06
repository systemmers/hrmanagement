"""
Transaction Utils 테스트

트랜잭션 관리 유틸리티 테스트
"""
import pytest
from unittest.mock import patch, Mock

from app.utils.transaction import atomic_transaction, transactional
from app.database import db


class TestAtomicTransaction:
    """atomic_transaction 컨텍스트 매니저 테스트"""

    def test_atomic_transaction_success(self, session):
        """트랜잭션 성공 시 commit"""
        with patch.object(db.session, 'commit') as mock_commit, \
             patch.object(db.session, 'rollback') as mock_rollback:
            with atomic_transaction():
                pass

            mock_commit.assert_called_once()
            mock_rollback.assert_not_called()

    def test_atomic_transaction_rollback_on_exception(self, session):
        """예외 발생 시 rollback"""
        with patch.object(db.session, 'commit') as mock_commit, \
             patch.object(db.session, 'rollback') as mock_rollback:
            with pytest.raises(ValueError):
                with atomic_transaction():
                    raise ValueError('테스트 에러')

            mock_commit.assert_not_called()
            mock_rollback.assert_called_once()

    def test_atomic_transaction_nested(self, session):
        """중첩된 트랜잭션"""
        with patch.object(db.session, 'commit') as mock_commit:
            with atomic_transaction():
                with atomic_transaction():
                    pass

            assert mock_commit.call_count == 2


class TestTransactionalDecorator:
    """transactional 데코레이터 테스트"""

    def test_transactional_decorator_success(self, session):
        """데코레이터 성공 시 commit"""
        with patch.object(db.session, 'commit') as mock_commit:

            @transactional
            def test_function():
                return 'success'

            result = test_function()

            assert result == 'success'
            mock_commit.assert_called_once()

    def test_transactional_decorator_rollback_on_exception(self, session):
        """데코레이터 예외 발생 시 rollback"""
        with patch.object(db.session, 'rollback') as mock_rollback:

            @transactional
            def test_function():
                raise ValueError('테스트 에러')

            with pytest.raises(ValueError):
                test_function()

            mock_rollback.assert_called_once()

    def test_transactional_decorator_with_args(self, session):
        """데코레이터 인자 전달"""
        with patch.object(db.session, 'commit') as mock_commit:

            @transactional
            def test_function(x, y):
                return x + y

            result = test_function(1, 2)

            assert result == 3
            mock_commit.assert_called_once()

