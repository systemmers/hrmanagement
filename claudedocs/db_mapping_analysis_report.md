# DB 매핑 분석 보고서

**분석일**: 2025-12-04
**분석자**: Claude Code (DevOps Architect Mode)
**분석 범위**: 입력필드(HTML), 처리로직(helpers.py), DB모델(SQLAlchemy) 간 스키마 정합성

---

## 1. 분석 요약

| 구분 | 정상 | 불일치 | 데이터 손실 위험 | Import 오류 |
|------|------|--------|-----------------|-------------|
| 가족정보 | 2 | 4 | **HIGH** | **YES** |
| 학력정보 | 2 | 4 | **HIGH** | NO |
| 경력정보 | 1 | 5 | **HIGH** | NO |
| 자격증 | 0 | 4 | **HIGH** | NO |
| 언어능력 | 2 | 2 | MEDIUM | NO |
| 병역정보 | 2 | 2 | MEDIUM | **YES** |
| 4대보험 | 0 | 11 | **CRITICAL** | NO |
| 급여정보 | 6 | 5 | MEDIUM | NO |
| **합계** | 15 | 37 | - | 2 |

### 심각도 등급
- **CRITICAL**: 런타임 오류 발생 또는 전체 데이터 손실
- **HIGH**: 사용자 입력 데이터가 DB에 저장되지 않음
- **MEDIUM**: 일부 필드 불일치, 기능 제한적 동작
- **LOW**: 네이밍 불일치, 동작에는 영향 없음

---

## 2. CRITICAL 문제점 (즉시 수정 필요)

### 2.1 Import 오류 - helpers.py

**파일**: `app/blueprints/employees/helpers.py`

| 라인 | 현재 코드 | 올바른 코드 | 영향 |
|------|----------|------------|------|
| 187 | `from ...models import Family` | `from ...models import FamilyMember` | 가족정보 저장 시 **ImportError** 발생 |
| 322 | `from ...models import Military` | `from ...models import MilitaryService` | 병역정보 저장 시 **ImportError** 발생 |

**결과**: 직원 등록/수정 시 가족정보, 병역정보 저장 기능이 완전히 동작하지 않음

### 2.2 4대보험 정보 - 전체 미구현

**폼 필드** (11개):
- `national_pension_number`, `national_pension_date`
- `health_insurance_number`, `health_insurance_date`
- `employment_insurance_number`, `employment_insurance_date`
- `industrial_insurance_number`, `industrial_insurance_date`
- `pension_exempt`, `health_exempt`, `employment_exempt`

**DB 모델** (Insurance):
- `national_pension` (Boolean), `health_insurance` (Boolean), `employment_insurance` (Boolean), `industrial_accident` (Boolean)
- `*_rate` 필드들만 존재

**helpers.py**: 4대보험 처리 함수 **없음** (`update_insurance_data()` 미구현)

**결과**: 사용자가 입력한 4대보험 정보가 **전혀 저장되지 않음**

---

## 3. HIGH 문제점 (데이터 손실)

### 3.1 가족정보 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `family_birth[]` | `family_birth_date[]` | `birth_date` | **불일치 - 데이터 손실** |
| Template | `family_job[]` | `family_occupation[]` | `occupation` | **불일치 - 데이터 손실** |
| helpers.py | - | `phone` | `contact` | **필드명 오류** |
| helpers.py | - | `cohabiting` | `is_cohabitant` | **필드명 오류** |

**영향**: 가족 생년월일, 직업 정보가 저장되지 않음

### 3.2 학력정보 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `education_school[]` | `education_school_name[]` | `school_name` | **불일치 - 데이터 손실** |
| Template | `education_year[]` | `education_graduation_year[]` | `graduation_date` | **불일치 - 데이터 손실** |
| helpers.py | - | `gpa` | (없음) | 모델에 필드 없음 |
| helpers.py | - | `graduation_year` | `graduation_date` | 타입 불일치 |

**영향**: 학교명, 졸업년도 정보가 저장되지 않음

