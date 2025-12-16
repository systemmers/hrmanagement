# Template Field Schema - Employee Form

## 문서 개요

- **생성일**: 2025-12-16
- **대상**: `app/templates/partials/employee_form/*.html`
- **목적**: 템플릿 필드명과 DB 컬럼 간의 완전한 매핑 정의

---

## 1. 개인 기본정보 (`_personal_info.html`)

### 1.1 기본 필드

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `name` | employees.name | String(100) | Yes | 이름 |
| `name_en` | employees.english_name | String(100) | No | 영문 이름 |
| `photo` | employees.photo | String(500) | No | 프로필 사진 URL |
| `birth_date` | employees.birth_date | String(20) | No | 생년월일 |
| `gender` | employees.gender | String(10) | No | 성별 (male/female) |
| `marital_status` | employees.marital_status | String(20) | No | 결혼여부 |
| `phone` | employees.phone | String(50) | Yes | 휴대전화 |
| `email` | employees.email | String(200) | Yes | 이메일 |

### 1.2 주소 정보

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `address` | employees.address | String(500) | No | 주소 |
| `detailed_address` | employees.detailed_address | String(500) | No | 상세주소 |
| `postal_code` | employees.postal_code | String(20) | No | 우편번호 (hidden) |
| `actual_address` | employees.actual_address | String(500) | No | 실제 거주지 |
| `actual_detailed_address` | employees.actual_detailed_address | String(500) | No | 실제 거주지 상세 |
| `actual_postal_code` | employees.actual_postal_code | String(20) | No | 실제 거주지 우편번호 (hidden) |

### 1.3 비상연락처

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `emergency_contact` | employees.emergency_contact | String(50) | No | 비상연락처 |
| `emergency_relation` | employees.emergency_relation | String(50) | No | 비상연락처 관계 |

### 1.4 추가 개인정보

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `rrn` | employees.resident_number | String(20) | No | 주민등록번호 |
| `blood_type` | employees.blood_type | String(10) | No | 혈액형 |
| `religion` | employees.religion | String(50) | No | 종교 |
| `hobby` | employees.hobby | String(200) | No | 취미 |
| `specialty` | employees.specialty | String(200) | No | 특기 |
| `disability_info` | employees.disability_info | Text | No | 장애정보 |

### 1.5 필드 매핑 주의사항

```python
# form_extractors.py에서 처리되는 매핑
'english_name' or 'name_en'      # 양방향 지원
'resident_number' or 'rrn'       # 양방향 지원
```

---

## 2. 계정정보 (`_account_info.html`)

### 2.1 신규 생성 모드 (action='create')

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `create_account` | - | Boolean | No | 계정 생성 여부 (체크박스) |
| `account_username` | users.username | String(80) | Yes | 아이디 |
| `account_email` | users.email | String(120) | Yes | 계정 이메일 |
| `account_password` | users.password_hash | String(256) | Yes | 초기 비밀번호 |
| `account_role` | users.role | String(20) | No | 역할 (employee/manager/admin) |

### 2.2 수정 모드 (action='update')

- 읽기 전용 표시: username, email, role, account_type, created_at, last_login

---

## 3. 소속정보 (`_organization_info.html`)

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `employee_number` | employees.employee_number | String(20) | No | 사번 (자동생성) |
| `organization_id` | employees.organization_id | Integer (FK) | Yes | 소속 조직 ID |
| `organization_display` | - | - | - | 조직명 표시용 (readonly) |
| `department` | employees.department | String(100) | No | 부서명 |
| `team` | employees.team | String(100) | No | 팀 |
| `position` | employees.position | String(100) | Yes | 직급 |
| `job_title` | employees.job_title | String(100) | No | 직책 |
| `work_location` | employees.work_location | String(200) | No | 근무지 |
| `internal_phone` | employees.internal_phone | String(50) | No | 내선번호 |
| `company_email` | employees.company_email | String(200) | No | 회사 이메일 |

---

## 4. 계약정보 (`_contract_info.html`)

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `hireDate` | employees.hire_date | String(20) | Yes | 입사일 | 완료 |
| `status` | employees.status | String(50) | Yes | 재직 상태 | 일치 |
| `employment_type` | contracts.employee_type | String(50) | No | 고용형태 | 완료 |
| `contract_period` | contracts.contract_period | String(50) | No | 계약기간 | 일치 |
| `probation_end` | - | - | No | 수습종료일 | DB 없음 |
| `resignation_date` | - | - | No | 퇴사일 | DB 없음 |

