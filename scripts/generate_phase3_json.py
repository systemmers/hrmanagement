"""
Phase 3: 인사평가 기능 JSON 파일 생성 스크립트
P3-T01: promotions.json 생성 (인사이동 및 승진)
P3-T02: evaluations.json 생성 (인사고과)
P3-T03: trainings.json 생성 (교육훈련)
P3-T04: attendance.json 생성 (근태현황)
"""
import json
import random
from datetime import datetime, timedelta

# 직원 기본 정보 로드
with open('data/employees.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

# P3-T01: promotions.json 생성 (인사이동 및 승진)
promotions = []
promotion_id = 1
promotion_types = ['신규채용', '승진', '전보', '직급조정', '부서이동']
positions_order = ['사원', '대리', '과장', '차장', '부장', '이사']
departments = ['개발팀', '디자인팀', '마케팅팀', '영업팀', '관리팀', '경영지원팀']

for emp in employees:
    hire_date = emp.get('hireDate', '2024-01-01')
    current_dept = emp.get('department', '개발팀')
    current_pos = emp.get('position', '사원')

    # 신규채용 기록 (모든 직원)
    promotions.append({
        "id": promotion_id,
        "employee_id": emp['id'],
        "effective_date": hire_date,
        "promotion_type": "신규채용",
        "from_department": None,
        "to_department": current_dept,
        "from_position": None,
        "to_position": current_pos,
        "job_role": emp.get('jobRole', None),
        "reason": "신규입사"
    })
    promotion_id += 1

    # 일부 직원에게 추가 인사이동 기록 생성 (30% 확률)
    if random.random() < 0.3:
        # 승진 기록
        try:
            pos_idx = positions_order.index(current_pos)
            if pos_idx > 0:
                prev_pos = positions_order[pos_idx - 1]
                promo_date = datetime.strptime(hire_date, '%Y-%m-%d') + timedelta(days=random.randint(365, 730))
                promotions.append({
                    "id": promotion_id,
                    "employee_id": emp['id'],
                    "effective_date": promo_date.strftime('%Y-%m-%d'),
                    "promotion_type": "승진",
                    "from_department": current_dept,
                    "to_department": current_dept,
                    "from_position": prev_pos,
                    "to_position": current_pos,
                    "job_role": emp.get('jobRole', None),
                    "reason": "정기승진"
                })
                promotion_id += 1
        except ValueError:
            pass

with open('data/promotions.json', 'w', encoding='utf-8') as f:
    json.dump(promotions, f, ensure_ascii=False, indent=2)

print(f"P3-T01: promotions.json 생성 완료 ({len(promotions)}개 레코드)")

# P3-T02: evaluations.json 생성 (인사고과)
evaluations = []
evaluation_id = 1
grades = ['S', 'A', 'B', 'C', 'D']
grade_weights = [5, 25, 50, 15, 5]  # 비율

for emp in employees:
    # 2024년, 2025년 평가 기록 생성
    for year in [2024, 2025]:
        q1 = random.choices(grades, weights=grade_weights)[0]
        q2 = random.choices(grades, weights=grade_weights)[0]
        q3 = random.choices(grades, weights=grade_weights)[0] if year == 2024 else None
        q4 = random.choices(grades, weights=grade_weights)[0] if year == 2024 else None

        # 종합평가 계산 (가장 많이 나온 등급)
        all_grades = [g for g in [q1, q2, q3, q4] if g]
        overall = max(set(all_grades), key=all_grades.count) if all_grades else None

        # 연봉협상 결과
        negotiation_results = ['인상 5%', '인상 3%', '동결', '인상 7%', '인상 10%']
        negotiation_weights = [30, 40, 20, 8, 2]

        evaluations.append({
            "id": evaluation_id,
            "employee_id": emp['id'],
            "year": year,
            "q1_grade": q1,
            "q2_grade": q2,
            "q3_grade": q3,
            "q4_grade": q4,
            "overall_grade": overall if year == 2024 else None,
            "salary_negotiation": random.choices(negotiation_results, weights=negotiation_weights)[0] if year == 2024 else None,
            "note": None
        })
        evaluation_id += 1

with open('data/evaluations.json', 'w', encoding='utf-8') as f:
    json.dump(evaluations, f, ensure_ascii=False, indent=2)

print(f"P3-T02: evaluations.json 생성 완료 ({len(evaluations)}개 레코드)")

# P3-T03: trainings.json 생성 (교육훈련)
trainings = []
training_id = 1
training_names = [
    ('정보보안 교육', '사내', 4),
    ('성희롱 예방교육', '사내', 2),
    ('개인정보보호 교육', '사내', 2),
    ('리더십 교육', '외부기관', 8),
    ('프로젝트 관리', '외부기관', 16),
    ('클라우드 기초', 'AWS', 8),
    ('데이터 분석', '외부기관', 24),
    ('커뮤니케이션 스킬', '사내', 4),
    ('신입사원 OJT', '사내', 40),
    ('직무역량 강화', '사내', 8)
]

for emp in employees:
    # 필수교육 (모든 직원)
    mandatory = [('정보보안 교육', '사내', 4), ('성희롱 예방교육', '사내', 2), ('개인정보보호 교육', '사내', 2)]
    for name, institution, hours in mandatory:
        train_date = datetime(2024, random.randint(1, 6), random.randint(1, 28))
        trainings.append({
            "id": training_id,
            "employee_id": emp['id'],
            "training_date": train_date.strftime('%Y-%m-%d'),
            "training_name": name,
            "institution": institution,
            "hours": hours,
            "completion_status": "이수",
            "note": "필수교육"
        })
        training_id += 1

    # 추가 교육 (50% 확률로 1~2개)
    if random.random() < 0.5:
        extra_trainings = random.sample(training_names[3:], k=random.randint(1, 2))
        for name, institution, hours in extra_trainings:
            train_date = datetime(2024, random.randint(1, 12), random.randint(1, 28))
            trainings.append({
                "id": training_id,
                "employee_id": emp['id'],
                "training_date": train_date.strftime('%Y-%m-%d'),
                "training_name": name,
                "institution": institution,
                "hours": hours,
                "completion_status": random.choice(["이수", "이수", "이수", "미이수"]),
                "note": None
            })
            training_id += 1

with open('data/trainings.json', 'w', encoding='utf-8') as f:
    json.dump(trainings, f, ensure_ascii=False, indent=2)

print(f"P3-T03: trainings.json 생성 완료 ({len(trainings)}개 레코드)")

# P3-T04: attendance.json 생성 (근태현황)
attendance = []
attendance_id = 1

for emp in employees:
    # 2024년 월별 근태 기록 생성
    for month in range(1, 13):
        # 월별 근무일수 계산 (대략적)
        work_days = random.randint(20, 23)
        absent_days = random.choices([0, 0, 0, 0, 1, 2], weights=[70, 10, 10, 5, 3, 2])[0]
        late_count = random.choices([0, 0, 0, 1, 2, 3], weights=[60, 20, 10, 5, 3, 2])[0]
        early_leave = random.choices([0, 0, 0, 1], weights=[80, 10, 5, 5])[0]
        annual_used = random.choices([0, 0, 0, 1, 2], weights=[50, 25, 15, 7, 3])[0]

        attendance.append({
            "id": attendance_id,
            "employee_id": emp['id'],
            "year": 2024,
            "month": month,
            "work_days": work_days - absent_days,
            "absent_days": absent_days,
            "late_count": late_count,
            "early_leave_count": early_leave,
            "annual_leave_used": annual_used
        })
        attendance_id += 1

    # 2025년 1~11월 근태 기록
    for month in range(1, 12):
        work_days = random.randint(20, 23)
        absent_days = random.choices([0, 0, 0, 0, 1], weights=[75, 10, 10, 3, 2])[0]
        late_count = random.choices([0, 0, 0, 1, 2], weights=[65, 20, 10, 3, 2])[0]
        early_leave = random.choices([0, 0, 1], weights=[85, 10, 5])[0]
        annual_used = random.choices([0, 0, 1, 2], weights=[55, 30, 10, 5])[0]

        attendance.append({
            "id": attendance_id,
            "employee_id": emp['id'],
            "year": 2025,
            "month": month,
            "work_days": work_days - absent_days,
            "absent_days": absent_days,
            "late_count": late_count,
            "early_leave_count": early_leave,
            "annual_leave_used": annual_used
        })
        attendance_id += 1

with open('data/attendance.json', 'w', encoding='utf-8') as f:
    json.dump(attendance, f, ensure_ascii=False, indent=2)

print(f"P3-T04: attendance.json 생성 완료 ({len(attendance)}개 레코드)")

print("\nPhase 3 JSON 파일 생성 완료!")
