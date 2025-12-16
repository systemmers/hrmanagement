# 프로필/인사카드 프론트엔드 템플릿 분석 보고서

## 분석 일자
2025-12-14

## 분석 대상 개요

### 3가지 계정 유형별 템플릿

1. **법인 관리자 - 직원 인사카드**
   - 파일: `profile/detail.html` (page_mode='hr_card', account_type='corporate' or 'corporate_admin')
   - 용도: 관리자가 직원의 전체 인사정보 조회
   - 섹션: 개인정보, 소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 가족정보, 학력, 경력, 자격증, 언어능력, 병역, 수상, 프로젝트, 근로계약, 인사이동, 근태

2. **법인 직원 - 회사 인사카드**
   - 파일: `mypage/company_info.html`
   - 용도: 법인 직원이 자신의 회사 인사정보 조회
   - 섹션: 동일 (개인정보 ~ 근태)

3. **개인 계정 - 프로필**
   - 파일: `profile/detail.html` (page_mode!='hr_card')
   - 용도: 개인 계정이 자신의 프로필 조회
   - 섹션: 개인정보, 가족정보, 학력, 경력, 자격증, 언어능력, 병역, 수상 (법인 전용 섹션 제외)

4. **개인 계정 - 회사 인사카드**
   - 파일: `personal/company_card_detail.html`
   - 용도: 개인 계정이 계약한 법인의 인사카드 조회
   - 섹션: 동일 (개인정보 ~ 근태, 법인 직원과 동일)

## 템플릿 구조 분석

### 공통 구조 패턴

모든 템플릿은 다음과 같은 공통 구조를 공유합니다:

```jinja2
{% extends "base.html" %}

<!-- 헤더: 직원/프로필 헤더 카드 -->
{% include 'partials/employee_detail/_employee_header.html' %}

<!-- 섹션 1-6: 기본정보 -->
{% include 'partials/employee_detail/_basic_info.html' %}

<!-- 섹션 7-13: 이력 및 경력 -->
{% include 'partials/employee_detail/_history_info.html' %}

<!-- 섹션 14-17: 인사기록 (인사카드 전용) -->
{% if page_mode == 'hr_card' %}
    {% include 'partials/employee_detail/_hr_records.html' %}
{% endif %}
```

### 파셜 템플릿 재사용

| 파셜 파일 | 용도 | 사용 템플릿 |
|---------|------|------------|
| `_employee_header.html` | 직원/프로필 헤더 카드 | 모든 템플릿 (variant 분기) |
| `_basic_info.html` | 섹션 1-7 (개인정보~가족정보) | 모든 템플릿 (조건부 표시) |
| `_history_info.html` | 섹션 8-13 (학력~프로젝트) | 모든 템플릿 (조건부 표시) |
| `_hr_records.html` | 섹션 14-17 (근로계약~근태) | 인사카드만 (`page_mode=='hr_card'`) |

## 섹션별 필드 상세 비교

### 헤더 카드 (_employee_header.html)

**variant 분기: corporate vs personal**

#### Corporate 변형 (법인 직원/인사카드)
- **메타 정보**
  - 소속 부서 (department)
  - 직급 (position)
  - 재직상태 (status)

- **통계 정보**
  - 입사일 (hire_date)
  - 재직기간 (tenure)
  - 연차 잔여 (remaining_leave)
  - 사번 (employee_number)

- **명함 영역**: 표시됨 (앞면/뒷면)

#### Personal 변형 (개인 계정 프로필)
- **메타 정보**
  - 이메일 (email)
  - 전화번호 (phone)
  - 주소 (address)

- **통계 정보**
  - 생년월일 (birth_date)
  - 계약 수 (contract_count)
  - 가입일 (created_at)
  - 회원번호 (user_number)

- **명함 영역**: 표시 안 됨

**일관성 상태**: ✅ 우수
- variant 조건부 분기로 명확하게 구분
- 각 변형별로 일관된 필드 구성

---

### 섹션 1: 개인 기본정보 (_basic_info.html)

**모든 템플릿에 공통 표시**

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 성명 (한글) | employee.name | - |
| 2 | 여권명 (영문) | employee.english_name | - |
| 3 | 주민등록번호 | employee.resident_number | - |
| 4 | 생년월일 | employee.birth_date | - |
| 5 | 성별 | employee.gender | get_gender_label() 함수 사용 |
| 6 | 결혼여부 | employee.marital_status | get_marital_status_label() 함수 사용 |
| 7 | 휴대전화 | employee.phone | format_phone() 함수 사용 |
| 8 | 개인 이메일 | employee.email | highlight=true |
| 9 | 비상연락처 | employee.emergency_contact | (관계) 포함 |
| 10 | 혈액형 | employee.blood_type | - |
| 11 | 종교 | employee.religion | - |
| 12 | 취미 | employee.hobby | - |
| 13 | 특기 | employee.specialty | - |
| 14 | 장애정보 | employee.disability_info | - |
| 15 | 주민등록상 주소 | employee.address | - |
| 16 | 상세주소 | employee.detailed_address | - |
| 17 | 실제 거주지 | employee.actual_address | 서브섹션 |
| 18 | 상세주소 | employee.actual_detailed_address | 서브섹션 |