### 4.1 필드 매핑 주의사항

```python
# form_extractors.py에서 처리되는 매핑
'hire_date' or 'hireDate'        # 양방향 지원

# 모델 프로퍼티로 처리 (2025-12-16 완료)
Employee.employment_type → contract.employee_type  # 프로퍼티
Contract.from_dict: 'employment_type' → 'employee_type'  # 역직렬화
```

---

## 5. 급여정보 (`_salary_info.html`)

### 5.1 기본 급여

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `base_salary` | salaries.base_salary | Integer | No | 기본급 | 일치 |
| `position_allowance` | salaries.position_allowance | Integer | No | 직책수당 | 일치 |
| `meal_allowance` | salaries.meal_allowance | Integer | No | 식대 | 일치 |
| `transport_allowance` | salaries.transportation_allowance | Integer | No | 교통비 | 완료 |
| `bonus_rate` | - | Integer | No | 상여금률 (%) | DB 없음 |
| `pay_type` | salaries.salary_type | String(50) | No | 급여 지급방식 | 완료 |

### 5.2 계좌 정보

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `bank_name` | - | String | No | 은행 | DB 없음 |
| `account_number` | salaries.bank_account | String(200) | No | 계좌번호 | 불일치 |

### 5.3 포괄임금제 필드

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `annual_salary` | salaries.annual_salary | Integer | No | 연봉 |
| `hourly_wage` | salaries.hourly_wage | Integer | No | 통상임금(시급) |
| `overtime_hours` | salaries.overtime_hours | Integer | No | 연장근로시간(월) |
| `overtime_allowance` | salaries.overtime_allowance | Integer | No | 연장근로수당 |
| `night_hours` | salaries.night_hours | Integer | No | 야간근로시간(월) |
| `night_allowance` | salaries.night_allowance | Integer | No | 야간근로수당 |
| `holiday_days` | salaries.holiday_days | Integer | No | 휴일근로일수(월) |
| `holiday_allowance` | salaries.holiday_allowance | Integer | No | 휴일근로수당 |

---

## 6. 4대보험 (`_insurance_info.html`)

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `national_pension_number` | - | String | No | 국민연금 가입번호 | DB 없음 |
| `national_pension_date` | - | Date | No | 국민연금 취득일 | DB 없음 |
| `health_insurance_number` | - | String | No | 건강보험 가입번호 | DB 없음 |
| `health_insurance_date` | - | Date | No | 건강보험 취득일 | DB 없음 |
| `employment_insurance_number` | - | String | No | 고용보험 가입번호 | DB 없음 |
| `employment_insurance_date` | - | Date | No | 고용보험 취득일 | DB 없음 |
| `industrial_insurance_number` | - | String | No | 산재보험 가입번호 | DB 없음 |
| `industrial_insurance_date` | - | Date | No | 산재보험 취득일 | DB 없음 |
| `pension_exempt` | - | Boolean | No | 국민연금 제외 | DB 없음 |
| `health_exempt` | - | Boolean | No | 건강보험 제외 | DB 없음 |
| `employment_exempt` | - | Boolean | No | 고용보험 제외 | DB 없음 |

### 6.1 DB 스키마 비교

**현재 DB (insurances 테이블)**:
- `national_pension` (Boolean) - 가입 여부
- `health_insurance` (Boolean) - 가입 여부
- `employment_insurance` (Boolean) - 가입 여부
- `industrial_accident` (Boolean) - 가입 여부
- `*_rate` (Float) - 각 보험 요율

**템플릿 요구사항**:
- 가입번호, 취득일 필드 필요
- 현재 DB 스키마와 불일치

---

## 7. 복리후생 (`_benefit_info.html`)

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| - | benefits.annual_leave_granted | Integer | No | 연차 발생일수 (읽기전용) |
| - | benefits.annual_leave_used | Integer | No | 연차 사용일수 (읽기전용) |
| - | benefits.annual_leave_remaining | Integer | No | 연차 잔여일수 (읽기전용) |
| - | benefits.severance_type | String(50) | No | 퇴직금 유형 (읽기전용) |
| - | benefits.severance_method | String(50) | No | 퇴직금 적립방법 (읽기전용) |
| - | benefits.year | Integer | No | 기준년도 (읽기전용) |

---

