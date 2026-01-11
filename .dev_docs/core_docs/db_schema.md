# 데이터베이스 스키마 문서

프로젝트: HR Management System
작성일: 2025-12-16
최종 업데이트: 2026-01-11
데이터베이스: PostgreSQL / SQLite (SQLAlchemy ORM)

## 목차
1. [개요](#개요)
2. [핵심 도메인](#핵심-도메인)
3. [테이블 상세 스키마](#테이블-상세-스키마)
4. [관계 다이어그램](#관계-다이어그램)
5. [인덱스 및 제약조건](#인덱스-및-제약조건)

---

## 개요

이 데이터베이스는 인사관리 시스템(HRMS)을 위한 스키마로, 다음과 같은 주요 기능을 지원합니다:

- 멀티테넌시: 여러 법인(Company)이 독립적으로 직원 관리
- 사용자 인증: 3가지 계정 유형 (personal, corporate, employee_sub)
- 직원 정보 관리: 기본정보, 확장정보, 경력, 학력, 자격증 등
- 조직 관리: 트리 구조의 조직도 (Organization)
- 계약 관리: 개인-법인 간 계약 관계 및 데이터 공유 설정
- 급여/복리후생: 급여, 보험, 복리후생 정보 관리
- 인사평가: 평가, 승진, 교육 이력
- 알림 시스템: 계약, 동기화, 시스템 알림
- 감사 로그: 모든 중요 작업의 이력 추적
- 첨부파일 관리: 다형성 기반 첨부파일 시스템 (2026-01-10)

**총 테이블 수**: 34개

---

## 핵심 도메인

### 1. 사용자 및 인증 (User & Authentication)

#### users
사용자 인증 및 권한 관리를 위한 핵심 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 사용자 ID |
| username | String(80) | Unique, Not Null, Index | 사용자명 |
| email | String(120) | Unique, Not Null, Index | 이메일 |
| password_hash | String(256) | Not Null | 암호화된 비밀번호 |
| role | String(20) | Not Null, Default='employee' | 권한 (admin/manager/employee) |
| employee_id | Integer | FK(employees.id), Nullable | 연결된 직원 ID |
| is_active | Boolean | Not Null, Default=True | 활성 상태 |
| account_type | String(20) | Not Null, Default='corporate', Index | 계정 유형 |
| company_id | Integer | FK(companies.id), Nullable, Index | 소속 법인 ID |
| parent_user_id | Integer | FK(users.id), Nullable | 상위 사용자 ID |
| privacy_settings | JSON | Nullable | 개인정보 공개 설정 |
| created_at | DateTime | Default=now() | 생성일시 |
| last_login | DateTime | Nullable | 마지막 로그인 |

**상수 정의**:
- ROLE: admin, manager, employee
- ACCOUNT_TYPE: personal, corporate, employee_sub

**관계**:
- 1:1 → Employee (employee)
- N:1 → Company (company)
- N:1 → User (parent_user)
- 1:N → User (sub_users)

---

### 2. 법인 및 조직 (Company & Organization)

#### companies
법인(기업) 정보 관리 - 멀티테넌시 핵심 모델

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 법인 ID |
| name | String(200) | Not Null, Index | 법인명 |
| business_number | String(20) | Unique, Not Null, Index | 사업자등록번호 |
| corporate_number | String(20) | Nullable | 법인등록번호 |
| representative | String(100) | Not Null | 대표자명 |
| business_type | String(100) | Nullable | 업종 |
| business_category | String(100) | Nullable | 업태 |
| establishment_date | Date | Nullable | 설립일 |
| phone | String(20) | Nullable | 전화번호 |
| fax | String(20) | Nullable | 팩스 |
| email | String(120) | Nullable | 이메일 |
| website | String(200) | Nullable | 웹사이트 |
| postal_code | String(10) | Nullable | 우편번호 |
| address | String(300) | Nullable | 주소 |
| address_detail | String(200) | Nullable | 상세주소 |
| root_organization_id | Integer | FK(organizations.id), Nullable | 루트 조직 ID |
| is_active | Boolean | Not Null, Default=True | 활성 상태 |
| is_verified | Boolean | Not Null, Default=False | 인증 여부 |
| verified_at | DateTime | Nullable | 인증 일시 |
| plan_type | String(50) | Not Null, Default='free' | 플랜 유형 |
| plan_expires_at | DateTime | Nullable | 플랜 만료일 |
| max_employees | Integer | Not Null, Default=10 | 최대 직원 수 |
| created_at | DateTime | Default=now() | 생성일시 |
| updated_at | DateTime | Default=now(), onupdate | 수정일시 |

**상수 정의**:
- PLAN_TYPE: free, basic, premium, enterprise
- PLAN_MAX_EMPLOYEES: {free: 10, basic: 50, premium: 200, enterprise: 9999}

**관계**:
- 1:1 → Organization (root_organization)
- 1:N → User (users)
- 1:N → PersonCorporateContract (person_contracts)

---

#### organizations
트리 구조의 조직도 관리

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 조직 ID |
| name | String(100) | Not Null | 조직명 |
| code | String(50) | Unique, Nullable | 조직 코드 |
| org_type | String(50) | Not Null, Default='department' | 조직 유형 |
| parent_id | Integer | FK(organizations.id), Nullable | 상위 조직 ID |
| manager_id | Integer | FK(employees.id), Nullable | 담당자 ID |
| sort_order | Integer | Default=0 | 정렬 순서 |
| is_active | Boolean | Not Null, Default=True | 활성 상태 |
| description | Text | Nullable | 설명 |
| created_at | DateTime | Default=now() | 생성일시 |
| updated_at | DateTime | Default=now(), onupdate | 수정일시 |

**상수 정의**:
- ORG_TYPE: company, division, department, team, unit

**관계**:
- Self-referential (parent → children)
- N:1 → Employee (manager)
- 1:N → Employee (employees)
- 1:1 ← Company (company)

---

### 3. 직원 정보 (Employee)

#### employees
직원 기본 정보 및 확장 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 직원 ID |
| employee_number | String(20) | Unique, Nullable | 사번 (EMP-YYYY-NNNN) |
| name | String(100) | Not Null | 이름 |
| photo | String(500) | Nullable | 사진 URL |
| department | String(100) | Nullable | 부서 |
| position | String(100) | Nullable | 직급 |
| status | String(50) | Nullable | 재직 상태 |
| hire_date | String(20) | Nullable | 입사일 |
| phone | String(50) | Nullable | 전화번호 |
| email | String(200) | Nullable | 이메일 |
| organization_id | Integer | FK(organizations.id), Nullable | 소속 조직 ID |
| team | String(100) | Nullable | 팀 |
| job_title | String(100) | Nullable | 직책 |
| work_location | String(200) | Nullable | 근무지 |
| internal_phone | String(50) | Nullable | 내선번호 |
| company_email | String(200) | Nullable | 회사 이메일 |
| english_name | String(100) | Nullable | 영문명 |
| chinese_name | String(100) | Nullable | 한자명 |
| birth_date | String(20) | Nullable | 생년월일 |
| lunar_birth | Boolean | Default=False | 음력 여부 |
| gender | String(10) | Nullable | 성별 |
| mobile_phone | String(50) | Nullable | 휴대폰 |
| home_phone | String(50) | Nullable | 자택전화 |
| address | String(500) | Nullable | 주소 |
| detailed_address | String(500) | Nullable | 상세주소 |
| postal_code | String(20) | Nullable | 우편번호 |
| resident_number | String(20) | Nullable | 주민등록번호 |
| nationality | String(50) | Nullable | 국적 |
| blood_type | String(10) | Nullable | 혈액형 |
| religion | String(50) | Nullable | 종교 |
| hobby | String(200) | Nullable | 취미 |
| specialty | String(200) | Nullable | 특기 |
| disability_info | Text | Nullable | 장애정보 |
| marital_status | String(20) | Nullable | 결혼여부 |
| actual_postal_code | String(20) | Nullable | 실제거주 우편번호 |
| actual_address | String(500) | Nullable | 실제거주 주소 |
| actual_detailed_address | String(500) | Nullable | 실제거주 상세주소 |
| emergency_contact | String(50) | Nullable | 비상연락처 |
| emergency_relation | String(50) | Nullable | 비상연락처 관계 |

**관계**:
- 1:1 ← User (user)
- N:1 → Organization (organization)
- 1:N → Education (educations)
- 1:N → Career (careers)
- 1:N → Certificate (certificates)
- 1:N → FamilyMember (family_members)
- 1:N → Language (languages)
- 1:N → SalaryHistory (salary_histories)
- 1:N → Promotion (promotions)
- 1:N → Evaluation (evaluations)
- 1:N → Training (trainings)
- 1:N → Attendance (attendances)
- 1:N → HrProject (hr_projects)
- 1:N → ProjectParticipation (project_participations)
- 1:N → Award (awards)
- 1:N → Asset (assets)
- 1:N → SalaryPayment (salary_payments)
- 1:N → Attachment (attachments)
- 1:1 → MilitaryService (military_service)
- 1:1 → Salary (salary)
- 1:1 → Benefit (benefit)
- 1:1 → Contract (contract)
- 1:1 → Insurance (insurance)

---

### 4. 개인정보 (Personal Information)

#### educations
학력 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 학력 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| school_type | String(50) | Nullable | 학교 유형 |
| school_name | String(200) | Nullable | 학교명 |
| major | String(200) | Nullable | 전공 |
| degree | String(50) | Nullable | 학위 |
| admission_date | String(20) | Nullable | 입학일 |
| graduation_date | String(20) | Nullable | 졸업일 |
| graduation_status | String(50) | Nullable | 졸업 상태 |
| gpa | String(20) | Nullable | 학점 |
| location | String(200) | Nullable | 소재지 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### careers
경력 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 경력 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| company_name | String(200) | Nullable | 회사명 |
| department | String(100) | Nullable | 부서 |
| position | String(100) | Nullable | 직급 |
| job_description | Text | Nullable | 업무내용 |
| start_date | String(20) | Nullable | 시작일 |
| end_date | String(20) | Nullable | 종료일 |
| salary | Integer | Nullable | 급여 |
| resignation_reason | String(500) | Nullable | 퇴사사유 |
| is_current | Boolean | Default=False | 현재근무 여부 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### certificates
자격증 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 자격증 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| certificate_name | String(200) | Nullable | 자격증명 |
| issuing_organization | String(200) | Nullable | 발급기관 |
| certificate_number | String(100) | Nullable | 자격증 번호 |
| acquisition_date | String(20) | Nullable | 취득일 |
| expiry_date | String(20) | Nullable | 만료일 |
| grade | String(50) | Nullable | 등급 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### family_members
가족 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 가족 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| relation | String(50) | Nullable | 관계 |
| name | String(100) | Nullable | 이름 |
| birth_date | String(20) | Nullable | 생년월일 |
| occupation | String(100) | Nullable | 직업 |
| contact | String(50) | Nullable | 연락처 |
| is_cohabitant | Boolean | Default=False | 동거 여부 |
| is_dependent | Boolean | Default=False | 부양 여부 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### languages
어학 능력 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 어학 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| language_name | String(100) | Nullable | 언어명 |
| exam_name | String(100) | Nullable | 시험명 |
| score | String(50) | Nullable | 점수 |
| level | String(50) | Nullable | 등급 |
| acquisition_date | String(20) | Nullable | 취득일 |
| expiry_date | String(20) | Nullable | 만료일 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### military_services
병역 정보 (1:1)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 병역 ID |
| employee_id | Integer | FK(employees.id), Unique, Not Null, Index | 직원 ID |
| military_status | String(50) | Nullable | 병역 상태 |
| service_type | String(100) | Nullable | 복무 유형 |
| branch | String(100) | Nullable | 군별 |
| rank | String(50) | Nullable | 계급 |
| enlistment_date | String(20) | Nullable | 입대일 |
| discharge_date | String(20) | Nullable | 제대일 |
| discharge_reason | String(200) | Nullable | 제대사유 |
| exemption_reason | String(500) | Nullable | 면제사유 |
| note | Text | Nullable | 비고 |

**관계**: 1:1 → Employee

---

### 5. 급여 및 복리후생 (Salary & Benefits)

#### salaries
급여 정보 (1:1)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 급여 ID |
| employee_id | Integer | FK(employees.id), Unique, Not Null, Index | 직원 ID |
| salary_type | String(50) | Nullable | 급여 유형 |
| base_salary | Integer | Default=0 | 기본급 |
| position_allowance | Integer | Default=0 | 직책수당 |
| meal_allowance | Integer | Default=0 | 식대 |
| transportation_allowance | Integer | Default=0 | 교통비 |
| total_salary | Integer | Default=0 | 총급여 |
| payment_day | Integer | Default=25 | 지급일 |
| payment_method | String(50) | Nullable | 지급방법 |
| bank_account | String(200) | Nullable | 계좌정보 |
| annual_salary | Integer | Default=0 | 연봉 |
| monthly_salary | Integer | Default=0 | 월급여 |
| hourly_wage | Integer | Default=0 | 통상임금(시급) |
| overtime_hours | Integer | Default=0 | 월 연장근로시간 |
| night_hours | Integer | Default=0 | 월 야간근로시간 |
| holiday_days | Integer | Default=0 | 월 휴일근로일수 |
| overtime_allowance | Integer | Default=0 | 연장근로수당 |
| night_allowance | Integer | Default=0 | 야간근로수당 |
| holiday_allowance | Integer | Default=0 | 휴일근로수당 |
| note | Text | Nullable | 비고 |

**관계**: 1:1 → Employee

---

#### salary_histories
연봉 계약 이력

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 이력 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| contract_year | Integer | Nullable | 계약 연도 |
| annual_salary | Integer | Default=0 | 연봉 |
| bonus | Integer | Default=0 | 보너스 |
| total_amount | Integer | Default=0 | 총액 |
| contract_period | String(100) | Nullable | 계약 기간 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### salary_payments
급여 지급 이력

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 지급 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| payment_date | String(20) | Nullable, Index | 지급일 |
| payment_period | String(50) | Nullable | 지급 기간 |
| base_salary | Integer | Default=0 | 기본급 |
| allowances | Integer | Default=0 | 수당 |
| gross_pay | Integer | Default=0 | 총지급액 |
| insurance | Integer | Default=0 | 보험료 |
| income_tax | Integer | Default=0 | 소득세 |
| total_deduction | Integer | Default=0 | 총공제액 |
| net_pay | Integer | Default=0 | 실수령액 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### benefits
복리후생 정보 (1:1)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 복리후생 ID |
| employee_id | Integer | FK(employees.id), Unique, Not Null, Index | 직원 ID |
| year | Integer | Nullable | 연도 |
| annual_leave_granted | Integer | Default=0 | 부여 연차 |
| annual_leave_used | Integer | Default=0 | 사용 연차 |
| annual_leave_remaining | Integer | Default=0 | 잔여 연차 |
| severance_type | String(50) | Nullable | 퇴직금 유형 |
| severance_method | String(50) | Nullable | 퇴직금 방법 |
| note | Text | Nullable | 비고 |

**관계**: 1:1 → Employee

---

#### insurances
보험 정보 (1:1)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 보험 ID |
| employee_id | Integer | FK(employees.id), Unique, Not Null, Index | 직원 ID |
| national_pension | Boolean | Default=True | 국민연금 가입 |
| health_insurance | Boolean | Default=True | 건강보험 가입 |
| employment_insurance | Boolean | Default=True | 고용보험 가입 |
| industrial_accident | Boolean | Default=True | 산재보험 가입 |
| national_pension_rate | Float | Default=4.5 | 국민연금 요율(%) |
| health_insurance_rate | Float | Default=3.545 | 건강보험 요율(%) |
| long_term_care_rate | Float | Default=0.9182 | 장기요양 요율(%) |
| employment_insurance_rate | Float | Default=0.9 | 고용보험 요율(%) |
| note | Text | Nullable | 비고 |

**관계**: 1:1 → Employee

---

### 6. 계약 관리 (Contract)

#### contracts
직원 계약 정보 (1:1)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 계약 ID |
| employee_id | Integer | FK(employees.id), Unique, Not Null, Index | 직원 ID |
| contract_date | String(20) | Nullable | 계약일 |
| contract_type | String(50) | Nullable | 계약 유형 |
| contract_period | String(50) | Nullable | 계약 기간 |
| employee_type | String(50) | Nullable | 직원 유형 |
| work_type | String(50) | Nullable | 근무 형태 |
| note | Text | Nullable | 비고 |

**관계**: 1:1 → Employee

---

#### person_corporate_contracts
개인-법인 간 계약 관계

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 계약 ID |
| person_user_id | Integer | FK(users.id), Not Null, Index | 개인 사용자 ID |
| company_id | Integer | FK(companies.id), Not Null, Index | 법인 ID |
| status | String(20) | Not Null, Default='requested', Index | 계약 상태 |
| contract_type | String(30) | Not Null, Default='employment' | 계약 유형 |
| contract_start_date | Date | Nullable | 계약 시작일 |
| contract_end_date | Date | Nullable | 계약 종료일 |
| position | String(100) | Nullable | 직위 |
| department | String(100) | Nullable | 부서 |
| employee_number | String(50) | Nullable | 사번 |
| requested_by | String(20) | Not Null, Default='company' | 요청자 |
| notes | Text | Nullable | 메모 |
| rejection_reason | Text | Nullable | 거절 사유 |
| termination_reason | Text | Nullable | 종료 사유 |
| requested_at | DateTime | Default=now() | 요청 일시 |
| approved_at | DateTime | Nullable | 승인 일시 |
| rejected_at | DateTime | Nullable | 거절 일시 |
| terminated_at | DateTime | Nullable | 종료 일시 |
| created_at | DateTime | Default=now() | 생성일시 |
| updated_at | DateTime | Default=now(), onupdate | 수정일시 |
| approved_by | Integer | FK(users.id), Nullable | 승인자 ID |
| rejected_by | Integer | FK(users.id), Nullable | 거절자 ID |
| terminated_by | Integer | FK(users.id), Nullable | 종료자 ID |

**상수 정의**:
- STATUS: requested, approved, rejected, terminated, expired
- CONTRACT_TYPE: employment, contract, freelance, intern

**관계**:
- N:1 → User (person_user)
- N:1 → Company (company)
- 1:1 → DataSharingSettings (data_sharing_settings)
- 1:N → SyncLog (sync_logs)

---

#### data_sharing_settings
데이터 공유 설정

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 설정 ID |
| contract_id | Integer | FK(person_corporate_contracts.id), Unique, Not Null | 계약 ID |
| share_basic_info | Boolean | Default=True | 기본정보 공유 |
| share_contact | Boolean | Default=True | 연락처 공유 |
| share_education | Boolean | Default=False | 학력 공유 |
| share_career | Boolean | Default=False | 경력 공유 |
| share_certificates | Boolean | Default=False | 자격증 공유 |
| share_languages | Boolean | Default=False | 어학 공유 |
| share_military | Boolean | Default=False | 병역 공유 |
| is_realtime_sync | Boolean | Default=False | 실시간 동기화 |
| created_at | DateTime | Default=now() | 생성일시 |
| updated_at | DateTime | Default=now(), onupdate | 수정일시 |

**관계**: 1:1 → PersonCorporateContract

---

#### sync_logs
동기화 이력

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 로그 ID |
| contract_id | Integer | FK(person_corporate_contracts.id), Not Null, Index | 계약 ID |
| sync_type | String(30) | Not Null | 동기화 유형 |
| entity_type | String(50) | Not Null | 엔티티 유형 |
| field_name | String(100) | Nullable | 필드명 |
| old_value | Text | Nullable | 이전 값 |
| new_value | Text | Nullable | 새 값 |
| direction | String(20) | Nullable | 방향 |
| executed_by | Integer | FK(users.id), Nullable | 실행자 ID |
| executed_at | DateTime | Default=now() | 실행 일시 |

**상수 정의**:
- SYNC_TYPE: auto, manual, initial

**관계**: N:1 → PersonCorporateContract

---

### 7. 인사평가 (HR Evaluation)

#### promotions
발령/인사이동 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 발령 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| effective_date | String(20) | Nullable | 발령일 |
| promotion_type | String(50) | Nullable | 발령 유형 |
| from_department | String(100) | Nullable | 이전 부서 |
| to_department | String(100) | Nullable | 이동 부서 |
| from_position | String(100) | Nullable | 이전 직급 |
| to_position | String(100) | Nullable | 이동 직급 |
| job_role | String(100) | Nullable | 직무 |
| reason | Text | Nullable | 사유 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### evaluations
인사평가 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 평가 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| year | Integer | Nullable | 연도 |
| q1_grade | String(10) | Nullable | 1분기 등급 |
| q2_grade | String(10) | Nullable | 2분기 등급 |
| q3_grade | String(10) | Nullable | 3분기 등급 |
| q4_grade | String(10) | Nullable | 4분기 등급 |
| overall_grade | String(10) | Nullable | 전체 등급 |
| salary_negotiation | String(100) | Nullable | 연봉 협상 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### trainings
교육 이력 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 교육 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| training_date | String(20) | Nullable | 교육일 |
| training_name | String(200) | Nullable | 교육명 |
| institution | String(200) | Nullable | 교육기관 |
| hours | Integer | Default=0 | 교육시간 |
| completion_status | String(50) | Nullable | 이수 상태 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

### 8. 근태 및 프로젝트 (Attendance & Projects)

#### attendances
근태 정보 (월별 집계)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 근태 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| year | Integer | Nullable | 연도 |
| month | Integer | Nullable | 월 |
| work_days | Integer | Default=0 | 근무일수 |
| absent_days | Integer | Default=0 | 결근일수 |
| late_count | Integer | Default=0 | 지각횟수 |
| early_leave_count | Integer | Default=0 | 조퇴횟수 |
| annual_leave_used | Integer | Default=0 | 연차사용 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### hr_projects
현재 회사 인사이력 프로젝트

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 프로젝트 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| project_name | String(200) | Nullable | 프로젝트명 |
| start_date | String(20) | Nullable | 시작일 |
| end_date | String(20) | Nullable | 종료일 |
| duration | String(50) | Nullable | 기간 |
| role | String(100) | Nullable | 역할 |
| duty | String(200) | Nullable | 업무 |
| client | String(200) | Nullable | 고객사 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### project_participations
과거 경력 프로젝트 참여이력

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 참여 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| project_name | String(200) | Nullable | 프로젝트명 |
| start_date | String(20) | Nullable | 시작일 |
| end_date | String(20) | Nullable | 종료일 |
| duration | String(50) | Nullable | 기간 |
| role | String(100) | Nullable | 역할 |
| duty | String(200) | Nullable | 업무 |
| client | String(200) | Nullable | 고객사 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### projects
(Legacy) 프로젝트 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 프로젝트 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| project_name | String(200) | Nullable | 프로젝트명 |
| start_date | String(20) | Nullable | 시작일 |
| end_date | String(20) | Nullable | 종료일 |
| duration | String(50) | Nullable | 기간 |
| role | String(100) | Nullable | 역할 |
| duty | String(200) | Nullable | 업무 |
| client | String(200) | Nullable | 고객사 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

### 9. 기타 (Assets, Awards, Attachments)

#### assets
자산 배정 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 자산 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| issue_date | String(20) | Nullable | 지급일 |
| item_name | String(200) | Nullable | 품목명 |
| model | String(200) | Nullable | 모델 |
| serial_number | String(100) | Nullable | 일련번호 |
| status | String(50) | Nullable | 상태 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### awards
수상 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 수상 ID |
| employee_id | Integer | FK(employees.id), Not Null, Index | 직원 ID |
| award_date | String(20) | Nullable | 수상일 |
| award_name | String(200) | Nullable | 수상명 |
| institution | String(200) | Nullable | 수여기관 |
| note | Text | Nullable | 비고 |

**관계**: N:1 → Employee

---

#### attachments (다형성 관계 - 2026-01-10 업데이트)
첨부파일 정보 - 다형성(Polymorphic) 관계 지원

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 첨부파일 ID |
| owner_type | String(50) | Not Null, Index | 소유자 타입 (employee, profile, contract) |
| owner_id | Integer | Not Null, Index | 소유자 ID |
| file_name | String(500) | Nullable | 파일명 |
| file_path | String(1000) | Nullable | 파일경로 |
| file_type | String(100) | Nullable | 파일형식 |
| file_size | Integer | Default=0 | 파일크기 |
| category | String(100) | Nullable, Index | 분류 (document, photo, businesscard) |
| upload_date | String(20) | Nullable | 업로드일 |
| note | Text | Nullable | 비고 |
| employee_id | Integer | FK(employees.id), Nullable, Index | 직원 ID (레거시 호환) |

**상수 정의**:
- OWNER_TYPE: employee, profile, contract
- CATEGORY: document, photo, businesscard, certificate

**관계**:
- 다형성 관계 (owner_type + owner_id)
- N:1 → Employee (레거시 호환)

---

### 10. 시스템 (System)

#### notifications
알림 정보

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 알림 ID |
| user_id | Integer | FK(users.id), Not Null, Index | 수신자 ID |
| notification_type | String(50) | Not Null, Index | 알림 유형 |
| title | String(200) | Not Null | 제목 |
| message | Text | Nullable | 메시지 |
| resource_type | String(50) | Nullable | 관련 리소스 유형 |
| resource_id | Integer | Nullable | 관련 리소스 ID |
| sender_id | Integer | FK(users.id), Nullable | 발신자 ID |
| is_read | Boolean | Not Null, Default=False, Index | 읽음 여부 |
| read_at | DateTime | Nullable | 읽은 일시 |
| priority | String(20) | Not Null, Default='normal' | 우선순위 |
| action_url | String(500) | Nullable | 액션 URL |
| action_label | String(100) | Nullable | 액션 레이블 |
| extra_data | Text | Nullable | 추가 데이터 (JSON) |
| created_at | DateTime | Default=now(), Index | 생성일시 |
| expires_at | DateTime | Nullable | 만료 일시 |

**상수 정의**:
- TYPE: contract_request, contract_approved, contract_rejected, contract_terminated, sync_completed, sync_failed, termination_processed, data_updated, system, info, warning
- PRIORITY: low, normal, high, urgent

**관계**:
- N:1 → User (user)
- N:1 → User (sender)

---

#### notification_preferences
알림 설정

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 설정 ID |
| user_id | Integer | FK(users.id), Unique, Not Null | 사용자 ID |
| receive_contract_notifications | Boolean | Default=True | 계약 알림 수신 |
| receive_sync_notifications | Boolean | Default=True | 동기화 알림 수신 |
| receive_termination_notifications | Boolean | Default=True | 퇴사 알림 수신 |
| receive_system_notifications | Boolean | Default=True | 시스템 알림 수신 |
| email_notifications_enabled | Boolean | Default=False | 이메일 알림 활성화 |
| email_digest_frequency | String(20) | Default='none' | 이메일 요약 주기 |
| created_at | DateTime | Default=now() | 생성일시 |
| updated_at | DateTime | Default=now(), onupdate | 수정일시 |

**관계**: 1:1 → User

---

#### audit_logs
감사 로그

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 로그 ID |
| user_id | Integer | FK(users.id), Nullable, Index | 사용자 ID |
| account_type | String(20) | Nullable | 계정 유형 |
| company_id | Integer | FK(companies.id), Nullable, Index | 법인 ID |
| action | String(50) | Not Null, Index | 액션 |
| resource_type | String(50) | Not Null, Index | 리소스 유형 |
| resource_id | Integer | Nullable | 리소스 ID |
| details | Text | Nullable | 세부사항 (JSON) |
| ip_address | String(50) | Nullable | IP 주소 |
| user_agent | String(500) | Nullable | User Agent |
| endpoint | String(200) | Nullable | API 엔드포인트 |
| method | String(10) | Nullable | HTTP 메서드 |
| status | String(20) | Default='success' | 상태 |
| error_message | Text | Nullable | 에러 메시지 |
| created_at | DateTime | Default=now(), Index | 생성일시 |

**상수 정의**:
- ACTION: view, create, update, delete, export, sync, login, logout, access_denied
- STATUS: success, failure, denied

**관계**:
- N:1 → User
- N:1 → Company

---

#### system_settings
시스템 전역 설정

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 설정 ID |
| key | String(100) | Unique, Not Null, Index | 설정 키 |
| value | Text | Nullable | 설정 값 |
| value_type | String(20) | Not Null, Default='string' | 값 타입 |
| description | String(500) | Nullable | 설명 |
| category | String(50) | Nullable, Index | 분류 |
| is_editable | Boolean | Default=True | 수정 가능 여부 |
| updated_at | DateTime | Default=now(), onupdate | 수정일시 |
| created_at | DateTime | Default=now() | 생성일시 |

**상수 정의**:
- VALUE_TYPE: string, integer, boolean, json, float

**관계**: 없음

---

#### classification_options
분류 옵션 (부서, 직급, 재직상태 등)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | Integer | PK, Auto | 옵션 ID |
| category | String(50) | Not Null, Index | 분류 카테고리 |
| value | String(100) | Not Null | 값 |
| label | String(200) | Nullable | 라벨 |
| sort_order | Integer | Default=0 | 정렬 순서 |

**제약조건**: Unique(category, value)

**관계**: 없음

---

## 관계 다이어그램

### 핵심 관계 (ERD 텍스트)

```
┌─────────────┐
│   Company   │ 1
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────┐
│    User     │ 1
└──────┬──────┘
       │
       │ 1:1
       ▼
┌─────────────┐       ┌──────────────────┐
│  Employee   │◄─────►│  Organization    │
└──────┬──────┘  N:1  └──────────────────┘
       │                      ▲
       │                      │ Self-referential
       │ 1:1                  │ (Tree Structure)
       ├─────────┐            │
       │         │            │
       ▼         ▼            │
┌──────────┐ ┌─────────┐     │
│ Contract │ │ Salary  │     │
└──────────┘ └─────────┘     │
                              │
┌─────────────────────────────┘
│
│ 1:N (Employee 중심 관계)
├─ Education
├─ Career
├─ Certificate
├─ FamilyMember
├─ Language
├─ SalaryHistory
├─ Promotion
├─ Evaluation
├─ Training
├─ Attendance
├─ HrProject
├─ ProjectParticipation
├─ Award
├─ Asset
├─ SalaryPayment
└─ Attachment

1:1 (Employee 중심 관계)
├─ MilitaryService
├─ Salary
├─ Benefit
├─ Contract
└─ Insurance
```

### 개인-법인 계약 관계

```
┌─────────────┐                 ┌─────────────┐
│    User     │ N               │   Company   │ 1
│ (personal)  ├────────┐   ┌────┤             │
└─────────────┘        │   │    └─────────────┘
                       │   │
                       ▼   ▼
            ┌──────────────────────────┐
            │ PersonCorporateContract  │
            └─────────┬────────────────┘
                      │
                      │ 1:1
                      ▼
            ┌──────────────────────────┐
            │  DataSharingSettings     │
            └──────────────────────────┘
                      │
                      │ 1:N
                      ▼
            ┌──────────────────────────┐
            │      SyncLog             │
            └──────────────────────────┘
```

### 알림 시스템

```
┌─────────────┐
│    User     │ 1
└──────┬──────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│  Notification    │
└──────────────────┘
       │
       │ 1:1
       ▼
┌───────────────────────────┐
│ NotificationPreference    │
└───────────────────────────┘
```

---

## 인덱스 및 제약조건

### 주요 인덱스

**users**
- username (Unique Index)
- email (Unique Index)
- account_type (Index)
- company_id (Index)

**companies**
- name (Index)
- business_number (Unique Index)

**organizations**
- code (Unique)

**employees**
- employee_id (Index for all employee relations)
- organization_id (Index)

**person_corporate_contracts**
- person_user_id (Index)
- company_id (Index)
- status (Index)

**notifications**
- user_id (Index)
- notification_type (Index)
- is_read (Index)
- created_at (Index)

**audit_logs**
- user_id (Index)
- company_id (Index)
- action (Index)
- resource_type (Index)
- created_at (Index)

**salary_payments**
- payment_date (Index)

**system_settings**
- key (Unique Index)
- category (Index)

**classification_options**
- category (Index)
- Unique(category, value)

### Unique 제약조건

- users: username, email
- companies: business_number
- organizations: code
- employees: employee_number
- salaries: employee_id
- contracts: employee_id
- benefits: employee_id
- insurances: employee_id
- military_services: employee_id
- data_sharing_settings: contract_id
- notification_preferences: user_id
- system_settings: key
- classification_options: (category, value)

### 외래키 제약조건

모든 FK 관계는 CASCADE 또는 SET NULL로 설정되어 있습니다.

**주요 CASCADE 설정**:
- Employee → 모든 1:N 관계 (educations, careers, etc.): `cascade='all, delete-orphan'`
- Employee → 모든 1:1 관계: `cascade='all, delete-orphan'`
- PersonCorporateContract → DataSharingSettings: `cascade='all, delete-orphan'`
- PersonCorporateContract → SyncLog: `cascade='all, delete-orphan'`

---

## 데이터 타입 정책

### 날짜/시간
- DateTime: created_at, updated_at, last_login 등 (UTC 기준)
- Date: establishment_date, contract_start_date 등
- String(20): hire_date, birth_date 등 (유연한 포맷 지원)

### 문자열
- Short: String(10~50) - 코드, 상태, 유형
- Medium: String(100~200) - 이름, 제목
- Long: String(500~1000) - 경로, 주소
- Text: 긴 설명, 메모, JSON 데이터

### 숫자
- Integer: ID, 금액, 일수, 횟수
- Float: 요율 (보험료율)
- Boolean: 플래그, 활성 상태

### JSON
- privacy_settings (users)
- extra_data (notifications)
- details (audit_logs, sync_logs)

---

## 마이그레이션 이력

현재 스키마는 다음과 같은 변화를 거쳤습니다:

1. Phase 1: Company 모델 추가 (멀티테넌시)
2. Phase 2: Organization 모델 추가 (조직 트리)
3. Phase 3: PersonCorporateContract, DataSharingSettings 추가 (계약 관리)
4. Phase 4: HrProject, ProjectParticipation 분리 (프로젝트 이력)
5. Phase 5: Notification, NotificationPreference 추가 (알림 시스템)
6. Phase 6: AuditLog 추가 (감사 로그)
7. Phase 31: Attachments 테이블 다형성 관계 적용 (owner_type/owner_id 추가, 2026-01-10)

---

## 보안 고려사항

1. **비밀번호**: password_hash (werkzeug.security)로 암호화 저장
2. **민감정보**: resident_number, bank_account 등 암호화 필요 (추후)
3. **감사 로그**: 모든 중요 작업을 audit_logs에 기록
4. **권한 관리**: User.role, User.account_type 기반 접근 제어
5. **데이터 공유**: DataSharingSettings로 세밀한 제어

---

## 성능 최적화 권장사항

1. **인덱스 추가**:
   - employee_number 검색 빈도가 높을 경우 복합 인덱스 고려
   - salary_payments의 payment_period도 인덱스 추가 검토

2. **쿼리 최적화**:
   - Employee의 1:N 관계는 lazy='dynamic'으로 설정되어 쿼리 지연 로딩
   - Organization 트리 조회 시 재귀 쿼리 깊이 제한 (현재 10)

3. **데이터 파티셔닝**:
   - audit_logs: 월별/분기별 파티셔닝 고려
   - notifications: 만료된 알림 정기 삭제

4. **캐싱**:
   - classification_options: 애플리케이션 레벨 캐싱
   - system_settings: 애플리케이션 레벨 캐싱

---

## 향후 개선 계획

1. **데이터 암호화**: 민감정보 필드 암호화
2. **버전 관리**: 주요 테이블에 version 컬럼 추가
3. **Soft Delete**: is_deleted 플래그 추가 (현재는 hard delete)
4. **Change Tracking**: 주요 테이블의 변경 이력 추적
5. **Full-text Search**: 직원 검색 성능 개선
6. **Time-series Data**: 근태 데이터를 시계열 DB로 분리

---

**문서 버전**: 1.1
**마지막 업데이트**: 2026-01-11

### 변경 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.1 | 2026-01-11 | attachments 테이블 다형성 관계 업데이트 |
| 1.0 | 2025-12-16 | 초기 문서 작성 |
