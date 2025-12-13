# 개인/법인 직원 프로필 페이지 비교 분석 보고서

> 작성일: 2025-12-13
> 분석 범위: 프로필 상세/수정 페이지, 인사카드 페이지

---

## 1. 분석 개요

### 1.1 분석 대상 페이지

| 구분 | 파일 경로 | 용도 | page_mode |
|------|-----------|------|-----------|
| 프로필 상세 | `profile/detail.html` | 개인 계정 본인 프로필 조회 | `profile` |
| 프로필 수정 | `profile/edit.html` | 개인 계정 본인 프로필 수정 | `profile` |
| 인사카드 상세 | `profile/detail.html` | 법인 직원 인사정보 조회 | `hr_card` |
| 개인 인사카드 | `personal/company_card_detail.html` | 개인이 계약된 법인 인사카드 조회 | `hr_card` |

### 1.2 핵심 파티셜 파일

| 파티셜 | 경로 | 역할 |
|--------|------|------|
| 헤더 카드 | `partials/employee_detail/_employee_header.html` | 직원 프로필 헤더 |
| 기본정보 | `partials/employee_detail/_basic_info.html` | 섹션 1-7 |
| 이력정보 | `partials/employee_detail/_history_info.html` | 섹션 7-13 |
| 인사기록 | `partials/employee_detail/_hr_records.html` | 섹션 12-14 |

---

## 2. 헤더 섹션 비교

### 2.1 variant 자동 감지 로직

```jinja2
{% set header_variant = variant|default('personal' if page_mode != 'hr_card' else 'corporate') %}
```

- `page_mode != 'hr_card'` → `variant='personal'` (그린 테마)
- `page_mode == 'hr_card'` → `variant='corporate'` (파란 테마)

### 2.2 메타 정보 비교 (상단 3개 아이콘)

| 위치 | 개인 (personal) | 법인 (corporate) |
|------|-----------------|------------------|
| 아이콘 1 | 이메일 (`fas fa-envelope`) | 소속/부서 (`fas fa-building`) |
| 아이콘 2 | 휴대전화 (`fas fa-phone`) | 직급 (`fas fa-id-badge`) |
| 아이콘 3 | 주소 (`fas fa-map-marker-alt`) | 재직상태 (`fas fa-calendar-check`) |

### 2.3 통계 정보 비교 (하단 4개 항목)

| 위치 | 개인 (personal) | 법인 (corporate) |
|------|-----------------|------------------|
| 통계 1 | 생년월일 | 입사일 |
| 통계 2 | 계약 수 | 재직기간 |
| 통계 3 | 가입일 | 연차 잔여 |
| 통계 4 | 회원번호 (USR-XXX) | 사번 (EMP-XXX) |

### 2.4 명함 영역

| 항목 | 개인 | 법인 |
|------|:----:|:----:|
| 표시 여부 | X | O |
| 앞면/뒷면 플레이스홀더 | - | O |
| 업로드 버튼 | - | O (권한 조건부) |
| 삭제 버튼 | - | O (권한 조건부) |

---

## 3. 기본정보 섹션 상세 (`_basic_info.html`)

### 3.1 섹션별 표시 조건 매트릭스

| 섹션 번호 | 섹션명 | 개인 (profile) | 법인 (hr_card) | 조건문 |
|:---------:|--------|:--------------:|:--------------:|--------|
| 1 | 개인 기본정보 | O | O | 없음 (항상 표시) |
| 2 | 소속정보 | X | O | `page_mode == 'hr_card'` |
| 3 | 계약정보 | X | O | `page_mode == 'hr_card'` |
| 4 | 급여정보 | X | O | `page_mode == 'hr_card'` |
| 5 | 연차 및 복리후생 | X | O | `page_mode == 'hr_card'` |
| 6 | 4대보험 | X | O | `page_mode == 'hr_card'` |
| 7 | 가족정보 | O | O | 없음 (항상 표시) |

