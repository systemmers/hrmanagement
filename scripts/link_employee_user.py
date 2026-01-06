"""
employee_sub 계정과 Employee 레코드 연결 스크립트

대상: employee_id가 NULL인 employee_sub 계정
- emp_a1~a5 (Company ID: 1, org_id: 2)
- emp_b1~b3 (Company ID: 3, org_id: 4)

각 계정에 대해:
1. Employee 레코드 생성 (해당 회사의 organization_id로)
2. User.employee_id에 새 Employee ID 연결

실행 방법:
    python scripts/link_employee_user.py
    python scripts/link_employee_user.py --dry-run  # 미리보기
"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database import db
from app.models.user import User
from app.domains.employee.models import Employee
from app.models.company import Company
from app.domains.employee.models import Education
from app.domains.employee.models import Career
from app.domains.employee.models import FamilyMember
from app.domains.employee.models import Language
from app.domains.employee.models import MilitaryService
from app.domains.employee.models import Salary
from app.domains.employee.models import Contract
from app.domains.employee.models import Benefit
from app.domains.employee.models import Insurance


# ============================================
# 데이터 풀 정의 (balance_test_data.py와 공유)
# ============================================

MALE_SURNAMES = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
MALE_NAMES = ['철수', '영호', '민수', '준혁', '성민', '동현', '재호', '승우', '현준', '지훈']
FEMALE_SURNAMES = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
FEMALE_NAMES = ['영희', '수진', '미영', '지현', '소연', '유진', '서연', '민지', '하늘', '예은']

NAME_TO_ENGLISH = {
    '철수': 'Chul Soo', '영호': 'Young Ho', '민수': 'Min Soo',
    '준혁': 'Jun Hyuk', '성민': 'Sung Min', '동현': 'Dong Hyun',
    '재호': 'Jae Ho', '승우': 'Seung Woo', '현준': 'Hyun Jun', '지훈': 'Ji Hoon',
    '영희': 'Young Hee', '수진': 'Su Jin', '미영': 'Mi Young',
    '지현': 'Ji Hyun', '소연': 'So Yeon', '유진': 'Yu Jin',
    '서연': 'Seo Yeon', '민지': 'Min Ji', '하늘': 'Ha Neul', '예은': 'Ye Eun',
    '김': 'Kim', '이': 'Lee', '박': 'Park', '최': 'Choi', '정': 'Jung',
    '강': 'Kang', '조': 'Cho', '윤': 'Yoon', '장': 'Jang', '임': 'Lim'
}

DEPARTMENTS = ['경영지원팀', '개발팀', '인사팀', '영업팀', '마케팅팀']
POSITIONS = ['사원', '대리', '과장']
TEAMS = ['1팀', '2팀', '기획파트', '운영파트']
JOB_TITLES = ['담당', '팀원', 'PM']
WORK_LOCATIONS = ['본사', '분당지사', '판교지사']

HIGH_SCHOOLS = ['서울고등학교', '한양고등학교', '경기고등학교']
UNIVERSITIES = ['서울대학교', '연세대학교', '고려대학교', '한양대학교']
MAJORS = ['경영학', '컴퓨터공학', '경제학', '법학']

COMPANIES_LIST = ['삼성전자', 'LG전자', '네이버', '카카오']
JOB_DESCRIPTIONS = ['프로젝트 관리', '소프트웨어 개발', '마케팅 전략']

BLOOD_TYPES = ['A', 'B', 'O', 'AB']
RELIGIONS = ['무교', '기독교', '불교', '천주교']
HOBBIES = ['등산', '독서', '영화감상', '운동', '여행']
SPECIALTIES = ['프로그래밍', '외국어', '프레젠테이션', '데이터분석']

ADDRESSES = [
    ('서울특별시 강남구 테헤란로 123', '06234'),
    ('서울특별시 서초구 서초대로 456', '06611'),
    ('경기도 성남시 분당구 판교역로 333', '13494'),
]

BANKS = ['국민은행', '신한은행', '우리은행', '하나은행']

LANGUAGE_EXAMS = [
    ('영어', 'TOEIC', ['700', '750', '800', '850']),
    ('영어', 'TOEIC Speaking', ['Level 5', 'Level 6', 'Level 7']),
]

MILITARY_BRANCHES = ['육군', '해군', '공군']
MILITARY_RANKS = ['병장', '상병']


# ============================================
# 유틸리티 함수
# ============================================

def random_date(start_year, end_year):
    """랜덤 날짜 생성"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')


