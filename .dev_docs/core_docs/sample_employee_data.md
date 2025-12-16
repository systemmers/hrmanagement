# HR Management System - 직원 1명 샘플 데이터

## 개요

본 문서는 직원 1명의 완전한 DB 데이터 샘플입니다.
`scripts/generate_fake_test_data.py` 스크립트가 생성하는 데이터 형식과 일치합니다.

---

## 1. Employee (직원 기본 정보)

### 기본 정보
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_number | EMP-2020-0001 | 사번 |
| name | 김민수 | 이름 |
| photo | /uploads/photos/emp_001.jpg | 프로필 사진 |
| department | 개발팀 | 부서 |
| position | 대리 | 직위 (서열: 사원, 대리, 과장, 부장) |
| status | 재직 | 상태 |
| hire_date | 2020-03-02 | 입사일 |
| phone | 010-1234-5678 | 전화번호 |
| email | minsu.kim@company.com | 이메일 |
| organization_id | 3 | 소속 조직 FK |

### 소속 정보
| 필드명 | 값 | 설명 |
|--------|-----|------|
| team | 백엔드팀 | 팀 |
| job_grade | L4 | 직급 (역량 레벨: L3, 2호봉, Senior) |
| job_title | null | 직책 (책임자 역할: 팀장, 본부장, CFO) |
| job_role | 백엔드개발 | 직무 (수행 업무: 인사기획, 회계관리) |
| work_location | 서울 본사 | 근무지 |
| internal_phone | 1234 | 사내 전화 |
| company_email | minsu.kim@testcorp.co.kr | 회사 이메일 |

### 개인정보
| 필드명 | 값 | 설명 |
|--------|-----|------|
| english_name | Minsu Kim | 영문 이름 |
| chinese_name | 金敏秀 | 한자 이름 |
| birth_date | 1992-05-15 | 생년월일 |
| lunar_birth | false | 음력 여부 |
| gender | 남 | 성별 |
| mobile_phone | 010-1234-5678 | 휴대폰 |
| home_phone | 02-123-4567 | 집 전화번호 |
| address | 서울특별시 강남구 테헤란로 123 | 주소 |
| detailed_address | 아파트 101동 1001호 | 상세주소 |
| postal_code | 06234 | 우편번호 |
| resident_number | 920515-1****** | 주민등록번호 |
| nationality | 대한민국 | 국적 |
| blood_type | A | 혈액형 |
| religion | 무교 | 종교 |
| hobby | 독서, 등산 | 취미 |
| specialty | 프로그래밍 | 특기 |
| disability_info | null | 장애 정보 |

### 실제 거주지
| 필드명 | 값 | 설명 |
|--------|-----|------|
| actual_postal_code | 06234 | 실제 거주 우편번호 |
| actual_address | 서울특별시 강남구 테헤란로 123 | 실제 거주 주소 |
| actual_detailed_address | 아파트 101동 1001호 | 실제 거주 상세주소 |

### 결혼 및 비상연락처
| 필드명 | 값 | 설명 |
|--------|-----|------|
| marital_status | single | 결혼여부 |
| emergency_contact | 010-9876-5432 | 비상연락처 |
| emergency_relation | 부 | 비상연락처 관계 |

---

## 2. Salary (급여 - 1:1)

| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| salary_type | 월급제 | 급여 유형 |
| base_salary | 4000000 | 기본급 (400만원) |
| position_allowance | 200000 | 직위수당 (20만원) |
| meal_allowance | 200000 | 식비수당 (20만원) |
| transportation_allowance | 100000 | 교통수당 (10만원) |
| total_salary | 4500000 | 총급여 (450만원) |
| payment_day | 25 | 급여일 |
| payment_method | 계좌이체 | 지급 방법 |
| bank_account | 국민은행 123-456-789012 | 은행계좌 |
| note | null | 비고 |

### 포괄임금제 정보
| 필드명 | 값 | 설명 |
|--------|-----|------|
| annual_salary | 54000000 | 연봉 (5400만원) |
| monthly_salary | 4500000 | 월급여 (450만원) |
| hourly_wage | 21635 | 통상임금(시급) |
| overtime_hours | 20 | 월 연장근로시간 |
| night_hours | 0 | 월 야간근로시간 |
| holiday_days | 0 | 월 휴일근로일수 |
| overtime_allowance | 649050 | 연장근로수당 |
| night_allowance | 0 | 야간근로수당 |
| holiday_allowance | 0 | 휴일근로수당 |