**일관성 상태**: ✅ 우수
- 모든 템플릿에서 동일한 순서와 라벨 사용
- 함수 호출도 일관됨

---

### 섹션 2: 소속정보 (_basic_info.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 소속 | employee.department | highlight=true |
| 2 | 부서 | employee.team or employee.department | highlight=true |
| 3 | 직급 | employee.position | - |
| 4 | 직책 | employee.job_title | - |
| 5 | 사원번호 | employee.employee_number | 기본값: 'EMP-%03d' |
| 6 | 근무형태 | employee.employment_type | get_employment_type_label() |
| 7 | 근무지 | employee.work_location | 기본값: '본사' |
| 8 | 내선번호 | employee.internal_phone | - |
| 9 | 회사 이메일 | employee.company_email | - |
| 10 | 재직상태 | employee.status | badge 스타일 |
| 11 | 입사일 | employee.hire_date | - |
| 12 | 재직기간 | calculate_tenure(hire_date) | highlight=true |

**일관성 상태**: ✅ 우수
- 인사카드에서만 표시되는 섹션
- 필드 순서와 라벨 일관됨

---

### 섹션 3: 계약정보 (_basic_info.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 계약형태 | contract.contract_type | fallback: employment_type |
| 2 | 계약기간 | contract.contract_period | fallback: '무기한' |
| 3 | 계약시작일 | contract.contract_date | fallback: hire_date |
| 4 | 직원유형 | contract.employee_type | - |
| 5 | 근무형태 | contract.work_type | - |
| 6 | 시용기간 종료 | employee.probation_end | - |
| 7 | 근무시간 | - | 하드코딩: '09:00 ~ 18:00' |
| 8 | 휴게시간 | - | 하드코딩: '12:00 ~ 13:00' |
| 9 | 퇴사일 | employee.resignation_date | 조건부 표시 |

**일관성 상태**: ⚠️ 주의
- 근무시간/휴게시간이 하드코딩되어 있음
- contract 객체와 employee 객체 간 fallback 로직 복잡

**개선 권장사항**:
- 근무시간/휴게시간을 contract 또는 employee 필드로 이동
- fallback 로직 명확화

---

### 섹션 4: 급여정보 (_basic_info.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 급여형태 | salary.salary_type | - |
| 2 | 기본급 | salary.base_salary | 천 단위 구분자, '원' 표시 |
| 3 | 직책수당 | salary.position_allowance | 천 단위 구분자, '원' 표시 |
| 4 | 식대 | salary.meal_allowance | 천 단위 구분자, '원' 표시 |
| 5 | 교통비 | salary.transportation_allowance | 천 단위 구분자, '원' 표시 |
| 6 | 총 급여 | salary.total_salary | 천 단위 구분자, '원' 표시 |
| 7 | 급여지급일 | salary.payment_day | '매월 X일' 형식 |
| 8 | 급여지급방법 | salary.payment_method | - |
| 9 | 급여계좌 | salary.bank_account | - |

**일관성 상태**: ✅ 우수
- 금액 포맷팅 일관됨 (`{:,}` + '원')
- 필드 순서와 라벨 일관됨

---

### 섹션 5: 연차 및 복리후생 (_basic_info.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 연차 발생일수 | benefit.annual_leave_granted | '일' 표시 |
| 2 | 연차 사용일수 | benefit.annual_leave_used | '일' 표시 |
| 3 | 연차 잔여일수 | benefit.annual_leave_remaining | '일' 표시, highlight=true |
| 4 | 퇴직금 유형 | benefit.severance_type | - |
| 5 | 퇴직금 적립방법 | benefit.severance_method | - |

**일관성 상태**: ✅ 우수
- 카드 헤더에 연도 표시: `({{ benefit.year }}년)`
- 필드 순서와 라벨 일관됨

---

### 섹션 6: 4대보험 (_basic_info.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 4대보험 | insurance.* | 전체 가입 여부, badge 스타일 |
| 2 | 건강보험 | insurance.health_insurance | badge 스타일 |
| 3 | 국민연금 | insurance.national_pension | badge 스타일 |
| 4 | 고용보험 | insurance.employment_insurance | badge 스타일 |
| 5 | 산재보험 | insurance.industrial_accident | badge 스타일 |

**일관성 상태**: ✅ 우수
- badge 스타일 일관됨 (가입: success, 미가입: secondary)
- 필드 순서와 라벨 일관됨

---

### 섹션 7: 가족정보 (_basic_info.html)

