"""
랜덤 직원 10명 샘플 데이터 생성 스크립트

조건: 남성 5명, 여성 5명
모든 필드 정보 + 관련 이력 + 인사관리 정보 포함
"""
import sys
import os
import random
from datetime import datetime, timedelta

# 프로젝트 루트를 path에 추가
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
from app.models.hr_project import HrProject
from app.models.award import Award
from app.models.asset import Asset
from app.models.attendance import Attendance


# ============================================
# 데이터 풀 정의
# ============================================

# 이름 데이터
MALE_SURNAMES = ['김', '이', '박', '최', '정']
MALE_NAMES = ['철수', '영호', '민수', '준혁', '성민']
FEMALE_SURNAMES = ['김', '이', '박', '최', '정']
FEMALE_NAMES = ['영희', '수진', '미영', '지현', '소연']

# 영문 이름 변환
NAME_TO_ENGLISH = {
    '철수': 'Chul Soo', '영호': 'Young Ho', '민수': 'Min Soo',
    '준혁': 'Jun Hyuk', '성민': 'Sung Min',
    '영희': 'Young Hee', '수진': 'Su Jin', '미영': 'Mi Young',
    '지현': 'Ji Hyun', '소연': 'So Yeon',
    '김': 'Kim', '이': 'Lee', '박': 'Park', '최': 'Choi', '정': 'Jung'
}

# 한자 이름 변환
NAME_TO_CHINESE = {
    '철수': '哲秀', '영호': '英鎬', '민수': '民秀',
    '준혁': '俊赫', '성민': '成旻',
    '영희': '英姬', '수진': '秀珍', '미영': '美英',
    '지현': '智賢', '소연': '素妍',
    '김': '金', '이': '李', '박': '朴', '최': '崔', '정': '鄭'
}

# 부서/직급/팀
DEPARTMENTS = ['경영지원팀', '개발팀', '인사팀', '영업팀', '마케팅팀']
POSITIONS = ['사원', '대리', '과장', '차장', '부장']
TEAMS = ['1팀', '2팀', '기획파트', '운영파트', '전략파트']
JOB_TITLES = ['담당', '파트장', '팀원', 'PM', '리더']
WORK_LOCATIONS = ['본사', '분당지사', '판교지사', '강남지사']

# 학력 데이터
HIGH_SCHOOLS = ['서울고등학교', '한양고등학교', '경기고등학교', '부산고등학교', '인천고등학교']
UNIVERSITIES = ['서울대학교', '연세대학교', '고려대학교', '한양대학교', '성균관대학교', '중앙대학교']
MAJORS = ['경영학', '컴퓨터공학', '경제학', '법학', '행정학', '전자공학', '기계공학']

# 경력 데이터
COMPANIES = ['삼성전자', 'LG전자', 'SK하이닉스', '네이버', '카카오', '현대자동차', 'CJ그룹']
JOB_DESCRIPTIONS = ['프로젝트 관리', '소프트웨어 개발', '마케팅 전략 수립', '영업 관리', '재무 분석', '인사 관리']

# 자격증 데이터
CERTIFICATES = [
    ('정보처리기사', '한국산업인력공단'),
    ('SQLD', '한국데이터산업진흥원'),
    ('컴퓨터활용능력 1급', '대한상공회의소'),
    ('TOEIC Speaking', 'ETS'),
    ('PMP', 'PMI'),
    ('AWS Solutions Architect', 'Amazon'),
]

# 어학 데이터
LANGUAGE_EXAMS = [
    ('영어', 'TOEIC', ['700', '750', '800', '850', '900', '950']),
    ('영어', 'TOEIC Speaking', ['Level 5', 'Level 6', 'Level 7', 'Level 8']),
    ('일본어', 'JLPT', ['N3', 'N2', 'N1']),
    ('중국어', 'HSK', ['4급', '5급', '6급']),
]

# 가족관계
FAMILY_RELATIONS = ['배우자', '자녀', '부', '모']
OCCUPATIONS = ['회사원', '교사', '자영업', '공무원', '주부', '학생', '무직']