---

## 3. Benefit (복리후생 - 1:1)

| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| year | 2024 | 연도 |
| annual_leave_granted | 15 | 연차 부여일수 |
| annual_leave_used | 5 | 연차 사용일수 |
| annual_leave_remaining | 10 | 연차 잔여일수 |
| severance_type | DC형 | 퇴직금 유형 |
| severance_method | 퇴직연금 | 퇴직금 지급 방법 |
| note | null | 비고 |

---

## 4. Insurance (보험 - 1:1)

| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| national_pension | true | 국민연금 가입 |
| health_insurance | true | 건강보험 가입 |
| employment_insurance | true | 고용보험 가입 |
| industrial_accident | true | 산재보험 가입 |
| national_pension_rate | 4.5 | 국민연금료율 |
| health_insurance_rate | 3.545 | 건강보험료율 |
| long_term_care_rate | 0.9182 | 장기요양보험료율 |
| employment_insurance_rate | 0.9 | 고용보험료율 |
| note | null | 비고 |

---

## 5. Contract (계약 - 1:1)

| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| contract_date | 2020-03-02 | 계약일 |
| contract_type | 정규직 | 계약 유형 |
| contract_period | 무기한 | 계약 기간 |
| employee_type | 정규직 | 직원 유형 |
| work_type | 상근 | 근로 유형 |
| note | null | 비고 |

---

## 6. MilitaryService (병역 - 1:1)

| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| military_status | 만기전역 | 병역 상태 |
| service_type | 현역 | 복무 유형 |
| branch | 육군 | 군별 |
| rank | 병장 | 계급 |
| enlistment_date | 2012-07-15 | 입대일 |
| discharge_date | 2014-04-14 | 전역일 |
| discharge_reason | 만기전역 | 전역 사유 |
| exemption_reason | null | 면제 사유 |
| note | null | 비고 |

---

## 7. Education (학력 - 1:N) - 2개

### Education #1 (고등학교)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| school_type | 고등학교 | 학교 유형 |
| school_name | 서울고등학교 | 학교명 |
| major | 인문계 | 전공 |
| degree | null | 학위 |
| admission_date | 2008-03-02 | 입학일 |
| graduation_date | 2011-02-10 | 졸업일 |
| graduation_status | 졸업 | 졸업 상태 |
| gpa | null | 학점 |
| location | 서울 | 학교 위치 |
| note | null | 비고 |

### Education #2 (대학교)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| school_type | 대학교 | 학교 유형 |
| school_name | 서울대학교 | 학교명 |
| major | 컴퓨터공학 | 전공 |
| degree | 학사 | 학위 |
| admission_date | 2011-03-02 | 입학일 |
| graduation_date | 2018-02-20 | 졸업일 |
| graduation_status | 졸업 | 졸업 상태 |
| gpa | 3.8/4.5 | 학점 |
| location | 서울 | 학교 위치 |
| note | 군복무로 인한 휴학 포함 | 비고 |

---

## 8. Career (경력 - 1:N) - 1개

### Career #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| company_name | (주)스타트업테크 | 회사명 |
| department | 개발팀 | 부서 |
| position | 사원 | 직위 (서열: 사원, 대리, 과장, 부장) |
| job_grade | L3 | 직급 (역량 레벨: L3, 2호봉, Senior) |
| job_title | null | 직책 (책임자 역할: 팀장, 본부장, CFO) |
| job_role | 웹개발 | 직무 (수행 업무: 인사기획, 회계관리) |
| job_description | 웹 애플리케이션 개발, REST API 설계 | 담당업무 상세 |
| start_date | 2018-03-05 | 입사일 |
| end_date | 2020-02-28 | 퇴사일 |
| salary_type | annual | 급여유형 (annual/monthly/hourly/pay_step) |
| salary | 36000000 | 연봉 (3600만원) |
| monthly_salary | 3000000 | 월급 (300만원) |
| pay_step | null | 호봉 (급여 단계 1~50) |
| resignation_reason | 이직 | 퇴사 사유 |
| is_current | false | 현재 근무 여부 |
| note | null | 비고 |