## 8. 병역정보 (`_military_info.html`)

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `military_status` | military_services.military_status | String(50) | No | 병역사항 | 일치 |
| `military_branch` | military_services.branch | String(100) | No | 군별 | 불일치 |
| `military_rank` | military_services.rank | String(50) | No | 계급 | 일치 |
| `military_period` | - | String | No | 복무기간 | DB 없음 |
| `military_duty` | - | String | No | 보직 | DB 없음 |
| `military_specialty` | - | String | No | 병과 | DB 없음 |
| `military_exemption_reason` | military_services.exemption_reason | String(500) | No | 면제사유 | 일치 |

### 8.1 DB 스키마 비교

**현재 DB (military_services 테이블)**:
- `enlistment_date`, `discharge_date` (입대일/제대일)
- `discharge_reason` (제대사유)
- `service_type` (복무 유형)

**템플릿 요구사항**:
- `military_period` (복무기간) - 텍스트 형식 "2018.01 ~ 2019.10"
- `military_duty` (보직), `military_specialty` (병과) 필드 없음

---

## 9. 학력정보 (`_education_info.html`) - 동적 폼

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `education_school_name[]` | educations.school_name | String(200) | No | 학교명 | 일치 |
| `education_degree[]` | educations.degree | String(50) | No | 학위 | 일치 |
| `education_major[]` | educations.major | String(200) | No | 전공 | 일치 |
| `education_graduation_year[]` | educations.graduation_date | String(20) | No | 졸업년도 | 타입불일치 |
| `education_gpa[]` | educations.gpa | String(20) | No | 학점 | 일치 |
| `education_graduation_status[]` | educations.graduation_status | String(50) | No | 졸업유무 | 일치 |
| `education_note[]` | educations.note | Text | No | 비고 | 일치 |

### 9.1 학위 옵션

```javascript
// 값: 라벨
'highschool': '고등학교 졸업'
'associate': '전문학사'
'bachelor': '학사'
'master': '석사'
'doctor': '박사'
```

### 9.2 졸업유무 옵션

```javascript
'graduated': '졸업'
'enrolled': '재학'
'leave': '휴학'
'dropout': '중퇴'
```

---

## 10. 경력정보 (`_career_info.html`) - 동적 폼

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `career_company_name[]` | careers.company_name | String(200) | No | 회사명 | 일치 |
| `career_department[]` | careers.department | String(100) | No | 부서 | 일치 |
| `career_position[]` | careers.position | String(100) | No | 직급/직책 | 일치 |
| `career_duties[]` | careers.job_description | Text | No | 담당업무 | 불일치 |
| `career_salary[]` | careers.salary | Integer | No | 연봉 | 일치 |
| `career_start_date[]` | careers.start_date | String(20) | No | 입사일 | 일치 |
| `career_end_date[]` | careers.end_date | String(20) | No | 퇴사일 | 일치 |

---

## 11. 자격증 (`_certificate_info.html`) - 동적 폼

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `certificate_name[]` | certificates.certificate_name | String(200) | No | 자격증명 | 일치 |
| `certificate_issuer[]` | certificates.issuing_organization | String(200) | No | 발급기관 | 불일치 |
| `certificate_grade[]` | certificates.grade | String(50) | No | 등급/점수 | 일치 |
| `certificate_date[]` | certificates.acquisition_date | String(20) | No | 취득일 | 불일치 |
| `certificate_number[]` | certificates.certificate_number | String(100) | No | 자격번호 | 일치 |
| `certificate_expiry_date[]` | certificates.expiry_date | String(20) | No | 만료일 | 불일치 |

---

## 12. 언어능력 (`_language_info.html`) - 동적 폼

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `language_name[]` | languages.language_name | String(100) | No | 언어 | 완료 |
| `language_level[]` | languages.level | String(50) | No | 수준 | 일치 |
| `language_test_name[]` | languages.exam_name | String(100) | No | 시험명 | 완료 |
| `language_score[]` | languages.score | String(50) | No | 점수/급수 | 일치 |
| `language_test_date[]` | languages.acquisition_date | String(20) | No | 취득일 | 완료 |

### 12.1 언어 옵션

```javascript
['영어', '일본어', '중국어', '스페인어', '프랑스어', '독일어', '러시아어', '베트남어', '태국어', '기타']
```

### 12.2 수준 옵션

```javascript
'native': '원어민'
'advanced': '상'
'intermediate': '중'
'basic': '하'
```

---

