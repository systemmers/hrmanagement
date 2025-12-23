# 3개 계정 유형 디테일/수정 페이지 필드 순서 비교 분석 보고서

## 분석 개요

**분석 대상**: personal(개인), corporate_admin(법인 관리자), employee(법인 직원) 3개 계정 유형
**분석 범위**: 디테일 페이지(출력/조회) + 수정 페이지(입력/편집) + API 입출력(to_dict/from_dict)
**분석 깊이**: Deep (--think-hard --depth deep)

---

## 1. 법인 직원 (Employee) 상세 분석

### 1.1 디테일 페이지 (출력) - 섹션 순서

| 순서 | 섹션 ID | 섹션명 | 필드 수 | 주요 필드 |
|:----:|---------|--------|:-------:|----------|
| 1 | personal-info | 개인 기본정보 | 16 | 성명, 여권명, 주민등록번호, 생년월일, 성별, 결혼여부, 휴대전화, 개인이메일, 비상연락처, 혈액형, 종교, 취미, 특기, 장애정보, 주소, 실제거주주소 |
| 2 | organization-info | 소속정보 | 14 | 소속, 부서, 직위, 직급, 직책, 직무, 사원번호, 근무형태, 근무지, 내선번호, 회사이메일, 재직상태, 입사일, 재직기간 |
| 3 | contract-info | 계약정보 | 9 | 계약형태, 계약기간, 계약시작일, 직원유형, 근무형태, 시용기간종료, 근무시간, 휴게시간, 퇴사일 |
| 4 | salary-info | 급여정보 | 9 | 급여형태, 기본급, 직책수당, 식대, 교통비, 총급여, 급여지급일, 급여지급방법, 급여계좌 |
| 5 | benefit-info | 연차/복리후생 | 5 | 연차발생일수, 연차사용일수, 연차잔여일수, 퇴직금유형, 퇴직금적립방법 |
| 6 | insurance-info | 4대보험 | 5 | 4대보험가입여부, 건강보험, 국민연금, 고용보험, 산재보험 |
| 7 | family-info | 가족정보 | 6 | 관계, 성명, 생년월일, 직업, 연락처, 동거여부 |
| 8 | education-info | 학력정보 | 7 | 학력구분, 학교명, 졸업년월, 전공, 학점, 졸업유무, 비고 |
| 9 | career-info | 경력정보 | 10 | 직장명, 부서, 직위, 직급, 직책, 직무, 재직기간, 급여유형, 연봉/월급, 담당업무 |
| 10 | certificate-info | 자격증/면허 | 6 | 구분, 종류, 등급/점수, 발행처, 취득일, 비고 |
| 11 | language-info | 언어능력 | 5 | 언어, 수준, 시험명, 점수, 취득일 |
| 12 | military-info | 병역정보 | 7 | 병역구분, 군별, 복무기간, 계급, 보직, 병과, 면제사유 |
| 13 | award-info | 수상내역 | 5 | 수상일, 수상명, 수여기관, 수상내용, 비고 |
| 14 | project-participation | 프로젝트 참여이력 | 7 | 사업명, 참여기간, 기간, 담당업무, 역할/직책, 발주처 |
| 15 | employment-contract | 근로계약/연봉 | 3테이블 | **디테일 전용** - 근로계약이력, 연봉계약이력, 급여지급이력 |
| 16 | personnel-movement | 인사이동/고과 | 3테이블 | **디테일 전용** - 인사이동/승진, 인사고과, 교육훈련 |
| 17 | hr-project-info | 프로젝트 | 7 | **디테일 전용** - 프로젝트명, 참여기간, 기간, 담당업무, 역할/직책, 발주처 |
| 18 | attendance-assets | 근태/비품 | 2테이블 | **디테일 전용** - 근태현황, 비품지급 |

### 1.2 수정 페이지 (입력) - 섹션 순서

| 순서 | 섹션 ID | 섹션명 | 필수 필드 | 선택 필드 |
|:----:|---------|--------|----------|----------|
| 1 | personal-info | 개인 기본정보 | 이름*, 휴대전화*, 이메일* | 영문이름, 생년월일, 성별, 결혼여부, 주소, 상세주소, 비상연락처, 비상연락처관계, 주민등록번호, 혈액형, 종교, 취미, 특기, 장애정보, 실제거주지, 실제거주지상세주소, **명함(앞/뒤)** |
| 2 | account-info | 계정정보 | **수정 전용** (신규등록시) - username*, password*, user_role* | |
| 3 | organization-info | 소속정보 | 소속조직*, 직위* | 사번(자동생성), 부서명, 팀, 직급, 직책, 직무, 근무지, 내선번호, 회사이메일 |
| 4 | contract-info | 계약정보 | 입사일*, 재직상태* | 고용형태, 계약기간, 수습종료일, 퇴사일 |
| 5 | salary-info | 급여정보 | (없음) | 기본급, 직책수당, 식대, 교통비, 상여금률, 급여지급방식, 은행, 계좌번호, **포괄임금제 8개(읽기전용)** |
| 6 | benefit-info | 연차/복리후생 | **(읽기전용, 수정모드만)** | 연차발생/사용/잔여일수, 퇴직금유형, 퇴직금적립방법, 기준년도 |
| 7 | insurance-info | 4대보험 | (없음) | 국민연금가입번호/취득일, 건강보험가입번호/취득일, 고용보험가입번호/취득일, 산재보험가입번호/취득일, 보험적용제외(체크박스) |
| 8 | family-info | 가족정보 | (동적 추가) | 관계, 성명, 생년월일, 직업, 연락처, 동거여부 |
| 9 | education-info | 학력정보 | (동적 추가) | 학력구분, 학교명, 졸업년월, 전공, 학점, 비고 |
| 10 | career-info | 경력정보 | (동적 추가) | 직장명, 부서, 직위, 직급, 직책, 직무, 재직기간, 급여유형, 연봉/월급, 담당업무 |
| 11 | certificate-info | 자격증 | (동적 추가) | 종류, 등급/점수, 발행처, 취득일, 만료일 |
| 12 | language-info | 언어능력 | (동적 추가) | 언어, 수준, 시험명, 점수, 취득일 |
| 13 | military-info | 병역정보 | (없음) | 병역구분, 군별, 복무시작, 복무종료, 계급, 보직, 병과, 면제사유 |
| 14 | award-info | 수상내역 | (동적 추가) | 수상일, 수상명, 수여기관, 수상내용, 비고 |
| 15 | project-participation | 프로젝트 참여이력 | (동적 추가) | 사업명, 참여기간, 기간, 담당업무, 역할/직책, 발주처 |
| 16 | project-info | 프로젝트 | **(수정모드만, 동적 추가)** | 프로젝트명, 참여기간, 기간, 담당업무, 역할/직책, 발주처 |

### 1.3 디테일 vs 수정 순서 차이 (Employee)

| 순서 | 디테일 페이지 | 수정 페이지 | 차이 |
|:----:|--------------|------------|------|
| 1 | 개인 기본정보 | 개인 기본정보 | 동일 |
| 2 | 소속정보 | **계정정보** | **수정에만 존재 (21번/22번 원칙)** |
| 3 | 계약정보 | 소속정보 | 순서 밀림 |
| 4 | 급여정보 | 계약정보 | 순서 밀림 |
| 5 | 연차/복리후생 | 급여정보 | 순서 밀림 |
| 6 | 4대보험 | 연차/복리후생 | 순서 밀림 |
| 7 | 가족정보 | 4대보험 | 순서 밀림 |
| 8 | 학력정보 | 가족정보 | 순서 밀림 |
| 9-14 | ... | ... | 동일 (1칸씩 밀림) |
| 15-18 | 인사기록 4개 | X | **디테일에만 존재** |
| - | X | 프로젝트 (16번) | **수정에만 존재 (수정모드)** |