### 3.2 섹션 1: 개인 기본정보 (18개 필드)

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 성명 (한글) | `employee.name` | text | |
| 여권명 (영문) | `employee.english_name` | text | |
| 주민등록번호 | `employee.resident_number` | text | 마스킹 필요 |
| 생년월일 | `employee.birth_date` | date | |
| 성별 | `employee.gender` | select | `get_gender_label()` |
| 결혼여부 | `employee.marital_status` | select | `get_marital_status_label()` |
| 휴대전화 | `employee.phone` | tel | `format_phone()` |
| 개인 이메일 | `employee.email` | email | highlight=true |
| 비상연락처 | `employee.emergency_contact` | text | 관계 포함 |
| 혈액형 | `employee.blood_type` | select | |
| 종교 | `employee.religion` | text | |
| 취미 | `employee.hobby` | text | |
| 특기 | `employee.specialty` | text | |
| 장애정보 | `employee.disability_info` | text | |
| 주민등록상 주소 | `employee.address` | text | |
| 상세주소 | `employee.detailed_address` | text | |
| 실제 거주지 | `employee.actual_address` | text | 항상 표시 |
| 실거주 상세주소 | `employee.actual_detailed_address` | text | |

### 3.3 섹션 2: 소속정보 (12개 필드) - 법인 전용

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 소속 | `employee.department` | text | highlight=true |
| 부서 | `employee.team` | text | highlight=true |
| 직급 | `employee.position` | text | |
| 직책 | `employee.job_title` | text | |
| 사원번호 | `employee.employee_number` | text | 자동생성 대체값 |
| 근무형태 | `employee.employment_type` | select | `get_employment_type_label()` |
| 근무지 | `employee.work_location` | text | 기본값: 본사 |
| 내선번호 | `employee.internal_phone` | text | |
| 회사 이메일 | `employee.company_email` | email | |
| 재직상태 | `employee.status` | badge | `get_status_text()` |
| 입사일 | `employee.hire_date` | date | |
| 재직기간 | `calculate_tenure()` | computed | highlight=true |

### 3.4 섹션 3: 계약정보 (9개 필드) - 법인 전용

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 계약형태 | `contract.contract_type` | text | 대체값: employment_type |
| 계약기간 | `contract.contract_period` | text | 기본값: 무기한 |
| 계약시작일 | `contract.contract_date` | date | 대체값: hire_date |
| 직원유형 | `contract.employee_type` | text | |
| 근무형태 | `contract.work_type` | text | |
| 시용기간 종료 | `employee.probation_end` | date | |
| 근무시간 | 고정값 | text | 09:00 ~ 18:00 |
| 휴게시간 | 고정값 | text | 12:00 ~ 13:00 |
| 퇴사일 | `employee.resignation_date` | date | 조건부 표시 |

### 3.5 섹션 4: 급여정보 (9개 필드) - 법인 전용

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 급여형태 | `salary.salary_type` | text | |
| 기본급 | `salary.base_salary` | currency | 포맷: {:,}원 |
| 직책수당 | `salary.position_allowance` | currency | |
| 식대 | `salary.meal_allowance` | currency | |
| 교통비 | `salary.transportation_allowance` | currency | |
| 총 급여 | `salary.total_salary` | currency | |
| 급여지급일 | `salary.payment_day` | text | 매월 N일 |
| 급여지급방법 | `salary.payment_method` | text | |
| 급여계좌 | `salary.bank_account` | text | |

### 3.6 섹션 5: 연차 및 복리후생 (5개 필드) - 법인 전용

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 연차 발생일수 | `benefit.annual_leave_granted` | number | 단위: 일 |
| 연차 사용일수 | `benefit.annual_leave_used` | number | |
| 연차 잔여일수 | `benefit.annual_leave_remaining` | number | highlight=true |
| 퇴직금 유형 | `benefit.severance_type` | text | |
| 퇴직금 적립방법 | `benefit.severance_method` | text | |

### 3.7 섹션 6: 4대보험 (5개 필드) - 법인 전용

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 4대보험 | `insurance` 객체 | badge | 가입/미가입 |
| 건강보험 | `insurance.health_insurance` | badge | |
| 국민연금 | `insurance.national_pension` | badge | |
| 고용보험 | `insurance.employment_insurance` | badge | |
| 산재보험 | `insurance.industrial_accident` | badge | |

### 3.8 섹션 7: 가족정보 테이블 (6개 컬럼)