### 3.3 경력정보 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `career_company[]` | `career_company_name[]` | `company_name` | **불일치 - 데이터 손실** |
| Template | `career_duty[]` | `career_duties[]` | `job_description` | **불일치 - 데이터 손실** |
| Template | `career_period[]` | `career_start_date[]`, `career_end_date[]` | `start_date`, `end_date` | **구조 불일치 - 데이터 손실** |
| helpers.py | - | `duties` | `job_description` | **필드명 오류** |

**영향**: 회사명, 담당업무, 재직기간 정보가 저장되지 않음

### 3.4 자격증정보 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `cert_name[]` | `certificate_name[]` | `certificate_name` | **불일치 - 데이터 손실** |
| Template | `cert_issuer[]` | `certificate_issuer[]` | `issuing_organization` | **불일치 - 데이터 손실** |
| Template | `cert_date[]` | `certificate_date[]` | `acquisition_date` | **불일치 - 데이터 손실** |
| Template | `cert_number[]` | (없음) | `certificate_number` | **처리 누락** |

**영향**: 자격증 전체 정보가 저장되지 않음

---

## 4. MEDIUM 문제점

### 4.1 언어능력 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `language_cert[]` | `language_test_name[]`, `language_score[]` | `exam_name`, `score` | 구조 불일치 |
| Template | `language_cert_date[]` | `language_test_date[]` | `acquisition_date` | 필드명 불일치 |

### 4.2 병역정보 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `military_period` | `military_start_date`, `military_end_date` | `enlistment_date`, `discharge_date` | 구조 불일치 |
| helpers.py | - | `specialty` | (없음) | 모델에 필드 없음 |

### 4.3 급여정보 필드명 불일치

| 계층 | 폼 필드명 | helpers.py 기대값 | DB 모델 필드 | 상태 |
|------|----------|------------------|-------------|------|
| Template | `transport_allowance` | - | `transportation_allowance` | 필드명 불일치 |
| Template | `bonus_rate` | - | (없음) | 모델에 필드 없음 |
| Template | `pay_type` | - | `salary_type` | 필드명 불일치 |
| Template | `bank_name` | - | (없음) | 모델에 필드 없음 |
| Template | `account_number` | - | `bank_account` | 필드명 불일치 |

---

## 5. 수정 체크리스트

### Phase 1: CRITICAL 수정 (즉시)

- [ ] **helpers.py Import 오류 수정**
  - [ ] Line 187: `Family` -> `FamilyMember`
  - [ ] Line 322: `Military` -> `MilitaryService`

- [ ] **helpers.py 필드명 오류 수정**
  - [ ] `update_family_data()`: `phone` -> `contact`, `cohabiting` -> `is_cohabitant`
  - [ ] `update_education_data()`: `graduation_year` 저장 로직 수정 (graduation_date 형식으로)
  - [ ] `update_career_data()`: `duties` -> `job_description`

### Phase 2: HIGH 수정 (템플릿-helpers.py 동기화)

**옵션 A: 템플릿 필드명 수정** (권장)
- [ ] `_family_info.html`: `family_birth[]` -> `family_birth_date[]`, `family_job[]` -> `family_occupation[]`
- [ ] `_education_info.html`: `education_school[]` -> `education_school_name[]`, `education_year[]` -> `education_graduation_year[]`
- [ ] `_career_info.html`: `career_company[]` -> `career_company_name[]`, `career_duty[]` -> `career_duties[]`
- [ ] `_career_info.html`: `career_period[]` -> `career_start_date[]`, `career_end_date[]` (2개 필드로 분리)
- [ ] `_certificate_info.html`: `cert_name[]` -> `certificate_name[]`, `cert_issuer[]` -> `certificate_issuer[]`, `cert_date[]` -> `certificate_date[]`

**옵션 B: helpers.py에서 폴백 처리** (호환성 유지)
- [ ] `getlist('certificate_name[]') or getlist('cert_name[]')` 패턴 적용

### Phase 3: 누락 기능 구현

