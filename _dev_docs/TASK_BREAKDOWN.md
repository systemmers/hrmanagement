# InsaCard Task 분해 및 의존성 매핑

> 생성일: 2025-11-25
> 참조: WORKFLOW.md

---

## 1. Task 의존성 그래프 (상세)

### 1.1 Phase 1: 기존 JSON 필드 보완

```
                    ┌─────────────────────────────────────────┐
                    │        Phase 1 의존성 그래프            │
                    └─────────────────────────────────────────┘

    [독립 실행 가능]              [순차 의존]                [검증]
    ─────────────────         ─────────────────         ─────────

    ┌─────────────┐           ┌─────────────┐
    │   P1-T01    │──────────>│   P1-T04    │──┐
    │ education   │           │ Education   │  │
    │  .json      │           │   Model     │  │
    └─────────────┘           └─────────────┘  │
                                               │     ┌─────────────┐
    ┌─────────────┐           ┌─────────────┐  ├────>│   P1-T07    │
    │   P1-T02    │──────────>│   P1-T05    │──┤     │   템플릿    │
    │ careers     │           │   Career    │  │     │    검증     │
    │  .json      │           │   Model     │  │     └─────────────┘
    └─────────────┘           └─────────────┘  │
                                               │
    ┌─────────────┐           ┌─────────────┐  │
    │   P1-T03    │──────────>│   P1-T06    │──┘
    │ military    │           │  Military   │
    │  .json      │           │   Model     │
    └─────────────┘           └─────────────┘


    병렬 실행 그룹:
    - Group A (병렬): P1-T01, P1-T02, P1-T03
    - Group B (병렬): P1-T04, P1-T05, P1-T06 (Group A 완료 후)
    - Group C (순차): P1-T07 (Group B 완료 후)
```

### 1.2 Phase 2: 핵심 기능 JSON 생성

```
                    ┌─────────────────────────────────────────┐
                    │        Phase 2 의존성 그래프            │
                    └─────────────────────────────────────────┘

    [JSON 생성]        [모델 생성]       [설정/통합]        [템플릿]
    ───────────        ───────────       ───────────        ───────

    ┌─────────┐       ┌─────────┐
    │ P2-T01  │──────>│ P2-T05  │──┐
    │salaries │       │ Salary  │  │
    └─────────┘       └─────────┘  │
                                   │
    ┌─────────┐       ┌─────────┐  │      ┌─────────┐
    │ P2-T02  │──────>│ P2-T06  │──┼─────>│ P2-T09  │──┐
    │benefits │       │ Benefit │  │      │Repository│  │
    └─────────┘       └─────────┘  │      │  (4개)  │  │
                                   │      └─────────┘  │
    ┌─────────┐       ┌─────────┐  │                   │    ┌─────────┐    ┌─────────┐
    │ P2-T03  │──────>│ P2-T07  │──┤                   ├───>│ P2-T11  │───>│ P2-T12  │
    │contracts│       │Contract │  │                   │    │ app.py  │    │템플릿   │
    └─────────┘       └─────────┘  │                   │    └─────────┘    └─────────┘
                                   │                   │
    ┌─────────┐       ┌─────────┐  │                   │
    │ P2-T04  │──────>│ P2-T08  │──┘                   │
    │sal_hist │       │SalHist  │                      │
    └─────────┘       └─────────┘                      │
                                                       │
    ┌─────────┐                                        │
    │P2-T01~04│───────────────────>┌─────────┐        │
    │ (공통)  │                    │ P2-T10  │────────┘
    └─────────┘                    │config.py│
                                   └─────────┘

    병렬 실행 그룹:
    - Group A (병렬): P2-T01, P2-T02, P2-T03, P2-T04
    - Group B (병렬): P2-T05, P2-T06, P2-T07, P2-T08, P2-T10 (Group A 완료 후)
    - Group C (순차): P2-T09 (Group B 모델 완료 후)
    - Group D (순차): P2-T11 (Group C + P2-T10 완료 후)
    - Group E (순차): P2-T12 (Group D 완료 후)
```

---

## 2. Task 상세 명세

### 2.1 Phase 1 Tasks

#### P1-T01: education.json 필드 추가
```yaml
task_id: P1-T01
type: data_modification
target_file: data/education.json
estimated_time: 15min
dependencies: none
parallel_group: A

작업 내용:
  - 기존 29개 레코드에 gpa, note 필드 추가
  - gpa: "3.5/4.5" 형식 또는 null
  - note: 비고 텍스트 또는 null

검증 기준:
  - JSON 문법 오류 없음
  - 모든 레코드에 필드 존재
  - 기존 데이터 무결성 유지
```

#### P1-T02: careers.json 필드 추가
```yaml
task_id: P1-T02
type: data_modification
target_file: data/careers.json
estimated_time: 15min
dependencies: none
parallel_group: A

작업 내용:
  - 기존 28개 레코드에 department, salary 필드 추가
  - department: 부서명 문자열 또는 null
  - salary: 연봉 숫자 또는 null

검증 기준:
  - JSON 문법 오류 없음
  - 모든 레코드에 필드 존재
```