| 컬럼명 | 데이터 소스 | 타입 |
|--------|-------------|------|
| 관계 | `family.relation` | select |
| 성명 | `family.name` | text |
| 생년월일 | `family.birth_date` | date |
| 직업 | `family.occupation` | text |
| 연락처 | `family.phone` | tel |
| 동거여부 | `family.living_together` | badge |

---

## 4. 이력정보 섹션 상세 (`_history_info.html`)

### 4.1 섹션별 표시 조건

| 섹션 번호 | 섹션명 | 개인 | 법인 | 조건문 |
|:---------:|--------|:----:|:----:|--------|
| 7 | 학력정보 | O | O | 없음 |
| 8 | 경력정보 | O | O | 없음 |
| 9 | 자격증 및 면허 | O | O | 없음 |
| 10 | 언어능력 | O | O | 없음 |
| 11 | 병역정보 | O | O | 없음 |
| 12 | 수상내역 | O | O | 없음 |
| 13 | 유사사업 참여경력 | X | O | `page_mode == 'hr_card'` |

### 4.2 섹션 7: 학력정보 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 학력구분 | `edu.degree` | `get_degree_label()` |
| 학교명 | `edu.school` | |
| 졸업년월 | `edu.graduation_year` | |
| 학부/학과 | `edu.major` | |
| 전공 | `edu.major` | 중복 컬럼 |
| 학점 | `edu.gpa` | |
| 졸업유무 | 고정값 | 졸업 badge |
| 비고 | `edu.note` | |

### 4.3 섹션 8: 경력정보 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 직장명 | `career.company` | |
| 입사일 | `career.start_date` | |
| 퇴사일 | `career.end_date` | 기본값: 재직중 |
| 경력 | - | 계산 필요 |
| 부서 | `career.department` | |
| 직급 | `career.position` | |
| 담당업무 | `career.duty` | |
| 연봉 | `career.salary` | 포맷: {:,}원 |

### 4.4 섹션 9: 자격증 및 면허 테이블 (6개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 구분 | 고정값 | 자격증 |
| 종류 | `cert.name` | |
| 등급/점수 | `cert.certificate_number` | |
| 발행처 | `cert.issuer` | |
| 취득일 | `cert.acquired_date` | |
| 비고 | `cert.expiry_date` | 만료일 표시 |

### 4.5 섹션 10: 언어능력 테이블 (5개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 언어 | `lang.language` | |
| 수준 | `lang.level` | `get_level_label()` |
| 시험명 | `lang.test_name` | |
| 점수 | `lang.score` | |
| 취득일 | `lang.acquired_date` | |

### 4.6 섹션 11: 병역정보 (7개 필드)

| 필드명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 병역구분 | `military.status` | `get_military_status_label()` |
| 군별 | `military.branch` | `get_branch_label()` |
| 복무기간 | `military.start_date ~ end_date` | |
| 계급 | `military.rank` | |
| 보직 | `military.duty` | |
| 병과 | `military.specialty` | |
| 면제사유 | `military.exemption_reason` | 조건부 표시 |

### 4.7 섹션 12: 수상내역 테이블 (5개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 수상일 | `award.award_date` | 역순 정렬 |
| 수상명 | `award.award_name` | |
| 수여기관 | `award.institution` | |
| 수상내용 | `award.description` | |
| 비고 | `award.notes` | |

### 4.8 섹션 13: 유사사업 참여경력 테이블 (6개 컬럼) - 법인 전용

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 사업명 | `project.project_name` | |
| 참여기간 | `project.start_date ~ end_date` | |
| 기간 | `project.duration` | |
| 담당업무 | `project.duty` | |
| 역할/직책 | `project.role` | |
| 발주처 | `project.client` | |

---

## 5. 인사기록 섹션 상세 (`_hr_records.html`)

> 표시 조건: `page_mode == 'hr_card'` AND `account_type != 'corporate_admin'`

### 5.1 섹션 12: 근로계약 및 연봉

#### 근로계약 이력 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 계약일 | `history.contract_date` |
| 계약구분 | `history.contract_type` |
| 계약기간 시작 | `history.start_date` |
| 계약기간 종료 | `history.end_date` |
| 계약기간 | `calculate_tenure()` |
| 직원구분 | `history.employee_type` |
| 근무형태 | `history.work_type` |
| 비고 | `history.note` |

