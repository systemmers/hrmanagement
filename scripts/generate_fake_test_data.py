"""
포괄적 테스트 데이터 생성 스크립트

법인 3개, 직원 20명, 개인 20명의 완전한 테스트 데이터를 생성합니다.
모든 테이블(33개)에 대해 현실적인 가짜 데이터를 생성합니다.

데이터 포함:
- 기본정보 (법인, 조직, 사용자, 직원, 개인 프로필)
- 이력정보 (학력, 경력, 자격증, 어학, 가족, 병역)
- 인사기록 (발령, 평가, 교육, 근태, 프로젝트)
- 급여정보 (급여, 연봉이력, 급여지급, 복리후생, 보험)
- 자산정보 (자산배정, 수상)
- 계약정보 (계약, 개인-법인 계약, 데이터공유설정)

실행 방법:
    python scripts/generate_fake_test_data.py
    python scripts/generate_fake_test_data.py --dry-run    # 미리보기
    python scripts/generate_fake_test_data.py --clear      # 기존 테스트 데이터 삭제 후 생성
    python scripts/generate_fake_test_data.py --status     # 현재 상태만 확인
"""
import sys
import os
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database import db
from app.models import (
    User, Company, Organization, Employee,
    Education, Career, Certificate, Language, FamilyMember,
    MilitaryService, Salary, Benefit, Contract, Insurance,
    SalaryHistory, SalaryPayment, Promotion, Evaluation, Training,
    Attendance, HrProject, ProjectParticipation, Award, Asset, Attachment,
    PersonalProfile, PersonalEducation, PersonalCareer,
    PersonalCertificate, PersonalLanguage, PersonalMilitaryService,
    PersonCorporateContract, DataSharingSettings
)


# ============================================================
# 한국식 가짜 데이터 상수
# ============================================================

KOREAN_LAST_NAMES = [
    '김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
    '한', '오', '서', '신', '권', '황', '안', '송', '류', '홍'
]

KOREAN_FIRST_NAMES_MALE = [
    '민준', '서준', '도윤', '예준', '시우', '하준', '주원', '지호', '준서', '준우',
    '현우', '지훈', '건우', '우진', '민재', '현준', '선우', '서진', '연우', '정우'
]

KOREAN_FIRST_NAMES_FEMALE = [
    '서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지민', '채원',
    '수아', '지아', '지윤', '다은', '은서', '예은', '수빈', '소율', '예린', '시은'
]

DEPARTMENTS = ['개발팀', '기획팀', '영업팀', '마케팅팀', '인사팀', '재무팀', '경영지원팀', 'R&D팀']
POSITIONS = ['사원', '주임', '대리', '과장', '차장', '부장', '이사', '상무']
JOB_TITLES = ['팀원', '파트장', '팀장', '실장', '본부장']
STATUS_OPTIONS = ['재직', '휴직', '퇴직']
WORK_LOCATIONS = ['본사', '서울지사', '부산지사', '대전지사', '광주지사', '재택근무']

SCHOOL_TYPES = ['고등학교', '전문대학', '대학교', '대학원']
SCHOOL_NAMES = [
    '서울대학교', '연세대학교', '고려대학교', '성균관대학교', '한양대학교',
    '중앙대학교', '경희대학교', '한국외국어대학교', '서강대학교', '이화여자대학교',
    '부산대학교', '경북대학교', '전남대학교', '충남대학교', '전북대학교',
    '인하대학교', '아주대학교', '숭실대학교', '건국대학교', '동국대학교'
]
HIGH_SCHOOL_NAMES = ['서울고등학교', '경기고등학교', '부산고등학교', '대전고등학교', '광주고등학교']
MAJORS = [
    '컴퓨터공학', '경영학', '경제학', '전자공학', '기계공학',
    '화학공학', '심리학', '국어국문학', '영어영문학', '수학',
    '물리학', '생명과학', '건축학', '산업디자인', '법학',
    '회계학', '통계학', '소프트웨어학', '정보통신학', '국제통상학'
]

CERTIFICATE_NAMES = [
    '정보처리기사', '전자계산기기사', 'SQLD', 'AWS Solutions Architect',
    '컴퓨터활용능력 1급', '사무자동화산업기사', 'PMP', 'TOEIC 900점 이상',
    '빅데이터분석기사', '리눅스마스터 1급', '네트워크관리사', 'JLPT N1',
    '정보보안기사', 'CCNA', 'Azure Administrator', '데이터분석전문가'
]

ISSUING_ORGS = [
    '한국산업인력공단', 'AWS', 'PMI', 'ETS', '한국데이터산업진흥원',
    '한국정보통신기술협회', '대한상공회의소', 'Microsoft', 'Cisco',
    '일본국제교류기금', '한국정보통신진흥협회'
]

LANGUAGES = ['영어', '일본어', '중국어', '독일어', '프랑스어', '스페인어']
LANGUAGE_EXAMS = {
    '영어': ['TOEIC', 'TOEFL', 'IELTS', 'TEPS', 'OPIc'],
    '일본어': ['JLPT', 'JPT'],
    '중국어': ['HSK', 'BCT', 'TSC'],
    '독일어': ['TestDaF', 'Goethe-Zertifikat'],
    '프랑스어': ['DELF', 'DALF', 'TCF'],
    '스페인어': ['DELE', 'SIELE']
}

FAMILY_RELATIONS = ['배우자', '자녀', '부', '모', '형', '누나', '동생', '조부', '조모']

MILITARY_STATUS = ['군필', '미필', '면제', '해당없음']
SERVICE_TYPES = ['육군', '해군', '공군', '해병대', '의무경찰', '사회복무요원', '산업기능요원']
RANKS = ['이병', '일병', '상병', '병장', '하사', '중사']
BRANCHES = ['육군', '해군', '공군', '해병대']

PROMOTION_TYPES = ['승진', '전보', '발령', '파견', '복직', '휴직', '직무변경']
EVALUATION_GRADES = ['S', 'A', 'B', 'C', 'D']

