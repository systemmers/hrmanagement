"""기존 샘플 데이터 삭제 스크립트"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.employee import Employee
from app.models.education import Education
from app.models.career import Career
from app.models.certificate import Certificate
from app.models.family_member import FamilyMember
from app.models.language import Language
from app.models.military_service import MilitaryService
from app.models.salary import Salary
from app.models.contract import Contract
from app.models.benefit import Benefit
from app.models.insurance import Insurance
from app.models.promotion import Promotion
from app.models.evaluation import Evaluation
from app.models.training import Training
from app.models.project import Project
from app.models.award import Award
from app.models.asset import Asset
from app.models.attendance import Attendance

def main():
    app = create_app()
    with app.app_context():
        print("기존 샘플 데이터 삭제 중...")

        # 관련 테이블 먼저 삭제 (외래 키 제약)
        Attendance.query.delete()
        Asset.query.delete()
        Award.query.delete()
        Project.query.delete()
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