**모든 템플릿에 공통 표시**

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 관계 | family.relation | get_relation_label() |
| 2 | 성명 | family.name | - |
| 3 | 생년월일 | family.birth_date | '-' fallback |
| 4 | 직업 | family.occupation | '-' fallback |
| 5 | 연락처 | family.phone | '-' fallback |
| 6 | 동거여부 | family.living_together | badge (동거: success, 별거: secondary) |

**일관성 상태**: ✅ 우수
- 테이블 칼럼 순서와 헤더명 일관됨
- badge 스타일 일관됨

---

### 섹션 8: 학력정보 (_history_info.html)

**모든 템플릿에 공통 표시**

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 학력구분 | edu.degree | get_degree_label() |
| 2 | 학교명 | edu.school | - |
| 3 | 졸업년월 | edu.graduation_year | - |
| 4 | 전공 | edu.major | '-' fallback |
| 5 | 학점 | edu.gpa | '-' fallback |
| 6 | 졸업유무 | - | 하드코딩: '졸업' badge |
| 7 | 비고 | edu.note | '-' fallback |

**일관성 상태**: ⚠️ 주의
- '졸업유무' 칼럼이 하드코딩되어 항상 '졸업' 표시
- 졸업/재학/중퇴 등 상태 구분 불가

**개선 권장사항**:
- `edu.graduation_status` 필드 추가하여 동적 표시

---

### 섹션 9: 경력정보 (_history_info.html)

**모든 템플릿에 공통 표시**

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 직장명 | career.company | - |
| 2 | 입사일 | career.start_date | - |
| 3 | 퇴사일 | career.end_date | '재직중' fallback |
| 4 | 경력 | - | 하드코딩: '-' |
| 5 | 부서 | career.department | '-' fallback |
| 6 | 직급 | career.position | '-' fallback |
| 7 | 담당업무 | career.duty | '-' fallback |
| 8 | 연봉 | career.salary | 천 단위 구분자, '원' 표시 |

**일관성 상태**: ⚠️ 주의
- '경력' 칼럼이 하드코딩되어 항상 '-' 표시
- 입사일/퇴사일로 경력 기간 자동 계산 안 됨

**개선 권장사항**:
- '경력' 칼럼을 입사일/퇴사일로 자동 계산하거나 필드 추가
- 또는 불필요한 칼럼으로 판단되면 제거

**테이블 하단 요약**:
- "총 경력: X개사" 표시

---

### 섹션 10: 자격증 및 면허 (_history_info.html)

**모든 템플릿에 공통 표시**

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 구분 | - | 하드코딩: '자격증' |
| 2 | 종류 | cert.name | - |
| 3 | 등급/점수 | cert.grade | '-' fallback |
| 4 | 발행처 | cert.issuer | - |
| 5 | 취득일 | cert.acquired_date | - |
| 6 | 비고 | cert.expiry_date | '만료: X' 형식 |

**일관성 상태**: ⚠️ 주의
- '구분' 칼럼이 하드코딩되어 항상 '자격증' 표시
- 면허 vs 자격증 구분 불가

**개선 권장사항**:
- `cert.certificate_type` 필드 추가 (자격증/면허 구분)
- 또는 불필요한 칼럼이면 제거

---

### 섹션 11: 언어능력 (_history_info.html)

**모든 템플릿에 공통 표시**

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 언어 | lang.language | - |
| 2 | 수준 | lang.level | get_level_label() |
| 3 | 시험명 | lang.test_name | '-' fallback |
| 4 | 점수 | lang.score | '-' fallback |
| 5 | 취득일 | lang.acquired_date | '-' fallback |

**일관성 상태**: ✅ 우수
- 테이블 칼럼 순서와 헤더명 일관됨
- get_level_label() 함수 사용 일관됨

---

### 섹션 12: 병역정보 (_history_info.html)

**모든 템플릿에 공통 표시**

#### 필드 목록 (순서대로)

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 병역구분 | military.status | get_military_status_label() |
| 2 | 군별 | military.branch | get_branch_label() |
| 3 | 복무기간 | military.start_date ~ end_date | 'X ~ Y' 또는 '복무중' |
| 4 | 계급 | military.rank | - |
| 5 | 보직 | military.duty | - |
| 6 | 병과 | military.specialty | - |
| 7 | 면제사유 | military.exemption_reason | 조건부 표시 |

**일관성 상태**: ✅ 우수
- 필드 순서와 라벨 일관됨
- 함수 호출 일관됨

---

### 섹션 13: 수상내역 (_history_info.html)

**모든 템플릿에 공통 표시**

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 수상일 | award.award_date | '-' fallback |
| 2 | 수상명 | award.award_name | - |
| 3 | 수여기관 | award.institution | '-' fallback |
| 4 | 수상내용 | award.description | '-' fallback |
| 5 | 비고 | award.notes | '-' fallback |

