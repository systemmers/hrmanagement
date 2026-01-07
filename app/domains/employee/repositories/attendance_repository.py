"""
Attendance Repository

근태 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.database import db
from app.domains.employee.models import Attendance
from app.shared.repositories.base_repository import BaseRelationRepository


class AttendanceRepository(BaseRelationRepository[Attendance]):
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

    def get_summary_by_employee(self, employee_id: int, year: int) -> Dict:
        """특정 직원의 연간 근태 요약 (snake_case)"""
        records = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.year == year
        ).all()

        if not records:
            return {
                'year': year,
                'total_work_days': 0,
                'total_absent_days': 0,
                'total_late_count': 0,
                'total_early_leave_count': 0,
                'total_annual_leave_used': 0
            }

        return {
            'year': year,
            'total_work_days': sum(r.work_days or 0 for r in records),
            'total_absent_days': sum(r.absent_days or 0 for r in records),
            'total_late_count': sum(r.late_count or 0 for r in records),
            'total_early_leave_count': sum(r.early_leave_count or 0 for r in records),
            'total_annual_leave_used': sum(r.annual_leave_used or 0 for r in records)
        }

    def get_by_employee_and_year(self, employee_id: int, year: int) -> List[Dict]:
        """특정 직원의 연간 월별 근태 조회"""
        records = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.year == year
        ).order_by(Attendance.month).all()

        return [record.to_dict() for record in records]