**핵심 차이**:
- 수정 페이지: 계정정보(2번) 삽입 → 이후 섹션 1칸씩 밀림
- 디테일 페이지: 인사기록 4개 섹션 (15-18번) 추가

---

## 2. 개인 계정 (Personal) 상세 분석

### 2.1 디테일 페이지 (출력) - 섹션 순서

| 순서 | 섹션 ID | 섹션명 | 필드 수 | 비고 |
|:----:|---------|--------|:-------:|------|
| 1 | personal-info | 개인 기본정보 | 16 | Employee 1번과 동일 |
| 2 | family-info | 가족정보 | 6 | Employee 7번과 동일 |
| 3 | education-info | 학력정보 | 7 | Employee 8번과 동일 |
| 4 | career-info | 경력정보 | 10 | Employee 9번과 동일 |
| 5 | certificate-info | 자격증/면허 | 6 | Employee 10번과 동일 |
| 6 | language-info | 언어능력 | 5 | Employee 11번과 동일 |
| 7 | military-info | 병역정보 | 7 | Employee 12번과 동일 |
| 8 | award-info | 수상내역 | 5 | Employee 13번과 동일 |
| 9 | project-participation | 프로젝트 참여이력 | 7 | Employee 14번과 동일 |

**제외된 섹션 (인사카드 전용)**: 소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 인사기록 4개

### 2.2 수정 페이지 (입력) - 섹션 순서

| 순서 | 섹션 ID | 섹션명 | 필수 필드 | 선택 필드 |
|:----:|---------|--------|----------|----------|
| 1 | personal-info | 개인 기본정보 | 이름*, 휴대전화*, 이메일* | Employee와 동일 (명함 제외) |
| 2 | family-info | 가족정보 | (동적 추가) | Employee와 동일 |
| 3 | education-info | 학력정보 | (동적 추가) | Employee와 동일 |
| 4 | career-info | 경력정보 | (동적 추가) | Employee와 동일 |
| 5 | certificate-info | 자격증 | (동적 추가) | Employee와 동일 |
| 6 | language-info | 언어능력 | (동적 추가) | Employee와 동일 |
| 7 | military-info | 병역정보 | (없음) | Employee와 동일 |
| 8 | award-info | 수상내역 | (동적 추가) | Employee와 동일 |
| 9 | project-participation | 프로젝트 참여이력 | (동적 추가) | Employee와 동일 |

### 2.3 디테일 vs 수정 순서 차이 (Personal)

**순서 완전 일치** - 법인 전용 섹션이 없어서 단순한 구조

---

## 3. 법인 관리자 (Corporate Admin) 상세 분석

### 3.1 디테일 페이지 (출력) - 섹션 순서

| 순서 | 섹션 ID | 섹션명 | 필드 수 | 비고 |
|:----:|---------|--------|:-------:|------|
| 1 | personal-info | 개인 기본정보 | 16 | Employee 1번과 동일 |
| 2 | education-info | 학력정보 | 7 | 빈 목록으로 표시 |
| 3 | career-info | 경력정보 | 10 | 빈 목록으로 표시 |
| 4 | certificate-info | 자격증/면허 | 6 | 빈 목록으로 표시 |
| 5 | language-info | 언어능력 | 5 | 빈 목록으로 표시 |
| 6 | military-info | 병역정보 | 7 | None으로 표시 |
| 7 | award-info | 수상내역 | 5 | 빈 목록으로 표시 |

**제외된 섹션**: 가족정보, 프로젝트 참여이력, 첨부파일 사이드바

### 3.2 수정 페이지 (입력) - 섹션 순서

| 순서 | 섹션 ID | 섹션명 | 필수 필드 | 선택 필드 |
|:----:|---------|--------|----------|----------|
| 1 | personal-info | 개인 기본정보 | 이름*, 휴대전화*, 이메일* | Employee와 동일 (명함 제외) |
| 2 | education-info | 학력정보 | (동적 추가) | Employee와 동일 |
| 3 | career-info | 경력정보 | (동적 추가) | Employee와 동일 |
| 4 | certificate-info | 자격증 | (동적 추가) | Employee와 동일 |
| 5 | language-info | 언어능력 | (동적 추가) | Employee와 동일 |
| 6 | military-info | 병역정보 | (없음) | Employee와 동일 |
| 7 | award-info | 수상내역 | (동적 추가) | Employee와 동일 |

### 3.3 디테일 vs 수정 순서 차이 (Corporate Admin)

**순서 완전 일치** - 가장 단순한 구조

---

## 4. API 필드 순서 비교 (to_dict vs from_dict)

### 4.1 Employee 모델

#### to_dict() 출력 순서 (47개 필드)

| 그룹 | 순서 | 필드명 |
|------|:----:|--------|
| 기본 | 1-9 | id, name, photo, department, position, status, hire_date, phone, email |
| 조직 | 10-11 | organization_id, **organization (nested)** |
| 개인 | 12-29 | english_name ~ marital_status |
| 실거주 | 30-32 | actual_postal_code ~ actual_detailed_address |
| 비상 | 33-34 | emergency_contact, emergency_relation |
| 소속 | 35-42 | team ~ employee_number |
| 스냅샷 | 43-47 | **profile_id ~ data_retention_until (출력 전용)** |

#### from_dict() 입력 순서 (41개 필드)

| 그룹 | 순서 | 필드명 |
|------|:----:|--------|
| 기본 | 1-10 | id ~ organization_id |
| 소속 | 11-18 | employee_number ~ company_email |
| 개인 | 19-41 | english_name ~ emergency_relation |

**출력 전용 필드**: organization (nested), profile_snapshot, snapshot_at, resignation_date, data_retention_until

### 4.2 Profile 모델

#### to_dict() 출력 순서 (35개 필드)

| 그룹 | 순서 | 필드명 |
|------|:----:|--------|
| 기본 | 1-9 | id ~ gender |
| 계산 | 10 | **age (@property)** |
| 연락 | 11-17 | mobile_phone ~ **full_address (@property)** |
| 상세 | 18-25 | nationality ~ marital_status |
| 실거주 | 26-29 | actual_* ~ **actual_full_address (@property)** |
| 비상 | 30-31 | emergency_contact, emergency_relation |
| 메타 | 32-35 | is_public, **is_personal (@property)**, created_at, updated_at |

#### from_dict() 입력 순서 (28개 필드)

**to_dict와 거의 동일 순서** (단순 개인정보 모델)

**출력 전용 필드**: age, full_address, actual_full_address, is_personal, created_at, updated_at

### 4.3 CorporateAdminProfile 모델

**DictSerializableMixin 자동 생성** - 컬럼 정의 순서 = to_dict 출력 순서

| 순서 | 필드명 | camelCase |
|:----:|--------|-----------|
| 1-3 | id, user_id, company_id | userId, companyId |
| 4-6 | name, english_name, position | englishName |
| 7-9 | mobile_phone, office_phone, email | mobilePhone, officePhone |
| 10-12 | photo, department, bio | |
| 13-15 | is_active, created_at, updated_at | isActive, createdAt, updatedAt |