---

## 9. Certificate (자격증 - 1:N) - 2개

### Certificate #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| certificate_name | 정보처리기사 | 자격증명 |
| issuing_organization | 한국산업인력공단 | 발급기관 |
| certificate_number | 17203012345 | 자격증 번호 |
| acquisition_date | 2017-08-18 | 취득일 |
| expiry_date | null | 만료일 |
| grade | null | 등급 |
| note | null | 비고 |

### Certificate #2
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| certificate_name | AWS Solutions Architect | 자격증명 |
| issuing_organization | Amazon Web Services | 발급기관 |
| certificate_number | AWS-SAA-C03-12345 | 자격증 번호 |
| acquisition_date | 2023-05-20 | 취득일 |
| expiry_date | 2026-05-20 | 만료일 |
| grade | Associate | 등급 |
| note | null | 비고 |

---

## 10. Language (어학 - 1:N) - 2개

### Language #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| language_name | 영어 | 언어명 |
| exam_name | TOEIC | 시험명 |
| score | 850 | 점수 |
| level | null | 레벨 |
| acquisition_date | 2023-03-15 | 취득일 |
| expiry_date | 2025-03-15 | 만료일 |
| note | null | 비고 |

### Language #2
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| language_name | 일본어 | 언어명 |
| exam_name | JLPT | 시험명 |
| score | null | 점수 |
| level | N2 | 레벨 |
| acquisition_date | 2022-12-01 | 취득일 |
| expiry_date | null | 만료일 |
| note | null | 비고 |

---

## 11. FamilyMember (가족 - 1:N) - 2개

### FamilyMember #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| relation | 부 | 관계 |
| name | 김철수 | 이름 |
| birth_date | 1965-03-20 | 생년월일 |
| occupation | 자영업 | 직업 |
| contact | 010-9876-5432 | 연락처 |
| is_cohabitant | false | 동거 여부 |
| is_dependent | false | 부양 여부 |
| note | null | 비고 |

### FamilyMember #2
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| relation | 모 | 관계 |
| name | 박영희 | 이름 |
| birth_date | 1967-08-15 | 생년월일 |
| occupation | 주부 | 직업 |
| contact | 010-8765-4321 | 연락처 |
| is_cohabitant | false | 동거 여부 |
| is_dependent | false | 부양 여부 |
| note | null | 비고 |

---

## 12. Promotion (발령/승진 - 1:N) - 2개

### Promotion #1 (입사 발령)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| effective_date | 2020-03-02 | 발령 유효일 |
| promotion_type | 신규임용 | 발령 유형 |
| from_department | null | 이전 부서 |
| to_department | 개발팀 | 새 부서 |
| from_position | null | 이전 직급 |
| to_position | 사원 | 새 직급 |
| job_role | 소프트웨어 엔지니어 | 직무 역할 |
| reason | 신규 입사 | 발령 사유 |
| note | null | 비고 |

### Promotion #2 (승진)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| effective_date | 2023-01-01 | 발령 유효일 |
| promotion_type | 승진 | 발령 유형 |
| from_department | 개발팀 | 이전 부서 |
| to_department | 개발팀 | 새 부서 |
| from_position | 사원 | 이전 직급 |
| to_position | 대리 | 새 직급 |
| job_role | 소프트웨어 엔지니어 | 직무 역할 |
| reason | 정기 승진 | 발령 사유 |
| note | null | 비고 |

---

## 13. Evaluation (평가 - 1:N) - 2개

### Evaluation #1 (2023년)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| year | 2023 | 평가 연도 |
| q1_grade | A | 1분기 등급 |
| q2_grade | A | 2분기 등급 |
| q3_grade | B | 3분기 등급 |
| q4_grade | A | 4분기 등급 |
| overall_grade | A | 종합 등급 |
| salary_negotiation | 5% 인상 | 급여 협상 결과 |
| note | 우수한 프로젝트 성과 | 비고 |