- [ ] **4대보험 처리 함수 구현**
  - [ ] Insurance 모델에 필드 추가: `national_pension_number`, `national_pension_date`, `health_insurance_number`, `health_insurance_date`, `employment_insurance_number`, `employment_insurance_date`, `industrial_insurance_number`, `industrial_insurance_date`, `pension_exempt`, `health_exempt`, `employment_exempt`
  - [ ] helpers.py에 `update_insurance_data()` 함수 추가
  - [ ] routes.py에서 `update_insurance_data()` 호출 추가

- [ ] **급여정보 처리 함수 구현**
  - [ ] Salary 모델에 필드 추가: `bonus_rate`, `bank_name`
  - [ ] helpers.py에 `update_salary_data()` 함수 추가

- [ ] **계약정보 처리 함수 구현**
  - [ ] Employee 모델에 필드 추가: `probation_end_date`, `resignation_date`
  - [ ] helpers.py에 `update_contract_data()` 함수 추가

### Phase 4: 템플릿 출력 필드 동기화

- [ ] `_family_info.html`: `member.birth` -> `member.birth_date`, `member.job` -> `member.occupation`
- [ ] `_education_info.html`: `edu.school` -> `edu.school_name`, `edu.year` -> `edu.graduation_year`
- [ ] `_career_info.html`: `career.company` -> `career.company_name`, `career.duty` -> `career.job_description`, `career.period` -> 계산 필드

---

## 6. 권장 수정 순서

```
1단계 (긴급): Import 오류 수정 -> 런타임 오류 해결
2단계 (높음): 템플릿 필드명 통일 -> 데이터 손실 방지
3단계 (중간): 누락 처리 함수 구현 -> 기능 완성
4단계 (낮음): 모델 필드 추가 -> 확장 기능
```

---

## 7. 영향받는 파일 목록

### 수정 필요 파일

| 파일 경로 | 수정 내용 | 우선순위 |
|----------|----------|---------|
| `app/blueprints/employees/helpers.py` | Import 수정, 필드명 수정, 함수 추가 | CRITICAL |
| `app/models/insurance.py` | 필드 추가 (11개) | HIGH |
| `app/models/salary.py` | 필드 추가 (2개) | MEDIUM |
| `app/models/employee.py` | 필드 추가 (2개) | MEDIUM |
| `app/templates/partials/employee_form/_family_info.html` | 필드명 수정 | HIGH |
| `app/templates/partials/employee_form/_education_info.html` | 필드명 수정 | HIGH |
| `app/templates/partials/employee_form/_career_info.html` | 필드명 수정, 구조 변경 | HIGH |
| `app/templates/partials/employee_form/_certificate_info.html` | 필드명 수정 | HIGH |
| `app/templates/partials/employee_form/_language_info.html` | 필드명 수정 | MEDIUM |
| `app/templates/partials/employee_form/_insurance_info.html` | 필드명 확인 | HIGH |

---

## 8. 테스트 시나리오

### 수정 후 검증 체크리스트

- [ ] 직원 신규 등록 시 모든 필드 저장 확인
- [ ] 직원 수정 시 기존 데이터 로드 확인
- [ ] 직원 수정 시 변경사항 저장 확인
- [ ] 동적 폼(가족, 학력, 경력 등) 추가/삭제 동작 확인
- [ ] 4대보험 정보 저장/조회 확인
- [ ] 급여정보 저장/조회 확인

---

## 9. 결론

현재 HR Management 시스템의 **폼 입력 -> 처리 로직 -> DB 저장** 파이프라인에 심각한 불일치가 존재합니다.

**가장 시급한 문제**:
1. `helpers.py`의 Import 오류로 가족정보, 병역정보 저장 기능이 **완전히 동작하지 않음**
2. 템플릿-helpers.py 간 필드명 불일치로 학력, 경력, 자격증 정보가 **저장되지 않음**
3. 4대보험 처리 로직 미구현으로 관련 정보가 **전혀 저장되지 않음**

즉시 Phase 1, 2 수정을 권장합니다.