**출력 전용 필드**: created_at, updated_at

---

## 5. 관계 모델 필드 순서

### 5.1 Education (DictSerializableMixin)

```
id → employee_id → profile_id → school_type → school_name → major → degree
→ admission_date → graduation_date → graduation_status → gpa → location → note
```

**Alias**: school→school_name, status→graduation_status, notes→note
**Computed**: graduation_year

### 5.2 Career (DictSerializableMixin)

```
id → employee_id → profile_id → company_name → department
→ position → job_grade → job_title → job_role → job_description
→ start_date → end_date → salary → salary_type → monthly_salary → pay_step
→ resignation_reason → is_current → note
```

**Alias**: company→company_name, duty→job_description, reason_for_leaving→resignation_reason

### 5.3 Salary (법인 전용)

```
id → employee_id → salary_type → base_salary → position_allowance
→ meal_allowance → transportation_allowance → total_salary
→ payment_day → payment_method → bank_account → note
→ annual_salary → monthly_salary → hourly_wage
→ overtime_hours → night_hours → holiday_days
→ overtime_allowance → night_allowance → holiday_allowance
```

**Alias**: transport_allowance→transportation_allowance, pay_type→salary_type

### 5.4 Contract (법인 전용)

```
id → employee_id → contract_date → contract_type → contract_period
→ employee_type → work_type → note
```

### 5.5 Insurance (법인 전용)

```
id → employee_id → national_pension → health_insurance
→ employment_insurance → industrial_accident
→ national_pension_rate → health_insurance_rate
→ long_term_care_rate → employment_insurance_rate → note
```

### 5.6 Benefit (법인 전용)

```
id → employee_id → year → annual_leave_granted → annual_leave_used
→ annual_leave_remaining → severance_type → severance_method → note
```

---

## 6. 어댑터 필드 순서

### 6.1 EmployeeProfileAdapter.get_basic_info()

```
id → name → english_name → chinese_name → birth_date → lunar_birth → gender
→ mobile_phone → home_phone → email → address → detailed_address → postal_code
→ photo → employee_number → nationality → blood_type → religion → hobby
→ specialty → disability_info → marital_status
→ actual_postal_code → actual_address → actual_detailed_address
→ emergency_contact → emergency_relation
```

### 6.2 PersonalProfileAdapter.get_basic_info()

```
id → name → english_name → chinese_name → resident_number → birth_date
→ lunar_birth → gender → mobile_phone → phone (템플릿 호환) → home_phone
→ email → address → detailed_address → postal_code → photo
→ employee_number (None) → nationality → blood_type → religion → hobby
→ specialty → disability_info → marital_status
→ actual_postal_code → actual_address → actual_detailed_address
→ emergency_contact → emergency_relation → is_public
```

### 6.3 CorporateAdminProfileAdapter.get_basic_info()

```
id → name → english_name → chinese_name (None) → birth_date (None)
→ lunar_birth (None) → gender (None) → mobile_phone → home_phone (None)
→ email → address (None) → detailed_address (None) → postal_code (None)
→ photo → employee_number (None) → nationality (None) → blood_type (None)
→ religion (None) → hobby (None) → specialty (None) → disability_info (None)
→ position → department → office_phone → bio
```

---

## 7. 종합 비교표

### 7.1 섹션 가용성 매트릭스

| 순서 | 섹션 | Employee 디테일 | Employee 수정 | Personal 디테일 | Personal 수정 | Corp Admin 디테일 | Corp Admin 수정 |
|:----:|------|:---------------:|:-------------:|:---------------:|:-------------:|:-----------------:|:---------------:|
| 1 | 개인 기본정보 | O | O | O | O | O | O |
| 2 | 계정정보 | X | **O (신규)** | X | X | X | X |
| 3 | 소속정보 | O | O | X | X | X | X |
| 4 | 계약정보 | O | O | X | X | X | X |
| 5 | 급여정보 | O | O | X | X | X | X |
| 6 | 연차/복리후생 | O | R | X | X | X | X |
| 7 | 4대보험 | O | O | X | X | X | X |
| 8 | 가족정보 | O | O | O | O | X | X |
| 9 | 학력정보 | O | O | O | O | - | O |
| 10 | 경력정보 | O | O | O | O | - | O |
| 11 | 자격증 | O | O | O | O | - | O |
| 12 | 언어능력 | O | O | O | O | - | O |
| 13 | 병역정보 | O | O | O | O | - | O |
| 14 | 수상내역 | O | O | O | O | - | O |
| 15 | 프로젝트 참여이력 | O | O | O | O | X | X |
| 16 | 근로계약/연봉 | **O** | X | X | X | X | X |
| 17 | 인사이동/고과 | **O** | X | X | X | X | X |
| 18 | 프로젝트 (인사기록) | **O** | R | X | X | X | X |
| 19 | 근태/비품 | **O** | X | X | X | X | X |

**범례**: O = 표시/편집, R = 읽기전용, X = 미표시, - = 빈 목록

### 7.2 디테일 vs 수정 필드 차이

| 구분 | 디테일 전용 (출력) | 수정 전용 (입력) |
|------|-------------------|------------------|
| **섹션** | 근로계약/연봉, 인사이동/고과, 프로젝트(인사기록), 근태/비품 | 계정정보 (21번/22번 원칙) |
| **필드** | 재직기간(계산), 총급여(계산), 나이(계산), 전체주소(조합) | 프로필 사진 업로드, 명함 업로드, 주소 검색 버튼, 조직 트리 선택, 동적 추가/삭제 버튼, 포괄임금 계산기 |
| **API** | organization (nested), profile_snapshot, age, full_address, is_personal | 없음 |

### 7.3 순서 불일치 요약

| 계정 | 디테일 섹션 수 | 수정 섹션 수 | 순서 차이 원인 |
|------|:-------------:|:------------:|---------------|
| **Employee** | 18개 | 16개 | 계정정보(2번) 삽입 → 이후 1칸씩 밀림, 인사기록 4개(디테일 전용) |
| **Personal** | 9개 | 9개 | 순서 완전 일치 |
| **Corp Admin** | 7개 | 7개 | 순서 완전 일치 |

### 7.4 to_dict vs from_dict 순서 차이

| 모델 | to_dict 특징 | from_dict 특징 | 차이 |
|------|-------------|---------------|------|
| **Employee** | 기본→조직(nested)→개인→소속→스냅샷 | 기본→조직ID→소속→개인 | 표시 순서 vs 입력 논리 순서 |
| **Profile** | 기본→계산(@property)→연락→실거주→메타 | 기본→연락→실거주→메타 | @property 필드 제외 |
| **CorporateAdmin** | 컬럼 정의 순서 (자동) | camelCase 매핑 (순서 무관) | DictSerializableMixin |

---

## 8. 핵심 발견사항

### 8.1 순서 일관성

1. **공통 패턴**: 기본→이름확장→생년월일→연락처→주소→신분→개인정보→실거주→비상연락
2. **계정별 확장**: Employee만 조직/소속 정보 추가 (2-7번 섹션)
3. **모델 vs 어댑터**: 모델은 전체 필드, 어댑터는 섹션별 그룹핑

### 8.2 입출력 불일치

1. **Employee to_dict vs from_dict**: 조직 정보 배치 순서 상이
2. **@property 필드**: age, full_address 등은 출력 전용
3. **Alias 필드**: 템플릿 호환성 위해 여러 이름 지원

### 8.3 조건부 렌더링

