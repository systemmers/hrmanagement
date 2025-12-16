# 프로필/인사카드 템플릿 구조 분석

## 개요
프로필과 인사카드 페이지의 섹션 및 필드 구조를 계정 타입별로 분석합니다.

## 계정 타입 정의
- **개인 계정 (personal)**: `page_mode != 'hr_card'`, `account_type = 'personal'`
- **법인 직원 계정 (corporate employee)**: `page_mode = 'hr_card'`, `account_type = 'corporate'`
- **법인 관리자 계정 (corporate admin)**: `page_mode = 'hr_card'`, `account_type = 'corporate_admin'`

---

## 1. 프로필 상세 페이지 (profile/detail.html)

### 템플릿 특징
- **통합 템플릿**: 개인/법인 계정 모두 지원
- **조건부 렌더링**: `page_mode`, `account_type`로 섹션 제어
- **파셜 기반**: 공유 파셜 컴포넌트 include

### 헤더 카드 (_employee_header.html)

#### 개인 계정 (variant='personal')
| 영역 | 필드명 | 라벨 | 칼럼수 | 비고 |
|------|--------|------|--------|------|
| 메타 정보 | email | - | 1 | 아이콘: envelope |
| 메타 정보 | phone | - | 1 | 아이콘: phone |
| 메타 정보 | address | - | 1 | 아이콘: map-marker-alt |
| 통계 | birth_date | 생년월일 | 1 | - |
| 통계 | contract_count | 계약 수 | 1 | 기본값: 0건 |
| 통계 | created_at | 가입일 | 1 | - |
| 통계 | id | 회원번호 | 1 | 형식: USR-XXX |

#### 법인 직원 계정 (variant='corporate')
| 영역 | 필드명 | 라벨 | 칼럼수 | 비고 |
|------|--------|------|--------|------|
| 메타 정보 | department | - | 1 | 아이콘: building |
| 메타 정보 | position | - | 1 | 아이콘: id-badge |
| 메타 정보 | status | - | 1 | 아이콘: calendar-check |
| 통계 | hire_date | 입사일 | 1 | - |
| 통계 | tenure | 재직기간 | 1 | 계산됨 |
| 통계 | remaining_leave | 연차 잔여 | 1 | 기본값: 15일 |
| 통계 | id | 사번 | 1 | 형식: EMP-XXX |
| 명함 | business_card | 명함 | - | 법인 전용, 앞/뒷면 |

---

## 2. 섹션별 필드 구조

### 섹션 1: 개인 기본정보 (personal-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_basic_info.html`

| 필드명 | 라벨 | 칼럼수 | 순서 | 조건 |
|--------|------|--------|------|------|
| name | 성명 (한글) | 1 | 1 | 필수 |
| english_name | 여권명 (영문) | 1 | 2 | - |
| resident_number | 주민등록번호 | 1 | 3 | - |
| birth_date | 생년월일 | 1 | 4 | - |
| gender | 성별 | 1 | 5 | get_gender_label() |
| marital_status | 결혼여부 | 1 | 6 | get_marital_status_label() |
| phone | 휴대전화 | 1 | 7 | format_phone() |
| email | 개인 이메일 | 1 | 8 | highlight |
| emergency_contact | 비상연락처 | 1 | 9 | emergency_relation 포함 |
| blood_type | 혈액형 | 1 | 10 | 신규 필드 |
| religion | 종교 | 1 | 11 | 신규 필드 |
| hobby | 취미 | 1 | 12 | 신규 필드 |
| specialty | 특기 | 1 | 13 | 신규 필드 |
| disability_info | 장애정보 | 1 | 14 | 신규 필드 |
| address | 주민등록상 주소 | 전체 | 15 | - |
| detailed_address | 상세주소 | 전체 | 16 | - |
| actual_address | 실제 거주지 | 전체 | 17 | 서브섹션 |
| actual_detailed_address | 상세주소 | 전체 | 18 | 서브섹션 |

---

### 섹션 2: 소속정보 (organization-info)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_basic_info.html`

