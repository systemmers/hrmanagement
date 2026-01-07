"""
SalaryPayment Repository

급여 지급 이력 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.database import db
from app.domains.employee.models import SalaryPayment
from app.shared.repositories.base_repository import BaseRelationRepository


class SalaryPaymentRepository(BaseRelationRepository[SalaryPayment]):
    """급여 지급 이력 저장소"""

    def __init__(self):
        super().__init__(SalaryPayment)

    def get_by_period(self, payment_period: str) -> List[Dict]:
        """특정 지급 기간의 모든 급여 조회"""
        records = SalaryPayment.query.filter_by(payment_period=payment_period).all()
        return [record.to_dict() for record in records]

    def get_by_employee_and_period_range(
        self,
        employee_id: str,
        start_period: str,
        end_period: str
    ) -> List[Dict]:
        """특정 직원의 기간별 급여 지급 이력 조회"""
        records = SalaryPayment.query.filter(
            SalaryPayment.employee_id == employee_id,
            SalaryPayment.payment_period >= start_period,
            SalaryPayment.payment_period <= end_period
        ).order_by(SalaryPayment.payment_period).all()

        return [record.to_dict() for record in records]

    def get_total_by_period(self, payment_period: str) -> Dict:
        """특정 기간의 총 급여 합계"""
        result = db.session.query(
            db.func.sum(SalaryPayment.base_salary),
            db.func.sum(SalaryPayment.total_allowances),
            db.func.sum(SalaryPayment.total_deductions),
            db.func.sum(SalaryPayment.net_salary),
            db.func.count(SalaryPayment.id)
        ).filter_by(payment_period=payment_period).first()

        return {
            'baseSalaryTotal': result[0] or 0,
            'totalAllowancesSum': result[1] or 0,
            'totalDeductionsSum': result[2] or 0,
            'netSalaryTotal': result[3] or 0,
            'employeeCount': result[4] or 0
        }
