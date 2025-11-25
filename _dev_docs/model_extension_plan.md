# Employee 모델 확장 계획서

## 1. 현황 분석

### 1.1 현재 Employee 모델 필드
```python
@dataclass
class Employee:
    id: int
    name: str
    photo: str
    department: str
    position: str
    status: str        # active, warning, expired
    hireDate: str
    phone: str
    email: str
```

### 1.2 UI에서 필요한 필드 (14개 섹션 기준)

프로토타입 및 재설계된 템플릿에서 표시하는 정보 영역:

| 섹션 | 현재 지원 | 추가 필요 필드 |
|------|----------|---------------|
| 개인 기본정보 | name, phone, email, photo | name_en, birth_date, gender, address, emergency_contact, emergency_relation |
| 소속정보 | department, position | employee_number, team, job_title, work_location, internal_phone, company_email |
| 계약정보 | hireDate, status | employment_type, contract_period, probation_end, resignation_date |
| 급여정보 | - | salary_type, base_salary, bonus, total_annual, bank, account_number |
| 연차/복리후생 | - | annual_leave_total, annual_leave_used, welfare_benefits |
| 4대보험 | - | national_pension, health_insurance, employment_insurance, accident_insurance |
| 학력정보 | - | education[] (school, degree, major, graduation_year) |
| 경력정보 | - | careers[] (company, position, duty, period) |
| 자격증 | - | certificates[] (name, issuer, date, number) |
| 언어능력 | - | languages[] (language, level, score) |
| 병역정보 | - | military_status, military_branch, military_rank, military_period |
| 프로젝트/수상 | - | projects[], awards[] |
| 인사이동/고과 | - | transfers[], evaluations[] |
| 근태/비품 | - | attendance_records[], equipment[] |

## 2. 확장 계획 (단계별)

### 2.1 Phase 1: 핵심 개인정보 확장 (우선순위: 높음)

```python
@dataclass
class Employee:
    # 기존 필드
    id: int
    name: str
    photo: str
    department: str
    position: str
    status: str
    hireDate: str
    phone: str
    email: str

    # Phase 1 추가 필드
    name_en: str = ""           # 영문 이름
    birth_date: str = ""        # 생년월일 (YYYY-MM-DD)
    gender: str = ""            # male, female
    address: str = ""           # 주소
    emergency_contact: str = "" # 비상연락처
    emergency_relation: str = "" # 비상연락처 관계
    employee_number: str = ""   # 사번
    team: str = ""              # 팀
    job_title: str = ""         # 직책
```

### 2.2 Phase 2: 계약/소속 정보 확장 (우선순위: 높음)

```python
    # Phase 2 추가 필드
    employment_type: str = ""   # regular, contract, parttime, intern
    contract_period: str = ""   # 계약기간
    probation_end: str = ""     # 수습종료일
    resignation_date: str = ""  # 퇴사일
    work_location: str = ""     # 근무지
    internal_phone: str = ""    # 내선번호
    company_email: str = ""     # 회사 이메일
```

### 2.3 Phase 3: 급여/보험 정보 (우선순위: 중간)

```python
    # Phase 3 추가 필드
    salary_type: str = ""       # monthly, annual
    base_salary: int = 0        # 기본급
    bonus: int = 0              # 성과급
    bank: str = ""              # 은행
    account_number: str = ""    # 계좌번호

    # 4대보험 (별도 관리 또는 자동계산)
```

### 2.4 Phase 4: 이력 정보 (별도 모델)

```python
@dataclass
class Education:
    employee_id: int
    school: str
    degree: str         # highschool, associate, bachelor, master, doctor
    major: str
    graduation_year: str

@dataclass
class Career:
    employee_id: int
    company: str
    position: str
    duty: str
    start_date: str
    end_date: str

@dataclass
class Certificate:
    employee_id: int
    name: str
    issuer: str
    acquired_date: str
    certificate_number: str

@dataclass
class FamilyMember:
    employee_id: int
    relation: str       # spouse, child, parent, sibling
    name: str
    birth_date: str
    occupation: str
```

### 2.5 Phase 5: 인사 기록 (별도 모델)

```python
@dataclass
class Transfer:
    employee_id: int
    date: str
    from_department: str
    to_department: str
    from_position: str
    to_position: str
    reason: str

@dataclass
class Evaluation:
    employee_id: int
    year: str
    period: str         # H1, H2, annual
    grade: str
    evaluator: str
    comments: str
```

## 3. 데이터 저장 구조 변경

### 3.1 현재 구조
```
data/
  employees.json        # 전체 직원 정보
  classification_options.json
```

### 3.2 확장 후 구조 (권장)
```
data/
  employees.json            # 기본 직원 정보
  education.json            # 학력 정보
  careers.json              # 경력 정보
  certificates.json         # 자격증 정보
  family_members.json       # 가족 정보
  transfers.json            # 인사이동 기록
  evaluations.json          # 평가 기록
  classification_options.json
```

또는 SQLite/PostgreSQL로 마이그레이션 고려

## 4. 구현 로드맵

### Week 1-2: Phase 1 구현
- [ ] Employee 모델 필드 확장
- [ ] employees.json 구조 업데이트
- [ ] 등록/수정 폼 백엔드 연동
- [ ] 상세보기 데이터 바인딩

### Week 3-4: Phase 2 구현
- [ ] 계약/소속 정보 필드 추가
- [ ] 관련 API 엔드포인트 수정

### Week 5-6: Phase 3 구현
- [ ] 급여/보험 정보 구현
- [ ] 보안 고려 (암호화 필요)

### Week 7-8: Phase 4 구현
- [ ] 별도 모델 클래스 생성
- [ ] Repository 클래스 확장
- [ ] CRUD API 구현

### Week 9-10: Phase 5 구현
- [ ] 인사 기록 모델 구현
- [ ] 이력 관리 UI 연동

## 5. 주의사항

### 5.1 하위 호환성
- 기존 데이터 마이그레이션 스크립트 필요
- 기본값 설정으로 누락 필드 처리

### 5.2 보안 고려
- 급여, 계좌정보 등 민감정보 암호화
- 접근 권한 관리 (향후 구현)

### 5.3 성능 고려
- JSON 파일 기반 시 데이터 증가에 따른 성능 저하 예상
- 100명 이상 시 DB 마이그레이션 권장

## 6. 현재 UI 상태

현재 UI는 모든 14개 섹션이 구현되어 있으며, 데이터가 없는 경우 "정보 없음" 또는 플레이스홀더로 표시됩니다. 모델 확장 시 해당 필드의 실제 데이터가 자동으로 표시됩니다.

### 구현 완료 섹션 목록
1. 개인 기본정보
2. 소속정보
3. 계약정보
4. 급여정보
5. 연차 및 복리후생
6. 4대보험
7. 학력정보
8. 경력정보
9. 자격증 및 면허
10. 언어능력
11. 병역정보
12. 프로젝트 이력
13. 수상 내역
14. 인사이동/고과
15. 근태/비품 (첨부파일)