| 필드명 | 라벨 | 칼럼수 | 순서 | 조건 |
|--------|------|--------|------|------|
| department | 소속 | 1 | 1 | highlight |
| team | 부서 | 1 | 2 | highlight, fallback to department |
| position | 직급 | 1 | 3 | - |
| job_title | 직책 | 1 | 4 | - |
| employee_number | 사원번호 | 1 | 5 | fallback: EMP-XXX |
| employment_type | 근무형태 | 1 | 6 | get_employment_type_label() |
| work_location | 근무지 | 1 | 7 | 기본값: '본사' |
| internal_phone | 내선번호 | 1 | 8 | 프로필에서 이동됨 |
| company_email | 회사 이메일 | 1 | 9 | 프로필에서 이동됨 |
| status | 재직상태 | 1 | 10 | badge, get_status_text() |
| hire_date | 입사일 | 1 | 11 | - |
| tenure | 재직기간 | 1 | 12 | calculate_tenure(), highlight |

---

### 섹션 3: 계약정보 (contract-info)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_basic_info.html`

| 필드명 | 라벨 | 칼럼수 | 순서 | 조건 |
|--------|------|--------|------|------|
| contract.contract_type | 계약형태 | 1 | 1 | fallback: employment_type |
| contract.contract_period | 계약기간 | 1 | 2 | fallback: '무기한' |
| contract.contract_date | 계약시작일 | 1 | 3 | fallback: hire_date |
| contract.employee_type | 직원유형 | 1 | 4 | - |
| contract.work_type | 근무형태 | 1 | 5 | - |
| probation_end | 시용기간 종료 | 1 | 6 | - |
| - | 근무시간 | 1 | 7 | 하드코딩: '09:00 ~ 18:00' |
| - | 휴게시간 | 1 | 8 | 하드코딩: '12:00 ~ 13:00' |
| resignation_date | 퇴사일 | 1 | 9 | 조건부 표시 |

---

### 섹션 4: 급여정보 (salary-info)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_basic_info.html`

| 필드명 | 라벨 | 칼럼수 | 순서 | 조건 |
|--------|------|--------|------|------|
| salary.salary_type | 급여형태 | 1 | 1 | - |
| salary.base_salary | 기본급 | 1 | 2 | 천단위 구분, '원' 접미사 |
| salary.position_allowance | 직책수당 | 1 | 3 | 천단위 구분, '원' 접미사 |
| salary.meal_allowance | 식대 | 1 | 4 | 천단위 구분, '원' 접미사 |
| salary.transportation_allowance | 교통비 | 1 | 5 | 천단위 구분, '원' 접미사 |
| salary.total_salary | 총 급여 | 1 | 6 | 천단위 구분, '원' 접미사 |
| salary.payment_day | 급여지급일 | 1 | 7 | '매월 X일' 형식 |
| salary.payment_method | 급여지급방법 | 1 | 8 | - |
| salary.bank_account | 급여계좌 | 1 | 9 | - |

---

### 섹션 5: 연차 및 복리후생 (benefit-info)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_basic_info.html`

| 필드명 | 라벨 | 칼럼수 | 순서 | 조건 |
|--------|------|--------|------|------|
| benefit.annual_leave_granted | 연차 발생일수 | 1 | 1 | 'X일' 형식 |
| benefit.annual_leave_used | 연차 사용일수 | 1 | 2 | 'X일' 형식 |
| benefit.annual_leave_remaining | 연차 잔여일수 | 1 | 3 | 'X일' 형식, highlight |
| benefit.severance_type | 퇴직금 유형 | 1 | 4 | - |
| benefit.severance_method | 퇴직금 적립방법 | 1 | 5 | - |

---

### 섹션 6: 4대보험 (insurance-info)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_basic_info.html`

| 필드명 | 라벨 | 칼럼수 | 순서 | 조건 |
|--------|------|--------|------|------|
| insurance.all | 4대보험 | 1 | 1 | badge: 가입/미가입 |
| insurance.health_insurance | 건강보험 | 1 | 2 | badge: 가입/미가입 |
| insurance.national_pension | 국민연금 | 1 | 3 | badge: 가입/미가입 |
| insurance.employment_insurance | 고용보험 | 1 | 4 | badge: 가입/미가입 |
| insurance.industrial_accident | 산재보험 | 1 | 5 | badge: 가입/미가입 |

---

### 섹션 7: 가족정보 (family-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_basic_info.html`

