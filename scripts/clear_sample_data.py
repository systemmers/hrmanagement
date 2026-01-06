"""기존 샘플 데이터 삭제 스크립트"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.domains.employee.models import Employee
from app.domains.employee.models import Education
from app.domains.employee.models import Career
from app.domains.employee.models import Certificate
from app.domains.employee.models import FamilyMember
from app.domains.employee.models import Language
from app.domains.employee.models import MilitaryService
from app.domains.employee.models import Salary
from app.domains.employee.models import Contract
from app.domains.employee.models import Benefit
from app.domains.employee.models import Insurance
from app.domains.employee.models import Promotion
from app.domains.employee.models import Evaluation
from app.domains.employee.models import Training
from app.domains.employee.models import HrProject
from app.domains.employee.models import Award
from app.domains.employee.models import Asset
from app.domains.employee.models import Attendance

def main():
    app = create_app()
    with app.app_context():
        print("기존 샘플 데이터 삭제 중...")

        # 관련 테이블 먼저 삭제 (외래 키 제약)
        Attendance.query.delete()
        Asset.query.delete()
        Award.query.delete()
        HrProject.query.delete()
        Training.query.delete()
        Evaluation.query.delete()
        Promotion.query.delete()
        Insurance.query.delete()
        Benefit.query.delete()
        Contract.query.delete()
        Salary.query.delete()
        MilitaryService.query.delete()
        Language.query.delete()
        FamilyMember.query.delete()
        Certificate.query.delete()
        Career.query.delete()
        Education.query.delete()

        # 직원 삭제
        Employee.query.delete()

        db.session.commit()
        print("삭제 완료!")
        print(f"직원 수: {Employee.query.count()}")

if __name__ == '__main__':
    main()