**일관성 상태**: ✅ 우수
- 테이블 칼럼 순서와 헤더명 일관됨
- 정렬: `award_date` 내림차순

---

### 섹션 14: 유사사업 참여경력 (_history_info.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 테이블 구조

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 사업명 | project.project_name | - |
| 2 | 참여기간 | project.start_date ~ end_date | 'X ~ Y' 형식 |
| 3 | 기간 | project.duration | - |
| 4 | 담당업무 | project.duty | - |
| 5 | 역할/직책 | project.role | - |
| 6 | 발주처 | project.client | - |

**일관성 상태**: ✅ 우수
- 테이블 칼럼 순서와 헤더명 일관됨

---

### 섹션 15: 근로계약 및 연봉 (_hr_records.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 하위 섹션 1: 근로계약 이력

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 계약일 | employee.hire_date | - |
| 2 | 계약구분 | - | 하드코딩: '정규직' badge |
| 3 | 계약기간 시작 | employee.hire_date | - |
| 4 | 계약기간 종료 | - | 하드코딩: '-' |
| 5 | 계약기간 | calculate_tenure(hire_date) | - |
| 6 | 직원구분 | - | 하드코딩: '정규직' |
| 7 | 근무형태 | - | 하드코딩: '전일제' |
| 8 | 비고 | - | 하드코딩: '신규입사' |

**일관성 상태**: ❌ 불량
- 대부분의 필드가 하드코딩되어 있음
- 실제 데이터 기반 표시 불가

**개선 권장사항**:
- contract 또는 employee 객체에서 실제 데이터 가져오기
- 하드코딩 제거

#### 하위 섹션 2: 연봉계약 이력

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 계약연도 | history.contract_year | 'X년' 형식 |
| 2 | 연봉 | history.annual_salary | 천 단위 구분자, '원' 표시 |
| 3 | 상여금 | history.bonus | 천 단위 구분자, '원' 표시 |
| 4 | 총액 | history.total_amount | 천 단위 구분자, '원' 표시, bold |
| 5 | 계약기간 | history.contract_period | - |

**일관성 상태**: ✅ 우수
- 정렬: `contract_year` 내림차순
- 금액 포맷팅 일관됨

#### 하위 섹션 3: 급여 지급 이력

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 지급일 | payment.payment_date | - |
| 2 | 지급기간 | payment.payment_period | - |
| 3 | 기본급 | payment.base_salary | 천 단위 구분자, '원' 표시 |
| 4 | 수당 | payment.allowances | 천 단위 구분자, '원' 표시 |
| 5 | 총지급액 | payment.gross_pay | 천 단위 구분자, '원' 표시 |
| 6 | 4대보험 | payment.insurance | 천 단위 구분자, '원' 표시 |
| 7 | 소득세 | payment.income_tax | 천 단위 구분자, '원' 표시 |
| 8 | 공제합계 | payment.total_deduction | 천 단위 구분자, '원' 표시 |
| 9 | 실지급액 | payment.net_pay | 천 단위 구분자, '원' 표시, bold |
| 10 | 비고 | payment.note | '-' fallback |

**일관성 상태**: ✅ 우수
- 정렬: `payment_date` 내림차순
- 금액 포맷팅 일관됨

---

### 섹션 16: 인사이동 및 고과 (_hr_records.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 하위 섹션 1: 인사이동 및 승진

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 발령일 | promo.effective_date | - |
| 2 | 발령구분 | promo.promotion_type | badge (신규채용: info, 승진: success, 기타: secondary) |
| 3 | 발령전 | promo.from_department | '-' fallback |
| 4 | 발령후 | promo.to_department | - |
| 5 | 발령전 직급 | promo.from_position | '-' fallback |
| 6 | 발령후 직급 | promo.to_position | - |
| 7 | 직무 | promo.job_role | '-' fallback |
| 8 | 발령사유 | promo.reason | '-' fallback |

**일관성 상태**: ✅ 우수
- 정렬: `effective_date` 내림차순
- badge 스타일 일관됨

#### 하위 섹션 2: 인사고과 - 정기평가

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 연차 | eval.year | 'X년' 형식 |
| 2 | 1분기 | eval.q1_grade | badge (S/A: success, B: primary, 기타: warning) |
| 3 | 2분기 | eval.q2_grade | badge (S/A: success, B: primary, 기타: warning) |
| 4 | 3분기 | eval.q3_grade | badge (S/A: success, B: primary, 기타: warning) |
| 5 | 4분기 | eval.q4_grade | badge (S/A: success, B: primary, 기타: warning) |
| 6 | 종합평가 | eval.overall_grade | badge (S/A: success, B: primary, 기타: warning), bold |
| 7 | 연봉협상 | eval.salary_negotiation | '-' fallback |
| 8 | 비고 | eval.note | '-' fallback |

**일관성 상태**: ✅ 우수
- 정렬: `year` 내림차순
- badge 스타일 일관됨