테이블 형식 (칼럼: 6개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 관계 | relation | get_relation_label() |
| 성명 | name | - |
| 생년월일 | birth_date | - |
| 직업 | occupation | - |
| 연락처 | phone | - |
| 동거여부 | living_together | badge: 동거/별거 |

---

### 섹션 8: 학력정보 (education-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_history_info.html`

테이블 형식 (칼럼: 7개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 학력구분 | degree | get_degree_label() |
| 학교명 | school | - |
| 졸업년월 | graduation_year | - |
| 전공 | major | - |
| 학점 | gpa | - |
| 졸업유무 | - | badge: 졸업 (하드코딩) |
| 비고 | note | - |

---

### 섹션 9: 경력정보 (career-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_history_info.html`

테이블 형식 (칼럼: 8개)
서브타이틀: "입사 전"

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 직장명 | company | - |
| 입사일 | start_date | - |
| 퇴사일 | end_date | '재직중' fallback |
| 경력 | - | 하이픈 (계산 안됨) |
| 부서 | department | - |
| 직급 | position | - |
| 담당업무 | duty | - |
| 연봉 | salary | 천단위 구분, '원' 접미사 |

테이블 하단: 총 경력 요약 (X개사)

---

### 섹션 10: 자격증 및 면허 (certificate-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_history_info.html`

테이블 형식 (칼럼: 6개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 구분 | - | 하드코딩: '자격증' |
| 종류 | name | - |
| 등급/점수 | grade | - |
| 발행처 | issuer | - |
| 취득일 | acquired_date | - |
| 비고 | expiry_date | '만료: X' 형식 |

---

### 섹션 11: 언어능력 (language-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_history_info.html`

테이블 형식 (칼럼: 5개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 언어 | language | - |
| 수준 | level | get_level_label() |
| 시험명 | test_name | - |
| 점수 | score | - |
| 취득일 | acquired_date | - |

---

### 섹션 12: 병역정보 (military-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_history_info.html`

그리드 형식 (info-grid)

| 필드명 | 라벨 | 칼럼수 | 순서 |
|--------|------|--------|------|
| military.status | 병역구분 | 1 | 1 |
| military.branch | 군별 | 1 | 2 |
| military.start_date ~ end_date | 복무기간 | 1 | 3 |
| military.rank | 계급 | 1 | 4 |
| military.duty | 보직 | 1 | 5 |
| military.specialty | 병과 | 1 | 6 |
| military.exemption_reason | 면제사유 | 1 | 7 |

---

### 섹션 13: 수상내역 (award-info)
**조건**: 전체 공통
**파일**: `partials/employee_detail/_history_info.html`

테이블 형식 (칼럼: 5개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 수상일 | award_date | - |
| 수상명 | award_name | - |
| 수여기관 | institution | - |
| 수상내용 | description | - |
| 비고 | notes | - |

정렬: award_date 내림차순

---

### 섹션 14: 유사사업 참여경력 (project-info)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_history_info.html`

테이블 형식 (칼럼: 6개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 사업명 | project_name | - |
| 참여기간 | start_date ~ end_date | - |
| 기간 | duration | - |
| 담당업무 | duty | - |
| 역할/직책 | role | - |
| 발주처 | client | - |

---

### 섹션 15: 근로계약 및 연봉 (employment-contract)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_hr_records.html`

#### 서브섹션 1: 근로계약 이력
테이블 형식 (칼럼: 8개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 계약일 | hire_date | - |
| 계약구분 | - | badge: 정규직 (하드코딩) |
| 계약기간 시작 | hire_date | - |
| 계약기간 종료 | - | 하이픈 |
| 계약기간 | tenure | calculate_tenure() |
| 직원구분 | - | '정규직' (하드코딩) |
| 근무형태 | - | '전일제' (하드코딩) |
| 비고 | - | '신규입사' (하드코딩) |

#### 서브섹션 2: 연봉계약 이력
테이블 형식 (칼럼: 5개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 계약연도 | contract_year | 'X년' 형식 |
| 연봉 | annual_salary | 천단위 구분, '원' 접미사 |
| 상여금 | bonus | 천단위 구분, '원' 접미사 |
| 총액 | total_amount | 천단위 구분, '원' 접미사, strong |
| 계약기간 | contract_period | - |

정렬: contract_year 내림차순

#### 서브섹션 3: 급여 지급 이력
테이블 형식 (칼럼: 10개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 지급일 | payment_date | - |
| 지급기간 | payment_period | - |
| 기본급 | base_salary | 천단위 구분, '원' 접미사 |
| 수당 | allowances | 천단위 구분, '원' 접미사 |
| 총지급액 | gross_pay | 천단위 구분, '원' 접미사 |
| 4대보험 | insurance | 천단위 구분, '원' 접미사 |
| 소득세 | income_tax | 천단위 구분, '원' 접미사 |
| 공제합계 | total_deduction | 천단위 구분, '원' 접미사 |
| 실지급액 | net_pay | 천단위 구분, '원' 접미사, strong |
| 비고 | note | - |

정렬: payment_date 내림차순

---

### 섹션 16: 인사이동 및 고과 (personnel-movement)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_hr_records.html`

#### 서브섹션 1: 인사이동 및 승진
테이블 형식 (칼럼: 8개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 발령일 | effective_date | - |
| 발령구분 | promotion_type | badge (신규채용/승진/기타) |
| 발령전 | from_department | - |
| 발령후 | to_department | - |
| 발령전 직급 | from_position | - |
| 발령후 직급 | to_position | - |
| 직무 | job_role | - |
| 발령사유 | reason | - |

정렬: effective_date 내림차순

#### 서브섹션 2: 인사고과 - 정기평가
테이블 형식 (칼럼: 8개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 연차 | year | 'X년' 형식 |
| 1분기 | q1_grade | badge (S/A/B 등급) |
| 2분기 | q2_grade | badge (S/A/B 등급) |
| 3분기 | q3_grade | badge (S/A/B 등급) |
| 4분기 | q4_grade | badge (S/A/B 등급) |
| 종합평가 | overall_grade | badge (S/A/B 등급), strong |
| 연봉협상 | salary_negotiation | - |
| 비고 | note | - |

정렬: year 내림차순

#### 서브섹션 3: 교육훈련
테이블 형식 (칼럼: 6개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 교육일 | training_date | - |
| 교육명 | training_name | - |
| 교육기관 | institution | - |
| 교육시간 | hours | 'X시간' 형식 |
| 이수여부 | completion_status | badge (이수/미이수) |
| 비고 | note | - |

정렬: training_date 내림차순

---

### 섹션 17: 근태 및 비품 (attendance-assets)
**조건**: `page_mode == 'hr_card'` (법인 전용)
**파일**: `partials/employee_detail/_hr_records.html`

#### 서브섹션 1: 근태현황
그리드 형식 (info-grid)

| 필드명 | 라벨 | 칼럼수 | 순서 |
|--------|------|--------|------|
| attendance_summary.total_work_days | 출근일수 | 1 | 1 |
| attendance_summary.total_absent_days | 결근일수 | 1 | 2 |
| attendance_summary.total_late_count | 지각횟수 | 1 | 3 |
| attendance_summary.total_early_leave | 조퇴횟수 | 1 | 4 |
| attendance_summary.total_annual_used | 연차사용 | 1 | 5 |
| benefit.annual_leave_remaining | 연차잔여 | 1 | 6 |

#### 서브섹션 2: 비품지급
테이블 형식 (칼럼: 6개)

| 칼럼명 | 필드명 | 함수/변환 |
|--------|--------|-----------|
| 지급일 | issue_date | - |
| 품목 | item_name | - |
| 모델/사양 | model | - |
| 시리얼번호 | serial_number | - |
| 상태 | status | badge (사용중/반납/기타) |
| 비고 | note | - |

정렬: issue_date 내림차순

---

## 3. 계정 타입별 섹션 표시 매트릭스

| 섹션 ID | 섹션명 | 개인 계정 | 법인 직원 | 법인 관리자 |
|---------|--------|-----------|-----------|-------------|
| personal-info | 개인 기본정보 | ✅ | ✅ | ✅ |
| organization-info | 소속정보 | ❌ | ✅ | ❌ |
| contract-info | 계약정보 | ❌ | ✅ | ❌ |
| salary-info | 급여정보 | ❌ | ✅ | ❌ |
| benefit-info | 연차 및 복리후생 | ❌ | ✅ | ❌ |
| insurance-info | 4대보험 | ❌ | ✅ | ❌ |
| family-info | 가족정보 | ✅ | ✅ | ❌ |
| education-info | 학력정보 | ✅ | ✅ | ✅ |
| career-info | 경력정보 | ✅ | ✅ | ✅ |
| certificate-info | 자격증 및 면허 | ✅ | ✅ | ✅ |
| language-info | 언어능력 | ✅ | ✅ | ✅ |
| military-info | 병역정보 | ✅ | ✅ | ✅ |
| award-info | 수상내역 | ✅ | ✅ | ✅ |
| project-info | 유사사업 참여경력 | ❌ | ✅ | ❌ |
| employment-contract | 근로계약 및 연봉 | ❌ | ✅ | ❌ |
| personnel-movement | 인사이동 및 고과 | ❌ | ✅ | ❌ |
| attendance-assets | 근태 및 비품 | ❌ | ✅ | ❌ |

---

## 4. 섹션 네비게이션 (Section Navigation)

### variant='profile' (개인 계정 프로필)
```
기본정보
  - 개인 기본정보
  - 가족정보

이력 및 경력
  - 학력정보
  - 경력정보
  - 자격증 및 면허
  - 언어능력

부가정보
  - 병역정보
  - 수상내역
```

### variant='full' (법인 직원 인사카드)
```
기본정보
  - 개인 기본정보
  - 소속정보
  - 계약정보
  - 급여정보
  - 연차 및 복리후생
  - 4대보험
  - 가족정보

이력 및 경력
  - 학력정보
  - 경력정보
  - 자격증 및 면허
  - 언어능력
  - 병역/프로젝트/수상

인사기록
  - 근로계약 및 연봉
  - 인사이동 및 고과
  - 근태 및 비품
```

---

## 5. 필드 네이밍 일관성 분석

### 일관성 있는 네이밍
대부분의 필드 라벨이 페이지 간 일관적으로 사용됨.

### 차이점 발견
1. **섹션 12 (병역정보)**:
   - 프로필: '병역정보' (단독 섹션)
   - 인사카드: '병역/프로젝트/수상' (네비게이션에서 통합 표시)
   - 실제로는 별도 섹션으로 분리되어 있음

2. **내선번호/회사이메일**:
   - dev_prompt.md에 따르면 "프로필에서 소속정보로 이동"
   - 현재 소속정보 섹션에 포함됨 (법인 전용)

3. **실제 거주 주소**:
   - dev_prompt.md: "전체공통"으로 명시
   - 현재 개인 기본정보 섹션에 서브섹션으로 포함 (전체 공통)

---

## 6. 주요 발견 사항

### 통합 템플릿 구조
- `profile/detail.html`, `profile/edit.html`이 통합 템플릿으로 개인/법인 모두 지원
- 파셜 컴포넌트 기반으로 재사용성 극대화
- `page_mode`와 `account_type`으로 섹션 제어

### 조건부 렌더링 패턴
```jinja2
{% if page_mode == 'hr_card' %}
  {# 법인 전용 섹션 #}
{% endif %}

{% if account_type != 'corporate_admin' %}
  {# 법인 관리자 제외 #}
{% endif %}
```

### 헤더 카드 variant
- `variant='personal'`: 개인 계정 (그린 테마, 연락처/개인정보)
- `variant='corporate'`: 법인 직원 (블루 테마, 소속정보/명함)

### 추가된 필드 (신규)
개인 기본정보 섹션:
- 혈액형 (blood_type)
- 종교 (religion)
- 취미 (hobby)
- 특기 (specialty)
- 장애정보 (disability_info)

### 하드코딩 데이터
- 계약정보: 근무시간, 휴게시간
- 근로계약 이력: 계약구분, 직원구분, 근무형태, 비고
- 자격증: 구분 ('자격증')
- 학력정보: 졸업유무 ('졸업')

---

## 7. 권장 개선 사항

### 1. 하드코딩 제거
- 근무시간, 휴게시간을 DB 데이터로 관리
- 근로계약 이력의 하드코딩 데이터를 실제 데이터로 교체

### 2. 네이밍 일관성
- 섹션 네비게이션의 '병역/프로젝트/수상'을 개별 섹션으로 분리 표시
- 또는 실제로 통합 섹션으로 구조 변경

### 3. 필드 표시 최적화
- 개인 계정에서 불필요한 법인 관련 필드 완전 제거 확인
- 법인 관리자 계정의 프로필 섹션 최소화

### 4. 데이터 계산 로직
- 경력정보의 '경력' 칼럼 계산 구현 (현재 하이픈만 표시)
- 재직기간, 연차 등 계산 함수의 일관성 확인

---

## 8. 결론

현재 프로필/인사카드 템플릿 구조는:
- 통합 템플릿으로 잘 설계됨
- 파셜 컴포넌트 재사용으로 유지보수성 높음
- 조건부 렌더링으로 계정 타입별 차별화 구현
- 일부 하드코딩과 네이밍 일관성 개선 필요

전체적으로 체계적인 구조이며, 권장 개선 사항 적용 시 더욱 견고한 시스템이 될 것으로 판단됨.
