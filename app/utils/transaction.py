"""
트랜잭션 관리 유틸리티 (SSOT)

Phase 27.1: 트랜잭션 중앙화
- atomic_transaction(): 컨텍스트 매니저
- transactional: 데코레이터

DRY 원칙: 모든 트랜잭션 래핑은 이 모듈을 통해 수행
"""
from contextlib import contextmanager
from functools import wraps
from typing import Callable, TypeVar

from app.database import db

T = TypeVar('T')


@contextmanager
def atomic_transaction():
    """단일 트랜잭션 컨텍스트 매니저 (SSOT)

    모든 작업이 성공하면 commit, 하나라도 실패하면 rollback.

    사용법:
        with atomic_transaction():
            repo.delete_by_id(id, commit=False)
            repo.create(data, commit=False)
            # 모든 작업 성공 시 자동 commit

        # 또는 Service 호출
        with atomic_transaction():
            service.delete_all_educations(id, commit=False)
            service.add_education(id, data, commit=False)

    주의:
        - with 블록 내에서 commit=False 사용 필수
        - 블록 종료 시 자동으로 commit 또는 rollback
    """
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def transactional(f: Callable[..., T]) -> Callable[..., T]:
    """트랜잭션 래핑 데코레이터

    함수 전체를 단일 트랜잭션으로 래핑합니다.
    예외 발생 시 자동 rollback.

    사용법:
        @transactional
        def update_employee_relations(employee_id, form_data):
            service.delete_all(employee_id, commit=False)
            service.create(employee_id, data, commit=False)
            # 자동 commit

    Args:
        f: 래핑할 함수

    Returns:
        트랜잭션이 적용된 함수
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with atomic_transaction():
            return f(*args, **kwargs)
    return decorated_function