**템플릿 조건 체계**:
- `page_mode == 'hr_card'` → 법인 직원 전용 섹션
- `account_type != 'corporate_admin'` → 가족정보, 프로젝트참여이력
- `action != 'create'` → 수정 모드 전용 섹션

---

## 9. 권장사항

1. **FieldRegistry 확대**: 중앙집중식 필드 순서 관리 (현재 부분 도입)
2. **Mixin 전환**: Employee도 DictSerializableMixin 사용 고려
3. **어댑터 표준화**: 모든 어댑터 get_*_info() 순서를 FieldRegistry 기반으로 통일
4. **순서 불일치 해결**: to_dict와 from_dict 순서 통일 검토

---

## 10. 개인 vs 법인 직원 필드 세부 비교 분석

### 10.1 모델 수준 필드 비교

#### 10.1.1 공통 필드 (Profile ∩ Employee) - 25개

| 순서 | 필드명 | Profile | Employee | 데이터 타입 | 용도 |
|:----:|--------|:-------:|:--------:|-------------|------|
| 1 | `name` | O | O | String(100) | 이름 (한글, 필수) |
| 2 | `english_name` | O | O | String(100) | 여권명 (영문) |
| 3 | `chinese_name` | O | O | String(100) | 한자명 |
| 4 | `photo` | O | O | String(500) | 프로필 사진 URL |
| 5 | `birth_date` | O | O | String(20) | 생년월일 |
| 6 | `lunar_birth` | O | O | Boolean | 음력 여부 |
| 7 | `gender` | O | O | String(10) | 성별 |
| 8 | `mobile_phone` | O | O | String(50) | 휴대전화 |
| 9 | `home_phone` | O | O | String(50) | 자택전화 |
| 10 | `email` | O | O | String(200) | 개인 이메일 |
| 11 | `postal_code` | O | O | String(20) | 우편번호 |
| 12 | `address` | O | O | String(500) | 주민등록상 주소 |
| 13 | `detailed_address` | O | O | String(500) | 상세주소 |
| 14 | `resident_number` | O | O | String(20) | 주민등록번호 |
| 15 | `nationality` | O | O | String(50) | 국적 |
| 16 | `blood_type` | O | O | String(10) | 혈액형 |
| 17 | `religion` | O | O | String(50) | 종교 |
| 18 | `hobby` | O | O | String(200) | 취미 |
| 19 | `specialty` | O | O | String(200) | 특기 |
| 20 | `disability_info` | O | O | Text | 장애정보 |
| 21 | `marital_status` | O | O | String(20) | 결혼여부 |
| 22 | `actual_postal_code` | O | O | String(20) | 실제 거주지 우편번호 |
| 23 | `actual_address` | O | O | String(500) | 실제 거주지 주소 |
| 24 | `actual_detailed_address` | O | O | String(500) | 실제 거주지 상세주소 |
| 25 | `emergency_contact` | O | O | String(50) | 비상연락처 |
| 26 | `emergency_relation` | O | O | String(50) | 비상연락처 관계 |

#### 10.1.2 개인 전용 필드 (Profile Only) - 4개

| 필드명 | 데이터 타입 | 용도 | 비고 |
|--------|-------------|------|------|
| `user_id` | Integer (FK) | User 계정 연결 | 1:1 관계 |
| `is_public` | Boolean | 프로필 공개 여부 | 기본값: False |
| `created_at` | DateTime | 생성일시 | 자동 |
| `updated_at` | DateTime | 수정일시 | 자동 |

#### 10.1.3 법인 직원 전용 필드 (Employee Only) - 24개

**기본/조직 정보 (10개)**:

| 필드명 | 데이터 타입 | 용도 |
|--------|-------------|------|
| `employee_number` | String(20) | 사번 (EMP-YYYY-NNNN) |
| `profile_id` | Integer (FK) | 통합 프로필 연결 |
| `organization_id` | Integer (FK) | 조직 연결 |
| `company_id` | Integer (FK) | 회사 연결 |
| `department` | String(100) | 부서 |
| `position` | String(100) | 직위 (서열) |
| `status` | String(50) | 재직상태 |
| `hire_date` | String(20) | 입사일 |
| `team` | String(100) | 팀 |
| `job_grade` | String(50) | 직급 (역량 레벨) |

**직무/연락 정보 (5개)**:

| 필드명 | 데이터 타입 | 용도 |
|--------|-------------|------|
| `job_title` | String(100) | 직책 (팀장, 본부장) |
| `job_role` | String(100) | 직무 (인사기획, 회계관리) |
| `work_location` | String(200) | 근무지 |
| `internal_phone` | String(50) | 내선번호 |
| `company_email` | String(200) | 회사 이메일 |

**스냅샷/퇴직 정보 (4개)**:

| 필드명 | 데이터 타입 | 용도 |
|--------|-------------|------|
| `profile_snapshot` | JSONB | 퇴사 시점 프로필 스냅샷 |
| `snapshot_at` | DateTime | 스냅샷 생성 시점 |
| `resignation_date` | Date | 퇴직일 |
| `data_retention_until` | Date | 데이터 보관 만료일 |

### 10.2 관계 데이터 비교

#### 10.2.1 공통 이력 데이터 (1:N, 양쪽 모두 사용) - 8개

| 관계 모델 | Profile | Employee | 연결 방식 |
|-----------|:-------:|:--------:|-----------|
| `Education` | O | O | `profile_id` 또는 `employee_id` |
| `Career` | O | O | `profile_id` 또는 `employee_id` |
| `Certificate` | O | O | `profile_id` 또는 `employee_id` |
| `Language` | O | O | `profile_id` 또는 `employee_id` |
| `MilitaryService` | O (1:N) | O (1:1) | `profile_id` 또는 `employee_id` |
| `FamilyMember` | O | O | `profile_id` 또는 `employee_id` |
| `Award` | O | O | `profile_id` 또는 `employee_id` |
| `ProjectParticipation` | O | O | `profile_id` 또는 `employee_id` |

#### 10.2.2 법인 직원 전용 관계 데이터 - 14개

**1:1 관계 (4개)**:

| 관계 모델 | 용도 |
|-----------|------|
| `Salary` | 급여 정보 (기본급, 수당, 총급여) |
| `Contract` | 계약 정보 (계약형태, 근무형태, 시용기간) |
| `Benefit` | 복리후생 (연차, 퇴직금 유형) |
| `Insurance` | 4대보험 (국민연금, 건강보험, 고용보험, 산재보험) |

**1:N 관계 (10개)**:

| 관계 모델 | 용도 |
|-----------|------|
| `SalaryHistory` | 급여 이력 |
| `Promotion` | 승진 이력 |
| `Evaluation` | 평가 이력 |
| `Training` | 교육 이력 |
| `Attendance` | 근태 기록 |
| `HrProject` | 인사이력 프로젝트 |
| `Asset` | 비품 관리 |
| `SalaryPayment` | 급여 지급 이력 |
| `AnnualContract` | 연봉 계약 |
| `Attachment` | 첨부파일 |

### 10.3 어댑터 메서드 비교

