"""
Attendance Repository

근태 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.database import db
from app.models import Attendance
from .base_repository import BaseRelationRepository


class AttendanceRepository(BaseRelationRepository):
    """근태 저장소"""

    def __init__(self):
        super().__init__(Attendance)

    def get_by_date(self, date: str) -> List[Dict]:
        """특정 날짜의 모든 근태 조회"""
        records = Attendance.query.filter_by(date=date).all()
        return [record.to_dict() for record in records]

    def get_by_employee_and_date_range(
        self,
        employee_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """특정 직원의 기간별 근태 조회"""
        records = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date).all()

        return [record.to_dict() for record in records]