# 군 관련
MILITARY_BRANCHES = ['육군', '해군', '공군', '해병대']
MILITARY_RANKS = ['병장', '상병', '일병', '이병']
SERVICE_TYPES = ['현역', '보충역', '전환복무']

# 은행
BANKS = ['국민은행', '신한은행', '우리은행', '하나은행', 'NH농협']

# 교육
TRAINING_NAMES = [
    '신입사원 교육', '리더십 과정', '보안 교육', '직무능력 향상',
    'OJT 교육', '성희롱 예방 교육', '개인정보보호 교육'
]
TRAINING_INSTITUTIONS = ['사내', '한국생산성본부', '삼성멀티캠퍼스', '패스트캠퍼스']

# 프로젝트
PROJECT_NAMES = [
    'ERP 시스템 구축', '웹사이트 리뉴얼', '모바일 앱 개발',
    'CRM 시스템 도입', 'AI 챗봇 개발', '클라우드 마이그레이션'
]
PROJECT_ROLES = ['PM', 'PL', '개발자', '기획자', 'QA', '디자이너']

# 수상
AWARDS = ['우수사원상', '혁신상', '최우수팀상', '고객만족상', 'MVP']

# 자산
ASSET_ITEMS = [
    ('노트북', ['MacBook Pro 14', 'Dell XPS 15', 'LG gram 17', 'ThinkPad X1']),
    ('모니터', ['Dell U2722D', 'LG 27UK850', 'Samsung 32']),
    ('의자', ['허먼밀러 에어론', '시디즈 T80', '듀오백']),
    ('키보드', ['Apple Magic Keyboard', 'Logitech MX Keys']),
]

# 혈액형, 종교
BLOOD_TYPES = ['A', 'B', 'O', 'AB']
RELIGIONS = ['무교', '기독교', '불교', '천주교']
HOBBIES = ['등산', '독서', '영화감상', '운동', '여행', '요리', '음악감상', '게임']
SPECIALTIES = ['프로그래밍', '외국어', '프레젠테이션', '데이터분석', '기획력']

# 서울 주소
ADDRESSES = [
    ('서울특별시 강남구 테헤란로 123', '06234'),
    ('서울특별시 서초구 서초대로 456', '06611'),
    ('서울특별시 송파구 올림픽로 789', '05551'),
    ('서울특별시 마포구 월드컵북로 111', '03991'),
    ('서울특별시 영등포구 여의대로 222', '07241'),
    ('경기도 성남시 분당구 판교역로 333', '13494'),
    ('경기도 수원시 영통구 광교로 444', '16229'),
]


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
    return f"{bank} {random.randint(100, 999)}-{random.randint(100000, 999999)}-{random.randint(10, 99)}-{random.randint(100, 999)}"


# ============================================
# 직원 생성 함수
# ============================================