| 메서드명 | PersonalProfileAdapter | EmployeeProfileAdapter | 차이점 |
|----------|:----------------------:|:----------------------:|--------|
| `get_basic_info()` | O (25개 필드) | O (25개 필드 + 사번) | Employee만 `employee_number` 포함 |
| `get_organization_info()` | X (None) | O (11개 필드) | 법인 전용 |
| `get_contract_info()` | X (None) | O (Contract.to_dict) | 법인 전용 |
| `get_salary_info()` | X (None) | O (Salary.to_dict) | 법인 전용 |
| `get_benefit_info()` | X (None) | O (Benefit.to_dict) | 법인 전용 |
| `get_insurance_info()` | X (None) | O (Insurance.to_dict) | 법인 전용 |
| `get_education_list()` | O (profile.educations) | O (employee.educations) | 동일 구조 |
| `get_career_list()` | O (profile.careers) | O (employee.careers) | 동일 구조 |
| `get_certificate_list()` | O | O | 동일 구조 |
| `get_language_list()` | O | O | 동일 구조 |
| `get_military_info()` | O (1:N, first()) | O (1:1) | 관계 타입 차이 |
| `get_family_list()` | O | O | 동일 구조 |
| `get_award_list()` | O | O | 동일 구조 |
| `get_project_participation_list()` | O | O | 동일 구조 |
| `is_corporate()` | False | True | 타입 구분 |
| `get_account_type()` | `'personal'` | `'corporate'` | 타입 구분 |
| `get_available_sections()` | 9개 | 14개 | 법인 전용 5개 추가 |

### 10.4 필드별 매핑 관계

#### 별칭(Alias) 필드

| 원본 필드 (모델) | 별칭 (어댑터/템플릿) | 사용처 |
|------------------|---------------------|--------|
| `mobile_phone` | `phone` | PersonalProfileAdapter에서 템플릿 호환용 |
| `english_name` | `name_en`, `englishName` | 템플릿 입력, camelCase 변환 |
| `resident_number` | `rrn`, `residentNumber` | 템플릿 입력, camelCase 변환 |

#### camelCase vs snake_case 변환 (17개)

| snake_case (DB) | camelCase (Frontend) |
|-----------------|----------------------|
| `english_name` | `englishName` |
| `chinese_name` | `chineseName` |
| `birth_date` | `birthDate` |
| `lunar_birth` | `lunarBirth` |
| `mobile_phone` | `mobilePhone` |
| `home_phone` | `homePhone` |
| `postal_code` | `postalCode` |
| `detailed_address` | `detailedAddress` |
| `resident_number` | `residentNumber` |
| `blood_type` | `bloodType` |
| `disability_info` | `disabilityInfo` |
| `marital_status` | `maritalStatus` |
| `actual_postal_code` | `actualPostalCode` |
| `actual_address` | `actualAddress` |
| `actual_detailed_address` | `actualDetailedAddress` |
| `emergency_contact` | `emergencyContact` |
| `emergency_relation` | `emergencyRelation` |

---

## 11. 왜 필드 구조가 다른가? (원인 분석)

### 11.1 도메인 모델 차이

| 구분 | 개인 계정 (Personal) | 법인 직원 (Employee) |
|------|---------------------|---------------------|
| **핵심 목적** | 개인 이력서/포트폴리오 관리 | 인사카드/인사관리 시스템 |
| **데이터 주체** | 본인 | 회사 (인사팀) |
| **소유권** | 개인 | 법인 |
| **접근 권한** | 본인만 | 인사관리자 + 본인 |
| **보관 의무** | 없음 | 법적 의무 (근로기준법) |

### 11.2 비즈니스 요구사항 차이

#### 개인 계정만 필요한 기능

| 기능 | 필드 | 이유 |
|------|------|------|
| 프로필 공개 설정 | `is_public` | 이력서 공유, 헤드헌터 열람 허용 |
| User 계정 연결 | `user_id` | 로그인 연동 (1:1) |

#### 법인 직원만 필요한 기능

| 기능 | 관련 필드/모델 | 이유 |
|------|---------------|------|
| 조직 관리 | `organization_id`, `department`, `team` | 조직도 구성, 부서 배치 |
| 직위/직급 체계 | `position`, `job_grade`, `job_title`, `job_role` | 인사 서열, 역량 평가, 책임 범위 |
| 급여 관리 | `Salary`, `SalaryHistory`, `SalaryPayment` | 급여 계산, 지급 이력 |
| 계약 관리 | `Contract`, `AnnualContract` | 고용 형태, 계약 기간 |
| 4대보험 | `Insurance` | 법적 의무 가입 |
| 연차/복리후생 | `Benefit` | 근로기준법 준수 |
| 인사 평가 | `Evaluation`, `Promotion` | 성과 관리, 승진 |
| 근태 관리 | `Attendance` | 출퇴근, 휴가, 초과근무 |
| 퇴직자 관리 | `profile_snapshot`, `resignation_date`, `data_retention_until` | 법적 보관 의무 |

### 11.3 법적 요구사항

| 법률 | 요구사항 | 해당 필드 |
|------|----------|----------|
| **근로기준법** | 근로계약서 보관 (3년) | `Contract`, `AnnualContract` |
| **근로기준법** | 임금대장 보관 (3년) | `Salary`, `SalaryPayment` |
| **근로기준법** | 연차휴가 관리 | `Benefit.annual_leave_*` |
| **4대보험법** | 가입/취득 기록 | `Insurance` |
| **개인정보보호법** | 퇴직자 정보 보관 기한 | `data_retention_until` |

### 11.4 데이터 관계 차이

```
[개인 계정]
User (1) ←→ (1) Profile ←→ (N) Education, Career, Certificate, ...

[법인 직원]
Company (1) ←→ (N) Organization ←→ (N) Employee
                                      ├── (1) Salary
                                      ├── (1) Contract
                                      ├── (1) Benefit
                                      ├── (1) Insurance
                                      ├── (N) Education, Career, ...
                                      └── (N) SalaryHistory, Attendance, ...
```

**핵심 차이**: 법인 직원은 **조직 계층 구조** 내에 존재하며, **법적 의무**에 따른 추가 데이터 관리가 필요

---

## 12. 공통 관리 가능성 분석 및 제안

### 12.1 현재 통합 상태 평가

| 항목 | 상태 | 평가 |
|------|------|------|
| 개인정보 필드 | 완전 동일 (25개) | 통합 완료 |
| 이력 데이터 | 동일 구조 (8개 모델) | 통합 완료 |
| 어댑터 패턴 | ProfileAdapter 추상화 | 통합 완료 |
| 템플릿 렌더링 | 조건부 렌더링 | 통합 완료 |
| FieldRegistry | 부분 적용 | 확대 필요 |

### 12.2 공통 관리 가능 영역

#### 이미 공통 관리 중인 영역

```
✅ 개인정보 필드 25개 → ProfileAdapter.get_basic_info()
✅ 이력 데이터 8개 모델 → profile_id 또는 employee_id로 연결
✅ 템플릿 렌더링 → 조건부 include로 통합
✅ 필드 순서 → FieldRegistry 일부 적용
```

#### 추가 통합 가능 영역

| 영역 | 현재 상태 | 통합 방안 |
|------|----------|----------|
| **필드 순서** | 분산 정의 | FieldRegistry 확대 |
| **별칭 처리** | 각 모델에서 개별 처리 | FieldRegistry.normalize_field_name() |
| **가시성 로직** | 템플릿/어댑터 중복 | FieldRegistry.Visibility 활용 |
| **to_dict/from_dict** | Employee 수동 구현 | DictSerializableMixin 전환 |

### 12.3 공통 관리 불가능 영역

#### 구조적으로 분리 필요한 영역