#### 연봉계약 이력 테이블 (5개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 계약연도 | `history.contract_year` |
| 연봉 | `history.annual_salary` |
| 상여금 | `history.bonus` |
| 총액 | `history.total_amount` |
| 계약기간 | `history.contract_period` |

#### 급여 지급 이력 테이블 (10개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 지급일 | `payment.payment_date` |
| 지급기간 | `payment.payment_period` |
| 기본급 | `payment.base_salary` |
| 수당 | `payment.allowances` |
| 총지급액 | `payment.gross_pay` |
| 4대보험 | `payment.insurance` |
| 소득세 | `payment.income_tax` |
| 공제합계 | `payment.total_deduction` |
| 실지급액 | `payment.net_pay` |
| 비고 | `payment.note` |

### 5.2 섹션 13: 인사이동 및 고과

#### 인사이동 및 승진 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 발령일 | `promo.effective_date` |
| 발령구분 | `promo.promotion_type` |
| 발령전 | `promo.from_department` |
| 발령후 | `promo.to_department` |
| 발령전 직급 | `promo.from_position` |
| 발령후 직급 | `promo.to_position` |
| 직무 | `promo.job_role` |
| 발령사유 | `promo.reason` |

#### 인사고과 - 정기평가 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 연차 | `eval.year` |
| 1분기 | `eval.q1_grade` |
| 2분기 | `eval.q2_grade` |
| 3분기 | `eval.q3_grade` |
| 4분기 | `eval.q4_grade` |
| 종합평가 | `eval.overall_grade` |
| 연봉협상 | `eval.salary_negotiation` |
| 비고 | `eval.note` |

#### 교육훈련 테이블 (6개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 교육일 | `train.training_date` |
| 교육명 | `train.training_name` |
| 교육기관 | `train.institution` |
| 교육시간 | `train.hours` |
| 이수여부 | `train.completion_status` |
| 비고 | `train.note` |

### 5.3 섹션 14: 근태 및 비품

#### 근태현황 (6개 필드)

| 필드명 | 데이터 소스 |
|--------|-------------|
| 출근일수 | `attendance_summary.total_work_days` |
| 결근일수 | `attendance_summary.total_absent_days` |
| 지각횟수 | `attendance_summary.total_late_count` |
| 조퇴횟수 | `attendance_summary.total_early_leave` |
| 연차사용 | `attendance_summary.total_annual_used` |
| 연차잔여 | `benefit.annual_leave_remaining` |

#### 비품지급 테이블 (6개 컬럼)

| 컬럼명 | 데이터 소스 |
|--------|-------------|
| 지급일 | `asset.issue_date` |
| 품목 | `asset.item_name` |
| 모델/사양 | `asset.model` |
| 시리얼번호 | `asset.serial_number` |
| 상태 | `asset.status` |
| 비고 | `asset.note` |

---

## 6. 개인 인사카드 페이지 (`company_card_detail.html`)

### 6.1 페이지 특성

| 항목 | 값 |
|------|-----|
| 조회 주체 | 개인 계정 |
| 데이터 출처 | PersonCorporateContract |
| 헤더 variant | corporate |
| 수정 가능 | X (읽기 전용) |

### 6.2 섹션 구성

| 섹션 | 섹션명 | 표시 조건 |
|:----:|--------|-----------|
| 1 | 소속정보 | 항상 |
| 2 | 계약정보 | 항상 |
| 3 | 급여정보 | `salary` 존재 시 |
| 4 | 연차 및 복리후생 | `benefit` 존재 시 |
| 5 | 4대보험 | `insurance` 존재 시 |
| 6 | 근로계약 및 연봉 | 항상 |
| 7 | 인사이동 및 고과 | 항상 |
| 8 | 근태 및 비품 | 항상 |

### 6.3 테이블 컬럼 차이점 (법인 인사카드 대비)

#### 연봉계약 이력