TRAINING_NAMES = [
    '신입사원 교육', '리더십 교육', 'OJT 교육', '직무역량 교육', '안전교육',
    '성희롱 예방교육', '개인정보보호 교육', '정보보안 교육', 'AI/ML 기초',
    '프로젝트 관리', '커뮤니케이션 스킬', '프레젠테이션 기법', '데이터 분석 실무'
]

TRAINING_INSTITUTIONS = [
    '사내교육팀', '한국생산성본부', '한국능률협회', '삼성멀티캠퍼스',
    'Coursera', 'Udemy', '패스트캠퍼스', '인프런'
]

PROJECT_NAMES = [
    'ERP 시스템 구축', '모바일 앱 개발', '웹사이트 리뉴얼', 'AI 챗봇 개발',
    '클라우드 마이그레이션', '보안 시스템 강화', '데이터 분석 플랫폼',
    'CRM 시스템 도입', 'IoT 플랫폼 개발', 'DevOps 환경 구축',
    'HR 시스템 고도화', '전자결재 시스템 구축', '통합 로그 시스템'
]

PROJECT_ROLES = ['PM', 'PL', '개발자', '기획자', 'QA', '디자이너', 'DBA', '아키텍트']

ASSET_ITEMS = [
    ('노트북', ['MacBook Pro 14', 'ThinkPad X1 Carbon', 'Dell XPS 15', 'LG Gram 17']),
    ('모니터', ['LG 27UL850', 'Dell U2720Q', 'Samsung 32 Curved']),
    ('키보드', ['Apple Magic Keyboard', 'Logitech MX Keys', 'HHKB Professional']),
    ('마우스', ['Apple Magic Mouse', 'Logitech MX Master 3', 'Microsoft Arc Mouse']),
    ('휴대폰', ['iPhone 15 Pro', 'Galaxy S24 Ultra', 'Pixel 8 Pro']),
    ('의자', ['허먼밀러 에어론', '시디즈 T80', '듀오백 DK-2500G']),
]

AWARD_NAMES = [
    '이달의 우수사원', '분기 MVP', '프로젝트 공로상', '고객만족상',
    '혁신상', '봉사상', '장기근속상', '신인상', '팀워크상'
]


# ============================================================
# 유틸리티 함수
# ============================================================

def generate_phone():
    """랜덤 휴대폰 번호 생성"""
    return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"


def generate_home_phone():
    """랜덤 자택 전화번호 생성"""
    area_codes = ['02', '031', '032', '051', '052', '053', '062', '042', '044']
    return f"{random.choice(area_codes)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def generate_email(name, domain='company.com'):
    """이메일 생성"""
    import unicodedata
    romanized = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    ).replace(' ', '').lower()
    if not romanized or not romanized.isascii():
        romanized = f"user{random.randint(1000, 9999)}"
    return f"{romanized}@{domain}"


def generate_birth_date(min_age=25, max_age=55):
    """생년월일 생성"""
    today = date.today()
    age = random.randint(min_age, max_age)
    birth_year = today.year - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"


def generate_hire_date(min_years=0, max_years=15):
    """입사일 생성"""
    today = date.today()
    years_ago = random.randint(min_years, max_years)
    months_ago = random.randint(0, 11)
    hire_date = today - timedelta(days=(years_ago * 365 + months_ago * 30))
    return hire_date.strftime('%Y-%m-%d')


def generate_past_date(min_years=1, max_years=5):
    """과거 날짜 생성"""
    today = date.today()
    days_ago = random.randint(min_years * 365, max_years * 365)
    past_date = today - timedelta(days=days_ago)
    return past_date.strftime('%Y-%m-%d')


def generate_address():
    """주소 생성"""
    cities = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '경기도']
    districts = {
        '서울특별시': ['강남구', '서초구', '송파구', '마포구', '영등포구', '용산구', '중구', '종로구', '강서구', '성북구'],
        '부산광역시': ['해운대구', '수영구', '동래구', '부산진구', '남구'],
        '대구광역시': ['수성구', '달서구', '중구', '동구'],
        '인천광역시': ['연수구', '남동구', '부평구', '계양구'],
        '광주광역시': ['서구', '북구', '동구', '남구'],
        '대전광역시': ['서구', '유성구', '중구', '동구'],
        '경기도': ['성남시 분당구', '용인시 수지구', '수원시 영통구', '고양시 일산동구', '안양시 동안구'],
    }
    city = random.choice(cities)
    district = random.choice(districts.get(city, ['중구']))
    streets = ['대로', '로', '길']
    return f"{city} {district} 테스트{random.choice(streets)} {random.randint(1, 500)}"


def generate_postal_code():
    """우편번호 생성"""
    return f"{random.randint(10000, 99999)}"


def generate_resident_number(birth_date, gender):
    """주민등록번호 생성 (가짜)"""
    front = birth_date.replace('-', '')[2:8]
    year = int(birth_date[:4])
    if year >= 2000:
        gender_code = '3' if gender == '남' else '4'
    else:
        gender_code = '1' if gender == '남' else '2'
    back = f"{gender_code}{random.randint(100000, 999999)}"
    return f"{front}-{back}"


def generate_employee_number(index):
    """사번 생성"""
    year = datetime.now().year
    return f"EMP-{year}-{index:04d}"


def generate_business_number():
    """사업자등록번호 생성"""
    return f"{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(10000, 99999)}"


def generate_bank_account():
    """계좌번호 생성"""
    banks = ['신한은행', '국민은행', '우리은행', '하나은행', 'IBK기업은행', '농협은행', '카카오뱅크', '토스뱅크']
    return f"{random.choice(banks)} {random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100000, 999999)}"


