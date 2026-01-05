"""
Base Repository 클래스

SQLAlchemy 기반 공통 CRUD 기능을 제공합니다.
Phase 6: 백엔드 리팩토링 - 중복 로직 통합
Phase 8: 제네릭 타입 적용 - IDE 자동완성 및 타입 안전성 강화
Phase 24: Option A 레이어 분리 - find_by_id(), find_all() 표준화 (Model 반환)
Phase 26: 레거시 메서드 완전 제거 (get_by_id, get_all 등)
Phase 27: 트랜잭션 안전성 - commit 파라미터 추가 (단일 트랜잭션 지원)
"""
from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from app.database import db

# 제네릭 타입 변수 정의
ModelType = TypeVar('ModelType', bound=db.Model)


class BaseRepository(Generic[ModelType]):
    """
    기본 Repository 클래스 (제네릭 타입 지원)

    Phase 24 Option A 표준:
    - Repository: Model 반환 (find_by_id, find_all)
    - Service: Dict 반환 (to_dict 호출)

    사용법:
        class EducationRepository(BaseRepository[Education]):
            def __init__(self):
                super().__init__(Education)
    """

    def __init__(self, model_class: Type[ModelType]):
        """
        Args:
            model_class: SQLAlchemy 모델 클래스
        """
        self.model_class = model_class

    def find_all(self) -> List[ModelType]:
        """
        모든 레코드 조회 (Model 반환)

        Returns:
            모델 객체 리스트
        """
        return self.model_class.query.all()

    def find_by_id(self, record_id: Any) -> Optional[ModelType]:
        """
        ID로 모델 객체 조회 (신규 표준 메서드)

        Phase 24 Option A: Repository는 Model만 반환
        Service에서 to_dict() 호출하여 Dict 변환

        Args:
            record_id: 조회할 레코드 ID

        Returns:
            모델 객체 또는 None
        """
        return self.model_class.query.get(record_id)

    def find_by_ids(self, record_ids: List[Any]) -> List[ModelType]:
        """
        여러 ID로 모델 객체 목록 조회 (벌크)

        Args:
            record_ids: 조회할 레코드 ID 목록

        Returns:
            모델 객체 리스트
        """
        if not record_ids:
            return []
        return self.model_class.query.filter(
            self.model_class.id.in_(record_ids)
        ).all()

    def create(self, data: Dict, commit: bool = True) -> Dict:
        """새 레코드 생성 (Dict에서)

        Args:
            data: 생성할 데이터 딕셔너리
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class.from_dict(data)
        db.session.add(record)
        if commit:
            db.session.commit()
        return record.to_dict()

    def create_model(self, model: ModelType, commit: bool = True) -> ModelType:
        """모델 객체 직접 저장

        Args:
            model: 저장할 모델 인스턴스
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        db.session.add(model)
        if commit:
            db.session.commit()
        return model

    def update(self, record_id: Any, data: Dict, commit: bool = True) -> Optional[Dict]:
        """레코드 수정

        Args:
            record_id: 수정할 레코드 ID
            data: 수정할 데이터 딕셔너리
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class.query.get(record_id)
        if not record:
            return None

        self._update_record_fields(record, data)
        if commit:
            db.session.commit()
        return record.to_dict()

    def delete(self, record_id: Any, commit: bool = True) -> bool:
        """레코드 삭제

        Args:
            record_id: 삭제할 레코드 ID
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class.query.get(record_id)
        if not record:
            return False

        db.session.delete(record)
        if commit:
            db.session.commit()
        return True

    def delete_model(self, model: ModelType, commit: bool = True) -> bool:
        """모델 객체 직접 삭제

        Args:
            model: 삭제할 모델 인스턴스
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        db.session.delete(model)
        if commit:
            db.session.commit()
        return True

    def _update_record_fields(self, record: ModelType, data: Dict) -> None:
        """
        레코드 필드 업데이트 (공통 로직)

        camelCase 키를 snake_case로 변환하여 레코드에 적용합니다.

        Args:
            record: SQLAlchemy 모델 인스턴스
            data: 업데이트할 데이터 딕셔너리
        """
        for key, value in data.items():
            snake_key = self._camel_to_snake(key)
            if hasattr(record, snake_key):
                setattr(record, snake_key, value)

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """camelCase를 snake_case로 변환"""
        result = []
        for char in name:
            if char.isupper():
                result.append('_')
                result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result).lstrip('_')


class BaseRelationRepository(BaseRepository[ModelType]):
    """
    관계형 데이터 Repository 기본 클래스

    Employee와 1:N 관계를 가진 모델용 Repository입니다.

    사용법:
        class EducationRepository(BaseRelationRepository[Education]):
            def __init__(self):
                super().__init__(Education)
    """

    def find_by_employee_id(self, employee_id: int) -> List[ModelType]:
        """
        특정 직원의 모든 레코드 조회 (신규 표준 메서드)

        Phase 24 Option A: Repository는 Model만 반환
        Service에서 to_dict() 호출하여 Dict 변환

        Args:
            employee_id: 직원 ID

        Returns:
            모델 객체 리스트
        """
        return self.model_class.query.filter_by(employee_id=employee_id).all()

    def delete_by_employee_id(self, employee_id: int, commit: bool = True) -> int:
        """특정 직원의 모든 레코드 삭제

        Args:
            employee_id: 직원 ID
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        count = self.model_class.query.filter_by(employee_id=employee_id).delete()
        if commit:
            db.session.commit()
        return count

    def create_for_employee(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """특정 직원에게 레코드 추가

        Args:
            employee_id: 직원 ID
            data: 생성할 데이터 딕셔너리
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        data['employeeId'] = employee_id
        return self.create(data, commit=commit)


class BaseProfileRelationRepository(BaseRepository[ModelType]):
    """
    Profile 관계형 데이터 Repository 기본 클래스

    Profile과 1:N 관계를 가진 모델용 Repository입니다.

    사용법:
        class ProfileEducationRepository(BaseProfileRelationRepository[Education]):
            def __init__(self):
                super().__init__(Education)
    """

    def find_by_profile_id(self, profile_id: int) -> List[ModelType]:
        """
        특정 프로필의 모든 레코드 조회 (신규 표준 메서드)

        Phase 24 Option A: Repository는 Model만 반환
        Service에서 to_dict() 호출하여 Dict 변환

        Args:
            profile_id: 프로필 ID

        Returns:
            모델 객체 리스트
        """
        return self.model_class.query.filter_by(profile_id=profile_id).all()

    def create_for_profile(self, profile_id: int, data: Dict, commit: bool = True) -> ModelType:
        """특정 프로필에 레코드 추가 (from_dict 없이 직접 생성)

        Args:
            profile_id: 프로필 ID
            data: 생성할 데이터 딕셔너리
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class(profile_id=profile_id, **data)
        db.session.add(record)
        if commit:
            db.session.commit()
        return record

    def delete_by_id_and_profile(self, record_id: int, profile_id: int, commit: bool = True) -> bool:
        """레코드 삭제 (소유권 확인)

        Args:
            record_id: 레코드 ID
            profile_id: 프로필 ID
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class.query.filter_by(
            id=record_id, profile_id=profile_id
        ).first()
        if not record:
            return False
        db.session.delete(record)
        if commit:
            db.session.commit()
        return True

    def delete_all_by_profile(self, profile_id: int, commit: bool = True) -> int:
        """프로필의 모든 레코드 삭제

        Args:
            profile_id: 프로필 ID
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        count = self.model_class.query.filter_by(profile_id=profile_id).delete()
        if commit:
            db.session.commit()
        return count


class BaseProfileOneToOneRepository(BaseRepository[ModelType]):
    """
    Profile 1:1 관계 데이터 Repository 기본 클래스

    Profile과 1:1 관계를 가진 모델용 Repository입니다.

    사용법:
        class ProfileMilitaryRepository(BaseProfileOneToOneRepository[MilitaryService]):
            def __init__(self):
                super().__init__(MilitaryService)
    """

    def find_by_profile_id(self, profile_id: int) -> Optional[ModelType]:
        """
        특정 프로필의 레코드 조회 (신규 표준 메서드, 1:1 관계)

        Phase 24 Option A: Repository는 Model만 반환
        Service에서 to_dict() 호출하여 Dict 변환

        Args:
            profile_id: 프로필 ID

        Returns:
            모델 객체 또는 None
        """
        return self.model_class.query.filter_by(profile_id=profile_id).first()

    def save_for_profile(self, profile_id: int, data: Dict, commit: bool = True) -> ModelType:
        """특정 프로필의 레코드 저장 (upsert)

        Args:
            profile_id: 프로필 ID
            data: 저장할 데이터 딕셔너리
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.find_by_profile_id(profile_id)

        if record:
            # 기존 레코드 업데이트
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            if commit:
                db.session.commit()
            return record
        else:
            # 새 레코드 생성
            record = self.model_class(profile_id=profile_id, **data)
            db.session.add(record)
            if commit:
                db.session.commit()
            return record

    def delete_by_profile_id(self, profile_id: int, commit: bool = True) -> bool:
        """특정 프로필의 레코드 삭제

        Args:
            profile_id: 프로필 ID
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.find_by_profile_id(profile_id)
        if record:
            db.session.delete(record)
            if commit:
                db.session.commit()
            return True
        return False


class BaseOneToOneRepository(BaseRepository[ModelType]):
    """
    1:1 관계 데이터 Repository 기본 클래스

    Employee와 1:1 관계를 가진 모델용 Repository입니다.

    사용법:
        class MilitaryRepository(BaseOneToOneRepository[MilitaryService]):
            def __init__(self):
                super().__init__(MilitaryService)
    """

    def find_by_employee_id(self, employee_id: int) -> Optional[ModelType]:
        """
        특정 직원의 레코드 조회 (신규 표준 메서드, 1:1 관계)

        Phase 24 Option A: Repository는 Model만 반환
        Service에서 to_dict() 호출하여 Dict 변환

        Args:
            employee_id: 직원 ID

        Returns:
            모델 객체 또는 None
        """
        return self.model_class.query.filter_by(employee_id=employee_id).first()

    def save_for_employee(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """특정 직원의 레코드 저장 (upsert)

        Args:
            employee_id: 직원 ID
            data: 저장할 데이터 딕셔너리
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class.query.filter_by(employee_id=employee_id).first()

        if record:
            # 기존 레코드 업데이트 (_update_record_fields 재사용)
            self._update_record_fields(record, data)
            if commit:
                db.session.commit()
            return record.to_dict()
        else:
            # 새 레코드 생성
            data['employeeId'] = employee_id
            return self.create(data, commit=commit)

    def delete_by_employee_id(self, employee_id: int, commit: bool = True) -> bool:
        """특정 직원의 레코드 삭제

        Args:
            employee_id: 직원 ID
            commit: True면 즉시 커밋, False면 트랜잭션 유지
        """
        record = self.model_class.query.filter_by(employee_id=employee_id).first()
        if record:
            db.session.delete(record)
            if commit:
                db.session.commit()
            return True
        return False