| 컬럼 | 개인 인사카드 | 법인 인사카드 |
|------|:-------------:|:-------------:|
| 계약연도 | O | O |
| 연봉 | O | O |
| 인상률 | O | X |
| 상여금 | X | O |
| 총액 | X | O |
| 계약일 | O | X |
| 계약기간 | X | O |
| 비고 | O | O |

#### 급여 지급 이력

| 컬럼 | 개인 인사카드 | 법인 인사카드 |
|------|:-------------:|:-------------:|
| 지급년월 | O | X |
| 지급일 | X | O |
| 지급기간 | X | O |
| 기본급 | O | O |
| 수당 | O | O |
| 총지급액 | X | O |
| 4대보험 | X | O |
| 소득세 | X | O |
| 공제 | O | X |
| 공제합계 | X | O |
| 실지급액 | O | O |
| 비고 | X | O |

---

## 7. 전체 필드 수 요약

### 7.1 프로필 페이지 (`page_mode='profile'`)

| 섹션 | 필드/컬럼 수 |
|------|:-----------:|
| 헤더 | 7 |
| 개인 기본정보 | 18 |
| 가족정보 | 6 |
| 학력정보 | 8 |
| 경력정보 | 8 |
| 자격증 및 면허 | 6 |
| 언어능력 | 5 |
| 병역정보 | 7 |
| 수상내역 | 5 |
| **총계** | **약 70개** |

### 7.2 인사카드 페이지 (`page_mode='hr_card'`)

| 섹션 | 필드/컬럼 수 |
|------|:-----------:|
| 헤더 + 명함 | 7+ |
| 개인 기본정보 | 18 |
| 소속정보 | 12 |
| 계약정보 | 9 |
| 급여정보 | 9 |
| 연차 및 복리후생 | 5 |
| 4대보험 | 5 |
| 가족정보 | 6 |
| 학력/경력/자격증/언어/병역/수상 | 39 |
| 유사사업 참여경력 | 6 |
| 근로계약 이력 | 8 |
| 연봉계약 이력 | 5 |
| 급여 지급 이력 | 10 |
| 인사이동 및 승진 | 8 |
| 인사고과 | 8 |
| 교육훈련 | 6 |
| 근태현황 | 6 |
| 비품지급 | 6 |
| **총계** | **약 165개** |

---

## 8. 발견된 문제점 및 개선 제안

### 8.1 데이터 일관성 문제

| 문제 | 상세 | 권장 조치 |
|------|------|-----------|
| 연봉계약 이력 컬럼 불일치 | `_hr_records.html` vs `company_card_detail.html` 컬럼 구성 상이 | 통일 필요 |
| 급여 지급 이력 컬럼 불일치 | 법인: 10컬럼, 개인: 6컬럼 | 개인에도 상세 공제내역 표시 검토 |
| 학력정보 전공 중복 | 학부/학과, 전공 컬럼 동일 데이터 | 컬럼 통합 또는 분리 |

### 8.2 UX 개선 제안

| 항목 | 현재 상태 | 개선 방안 |
|------|-----------|-----------|
| 조건부 표시 패턴 | 일부는 데이터 유무, 일부는 무조건 표시 | 동일 패턴으로 통일 |
| 개인 인사카드 기본정보 | 헤더만 표시, 기본정보 섹션 없음 | `_basic_info.html` 섹션1 포함 검토 |
| 경력 컬럼 | 계산값 없이 `-` 표시 | 자동 계산 구현 |

### 8.3 코드 구조 개선

| 항목 | 현재 상태 | 개선 방안 |
|------|-----------|-----------|
| 테이블 중복 | `company_card_detail.html`과 `_hr_records.html`에 유사 구조 | 공통 매크로 추출 |
| 파티셜 크기 | `_hr_records.html` 342라인 | 소단위 분리 검토 |

---

## 9. 관련 파일 목록

```
app/
├── templates/
│   ├── profile/
│   │   ├── detail.html
│   │   └── edit.html
│   ├── personal/
│   │   └── company_card_detail.html
│   └── partials/
│       └── employee_detail/
│           ├── _employee_header.html
│           ├── _basic_info.html
│           ├── _history_info.html
│           └── _hr_records.html
└── blueprints/
    ├── mypage.py
    └── personal.py
```

---

*문서 끝*
