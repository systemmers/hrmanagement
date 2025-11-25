"""
Phase 2: 핵심 기능 JSON 파일 생성 스크립트
P2-T01: salaries.json 생성
P2-T02: benefits.json 생성
P2-T03: contracts.json 생성
P2-T04: salary_history.json 생성
"""
import json
import random
from datetime import datetime, timedelta

# 직원 기본 정보 로드
with open('data/employees.json', 'r', encoding='utf-8') as f:
    employees = json.load(f)

# P2-T01: salaries.json 생성
salaries = []
salary_bases = {
    '사원': (3000000, 3500000),
    '대리': (3500000, 4500000),
    '과장': (4500000, 5500000),
    '차장': (5500000, 6500000),
    '부장': (6500000, 8000000),
    '이사': (8000000, 10000000)
}
banks = ['국민은행', '신한은행', '우리은행', '하나은행', 'IBK기업은행', '농협은행']

for i, emp in enumerate(employees, 1):
    position = emp.get('position', '사원')
    base_range = salary_bases.get(position, (3000000, 4000000))
    base_salary = random.randint(base_range[0] // 100000, base_range[1] // 100000) * 100000
    position_allowance = random.choice([200000, 300000, 400000, 500000])
    meal_allowance = 200000
    transportation_allowance = random.choice([100000, 150000, 200000])

    salaries.append({
        "id": i,
        "employee_id": emp['id'],
        "salary_type": "월급",
        "base_salary": base_salary,
        "position_allowance": position_allowance,
        "meal_allowance": meal_allowance,
        "transportation_allowance": transportation_allowance,
        "total_salary": base_salary + position_allowance + meal_allowance + transportation_allowance,
        "payment_day": 25,
        "payment_method": "계좌이체",
        "bank_account": f"{random.choice(banks)} {random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100000, 999999)}"
    })

with open('data/salaries.json', 'w', encoding='utf-8') as f:
    json.dump(salaries, f, ensure_ascii=False, indent=2)

print(f"P2-T01: salaries.json 생성 완료 ({len(salaries)}개 레코드)")

# P2-T02: benefits.json 생성
benefits = []
severance_types = ['DC형', 'DB형', 'IRP']
severance_methods = ['퇴직연금', '퇴직금']

for i, emp in enumerate(employees, 1):
    # 입사일 기준으로 연차 계산 (간략화)
    annual_granted = random.randint(11, 20)
    annual_used = random.randint(0, min(10, annual_granted))

    benefits.append({
        "id": i,
        "employee_id": emp['id'],
        "year": 2025,
        "annual_leave_granted": annual_granted,
        "annual_leave_used": annual_used,
        "annual_leave_remaining": annual_granted - annual_used,
        "severance_type": random.choice(severance_types),
        "severance_method": random.choice(severance_methods)
    })

with open('data/benefits.json', 'w', encoding='utf-8') as f:
    json.dump(benefits, f, ensure_ascii=False, indent=2)

print(f"P2-T02: benefits.json 생성 완료 ({len(benefits)}개 레코드)")

# P2-T03: contracts.json 생성
contracts = []
contract_types = ['정규직', '계약직', '파견직']
employee_types = ['일반직', '전문직', '기술직', '관리직']
work_types = ['주5일', '주4일', '교대근무', '유연근무']

for i, emp in enumerate(employees, 1):
    # 입사일 사용
    hire_date = emp.get('hireDate', '2024-01-01')
    contract_type = random.choices(contract_types, weights=[80, 15, 5])[0]

    contracts.append({
        "id": i,
        "employee_id": emp['id'],
        "contract_date": hire_date,
        "contract_type": contract_type,
        "contract_period": "무기계약" if contract_type == '정규직' else "1년",
        "employee_type": random.choice(employee_types),
        "work_type": random.choices(work_types, weights=[85, 5, 5, 5])[0]
    })

with open('data/contracts.json', 'w', encoding='utf-8') as f:
    json.dump(contracts, f, ensure_ascii=False, indent=2)

print(f"P2-T03: contracts.json 생성 완료 ({len(contracts)}개 레코드)")

# P2-T04: salary_history.json 생성
salary_history = []
history_id = 1

for emp in employees:
    # 각 직원당 1~3년치 연봉 이력 생성
    emp_salary = next((s for s in salaries if s['employee_id'] == emp['id']), None)
    if emp_salary:
        base_annual = emp_salary['total_salary'] * 12

        for year_offset in range(random.randint(1, 3)):
            year = 2025 - year_offset
            annual_salary = int(base_annual * (1 - year_offset * 0.05))  # 과거로 갈수록 5% 감소
            bonus = int(annual_salary * random.choice([0.05, 0.08, 0.10, 0.12]))

            salary_history.append({
                "id": history_id,
                "employee_id": emp['id'],
                "contract_year": year,
                "annual_salary": annual_salary,
                "bonus": bonus,
                "total_amount": annual_salary + bonus,
                "contract_period": f"{year}-01-01 ~ {year}-12-31"
            })
            history_id += 1

with open('data/salary_history.json', 'w', encoding='utf-8') as f:
    json.dump(salary_history, f, ensure_ascii=False, indent=2)

print(f"P2-T04: salary_history.json 생성 완료 ({len(salary_history)}개 레코드)")

print("\nPhase 2 JSON 파일 생성 완료!")
