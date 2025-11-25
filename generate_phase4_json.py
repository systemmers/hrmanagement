"""
Phase 4: 부가 기능 JSON 파일 생성 스크립트
P4-T01: insurances.json 생성 (4대보험)
P4-T02: projects.json 생성 (유사사업참여경력)
P4-T03: awards.json 생성 (수상내역)
P4-T04: assets.json 생성 (비품지급)
"""
import json
import random
from datetime import datetime, timedelta

# 직원 기본 정보 로드
with open('data/employees.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

# P4-T01: insurances.json 생성 (4대보험)
insurances = []
for emp in employees:
    insurances.append({
        "id": emp['id'],
        "employee_id": emp['id'],
        "national_pension": True,
        "health_insurance": True,
        "employment_insurance": True,
        "industrial_accident": True,
        "national_pension_rate": 4.5,
        "health_insurance_rate": 3.545,
        "long_term_care_rate": 0.9182,
        "employment_insurance_rate": 0.9
    })

with open('data/insurances.json', 'w', encoding='utf-8') as f:
    json.dump(insurances, f, ensure_ascii=False, indent=2)

print(f"P4-T01: insurances.json 생성 완료 ({len(insurances)}개 레코드)")

# P4-T02: projects.json 생성 (유사사업참여경력)
projects = []
project_id = 1
project_names = [
    ("스마트시티 플랫폼 구축", "서울특별시"),
    ("공공데이터 포털 개선", "행정안전부"),
    ("클라우드 마이그레이션", "삼성SDS"),
    ("AI 챗봇 시스템 구축", "KB국민은행"),
    ("ERP 시스템 고도화", "LG전자"),
    ("빅데이터 분석 플랫폼", "SK텔레콤"),
    ("모바일 뱅킹 앱 개발", "신한은행"),
    ("IoT 관제 시스템", "한국전력공사"),
    ("전자상거래 플랫폼", "CJ대한통운"),
    ("의료정보시스템 구축", "서울대병원")
]
roles = ["PM", "PL", "개발자", "설계자", "QA", "아키텍트"]
duties = ["프로젝트 총괄", "개발 리드", "백엔드 개발", "프론트엔드 개발", "품질관리", "시스템 설계"]

# 일부 직원에게만 프로젝트 경력 부여 (40% 확률)
for emp in employees:
    if random.random() < 0.4:
        num_projects = random.randint(1, 3)
        for _ in range(num_projects):
            project_name, client = random.choice(project_names)
            start_year = random.randint(2018, 2023)
            start_month = random.randint(1, 6)
            duration = random.randint(6, 18)
            end_date = datetime(start_year, start_month, 1) + timedelta(days=duration * 30)

            projects.append({
                "id": project_id,
                "employee_id": emp['id'],
                "project_name": project_name,
                "start_date": f"{start_year}-{start_month:02d}",
                "end_date": end_date.strftime("%Y-%m"),
                "duration": f"{duration}개월",
                "role": random.choice(roles),
                "duty": random.choice(duties),
                "client": client
            })
            project_id += 1

with open('data/projects.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

print(f"P4-T02: projects.json 생성 완료 ({len(projects)}개 레코드)")

# P4-T03: awards.json 생성 (수상내역)
awards = []
award_id = 1
award_names = [
    ("우수사원상", "인사팀"),
    ("혁신상", "경영지원팀"),
    ("베스트 프로젝트상", "개발팀"),
    ("고객만족 우수상", "영업팀"),
    ("기술혁신상", "기술연구소"),
    ("올해의 신입사원상", "인사팀"),
    ("팀워크상", "경영지원팀"),
    ("최우수 성과상", "경영기획팀")
]

# 일부 직원에게만 수상 내역 부여 (25% 확률)
for emp in employees:
    if random.random() < 0.25:
        num_awards = random.randint(1, 2)
        for _ in range(num_awards):
            award_name, institution = random.choice(award_names)
            award_year = random.randint(2021, 2024)
            award_month = random.randint(1, 12)

            notes = ["상반기 실적 우수", "하반기 실적 우수", "연간 최우수", "분기별 목표 달성", None]

            awards.append({
                "id": award_id,
                "employee_id": emp['id'],
                "award_date": f"{award_year}-{award_month:02d}-01",
                "award_name": award_name,
                "institution": institution,
                "note": random.choice(notes)
            })
            award_id += 1

with open('data/awards.json', 'w', encoding='utf-8') as f:
    json.dump(awards, f, ensure_ascii=False, indent=2)

print(f"P4-T03: awards.json 생성 완료 ({len(awards)}개 레코드)")

# P4-T04: assets.json 생성 (비품지급)
assets = []
asset_id = 1
asset_items = [
    ("노트북", ["MacBook Pro 14", "MacBook Pro 16", "Dell XPS 15", "ThinkPad X1 Carbon", "LG gram 17"]),
    ("모니터", ["Dell U2722D 27인치", "LG 27UK850 27인치", "삼성 C34F791 34인치"]),
    ("키보드", ["Apple Magic Keyboard", "로지텍 MX Keys", "레오폴드 FC750R"]),
    ("마우스", ["Apple Magic Mouse", "로지텍 MX Master 3", "로지텍 MX Anywhere 3"]),
    ("헤드셋", ["Jabra Evolve2 75", "Sony WH-1000XM4", "Bose 700"]),
    ("사무용품", ["책상 세트", "의자", "모니터 암"])
]
statuses = ["사용중", "사용중", "사용중", "반납", "분실"]

# 모든 직원에게 기본 비품 지급 (노트북)
for emp in employees:
    hire_date = emp.get('hireDate', '2024-01-01')

    # 노트북 지급 (모든 직원)
    laptop_model = random.choice(asset_items[0][1])
    serial_prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    serial_number = f"{serial_prefix}{random.randint(100000, 999999)}"

    assets.append({
        "id": asset_id,
        "employee_id": emp['id'],
        "issue_date": hire_date,
        "item_name": "노트북",
        "model": laptop_model,
        "serial_number": serial_number,
        "status": "사용중",
        "note": None
    })
    asset_id += 1

    # 추가 비품 지급 (50% 확률로 1-2개 추가)
    if random.random() < 0.5:
        additional_items = random.sample(asset_items[1:], k=random.randint(1, 2))
        for item_name, models in additional_items:
            model = random.choice(models)
            serial_prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
            serial_number = f"{serial_prefix}-{random.randint(1000, 9999)}"

            issue_date = datetime.strptime(hire_date, '%Y-%m-%d') + timedelta(days=random.randint(0, 30))

            assets.append({
                "id": asset_id,
                "employee_id": emp['id'],
                "issue_date": issue_date.strftime('%Y-%m-%d'),
                "item_name": item_name,
                "model": model,
                "serial_number": serial_number,
                "status": random.choice(statuses[:3]),  # 대부분 사용중
                "note": None
            })
            asset_id += 1

with open('data/assets.json', 'w', encoding='utf-8') as f:
    json.dump(assets, f, ensure_ascii=False, indent=2)

print(f"P4-T04: assets.json 생성 완료 ({len(assets)}개 레코드)")

print("\nPhase 4 JSON 파일 생성 완료!")