| 영역 | 이유 | 현재 상태 |
|------|------|----------|
| **조직 연결** | 법인만 조직 계층 구조 존재 | Employee.organization_id |
| **급여/계약** | 법인만 고용 관계 존재 | Salary, Contract 모델 |
| **4대보험** | 법인만 법적 의무 | Insurance 모델 |
| **인사 기록** | 법인만 인사 관리 필요 | Evaluation, Promotion, Attendance |
| **퇴직자 관리** | 법인만 법적 보관 의무 | profile_snapshot, data_retention_until |

### 12.4 통합 아키텍처 제안

#### 제안 1: FieldRegistry 중심 통합 (권장)

```
┌─────────────────────────────────────────────────────────┐
│                     FieldRegistry                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  공통 섹션 (personal_basic, contact, address, ...)  │ │
│  │  - Visibility.ALL → 모든 계정에서 표시              │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  법인 전용 섹션 (organization, salary, contract...) │ │
│  │  - Visibility.CORPORATE → 법인만 표시              │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    ProfileAdapter                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Personal    │  │  Employee    │  │ CorpAdmin    │   │
│  │  Adapter     │  │  Adapter     │  │  Adapter     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │                 │                 │           │
│         ▼                 ▼                 ▼           │
│   get_basic_info()  → FieldRegistry.to_ordered_dict()   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Template Layer                        │
│  {% for field in adapter.get_ordered_basic_info() %}    │
│      {% if field.is_visible_for(account_type) %}        │
│          {{ render_field(field) }}                       │
│      {% endif %}                                         │
│  {% endfor %}                                            │
└─────────────────────────────────────────────────────────┘
```

#### 제안 2: 통합 BaseProfile + 확장 패턴

```python
# 공통 필드를 BaseProfile로 추출
class BaseProfileMixin:
    """개인/법인 공통 프로필 필드"""
    name = db.Column(db.String(100), nullable=False)
    english_name = db.Column(db.String(100))
    chinese_name = db.Column(db.String(100))
    # ... 25개 공통 필드

    def get_basic_info(self) -> Dict:
        """공통 기본정보 반환"""
        return FieldRegistry.to_ordered_dict('personal_basic', {
            'name': self.name,
            'english_name': self.english_name,
            # ...
        })

# 개인 계정
class Profile(BaseProfileMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=False)

# 법인 직원
class Employee(BaseProfileMixin, db.Model):
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    employee_number = db.Column(db.String(20))
    # ... 법인 전용 필드

    # 1:1 관계
    salary = db.relationship('Salary', uselist=False)
    contract = db.relationship('Contract', uselist=False)
    # ...
```

### 12.5 구현 로드맵

| 단계 | 작업 | 효과 | 위험도 |
|:----:|------|------|:------:|
| **1** | FieldRegistry에 모든 섹션 등록 | 필드 순서 중앙 관리 | 낮음 |
| **2** | 어댑터 get_*_info()를 FieldRegistry 기반으로 수정 | 순서 일관성 확보 | 낮음 |
| **3** | Employee에 DictSerializableMixin 적용 | to_dict/from_dict 자동화 | 중간 |
| **4** | BaseProfileMixin 추출 (선택적) | 코드 중복 제거 | 높음 |

### 12.6 결론

#### 공통 관리 가능한 것

| 영역 | 방법 |
|------|------|
| 개인정보 필드 25개 | FieldRegistry + ProfileAdapter |
| 이력 데이터 8개 모델 | profile_id 통합 (이미 완료) |
| 필드 순서 | FieldRegistry 확대 |
| 별칭/가시성 | FieldRegistry 메서드 활용 |

#### 공통 관리 불가능한 것

| 영역 | 이유 |
|------|------|
| 조직/소속 정보 | 법인만 조직 계층 구조 존재 |
| 급여/계약/보험 | 법인만 고용 관계 및 법적 의무 |
| 인사 기록 | 법인만 인사 관리 프로세스 존재 |

#### 최종 평가

```
현재 아키텍처 점수: ⭐⭐⭐⭐⭐ (5/5)

- 개인정보 필드: 완전히 동일 (100% 호환)
- 어댑터 패턴: ProfileAdapter 추상화 우수
- 템플릿 호환성: 조건부 렌더링 완벽
- FieldRegistry: 부분 적용 (확대 권장)
- 이력 데이터: profile_id 기반 통합 완료

권장사항: FieldRegistry 확대 적용으로 필드 순서 중앙 관리 완성
```

---

## 13. DB 필드 vs UI 노출 불일치 분석

### 13.1 분석 개요

**분석 목적**: 데이터베이스에 정의되어 있지만 UI(템플릿)에서 노출되지 않는 "숨겨진 필드" 식별
**분석 방법**: 모델 컬럼 정의 vs 템플릿 input name 교차 검증

### 13.2 UI 미노출 필드 목록

#### 13.2.1 공통 필드 (Profile + Employee 모두 해당) - 4개

| 필드명 | DB 타입 | 용도 | 미노출 이유 | 권장 조치 |
|--------|---------|------|------------|----------|
| `chinese_name` | String(100) | 한자명 | 템플릿에 입력 필드 없음 | 입력 폼에 추가 또는 필드 제거 결정 필요 |
| `lunar_birth` | Boolean | 음력 생일 여부 | 생년월일 옆 체크박스 누락 | birth_date 옆에 체크박스 추가 권장 |
| `home_phone` | String(50) | 자택 전화 | 휴대전화만 입력 가능 | 필드 추가 또는 컬럼 제거 결정 필요 |
| `nationality` | String(50) | 국적 | 입력 폼에 없음 | 외국인 직원 관리 시 필요, 추가 권장 |

#### 13.2.2 Profile 전용 필드 - 2개

| 필드명 | DB 타입 | 용도 | 미노출 이유 | 권장 조치 |
|--------|---------|------|------------|----------|
| `is_public` | Boolean | 프로필 공개 여부 | 대시보드 `_visibility_status.html`에서만 사용 | 프로필 수정에서 설정 가능하도록 추가 |
| `user_id` | Integer (FK) | User 연결 | 시스템 내부 필드 | 노출 불필요 (정상) |

#### 13.2.3 Employee 전용 필드 - 7개

| 필드명 | DB 타입 | 용도 | 미노출 이유 | 권장 조치 |
|--------|---------|------|------------|----------|
| `profile_id` | Integer (FK) | Profile 연결 | 시스템 내부 필드 | 노출 불필요 (정상) |
| `organization_id` | Integer (FK) | 조직 연결 | 트리 선택기로 간접 설정 | 노출 불필요 (정상) |
| `company_id` | Integer (FK) | 회사 연결 | 세션에서 자동 설정 | 노출 불필요 (정상) |
| `profile_snapshot` | JSONB | 퇴사 시점 스냅샷 | 시스템 자동 생성 | 노출 불필요 (정상) |
| `snapshot_at` | DateTime | 스냅샷 생성 시점 | 시스템 자동 생성 | 노출 불필요 (정상) |
| `resignation_date` | Date | 퇴직일 | `_contract_info.html`에 있음 | 정상 노출 중 |
| `data_retention_until` | Date | 데이터 보관 만료 | 관리자 전용 필드 | 관리자 페이지에 추가 권장 |

#### 13.2.4 CorporateAdminProfile 필드 - 2개

| 필드명 | DB 타입 | 용도 | 미노출 이유 | 권장 조치 |
|--------|---------|------|------------|----------|
| `photo` | String(500) | 프로필 사진 | 법인 관리자 수정 폼에 없음 | 사진 업로드 추가 권장 |
| `is_active` | Boolean | 활성 상태 | 관리자 전용 필드 | 관리자 페이지에 추가 권장 |