#### 하위 섹션 3: 교육훈련

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 교육일 | train.training_date | - |
| 2 | 교육명 | train.training_name | - |
| 3 | 교육기관 | train.institution | - |
| 4 | 교육시간 | train.hours | 'X시간' 형식 |
| 5 | 이수여부 | train.completion_status | badge (이수: success, 미이수: danger) |
| 6 | 비고 | train.note | '-' fallback |

**일관성 상태**: ✅ 우수
- 정렬: `training_date` 내림차순
- badge 스타일 일관됨

---

### 섹션 17: 근태 및 비품 (_hr_records.html)

**조건**: `page_mode == 'hr_card'` (인사카드 전용)

#### 하위 섹션 1: 근태현황

| 순번 | 필드명(라벨) | 데이터 키 | 비고 |
|-----|------------|----------|------|
| 1 | 출근일수 | attendance_summary.total_work_days | '일' 표시 |
| 2 | 결근일수 | attendance_summary.total_absent_days | '일' 표시 |
| 3 | 지각횟수 | attendance_summary.total_late_count | '회' 표시 |
| 4 | 조퇴횟수 | attendance_summary.total_early_leave | '회' 표시 |
| 5 | 연차사용 | attendance_summary.total_annual_used | '일' 표시 |
| 6 | 연차잔여 | benefit.annual_leave_remaining | '일' 표시, highlight=true, 기본값: 15 |

**일관성 상태**: ✅ 우수
- 필드 순서와 라벨 일관됨
- 기본값 처리 일관됨

#### 하위 섹션 2: 비품지급

| 칼럼 순서 | 헤더명(한글) | 데이터 키 | 비고 |
|----------|------------|----------|------|
| 1 | 지급일 | asset.issue_date | - |
| 2 | 품목 | asset.item_name | - |
| 3 | 모델/사양 | asset.model | - |
| 4 | 시리얼번호 | asset.serial_number | - |
| 5 | 상태 | asset.status | badge (사용중: success, 반납: secondary, 기타: danger) |
| 6 | 비고 | asset.note | '-' fallback |

**일관성 상태**: ✅ 우수
- 정렬: `issue_date` 내림차순
- badge 스타일 일관됨

---

## 전체 섹션 순서 비교

### 법인 관리자/직원 인사카드 (page_mode='hr_card')

1. 개인 기본정보
2. 소속정보
3. 계약정보
4. 급여정보
5. 연차 및 복리후생
6. 4대보험
7. 가족정보
8. 학력정보
9. 경력정보
10. 자격증 및 면허
11. 언어능력
12. 병역정보
13. 수상내역
14. 유사사업 참여경력
15. 근로계약 및 연봉 (하위: 근로계약 이력, 연봉계약 이력, 급여 지급 이력)
16. 인사이동 및 고과 (하위: 인사이동 및 승진, 인사고과 - 정기평가, 교육훈련)
17. 근태 및 비품 (하위: 근태현황, 비품지급)

**총 17개 섹션 (21개 하위 섹션 포함)**

### 개인 계정 프로필 (page_mode!='hr_card')

1. 개인 기본정보
2. 가족정보
3. 학력정보
4. 경력정보
5. 자격증 및 면허
6. 언어능력
7. 병역정보
8. 수상내역

**총 8개 섹션**

---

## 불일치 및 개선 필요 사항 요약

### 심각도 높음 (빨강 - 즉시 수정 권장)

| 위치 | 문제 | 영향 | 권장 조치 |
|-----|------|------|---------|
| 섹션 15 - 근로계약 이력 | 대부분 필드 하드코딩 | 데이터 미반영, 사용자 혼란 | contract 테이블 데이터 활용, 하드코딩 제거 |

### 심각도 중간 (노랑 - 개선 권장)

| 위치 | 문제 | 영향 | 권장 조치 |
|-----|------|------|---------|
| 섹션 3 - 계약정보 | 근무시간/휴게시간 하드코딩 | 유연성 부족 | contract 또는 employee 필드로 이동 |
| 섹션 8 - 학력정보 | 졸업유무 하드코딩 ('졸업') | 재학/중퇴 구분 불가 | graduation_status 필드 추가 |
| 섹션 9 - 경력정보 | 경력 칼럼 하드코딩 ('-') | 경력 기간 미표시 | 입사/퇴사일로 자동 계산 또는 필드 추가 |
| 섹션 10 - 자격증 | 구분 칼럼 하드코딩 ('자격증') | 면허 vs 자격증 구분 불가 | certificate_type 필드 추가 |

### 심각도 낮음 (초록 - 선택적 개선)

| 위치 | 문제 | 영향 | 권장 조치 |
|-----|------|------|---------|
| 전체 | fallback 로직 복잡 | 유지보수성 저하 | 템플릿 매크로 또는 헬퍼 함수로 추출 |
| 전체 | badge 스타일 조건 중복 | 코드 중복 | badge 매크로 함수 생성 |