#### P1-T03: military.json 필드 추가
```yaml
task_id: P1-T03
type: data_modification
target_file: data/military.json
estimated_time: 10min
dependencies: none
parallel_group: A

작업 내용:
  - 기존 13개 레코드에 duty, specialty 필드 추가
  - duty: 보직 문자열 또는 null
  - specialty: 병과 문자열 또는 null

검증 기준:
  - JSON 문법 오류 없음
  - 모든 레코드에 필드 존재
```

#### P1-T04: Education 모델 수정
```yaml
task_id: P1-T04
type: code_modification
target_file: models.py
estimated_time: 10min
dependencies: [P1-T01]
parallel_group: B

작업 내용:
  - Education.__init__()에 gpa, note 파라미터 추가
  - from_dict(), to_dict() 메서드 업데이트

코드 변경:
  class Education:
      def __init__(self, ..., gpa: str = None, note: str = None):
          self.gpa = gpa
          self.note = note
```

#### P1-T05: Career 모델 수정
```yaml
task_id: P1-T05
type: code_modification
target_file: models.py
estimated_time: 10min
dependencies: [P1-T02]
parallel_group: B

작업 내용:
  - Career.__init__()에 department, salary 파라미터 추가
  - from_dict(), to_dict() 메서드 업데이트
```

#### P1-T06: Military 모델 수정
```yaml
task_id: P1-T06
type: code_modification
target_file: models.py
estimated_time: 10min
dependencies: [P1-T03]
parallel_group: B

작업 내용:
  - Military.__init__()에 duty, specialty 파라미터 추가
  - from_dict(), to_dict() 메서드 업데이트
```

#### P1-T07: 템플릿 데이터 바인딩 검증
```yaml
task_id: P1-T07
type: verification
target_file: templates/employee_detail.html
estimated_time: 20min
dependencies: [P1-T04, P1-T05, P1-T06]
parallel_group: C

작업 내용:
  - Flask 서버 실행
  - 직원 상세 페이지 접근
  - 학력정보 섹션 gpa, note 표시 확인
  - 경력정보 섹션 department, salary 표시 확인
  - 병역정보 섹션 duty, specialty 표시 확인

검증 기준:
  - 페이지 오류 없이 로드
  - 추가 필드 정상 표시
  - null 값 시 "정보 없음" 또는 빈칸 표시
```

### 2.2 Phase 2 Tasks (핵심 4개만 상세)

#### P2-T01: salaries.json 생성
```yaml
task_id: P2-T01
type: data_creation
target_file: data/salaries.json
estimated_time: 30min
dependencies: none
parallel_group: A

스키마:
{
  "id": number,
  "employee_id": number,
  "salary_type": string,        # "월급", "연봉", "시급"
  "base_salary": number,        # 기본급
  "position_allowance": number, # 직책수당
  "meal_allowance": number,     # 식대
  "transportation_allowance": number, # 교통비
  "total_salary": number,       # 총급여
  "payment_day": number,        # 급여지급일 (1-31)
  "payment_method": string,     # "계좌이체", "현금"
  "bank_account": string        # 급여계좌
}

생성 기준:
  - employee_id 1~25 각각 1개 레코드
  - 직급/직책에 따른 급여 차등
  - 현실적인 급여 범위 설정
```

#### P2-T05: Salary 모델 생성
```yaml
task_id: P2-T05
type: code_creation
target_file: models.py
estimated_time: 15min
dependencies: [P2-T01]
parallel_group: B

코드 템플릿:
class Salary:
    def __init__(self, id: int, employee_id: int, salary_type: str,
                 base_salary: int, position_allowance: int = 0,
                 meal_allowance: int = 0, transportation_allowance: int = 0,
                 total_salary: int = 0, payment_day: int = 25,
                 payment_method: str = '계좌이체', bank_account: str = None):
        # 필드 할당

    @classmethod
    def from_dict(cls, data: dict) -> 'Salary':
        return cls(**data)

    def to_dict(self) -> dict:
        return self.__dict__.copy()
```

#### P2-T09: Repository 클래스 생성
```yaml
task_id: P2-T09
type: code_creation
target_file: models.py
estimated_time: 20min
dependencies: [P2-T05, P2-T06, P2-T07, P2-T08]
parallel_group: C

생성할 Repository:
  - SalaryRepository(BaseRelationRepository)
  - BenefitRepository(BaseRelationRepository)
  - ContractRepository(BaseRelationRepository)
  - SalaryHistoryRepository(BaseRelationRepository)

패턴:
  - BaseRelationRepository 상속
  - model_class, json_path 오버라이드
  - get_by_employee_id() 메서드 자동 상속
```