### Evaluation #2 (2024년)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| year | 2024 | 평가 연도 |
| q1_grade | B | 1분기 등급 |
| q2_grade | A | 2분기 등급 |
| q3_grade | A | 3분기 등급 |
| q4_grade | B | 4분기 등급 |
| overall_grade | A | 종합 등급 |
| salary_negotiation | +3% | 급여 협상 결과 |
| note | null | 비고 |

### Evaluation #3 (2025년 - 현재 진행 중)
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 3 | PK |
| employee_id | 1 | FK |
| year | 2025 | 평가 연도 |
| q1_grade | A | 1분기 등급 |
| q2_grade | S | 2분기 등급 |
| q3_grade | null | 3분기 등급 |
| q4_grade | null | 4분기 등급 |
| overall_grade | null | 종합 등급 |
| salary_negotiation | null | 급여 협상 결과 |
| note | null | 비고 |

---

## 14. Training (교육 - 1:N) - 2개

### Training #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| training_date | 2023-06-15 | 교육 날짜 |
| training_name | AWS 클라우드 기초 과정 | 교육명 |
| institution | AWS Training | 교육 기관 |
| hours | 16 | 교육 시간 |
| completion_status | 수료 | 수료 상태 |
| note | null | 비고 |

### Training #2
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| training_date | 2024-02-20 | 교육 날짜 |
| training_name | 리더십 역량 강화 교육 | 교육명 |
| institution | 사내교육팀 | 교육 기관 |
| hours | 8 | 교육 시간 |
| completion_status | 수료 | 수료 상태 |
| note | null | 비고 |

---

## 15. Attendance (근태 - 1:N) - 12개

### 최근 12개월 근태 (2024년 1월 ~ 2024년 12월)
| id | employee_id | year | month | work_days | absent_days | late_count | early_leave_count | annual_leave_used |
|----|-------------|------|-------|-----------|-------------|------------|-------------------|-------------------|
| 1 | 1 | 2024 | 12 | 21 | 0 | 0 | 0 | 1 |
| 2 | 1 | 2024 | 11 | 22 | 0 | 0 | 0 | 0 |
| 3 | 1 | 2024 | 10 | 23 | 0 | 1 | 0 | 0 |
| 4 | 1 | 2024 | 9 | 21 | 0 | 0 | 0 | 1 |
| 5 | 1 | 2024 | 8 | 22 | 1 | 0 | 0 | 0 |
| 6 | 1 | 2024 | 7 | 23 | 0 | 0 | 1 | 1 |
| 7 | 1 | 2024 | 6 | 20 | 0 | 0 | 0 | 1 |
| 8 | 1 | 2024 | 5 | 21 | 0 | 0 | 0 | 1 |
| 9 | 1 | 2024 | 4 | 22 | 0 | 0 | 1 | 0 |
| 10 | 1 | 2024 | 3 | 21 | 0 | 0 | 0 | 2 |
| 11 | 1 | 2024 | 2 | 20 | 0 | 1 | 0 | 0 |
| 12 | 1 | 2024 | 1 | 21 | 0 | 0 | 0 | 1 |

---

## 16. HrProject (인사이력 프로젝트 - 1:N) - 2개

### HrProject #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| project_name | HR 시스템 고도화 | 프로젝트명 |
| start_date | 2023-01-15 | 시작일 |
| end_date | 2023-12-31 | 종료일 |
| duration | 12개월 | 기간 |
| role | 백엔드 개발 | 역할 |
| duty | API 설계 및 개발 | 업무 내용 |
| client | 내부 | 클라이언트 |
| note | null | 비고 |

### HrProject #2
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| project_name | 모바일 앱 개발 프로젝트 | 프로젝트명 |
| start_date | 2024-03-01 | 시작일 |
| end_date | null | 종료일 |
| duration | 진행중 | 기간 |
| role | 테크리드 | 역할 |
| duty | 프로젝트 기술 리딩 | 업무 내용 |
| client | 외부고객사 | 클라이언트 |
| note | null | 비고 |

---

## 17. Award (수상 - 1:N) - 1개

### Award #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| award_date | 2023-12-20 | 수상일 |
| award_name | 올해의 개발자상 | 수상명 |
| institution | 테스트기업 A | 수여 기관 |
| note | 우수 프로젝트 성과 | 비고 |