## 13. 가족사항 (`_family_info.html`) - 동적 폼

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `family_relation[]` | family_members.relation | String(50) | No | 관계 | 일치 |
| `family_name[]` | family_members.name | String(100) | No | 성명 | 일치 |
| `family_birth_date[]` | family_members.birth_date | String(20) | No | 생년월일 | 일치 |
| `family_occupation[]` | family_members.occupation | String(100) | No | 직업 | 일치 |
| `family_phone[]` | family_members.contact | String(50) | No | 연락처 | 불일치 |
| `family_living_together[]` | family_members.is_cohabitant | Boolean | No | 동거여부 | 불일치 |

### 13.1 관계 옵션

```javascript
'spouse': '배우자'
'child': '자녀'
'parent': '부모'
'sibling': '형제/자매'
```

---

## 14. 수상내역 (`_award_info.html`) - 동적 폼

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 | 상태 |
|---------------|----------------|------|------|------|------|
| `award_name[]` | awards.award_name | String(200) | Yes | 수상명 | 일치 |
| `award_date[]` | awards.award_date | String(20) | No | 수상일 | 일치 |
| `award_institution[]` | awards.institution | String(200) | No | 수여기관 | 일치 |
| `award_description[]` | - | Text | No | 수상내용 | DB 없음 |
| `award_notes[]` | awards.note | Text | No | 비고 | 불일치 |

---

## 15. 프로젝트 (`_project_info.html`) - 동적 폼

**용도**: 현재 소속 회사에서의 프로젝트 이력

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `hr_project_name[]` | hr_projects.project_name | String(200) | No | 프로젝트명 |
| `hr_project_role[]` | hr_projects.role | String(100) | No | 역할/직책 |
| `hr_project_start_date[]` | hr_projects.start_date | String(20) | No | 시작일 |
| `hr_project_end_date[]` | hr_projects.end_date | String(20) | No | 종료일 |
| `hr_project_duty[]` | hr_projects.duty | String(200) | No | 담당업무 |
| `hr_project_client[]` | hr_projects.client | String(200) | No | 발주처 |

---

## 16. 프로젝트 참여이력 (`_project_participation_info.html`) - 동적 폼

**용도**: 과거 경력에서 참여했던 프로젝트/사업 이력

| 템플릿 필드명 | DB 테이블.컬럼 | 타입 | 필수 | 설명 |
|---------------|----------------|------|------|------|
| `participation_project_name[]` | project_participations.project_name | String(200) | No | 사업명 |
| `participation_role[]` | project_participations.role | String(100) | No | 역할/직책 |
| `participation_start_date[]` | project_participations.start_date | String(20) | No | 시작일 |
| `participation_end_date[]` | project_participations.end_date | String(20) | No | 종료일 |
| `participation_duty[]` | project_participations.duty | String(200) | No | 담당업무 |
| `participation_client[]` | project_participations.client | String(200) | No | 발주처 |

---

## 17. 불일치 요약

### 17.1 필드명 불일치 (매핑 상태)

| 템플릿 | DB | 테이블 | 상태 | 처리 위치 |
|--------|-----|--------|------|-----------|
| `name_en` | `english_name` | employees | 완료 | form_extractors.py |
| `rrn` | `resident_number` | employees | 완료 | form_extractors.py |
| `hireDate` | `hire_date` | employees | 완료 | form_extractors.py |
| `employment_type` | `employee_type` | contracts | 완료 | Employee.employment_type 프로퍼티, Contract.from_dict |
| `transport_allowance` | `transportation_allowance` | salaries | 완료 | Salary.transport_allowance 프로퍼티, Salary.from_dict |
| `pay_type` | `salary_type` | salaries | 완료 | Salary.pay_type 프로퍼티, Salary.from_dict |
| `account_number` | `bank_account` | salaries | 미완료 | 매핑 추가 필요 |
| `career_duties` | `job_description` | careers | 완료 | relation_updaters.py |
| `certificate_issuer` | `issuing_organization` | certificates | 완료 | relation_updaters.py |
| `certificate_date` | `acquisition_date` | certificates | 완료 | relation_updaters.py |
| `language_test_name` | `exam_name` | languages | 완료 | relation_updaters.py (2025-12-16 수정) |
| `language_test_date` | `acquisition_date` | languages | 완료 | relation_updaters.py (2025-12-16 수정) |
| `language_name` | `language_name` | languages | 완료 | relation_updaters.py (2025-12-16 수정) |
| `family_phone` | `contact` | family_members | 완료 | relation_updaters.py |
| `family_living_together` | `is_cohabitant` | family_members | 완료 | relation_updaters.py |
| `military_branch` | `branch` | military_services | 완료 | relation_updaters.py |
| `award_notes` | `note` | awards | 미완료 | 매핑 추가 필요 |

