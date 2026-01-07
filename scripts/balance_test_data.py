"""
법인별 테스트 직원 데이터 균형화 스크립트

생성 대상:
- (주)테스트기업 (Company ID: 2, org_id: 3): 5명
- 테스트기업 B (Company ID: 3, org_id: 4): 5명

실행 방법:
    python scripts/balance_test_data.py
    python scripts/balance_test_data.py --dry-run  # 미리보기
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
from app.domains.employee.models import Employee
from app.domains.company.models import Company
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


# ============================================
# 데이터 풀 정의 (generate_sample_employees.py 참조)
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
POSITIONS = ['사원', '대리', '과장', '차장', '부장']
TEAMS = ['1팀', '2팀', '기획파트', '운영파트', '전략파트']
JOB_TITLES = ['담당', '파트장', '팀원', 'PM', '리더']
WORK_LOCATIONS = ['본사', '분당지사', '판교지사', '강남지사']

HIGH_SCHOOLS = ['서울고등학교', '한양고등학교', '경기고등학교', '부산고등학교', '인천고등학교']
UNIVERSITIES = ['서울대학교', '연세대학교', '고려대학교', '한양대학교', '성균관대학교']
MAJORS = ['경영학', '컴퓨터공학', '경제학', '법학', '행정학', '전자공학']

COMPANIES_LIST = ['삼성전자', 'LG전자', 'SK하이닉스', '네이버', '카카오', '현대자동차']
JOB_DESCRIPTIONS = ['프로젝트 관리', '소프트웨어 개발', '마케팅 전략', '영업 관리', '재무 분석']

BLOOD_TYPES = ['A', 'B', 'O', 'AB']
RELIGIONS = ['무교', '기독교', '불교', '천주교']
HOBBIES = ['등산', '독서', '영화감상', '운동', '여행', '요리', '음악감상']
SPECIALTIES = ['프로그래밍', '외국어', '프레젠테이션', '데이터분석', '기획력']

ADDRESSES = [
    ('서울특별시 강남구 테헤란로 123', '06234'),
    ('서울특별시 서초구 서초대로 456', '06611'),
    ('서울특별시 송파구 올림픽로 789', '05551'),
    ('경기도 성남시 분당구 판교역로 333', '13494'),
    ('경기도 수원시 영통구 광교로 444', '16229'),
]

BANKS = ['국민은행', '신한은행', '우리은행', '하나은행', 'NH농협']

LANGUAGE_EXAMS = [
    ('영어', 'TOEIC', ['700', '750', '800', '850', '900']),
    ('영어', 'TOEIC Speaking', ['Level 5', 'Level 6', 'Level 7']),
    ('일본어', 'JLPT', ['N3', 'N2', 'N1']),
]

MILITARY_BRANCHES = ['육군', '해군', '공군', '해병대']
MILITARY_RANKS = ['병장', '상병', '일병']


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
    area = random.choice(['02', '031', '032', '051'])
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

def generate_employee(gender, index, org_id, emp_number):
    """직원 기본 정보 생성"""
    if gender == 'M':
        surname = MALE_SURNAMES[index % len(MALE_SURNAMES)]
        given_name = MALE_NAMES[index % len(MALE_NAMES)]
        photo = f'/static/images/face/face_{(index % 11) + 1:02d}_m.png'
    else:
        surname = FEMALE_SURNAMES[index % len(FEMALE_SURNAMES)]
        given_name = FEMALE_NAMES[index % len(FEMALE_NAMES)]
        photo = f'/static/images/face/face_{(index % 14) + 12:02d}_f.png'

    name = surname + given_name
    english_surname = NAME_TO_ENGLISH.get(surname, surname)
    english_given = NAME_TO_ENGLISH.get(given_name, given_name)
    english_name = f"{english_surname} {english_given}"

    birth_year = random.randint(1980, 1998)
    birth_date = random_date(birth_year, birth_year)
    hire_date = random_date(2018, 2024)

    department = random.choice(DEPARTMENTS)
    position = random.choice(POSITIONS)
    team = department.replace('팀', '') + random.choice(TEAMS)

    address, postal_code = random.choice(ADDRESSES)
    detailed_address = f"아파트 {random.randint(101, 120)}동 {random.randint(101, 2505)}호"

    birth_short = birth_date.replace('-', '')[2:]
    gender_digit = '1' if gender == 'M' else '2'
    if birth_year >= 2000:
        gender_digit = '3' if gender == 'M' else '4'
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
        email=f"{surname.lower()}{given_name.lower()}{random.randint(1,99)}@example.com",
        organization_id=org_id,
        team=team,
        job_title=random.choice(JOB_TITLES),
        work_location=random.choice(WORK_LOCATIONS),
        internal_phone=str(random.randint(100, 999)),
        company_email=f"{surname.lower()}{given_name.lower()}@company.co.kr",
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

    return employee


def generate_educations(employee_id, birth_year):
    """학력 정보 생성"""
    educations = []

    hs_admission = birth_year + 16
    hs_graduation = birth_year + 19
    educations.append(Education(
        employee_id=employee_id,
        school_type='고등학교',
        school_name=random.choice(HIGH_SCHOOLS),
        major='인문계' if random.random() > 0.5 else '이공계',
        admission_date=f"{hs_admission}-03-01",
        graduation_date=f"{hs_graduation}-02-28",
        graduation_status='졸업',
        location='서울',
    ))

    univ_graduation = hs_graduation + 4
    educations.append(Education(
        employee_id=employee_id,
        school_type='대학교',
        school_name=random.choice(UNIVERSITIES),
        major=random.choice(MAJORS),
        degree='학사',
        admission_date=f"{hs_graduation}-03-01",
        graduation_date=f"{univ_graduation}-02-28",
        graduation_status='졸업',
        location='서울',
    ))

    return educations


def generate_careers(employee_id, hire_date):
    """경력 정보 생성"""
    careers = []
    hire_year = int(hire_date[:4])
    end_year = hire_year - 1
    start_year = end_year - random.randint(1, 3)

    careers.append(Career(
        employee_id=employee_id,
        company_name=random.choice(COMPANIES_LIST),
        department=random.choice(DEPARTMENTS),
        position=random.choice(['사원', '대리']),
        job_description=random.choice(JOB_DESCRIPTIONS),
        start_date=f"{start_year}-{random.randint(1,12):02d}-01",
        end_date=f"{end_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        resignation_reason='이직',
        is_current=False,
    ))

    return careers


def generate_family_members(employee_id):
    """가족 정보 생성"""
    members = []

    members.append(FamilyMember(
        employee_id=employee_id,
        relation='부',
        name=random.choice(MALE_SURNAMES) + random.choice(['진호', '성철', '동수']),
        birth_date=random_date(1950, 1965),
        occupation=random.choice(['회사원', '자영업', '공무원']),
        contact=random_phone(),
        is_cohabitant=random.choice([True, False]),
        is_dependent=random.choice([True, False]),
    ))

    members.append(FamilyMember(
        employee_id=employee_id,
        relation='모',
        name=random.choice(FEMALE_SURNAMES) + random.choice(['정숙', '미자', '영희']),
        birth_date=random_date(1953, 1968),
        occupation=random.choice(['회사원', '주부', '교사']),
        contact=random_phone(),
        is_cohabitant=random.choice([True, False]),
        is_dependent=random.choice([True, False]),
    ))

    return members


def generate_languages(employee_id):
    """어학 정보 생성"""
    languages = []
    lang_name, exam_name, scores = random.choice(LANGUAGE_EXAMS)
    acq_year = random.randint(2020, 2024)

    languages.append(Language(
        employee_id=employee_id,
        language_name=lang_name,
        exam_name=exam_name,
        score=random.choice(scores),
        acquisition_date=random_date(acq_year, acq_year),
    ))

    return languages


def generate_military_service(employee_id, gender):
    """병역 정보 생성"""
    if gender != 'M':
        return None

    if random.random() < 0.9:
        enlist_year = random.randint(2010, 2018)
        return MilitaryService(
            employee_id=employee_id,
            military_status='군필',
            service_type='현역',
            branch=random.choice(MILITARY_BRANCHES),
            rank=random.choice(MILITARY_RANKS),
            enlistment_date=f"{enlist_year}-{random.randint(1,12):02d}-01",
            discharge_date=f"{enlist_year + 2}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            discharge_reason='만기전역',
        )
    else:
        return MilitaryService(
            employee_id=employee_id,
            military_status='면제',
            exemption_reason='신체등급',
        )


def generate_salary(employee_id, position):
    """급여 정보 생성"""
    base_by_position = {
        '사원': 3000000, '대리': 4000000, '과장': 5000000,
        '차장': 6000000, '부장': 7500000
    }
    base = base_by_position.get(position, 3500000)
    base += random.randint(-200000, 500000)

    position_allowance = random.randint(0, 500000)
    meal_allowance = random.choice([100000, 150000, 200000])
    transportation = random.choice([100000, 150000, 200000])
    total = base + position_allowance + meal_allowance + transportation

    bank = random.choice(BANKS)

    return Salary(
        employee_id=employee_id,
        salary_type='월급',
        base_salary=base,
        position_allowance=position_allowance,
        meal_allowance=meal_allowance,
        transportation_allowance=transportation,
        total_salary=total,
        payment_day=random.choice([10, 15, 25]),
        payment_method='계좌이체',
        bank_account=random_bank_account(bank),
    )


def generate_contract(employee_id, hire_date):
    """계약 정보 생성"""
    return Contract(
        employee_id=employee_id,
        contract_date=hire_date,
        contract_type='정규직',
        contract_period='무기한',
        employee_type='정규직',
        work_type='정규',
    )


def generate_benefit(employee_id, hire_date):
    """복리후생 정보 생성"""
    hire_year = int(hire_date[:4])
    years_worked = 2025 - hire_year
    granted = 15 + min(years_worked, 10)
    used = random.randint(0, min(granted // 2, 10))

    return Benefit(
        employee_id=employee_id,
        year=2025,
        annual_leave_granted=granted,
        annual_leave_used=used,
        annual_leave_remaining=granted - used,
        severance_type=random.choice(['DC형', 'DB형']),
        severance_method='퇴직연금',
    )


def generate_insurance(employee_id):
    """보험 정보 생성"""
    return Insurance(
        employee_id=employee_id,
        national_pension=True,
        health_insurance=True,
        employment_insurance=True,
        industrial_accident=True,
        national_pension_rate=4.5,
        health_insurance_rate=3.545,
        long_term_care_rate=0.9182,
        employment_insurance_rate=0.9,
    )


# ============================================
# 메인 실행
# ============================================

def create_employees_for_company(company, count, male_count, start_number, dry_run=False):
    """특정 회사에 직원 데이터 생성"""
    org_id = company.root_organization_id
    if not org_id:
        print(f"  [ERROR] {company.name}: root_organization_id 없음")
        return []

    print(f"\n[{company.name}] organization_id={org_id}에 {count}명 생성")

    employees_created = []
    emp_number = start_number

    # 남성 직원
    for i in range(male_count):
        emp = generate_employee('M', i, org_id, emp_number)
        if not dry_run:
            db.session.add(emp)
            db.session.flush()
        employees_created.append(emp)
        print(f"  + {emp.name} ({emp.employee_number}) - 남성")
        emp_number += 1

    # 여성 직원
    female_count = count - male_count
    for i in range(female_count):
        emp = generate_employee('F', i, org_id, emp_number)
        if not dry_run:
            db.session.add(emp)
            db.session.flush()
        employees_created.append(emp)
        print(f"  + {emp.name} ({emp.employee_number}) - 여성")
        emp_number += 1

    # 관련 데이터 생성
    if not dry_run:
        for emp in employees_created:
            birth_year = int(emp.birth_date[:4])

            for edu in generate_educations(emp.id, birth_year):
                db.session.add(edu)

            for career in generate_careers(emp.id, emp.hire_date):
                db.session.add(career)

            for family in generate_family_members(emp.id):
                db.session.add(family)

            for lang in generate_languages(emp.id):
                db.session.add(lang)

            military = generate_military_service(emp.id, emp.gender)
            if military:
                db.session.add(military)

            db.session.add(generate_salary(emp.id, emp.position))
            db.session.add(generate_contract(emp.id, emp.hire_date))
            db.session.add(generate_benefit(emp.id, emp.hire_date))
            db.session.add(generate_insurance(emp.id))

    return employees_created


def show_current_status():
    """현재 상태 출력"""
    print("\n[현재 상태]")
    print("-" * 50)

    companies = Company.query.all()
    for company in companies:
        if company.root_organization_id:
            emp_count = Employee.query.filter_by(
                organization_id=company.root_organization_id
            ).count()
        else:
            emp_count = 0
        print(f"  - {company.name} (ID: {company.id}, org: {company.root_organization_id}): {emp_count}명")


def main():
    """메인 실행 함수"""
    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("법인별 테스트 직원 데이터 균형화")
    if dry_run:
        print("[DRY RUN 모드 - 실제 데이터 생성하지 않음]")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        show_current_status()

        # 대상 회사 확인
        company_2 = Company.query.get(2)  # (주)테스트기업
        company_3 = Company.query.get(3)  # 테스트기업 B

        if not company_2:
            print("\n[ERROR] Company ID 2 ((주)테스트기업) 없음")
            return
        if not company_3:
            print("\n[ERROR] Company ID 3 (테스트기업 B) 없음")
            return

        start_number = get_next_employee_number()
        print(f"\n시작 직원번호: EMP-2025-{start_number:04d}")

        # (주)테스트기업: 5명 (남2, 여3)
        emp_list_2 = create_employees_for_company(
            company_2, count=5, male_count=2,
            start_number=start_number, dry_run=dry_run
        )

        # 테스트기업 B: 5명 (남3, 여2)
        emp_list_3 = create_employees_for_company(
            company_3, count=5, male_count=3,
            start_number=start_number + 5, dry_run=dry_run
        )

        if not dry_run:
            db.session.commit()
            print("\n[OK] 데이터베이스 커밋 완료!")

        # 결과 출력
        print("\n" + "=" * 60)
        print("생성 결과")
        print("=" * 60)
        print(f"  - (주)테스트기업: {len(emp_list_2)}명 생성")
        print(f"  - 테스트기업 B: {len(emp_list_3)}명 생성")

        if not dry_run:
            show_current_status()


if __name__ == '__main__':
    main()
