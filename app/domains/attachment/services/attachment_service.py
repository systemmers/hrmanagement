"""
첨부파일 서비스

첨부파일 관리 비즈니스 로직을 제공합니다.
Phase 31: 독립 도메인으로 분리 + owner_type/owner_id 범용화
Phase 32: blueprints 추가 및 서비스 확장 (create, update_order, get_by_id, delete)
"""
from typing import List, Dict, Optional

from app.database import db


class AttachmentService:
    """
    첨부파일 서비스 (범용)

    첨부파일 CRUD 및 조회 기능을 제공합니다.
    """

    @property
    def attachment_repo(self):
        """지연 초기화된 첨부파일 Repository"""
        from app.domains.attachment import get_attachment_repo
        return get_attachment_repo()

    # ===== 범용 메서드 (owner_type + owner_id) =====

    def get_by_owner(self, owner_type: str, owner_id: int) -> List[Dict]:
        """
        소유자별 첨부파일 목록 조회

        Args:
            owner_type: 소유자 타입 (employee, profile, company)
            owner_id: 소유자 ID

        Returns:
            첨부파일 목록
        """
        models = self.attachment_repo.get_by_owner(owner_type, owner_id)
        return [m.to_dict() for m in models]

    def get_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str
    ) -> List[Dict]:
        """
        소유자 및 카테고리별 첨부파일 조회

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 카테고리명

        Returns:
            해당 카테고리의 첨부파일 목록
        """
        models = self.attachment_repo.get_by_owner_and_category(
            owner_type, owner_id, category
        )
        return [m.to_dict() for m in models]

    def get_one_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str
    ) -> Optional[Dict]:
        """
        소유자 및 카테고리별 첨부파일 1개 조회

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 카테고리명

        Returns:
            첨부파일 또는 None
        """
        model = self.attachment_repo.get_one_by_owner_and_category(
            owner_type, owner_id, category
        )
        return model.to_dict() if model else None

    def delete_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str, commit: bool = True
    ) -> int:
        """
        소유자 및 카테고리별 첨부파일 삭제

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 카테고리명
            commit: DB 커밋 여부

        Returns:
            삭제된 첨부파일 개수
        """
        return self.attachment_repo.delete_by_owner_and_category(
            owner_type, owner_id, category, commit
        )

    def delete_by_owner(self, owner_type: str, owner_id: int, commit: bool = True) -> int:
        """
        소유자의 모든 첨부파일 삭제

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            commit: DB 커밋 여부

        Returns:
            삭제된 첨부파일 개수
        """
        return self.attachment_repo.delete_by_owner(owner_type, owner_id, commit)

    # ===== CRUD 메서드 =====

    def get_by_id(self, attachment_id: int) -> Optional[Dict]:
        """
        첨부파일 ID로 조회

        Args:
            attachment_id: 첨부파일 ID

        Returns:
            첨부파일 정보 또는 None
        """
        model = self.attachment_repo.find_by_id(attachment_id)
        return model.to_dict() if model else None

    def create(self, data: Dict, commit: bool = True) -> Dict:
        """
        첨부파일 생성

        Args:
            data: 첨부파일 데이터
            commit: DB 커밋 여부

        Returns:
            생성된 첨부파일 정보
        """
        from app.domains.attachment.models import Attachment

        attachment = Attachment(
            owner_type=data.get('owner_type'),
            owner_id=data.get('owner_id'),
            file_name=data.get('file_name'),
            file_path=data.get('file_path'),
            file_type=data.get('file_type'),
            file_size=data.get('file_size', 0),
            category=data.get('category'),
            upload_date=data.get('upload_date'),
            note=data.get('note'),
            display_order=data.get('display_order', 0),
            # Phase 4.2: 항목별 증빙 서류 연동
            linked_entity_type=data.get('linked_entity_type'),
            linked_entity_id=data.get('linked_entity_id'),
            # 레거시 호환
            employee_id=data.get('employee_id')
        )

        db.session.add(attachment)
        if commit:
            db.session.commit()

        return attachment.to_dict()

    def delete(self, attachment_id: int, commit: bool = True) -> bool:
        """
        첨부파일 삭제

        Args:
            attachment_id: 첨부파일 ID
            commit: DB 커밋 여부

        Returns:
            삭제 성공 여부
        """
        return self.attachment_repo.delete(attachment_id, commit)

    def update_order(
        self, owner_type: str, owner_id: int, order: List[int], commit: bool = True
    ) -> None:
        """
        첨부파일 순서 변경

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            order: 첨부파일 ID 순서 배열
            commit: DB 커밋 여부
        """
        from app.domains.attachment.models import Attachment

        for index, attachment_id in enumerate(order):
            attachment = Attachment.query.get(attachment_id)
            if attachment and attachment.owner_type == owner_type and attachment.owner_id == owner_id:
                attachment.display_order = index

        if commit:
            db.session.commit()

    # ===== 항목별 증빙 서류 연동 메서드 (Phase 4.2) =====

    def get_by_linked_entity(
        self, owner_type: str, owner_id: int,
        linked_entity_type: str, linked_entity_id: int
    ) -> List[Dict]:
        """
        연결된 엔티티별 첨부파일 조회

        Args:
            owner_type: 소유자 타입 (employee, profile)
            owner_id: 소유자 ID
            linked_entity_type: 연결 엔티티 타입 (education, career, certificate)
            linked_entity_id: 연결 엔티티 ID

        Returns:
            해당 엔티티에 연결된 첨부파일 목록
        """
        from app.domains.attachment.models import Attachment

        models = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            linked_entity_type=linked_entity_type,
            linked_entity_id=linked_entity_id
        ).order_by(Attachment.display_order.asc()).all()

        return [m.to_dict() for m in models]

    def get_all_by_linked_entity_type(
        self, owner_type: str, owner_id: int, linked_entity_type: str
    ) -> List[Dict]:
        """
        연결 엔티티 타입별 모든 첨부파일 조회

        Args:
            owner_type: 소유자 타입 (employee, profile)
            owner_id: 소유자 ID
            linked_entity_type: 연결 엔티티 타입 (education, career, certificate)

        Returns:
            해당 타입의 모든 첨부파일 목록
        """
        from app.domains.attachment.models import Attachment

        models = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            linked_entity_type=linked_entity_type
        ).order_by(Attachment.linked_entity_id, Attachment.display_order.asc()).all()

        return [m.to_dict() for m in models]

    def delete_by_linked_entity(
        self, owner_type: str, owner_id: int,
        linked_entity_type: str, linked_entity_id: int,
        commit: bool = True
    ) -> int:
        """
        연결된 엔티티의 모든 첨부파일 삭제

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            linked_entity_type: 연결 엔티티 타입
            linked_entity_id: 연결 엔티티 ID
            commit: DB 커밋 여부

        Returns:
            삭제된 첨부파일 개수
        """
        from app.domains.attachment.models import Attachment

        result = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            linked_entity_type=linked_entity_type,
            linked_entity_id=linked_entity_id
        ).delete()

        if commit:
            db.session.commit()

        return result

    def link_attachment_to_entity(
        self, attachment_id: int,
        linked_entity_type: str, linked_entity_id: int,
        commit: bool = True
    ) -> Optional[Dict]:
        """
        기존 첨부파일을 엔티티에 연결

        Args:
            attachment_id: 첨부파일 ID
            linked_entity_type: 연결할 엔티티 타입
            linked_entity_id: 연결할 엔티티 ID
            commit: DB 커밋 여부

        Returns:
            수정된 첨부파일 정보 또는 None
        """
        from app.domains.attachment.models import Attachment

        attachment = Attachment.query.get(attachment_id)
        if not attachment:
            return None

        attachment.linked_entity_type = linked_entity_type
        attachment.linked_entity_id = linked_entity_id

        if commit:
            db.session.commit()

        return attachment.to_dict()

    def unlink_attachment_from_entity(
        self, attachment_id: int, commit: bool = True
    ) -> Optional[Dict]:
        """
        첨부파일의 엔티티 연결 해제

        Args:
            attachment_id: 첨부파일 ID
            commit: DB 커밋 여부

        Returns:
            수정된 첨부파일 정보 또는 None
        """
        from app.domains.attachment.models import Attachment

        attachment = Attachment.query.get(attachment_id)
        if not attachment:
            return None

        attachment.linked_entity_type = None
        attachment.linked_entity_id = None

        if commit:
            db.session.commit()

        return attachment.to_dict()

    def get_evidence_status(
        self, owner_type: str, owner_id: int, linked_entity_type: str
    ) -> Dict:
        """
        특정 엔티티 타입의 증빙 서류 현황 조회

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            linked_entity_type: 연결 엔티티 타입

        Returns:
            {
                'entity_ids_with_evidence': [1, 3, 5],  # 증빙 파일이 있는 엔티티 ID 목록
                'total_evidence_count': 8  # 총 증빙 파일 수
            }
        """
        from app.domains.attachment.models import Attachment
        from sqlalchemy import func

        attachments = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            linked_entity_type=linked_entity_type
        ).all()

        entity_ids = set(a.linked_entity_id for a in attachments if a.linked_entity_id)

        return {
            'entity_ids_with_evidence': list(entity_ids),
            'total_evidence_count': len(attachments)
        }

    # ===== 레거시 호환 메서드 (employee_id) =====

    def get_by_employee_id(self, employee_id: int) -> List[Dict]:
        """
        직원 ID로 첨부파일 목록 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID

        Returns:
            첨부파일 목록
        """
        return self.get_by_owner('employee', employee_id)

    def get_by_category(self, employee_id: int, category: str) -> List[Dict]:
        """
        카테고리별 첨부파일 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            해당 카테고리의 첨부파일 목록
        """
        return self.attachment_repo.get_by_category(employee_id, category)

    def get_one_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        """
        카테고리별 첨부파일 1개 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            첨부파일 또는 None
        """
        return self.attachment_repo.get_one_by_category(employee_id, category)

    def get_by_file_type(self, employee_id: int, file_type: str) -> List[Dict]:
        """
        파일 타입별 첨부파일 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID
            file_type: 파일 타입

        Returns:
            해당 타입의 첨부파일 목록
        """
        return self.attachment_repo.get_by_file_type(employee_id, file_type)

    def delete_by_category(self, employee_id: int, category: str, commit: bool = True) -> bool:
        """
        카테고리별 첨부파일 삭제 (레거시 호환)

        Args:
            employee_id: 직원 ID
            category: 카테고리명
            commit: DB 커밋 여부

        Returns:
            삭제 성공 여부
        """
        return self.attachment_repo.delete_by_category(employee_id, category, commit)


# 싱글톤 인스턴스
attachment_service = AttachmentService()