def generate_employee(gender: str, index: int) -> Employee:
    """직원 기본 정보 생성"""
    if gender == 'M':
        surname = MALE_SURNAMES[index % len(MALE_SURNAMES)]
        given_name = MALE_NAMES[index % len(MALE_NAMES)]
        # 남성 이미지: face_01_m.png ~ face_11_m.png
        photo = f'/static/images/face/face_{(index % 11) + 1:02d}_m.png'
    else:
        surname = FEMALE_SURNAMES[index % len(FEMALE_SURNAMES)]
        given_name = FEMALE_NAMES[index % len(FEMALE_NAMES)]
        # 여성 이미지: face_12_f.png ~ face_25_f.png
        photo = f'/static/images/face/face_{(index % 14) + 12:02d}_f.png'

    name = surname + given_name
    english_surname = NAME_TO_ENGLISH.get(surname, surname)
    english_given = NAME_TO_ENGLISH.get(given_name, given_name)
    english_name = f"{english_surname} {english_given}"

    chinese_surname = NAME_TO_CHINESE.get(surname, surname)
    chinese_given = NAME_TO_CHINESE.get(given_name, given_name)
    chinese_name = f"{chinese_surname}{chinese_given}"

    # 생년월일 (1975~1998)
    birth_year = random.randint(1975, 1998)
    birth_date = random_date(birth_year, birth_year)

    # 입사일 (2015~2024)
    hire_date = random_date(2015, 2024)

    # 부서/직급
    department = random.choice(DEPARTMENTS)
    position = random.choice(POSITIONS)
    team = department.replace('팀', '') + random.choice(TEAMS)

    # 주소
    address, postal_code = random.choice(ADDRESSES)
    detailed_address = f"아파트 {random.randint(101, 120)}동 {random.randint(101, 2505)}호"

    # 주민번호 (마스킹)
    birth_short = birth_date.replace('-', '')[2:]
    gender_digit = '1' if gender == 'M' else '2'
    if birth_year >= 2000:
        gender_digit = '3' if gender == 'M' else '4'
    resident_number = f"{birth_short}-{gender_digit}******"

    # 직원번호
    employee_number = f"EMP-2025-{1001 + index:04d}"

    employee = Employee(
        employee_number=employee_number,
        name=name,
        photo=photo,
        department=department,
        position=position,
        status='active',
        hire_date=hire_date,
        phone=random_phone(),
        email=f"{name.lower().replace(' ', '')}@example.com",
        team=team,
        job_title=random.choice(JOB_TITLES),
        work_location=random.choice(WORK_LOCATIONS),
        internal_phone=str(random.randint(100, 999)),
        company_email=f"{name.lower()}@company.co.kr",
        english_name=english_name,
        chinese_name=chinese_name,
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
        disability_info=None,
    )

    return employee


# ============================================
# 이력 정보 생성 함수들
# ============================================

def generate_educations(employee_id: int, birth_year: int) -> list:
    """학력 정보 생성 (2~3건)"""
    educations = []

    # 고등학교 (18세)
    hs_admission = birth_year + 16
    hs_graduation = birth_year + 19
    educations.append(Education(
        employee_id=employee_id,
        school_type='고등학교',
        school_name=random.choice(HIGH_SCHOOLS),
        major='인문계' if random.random() > 0.5 else '이공계',
        degree=None,
        admission_date=f"{hs_admission}-03-01",
        graduation_date=f"{hs_graduation}-02-28",
        graduation_status='졸업',
        location='서울',
    ))

    # 대학교 (4년제)
    univ_admission = hs_graduation
    univ_graduation = univ_admission + 4
    educations.append(Education(
        employee_id=employee_id,
        school_type='대학교',
        school_name=random.choice(UNIVERSITIES),
        major=random.choice(MAJORS),
        degree='학사',
        admission_date=f"{univ_admission}-03-01",
        graduation_date=f"{univ_graduation}-02-28",
        graduation_status='졸업',
        location='서울',
    ))

    # 대학원 (30% 확률)
    if random.random() < 0.3:
        grad_admission = univ_graduation
        grad_graduation = grad_admission + 2
        educations.append(Education(
            employee_id=employee_id,
            school_type='대학원',
            school_name=random.choice(UNIVERSITIES) + ' 대학원',
            major=random.choice(MAJORS),
            degree='석사',
            admission_date=f"{grad_admission}-03-01",
            graduation_date=f"{grad_graduation}-02-28",
            graduation_status='졸업',
            location='서울',
        ))

    return educations


def generate_careers(employee_id: int, hire_date: str) -> list:
    """경력 정보 생성 (1~2건)"""
    careers = []
    hire_year = int(hire_date[:4])

    # 이전 경력 1
    end_year = hire_year - 1
    start_year = end_year - random.randint(1, 3)

    careers.append(Career(
        employee_id=employee_id,
        company_name=random.choice(COMPANIES),
        department=random.choice(DEPARTMENTS),
        position=random.choice(['사원', '대리']),
        job_description=random.choice(JOB_DESCRIPTIONS),
        start_date=f"{start_year}-{random.randint(1,12):02d}-01",
        end_date=f"{end_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        resignation_reason='이직',
        is_current=False,
    ))

    # 50% 확률로 추가 경력
    if random.random() < 0.5:
        end_year2 = start_year - 1
        start_year2 = end_year2 - random.randint(1, 2)
        careers.append(Career(
            employee_id=employee_id,
            company_name=random.choice(COMPANIES),
            department=random.choice(DEPARTMENTS),
            position='사원',
            job_description=random.choice(JOB_DESCRIPTIONS),
            start_date=f"{start_year2}-{random.randint(1,12):02d}-01",
            end_date=f"{end_year2}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            resignation_reason='이직',
            is_current=False,
        ))

    return careers