#### P2-T11: app.py 라우트 수정
```yaml
task_id: P2-T11
type: code_modification
target_file: app.py
estimated_time: 20min
dependencies: [P2-T09, P2-T10]
parallel_group: D

수정 위치: employee_detail() 함수

추가 코드:
    # 급여 정보 로드
    salary_repo = SalaryRepository()
    salary = salary_repo.get_by_employee_id(id)
    salary = salary[0] if salary else None

    # 복리후생 로드
    benefit_repo = BenefitRepository()
    benefit_list = benefit_repo.get_by_employee_id(id)

    # 근로계약 이력 로드
    contract_repo = ContractRepository()
    contract_list = contract_repo.get_by_employee_id(id)

    # 연봉계약 이력 로드
    salary_history_repo = SalaryHistoryRepository()
    salary_history_list = salary_history_repo.get_by_employee_id(id)

템플릿 컨텍스트 추가:
    return render_template('employee_detail.html',
        ...,
        salary=salary,
        benefit_list=benefit_list,
        contract_list=contract_list,
        salary_history_list=salary_history_list
    )
```

---

## 3. 실행 순서 매트릭스

### 3.1 최적 실행 순서 (병렬화 고려)

```
시간축 ──────────────────────────────────────────────────────────────>

T0          T1          T2          T3          T4          T5
│           │           │           │           │           │
├── Phase 1 ─────────────────────────────────────┤
│           │           │           │           │
│ [P1-T01]  │ [P1-T04]  │           │           │
│ [P1-T02]  │ [P1-T05]  │ [P1-T07]  │           │
│ [P1-T03]  │ [P1-T06]  │           │           │
│  (병렬)   │  (병렬)   │  (순차)   │           │
│           │           │           │           │
├─────────── Phase 2 ────────────────────────────────────────────┤
│           │           │           │           │           │
│           │ [P2-T01]  │ [P2-T05]  │ [P2-T09]  │ [P2-T11]  │ [P2-T12]
│           │ [P2-T02]  │ [P2-T06]  │           │           │
│           │ [P2-T03]  │ [P2-T07]  │           │           │
│           │ [P2-T04]  │ [P2-T08]  │           │           │
│           │  (병렬)   │ [P2-T10]  │  (순차)   │  (순차)   │ (순차)
│           │           │  (병렬)   │           │           │
```

### 3.2 Phase별 예상 소요 시간

| Phase | 병렬 그룹 | Task 수 | 단일 작업 시간 | 병렬 실행 시간 |
|-------|----------|--------|---------------|---------------|
| Phase 1 | A | 3 | 40min | 15min |
| Phase 1 | B | 3 | 30min | 10min |
| Phase 1 | C | 1 | 20min | 20min |
| **Phase 1 합계** | - | 7 | 90min | **45min** |
| Phase 2 | A | 4 | 120min | 30min |
| Phase 2 | B | 5 | 75min | 20min |
| Phase 2 | C | 1 | 20min | 20min |
| Phase 2 | D | 1 | 20min | 20min |
| Phase 2 | E | 1 | 30min | 30min |
| **Phase 2 합계** | - | 12 | 265min | **120min** |

---

## 4. 리스크 매트릭스

| Task ID | 리스크 | 확률 | 영향도 | 대응 방안 |
|---------|--------|------|--------|----------|
| P1-T01~03 | JSON 파싱 오류 | 낮음 | 높음 | 변경 전 백업 |
| P1-T04~06 | 모델 타입 오류 | 중간 | 중간 | 기본값 설정 |
| P2-T01~04 | 데이터 불일치 | 중간 | 높음 | employee_id 검증 |
| P2-T09 | Repository 상속 오류 | 낮음 | 중간 | 기존 패턴 참조 |
| P2-T11 | 라우트 충돌 | 낮음 | 높음 | 기존 코드 보존 |
| P2-T12 | 템플릿 렌더링 오류 | 중간 | 중간 | 점진적 바인딩 |

---

## 5. 완료 기준 (Definition of Done)

### 각 Task 완료 조건

1. **JSON 수정/생성 Task**
   - [ ] JSON 문법 유효
   - [ ] 필수 필드 모두 존재
   - [ ] employee_id 유효성 검증
   - [ ] 샘플 데이터 현실성 검토

2. **모델 수정/생성 Task**
   - [ ] from_dict() 정상 동작
   - [ ] to_dict() 정상 동작
   - [ ] 타입 힌트 명시
   - [ ] 기본값 설정

3. **Repository 생성 Task**
   - [ ] BaseRelationRepository 상속
   - [ ] get_by_employee_id() 동작
   - [ ] get_all() 동작

4. **라우트 수정 Task**
   - [ ] 기존 기능 유지
   - [ ] 신규 데이터 로드
   - [ ] 에러 핸들링

5. **템플릿 바인딩 Task**
   - [ ] 데이터 정상 표시
   - [ ] null 값 처리
   - [ ] 반복문 정상 동작
   - [ ] CSS 스타일 유지
