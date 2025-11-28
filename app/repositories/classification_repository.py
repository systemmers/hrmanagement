"""
Classification Options Repository

부서, 직급, 재직상태 등의 분류 옵션을 관리합니다.
"""
from typing import List, Dict
from app.database import db
from app.models import ClassificationOption
from .base_repository import BaseRepository


class ClassificationOptionsRepository(BaseRepository):
    """분류 옵션 저장소"""

    def __init__(self):
        super().__init__(ClassificationOption)

    def get_departments(self) -> List[Dict]:
        """부서 목록 조회"""
        return self._get_by_category('department')

    def get_positions(self) -> List[Dict]:
        """직급 목록 조회"""
        return self._get_by_category('position')

    def get_statuses(self) -> List[Dict]:
        """재직상태 목록 조회"""
        return self._get_by_category('status')

    def get_all_options(self) -> Dict[str, List[Dict]]:
        """모든 분류 옵션 조회"""
        return {
            'departments': self.get_departments(),
            'positions': self.get_positions(),
            'statuses': self.get_statuses()
        }

    def add_department(self, value: str, label: str = None) -> Dict:
        """부서 추가"""
        return self._add_option('department', value, label)

    def add_position(self, value: str, label: str = None) -> Dict:
        """직급 추가"""
        return self._add_option('position', value, label)

    def add_status(self, value: str, label: str = None) -> Dict:
        """재직상태 추가"""
        return self._add_option('status', value, label)

    def remove_department(self, value: str) -> bool:
        """부서 삭제"""
        return self._remove_option('department', value)

    def remove_position(self, value: str) -> bool:
        """직급 삭제"""
        return self._remove_option('position', value)

    def remove_status(self, value: str) -> bool:
        """재직상태 삭제"""
        return self._remove_option('status', value)

    def update_sort_order(self, category: str, value: str, sort_order: int) -> bool:
        """정렬 순서 수정"""
        option = ClassificationOption.query.filter_by(
            category=category,
            value=value
        ).first()

        if option:
            option.sort_order = sort_order
            db.session.commit()
            return True
        return False

    def _get_by_category(self, category: str) -> List[Dict]:
        """카테고리별 옵션 조회"""
        options = ClassificationOption.query.filter_by(
            category=category
        ).order_by(ClassificationOption.sort_order).all()

        return [
            {'value': opt.value, 'label': opt.label or opt.value}
            for opt in options
        ]

    def _add_option(self, category: str, value: str, label: str = None) -> Dict:
        """옵션 추가"""
        # 중복 확인
        existing = ClassificationOption.query.filter_by(
            category=category,
            value=value
        ).first()

        if existing:
            return existing.to_dict()

        # 정렬 순서 계산
        max_order = db.session.query(
            db.func.max(ClassificationOption.sort_order)
        ).filter_by(category=category).scalar() or 0

        option = ClassificationOption(
            category=category,
            value=value,
            label=label or value,
            sort_order=max_order + 1
        )

        db.session.add(option)
        db.session.commit()
        return option.to_dict()

    def _remove_option(self, category: str, value: str) -> bool:
        """옵션 삭제"""
        option = ClassificationOption.query.filter_by(
            category=category,
            value=value
        ).first()

        if option:
            db.session.delete(option)
            db.session.commit()
            return True
        return False