def generate_certificates(employee_id: int) -> list:
    """자격증 정보 생성 (0~2건)"""
    certificates = []
    count = random.randint(0, 2)

    selected = random.sample(CERTIFICATES, min(count, len(CERTIFICATES)))
    for cert_name, org in selected:
        acq_year = random.randint(2018, 2024)
        certificates.append(Certificate(
            employee_id=employee_id,
            certificate_name=cert_name,
            issuing_organization=org,
            certificate_number=f"CERT-{random.randint(10000, 99999)}",
            acquisition_date=random_date(acq_year, acq_year),
            expiry_date=None,
            grade=None,
        ))

    return certificates


def generate_family_members(employee_id: int) -> list:
    """가족 정보 생성 (2~4건)"""
    members = []

    # 부모 (필수)
    members.append(FamilyMember(
        employee_id=employee_id,
        relation='부',
        name=random.choice(MALE_SURNAMES) + random.choice(['진호', '성철', '동수', '상현']),
        birth_date=random_date(1945, 1960),
        occupation=random.choice(OCCUPATIONS),
        contact=random_phone(),
        is_cohabitant=random.choice([True, False]),
        is_dependent=random.choice([True, False]),
    ))

    members.append(FamilyMember(
        employee_id=employee_id,
        relation='모',
        name=random.choice(FEMALE_SURNAMES) + random.choice(['정숙', '미자', '영희', '순자']),
        birth_date=random_date(1948, 1963),
        occupation=random.choice(OCCUPATIONS),
        contact=random_phone(),
        is_cohabitant=random.choice([True, False]),
        is_dependent=random.choice([True, False]),
    ))

    # 50% 확률로 배우자
    if random.random() < 0.5:
        members.append(FamilyMember(
            employee_id=employee_id,
            relation='배우자',
            name=random.choice(FEMALE_SURNAMES + MALE_SURNAMES) + random.choice(['민지', '수현', '준호', '현우']),
            birth_date=random_date(1980, 1995),
            occupation=random.choice(OCCUPATIONS),
            contact=random_phone(),
            is_cohabitant=True,
            is_dependent=False,
        ))

        # 배우자가 있으면 30% 확률로 자녀
        if random.random() < 0.3:
            members.append(FamilyMember(
                employee_id=employee_id,
                relation='자녀',
                name=random.choice(MALE_SURNAMES + FEMALE_SURNAMES) + random.choice(['서준', '하윤', '도윤', '시우']),
                birth_date=random_date(2015, 2022),
                occupation='학생',
                contact=None,
                is_cohabitant=True,
                is_dependent=True,
            ))

    return members


def generate_languages(employee_id: int) -> list:
    """어학 정보 생성 (1~2건)"""
    languages = []
    count = random.randint(1, 2)

    selected = random.sample(LANGUAGE_EXAMS, min(count, len(LANGUAGE_EXAMS)))
    for lang_name, exam_name, scores in selected:
        acq_year = random.randint(2019, 2024)
        languages.append(Language(
            employee_id=employee_id,
            language_name=lang_name,
            exam_name=exam_name,
            score=random.choice(scores),
            level=None,
            acquisition_date=random_date(acq_year, acq_year),
            expiry_date=f"{acq_year + 2}-12-31" if 'TOEIC' in exam_name else None,
        ))

    return languages