### 13.3 필드 노출 상태 매트릭스

| 필드 | Profile DB | Employee DB | Personal UI | Employee UI | CorpAdmin UI |
|------|:----------:|:-----------:|:-----------:|:-----------:|:------------:|
| `name` | O | O | O | O | O |
| `english_name` | O | O | O | O | O |
| **`chinese_name`** | O | O | X | X | X |
| `birth_date` | O | O | O | O | X |
| **`lunar_birth`** | O | O | X | X | X |
| `gender` | O | O | O | O | X |
| `mobile_phone` | O | O | O | O | O |
| **`home_phone`** | O | O | X | X | X |
| `email` | O | O | O | O | O |
| `address` | O | O | O | O | X |
| `detailed_address` | O | O | O | O | X |
| `postal_code` | O | O | O (hidden) | O (hidden) | X |
| `resident_number` | O | O | O | O | X |
| **`nationality`** | O | O | X | X | X |
| `blood_type` | O | O | O | O | X |
| `religion` | O | O | O | O | X |
| `hobby` | O | O | O | O | X |
| `specialty` | O | O | O | O | X |
| `disability_info` | O | O | O | O | X |
| `marital_status` | O | O | O | O | X |
| `actual_address` | O | O | O | O | X |
| `emergency_contact` | O | O | O | O | X |
| `emergency_relation` | O | O | O | O | X |
| **`is_public`** | O | - | 대시보드만 | - | - |

**범례**: O = DB 존재 및 UI 노출, X = UI 미노출, - = 해당 없음

### 13.4 미노출 필드 영향도 분석

#### 긴급 조치 필요 (High Priority)

| 필드 | 영향도 | 이유 |
|------|:------:|------|
| `chinese_name` | 중간 | 한자 문화권 직원 관리 시 필수, 법적 문서에 한자명 기재 필요 |
| `nationality` | 높음 | 외국인 직원 고용 시 비자/취업허가 관리에 필수 |
| `lunar_birth` | 낮음 | 음력 생일 알림 기능 구현 시 필요 |

#### 선택적 조치 (Low Priority)

| 필드 | 영향도 | 이유 |
|------|:------:|------|
| `home_phone` | 낮음 | 휴대전화가 주 연락처, 자택 전화 사용 감소 추세 |
| `is_public` | 중간 | 프로필 공개 설정이 대시보드에서만 가능, UX 개선 여지 |
| `photo` (CorpAdmin) | 중간 | 법인 관리자 프로필 사진 업로드 불가 |

### 13.5 권장 조치 요약

```
[즉시 조치]
1. nationality 필드 → 개인정보 섹션에 select 추가 (외국인 고용 대비)
2. chinese_name 필드 → 이름 섹션에 입력 필드 추가

[단기 조치]
3. lunar_birth 체크박스 → birth_date 옆에 추가
4. is_public 토글 → 프로필 수정 페이지에 추가

[장기 조치/검토]
5. home_phone → 사용 빈도 분석 후 유지/제거 결정
6. data_retention_until → 관리자 대시보드에 표시 추가
```

---

## 14. 필드 네이밍 일관성 분석

### 14.1 분석 개요

**분석 대상**:
1. 템플릿 input name vs DB 컬럼명 매핑
2. camelCase vs snake_case 혼용 현황
3. 모델 별칭(alias) 정의 일관성
4. FieldRegistry 별칭과 모델 별칭 정합성

### 14.2 템플릿 input name vs DB 컬럼 불일치

#### 14.2.1 개인정보 섹션 (`_personal_info.html`)

| 템플릿 input name | DB 컬럼명 | 변환 필요 | 처리 위치 |
|------------------|-----------|:---------:|----------|
| `name_en` | `english_name` | O | form_extractors.py |
| `phone` | `mobile_phone` | O | 어댑터 alias |
| `rrn` | `resident_number` | O | form_extractors.py |
| `photo` | `photo` | - | 일치 |
| `birth_date` | `birth_date` | - | 일치 |
| `gender` | `gender` | - | 일치 |
| `blood_type` | `blood_type` | - | 일치 |
| `postal_code` | `postal_code` | - | 일치 (hidden) |

#### 14.2.2 계약정보 섹션 (`_contract_info.html`)

| 템플릿 input name | DB 컬럼명 | 변환 필요 | 문제점 |
|------------------|-----------|:---------:|--------|
| **`hireDate`** | `hire_date` | O | **camelCase 사용** |
| `status` | `status` | - | 일치 |
| `employment_type` | `employee_type` (Contract) | O | 네이밍 불일치 |
| `contract_period` | `contract_period` | - | 일치 |
| `probation_end` | (없음) | ? | DB 컬럼 확인 필요 |
| `resignation_date` | `resignation_date` | - | 일치 |

#### 14.2.3 급여정보 섹션 (`_salary_info.html`)

| 템플릿 input name | DB 컬럼명 | 변환 필요 | 처리 방법 |
|------------------|-----------|:---------:|----------|
| **`transport_allowance`** | `transportation_allowance` | O | Salary.__dict_aliases__ |
| **`pay_type`** | `salary_type` | O | Salary.__dict_aliases__ |
| `base_salary` | `base_salary` | - | 일치 |
| `position_allowance` | `position_allowance` | - | 일치 |
| `meal_allowance` | `meal_allowance` | - | 일치 |

#### 14.2.4 경력정보 섹션 (`_career_info.html`)

| 템플릿 input name | DB 컬럼명 | 변환 필요 | 처리 방법 |
|------------------|-----------|:---------:|----------|
| `career_company_name[]` | `company_name` | O | prefix 제거 |
| `career_department[]` | `department` | O | prefix 제거 |
| **`career_duties[]`** | `job_description` | O | **별도 매핑 필요** |
| `career_salary_type[]` | `salary_type` | O | prefix 제거 |
| `career_salary[]` | `salary` | O | prefix 제거 |

#### 14.2.5 수상내역 섹션 (`_award_info.html`)

| 템플릿 input name | DB 컬럼명 | 변환 필요 | 처리 방법 |
|------------------|-----------|:---------:|----------|
| **`award_notes[]`** | `note` | O | Award.__dict_aliases__ (`notes` → `note`) |
| `award_name[]` | `award_name` | O | prefix 제거 |
| `award_date[]` | `award_date` | O | prefix 제거 |
| `award_institution[]` | `institution` | O | prefix 제거 |
| `award_description[]` | `description` | O | prefix 제거 |

### 14.3 camelCase vs snake_case 혼용 현황

#### 14.3.1 문제 케이스

| 위치 | 필드 | 현재 | 표준 | 심각도 |
|------|------|------|------|:------:|
| `_contract_info.html` | `hireDate` | camelCase | snake_case | **높음** |
| JavaScript 전역 | 다수 | camelCase | - | 정상 (JS 관례) |
| API 응답 | 다수 | snake_case | - | 정상 (Python 관례) |

#### 14.3.2 변환 패턴 분석

**프론트엔드 → 백엔드 (form submit)**
```
템플릿 (snake_case) → Flask request.form → form_extractors.py → DB 저장
예: phone → mobile_phone (매핑)
예: rrn → resident_number (매핑)
```

**백엔드 → 프론트엔드 (API 응답)**
```
DB (snake_case) → to_dict() → JSON (snake_case 유지)
                            → 템플릿 (Jinja2에서 snake_case 사용)
```

