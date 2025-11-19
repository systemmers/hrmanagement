"""
샘플 데이터 생성 스크립트
프로필 이미지가 포함된 25명 직원 데이터 생성
"""
import sys
import os
from datetime import date

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Employee, Department, Position


def seed_employees():
    """샘플 직원 데이터 생성"""
    app = create_app('development')

    with app.app_context():
        # 부서 및 직급 조회
        dept_dev = Department.query.filter_by(name='개발팀').first()
        dept_design = Department.query.filter_by(name='디자인팀').first()
        dept_marketing = Department.query.filter_by(name='마케팅팀').first()
        dept_sales = Department.query.filter_by(name='영업팀').first()
        dept_admin = Department.query.filter_by(name='관리팀').first()

        pos_staff = Position.query.filter_by(name='사원').first()
        pos_assistant = Position.query.filter_by(name='대리').first()
        pos_manager = Position.query.filter_by(name='과장').first()
        pos_deputy = Position.query.filter_by(name='차장').first()
        pos_general = Position.query.filter_by(name='부장').first()

        # 샘플 직원 데이터 (프로필 이미지 포함)
        employees = [
            # 남성 직원 11명
            {'name': '김철수', 'photo': 'employees/profile_01_m.png', 'department': dept_dev, 'position': pos_manager, 'status': 'active', 'hire_date': date(2020, 3, 15), 'phone': '010-1234-5678', 'email': 'chulsoo.kim@company.com', 'address': '서울특별시 강남구 테헤란로 123'},
            {'name': '박민수', 'photo': 'employees/profile_02_m.png', 'department': dept_dev, 'position': pos_staff, 'status': 'warning', 'hire_date': date(2022, 1, 10), 'phone': '010-3456-7890', 'email': 'minsu.park@company.com', 'address': '서울특별시 서초구 서초대로 456'},
            {'name': '최동욱', 'photo': 'employees/profile_03_m.png', 'department': dept_sales, 'position': pos_general, 'status': 'active', 'hire_date': date(2018, 3, 25), 'phone': '010-5678-9012', 'email': 'dongwook.choi@company.com', 'address': '서울특별시 송파구 올림픽로 789'},
            {'name': '강태양', 'photo': 'employees/profile_04_m.png', 'department': dept_design, 'position': pos_manager, 'status': 'warning', 'hire_date': date(2020, 11, 30), 'phone': '010-7890-1234', 'email': 'taeyang.kang@company.com', 'address': '서울특별시 마포구 월드컵북로 234'},
            {'name': '송민호', 'photo': 'employees/profile_05_m.png', 'department': dept_dev, 'position': pos_assistant, 'status': 'expired', 'hire_date': date(2021, 9, 5), 'phone': '010-9012-3456', 'email': 'minho.song@company.com', 'address': '서울특별시 용산구 한강대로 567'},
            {'name': '오준석', 'photo': 'employees/profile_06_m.png', 'department': dept_dev, 'position': pos_staff, 'status': 'active', 'hire_date': date(2023, 6, 1), 'phone': '010-1234-5670', 'email': 'junseok.oh@company.com', 'address': '서울특별시 성동구 왕십리로 890'},
            {'name': '신동혁', 'photo': 'employees/profile_07_m.png', 'department': dept_sales, 'position': pos_assistant, 'status': 'active', 'hire_date': date(2021, 3, 8), 'phone': '010-3456-7012', 'email': 'donghyuk.shin@company.com', 'address': '서울특별시 강동구 천호대로 123'},
            {'name': '권지훈', 'photo': 'employees/profile_08_m.png', 'department': dept_dev, 'position': pos_manager, 'status': 'active', 'hire_date': date(2020, 7, 12), 'phone': '010-5670-1234', 'email': 'jihoon.kwon@company.com', 'address': '서울특별시 광진구 광나루로 456'},
            {'name': '황재민', 'photo': 'employees/profile_09_m.png', 'department': dept_sales, 'position': pos_staff, 'status': 'active', 'hire_date': date(2022, 8, 27), 'phone': '010-7012-3456', 'email': 'jaemin.hwang@company.com', 'address': '서울특별시 동대문구 천호대로 789'},
            {'name': '홍성우', 'photo': 'employees/profile_10_m.png', 'department': dept_dev, 'position': pos_staff, 'status': 'active', 'hire_date': date(2023, 3, 9), 'phone': '010-1230-4567', 'email': 'sungwoo.hong@company.com', 'address': '서울특별시 종로구 종로 234'},
            {'name': '문준혁', 'photo': 'employees/profile_11_m.png', 'department': dept_design, 'position': pos_staff, 'status': 'active', 'hire_date': date(2022, 6, 13), 'phone': '010-3450-6789', 'email': 'junhyuk.moon@company.com', 'address': '서울특별시 중구 을지로 567'},

            # 여성 직원 14명
            {'name': '이영희', 'photo': 'employees/profile_12_f.png', 'department': dept_design, 'position': pos_assistant, 'status': 'active', 'hire_date': date(2021, 5, 20), 'phone': '010-2345-6789', 'email': 'younghee.lee@company.com', 'address': '서울특별시 영등포구 여의대로 890'},
            {'name': '정수진', 'photo': 'employees/profile_13_f.png', 'department': dept_marketing, 'position': pos_deputy, 'status': 'active', 'hire_date': date(2019, 8, 12), 'phone': '010-4567-8901', 'email': 'sujin.jung@company.com', 'address': '서울특별시 강서구 공항대로 123'},
            {'name': '한지민', 'photo': 'employees/profile_14_f.png', 'department': dept_dev, 'position': pos_staff, 'status': 'active', 'hire_date': date(2023, 2, 14), 'phone': '010-6789-0123', 'email': 'jimin.han@company.com', 'address': '서울특별시 구로구 디지털로 456'},
            {'name': '임현정', 'photo': 'employees/profile_15_f.png', 'department': dept_marketing, 'position': pos_staff, 'status': 'active', 'hire_date': date(2022, 7, 18), 'phone': '010-8901-2345', 'email': 'hyunjung.lim@company.com', 'address': '서울특별시 금천구 가산디지털1로 789'},
            {'name': '윤서연', 'photo': 'employees/profile_16_f.png', 'department': dept_admin, 'position': pos_deputy, 'status': 'active', 'hire_date': date(2019, 4, 22), 'phone': '010-0123-4567', 'email': 'seoyeon.yoon@company.com', 'address': '서울특별시 양천구 목동서로 234'},
            {'name': '배수지', 'photo': 'employees/profile_17_f.png', 'department': dept_design, 'position': pos_staff, 'status': 'warning', 'hire_date': date(2022, 10, 15), 'phone': '010-2345-6701', 'email': 'suji.bae@company.com', 'address': '서울특별시 강북구 도봉로 567'},
            {'name': '류혜진', 'photo': 'employees/profile_18_f.png', 'department': dept_marketing, 'position': pos_staff, 'status': 'active', 'hire_date': date(2023, 1, 20), 'phone': '010-4567-0123', 'email': 'hyejin.ryu@company.com', 'address': '서울특별시 도봉구 노해로 890'},
            {'name': '안소희', 'photo': 'employees/profile_19_f.png', 'department': dept_design, 'position': pos_assistant, 'status': 'warning', 'hire_date': date(2021, 12, 3), 'phone': '010-6701-2345', 'email': 'sohee.ahn@company.com', 'address': '서울특별시 노원구 동일로 123'},
            {'name': '서은채', 'photo': 'employees/profile_20_f.png', 'department': dept_marketing, 'position': pos_assistant, 'status': 'expired', 'hire_date': date(2021, 5, 16), 'phone': '010-0123-4567', 'email': 'eunchae.seo@company.com', 'address': '서울특별시 은평구 은평로 456'},
            {'name': '조미래', 'photo': 'employees/profile_21_f.png', 'department': dept_admin, 'position': pos_assistant, 'status': 'active', 'hire_date': date(2021, 11, 24), 'phone': '010-2340-5678', 'email': 'mirae.cho@company.com', 'address': '서울특별시 서대문구 신촌로 789'},
            {'name': '장서윤', 'photo': 'employees/profile_22_f.png', 'department': dept_sales, 'position': pos_manager, 'status': 'warning', 'hire_date': date(2020, 9, 18), 'phone': '010-4560-7890', 'email': 'seoyoon.jang@company.com', 'address': '서울특별시 마포구 마포대로 234'},
            {'name': '구민지', 'photo': 'employees/profile_23_f.png', 'department': dept_dev, 'position': pos_assistant, 'status': 'active', 'hire_date': date(2021, 7, 28), 'phone': '010-6780-9012', 'email': 'minji.gu@company.com', 'address': '서울특별시 중랑구 망우로 567'},
            {'name': '표지은', 'photo': 'employees/profile_24_f.png', 'department': dept_admin, 'position': pos_staff, 'status': 'active', 'hire_date': date(2022, 12, 11), 'phone': '010-7890-0123', 'email': 'jieun.pyo@company.com', 'address': '서울특별시 성북구 동소문로 890'},
            {'name': '노은영', 'photo': 'employees/profile_25_f.png', 'department': dept_marketing, 'position': pos_staff, 'status': 'active', 'hire_date': date(2023, 4, 5), 'phone': '010-5670-8901', 'email': 'eunyoung.noh@company.com', 'address': '서울특별시 동작구 상도로 123'}
        ]

        # 직원 데이터 추가
        for emp_data in employees:
            employee = Employee(
                name=emp_data['name'],
                photo=emp_data['photo'],
                department_id=emp_data['department'].id if emp_data['department'] else None,
                position_id=emp_data['position'].id if emp_data['position'] else None,
                status=emp_data['status'],
                hire_date=emp_data['hire_date'],
                phone=emp_data['phone'],
                email=emp_data['email'],
                address=emp_data['address'],
                employment_type='정규직',
                workplace='본사'
            )
            db.session.add(employee)

        db.session.commit()
        print(f'\n샘플 직원 데이터 생성 완료: {len(employees)}명')
        print('-' * 50)
        print('부서별 인원:')
        print(f'  개발팀: {sum(1 for e in employees if e["department"] == dept_dev)}명')
        print(f'  디자인팀: {sum(1 for e in employees if e["department"] == dept_design)}명')
        print(f'  마케팅팀: {sum(1 for e in employees if e["department"] == dept_marketing)}명')
        print(f'  영업팀: {sum(1 for e in employees if e["department"] == dept_sales)}명')
        print(f'  관리팀: {sum(1 for e in employees if e["department"] == dept_admin)}명')
        print('-' * 50)


if __name__ == '__main__':
    seed_employees()