def generate_military_service(employee_id: int, gender: str) -> MilitaryService:
    """병역 정보 생성 (남성만)"""
    if gender != 'M':
        return None

    # 90% 군필, 10% 면제
    if random.random() < 0.9:
        enlist_year = random.randint(2010, 2018)
        discharge_year = enlist_year + 2
        return MilitaryService(
            employee_id=employee_id,
            military_status='군필',
            service_type=random.choice(SERVICE_TYPES[:2]),  # 현역 또는 보충역
            branch=random.choice(MILITARY_BRANCHES),
            rank=random.choice(MILITARY_RANKS),
            enlistment_date=f"{enlist_year}-{random.randint(1,12):02d}-01",
            discharge_date=f"{discharge_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            discharge_reason='만기전역',
            exemption_reason=None,
        )
    else:
        return MilitaryService(
            employee_id=employee_id,
            military_status='면제',
            service_type=None,
            branch=None,
            rank=None,
            enlistment_date=None,
            discharge_date=None,
            discharge_reason=None,
            exemption_reason='신체등급',
        )


# ============================================
# 인사관리 정보 생성 함수들
# ============================================

def generate_salary(employee_id: int, position: str) -> Salary:
    """급여 정보 생성"""
    # 직급별 기본급
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


def generate_contract(employee_id: int, hire_date: str) -> Contract:
    """계약 정보 생성"""
    return Contract(
        employee_id=employee_id,
        contract_date=hire_date,
        contract_type='정규직',
        contract_period='무기한',
        employee_type='정규직',
        work_type='정규',
    )


def generate_benefit(employee_id: int, hire_date: str) -> Benefit:
    """복리후생 정보 생성"""
    # 근속년수에 따른 연차
    hire_year = int(hire_date[:4])
    years_worked = 2025 - hire_year
    granted = 15 + min(years_worked, 10)  # 최대 25일
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


def generate_insurance(employee_id: int) -> Insurance:
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


def generate_promotions(employee_id: int, hire_date: str, department: str, position: str) -> list:
    """발령 정보 생성 (1~2건)"""
    promotions = []
    hire_year = int(hire_date[:4])

    # 입사 발령
    promotions.append(Promotion(
        employee_id=employee_id,
        effective_date=hire_date,
        promotion_type='입사',
        from_department=None,
        to_department=department,
        from_position=None,
        to_position='사원',
        job_role=random.choice(JOB_TITLES),
        reason='신규입사',
    ))

    # 재직기간에 따라 승진 발령
    years_worked = 2025 - hire_year
    if years_worked >= 3 and position != '사원':
        promo_year = hire_year + random.randint(2, min(years_worked, 4))
        prev_positions = {'대리': '사원', '과장': '대리', '차장': '과장', '부장': '차장'}
        from_pos = prev_positions.get(position, '사원')

        promotions.append(Promotion(
            employee_id=employee_id,
            effective_date=f"{promo_year}-{random.choice(['01', '03', '07'])}-01",
            promotion_type='승진',
            from_department=department,
            to_department=department,
            from_position=from_pos,
            to_position=position,
            job_role=random.choice(JOB_TITLES),
            reason='정기승진',
        ))

    return promotions


def generate_evaluations(employee_id: int, hire_date: str) -> list:
    """평가 정보 생성 (1~2건)"""
    evaluations = []
    hire_year = int(hire_date[:4])

    for year in [2024, 2023]:
        if year > hire_year:
            grades = ['A', 'B+', 'B', 'B-', 'C']
            q1 = random.choice(grades)
            q2 = random.choice(grades)
            q3 = random.choice(grades)
            q4 = random.choice(grades)
            overall = random.choice(['A', 'B+', 'B'])

            evaluations.append(Evaluation(
                employee_id=employee_id,
                year=year,
                q1_grade=q1,
                q2_grade=q2,
                q3_grade=q3,
                q4_grade=q4,
                overall_grade=overall,
                salary_negotiation=f"{random.randint(3, 7)}% 인상" if overall in ['A', 'B+'] else '동결',
            ))

    return evaluations