**JavaScript 내부**
```
JS 변수: camelCase (관례)
API 호출 시: snake_case로 변환 필요
DOM 조작: snake_case (HTML attribute와 일치)
```

### 14.4 모델 별칭(alias) 정의 현황

#### 14.4.1 `__dict_aliases__` 정의 목록

| 모델 | 별칭 | 실제 필드 | 용도 |
|------|------|----------|------|
| **Career** | `company` | `company_name` | 템플릿 호환 |
| | `duty` | `job_description` | 템플릿 호환 |
| | `reason_for_leaving` | `resignation_reason` | Personal 호환 |
| | `notes` | `note` | Personal 호환 |
| | `responsibilities` | `job_description` | Personal 호환 |
| **Education** | `school` | `school_name` | 템플릿 호환 |
| | `status` | `graduation_status` | Personal 호환 |
| | `notes` | `note` | Personal 호환 |
| **Certificate** | `name` | `certificate_name` | 템플릿 호환 |
| | `issuer` | `issuing_organization` | 템플릿 호환 |
| | `acquired_date` | `acquisition_date` | 템플릿 호환 |
| | `notes` | `note` | Personal 호환 |
| | `issue_date` | `acquisition_date` | Personal 호환 |
| **MilitaryService** | `status` | `military_status` | 템플릿 호환 |
| | `start_date` | `enlistment_date` | 템플릿 호환 |
| | `end_date` | `discharge_date` | 템플릿 호환 |
| | `duty` | `service_type` | 템플릿 호환 |
| | `discharge_type` | `discharge_reason` | Personal 호환 |
| **Salary** | `transport_allowance` | `transportation_allowance` | 템플릿 호환 |
| | `pay_type` | `salary_type` | 템플릿 호환 |
| **FamilyMember** | `phone` | `contact` | 템플릿 호환 |
| | `living_together` | `is_cohabitant` | 템플릿 호환 |
| | `notes` | `note` | Personal 호환 |
| **Language** | `language` | `language_name` | Personal 호환 |
| | `test_name` | `exam_name` | Personal 호환 |
| | `proficiency` | `level` | Personal 호환 |
| | `test_date` | `acquisition_date` | Personal 호환 |
| **Award** | `notes` | `note` | Personal 호환 |
| **ProjectParticipation** | `notes` | `note` | Personal 호환 |

#### 14.4.2 `__dict_camel_mapping__` 정의 패턴

모든 모델에서 일관된 패턴 사용:
```python
__dict_camel_mapping__ = {
    'snake_case_field': ['camelCaseField'],
    # 예: 'employee_id': ['employeeId'],
    # 예: 'birth_date': ['birthDate'],
}
```

**적용 모델 수**: 25개 모델에서 정의

### 14.5 FieldRegistry 별칭 vs 모델 별칭 비교

| 섹션 | FieldRegistry aliases | 모델 __dict_aliases__ | 정합성 |
|------|----------------------|----------------------|:------:|
| `personal_basic` | `name_en` → `english_name` | (없음) | 불일치 |
| | `birthDate` → `birth_date` | (없음) | FieldRegistry만 |
| | `lunarBirth` → `lunar_birth` | (없음) | FieldRegistry만 |
| | `rrn` → `resident_number` | (없음) | FieldRegistry만 |
| `contact` | `phone` → `mobile_phone` | (어댑터에서 처리) | 간접 일치 |
| `military` | `serviceStart` → `service_start` | `start_date` → `enlistment_date` | **충돌 가능** |
| `education` | (없음) | `school` → `school_name` | 모델만 |

### 14.6 일관성 문제 요약

#### 14.6.1 심각도별 분류

**Critical (즉시 수정 필요)**

| 문제 | 위치 | 영향 |
|------|------|------|
| `hireDate` camelCase | `_contract_info.html:11` | snake_case 표준 위반 |
| `career_duties[]` → `job_description` 미매핑 | form_extractors.py | 데이터 손실 가능 |

**Warning (개선 권장)**

| 문제 | 위치 | 영향 |
|------|------|------|
| 별칭 중복 정의 | FieldRegistry + 모델 | 유지보수 복잡성 |
| `notes` → `note` 반복 | 8개 모델 | DRY 원칙 위반 |
| prefix 패턴 불일치 | 템플릿 배열 필드 | `career_*[]` vs `education_*[]` 등 |

**Info (문서화 필요)**

| 문제 | 위치 | 영향 |
|------|------|------|
| camelCase 변환 자동화 | DictSerializableMixin | 개발자 인지 필요 |
| 템플릿 → DB 매핑 문서 부재 | - | 신규 개발자 혼란 |

### 14.7 권장 개선 방안

#### 14.7.1 단기 개선 (Hotfix)

```python
# 1. hireDate → hire_date 수정 (_contract_info.html:11)
# 변경 전:
<input type="date" id="hireDate" name="hireDate" class="form-input" ...>

# 변경 후:
<input type="date" id="hire_date" name="hire_date" class="form-input" ...>
```

```python
# 2. career_duties 매핑 추가 (form_extractors.py)
career_data = {
    'company_name': career_company_names[i],
    'job_description': career_duties[i],  # duties → job_description 매핑
    ...
}
```

#### 14.7.2 중기 개선 (FieldRegistry 통합)

```python
# FieldRegistry에 input_name 속성 추가
create_field(
    name='english_name',
    label='영문명',
    input_name='name_en',  # 템플릿 input name
    aliases=['name_en', 'englishName'],
    ...
)

# form_extractors.py에서 FieldRegistry 기반 자동 매핑
def extract_personal_info(form_data):
    return FieldRegistry.normalize_form_data('personal_basic', form_data)
```

#### 14.7.3 장기 개선 (별칭 통합)

```python
# 1. 모델 __dict_aliases__를 FieldRegistry로 마이그레이션
# 2. 모델에서는 FieldRegistry 참조만 유지

class Career(DictSerializableMixin, db.Model):
    __dict_field_domain__ = 'career'  # FieldRegistry 섹션 참조
    # __dict_aliases__ 제거 → FieldRegistry로 통합
```

### 14.8 네이밍 규칙 권장안

#### 14.8.1 계층별 네이밍 표준

| 계층 | 규칙 | 예시 |
|------|------|------|
| **DB 컬럼** | snake_case | `english_name`, `birth_date` |
| **Python 변수** | snake_case | `employee_data`, `form_values` |
| **템플릿 input name** | snake_case | `name="birth_date"` |
| **JavaScript 변수** | camelCase | `employeeData`, `formValues` |
| **API 응답 키** | snake_case | `{"birth_date": "1990-01-01"}` |
| **FieldRegistry 필드명** | snake_case | `name='birth_date'` |

#### 14.8.2 별칭 정의 원칙

```
1. SSOT (Single Source of Truth): FieldRegistry에서만 별칭 정의
2. 템플릿 호환 별칭: 기존 템플릿 코드와의 호환성 유지
3. Personal 호환 별칭: 개인/법인 공통 이력 모델 호환
4. camelCase 매핑: from_dict() 역직렬화 전용
```

---

*분석 완료: 2025-12-22*
*분석 도구: frontend-architect + backend-architect 병렬 실행*
*분석 범위: 템플릿 18개, 모델 10개, 어댑터 3개*
*추가 분석: 개인 vs 법인 직원 필드 세부 비교, 공통 관리 가능성 분석*
*추가 분석 (v2): DB 필드 vs UI 노출 불일치 분석, 필드 네이밍 일관성 분석*
