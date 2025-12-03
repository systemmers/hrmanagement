# 멀티테넌시 버그 분석 보고서

분석일: 2025-12-03
분석 대상: dev_prompt.md ###12 - 법인간 데이터 격리 문제

---

## 1. 문제 요약

### 보고된 증상
1. **직원 공유 버그**: 법인 3개에 등록된 직원이 모두 공유됨
2. **설정 공유 버그**: 모든 법인의 세팅값이 동일함
3. **초기화 문제**: 신규 법인 생성시 세팅값이 초기화되지 않음

---

## 2. 근본 원인 분석

### 2.1 핵심 버그 #1: Employee.organization_id가 NULL

**위치**: `app/models/employee.py:26`

```python
organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
```

**문제점**:
- 모든 10개 Employee 레코드의 `organization_id`가 NULL
- Employee와 Company간 연결이 끊어져 있음

**데이터베이스 현황**:
```
Employee 테이블 (10개 레코드)
├── organization_id: 전부 NULL
└── Company 연결: 불가능

Company 테이블 (3개 레코드)
├── Company ID 1: root_organization_id = 7
├── Company ID 2: root_organization_id = NULL (미설정)
└── Company ID 3: root_organization_id = 10
```

**연결 구조 설계**:
```
Company.root_organization_id → Organization.id
Employee.organization_id → Organization.id
```
- Company와 Employee가 같은 Organization.id를 공유해야 연결됨
- 현재 Employee의 organization_id가 NULL이므로 연결 실패

---

### 2.2 핵심 버그 #2: EmployeeRepository에 회사 필터 없음

**위치**: `app/repositories/employee_repository.py:18-21`

```python
def get_all(self) -> List[Dict]:
    """모든 직원 조회"""
    employees = Employee.query.order_by(Employee.id).all()
    return [emp.to_dict() for emp in employees]
```

**문제점**:
- `get_all()` 메서드가 전체 직원을 반환
- 회사(organization_id) 필터가 전혀 없음
- 모든 법인에서 동일한 직원 목록이 표시됨

**영향받는 메서드들**:
| 메서드 | 라인 | 회사 필터 |
|--------|------|-----------|
| `get_all()` | 18-21 | 없음 |
| `search()` | 78-93 | 없음 |
| `filter_by_department()` | 95-98 | 없음 |
| `filter_by_status()` | 100-103 | 없음 |
| `get_count()` | 105-107 | 없음 |
| `filter_employees()` | 157-193 | 없음 |
| `get_statistics()` | 127-139 | 없음 |
| `get_recent_employees()` | 150-155 | 없음 |

---

### 2.3 핵심 버그 #3: 직원 생성시 organization_id 미설정

**위치**: `app/blueprints/employees.py:277-295`

```python
@employees_bp.route('/employees', methods=['POST'])
@manager_or_admin_required
def employee_create():
    """직원 등록 처리"""
    try:
        employee = extract_employee_from_form(request.form, employee_id=0)
        # organization_id는 폼에서 받지만, 기본값 없음
        # 세션의 company_id → organization_id 자동 설정 없음
```

**문제점**:
- `extract_employee_from_form()`은 폼에서 `organization_id`를 받음
- 폼에서 명시적으로 선택하지 않으면 NULL로 저장
- 로그인한 법인의 `root_organization_id`를 자동 설정하지 않음

**올바른 동작**:
```python
# 세션에서 회사 정보 가져오기
company_id = session.get('company_id')
company = Company.query.get(company_id)

# 직원 생성시 자동으로 organization_id 설정
employee.organization_id = company.root_organization_id
```

---

### 2.4 핵심 버그 #4: 직원 목록 조회시 회사 격리 없음

**위치**: `app/blueprints/employees.py:71-127`

```python
@employees_bp.route('/employees')
@manager_or_admin_required
def employee_list():
    # 현재 로그인한 법인 정보 확인 없음
    # session.get('company_id') 사용 안함

    employees = employee_repo.filter_employees(...)  # 전체 직원 반환
```

**문제점**:
- 로그인한 법인 확인 없이 전체 직원 조회
- Repository에 회사 필터 파라미터 전달 안함
- 모든 법인에서 동일한 직원 목록 표시

---

## 3. 영향 범위

### 3.1 보안 위험 (Critical)
- **데이터 유출**: 법인 A의 직원이 법인 B, C에서도 열람 가능
- **개인정보 노출**: 주민등록번호, 급여정보 등 민감 정보 노출
- **멀티테넌시 위반**: 기본적인 데이터 격리 원칙 위반

### 3.2 기능 오류
- 직원 수 통계가 전체 합산으로 표시
- 부서별/상태별 필터가 전체 데이터 대상
- 직원 검색이 타 법인 직원도 포함

### 3.3 비즈니스 로직 오류
- `Company.can_add_employee()`: organization_id 기반 집계 - 항상 0 반환
- `Company.get_employee_count()`: 같은 이유로 0 반환
- 플랜별 직원 제한이 작동하지 않음

---

## 4. 데이터 현황 검증

### 4.1 Employee-Organization 연결 상태
```sql
SELECT organization_id, COUNT(*)
FROM employees
GROUP BY organization_id;

-- 결과:
-- organization_id | count
-- NULL            | 10
```

