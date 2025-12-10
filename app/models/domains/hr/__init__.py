"""인사 도메인 모델"""
from app.models.salary import Salary
from app.models.salary_history import SalaryHistory
from app.models.salary_payment import SalaryPayment
from app.models.benefit import Benefit
from app.models.insurance import Insurance
from app.models.promotion import Promotion
from app.models.evaluation import Evaluation
from app.models.training import Training
from app.models.attendance import Attendance

__all__ = [
    'Salary',
    'SalaryHistory',
    'SalaryPayment',
    'Benefit',
    'Insurance',
    'Promotion',
    'Evaluation',
    'Training',
    'Attendance',
]
