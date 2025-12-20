"""
Base Repository 클래스

SQLAlchemy 기반 공통 CRUD 기능을 제공합니다.
Phase 6: 백엔드 리팩토링 - 중복 로직 통합
Phase 8: 제네릭 타입 적용 - IDE 자동완성 및 타입 안전성 강화
"""
from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from app.database import db

# 제네릭 타입 변수 정의
ModelType = TypeVar('ModelType', bound=db.Model)


class BaseRepository(Generic[ModelType]):
    """
    기본 Repository 클래스 (제네릭 타입 지원)

    사용법:
        class EducationRepository(BaseRepository[Education]):
            def __init__(self):
                super().__init__(Education)

        # IDE에서 get_model() 반환 타입이 Education으로 추론됨
    """

    def __init__(self, model_class: Type[ModelType]):
        """
        Args:
            model_class: SQLAlchemy 모델 클래스
        """
        self.model_class = model_class

    def get_all(self) -> List[Dict]:
        """모든 레코드 조회"""
        records = self.model_class.query.all()
        return [record.to_dict() for record in records]

    def get_all_models(self) -> List[ModelType]:
        """모든 레코드를 모델 객체로 조회"""
        return self.model_class.query.all()

    def get_by_id(self, record_id: Any) -> Optional[Dict]:
        """ID로 레코드 조회 (Dict 반환)"""
        record = self.model_class.query.get(record_id)
        return record.to_dict() if record else None

    def get_model_by_id(self, record_id: Any) -> Optional[ModelType]:
        """ID로 모델 객체 조회"""
        return self.model_class.query.get(record_id)

    def create(self, data: Dict) -> Dict:
        """새 레코드 생성 (Dict에서)"""
        record = self.model_class.from_dict(data)
        db.session.add(record)
        db.session.commit()
        return record.to_dict()

    def create_model(self, model: ModelType) -> ModelType:
        """모델 객체 직접 저장"""
        db.session.add(model)
        db.session.commit()
        return model

    def update(self, record_id: Any, data: Dict) -> Optional[Dict]:
        """레코드 수정"""
        record = self.model_class.query.get(record_id)
        if not record:
            return None

        self._update_record_fields(record, data)
        db.session.commit()
        return record.to_dict()

    def delete(self, record_id: Any) -> bool:
        """레코드 삭제"""
        record = self.model_class.query.get(record_id)
        if not record:
            return False

        db.session.delete(record)
        db.session.commit()
        return True

    def delete_model(self, model: ModelType) -> bool:
        """모델 객체 직접 삭제"""
        db.session.delete(model)
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

    def get_by_employee_id(self, employee_id: int) -> List[Dict]:
        """특정 직원의 모든 레코드 조회"""
        records = self.model_class.query.filter_by(employee_id=employee_id).all()
        return [record.to_dict() for record in records]

    def get_models_by_employee_id(self, employee_id: int) -> List[ModelType]:
        """특정 직원의 모든 레코드를 모델 객체로 조회"""
        return self.model_class.query.filter_by(employee_id=employee_id).all()

    def delete_by_employee_id(self, employee_id: int) -> int:
        """특정 직원의 모든 레코드 삭제"""
        count = self.model_class.query.filter_by(employee_id=employee_id).delete()
        db.session.commit()
        return count

    def create_for_employee(self, employee_id: int, data: Dict) -> Dict:
        """특정 직원에게 레코드 추가"""
        data['employeeId'] = employee_id
        return self.create(data)


class BaseProfileRelationRepository(BaseRepository[ModelType]):
    """
    Profile 관계형 데이터 Repository 기본 클래스

    Profile과 1:N 관계를 가진 모델용 Repository입니다.

    사용법:
        class ProfileEducationRepository(BaseProfileRelationRepository[Education]):
            def __init__(self):
                super().__init__(Education)
    """

    def get_by_profile_id(self, profile_id: int) -> List[Dict]:
        """특정 프로필의 모든 레코드 조회"""
        records = self.model_class.query.filter_by(profile_id=profile_id).all()
        return [record.to_dict() for record in records]

    def get_models_by_profile_id(self, profile_id: int) -> List[ModelType]:
        """특정 프로필의 모든 레코드를 모델 객체로 조회"""
        return self.model_class.query.filter_by(profile_id=profile_id).all()

    def create_for_profile(self, profile_id: int, data: Dict) -> ModelType:
        """특정 프로필에 레코드 추가 (from_dict 없이 직접 생성)"""
        record = self.model_class(profile_id=profile_id, **data)
        db.session.add(record)
        db.session.commit()
        return record

    def delete_by_id_and_profile(self, record_id: int, profile_id: int) -> bool:
        """레코드 삭제 (소유권 확인)"""
        record = self.model_class.query.filter_by(
            id=record_id, profile_id=profile_id
        ).first()
        if not record:
            return False
        db.session.delete(record)
        db.session.commit()
        return True

    def delete_all_by_profile(self, profile_id: int) -> int:
        """프로필의 모든 레코드 삭제"""
        count = self.model_class.query.filter_by(profile_id=profile_id).delete()
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

    def get_by_profile_id(self, profile_id: int) -> Optional[ModelType]:
        """특정 프로필의 레코드 조회 (1:1)"""
        return self.model_class.query.filter_by(profile_id=profile_id).first()

    def save_for_profile(self, profile_id: int, data: Dict) -> ModelType:
        """특정 프로필의 레코드 저장 (upsert)"""
        record = self.get_by_profile_id(profile_id)

        if record:
            # 기존 레코드 업데이트
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.session.commit()
            return record
        else:
            # 새 레코드 생성
            record = self.model_class(profile_id=profile_id, **data)
            db.session.add(record)
            db.session.commit()
            return record

    def delete_by_profile_id(self, profile_id: int) -> bool:
        """특정 프로필의 레코드 삭제"""
        record = self.get_by_profile_id(profile_id)
        if record:
            db.session.delete(record)
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

    def get_by_employee_id(self, employee_id: int) -> Optional[Dict]:
        """특정 직원의 레코드 조회 (1:1) - Dict 반환"""
        record = self.model_class.query.filter_by(employee_id=employee_id).first()
        return record.to_dict() if record else None

    def get_model_by_employee_id(self, employee_id: int) -> Optional[ModelType]:
        """특정 직원의 레코드 조회 (1:1) - 모델 객체 반환"""
        return self.model_class.query.filter_by(employee_id=employee_id).first()

    def save_for_employee(self, employee_id: int, data: Dict) -> Dict:
        """특정 직원의 레코드 저장 (upsert)"""
        record = self.model_class.query.filter_by(employee_id=employee_id).first()

        if record:
            # 기존 레코드 업데이트 (_update_record_fields 재사용)
            self._update_record_fields(record, data)
            db.session.commit()
            return record.to_dict()
        else:
            # 새 레코드 생성
            data['employeeId'] = employee_id
            return self.create(data)

    def delete_by_employee_id(self, employee_id: int) -> bool:
        """특정 직원의 레코드 삭제"""
        record = self.model_class.query.filter_by(employee_id=employee_id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False