### 4.2 Company-Organization 연결 상태
```sql
SELECT id, name, root_organization_id
FROM companies;

-- 결과:
-- id | name           | root_organization_id
-- 1  | 테스트기업(주)  | 7
-- 2  | (주)테스트기업  | NULL
-- 3  | 테스트기업 B    | 10
```

### 4.3 법인별 직원 수 (현재 버그 상태)
| 법인 | 예상 직원 수 | 실제 조회 수 | 상태 |
|------|-------------|-------------|------|
| 테스트기업(주) | ? | 10 | 전체 공유 |
| (주)테스트기업 | ? | 10 | 전체 공유 |
| 테스트기업 B | ? | 10 | 전체 공유 |

---

## 5. 수정 방안

### 5.1 단기 수정 (Hotfix)

#### A. EmployeeRepository에 organization_id 필터 추가

```python
# app/repositories/employee_repository.py

def get_all(self, organization_id: int = None) -> List[Dict]:
    """모든 직원 조회 (회사별 필터링)"""
    query = Employee.query
    if organization_id:
        query = query.filter_by(organization_id=organization_id)
    employees = query.order_by(Employee.id).all()
    return [emp.to_dict() for emp in employees]

def get_by_company(self, company_id: int) -> List[Dict]:
    """회사 ID로 직원 조회"""
    from app.models.company import Company
    company = Company.query.get(company_id)
    if not company or not company.root_organization_id:
        return []
    return self.get_all(organization_id=company.root_organization_id)
```

#### B. 직원 목록 Blueprint 수정

```python
# app/blueprints/employees.py

@employees_bp.route('/employees')
@manager_or_admin_required
def employee_list():
    # 현재 로그인한 법인의 organization_id 가져오기
    company_id = session.get('company_id')
    company = Company.query.get(company_id) if company_id else None
    org_id = company.root_organization_id if company else None

    employees = employee_repo.filter_employees(
        organization_id=org_id,  # 회사 필터 추가
        ...
    )
```

#### C. 직원 생성시 자동 organization_id 설정

```python
# app/blueprints/employees.py

@employees_bp.route('/employees', methods=['POST'])
def employee_create():
    employee = extract_employee_from_form(request.form, employee_id=0)

    # 자동으로 organization_id 설정
    company_id = session.get('company_id')
    if company_id and not employee.organization_id:
        company = Company.query.get(company_id)
        if company and company.root_organization_id:
            employee.organization_id = company.root_organization_id
```

### 5.2 데이터 마이그레이션

```sql
-- 기존 직원 데이터에 organization_id 할당 (예시)
-- 실제로는 각 직원이 어느 법인 소속인지 확인 필요

-- 방법 1: User-Employee 연결을 통한 마이그레이션
UPDATE employees e
SET organization_id = (
    SELECT c.root_organization_id
    FROM users u
    JOIN companies c ON u.company_id = c.id
    WHERE u.employee_id = e.id
    LIMIT 1
)
WHERE e.organization_id IS NULL;
```

### 5.3 장기 수정 (리팩토링)

1. **Repository 패턴 개선**: 모든 Repository 메서드에 `organization_id` 또는 `company_id` 필수화
2. **미들웨어 추가**: 요청마다 현재 법인 컨텍스트 자동 설정
3. **모델 제약조건**: `Employee.organization_id`를 `nullable=False`로 변경
4. **테스트 강화**: 멀티테넌시 격리 테스트 케이스 추가

---

## 6. 테스트 시나리오

### 6.1 직원 목록 격리 테스트
1. 법인 A 로그인 → 직원 목록 조회 → 법인 A 직원만 표시 확인
2. 법인 B 로그인 → 직원 목록 조회 → 법인 B 직원만 표시 확인
3. 법인 A 직원이 법인 B에서 검색 불가 확인

### 6.2 직원 생성 테스트
1. 법인 A에서 신규 직원 생성 → organization_id가 법인 A의 root_organization_id인지 확인
2. 생성된 직원이 법인 B에서 조회 불가 확인

### 6.3 통계 격리 테스트
1. 법인별 직원 수 통계가 해당 법인 직원만 집계되는지 확인
2. 부서별/상태별 통계가 법인 내에서만 계산되는지 확인

---

## 7. 결론

### 심각도: Critical

현재 시스템은 **멀티테넌시 기본 원칙인 데이터 격리가 전혀 구현되어 있지 않습니다.**

- 모든 Employee 레코드의 `organization_id`가 NULL
- Repository 레이어에 회사 필터 로직 부재
- Blueprint에서 세션 기반 회사 필터링 미적용

### 우선순위
1. **즉시**: EmployeeRepository에 organization_id 필터 추가
2. **긴급**: 기존 Employee 데이터에 올바른 organization_id 할당
3. **중요**: 직원 생성시 자동 organization_id 설정 로직 추가
4. **계획**: 전체 Repository/Blueprint 멀티테넌시 검토

---

## 부록: 관련 파일 목록

| 파일 | 역할 | 수정 필요 |
|------|------|----------|
| `app/models/employee.py` | Employee 모델 | 제약조건 강화 |
| `app/models/company.py` | Company 모델 | 정상 |
| `app/repositories/employee_repository.py` | 직원 CRUD | 필터 추가 필수 |
| `app/blueprints/employees.py` | 직원 관리 라우트 | 세션 필터 추가 |
| `app/blueprints/corporate.py` | 법인 관리 라우트 | 참고용 |