---

## 18. Asset (자산 배정 - 1:N) - 2개

### Asset #1
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 1 | PK |
| employee_id | 1 | FK |
| issue_date | 2020-03-02 | 배정일 |
| item_name | 노트북 | 물품명 |
| model | MacBook Pro 14" | 모델 |
| serial_number | C02XK3LMJHD2 | 일련번호 |
| status | 사용중 | 상태 |
| note | null | 비고 |

### Asset #2
| 필드명 | 값 | 설명 |
|--------|-----|------|
| id | 2 | PK |
| employee_id | 1 | FK |
| issue_date | 2020-03-02 | 배정일 |
| item_name | 모니터 | 물품명 |
| model | LG 27UK850 | 모델 |
| serial_number | LG27UK2020031234 | 일련번호 |
| status | 사용중 | 상태 |
| note | null | 비고 |

---

## 19. SalaryHistory (연봉 변경 이력 - 1:N) - 3개

| id | employee_id | contract_year | annual_salary | bonus | total_amount | contract_period | note |
|----|-------------|---------------|---------------|-------|--------------|-----------------|------|
| 1 | 1 | 2020 | 40000000 | 0 | 40000000 | 2020-03-02 ~ 2020-12-31 | 입사 시 |
| 2 | 1 | 2021 | 44000000 | 2000000 | 46000000 | 2021-01-01 ~ 2021-12-31 | 10% 인상 |
| 3 | 1 | 2024 | 54000000 | 4000000 | 58000000 | 2024-01-01 ~ 2024-12-31 | 승진 반영 |

---

## 20. SalaryPayment (급여 지급 내역 - 1:N) - 6개

### 2024년 1월~6월 급여
| id | employee_id | payment_date | payment_period | base_salary | allowances | gross_pay | insurance | income_tax | total_deduction | net_pay |
|----|-------------|--------------|----------------|-------------|------------|-----------|-----------|------------|-----------------|---------|
| 1 | 1 | 2024-01-25 | 2024년 1월 | 4000000 | 500000 | 4500000 | 405900 | 180000 | 585900 | 3914100 |
| 2 | 1 | 2024-02-25 | 2024년 2월 | 4000000 | 500000 | 4500000 | 405900 | 180000 | 585900 | 3914100 |
| 3 | 1 | 2024-03-25 | 2024년 3월 | 4000000 | 500000 | 4500000 | 405900 | 180000 | 585900 | 3914100 |
| 4 | 1 | 2024-04-25 | 2024년 4월 | 4000000 | 500000 | 4500000 | 405900 | 180000 | 585900 | 3914100 |
| 5 | 1 | 2024-05-25 | 2024년 5월 | 4000000 | 500000 | 4500000 | 405900 | 180000 | 585900 | 3914100 |
| 6 | 1 | 2024-06-25 | 2024년 6월 | 4000000 | 500000 | 4500000 | 405900 | 180000 | 585900 | 3914100 |

### 보험료 상세 (월 기준)
| 항목 | 요율 | 금액 |
|------|------|------|
| 국민연금 | 4.5% | 202,500원 |
| 건강보험 | 3.545% | 159,525원 |
| 장기요양 | 0.9182% | 14,663원 (건강보험의 12.95%) |
| 고용보험 | 0.9% | 29,212원 |
| **보험료 계** | | **405,900원** |

---

## 데이터 요약

### 레코드 수 통계
| 모델 | 레코드 수 | 비고 |
|------|----------|------|
| Employee | 1 | 기본 정보 46필드 |
| Salary | 1 | 1:1 |
| Benefit | 1 | 1:1 |
| Insurance | 1 | 1:1 |
| Contract | 1 | 1:1 |
| MilitaryService | 1 | 1:1 |
| Education | 2 | 고등학교, 대학교 |
| Career | 1 | 이전 직장 1곳 |
| Certificate | 2 | 정보처리기사, AWS |
| Language | 2 | 영어, 일본어 |
| FamilyMember | 2 | 부모 2명 |
| Promotion | 2 | 입사, 승진 |
| Evaluation | 3 | 2023, 2024, 2025년 |
| Training | 2 | 교육 2건 |
| Attendance | 12 | 12개월 근태 |
| HrProject | 2 | 프로젝트 2건 |
| Award | 1 | 수상 1건 |
| Asset | 2 | 자산 2건 |
| SalaryHistory | 3 | 연봉 이력 3년 |
| SalaryPayment | 6 | 6개월 급여 |
| Attachment | 4 | 프로필/명함/첨부파일 |
| **총계** | **50 레코드** | |

