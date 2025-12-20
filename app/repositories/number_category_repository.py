"""
Number Category Repository

번호 체계 분류코드를 관리합니다.
"""
from typing import Dict, Optional, List
from app.database import db
from app.models import NumberCategory, NumberRegistry
from .base_repository import BaseRepository


class NumberCategoryRepository(BaseRepository[NumberCategory]):
    """번호 분류코드 저장소"""

    def __init__(self):
        super().__init__(NumberCategory)

    def get_by_company(self, company_id: int, type_filter: str = None) -> List[Dict]:
        """법인별 분류코드 조회"""
        query = NumberCategory.query.filter_by(
            company_id=company_id,
            is_active=True
        )

        if type_filter:
            query = query.filter_by(type=type_filter)

        return [c.to_dict() for c in query.order_by(NumberCategory.code).all()]

    def get_employee_categories(self, company_id: int) -> List[Dict]:
        """사번 분류코드 조회"""
        return self.get_by_company(company_id, NumberCategory.TYPE_EMPLOYEE)

    def get_asset_categories(self, company_id: int) -> List[Dict]:
        """자산번호 분류코드 조회"""
        return self.get_by_company(company_id, NumberCategory.TYPE_ASSET)

    def get_by_code(self, company_id: int, type_code: str, code: str) -> Optional[Dict]:
        """코드로 분류 조회"""
        category = NumberCategory.query.filter_by(
            company_id=company_id,
            type=type_code,
            code=code.upper()
        ).first()

        return category.to_dict() if category else None

    def create_category(self, company_id: int, type_code: str, code: str,
                        name: str, description: str = None) -> Dict:
        """분류코드 생성"""
        # 중복 확인
        existing = NumberCategory.query.filter_by(
            company_id=company_id,
            type=type_code,
            code=code.upper()
        ).first()

        if existing:
            return existing.to_dict()

        category = NumberCategory(
            company_id=company_id,
            type=type_code,
            code=code.upper()[:6],
            name=name,
            description=description,
            current_sequence=0,
            is_active=True
        )

        db.session.add(category)
        db.session.commit()
        return category.to_dict()

    def update_category(self, category_id: int, company_id: int, data: Dict) -> Optional[Dict]:
        """분류코드 수정"""
        category = NumberCategory.query.filter_by(
            id=category_id,
            company_id=company_id
        ).first()

        if not category:
            return None

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'isActive' in data:
            category.is_active = data['isActive']

        db.session.commit()
        return category.to_dict()

    def delete_category(self, category_id: int, company_id: int) -> bool:
        """분류코드 삭제 (사용중인 번호가 없는 경우만)"""
        category = NumberCategory.query.filter_by(
            id=category_id,
            company_id=company_id
        ).first()

        if not category:
            return False

        # 사용중인 번호 확인
        in_use_count = NumberRegistry.query.filter_by(
            category_id=category_id,
            status='in_use'
        ).count()

        if in_use_count > 0:
            return False

        db.session.delete(category)
        db.session.commit()
        return True

    def get_next_number(self, category_id: int, company_code: str,
                        separator: str = '-', digits: int = 6) -> Dict:
        """다음 번호 생성 및 예약"""
        category = NumberCategory.query.get(category_id)
        if not category:
            return None

        # 다음 시퀀스 가져오기 (동시성 고려하여 락 사용)
        category.current_sequence += 1
        seq = category.current_sequence
        db.session.flush()

        # 전체 번호 생성
        seq_str = str(seq).zfill(digits)
        full_number = f"{company_code}{separator}{category.code}{separator}{seq_str}"

        # 레지스트리에 등록
        registry = NumberRegistry(
            company_id=category.company_id,
            category_id=category_id,
            full_number=full_number,
            sequence=seq,
            status=NumberRegistry.STATUS_AVAILABLE
        )
        db.session.add(registry)
        db.session.commit()

        return {
            'categoryId': category_id,
            'sequence': seq,
            'fullNumber': full_number,
            'registryId': registry.id
        }

    def preview_next_number(self, category_id: int, company_code: str,
                            separator: str = '-', digits: int = 6) -> str:
        """다음 번호 미리보기 (시퀀스 증가 없음)"""
        category = NumberCategory.query.get(category_id)
        if not category:
            return None

        next_seq = category.current_sequence + 1
        seq_str = str(next_seq).zfill(digits)
        return f"{company_code}{separator}{category.code}{separator}{seq_str}"

    def initialize_default_asset_categories(self, company_id: int) -> List[Dict]:
        """기본 자산 분류코드 초기화"""
        results = []
        for code, name, description in NumberCategory.DEFAULT_ASSET_CATEGORIES:
            result = self.create_category(
                company_id=company_id,
                type_code=NumberCategory.TYPE_ASSET,
                code=code,
                name=name,
                description=description
            )
            results.append(result)
        return results
