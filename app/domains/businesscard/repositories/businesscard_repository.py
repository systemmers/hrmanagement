"""
BusinessCard Repository

명함 첨부파일 데이터의 CRUD 기능을 제공합니다.
Attachment 모델을 재사용하며, category 기반으로 명함 데이터를 필터링합니다.
"""
from typing import Dict, Optional, List
from app.domains.attachment.models import Attachment
from app.shared.repositories.base_repository import BaseRepository
from app.database import db


class BusinessCardRepository(BaseRepository[Attachment]):
    """명함 첨부파일 저장소"""

    # 명함 카테고리 상수
    CATEGORY_FRONT = 'business_card_front'
    CATEGORY_BACK = 'business_card_back'
    VALID_SIDES = ['front', 'back']

    def __init__(self):
        super().__init__(Attachment)

    def _get_category(self, side: str) -> str:
        """side를 category로 변환"""
        return f'business_card_{side}'

    def get_by_employee(self, employee_id: int) -> Dict[str, Optional[Dict]]:
        """
        직원의 명함 이미지 조회 (앞면/뒷면)

        Returns:
            {'front': {...} or None, 'back': {...} or None}
        """
        result = {'front': None, 'back': None}

        for side in self.VALID_SIDES:
            category = self._get_category(side)
            record = Attachment.query.filter_by(
                employee_id=employee_id,
                category=category
            ).order_by(Attachment.upload_date.desc()).first()

            if record:
                result[side] = record.to_dict()

        return result

    def get_one_by_side(self, employee_id: int, side: str) -> Optional[Dict]:
        """
        직원의 특정 면 명함 이미지 조회

        Args:
            employee_id: 직원 ID
            side: 'front' 또는 'back'

        Returns:
            명함 데이터 dict 또는 None
        """
        if side not in self.VALID_SIDES:
            return None

        category = self._get_category(side)
        record = Attachment.query.filter_by(
            employee_id=employee_id,
            category=category
        ).order_by(Attachment.upload_date.desc()).first()

        return record.to_dict() if record else None

    def create_business_card(self, data: Dict) -> Attachment:
        """
        명함 첨부파일 생성

        Args:
            data: {
                'employee_id': int,
                'file_name': str,
                'file_path': str,
                'file_type': str,
                'file_size': int,
                'side': str ('front' or 'back'),
                'upload_date': str (optional)
            }
        """
        side = data.pop('side', 'front')
        category = self._get_category(side)

        attachment = Attachment.from_dict({
            'employeeId': data.get('employee_id'),
            'fileName': data.get('file_name'),
            'filePath': data.get('file_path'),
            'fileType': data.get('file_type'),
            'fileSize': data.get('file_size'),
            'category': category,
            'uploadDate': data.get('upload_date')
        })

        db.session.add(attachment)
        db.session.commit()
        return attachment

    def delete_by_side(self, employee_id: int, side: str, commit: bool = True) -> bool:
        """
        직원의 특정 면 명함 이미지 삭제

        Args:
            employee_id: 직원 ID
            side: 'front' 또는 'back'
            commit: 커밋 여부

        Returns:
            삭제 성공 여부
        """
        if side not in self.VALID_SIDES:
            return False

        category = self._get_category(side)
        records = Attachment.query.filter_by(
            employee_id=employee_id,
            category=category
        ).all()

        for record in records:
            db.session.delete(record)

        if commit:
            db.session.commit()

        return len(records) > 0

    def delete_all_by_employee(self, employee_id: int, commit: bool = True) -> int:
        """
        직원의 모든 명함 이미지 삭제

        Returns:
            삭제된 레코드 수
        """
        count = 0
        for side in self.VALID_SIDES:
            if self.delete_by_side(employee_id, side, commit=False):
                count += 1

        if commit:
            db.session.commit()

        return count