def random_phone():
    """랜덤 휴대폰 번호 생성"""
    return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"


def random_home_phone():
    """랜덤 집전화 번호 생성"""
    area = random.choice(['02', '031', '032'])
    return f"{area}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_bank_account(bank):
    """랜덤 계좌번호 생성"""
    return f"{bank} {random.randint(100, 999)}-{random.randint(100000, 999999)}-{random.randint(10, 99)}"


def get_next_employee_number():
    """다음 직원번호 반환"""
    max_emp = db.session.query(db.func.max(Employee.employee_number)).scalar()
    if max_emp:
        try:
            num = int(max_emp.split('-')[-1]) + 1
            return num
        except (ValueError, IndexError):
            pass
    return Employee.query.count() + 1001


# ============================================
# 직원 생성 함수
# ============================================

def create_employee_for_user(user, org_id, emp_number, dry_run=False):
    """사용자에 대한 Employee 레코드 생성"""

    # 이름 생성 (username 기반으로 유추 또는 랜덤)
    gender = random.choice(['M', 'F'])
    if gender == 'M':
        surname = random.choice(MALE_SURNAMES)
        given_name = random.choice(MALE_NAMES)
        photo = f'/static/images/face/face_{random.randint(1, 11):02d}_m.png'
    else:
        surname = random.choice(FEMALE_SURNAMES)
        given_name = random.choice(FEMALE_NAMES)
        photo = f'/static/images/face/face_{random.randint(12, 25):02d}_f.png'

    name = surname + given_name
    english_surname = NAME_TO_ENGLISH.get(surname, surname)
    english_given = NAME_TO_ENGLISH.get(given_name, given_name)
    english_name = f"{english_surname} {english_given}"

    birth_year = random.randint(1985, 1998)
    birth_date = random_date(birth_year, birth_year)
    hire_date = random_date(2020, 2024)

    department = random.choice(DEPARTMENTS)
    position = random.choice(POSITIONS)
    team = department.replace('팀', '') + random.choice(TEAMS)

    address, postal_code = random.choice(ADDRESSES)
    detailed_address = f"아파트 {random.randint(101, 120)}동 {random.randint(101, 1505)}호"

    birth_short = birth_date.replace('-', '')[2:]
    gender_digit = '1' if gender == 'M' else '2'
    resident_number = f"{birth_short}-{gender_digit}******"

    employee_number = f"EMP-2025-{emp_number:04d}"

    employee = Employee(
        employee_number=employee_number,
        name=name,
        photo=photo,
        department=department,
        position=position,
        status='active',
        hire_date=hire_date,
        phone=random_phone(),
        email=user.email,  # 사용자 이메일 사용
        organization_id=org_id,
        team=team,
        job_title=random.choice(JOB_TITLES),
        work_location=random.choice(WORK_LOCATIONS),
        internal_phone=str(random.randint(100, 999)),
        company_email=f"{user.username}@company.co.kr",
        english_name=english_name,
        birth_date=birth_date,
        lunar_birth=random.choice([True, False]),
        gender=gender,
        mobile_phone=random_phone(),
        home_phone=random_home_phone(),
        address=address,
        detailed_address=detailed_address,
        postal_code=postal_code,
        resident_number=resident_number,
        nationality='대한민국',
        blood_type=random.choice(BLOOD_TYPES),
        religion=random.choice(RELIGIONS),
        hobby=', '.join(random.sample(HOBBIES, 2)),
        specialty=', '.join(random.sample(SPECIALTIES, 2)),
    )

    if not dry_run:
        db.session.add(employee)
        db.session.flush()

        # 관련 데이터 생성
        create_employee_related_data(employee, dry_run)

    return employee