def generate_trainings(employee_id: int, hire_date: str) -> list:
    """교육 정보 생성 (1~2건)"""
    trainings = []
    hire_year = int(hire_date[:4])
    count = random.randint(1, 2)

    selected = random.sample(TRAINING_NAMES, min(count, len(TRAINING_NAMES)))
    for training_name in selected:
        year = random.randint(max(hire_year, 2022), 2024)
        trainings.append(Training(
            employee_id=employee_id,
            training_date=random_date(year, year),
            training_name=training_name,
            institution=random.choice(TRAINING_INSTITUTIONS),
            hours=random.choice([8, 16, 24, 32, 40]),
            completion_status='수료',
        ))

    return trainings


def generate_projects(employee_id: int, hire_date: str) -> list:
    """프로젝트 정보 생성 (0~2건)"""
    projects = []
    hire_year = int(hire_date[:4])
    count = random.randint(0, 2)

    selected = random.sample(PROJECT_NAMES, min(count, len(PROJECT_NAMES)))
    for project_name in selected:
        start_year = random.randint(max(hire_year, 2022), 2024)
        start_month = random.randint(1, 6)
        end_month = start_month + random.randint(3, 6)
        end_year = start_year if end_month <= 12 else start_year + 1
        end_month = end_month if end_month <= 12 else end_month - 12

        projects.append(HrProject(
            employee_id=employee_id,
            project_name=project_name,
            start_date=f"{start_year}-{start_month:02d}-01",
            end_date=f"{end_year}-{end_month:02d}-{random.randint(15, 28):02d}",
            duration=f"{random.randint(3, 8)}개월",
            role=random.choice(PROJECT_ROLES),
            duty=random.choice(JOB_DESCRIPTIONS),
            client=random.choice(['내부', '외부고객사']),
        ))

    return projects


def generate_awards(employee_id: int, hire_date: str) -> list:
    """수상 정보 생성 (0~1건)"""
    awards = []
    hire_year = int(hire_date[:4])

    if random.random() < 0.3:  # 30% 확률
        year = random.randint(max(hire_year + 1, 2022), 2024)
        awards.append(Award(
            employee_id=employee_id,
            award_date=f"{year}-12-{random.randint(15, 28):02d}",
            award_name=random.choice(AWARDS),
            institution='주식회사 샘플컴퍼니',
        ))

    return awards


def generate_assets(employee_id: int, hire_date: str) -> list:
    """자산 정보 생성 (1~2건)"""
    assets = []
    count = random.randint(1, 2)

    selected = random.sample(ASSET_ITEMS, min(count, len(ASSET_ITEMS)))
    for item_name, models in selected:
        assets.append(Asset(
            employee_id=employee_id,
            issue_date=hire_date,
            item_name=item_name,
            model=random.choice(models),
            serial_number=f"SN-{random.randint(20200001, 20259999)}",
            status='사용중',
        ))

    return assets


def generate_attendances(employee_id: int) -> list:
    """근태 정보 생성 (최근 3개월)"""
    attendances = []

    for month in [9, 10, 11]:  # 2025년 9, 10, 11월
        work_days = random.randint(20, 23)
        absent = random.randint(0, 2)
        late = random.randint(0, 3)
        early = random.randint(0, 2)
        leave_used = random.randint(0, 2)

        attendances.append(Attendance(
            employee_id=employee_id,
            year=2025,
            month=month,
            work_days=work_days,
            absent_days=absent,
            late_count=late,
            early_leave_count=early,
            annual_leave_used=leave_used,
        ))

    return attendances


# ============================================
# 메인 실행
# ============================================