### 17.2 템플릿에만 존재 (DB 컬럼 없음)

| 템플릿 필드 | 섹션 | 권장 조치 |
|-------------|------|-----------|
| `probation_end` | 계약정보 | DB 컬럼 추가 |
| `resignation_date` | 계약정보 | DB 컬럼 추가 |
| `bonus_rate` | 급여정보 | DB 컬럼 추가 |
| `bank_name` | 급여정보 | DB 컬럼 추가 |
| `national_pension_number/date` | 4대보험 | DB 스키마 확장 |
| `health_insurance_number/date` | 4대보험 | DB 스키마 확장 |
| `employment_insurance_number/date` | 4대보험 | DB 스키마 확장 |
| `industrial_insurance_number/date` | 4대보험 | DB 스키마 확장 |
| `pension_exempt`, `health_exempt`, `employment_exempt` | 4대보험 | DB 스키마 확장 |
| `military_period`, `military_duty`, `military_specialty` | 병역정보 | DB 컬럼 추가 |
| `award_description` | 수상내역 | DB 컬럼 추가 |

### 17.3 DB에만 존재 (템플릿 미사용)

| DB 컬럼 | 테이블 | 설명 |
|---------|--------|------|
| `chinese_name` | employees | 한자명 |
| `lunar_birth` | employees | 음력 생일 여부 |
| `nationality` | employees | 국적 |
| `mobile_phone` | employees | 휴대폰 (phone과 중복?) |
| `home_phone` | employees | 자택전화 |
| `contract_date` | contracts | 계약일 |
| `work_type` | contracts | 근무 형태 |
| `payment_day` | salaries | 지급일 |
| `payment_method` | salaries | 지급방법 |
| `monthly_salary` | salaries | 월급여 |
| `total_salary` | salaries | 총급여 |
| `*_rate` | insurances | 보험 요율 |
| `is_dependent` | family_members | 부양 여부 |
| `enlistment_date`, `discharge_date` | military_services | 입대일/제대일 |
| `service_type` | military_services | 복무 유형 |
| `school_type`, `admission_date`, `location` | educations | 학교유형/입학일/소재지 |
| `resignation_reason`, `is_current` | careers | 퇴사사유/현재근무여부 |
| `duration` | hr_projects | 기간 |
| `duration` | project_participations | 기간 |

---

## 18. 권장 조치 우선순위

### Priority 1: 즉시 수정 (데이터 저장 영향) - 완료

1. **모델 프로퍼티 추가** (2025-12-16 완료):
   - `Employee.employment_type` 프로퍼티 추가 (`employee.py:94-98`)
   - `Salary.transport_allowance` 프로퍼티 추가 (`salary.py:42-50`)
   - `Salary.pay_type` 프로퍼티 추가 (`salary.py:52-60`)

2. **from_dict 매핑 추가** (2025-12-16 완료):
   - `Contract.from_dict`: `employment_type` → `employee_type` (`contract.py:43-44`)
   - `Salary.from_dict`: `transport_allowance` → `transportation_allowance` (`salary.py:99-100`)
   - `Salary.from_dict`: `pay_type` → `salary_type` (`salary.py:94-95`)

3. **동적 폼 필드 매핑** (2025-12-16 완료):
   - `relation_updaters.py` Language updater 수정:
     - `name` → `language_name` (기존: `language`)
     - `test_name` → `exam_name` (기존: `test_name`)
     - `test_date` → `acquisition_date` (기존: `test_date`)

4. **미완료 항목**:
   - `account_number` ↔ `bank_account` 매핑
   - `award_notes` ↔ `note` 매핑

### Priority 2: DB 스키마 확장 (기능 완성도) - 미완료

1. 4대보험 상세 필드 추가
2. 병역정보 확장 필드 추가
3. 계약정보 필드 추가 (`probation_end`, `resignation_date`)

### Priority 3: 정리 (코드 품질) - 미완료

1. 미사용 DB 컬럼 검토 및 정리
2. 템플릿-DB 네이밍 컨벤션 통일

---

## 19. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-12-16 | 1.0 | 최초 작성 |
| 2025-12-16 | 1.1 | Priority 1 필드 매핑 완료 반영 |

---

**문서 버전**: 1.1
**마지막 업데이트**: 2025-12-16