def create_employee_related_data(employee, dry_run=False):
    """직원 관련 데이터 생성"""
    if dry_run:
        return

    birth_year = int(employee.birth_date[:4])

    # 학력
    hs_admission = birth_year + 16
    hs_graduation = birth_year + 19
    db.session.add(Education(
        employee_id=employee.id,
        school_type='고등학교',
        school_name=random.choice(HIGH_SCHOOLS),
        major='인문계' if random.random() > 0.5 else '이공계',
        admission_date=f"{hs_admission}-03-01",
        graduation_date=f"{hs_graduation}-02-28",
        graduation_status='졸업',
        location='서울',
    ))

    db.session.add(Education(
        employee_id=employee.id,
        school_type='대학교',
        school_name=random.choice(UNIVERSITIES),
        major=random.choice(MAJORS),
        degree='학사',
        admission_date=f"{hs_graduation}-03-01",
        graduation_date=f"{hs_graduation + 4}-02-28",
        graduation_status='졸업',
        location='서울',
    ))

    # 경력
    hire_year = int(employee.hire_date[:4])
    end_year = hire_year - 1
    start_year = end_year - random.randint(1, 2)
    db.session.add(Career(
        employee_id=employee.id,
        company_name=random.choice(COMPANIES_LIST),
        department=random.choice(DEPARTMENTS),
        position='사원',
        job_description=random.choice(JOB_DESCRIPTIONS),
        start_date=f"{start_year}-{random.randint(1,12):02d}-01",
        end_date=f"{end_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        resignation_reason='이직',
        is_current=False,
    ))

    # 가족
    db.session.add(FamilyMember(
        employee_id=employee.id,
        relation='부',
        name=random.choice(MALE_SURNAMES) + random.choice(['진호', '성철']),
        birth_date=random_date(1955, 1965),
        occupation=random.choice(['회사원', '자영업']),
        contact=random_phone(),
        is_cohabitant=random.choice([True, False]),
        is_dependent=random.choice([True, False]),
    ))

    db.session.add(FamilyMember(
        employee_id=employee.id,
        relation='모',
        name=random.choice(FEMALE_SURNAMES) + random.choice(['정숙', '미자']),
        birth_date=random_date(1958, 1968),
        occupation=random.choice(['주부', '교사']),
        contact=random_phone(),
        is_cohabitant=random.choice([True, False]),
        is_dependent=random.choice([True, False]),
    ))

    # 어학
    lang_name, exam_name, scores = random.choice(LANGUAGE_EXAMS)
    db.session.add(Language(
        employee_id=employee.id,
        language_name=lang_name,
        exam_name=exam_name,
        score=random.choice(scores),
        acquisition_date=random_date(2021, 2024),
    ))

    # 병역 (남성만)
    if employee.gender == 'M' and random.random() < 0.9:
        enlist_year = random.randint(2012, 2018)
        db.session.add(MilitaryService(
            employee_id=employee.id,
            military_status='군필',
            service_type='현역',
            branch=random.choice(MILITARY_BRANCHES),
            rank=random.choice(MILITARY_RANKS),
            enlistment_date=f"{enlist_year}-{random.randint(1,12):02d}-01",
            discharge_date=f"{enlist_year + 2}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            discharge_reason='만기전역',
        ))

    # 급여
    base_by_position = {'사원': 3000000, '대리': 4000000, '과장': 5000000}
    base = base_by_position.get(employee.position, 3500000) + random.randint(-200000, 300000)
    position_allowance = random.randint(0, 300000)
    meal_allowance = 150000
    transportation = 150000
    bank = random.choice(BANKS)

    db.session.add(Salary(
        employee_id=employee.id,
        salary_type='월급',
        base_salary=base,
        position_allowance=position_allowance,
        meal_allowance=meal_allowance,
        transportation_allowance=transportation,
        total_salary=base + position_allowance + meal_allowance + transportation,
        payment_day=random.choice([10, 15, 25]),
        payment_method='계좌이체',
        bank_account=random_bank_account(bank),
    ))

    # 계약
    db.session.add(Contract(
        employee_id=employee.id,
        contract_date=employee.hire_date,
        contract_type='정규직',
        contract_period='무기한',
        employee_type='정규직',
        work_type='정규',
    ))

    # 복리후생
    hire_year = int(employee.hire_date[:4])
    years_worked = 2025 - hire_year
    granted = 15 + min(years_worked, 10)
    used = random.randint(0, min(granted // 2, 8))

    db.session.add(Benefit(
        employee_id=employee.id,
        year=2025,
        annual_leave_granted=granted,
        annual_leave_used=used,
        annual_leave_remaining=granted - used,
        severance_type=random.choice(['DC형', 'DB형']),
        severance_method='퇴직연금',
    ))

    # 보험
    db.session.add(Insurance(
        employee_id=employee.id,
        national_pension=True,
        health_insurance=True,
        employment_insurance=True,
        industrial_accident=True,
        national_pension_rate=4.5,
        health_insurance_rate=3.545,
        long_term_care_rate=0.9182,
        employment_insurance_rate=0.9,
    ))


# ============================================
# 메인 실행
# ============================================

def get_unlinked_employee_sub_accounts():
    """연결되지 않은 employee_sub 계정 조회"""
    return User.query.filter(
        User.account_type == User.ACCOUNT_EMPLOYEE_SUB,
        User.employee_id.is_(None),
        User.role == User.ROLE_EMPLOYEE
    ).all()


def show_current_status():
    """현재 상태 출력"""
    print("\n[현재 상태]")
    print("-" * 60)

    # employee_sub 계정 상태
    all_sub = User.query.filter_by(account_type=User.ACCOUNT_EMPLOYEE_SUB).all()
    linked = [u for u in all_sub if u.employee_id is not None]
    unlinked = [u for u in all_sub if u.employee_id is None]

    print(f"  employee_sub 계정 총: {len(all_sub)}개")
    print(f"    - Employee 연결됨: {len(linked)}개")
    print(f"    - Employee 미연결: {len(unlinked)}개")

    if unlinked:
        print("\n  [미연결 계정 목록]")
        for u in unlinked:
            company = u.get_company()
            company_name = company.name if company else "미연결"
            print(f"    - {u.username} (ID: {u.id}) | Company: {company_name}")


def main():
    """메인 실행 함수"""
    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("employee_sub 계정 - Employee 레코드 연결")
    if dry_run:
        print("[DRY RUN 모드 - 실제 데이터 생성하지 않음]")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        show_current_status()

        unlinked_users = get_unlinked_employee_sub_accounts()

        if not unlinked_users:
            print("\n[OK] 모든 employee_sub 계정이 이미 Employee와 연결되어 있습니다.")
            return

        print(f"\n{len(unlinked_users)}개 계정에 Employee 생성 및 연결 시작...")

        start_number = get_next_employee_number()
        emp_number = start_number
        linked_count = 0

        for user in unlinked_users:
            company = user.get_company()
            if not company:
                print(f"  [SKIP] {user.username}: Company 연결 없음")
                continue

            org_id = company.root_organization_id
            if not org_id:
                print(f"  [SKIP] {user.username}: Company {company.name}에 root_organization_id 없음")
                continue

            print(f"\n[{user.username}]")
            print(f"  Company: {company.name} (ID: {company.id})")
            print(f"  Organization ID: {org_id}")

            # Employee 생성
            employee = create_employee_for_user(user, org_id, emp_number, dry_run)
            print(f"  Employee 생성: {employee.name} ({employee.employee_number})")

            # User.employee_id 연결
            if not dry_run:
                user.employee_id = employee.id
                print(f"  User.employee_id = {employee.id} 연결 완료")

            emp_number += 1
            linked_count += 1

        if not dry_run:
            db.session.commit()
            print("\n[OK] 데이터베이스 커밋 완료!")

        # 결과 출력
        print("\n" + "=" * 60)
        print("연결 결과")
        print("=" * 60)
        print(f"  - 총 연결: {linked_count}개 계정")

        if not dry_run:
            show_current_status()


if __name__ == '__main__':
    main()