def main():
    """메인 실행 함수"""
    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("샘플 직원 데이터 생성 시작")
        print("=" * 50)

        # 기존 데이터 확인
        existing_count = Employee.query.count()
        print(f"기존 직원 수: {existing_count}")

        # 기존 직원번호 중 최대값 확인
        max_emp = db.session.query(db.func.max(Employee.employee_number)).scalar()
        if max_emp:
            try:
                # EMP-2025-1005 형식에서 숫자 추출
                start_number = int(max_emp.split('-')[-1]) + 1
            except:
                start_number = 1001 + existing_count
        else:
            start_number = 1001

        print(f"시작 직원번호: EMP-2025-{start_number:04d}")

        employees_created = []
        emp_index = 0

        # 남성 5명 생성
        print("\n[남성 직원 5명 생성]")
        for i in range(5):
            emp = generate_employee('M', i)
            emp.employee_number = f"EMP-2025-{start_number + emp_index:04d}"
            db.session.add(emp)
            db.session.flush()  # ID 확보
            employees_created.append(emp)
            print(f"  - {emp.name} ({emp.employee_number})")
            emp_index += 1

        # 여성 5명 생성
        print("\n[여성 직원 5명 생성]")
        for i in range(5):
            emp = generate_employee('F', i)
            emp.employee_number = f"EMP-2025-{start_number + emp_index:04d}"
            db.session.add(emp)
            db.session.flush()  # ID 확보
            employees_created.append(emp)
            print(f"  - {emp.name} ({emp.employee_number})")
            emp_index += 1

        # 각 직원별 관련 데이터 생성
        print("\n[관련 데이터 생성]")
        for emp in employees_created:
            birth_year = int(emp.birth_date[:4])

            # 이력 정보
            for edu in generate_educations(emp.id, birth_year):
                db.session.add(edu)

            for career in generate_careers(emp.id, emp.hire_date):
                db.session.add(career)

            for cert in generate_certificates(emp.id):
                db.session.add(cert)

            for family in generate_family_members(emp.id):
                db.session.add(family)

            for lang in generate_languages(emp.id):
                db.session.add(lang)

            military = generate_military_service(emp.id, emp.gender)
            if military:
                db.session.add(military)

            # 인사관리 정보
            db.session.add(generate_salary(emp.id, emp.position))
            db.session.add(generate_contract(emp.id, emp.hire_date))
            db.session.add(generate_benefit(emp.id, emp.hire_date))
            db.session.add(generate_insurance(emp.id))

            for promo in generate_promotions(emp.id, emp.hire_date, emp.department, emp.position):
                db.session.add(promo)

            for eval_item in generate_evaluations(emp.id, emp.hire_date):
                db.session.add(eval_item)

            for training in generate_trainings(emp.id, emp.hire_date):
                db.session.add(training)

            for project in generate_projects(emp.id, emp.hire_date):
                db.session.add(project)

            for award in generate_awards(emp.id, emp.hire_date):
                db.session.add(award)

            for asset in generate_assets(emp.id, emp.hire_date):
                db.session.add(asset)

            for attendance in generate_attendances(emp.id):
                db.session.add(attendance)

            print(f"  - {emp.name}: 이력/인사관리 데이터 생성 완료")

        # 커밋
        db.session.commit()

        print("\n" + "=" * 50)
        print(f"생성 완료! 총 {len(employees_created)}명의 직원 데이터가 추가되었습니다.")
        print("=" * 50)

        # 통계 출력
        print("\n[생성된 데이터 통계]")
        print(f"  - 직원: {Employee.query.count()}명")
        print(f"  - 학력: {Education.query.count()}건")
        print(f"  - 경력: {Career.query.count()}건")
        print(f"  - 자격증: {Certificate.query.count()}건")
        print(f"  - 가족: {FamilyMember.query.count()}건")
        print(f"  - 어학: {Language.query.count()}건")
        print(f"  - 병역: {MilitaryService.query.count()}건")
        print(f"  - 급여: {Salary.query.count()}건")
        print(f"  - 계약: {Contract.query.count()}건")
        print(f"  - 복리후생: {Benefit.query.count()}건")
        print(f"  - 보험: {Insurance.query.count()}건")
        print(f"  - 발령: {Promotion.query.count()}건")
        print(f"  - 평가: {Evaluation.query.count()}건")
        print(f"  - 교육: {Training.query.count()}건")
        print(f"  - 프로젝트: {Project.query.count()}건")
        print(f"  - 수상: {Award.query.count()}건")
        print(f"  - 자산: {Asset.query.count()}건")
        print(f"  - 근태: {Attendance.query.count()}건")


if __name__ == '__main__':
    main()