def generate_serial_number():
    """시리얼 번호 생성"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choices(chars, k=12))


# ============================================================
# 법인 데이터 생성
# ============================================================

def create_companies(dry_run=False):
    """법인 3개 생성"""
    print("\n[Phase 1] 법인 데이터 생성")
    print("-" * 50)

    companies_data = [
        {
            'name': '(주)테크노소프트',
            'business_number': '1234567890',
            'representative': '김대표',
            'business_type': '정보통신업',
            'business_category': '소프트웨어 개발 및 공급업',
            'email': 'contact@technosoft.co.kr',
            'phone': '02-1234-5678',
            'fax': '02-1234-5679',
            'website': 'https://technosoft.co.kr',
            'address': '서울특별시 강남구 테헤란로 123',
            'address_detail': '테크노빌딩 10층',
            'postal_code': '06142',
            'plan_type': 'premium',
            'max_employees': 200,
        },
        {
            'name': '(주)디지털웨이브',
            'business_number': '2345678901',
            'representative': '이사장',
            'business_type': '정보통신업',
            'business_category': '플랫폼 서비스업',
            'email': 'info@digitalwave.kr',
            'phone': '02-2345-6789',
            'fax': '02-2345-6780',
            'website': 'https://digitalwave.kr',
            'address': '서울특별시 서초구 서초대로 456',
            'address_detail': '웨이브타워 15층',
            'postal_code': '06623',
            'plan_type': 'basic',
            'max_employees': 50,
        },
        {
            'name': '(주)스마트솔루션즈',
            'business_number': '3456789012',
            'representative': '박회장',
            'business_type': '제조업',
            'business_category': 'IoT 디바이스 제조업',
            'email': 'hello@smartsolutions.com',
            'phone': '031-3456-7890',
            'fax': '031-3456-7891',
            'website': 'https://smartsolutions.com',
            'address': '경기도 성남시 분당구 판교로 789',
            'address_detail': '스마트센터 5층',
            'postal_code': '13494',
            'plan_type': 'enterprise',
            'max_employees': 500,
        }
    ]

    created_companies = []

    for i, data in enumerate(companies_data, 1):
        existing = Company.query.filter_by(business_number=data['business_number']).first()
        if existing:
            print(f"  [SKIP] {data['name']} - 이미 존재")
            created_companies.append(existing)
            continue

        if dry_run:
            print(f"  [DRY] {data['name']} 생성 예정")
            continue

        # Organization 생성 (루트)
        org = Organization(
            name=data['name'],
            code=f"ORG-{i:03d}",
            org_type='company',
            is_active=True,
            description=f"{data['name']} 루트 조직"
        )
        db.session.add(org)
        db.session.flush()

        # 하위 조직 생성 (부서)
        dept_names = ['개발본부', '경영지원본부', '영업본부']
        for j, dept_name in enumerate(dept_names, 1):
            dept = Organization(
                name=dept_name,
                code=f"ORG-{i:03d}-{j:02d}",
                org_type='division',
                parent_id=org.id,
                sort_order=j,
                is_active=True
            )
            db.session.add(dept)
        db.session.flush()

        # Company 생성
        company = Company(
            name=data['name'],
            business_number=data['business_number'],
            representative=data['representative'],
            business_type=data['business_type'],
            business_category=data['business_category'],
            email=data['email'],
            phone=data['phone'],
            fax=data['fax'],
            website=data['website'],
            address=data['address'],
            address_detail=data['address_detail'],
            postal_code=data['postal_code'],
            plan_type=data['plan_type'],
            max_employees=data['max_employees'],
            root_organization_id=org.id,
            is_active=True,
            is_verified=True,
            verified_at=datetime.utcnow(),
            establishment_date=date(2010 + i, 1, 1)
        )
        db.session.add(company)
        db.session.flush()

        # Corporate User 생성
        username = f"corp_{i}"
        email = f"corp{i}@test.com"

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if not existing_user:
            corp_user = User(
                username=username,
                email=email,
                role='admin',
                account_type='corporate',
                company_id=company.id,
                is_active=True
            )
            corp_user.set_password('corp1234')
            db.session.add(corp_user)

        created_companies.append(company)
        print(f"  + {data['name']} (ID: {company.id})")

    if not dry_run and created_companies:
        db.session.commit()

    print(f"\n  총 {len(created_companies)}개 법인 처리 완료")
    return created_companies


# ============================================================
# 직원 데이터 생성 (모든 관련 테이블 포함)
# ============================================================

def create_employees(companies, count=20, dry_run=False):
    """직원 20명 생성 (모든 관련 데이터 포함)"""
    print("\n[Phase 2] 직원 데이터 생성")
    print("-" * 50)

    if not companies:
        print("  [ERROR] 법인이 없습니다.")
        return []

    # 법인별 직원 분배 (7, 7, 6)
    distribution = [7, 7, 6]
    created_employees = []
    emp_index = 1

    for company_idx, company in enumerate(companies):
        if company_idx >= len(distribution):
            break

        emp_count = distribution[company_idx]
        print(f"\n  {company.name}: {emp_count}명 생성")

        for i in range(emp_count):
            gender = '남' if random.random() < 0.6 else '여'
            last_name = random.choice(KOREAN_LAST_NAMES)
            first_name = random.choice(
                KOREAN_FIRST_NAMES_MALE if gender == '남' else KOREAN_FIRST_NAMES_FEMALE
            )
            name = f"{last_name}{first_name}"
            birth_date = generate_birth_date()
            hire_date = generate_hire_date()
            department = random.choice(DEPARTMENTS)
            position = random.choice(POSITIONS)

            if dry_run:
                print(f"    [DRY] {name} 생성 예정")
                emp_index += 1
                continue

            # Employee 기본 정보
            employee = Employee(
                employee_number=generate_employee_number(emp_index),
                name=name,
                department=department,
                position=position,
                status='active',
                hire_date=hire_date,
                phone=generate_phone(),
                email=generate_email(name, 'company.co.kr'),
                organization_id=company.root_organization_id,
                team=random.choice(['A팀', 'B팀', 'C팀', None]),
                job_title=random.choice(JOB_TITLES),
                work_location=random.choice(WORK_LOCATIONS),
                internal_phone=f"{random.randint(100, 999)}",
                company_email=generate_email(name, f"{company.name.replace('(주)', '').strip()}.co.kr"),
                english_name=f"{first_name} {last_name}",
                birth_date=birth_date,
                lunar_birth=random.choice([True, False]),
                gender=gender,
                mobile_phone=generate_phone(),
                home_phone=generate_home_phone() if random.random() > 0.5 else None,
                address=generate_address(),
                detailed_address=f"테스트아파트 {random.randint(100, 999)}호",
                postal_code=generate_postal_code(),
                resident_number=generate_resident_number(birth_date, gender),
                nationality='대한민국',
                blood_type=random.choice(['A', 'B', 'O', 'AB']),
                religion=random.choice(['무교', '기독교', '불교', '천주교', None]),
                hobby=random.choice(['독서', '운동', '여행', '음악감상', '요리', None]),
                specialty=random.choice(['프로그래밍', '기획', '디자인', '영업', None]),
                marital_status=random.choice(['single', 'married']),
                emergency_contact=generate_phone(),
                emergency_relation=random.choice(['배우자', '부모', '형제']),
                actual_postal_code=generate_postal_code(),
                actual_address=generate_address(),
                actual_detailed_address=f"실거주아파트 {random.randint(100, 999)}호",
            )
            db.session.add(employee)
            db.session.flush()

            # === 1:N 관계 데이터 생성 ===

            # 학력 (1-3개)
            for edu_idx in range(random.randint(1, 3)):
                if edu_idx == 0:  # 고등학교
                    edu = Education(
                        employee_id=employee.id,
                        school_type='고등학교',
                        school_name=random.choice(HIGH_SCHOOL_NAMES),
                        graduation_date=f"{int(birth_date[:4]) + 18}-02-28",
                        graduation_status='졸업'
                    )
                else:  # 대학교
                    edu = Education(
                        employee_id=employee.id,
                        school_type=random.choice(['대학교', '전문대학', '대학원']),
                        school_name=random.choice(SCHOOL_NAMES),
                        major=random.choice(MAJORS),
                        degree=random.choice(['학사', '석사', '박사', '전문학사']),
                        admission_date=f"{int(birth_date[:4]) + 18 + (edu_idx * 4)}-03-01",
                        graduation_date=f"{int(birth_date[:4]) + 22 + (edu_idx * 4)}-02-28",
                        graduation_status='졸업',
                        gpa=f"{random.uniform(3.0, 4.5):.2f}/4.5",
                        location=random.choice(['서울', '경기', '부산', '대전'])
                    )
                db.session.add(edu)

            # 경력 (0-3개)
            for _ in range(random.randint(0, 3)):
                start_year = random.randint(2015, 2020)
                end_year = start_year + random.randint(1, 3)
                career = Career(
                    employee_id=employee.id,
                    company_name=f"(주){random.choice(['테스트', '샘플', '예시', '이전'])}기업",
                    department=random.choice(DEPARTMENTS),
                    position=random.choice(POSITIONS),
                    job_description=f"{random.choice(['서비스 개발', '프로젝트 관리', '영업 활동', '마케팅'])} 담당",
                    start_date=f"{start_year}-{random.randint(1, 12):02d}-01",
                    end_date=f"{end_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    salary=random.randint(3000, 6000) * 10000,
                    resignation_reason=random.choice(['이직', '계약만료', '개인사정', None]),
                    is_current=False
                )
                db.session.add(career)

            # 자격증 (0-3개)
            for _ in range(random.randint(0, 3)):
                cert = Certificate(
                    employee_id=employee.id,
                    certificate_name=random.choice(CERTIFICATE_NAMES),
                    issuing_organization=random.choice(ISSUING_ORGS),
                    certificate_number=f"CERT-{random.randint(10000, 99999)}",
                    acquisition_date=generate_past_date(1, 5),
                    expiry_date=None if random.random() > 0.3 else generate_past_date(-3, -1),
                    grade=random.choice(['1급', '2급', '전문가', None])
                )
                db.session.add(cert)

            # 어학 (0-2개)
            for _ in range(random.randint(0, 2)):
                lang_name = random.choice(LANGUAGES)
                lang = Language(
                    employee_id=employee.id,
                    language_name=lang_name,
                    exam_name=random.choice(LANGUAGE_EXAMS.get(lang_name, ['기타'])),
                    score=str(random.randint(700, 990)) if lang_name == '영어' else random.choice(['N1', 'N2', '고급', '중급']),
                    level=random.choice(['상', '중', '하']),
                    acquisition_date=generate_past_date(1, 3)
                )
                db.session.add(lang)

            # 가족 (0-4명)
            if random.random() > 0.3:  # 70% 확률로 가족 정보 있음
                for _ in range(random.randint(1, 4)):
                    relation = random.choice(FAMILY_RELATIONS)
                    family = FamilyMember(
                        employee_id=employee.id,
                        relation=relation,
                        name=f"{random.choice(KOREAN_LAST_NAMES)}{random.choice(KOREAN_FIRST_NAMES_MALE + KOREAN_FIRST_NAMES_FEMALE)}",
                        birth_date=generate_birth_date(1, 80),
                        occupation=random.choice(['회사원', '공무원', '자영업', '학생', '주부', None]),
                        contact=generate_phone() if random.random() > 0.5 else None,
                        is_cohabitant=random.choice([True, False]),
                        is_dependent=relation in ['자녀', '부', '모']
                    )
                    db.session.add(family)

            # 발령/인사이동 (1-3개)
            current_dept = department
            current_pos = position
            for promo_idx in range(random.randint(1, 3)):
                new_dept = random.choice(DEPARTMENTS)
                new_pos = random.choice(POSITIONS)
                promo = Promotion(
                    employee_id=employee.id,
                    effective_date=generate_past_date(promo_idx, promo_idx + 1),
                    promotion_type=random.choice(PROMOTION_TYPES),
                    from_department=current_dept,
                    to_department=new_dept,
                    from_position=current_pos,
                    to_position=new_pos,
                    job_role=random.choice(JOB_TITLES),
                    reason='정기 인사' if promo_idx == 0 else random.choice(['승진', '전보', '조직개편'])
                )
                db.session.add(promo)
                current_dept, current_pos = new_dept, new_pos

            # 인사평가 (최근 3년)
            current_year = datetime.now().year
            for year in range(current_year - 2, current_year + 1):
                evaluation = Evaluation(
                    employee_id=employee.id,
                    year=year,
                    q1_grade=random.choice(EVALUATION_GRADES),
                    q2_grade=random.choice(EVALUATION_GRADES),
                    q3_grade=random.choice(EVALUATION_GRADES) if year < current_year else None,
                    q4_grade=random.choice(EVALUATION_GRADES) if year < current_year else None,
                    overall_grade=random.choice(EVALUATION_GRADES) if year < current_year else None,
                    salary_negotiation=f"+{random.randint(0, 10)}%" if year < current_year else None
                )
                db.session.add(evaluation)

            # 교육 이력 (2-5개)
            for _ in range(random.randint(2, 5)):
                training = Training(
                    employee_id=employee.id,
                    training_date=generate_past_date(0, 3),
                    training_name=random.choice(TRAINING_NAMES),
                    institution=random.choice(TRAINING_INSTITUTIONS),
                    hours=random.choice([8, 16, 24, 40, 80]),
                    completion_status=random.choice(['수료', '이수', '진행중'])
                )
                db.session.add(training)

            # 근태 (최근 12개월)
            for month_offset in range(12):
                month_date = date.today().replace(day=1) - timedelta(days=30 * month_offset)
                attendance = Attendance(
                    employee_id=employee.id,
                    year=month_date.year,
                    month=month_date.month,
                    work_days=random.randint(18, 23),
                    absent_days=random.randint(0, 2),
                    late_count=random.randint(0, 3),
                    early_leave_count=random.randint(0, 2),
                    annual_leave_used=random.randint(0, 2)
                )
                db.session.add(attendance)

            # 인사이력 프로젝트 (1-3개)
            for _ in range(random.randint(1, 3)):
                start_date = generate_past_date(0, 2)
                hr_project = HrProject(
                    employee_id=employee.id,
                    project_name=random.choice(PROJECT_NAMES),
                    start_date=start_date,
                    end_date=None if random.random() > 0.7 else generate_past_date(0, 1),
                    duration=f"{random.randint(3, 24)}개월",
                    role=random.choice(PROJECT_ROLES),
                    duty=f"{random.choice(['개발', '기획', '관리', '분석'])} 업무",
                    client=f"{random.choice(['삼성', 'LG', 'SK', 'KT', '현대', '롯데'])}그룹"
                )
                db.session.add(hr_project)

            # 경력 프로젝트 참여이력 (0-2개)
            for _ in range(random.randint(0, 2)):
                participation = ProjectParticipation(
                    employee_id=employee.id,
                    project_name=f"이전회사 {random.choice(PROJECT_NAMES)}",
                    start_date=generate_past_date(3, 5),
                    end_date=generate_past_date(2, 3),
                    role=random.choice(PROJECT_ROLES),
                    duty=f"{random.choice(['개발', '기획', '관리'])} 담당",
                    client=f"이전고객사"
                )
                db.session.add(participation)

            # 수상 (0-2개)
            for _ in range(random.randint(0, 2)):
                award = Award(
                    employee_id=employee.id,
                    award_date=generate_past_date(0, 3),
                    award_name=random.choice(AWARD_NAMES),
                    institution=company.name
                )
                db.session.add(award)

            # 자산 배정 (1-3개)
            for _ in range(random.randint(1, 3)):
                item_category, models = random.choice(ASSET_ITEMS)
                asset = Asset(
                    employee_id=employee.id,
                    issue_date=generate_past_date(0, 2),
                    item_name=item_category,
                    model=random.choice(models),
                    serial_number=generate_serial_number(),
                    status=random.choice(['사용중', '반납', '수리중'])
                )
                db.session.add(asset)

            # === 1:1 관계 데이터 생성 ===

            # 병역 (남성만)
            if gender == '남':
                military = MilitaryService(
                    employee_id=employee.id,
                    military_status=random.choice(['군필', '면제']),
                    service_type=random.choice(SERVICE_TYPES) if random.random() > 0.2 else None,
                    branch=random.choice(BRANCHES),
                    rank=random.choice(RANKS),
                    enlistment_date=f"{int(birth_date[:4]) + 20}-{random.randint(1, 12):02d}-01" if random.random() > 0.2 else None,
                    discharge_date=f"{int(birth_date[:4]) + 22}-{random.randint(1, 12):02d}-01" if random.random() > 0.2 else None,
                    discharge_reason='만기전역'
                )
                db.session.add(military)

            # 급여 정보
            base_salary = random.randint(3000, 8000) * 10000
            position_allowance = random.randint(10, 50) * 10000
            meal_allowance = 200000
            transportation_allowance = 100000
            total_salary = base_salary + position_allowance + meal_allowance + transportation_allowance

            salary = Salary(
                employee_id=employee.id,
                salary_type=random.choice(['연봉제', '월급제']),
                base_salary=base_salary,
                position_allowance=position_allowance,
                meal_allowance=meal_allowance,
                transportation_allowance=transportation_allowance,
                total_salary=total_salary,
                payment_day=25,
                payment_method='계좌이체',
                bank_account=generate_bank_account(),
                annual_salary=total_salary * 12,
                monthly_salary=total_salary,
                hourly_wage=int(total_salary / 209),
                overtime_hours=random.randint(0, 20),
                night_hours=random.randint(0, 10),
                holiday_days=random.randint(0, 2)
            )
            db.session.add(salary)

            # 연봉 계약 이력 (최근 3년)
            for year in range(current_year - 2, current_year + 1):
                annual = base_salary * 12 * (1 + (current_year - year) * 0.05)
                history = SalaryHistory(
                    employee_id=employee.id,
                    contract_year=year,
                    annual_salary=int(annual),
                    bonus=int(annual * 0.1),
                    total_amount=int(annual * 1.1),
                    contract_period=f"{year}-01-01 ~ {year}-12-31"
                )
                db.session.add(history)

            # 급여 지급 이력 (최근 6개월)
            for month_offset in range(6):
                payment_date = date.today().replace(day=25) - timedelta(days=30 * month_offset)
                gross = total_salary
                insurance_amount = int(gross * 0.09)
                tax = int(gross * 0.03)
                deduction = insurance_amount + tax
                payment = SalaryPayment(
                    employee_id=employee.id,
                    payment_date=payment_date.strftime('%Y-%m-%d'),
                    payment_period=f"{payment_date.year}년 {payment_date.month}월",
                    base_salary=base_salary,
                    allowances=position_allowance + meal_allowance + transportation_allowance,
                    gross_pay=gross,
                    insurance=insurance_amount,
                    income_tax=tax,
                    total_deduction=deduction,
                    net_pay=gross - deduction
                )
                db.session.add(payment)

            # 보험 정보
            insurance = Insurance(
                employee_id=employee.id,
                national_pension=True,
                health_insurance=True,
                employment_insurance=True,
                industrial_accident=True,
                national_pension_rate=4.5,
                health_insurance_rate=3.545,
                long_term_care_rate=0.9182,
                employment_insurance_rate=0.9
            )
            db.session.add(insurance)

            # 복리후생 정보
            hire_years = (date.today() - datetime.strptime(hire_date, '%Y-%m-%d').date()).days // 365
            annual_leave = min(15 + hire_years, 25)
            benefit = Benefit(
                employee_id=employee.id,
                year=current_year,
                annual_leave_granted=annual_leave,
                annual_leave_used=random.randint(0, annual_leave // 2),
                annual_leave_remaining=annual_leave - random.randint(0, annual_leave // 2),
                severance_type='퇴직연금',
                severance_method='DB형'
            )
            db.session.add(benefit)

            # 계약 정보
            contract = Contract(
                employee_id=employee.id,
                contract_type='정규직',
                contract_date=hire_date,
                contract_period='무기계약',
                employee_type='정규직',
                work_type='주5일'
            )
            db.session.add(contract)

            # employee_sub 계정 생성
            sub_username = f"emp_{company_idx + 1}_{i + 1}"
            sub_email = f"emp{company_idx + 1}_{i + 1}@test.com"

            existing_user = User.query.filter(
                (User.username == sub_username) | (User.email == sub_email)
            ).first()

            if not existing_user:
                sub_user = User(
                    username=sub_username,
                    email=sub_email,
                    role='employee',
                    account_type='employee_sub',
                    company_id=company.id,
                    employee_id=employee.id,
                    is_active=True
                )
                sub_user.set_password('emp1234')
                db.session.add(sub_user)

            created_employees.append(employee)
            print(f"    + {name} ({employee.employee_number}) - 모든 관련 데이터 생성")
            emp_index += 1

    if not dry_run and created_employees:
        db.session.commit()

    print(f"\n  총 {len(created_employees)}명 직원 생성 완료")
    return created_employees


# ============================================================
# 개인 계정 데이터 생성
# ============================================================

def create_personal_accounts(count=20, dry_run=False):
    """개인 계정 20명 생성"""
    print("\n[Phase 3] 개인 계정 데이터 생성")
    print("-" * 50)

    created_profiles = []

    for i in range(1, count + 1):
        gender = '남' if random.random() < 0.5 else '여'
        last_name = random.choice(KOREAN_LAST_NAMES)
        first_name = random.choice(
            KOREAN_FIRST_NAMES_MALE if gender == '남' else KOREAN_FIRST_NAMES_FEMALE
        )
        name = f"{last_name}{first_name}"
        birth_date = generate_birth_date(22, 45)

        username = f"personal{i}"
        email = f"personal{i}@test.com"

        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            print(f"  [SKIP] {username} - 이미 존재")
            if existing.personal_profile:
                created_profiles.append(existing.personal_profile)
            continue

        if dry_run:
            print(f"  [DRY] {name} ({username}) 생성 예정")
            continue

        # User 생성
        user = User(
            username=username,
            email=email,
            role='employee',
            account_type='personal',
            is_active=True
        )
        user.set_password('personal1234')
        db.session.add(user)
        db.session.flush()

        # PersonalProfile 생성
        profile = PersonalProfile(
            user_id=user.id,
            name=name,
            english_name=f"{first_name} {last_name}",
            birth_date=birth_date,
            lunar_birth=random.choice([True, False]),
            gender=gender,
            mobile_phone=generate_phone(),
            home_phone=generate_home_phone() if random.random() > 0.5 else None,
            email=email,
            postal_code=generate_postal_code(),
            address=generate_address(),
            detailed_address=f"개인아파트 {random.randint(100, 999)}호",
            nationality='대한민국',
            blood_type=random.choice(['A', 'B', 'O', 'AB']),
            religion=random.choice(['무교', '기독교', '불교', '천주교', None]),
            hobby=random.choice(['독서', '운동', '여행', '음악감상', '요리', None]),
            specialty=random.choice(['프로그래밍', '기획', '디자인', '영업', None]),
            marital_status=random.choice(['single', 'married']),
            is_public=random.choice([True, False]),
            emergency_contact=generate_phone(),
            emergency_relation=random.choice(['배우자', '부모', '형제']),
            actual_postal_code=generate_postal_code(),
            actual_address=generate_address(),
            actual_detailed_address=f"실거주 {random.randint(100, 999)}호"
        )
        db.session.add(profile)
        db.session.flush()

        # 학력 (1-3개)
        for edu_idx in range(random.randint(1, 3)):
            if edu_idx == 0:
                edu = PersonalEducation(
                    profile_id=profile.id,
                    school_type='고등학교',
                    school_name=random.choice(HIGH_SCHOOL_NAMES),
                    graduation_date=f"{int(birth_date[:4]) + 18}-02-28",
                    graduation_status='졸업'
                )
            else:
                edu = PersonalEducation(
                    profile_id=profile.id,
                    school_type=random.choice(['대학교', '전문대학', '대학원']),
                    school_name=random.choice(SCHOOL_NAMES),
                    major=random.choice(MAJORS),
                    degree=random.choice(['학사', '석사', '박사', '전문학사']),
                    graduation_date=f"{int(birth_date[:4]) + 22 + (edu_idx * 4)}-02-28",
                    graduation_status='졸업'
                )
            db.session.add(edu)

        # 경력 (0-4개)
        for _ in range(random.randint(0, 4)):
            start_year = random.randint(2015, 2022)
            career = PersonalCareer(
                profile_id=profile.id,
                company_name=f"(주){random.choice(['테스트', '샘플', '예시', '이전'])}기업",
                department=random.choice(DEPARTMENTS),
                position=random.choice(POSITIONS),
                start_date=f"{start_year}-{random.randint(1, 12):02d}-01",
                end_date=f"{start_year + random.randint(1, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" if random.random() > 0.2 else None,
                is_current=random.random() > 0.8
            )
            db.session.add(career)

        # 자격증 (0-4개)
        for _ in range(random.randint(0, 4)):
            cert = PersonalCertificate(
                profile_id=profile.id,
                certificate_name=random.choice(CERTIFICATE_NAMES),
                issuing_organization=random.choice(ISSUING_ORGS),
                acquisition_date=generate_past_date(1, 5)
            )
            db.session.add(cert)

        # 어학 (0-3개)
        for _ in range(random.randint(0, 3)):
            lang_name = random.choice(LANGUAGES)
            lang = PersonalLanguage(
                profile_id=profile.id,
                language_name=lang_name,
                exam_name=random.choice(LANGUAGE_EXAMS.get(lang_name, ['기타'])),
                score=str(random.randint(700, 990)) if lang_name == '영어' else random.choice(['N1', 'N2', '고급', '중급']),
                level=random.choice(['상', '중', '하']),
                acquisition_date=generate_past_date(1, 3)
            )
            db.session.add(lang)

        # 병역 (남성만)
        if gender == '남':
            military = PersonalMilitaryService(
                profile_id=profile.id,
                military_status=random.choice(['군필', '면제']),
                service_type=random.choice(SERVICE_TYPES) if random.random() > 0.2 else None,
                branch=random.choice(BRANCHES),
                rank=random.choice(RANKS)
            )
            db.session.add(military)

        created_profiles.append(profile)
        print(f"  + {name} ({username}) - 모든 관련 데이터 생성")

    if not dry_run and created_profiles:
        db.session.commit()

    print(f"\n  총 {len(created_profiles)}명 개인 계정 생성 완료")
    return created_profiles


# ============================================================
# 개인-법인 계약 생성
# ============================================================

def create_person_corporate_contracts(companies, dry_run=False):
    """개인-법인 계약 생성 (일부 개인 계정을 법인과 연결)"""
    print("\n[Phase 4] 개인-법인 계약 생성")
    print("-" * 50)

    if not companies:
        print("  [SKIP] 법인이 없습니다.")
        return []

    personal_users = User.query.filter_by(account_type='personal').limit(5).all()
    created_contracts = []

    for idx, user in enumerate(personal_users):
        company = companies[idx % len(companies)]

        existing = PersonCorporateContract.query.filter_by(
            person_user_id=user.id,
            company_id=company.id
        ).first()

        if existing:
            print(f"  [SKIP] {user.username} <-> {company.name} - 이미 존재")
            continue

        if dry_run:
            print(f"  [DRY] {user.username} <-> {company.name} 계약 생성 예정")
            continue

        contract = PersonCorporateContract(
            person_user_id=user.id,
            company_id=company.id,
            status='approved',
            contract_type='employment',
            contract_start_date=date.today() - timedelta(days=random.randint(30, 365)),
            position=random.choice(POSITIONS),
            department=random.choice(DEPARTMENTS),
            employee_number=f"EXT-{datetime.now().year}-{idx + 1:04d}",
            requested_by='company',
            approved_at=datetime.utcnow()
        )
        db.session.add(contract)
        db.session.flush()

        # DataSharingSettings 생성
        sharing = DataSharingSettings(
            contract_id=contract.id,
            share_basic_info=True,
            share_contact=True,
            share_education=random.choice([True, False]),
            share_career=random.choice([True, False]),
            share_certificates=random.choice([True, False]),
            share_languages=random.choice([True, False]),
            share_military=False,
            is_realtime_sync=random.choice([True, False])
        )
        db.session.add(sharing)

        created_contracts.append(contract)
        print(f"  + {user.username} <-> {company.name} 계약 생성")

    if not dry_run and created_contracts:
        db.session.commit()

    print(f"\n  총 {len(created_contracts)}개 계약 생성 완료")
    return created_contracts


# ============================================================
# 기존 테스트 데이터 삭제
# ============================================================

def clear_test_data(dry_run=False):
    """테스트 데이터 삭제"""
    print("\n[Phase 0] 기존 테스트 데이터 삭제")
    print("-" * 50)

    if dry_run:
        print("  [DRY] 삭제 작업 미리보기")
        return

    # 테스트 계정 삭제 (personal*, corp_*, emp_*)
    test_users = User.query.filter(
        (User.username.like('personal%')) |
        (User.username.like('corp_%')) |
        (User.username.like('emp_%'))
    ).all()

    deleted_users = 0
    deleted_employees = 0

    for user in test_users:
        if user.personal_profile:
            db.session.delete(user.personal_profile)
        if user.employee_id:
            emp = Employee.query.get(user.employee_id)
            if emp and emp.employee_number and emp.employee_number.startswith('EMP-'):
                db.session.delete(emp)
                deleted_employees += 1
        db.session.delete(user)
        deleted_users += 1

    # 테스트 법인 삭제
    test_companies = Company.query.filter(
        Company.business_number.in_(['1234567890', '2345678901', '3456789012'])
    ).all()

    deleted_companies = 0
    for company in test_companies:
        # 관련 조직 삭제
        if company.root_organization:
            children = Organization.query.filter_by(parent_id=company.root_organization_id).all()
            for child in children:
                db.session.delete(child)
            db.session.delete(company.root_organization)
        db.session.delete(company)
        deleted_companies += 1

    db.session.commit()
    print(f"  삭제 완료: User {deleted_users}명, Employee {deleted_employees}명, Company {deleted_companies}개")


# ============================================================
# 상태 리포트
# ============================================================

def show_status():
    """현재 데이터 상태 출력"""
    print("\n" + "=" * 70)
    print("데이터베이스 현황 리포트")
    print("=" * 70)

    # Company 현황
    companies = Company.query.all()
    print(f"\n[법인] 총 {len(companies)}개")
    for company in companies:
        emp_count = 0
        if company.root_organization_id:
            emp_count = Employee.query.filter_by(
                organization_id=company.root_organization_id
            ).count()
        print(f"  - {company.name} (ID: {company.id}): 직원 {emp_count}명")

    # User 현황
    personal = User.query.filter_by(account_type='personal').count()
    corporate = User.query.filter_by(account_type='corporate').count()
    employee_sub = User.query.filter_by(account_type='employee_sub').count()

    print(f"\n[계정] 총 {personal + corporate + employee_sub}개")
    print(f"  - Personal: {personal}개")
    print(f"  - Corporate: {corporate}개")
    print(f"  - Employee Sub: {employee_sub}개")

    # Employee 현황
    total_emp = Employee.query.count()
    print(f"\n[직원] 총 {total_emp}명")

    # 관련 데이터 현황
    print(f"\n[직원 관련 데이터]")
    print(f"  - 학력: {Education.query.count()}건")
    print(f"  - 경력: {Career.query.count()}건")
    print(f"  - 자격증: {Certificate.query.count()}건")
    print(f"  - 어학: {Language.query.count()}건")
    print(f"  - 가족: {FamilyMember.query.count()}건")
    print(f"  - 병역: {MilitaryService.query.count()}건")
    print(f"  - 급여: {Salary.query.count()}건")
    print(f"  - 연봉이력: {SalaryHistory.query.count()}건")
    print(f"  - 급여지급: {SalaryPayment.query.count()}건")
    print(f"  - 보험: {Insurance.query.count()}건")
    print(f"  - 복리후생: {Benefit.query.count()}건")
    print(f"  - 계약: {Contract.query.count()}건")
    print(f"  - 발령: {Promotion.query.count()}건")
    print(f"  - 평가: {Evaluation.query.count()}건")
    print(f"  - 교육: {Training.query.count()}건")
    print(f"  - 근태: {Attendance.query.count()}건")
    print(f"  - 프로젝트: {HrProject.query.count()}건")
    print(f"  - 수상: {Award.query.count()}건")
    print(f"  - 자산: {Asset.query.count()}건")

    # PersonalProfile 현황
    total_profile = PersonalProfile.query.count()
    print(f"\n[개인 프로필] 총 {total_profile}개")
    print(f"  - 학력: {PersonalEducation.query.count()}건")
    print(f"  - 경력: {PersonalCareer.query.count()}건")
    print(f"  - 자격증: {PersonalCertificate.query.count()}건")
    print(f"  - 어학: {PersonalLanguage.query.count()}건")
    print(f"  - 병역: {PersonalMilitaryService.query.count()}건")

    # 계약 현황
    contracts = PersonCorporateContract.query.count()
    print(f"\n[개인-법인 계약] 총 {contracts}건")

    print("\n" + "=" * 70)


# ============================================================
# 메인 함수
# ============================================================

def main():
    """메인 실행 함수"""
    dry_run = '--dry-run' in sys.argv
    clear = '--clear' in sys.argv
    status_only = '--status' in sys.argv

    print("=" * 70)
    print("포괄적 테스트 데이터 생성 스크립트")
    print("법인 3개, 직원 20명, 개인 20명 + 모든 관련 테이블")
    print("=" * 70)

    if dry_run:
        print("[DRY RUN 모드 - 실제 데이터 변경 없음]")

    app = create_app()

    with app.app_context():
        if status_only:
            show_status()
            return

        # 기존 데이터 삭제 (--clear 옵션)
        if clear:
            clear_test_data(dry_run)

        # 실행 전 상태
        print("\n[실행 전 상태]")
        show_status()

        # 1. 법인 생성
        companies = create_companies(dry_run)

        # 2. 직원 생성 (모든 관련 데이터 포함)
        employees = create_employees(companies, count=20, dry_run=dry_run)

        # 3. 개인 계정 생성
        profiles = create_personal_accounts(count=20, dry_run=dry_run)

        # 4. 개인-법인 계약 생성
        contracts = create_person_corporate_contracts(companies, dry_run=dry_run)

        # 실행 후 상태
        if not dry_run:
            print("\n[실행 후 상태]")
            show_status()

        print("\n[완료]")
        if dry_run:
            print("DRY RUN 모드였습니다. 실제 실행하려면 --dry-run 없이 실행하세요.")
        else:
            print("모든 테스트 데이터가 생성되었습니다.")

        print("\n" + "=" * 70)
        print("테스트 계정 정보")
        print("=" * 70)
        print("\n[법인 계정]")
        print("  - corp1@test.com / corp1234  (테크노소프트, admin)")
        print("  - corp2@test.com / corp1234  (디지털웨이브, admin)")
        print("  - corp3@test.com / corp1234  (스마트솔루션즈, admin)")
        print("\n[직원 계정]")
        print("  - emp1_1@test.com ~ emp1_7@test.com / emp1234  (테크노소프트)")
        print("  - emp2_1@test.com ~ emp2_7@test.com / emp1234  (디지털웨이브)")
        print("  - emp3_1@test.com ~ emp3_6@test.com / emp1234  (스마트솔루션즈)")
        print("\n[개인 계정]")
        print("  - personal1@test.com ~ personal20@test.com / personal1234")
        print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