---

## 템플릿 재사용성 분석

### 현재 파셜 구조

```
partials/employee_detail/
├── _employee_header.html      (변형: corporate, personal)
├── _basic_info.html            (섹션 1-7, 조건부 표시)
├── _history_info.html          (섹션 8-14, 조건부 표시)
└── _hr_records.html            (섹션 15-17, 인사카드 전용)
```

### 재사용성 평가

| 파셜 파일 | 재사용성 | 유연성 | 비고 |
|---------|---------|-------|------|
| _employee_header.html | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | variant 조건으로 완벽한 분기 |
| _basic_info.html | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | page_mode 조건으로 유연한 섹션 표시 |
| _history_info.html | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | page_mode 조건으로 유연한 섹션 표시 |
| _hr_records.html | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 인사카드 전용이지만 하드코딩 문제 존재 |

**총평**: 파셜 구조가 잘 설계되어 있으며, 템플릿 재사용성이 높음. 조건부 분기를 통해 여러 계정 유형을 효율적으로 지원.

---

## 필드 라벨 일관성 분석

### 동일 필드, 다른 라벨 사례

**현재 발견 없음** - 모든 필드 라벨이 일관되게 사용됨

### 동일 라벨, 다른 필드 사례

**현재 발견 없음** - 모든 라벨이 고유한 필드에 매핑됨

### 라벨 네이밍 패턴 분석

- **일관된 패턴**: 대부분의 라벨이 명확하고 일관된 한글 용어 사용
- **포맷팅**:
  - 금액: `{:,}원` 형식
  - 날짜: `YYYY-MM-DD` 형식
  - 기간: `X ~ Y` 형식
  - 단위: `X일`, `X회`, `X시간` 형식

---

## 함수 사용 일관성 분석

### 사용되는 헬퍼 함수

| 함수명 | 용도 | 사용 위치 | 일관성 |
|-------|------|---------|--------|
| `get_gender_label()` | 성별 라벨 변환 | 섹션 1 | ✅ |
| `get_marital_status_label()` | 결혼여부 라벨 변환 | 섹션 1 | ✅ |
| `format_phone()` | 전화번호 포맷팅 | 섹션 1 | ✅ |
| `get_employment_type_label()` | 근무형태 라벨 변환 | 섹션 2, 3 | ✅ |
| `get_status_badge_class()` | 재직상태 badge 클래스 | 섹션 2 | ✅ |
| `get_status_text()` | 재직상태 텍스트 | 섹션 2, 헤더 | ✅ |
| `calculate_tenure()` | 재직기간 계산 | 섹션 2, 15, 헤더 | ✅ |
| `get_relation_label()` | 가족 관계 라벨 변환 | 섹션 7 | ✅ |
| `get_degree_label()` | 학력구분 라벨 변환 | 섹션 8 | ✅ |
| `get_level_label()` | 언어 수준 라벨 변환 | 섹션 11 | ✅ |
| `get_military_status_label()` | 병역구분 라벨 변환 | 섹션 12 | ✅ |
| `get_branch_label()` | 군별 라벨 변환 | 섹션 12 | ✅ |

**총평**: 모든 헬퍼 함수가 일관되게 사용되고 있으며, 명명 규칙도 통일됨 (`get_*_label()` 패턴)

---

## 조건부 표시 로직 분석

### page_mode 조건

| 섹션 | 조건 | 표시 여부 |
|-----|------|---------|
| 소속정보 (섹션 2) | `page_mode == 'hr_card'` | 인사카드만 |
| 계약정보 (섹션 3) | `page_mode == 'hr_card'` | 인사카드만 |
| 급여정보 (섹션 4) | `page_mode == 'hr_card'` | 인사카드만 |
| 복리후생 (섹션 5) | `page_mode == 'hr_card'` | 인사카드만 |
| 4대보험 (섹션 6) | `page_mode == 'hr_card'` | 인사카드만 |
| 프로젝트 (섹션 14) | `page_mode == 'hr_card'` | 인사카드만 |
| 근로계약/연봉 (섹션 15) | `page_mode == 'hr_card'` | 인사카드만 |
| 인사이동/고과 (섹션 16) | `page_mode == 'hr_card'` | 인사카드만 |
| 근태/비품 (섹션 17) | `page_mode == 'hr_card'` | 인사카드만 |

### account_type 조건

| 섹션 | 조건 | 표시 여부 |
|-----|------|---------|
| 모든 인사카드 섹션 | `account_type != 'corporate_admin'` | 관리자 본인 제외 |

**총평**: 조건부 로직이 명확하고 일관됨. `page_mode`와 `account_type`을 조합하여 유연한 표시 제어.

---

## 네비게이션 일관성 분석

### 섹션 네비게이션 (section_nav 매크로)

