"""
개인 계정 5명 샘플 생성 스크립트

Phase 4 통합 프로필 구조를 사용하여 Personal Account 5명의 완전한 샘플 데이터를 생성합니다.

무결성 보장:
- User: account_type='personal', company_id=NULL, employee_id=NULL, parent_user_id=NULL
- Profile: user_id 연결 (1:1)
- 이력 정보: 모두 profile_id 사용, employee_id=NULL

실행 방법:
    python scripts/generate_personal_sample.py
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
from app.domains.employee.models import (
    Career,
    Certificate,
    Education,
    FamilyMember,
    Language,
    MilitaryService,
    Profile,
)
from app.domains.user.models import User


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

DEPARTMENTS = ['개발팀', '기획팀', '영업팀', '마케팅팀', '인사팀', '재무팀', '경영지원팀', 'R&D팀']
POSITIONS = ['사원', '주임', '대리', '과장', '차장', '부장', '이사', '상무']

SERVICE_TYPES = ['육군', '해군', '공군', '해병대', '의무경찰', '사회복무요원', '산업기능요원']
RANKS = ['이병', '일병', '상병', '병장', '하사', '중사']
BRANCHES = ['육군', '해군', '공군', '해병대']


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


def generate_email(name, domain='test.com'):
    """이메일 생성"""
    import unicodedata
    romanized = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    ).replace(' ', '').lower()
    if not romanized or not romanized.isascii():
        romanized = f"user{random.randint(1000, 9999)}"
    return f"{romanized}@{domain}"


def generate_birth_date(min_age=22, max_age=45):
    """생년월일 생성"""
    today = date.today()
    age = random.randint(min_age, max_age)
    birth_year = today.year - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"


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


# ============================================================
# Personal Account 생성
# ============================================================

def create_personal_accounts(count=5):
    """개인 계정 생성 (무결성 보장)"""
    print("\n[1] Personal Account 생성")
    print("-" * 50)
    
    created_accounts = []
    
    for i in range(1, count + 1):
        gender = '남' if random.random() < 0.5 else '여'
        last_name = random.choice(KOREAN_LAST_NAMES)
        first_name = random.choice(
            KOREAN_FIRST_NAMES_MALE if gender == '남' else KOREAN_FIRST_NAMES_FEMALE
        )
        name = f"{last_name}{first_name}"
        birth_date = generate_birth_date(22, 45)
        
        username = f"personal_user{i}"
        email = f"personal{i}@test.com"
        
        # 중복 확인
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            print(f"  [SKIP] {username} - 이미 존재")
            continue
        
        # User 생성 (무결성: account_type='personal', company_id=NULL, employee_id=NULL, parent_user_id=NULL)
        user = User(
            username=username,
            email=email,
            role=User.ROLE_EMPLOYEE,
            account_type=User.ACCOUNT_PERSONAL,
            company_id=None,  # 무결성: NULL 필수
            employee_id=None,  # 무결성: NULL 필수
            parent_user_id=None,  # 무결성: NULL 필수
            is_active=True
        )
        user.set_password('personal1234')
        db.session.add(user)
        db.session.flush()
        
        # Profile 생성 (user_id 연결, 1:1)
        profile = Profile(
            user_id=user.id,  # 무결성: 필수
            name=name,
            english_name=f"{first_name} {last_name}",
            birth_date=birth_date,
            lunar_birth=random.choice([True, False]),
            gender=gender,
            mobile_phone=generate_phone(),
            home_phone=generate_home_phone() if random.random() > 0.5 else None,
            email=email,
            address=generate_address(),
            detailed_address=f"아파트 {random.randint(100, 999)}호",
            postal_code=generate_postal_code(),
            nationality='대한민국',
            marital_status=random.choice(['single', 'married', 'divorced']),
            hobby=random.choice(['독서', '운동', '여행', '음악감상', '요리', None]),
            specialty=random.choice(['프로그래밍', '기획', '디자인', '영업', None]),
            is_public=random.choice([True, False]),
            emergency_contact=generate_phone(),
            emergency_relation=random.choice(['배우자', '부모', '형제']),
            actual_postal_code=generate_postal_code(),
            actual_address=generate_address(),
            actual_detailed_address=f"실거주 아파트 {random.randint(100, 999)}호"
        )
        db.session.add(profile)
        db.session.flush()
        
        # 이력 정보 생성 (모두 profile_id 사용, employee_id=NULL)
        birth_year = int(birth_date[:4])
        
        # 학력 (고등학교 + 대학교, 선택적으로 대학원)
        edu1 = Education(
            profile_id=profile.id,  # profile_id 사용
            employee_id=None,  # employee_id는 NULL
            school_type='고등학교',
            school_name=random.choice(HIGH_SCHOOL_NAMES),
            graduation_date=f"{birth_year + 18}-02-28",
            graduation_status='졸업'
        )
        db.session.add(edu1)
        
        edu2 = Education(
            profile_id=profile.id,  # profile_id 사용
            employee_id=None,  # employee_id는 NULL
            school_type='대학교',
            school_name=random.choice(SCHOOL_NAMES),
            major=random.choice(MAJORS),
            degree='학사',
            admission_date=f"{birth_year + 18}-03-01",
            graduation_date=f"{birth_year + 22}-02-28",
            graduation_status='졸업',
            location=random.choice(['서울', '경기', '부산', '대전'])
        )
        db.session.add(edu2)
        
        # 대학원 (30% 확률)
        if random.random() < 0.3:
            edu3 = Education(
                profile_id=profile.id,
                employee_id=None,
                school_type='대학원',
                school_name=random.choice(SCHOOL_NAMES) + ' 대학원',
                major=random.choice(MAJORS),
                degree='석사',
                admission_date=f"{birth_year + 22}-03-01",
                graduation_date=f"{birth_year + 24}-02-28",
                graduation_status='졸업',
                location=random.choice(['서울', '경기'])
            )
            db.session.add(edu3)
        
        # 경력 (0-3개)
        for _ in range(random.randint(0, 3)):
            start_year = random.randint(birth_year + 22, 2020)
            career = Career(
                profile_id=profile.id,  # profile_id 사용
                employee_id=None,  # employee_id는 NULL
                company_name=f"(주){random.choice(['테스트', '샘플', '예시', '이전'])}기업",
                department=random.choice(DEPARTMENTS),
                position=random.choice(POSITIONS[:4]),  # 사원~과장
                job_description=f"{random.choice(['서비스 개발', '프로젝트 관리', '영업 활동', '마케팅'])} 담당",
                start_date=f"{start_year}-{random.randint(1, 12):02d}-01",
                end_date=f"{start_year + random.randint(1, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" if random.random() > 0.3 else None,
                resignation_reason=random.choice(['이직', '계약만료', '개인사정', None]) if random.random() > 0.5 else None,
                is_current=random.random() > 0.7
            )
            db.session.add(career)
        
        # 자격증 (0-3개)
        for _ in range(random.randint(0, 3)):
            cert = Certificate(
                profile_id=profile.id,  # profile_id 사용
                employee_id=None,  # employee_id는 NULL
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
                profile_id=profile.id,  # profile_id 사용
                employee_id=None,  # employee_id는 NULL
                language_name=lang_name,
                exam_name=random.choice(LANGUAGE_EXAMS.get(lang_name, ['기타'])),
                score=str(random.randint(700, 990)) if lang_name == '영어' else random.choice(['N1', 'N2', '고급', '중급']),
                level=random.choice(['상', '중', '하']),
                acquisition_date=generate_past_date(1, 3),
                expiry_date=f"{datetime.now().year + 2}-12-31" if 'TOEIC' in lang_name or 'TOEFL' in lang_name else None
            )
            db.session.add(lang)
        
        # 가족 (부모 필수, 배우자/자녀 선택)
        # 부
        family_father = FamilyMember(
            profile_id=profile.id,  # profile_id 사용
            employee_id=None,  # employee_id는 NULL
            relation='부',
            name=f"{random.choice(KOREAN_LAST_NAMES)}{random.choice(['진호', '성철', '동수', '상현'])}",
            birth_date=generate_birth_date(50, 75),
            occupation=random.choice(['회사원', '공무원', '자영업', '무직']),
            contact=generate_phone() if random.random() > 0.3 else None,
            is_cohabitant=random.choice([True, False]),
            is_dependent=random.choice([True, False])
        )
        db.session.add(family_father)
        
        # 모
        family_mother = FamilyMember(
            profile_id=profile.id,  # profile_id 사용
            employee_id=None,  # employee_id는 NULL
            relation='모',
            name=f"{random.choice(KOREAN_LAST_NAMES)}{random.choice(['정숙', '미자', '영희', '순자'])}",
            birth_date=generate_birth_date(48, 73),
            occupation=random.choice(['회사원', '공무원', '자영업', '주부', '무직']),
            contact=generate_phone() if random.random() > 0.3 else None,
            is_cohabitant=random.choice([True, False]),
            is_dependent=random.choice([True, False])
        )
        db.session.add(family_mother)
        
        # 배우자 (50% 확률)
        if random.random() < 0.5:
            spouse_gender = '여' if gender == '남' else '남'
            spouse_name = f"{random.choice(KOREAN_LAST_NAMES)}{random.choice(
                KOREAN_FIRST_NAMES_FEMALE if spouse_gender == '여' else KOREAN_FIRST_NAMES_MALE
            )}"
            family_spouse = FamilyMember(
                profile_id=profile.id,  # profile_id 사용
                employee_id=None,  # employee_id는 NULL
                relation='배우자',
                name=spouse_name,
                birth_date=generate_birth_date(22, 45),
                occupation=random.choice(['회사원', '공무원', '자영업', '주부', '학생', '무직']),
                contact=generate_phone(),
                is_cohabitant=True,
                is_dependent=False
            )
            db.session.add(family_spouse)
            
            # 자녀 (배우자가 있으면 30% 확률)
            if random.random() < 0.3:
                child_name = f"{random.choice(KOREAN_LAST_NAMES)}{random.choice(['서준', '하윤', '도윤', '시우'])}"
                family_child = FamilyMember(
                    profile_id=profile.id,  # profile_id 사용
                    employee_id=None,  # employee_id는 NULL
                    relation='자녀',
                    name=child_name,
                    birth_date=generate_birth_date(1, 15),
                    occupation='학생',
                    contact=None,
                    is_cohabitant=True,
                    is_dependent=True
                )
                db.session.add(family_child)
        
        # 병역 (남성만, 선택)
        if gender == '남':
            if random.random() < 0.8:  # 80% 확률로 군필
                military = MilitaryService(
                    profile_id=profile.id,  # profile_id 사용
                    employee_id=None,  # employee_id는 NULL
                    military_status='군필',
                    service_type=random.choice(SERVICE_TYPES[:4]),  # 육군, 해군, 공군, 해병대
                    branch=random.choice(BRANCHES),
                    rank=random.choice(RANKS),
                    enlistment_date=f"{birth_year + 20}-{random.randint(1, 12):02d}-01",
                    discharge_date=f"{birth_year + 22}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    discharge_reason='만기전역'
                )
            else:  # 20% 확률로 면제
                military = MilitaryService(
                    profile_id=profile.id,  # profile_id 사용
                    employee_id=None,  # employee_id는 NULL
                    military_status='면제',
                    service_type=None,
                    branch=None,
                    rank=None,
                    enlistment_date=None,
                    discharge_date=None,
                    discharge_reason=None,
                    exemption_reason='신체등급'
                )
            db.session.add(military)
        
        created_accounts.append({
            'user': user,
            'profile': profile,
            'username': username,
            'email': email,
            'password': 'personal1234',
            'name': name
        })
        
        print(f"  + {name} ({username}) - User + Profile + 이력 생성")
    
    db.session.commit()
    print(f"\n  총 {len(created_accounts)}개 Personal Account 생성 완료")
    return created_accounts


# ============================================================
# 무결성 검증
# ============================================================

def verify_integrity():
    """무결성 검증"""
    print("\n[2] 무결성 검증")
    print("-" * 50)
    
    errors = []
    
    # Personal Account 제약 조건 확인
    personal_users = User.query.filter_by(account_type=User.ACCOUNT_PERSONAL).all()
    
    for user in personal_users:
        # company_id 확인
        if user.company_id is not None:
            errors.append(f"User {user.id} ({user.username}): company_id should be NULL, got {user.company_id}")
        
        # employee_id 확인
        if user.employee_id is not None:
            errors.append(f"User {user.id} ({user.username}): employee_id should be NULL, got {user.employee_id}")
        
        # parent_user_id 확인
        if user.parent_user_id is not None:
            errors.append(f"User {user.id} ({user.username}): parent_user_id should be NULL, got {user.parent_user_id}")
        
        # Profile 연결 확인
        profile = Profile.query.filter_by(user_id=user.id).first()
        if not profile:
            errors.append(f"User {user.id} ({user.username}): Profile missing")
        else:
            # 이력 정보 profile_id 연결 확인
            educations = Education.query.filter_by(profile_id=profile.id).all()
            for edu in educations:
                if edu.employee_id is not None:
                    errors.append(f"Education {edu.id}: employee_id should be NULL for personal account")
            
            careers = Career.query.filter_by(profile_id=profile.id).all()
            for career in careers:
                if career.employee_id is not None:
                    errors.append(f"Career {career.id}: employee_id should be NULL for personal account")
            
            certificates = Certificate.query.filter_by(profile_id=profile.id).all()
            for cert in certificates:
                if cert.employee_id is not None:
                    errors.append(f"Certificate {cert.id}: employee_id should be NULL for personal account")
            
            languages = Language.query.filter_by(profile_id=profile.id).all()
            for lang in languages:
                if lang.employee_id is not None:
                    errors.append(f"Language {lang.id}: employee_id should be NULL for personal account")
            
            family_members = FamilyMember.query.filter_by(profile_id=profile.id).all()
            for family in family_members:
                if family.employee_id is not None:
                    errors.append(f"FamilyMember {family.id}: employee_id should be NULL for personal account")
            
            military = MilitaryService.query.filter_by(profile_id=profile.id).first()
            if military and military.employee_id is not None:
                errors.append(f"MilitaryService {military.id}: employee_id should be NULL for personal account")
    
    if errors:
        print("  [ERROR] 무결성 위반 발견:")
        for error in errors:
            print(f"    - {error}")
        return False
    else:
        print("  [OK] 모든 무결성 검증 통과")
        return True


# ============================================================
# 통계 출력
# ============================================================

def show_statistics():
    """생성된 데이터 통계 출력"""
    print("\n[3] 생성된 데이터 통계")
    print("-" * 50)
    
    personal_count = User.query.filter_by(account_type=User.ACCOUNT_PERSONAL).count()
    profile_count = Profile.query.filter(Profile.user_id.isnot(None)).count()
    
    print(f"  - Personal Account: {personal_count}개")
    print(f"  - Profile: {profile_count}개")
    
    # 이력 정보 통계
    educations = Education.query.join(Profile).filter(Profile.user_id.isnot(None)).count()
    careers = Career.query.join(Profile).filter(Profile.user_id.isnot(None)).count()
    certificates = Certificate.query.join(Profile).filter(Profile.user_id.isnot(None)).count()
    languages = Language.query.join(Profile).filter(Profile.user_id.isnot(None)).count()
    family_members = FamilyMember.query.join(Profile).filter(Profile.user_id.isnot(None)).count()
    military_services = MilitaryService.query.join(Profile).filter(Profile.user_id.isnot(None)).count()
    
    print(f"\n  [이력 정보]")
    print(f"    - 학력: {educations}건")
    print(f"    - 경력: {careers}건")
    print(f"    - 자격증: {certificates}건")
    print(f"    - 어학: {languages}건")
    print(f"    - 가족: {family_members}건")
    print(f"    - 병역: {military_services}건")


# ============================================================
# 메인 실행
# ============================================================

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("개인 계정 5명 샘플 생성 스크립트")
    print("Phase 4 통합 프로필 구조 사용")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        # 1. Personal Account 생성
        created_accounts = create_personal_accounts(count=5)
        
        # 2. 무결성 검증
        integrity_ok = verify_integrity()
        
        # 3. 통계 출력
        show_statistics()
        
        # 4. 생성된 계정 정보 출력
        print("\n[4] 생성된 계정 정보")
        print("-" * 50)
        for acc in created_accounts:
            print(f"  - {acc['name']} ({acc['username']})")
            print(f"    Email: {acc['email']}")
            print(f"    Password: {acc['password']}")
        
        print("\n" + "=" * 70)
        if integrity_ok:
            print("생성 완료! 모든 무결성 검증을 통과했습니다.")
        else:
            print("생성 완료! 단, 무결성 검증에서 오류가 발견되었습니다.")
        print("=" * 70)


if __name__ == '__main__':
    main()


