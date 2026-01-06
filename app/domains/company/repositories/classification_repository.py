"""
Classification Options Repository

부서, 직급, 재직상태 등의 분류 옵션을 관리합니다.
법인별 커스텀 옵션을 지원합니다.

Phase 7: 도메인 중심 마이그레이션 완료
Updated: 2026-01-05 - ConflictError 중복 체크 추가
"""
from typing import List, Dict, Optional
from app.database import db
from app.models import ClassificationOption
from app.shared.utils.exceptions import ConflictError
from app.repositories.base_repository import BaseRepository


class ClassificationOptionsRepository(BaseRepository[ClassificationOption]):
    """분류 옵션 저장소"""

    def __init__(self):
        super().__init__(ClassificationOption)

    def get_departments(self, company_id: int = None) -> List[Dict]:
        """부서 목록 조회"""
        return self._get_by_category('department', company_id)

    def get_positions(self, company_id: int = None) -> List[Dict]:
        """직급 목록 조회"""
        return self._get_by_category('position', company_id)

    def get_ranks(self, company_id: int = None) -> List[Dict]:
        """직위 목록 조회"""
        return self._get_by_category('rank', company_id)

    def get_statuses(self, company_id: int = None) -> List[Dict]:
        """재직상태 목록 조회"""
        return self._get_by_category('status', company_id)

    def get_job_titles(self, company_id: int = None) -> List[Dict]:
        """직책 목록 조회"""
        return self._get_by_category('job_title', company_id)

    def get_teams(self, company_id: int = None) -> List[Dict]:
        """팀 목록 조회"""
        return self._get_by_category('team', company_id)

    def get_work_locations(self, company_id: int = None) -> List[Dict]:
        """근무지 목록 조회"""
        return self._get_by_category('work_location', company_id)

    def get_banks(self, company_id: int = None) -> List[Dict]:
        """은행 목록 조회 (공통 + 법인별)"""
        return self._get_by_category('bank', company_id, include_system=True)

    def get_employment_types(self, company_id: int = None) -> List[Dict]:
        """고용형태 목록 조회"""
        return self._get_by_category('employment_type', company_id, include_system=True)

    def get_pay_types(self, company_id: int = None) -> List[Dict]:
        """급여방식 목록 조회"""
        return self._get_by_category('pay_type', company_id, include_system=True)

    def get_all_options(self, company_id: int = None) -> Dict[str, List[Dict]]:
        """모든 분류 옵션 조회"""
        return {
            'departments': self.get_departments(company_id),
            'positions': self.get_positions(company_id),
            'ranks': self.get_ranks(company_id),
            'job_titles': self.get_job_titles(company_id),
            'teams': self.get_teams(company_id),
            'work_locations': self.get_work_locations(company_id),
            'statuses': self.get_statuses(company_id),
            'banks': self.get_banks(company_id),
            'employment_types': self.get_employment_types(company_id),
            'pay_types': self.get_pay_types(company_id),
        }

    def get_organization_options(self, company_id: int = None) -> Dict[str, List[Dict]]:
        """조직 구조 탭용 옵션 조회"""
        return {
            'department': self._get_by_category('department', company_id),
            'position': self._get_by_category('position', company_id),
            'rank': self._get_by_category('rank', company_id),
            'job_title': self._get_by_category('job_title', company_id),
            'team': self._get_by_category('team', company_id),
            'work_location': self._get_by_category('work_location', company_id),
            'job_role': self._get_by_category('job_role', company_id),
            'job_grade': self._get_by_category('job_grade', company_id),
            'org_unit': self._get_by_category('org_unit', company_id),
        }

    def get_employment_options(self, company_id: int = None) -> Dict[str, List[Dict]]:
        """고용 정책 탭용 옵션 조회"""
        return {
            'employment_type': self._get_by_category('employment_type', company_id, include_system=True),
            'status': self._get_by_category('status', company_id),
            'pay_type': self._get_by_category('pay_type', company_id, include_system=True),
            'contract_type': self._get_by_category('contract_type', company_id),
            'bank': self._get_by_category('bank', company_id, include_system=True),
            'language': self._get_by_category('language', company_id),
            'language_level': self._get_by_category('language_level', company_id),
            'family_relation': self._get_by_category('family_relation', company_id),
        }

    def get_by_category_for_company(self, category: str, company_id: int) -> List[Dict]:
        """카테고리별 법인 옵션 조회 (전체 정보 포함)"""
        query = ClassificationOption.query.filter(
            ClassificationOption.category == category,
            ClassificationOption.is_active == True,
            db.or_(
                ClassificationOption.company_id == company_id,
                ClassificationOption.company_id.is_(None)
            )
        ).order_by(ClassificationOption.sort_order)

        return [opt.to_dict() for opt in query.all()]

    def add_option_for_company(self, company_id: int, category: str, value: str,
                               label: str = None, sort_order: int = None) -> Dict:
        """법인용 옵션 추가"""
        # 중복 확인 (글로벌 옵션 + 해당 법인 옵션 모두 체크)
        existing = ClassificationOption.query.filter(
            ClassificationOption.category == category,
            ClassificationOption.value == value,
            db.or_(
                ClassificationOption.company_id == company_id,
                ClassificationOption.company_id.is_(None)
            )
        ).first()

        if existing:
            raise ConflictError("이미 존재하는 항목입니다", field="value")

        # 정렬 순서 계산
        if sort_order is None:
            max_order = db.session.query(
                db.func.max(ClassificationOption.sort_order)
            ).filter(
                ClassificationOption.category == category,
                db.or_(
                    ClassificationOption.company_id == company_id,
                    ClassificationOption.company_id.is_(None)
                )
            ).scalar() or 0
            sort_order = max_order + 1

        option = ClassificationOption(
            company_id=company_id,
            category=category,
            value=value,
            label=label or value,
            sort_order=sort_order,
            is_system=False,
            is_active=True
        )

        db.session.add(option)
        db.session.commit()
        return option.to_dict()

    def update_option(self, option_id: int, company_id: int, data: Dict) -> Optional[Dict]:
        """옵션 수정"""
        option = ClassificationOption.query.filter_by(
            id=option_id,
            company_id=company_id
        ).first()

        if not option:
            return None

        # 시스템 옵션은 수정 불가
        if option.is_system:
            return None

        # value 변경 시 중복 체크 (글로벌 옵션 + 해당 법인 옵션 모두 체크)
        new_value = data.get('value')
        if new_value and new_value != option.value:
            existing = ClassificationOption.query.filter(
                ClassificationOption.category == option.category,
                ClassificationOption.value == new_value,
                ClassificationOption.id != option_id,
                db.or_(
                    ClassificationOption.company_id == company_id,
                    ClassificationOption.company_id.is_(None)
                )
            ).first()

            if existing:
                raise ConflictError("이미 존재하는 항목입니다", field="value")

            option.value = new_value

        if 'label' in data:
            option.label = data['label']
        if 'sortOrder' in data:
            option.sort_order = data['sortOrder']
        if 'isActive' in data:
            option.is_active = data['isActive']

        db.session.commit()
        return option.to_dict()

    def delete_option_for_company(self, option_id: int, company_id: int) -> bool:
        """법인 옵션 삭제"""
        option = ClassificationOption.query.filter_by(id=option_id).first()

        if not option:
            return False

        # 글로벌 옵션(company_id=None) 또는 해당 법인 옵션만 삭제 가능
        if option.company_id is not None and option.company_id != company_id:
            return False

        db.session.delete(option)
        db.session.commit()
        return True

    def toggle_system_option(self, company_id: int, category: str, value: str,
                             is_active: bool) -> Optional[Dict]:
        """시스템 옵션 활성화/비활성화 토글 (법인별)"""
        # 기존 비활성화 레코드 찾기
        toggle_record = ClassificationOption.query.filter_by(
            company_id=company_id,
            category=category,
            value=value,
            is_system=False
        ).first()

        if toggle_record:
            toggle_record.is_active = is_active
            db.session.commit()
            return toggle_record.to_dict()

        if not is_active:
            # 비활성화 레코드 생성
            toggle_record = ClassificationOption(
                company_id=company_id,
                category=category,
                value=value,
                label=value,
                is_system=False,
                is_active=False
            )
            db.session.add(toggle_record)
            db.session.commit()
            return toggle_record.to_dict()

        return None

    # Legacy methods (backward compatibility)
    def add_department(self, value: str, label: str = None) -> Dict:
        """부서 추가 (글로벌)"""
        return self._add_option('department', value, label)

    def add_position(self, value: str, label: str = None) -> Dict:
        """직급 추가 (글로벌)"""
        return self._add_option('position', value, label)

    def add_status(self, value: str, label: str = None) -> Dict:
        """재직상태 추가 (글로벌)"""
        return self._add_option('status', value, label)

    def add_job_title(self, value: str, label: str = None) -> Dict:
        """직책 추가 (글로벌)"""
        return self._add_option('job_title', value, label)

    def remove_department(self, value: str) -> bool:
        """부서 삭제 (글로벌)"""
        return self._remove_option('department', value)

    def remove_position(self, value: str) -> bool:
        """직급 삭제 (글로벌)"""
        return self._remove_option('position', value)

    def remove_status(self, value: str) -> bool:
        """재직상태 삭제 (글로벌)"""
        return self._remove_option('status', value)

    def remove_job_title(self, value: str) -> bool:
        """직책 삭제 (글로벌)"""
        return self._remove_option('job_title', value)

    def update_sort_order(self, category: str, value: str, sort_order: int) -> bool:
        """정렬 순서 수정 (글로벌)"""
        option = ClassificationOption.query.filter_by(
            category=category,
            value=value,
            company_id=None
        ).first()

        if option:
            option.sort_order = sort_order
            db.session.commit()
            return True
        return False

    def _get_by_category(self, category: str, company_id: int = None,
                         include_system: bool = False) -> List[Dict]:
        """카테고리별 옵션 조회 (글로벌 + 법인별 모두 포함)"""
        # 글로벌 옵션 (company_id=None) + 해당 법인 옵션 조회
        query = ClassificationOption.query.filter(
            ClassificationOption.category == category,
            ClassificationOption.is_active == True
        )

        if company_id:
            # 글로벌 옵션 또는 해당 법인 옵션
            query = query.filter(
                db.or_(
                    ClassificationOption.company_id.is_(None),
                    ClassificationOption.company_id == company_id
                )
            )
        else:
            # 글로벌 옵션만
            query = query.filter(ClassificationOption.company_id.is_(None))

        options = query.order_by(ClassificationOption.sort_order).all()

        return [
            {
                'value': opt.value,
                'label': opt.label or opt.value,
                'id': opt.id,
                'isSystem': opt.is_system,
                'companyId': opt.company_id
            }
            for opt in options
        ]

    def _add_option(self, category: str, value: str, label: str = None) -> Dict:
        """옵션 추가 (글로벌)"""
        existing = ClassificationOption.query.filter_by(
            category=category,
            value=value,
            company_id=None
        ).first()

        if existing:
            return existing.to_dict()

        max_order = db.session.query(
            db.func.max(ClassificationOption.sort_order)
        ).filter_by(category=category, company_id=None).scalar() or 0

        option = ClassificationOption(
            category=category,
            value=value,
            label=label or value,
            sort_order=max_order + 1,
            is_system=True,
            is_active=True
        )

        db.session.add(option)
        db.session.commit()
        return option.to_dict()

    def _remove_option(self, category: str, value: str) -> bool:
        """옵션 삭제 (글로벌)"""
        option = ClassificationOption.query.filter_by(
            category=category,
            value=value,
            company_id=None
        ).first()

        if option:
            db.session.delete(option)
            db.session.commit()
            return True
        return False


# 싱글톤 인스턴스
classification_repository = ClassificationOptionsRepository()