#### 법인 인사카드 (variant='full')
- 섹션 1-17 모두 표시
- 네비게이션 링크와 섹션 ID 매칭

#### 개인 프로필 (variant='profile')
- 섹션 1, 7-13 표시 (법인 전용 섹션 제외)
- 네비게이션 링크와 섹션 ID 매칭

**일관성 상태**: ✅ 우수
- section_nav 매크로가 variant에 따라 정확히 분기
- 섹션 ID와 네비게이션 href가 일치

---

## 스타일 클래스 일관성 분석

### 공통 클래스 패턴

| 클래스명 | 용도 | 사용 위치 |
|---------|------|---------|
| `.content-section` | 섹션 컨테이너 | 모든 섹션 |
| `.card` | 카드 컨테이너 | 모든 카드 |
| `.card-header` | 카드 헤더 | 모든 카드 |
| `.card-body` | 카드 본문 | 모든 카드 |
| `.info-grid` | 정보 그리드 레이아웃 | 필드 그리드 섹션 |
| `.info-item` | 정보 항목 | 필드 그리드 내 |
| `.info-label` | 라벨 | 필드 그리드 내 |
| `.info-value` | 값 | 필드 그리드 내 |
| `.table-container` | 테이블 컨테이너 | 모든 테이블 섹션 |
| `.table-empty` | 빈 테이블 행 | 데이터 없음 표시 |
| `.badge` | 뱃지 | 상태/구분 표시 |

**일관성 상태**: ✅ 우수
- 모든 템플릿에서 동일한 클래스 패턴 사용
- BEM 스타일 명명 규칙 준수

---

## 데이터 바인딩 패턴 분석

### employee vs profile vs contract vs salary 등

| 데이터 객체 | 사용 섹션 | 비고 |
|-----------|---------|------|
| `employee` | 모든 섹션 | 메인 데이터 객체 |
| `contract` | 섹션 3, 15 | 계약정보, fallback 있음 |
| `salary` | 섹션 4 | 급여정보 |
| `benefit` | 섹션 5, 17 | 복리후생, 연차 정보 |
| `insurance` | 섹션 6 | 4대보험 |
| `family_list` | 섹션 7 | 가족정보 (리스트) |
| `education_list` | 섹션 8 | 학력정보 (리스트) |
| `career_list` | 섹션 9 | 경력정보 (리스트) |
| `certificate_list` | 섹션 10 | 자격증 (리스트) |
| `language_list` | 섹션 11 | 언어능력 (리스트) |
| `military` | 섹션 12 | 병역정보 |
| `award_list` | 섹션 13 | 수상내역 (리스트) |
| `project_list` | 섹션 14 | 프로젝트 (리스트) |
| `salary_history_list` | 섹션 15 | 연봉계약 이력 (리스트) |
| `salary_payment_list` | 섹션 15 | 급여 지급 이력 (리스트) |
| `promotion_list` | 섹션 16 | 인사이동 (리스트) |
| `evaluation_list` | 섹션 16 | 인사고과 (리스트) |
| `training_list` | 섹션 16 | 교육훈련 (리스트) |
| `attendance_summary` | 섹션 17 | 근태현황 |
| `asset_list` | 섹션 17 | 비품지급 (리스트) |

**일관성 상태**: ✅ 우수
- 데이터 객체 명명이 명확하고 일관됨
- 단일 객체는 객체명, 리스트는 `*_list` 패턴

---

## 빈 데이터 처리 패턴 분석

### 필드 레벨 빈 데이터

- **패턴**: `{{ field or '정보 없음' }}` 또는 `{{ field or '-' }}`
- **일관성**: 대부분 `-` 사용, 일부 `정보 없음` 사용
- **권장**: 통일 필요 (권장: `-`)

### 테이블 빈 데이터

- **패턴**:
  ```html
  <tr>
      <td colspan="X" class="table-empty">
          <i class="fas fa-icon"></i>
          <p>등록된 X 정보가 없습니다</p>
      </td>
  </tr>
  ```
- **일관성**: ✅ 모든 테이블에서 동일한 패턴 사용

### badge 빈 데이터

- **패턴**: 조건부 표시, 값 없을 시 `-` 또는 표시 안 함
- **일관성**: ✅ badge는 값이 있을 때만 표시

**총평**: 테이블 빈 데이터 처리는 우수, 필드 레벨은 통일 필요

---

## 접근성(A11y) 분석

### 시맨틱 마크업

- ✅ `<section>`, `<table>`, `<thead>`, `<tbody>` 적절히 사용
- ✅ 헤딩 계층 구조 (section_title 매크로)
- ✅ `<label>` 대신 `.info-label` 클래스 사용 (form이 아니므로 적절)

### 아이콘 접근성