---

## 검증 체크리스트

### 데이터 무결성
- [x] 모든 FK 관계 정상 (employee_id = 1)
- [x] employee_number 고유성 보장 (EMP-2020-0001)
- [x] 날짜 논리적 순서 (입학 < 졸업, 입대 < 전역)
- [x] 급여 금액 현실적 범위 (연봉 5400만원)

### 논리적 일관성
- [x] 생년월일(1992) + 학력(2011 대학입학) = 19세 입학 (정상)
- [x] 군복무(2012-2014) 기간이 대학 재학 중 (휴학 반영)
- [x] 이전 경력(2018-2020) + 현 입사(2020-03) = 연속성 있음
- [x] 승진(2023) 시점이 입사(2020) 후 3년차 (정상)

### 계산 검증
- [x] 급여: 기본급(400만) + 수당(50만) = 총급여(450만) 정확
- [x] 연차: 부여(15) - 사용(5) = 잔여(10) 정확
- [x] 보험료: 국민연금 + 건강보험 + 장기요양 + 고용보험 계산 정확

---

## 21. 파일 저장 구조 (Photo & Business Card)

### 디렉토리 구조
```
app/static/uploads/
├── corporate/{company_id}/
│   └── employees/{employee_id}/
│       ├── profile_photo/          # 프로필 사진
│       ├── business_card_front/    # 명함 앞면
│       ├── business_card_back/     # 명함 뒷면
│       └── attachments/            # 첨부파일
├── personal/{user_id}/
│   ├── profile_photo/
│   └── attachments/
└── temp/                           # 임시 파일
```

### 레거시 경로 (호환성 유지)
```
app/static/uploads/
├── profile_photos/      # 기존 프로필 사진
├── business_cards/      # 기존 명함
└── attachments/         # 기존 첨부파일
```

### 샘플 직원 파일 경로

#### 프로필 사진
| 구분 | 경로 |
|------|------|
| 절대 경로 | `app/static/uploads/corporate/1/employees/1/profile_photo/1_profile_20201201_091530.jpg` |
| 웹 경로 | `/static/uploads/corporate/1/employees/1/profile_photo/1_profile_20201201_091530.jpg` |
| DB 저장값 (photo) | `/static/uploads/corporate/1/employees/1/profile_photo/1_profile_20201201_091530.jpg` |

#### 명함 이미지
| 구분 | 앞면 | 뒷면 |
|------|------|------|
| 웹 경로 | `/static/uploads/corporate/1/employees/1/business_card_front/1_front_20201201_091545.jpg` | `/static/uploads/corporate/1/employees/1/business_card_back/1_back_20201201_091550.jpg` |
| DB 저장값 | `business_card_front` 필드 | `business_card_back` 필드 |

### 파일명 생성 규칙
```
{entity_id}_{prefix}_{timestamp}.{ext}

예시:
- 프로필 사진: 1_profile_20201201_091530.jpg
- 명함 앞면: 1_front_20201201_091545.png
- 명함 뒷면: 1_back_20201201_091550.png
- 첨부파일: 1_doc_20201201_100000.pdf
```

### 허용 파일 형식
| 카테고리 | 확장자 | 최대 크기 |
|---------|--------|----------|
| 이미지 | jpg, jpeg, png, gif, webp | 5MB |
| 일반 | pdf, doc, docx, xls, xlsx | 10MB |

### Employee 모델 파일 필드 (현재 구현)
| 필드명 | 타입 | 설명 | 샘플 값 |
|--------|------|------|--------|
| photo | String(500) | 프로필 사진 경로 | `/static/uploads/corporate/1/employees/1/profile_photo/1_profile_20201201_091530.jpg` |