- ⚠️ `<i>` 태그 사용, `aria-label` 또는 스크린 리더 텍스트 없음
- **권장**: 아이콘에 `aria-hidden="true"` 추가, 인접 텍스트로 의미 전달

### 이미지 alt 텍스트

- ✅ 직원 사진: `alt="{{ employee.name }}"`
- ✅ 명함: `alt="명함 앞면"`, `alt="명함 뒷면"`

### 키보드 네비게이션

- ✅ `<a>`, `<button>` 태그 사용으로 기본 키보드 접근성 확보
- ⚠️ 명함 뒤집기 기능: 마우스 오버 전용, 키보드 접근 어려움

**총평**: 기본 접근성은 확보되어 있으나, 아이콘과 일부 인터랙션 개선 필요

---

## 성능 및 최적화 분석

### 템플릿 include 횟수

- `_employee_header.html`: 1회
- `_basic_info.html`: 1회
- `_history_info.html`: 1회
- `_hr_records.html`: 1회 (조건부)

**총평**: ✅ 적절한 파셜 분할, 성능 영향 최소

### 조건부 렌더링

- ✅ `{% if page_mode == 'hr_card' %}` 등 조건부 렌더링으로 불필요한 HTML 생성 방지
- ✅ 빈 데이터 시 테이블 전체 렌더링 생략 (빈 row만 표시)

### 정렬 및 필터링

- ✅ Jinja2 필터 사용: `|sort(attribute='date', reverse=True)`
- ✅ 서버 측 정렬로 클라이언트 부담 최소

**총평**: ✅ 성능 최적화 우수

---

## 종합 평가

### 강점

1. **파셜 구조 설계 우수**: 재사용성과 유연성이 뛰어난 파셜 구조
2. **필드 라벨 일관성**: 모든 템플릿에서 동일한 라벨과 순서 사용
3. **헬퍼 함수 일관성**: 함수 명명과 사용이 일관됨
4. **조건부 로직 명확**: `page_mode`와 `account_type`으로 명확한 분기
5. **스타일 클래스 통일**: 공통 클래스 패턴으로 일관된 UI
6. **빈 데이터 처리**: 테이블 빈 데이터 표시가 사용자 친화적
7. **성능 최적화**: 적절한 파셜 분할과 조건부 렌더링

### 개선 필요 사항

#### 즉시 수정 권장 (빨강)

1. **섹션 15 - 근로계약 이력**: 하드코딩 제거, 실제 데이터 반영

#### 개선 권장 (노랑)

2. **섹션 3 - 계약정보**: 근무시간/휴게시간 필드화
3. **섹션 8 - 학력정보**: 졸업유무 동적 표시
4. **섹션 9 - 경력정보**: 경력 기간 자동 계산
5. **섹션 10 - 자격증**: 구분 필드 추가

#### 선택적 개선 (초록)

6. **빈 데이터 표시 통일**: `정보 없음` vs `-` 중 하나로 통일 (권장: `-`)
7. **아이콘 접근성**: `aria-hidden="true"` 추가
8. **명함 뒤집기**: 키보드 접근성 추가
9. **fallback 로직**: 템플릿 매크로로 추출하여 가독성 향상
10. **badge 매크로**: 중복 조건 제거를 위한 badge 매크로 함수 생성

---

## 권장 작업 순서

### 1단계 (즉시)
- [ ] 섹션 15 - 근로계약 이력 하드코딩 제거

### 2단계 (단기)
- [ ] 섹션 3 - 근무시간/휴게시간 필드화
- [ ] 섹션 8 - 학력정보 졸업유무 동적 표시
- [ ] 섹션 9 - 경력정보 경력 기간 자동 계산
- [ ] 섹션 10 - 자격증 구분 필드 추가

### 3단계 (중기)
- [ ] 빈 데이터 표시 통일 (전체 템플릿)
- [ ] 아이콘 접근성 개선
- [ ] 명함 뒤집기 키보드 접근성 추가

### 4단계 (장기)
- [ ] 템플릿 매크로 추출 (fallback, badge 등)
- [ ] 공통 컴포넌트 라이브러리 구축

---

## 결론

프로필 및 인사카드 프론트엔드 템플릿은 전반적으로 우수한 일관성과 재사용성을 보이고 있습니다. 파셜 구조가 잘 설계되어 있으며, 필드 라벨과 순서가 모든 템플릿에서 일관되게 사용되고 있습니다.

주요 개선 사항은 섹션 15의 근로계약 이력 하드코딩 제거와 일부 섹션의 필드 동적화입니다. 이러한 개선을 통해 템플릿의 정확성과 유지보수성을 더욱 향상시킬 수 있습니다.

접근성과 성능 최적화도 기본적으로 잘 구현되어 있으나, 아이콘 접근성과 일부 인터랙션 개선을 통해 사용자 경험을 더욱 향상시킬 수 있습니다.

---

**분석 완료일**: 2025-12-14
**분석자**: Frontend Architect