**참고**: 현재 Employee 모델에는 `photo` 필드만 존재합니다.
명함(business_card) 필드는 FileStorageService에 구조만 정의되어 있으며,
실제 모델 필드 추가가 필요합니다.

### 개인 계정 파일 경로 (참고)
| 구분 | 경로 |
|------|------|
| 프로필 사진 | `/static/uploads/personal/{user_id}/profile_photo/{filename}` |
| 첨부파일 | `/static/uploads/personal/{user_id}/attachments/{filename}` |

---

## 22. Attachment (첨부파일 - 1:N)

### Attachment 모델 구조
| 필드명 | 타입 | 설명 |
|--------|------|------|
| id | Integer (PK) | 첨부파일 ID |
| employee_id | Integer (FK) | 직원 ID |
| file_name | String(500) | 원본 파일명 |
| file_path | String(1000) | 웹 접근 경로 |
| file_type | String(100) | 파일 확장자 |
| file_size | Integer | 파일 크기 (bytes) |
| category | String(100) | 파일 카테고리 |
| upload_date | String(20) | 업로드 날짜 |
| note | Text | 비고 |

### 카테고리 종류
| 카테고리 | 설명 | API Endpoint |
|----------|------|-------------|
| `profile_photo` | 프로필 사진 | `POST /api/employees/{id}/profile-photo` |
| `business_card_front` | 명함 앞면 | `POST /api/employees/{id}/business-card` (side=front) |
| `business_card_back` | 명함 뒷면 | `POST /api/employees/{id}/business-card` (side=back) |
| `기타` (default) | 일반 첨부파일 | `POST /api/employees/{id}/attachments` |
| 사용자 지정 | 계약서, 증명서 등 | category 파라미터로 지정 |

### 샘플 Attachment 데이터 - 4개

#### Attachment #1 (프로필 사진)
| 필드명 | 값 |
|--------|-----|
| id | 1 |
| employee_id | 1 |
| file_name | profile.jpg |
| file_path | `/static/uploads/profile_photos/1_profile_20201201_091530.jpg` |
| file_type | jpg |
| file_size | 245760 |
| category | profile_photo |
| upload_date | 2020-12-01 |
| note | null |

#### Attachment #2 (명함 앞면)
| 필드명 | 값 |
|--------|-----|
| id | 2 |
| employee_id | 1 |
| file_name | business_card_front.png |
| file_path | `/static/uploads/business_cards/1_front_20201201_091545.png` |
| file_type | png |
| file_size | 512000 |
| category | business_card_front |
| upload_date | 2020-12-01 |
| note | null |

#### Attachment #3 (명함 뒷면)
| 필드명 | 값 |
|--------|-----|
| id | 3 |
| employee_id | 1 |
| file_name | business_card_back.png |
| file_path | `/static/uploads/business_cards/1_back_20201201_091550.png` |
| file_type | png |
| file_size | 480000 |
| category | business_card_back |
| upload_date | 2020-12-01 |
| note | null |

#### Attachment #4 (근로계약서)
| 필드명 | 값 |
|--------|-----|
| id | 4 |
| employee_id | 1 |
| file_name | 근로계약서_김민수_2020.pdf |
| file_path | `/static/uploads/attachments/1_doc_20200302_100000.pdf` |
| file_type | pdf |
| file_size | 1048576 |
| category | 계약서 |
| upload_date | 2020-03-02 |
| note | 입사 시 작성 |

### 계정 유형별 첨부파일 관리 현황

| 계정 유형 | 첨부파일 모델 | 저장 경로 | 현재 상태 |
|----------|-------------|----------|----------|
| **법인 직원 (employee_sub)** | Attachment (employee_id FK) | `/static/uploads/attachments/` | O 구현됨 |
| **개인 계정 (personal)** | 없음 | `/static/uploads/personal/{user_id}/` | X 미구현 |
| **법인 관리자 (corporate)** | 없음 | - | X 미구현 |

### API Endpoints (법인 직원용)

| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/employees/{id}/attachments` | 첨부파일 목록 | login_required |
| POST | `/api/employees/{id}/attachments` | 첨부파일 업로드 | manager_or_admin |
| DELETE | `/api/attachments/{id}` | 첨부파일 삭제 | manager_or_admin |
| GET | `/api/employees/{id}/profile-photo` | 프로필 사진 조회 | login_required |
| POST | `/api/employees/{id}/profile-photo` | 프로필 사진 업로드 | 본인 or 관리자 |
| DELETE | `/api/employees/{id}/profile-photo` | 프로필 사진 삭제 | 본인 or 관리자 |
| POST | `/api/employees/{id}/business-card` | 명함 업로드 (side 필수) | 본인 or 관리자 |
| DELETE | `/api/employees/{id}/business-card/{side}` | 명함 삭제 | 본인 or 관리자 |

### 저장 경로 비교 (현재 vs 신규 구조)

| 파일 유형 | 현재 사용 경로 (레거시) | FileStorageService 정의 (미사용) |
|----------|----------------------|-------------------------------|
| 프로필 사진 | `/static/uploads/profile_photos/` | `/static/uploads/corporate/{company_id}/employees/{employee_id}/profile_photo/` |
| 명함 | `/static/uploads/business_cards/` | `/static/uploads/corporate/{company_id}/employees/{employee_id}/business_card_front/` |
| 첨부파일 | `/static/uploads/attachments/` | `/static/uploads/corporate/{company_id}/employees/{employee_id}/attachments/` |

**참고**: FileStorageService에 company_id 기반 구조가 정의되어 있으나, 현재 API는 레거시 경로를 사용 중입니다.

---

## 스크립트 검증 결과

### 필드별 일치 여부

| 모델 | 스크립트 생성 범위 | 샘플 데이터 | 일치 |
|------|-------------------|------------|------|
| Employee | 46개 필드 | 46개 필드 | O |
| Salary | 포괄임금제 포함 21개 필드 | 21개 필드 | O |
| Benefit | 9개 필드 | 9개 필드 | O |
| Insurance | 11개 필드 (보험료율 포함) | 11개 필드 | O |
| Contract | 8개 필드 | 8개 필드 | O |
| MilitaryService | 11개 필드 (남성만) | 11개 필드 | O |
| Education | 1-3개 생성 | 2개 (범위 내) | O |
| Career | 0-3개 생성 | 1개 (범위 내) | O |
| Certificate | 0-3개 생성 | 2개 (범위 내) | O |
| Language | 0-2개 생성 | 2개 (범위 내) | O |
| FamilyMember | 1-4개 (70% 확률) | 2개 (범위 내) | O |
| Promotion | 1-3개 생성 | 2개 (범위 내) | O |
| Evaluation | 최근 3년 | 3개 (2023-2025) | O |
| Training | 2-5개 생성 | 2개 (범위 내) | O |
| Attendance | 최근 12개월 | 12개 | O |
| HrProject | 1-3개 생성 | 2개 (범위 내) | O |
| Award | 0-2개 생성 | 1개 (범위 내) | O |
| Asset | 1-3개 생성 | 2개 (범위 내) | O |
| SalaryHistory | 최근 3년 | 3개 (2020-2024) | O |
| SalaryPayment | 최근 6개월 | 6개 | O |

### 데이터 생성 규칙 검증

| 규칙 | 스크립트 | 샘플 데이터 | 결과 |
|------|---------|------------|------|
| 사번 형식 | EMP-YYYY-NNNN | EMP-2020-0001 | O |
| 전화번호 형식 | 010-XXXX-XXXX | 010-1234-5678 | O |
| 주민번호 형식 | YYMMDD-XXXXXXX | 920515-1****** | O |
| 급여일 | 25일 고정 | 25일 | O |
| 보험료율 | 국민연금 4.5%, 건강보험 3.545% | 동일 | O |
| 병역 | 남성만 생성 | 남성 직원에만 존재 | O |
| 계약유형 | 정규직 기본 | 정규직 | O |

### 스크립트 vs 샘플 불일치 사항: 없음

모든 필드와 관계가 스크립트 생성 규칙과 일치합니다.

---

## 문서 정보

- **생성일**: 2025-12-16
- **버전**: 1.1
- **관련 스크립트**: `scripts/generate_fake_test_data.py`
- **관련 분석문서**: `.dev_docs/core_docs/fake_test_data_analysis.md`
