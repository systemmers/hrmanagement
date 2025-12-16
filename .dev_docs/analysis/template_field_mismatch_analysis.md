# 템플릿 필드명 vs DB 스키마 불일치 분석

**분석일**: 2025-12-16
**목적**: HTML 템플릿의 필드명과 DB 컬럼명 간 불일치 식별 및 우선순위별 정리

---

## 분석 개요

템플릿에서 사용되는 필드명과 DB 스키마의 컬럼명을 비교하여 불일치를 식별했습니다.
주요 문제는 snake_case(DB) vs camelCase(템플릿) 명명 규칙 불일치입니다.

### 검토 대상
- `app/templates/employees/list.html`
- `app/templates/profile/edit.html`
- `app/templates/partials/employee_form/*.html` (12개 섹션)

---

## 우선순위별 불일치 항목

### 🔴 Priority 1: 핵심 기능 영향 (즉시 수정 필요)

#### 1. 직원 목록 조회 (employees/list.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `employee.hire_date` | `hire_date` | ✅ 일치 | - |
| `employee.contract_status` | (계산 필드) | 추가 필드 | 높음 - 계약 상태 표시 |
| `employee.user_id` | (관계 필드) | 추가 필드 | 높음 - 계약 요청 |

**이슈**:
- `contract_status`는 DB 컬럼이 아닌 Python 백엔드에서 계산되어야 하는 필드
- `PersonCorporateContract` 모델과의 조인 필요

#### 2. 개인 기본정보 (_personal_info.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `name_en` | `english_name` | **camelCase vs snake_case** | **높음** |
| `birth_date` | `birth_date` | ✅ 일치 | - |
| `rrn` | `resident_number` | **약어 vs 전체명** | **높음** |
| `phone` | `mobile_phone` | **필드명 불일치** | **중간** |

**이슈**:
- `name_en` → `english_name`: 템플릿과 DB 불일치
- `rrn` → `resident_number`: 약어 사용으로 혼란
- `phone` vs `mobile_phone`: employees 테이블에는 `phone` 컬럼 존재하지만 `mobile_phone`도 존재

#### 3. 조직 정보 (_organization_info.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `employee_number` | `employee_number` | ✅ 일치 | - |
| `organization_id` | `organization_id` | ✅ 일치 | - |
| `internal_phone` | `internal_phone` | ✅ 일치 | - |

**이슈**: 없음

#### 4. 계약 정보 (_contract_info.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `hireDate` | `hire_date` | **camelCase vs snake_case** | **높음** |
| `status` | `status` | ✅ 일치 | - |
| `employment_type` | (없음 - contracts 테이블: `employee_type`) | **필드명 불일치** | **높음** |
| `contract_period` | `contract_period` (contracts) | ✅ 일치 | - |
| `probation_end` | (없음) | **누락된 필드** | 중간 |
| `resignation_date` | (없음) | **누락된 필드** | 중간 |

**이슈**:
- `hireDate` → `hire_date`: camelCase 사용으로 백엔드 처리 필요
- `employment_type`: employees 테이블에는 없고 contracts 테이블에는 `employee_type`으로 존재
- `probation_end`, `resignation_date`: DB 스키마에 없는 필드

---

### 🟡 Priority 2: 데이터 처리 영향 (중기 수정 필요)

#### 5. 급여 정보 (_salary_info.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `base_salary` | `base_salary` | ✅ 일치 | - |
| `position_allowance` | `position_allowance` | ✅ 일치 | - |
| `meal_allowance` | `meal_allowance` | ✅ 일치 | - |
| `transport_allowance` | `transportation_allowance` | **필드명 불일치** | **중간** |
| `bonus_rate` | (없음) | **누락된 필드** | 중간 |
| `pay_type` | `salary_type` | **필드명 불일치** | 중간 |
| `bank_name` | (없음) | **누락된 필드** | 중간 |
| `account_number` | `bank_account` | **필드명 불일치** | 중간 |
| `annual_salary` | `annual_salary` | ✅ 일치 | - |
| `hourly_wage` | `hourly_wage` | ✅ 일치 | - |

**이슈**:
- `transport_allowance` → `transportation_allowance`: 불일치
- `pay_type` → `salary_type`: 필드명 다름
- `bank_name`: DB에 없음, `bank_account`가 통합 필드인지 확인 필요
- `account_number` → `bank_account`: 통합 여부 확인 필요
- `bonus_rate`: DB 스키마에 없는 필드

#### 6. 학력 정보 (_education_info.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `education_school_name[]` | `school_name` | ✅ 일치 | - |
| `education_degree[]` | `degree` | ✅ 일치 | - |
| `education_major[]` | `major` | ✅ 일치 | - |
| `education_graduation_year[]` | (없음) | **누락된 필드** | 중간 |
| `education_gpa[]` | `gpa` | ✅ 일치 | - |
| `education_graduation_status[]` | `graduation_status` | ✅ 일치 | - |
| `education_note[]` | `note` | ✅ 일치 | - |

**이슈**:
- `graduation_year`: DB에는 `graduation_date` (String(20)) 존재
- 템플릿에서 `graduation_year` 사용하지만 DB는 전체 날짜 저장
- `admission_date` (DB 컬럼)는 템플릿에서 사용 안 함

#### 7. 경력 정보 (_career_info.html)

| 템플릿 필드명 | DB 컬럼명 | 불일치 유형 | 영향도 |
|--------------|-----------|------------|-------|
| `career_company_name[]` | `company_name` | ✅ 일치 | - |
| `career_department[]` | `department` | ✅ 일치 | - |
| `career_position[]` | `position` | ✅ 일치 | - |
| `career_duties[]` | `job_description` | **필드명 불일치** | 중간 |
| `career_salary[]` | `salary` | ✅ 일치 | - |
| `career_start_date[]` | `start_date` | ✅ 일치 | - |
| `career_end_date[]` | `end_date` | ✅ 일치 | - |

**이슈**:
- `career_duties` → `job_description`: 필드명 불일치
- `resignation_reason` (DB): 템플릿에서 사용 안 함
- `is_current` (DB): 템플릿에서 사용 안 함

---

### 🟢 Priority 3: 선택 필드 (장기 개선 항목)

#### 8. 누락된 DB 컬럼들 (템플릿에서 미사용)

**employees 테이블**:
- `chinese_name` (한자명)
- `lunar_birth` (음력 여부)
- `home_phone` (자택전화)
- `nationality` (국적)

**contracts 테이블 (1:1)**:
- `contract_date` (계약일)
- `contract_type` (계약 유형)
- `work_type` (근무 형태)
- `note` (비고)

**salaries 테이블 (1:1)**:
- `payment_day` (지급일)
- `payment_method` (지급방법)
- `monthly_salary` (월급여)

---

## 명명 규칙 불일치 패턴

### camelCase vs snake_case 불일치

| 템플릿 (camelCase) | DB (snake_case) | 섹션 |
|-------------------|----------------|------|
| `hireDate` | `hire_date` | 계약정보 |
| `name_en` | `english_name` | 개인정보 |

### 필드명 의미 불일치

| 템플릿 | DB | 섹션 |
|-------|-----|------|
| `phone` | `mobile_phone` | 개인정보 |
| `rrn` | `resident_number` | 개인정보 |
| `pay_type` | `salary_type` | 급여정보 |
| `transport_allowance` | `transportation_allowance` | 급여정보 |
| `account_number` | `bank_account` | 급여정보 |
| `employment_type` | `employee_type` (contracts) | 계약정보 |
| `career_duties` | `job_description` | 경력정보 |

### DB에 없는 필드 (추가 필요)

| 템플릿 필드 | 섹션 | 용도 |
|-----------|------|-----|
| `contract_status` | 직원목록 | 계약 상태 (계산 필드) |
| `bonus_rate` | 급여정보 | 상여금률 |
| `bank_name` | 급여정보 | 은행명 |
| `probation_end` | 계약정보 | 수습종료일 |
| `resignation_date` | 계약정보 | 퇴사일 |
| `education_graduation_year` | 학력정보 | 졸업년도 (vs graduation_date) |

---

## 권장 조치사항

### 즉시 조치 (Priority 1)

1. **백엔드 필드명 매핑 강화**
   - `employees/mutation_routes.py`의 `form_extractors.py`에서 필드명 매핑 명확화
   - camelCase → snake_case 자동 변환 로직 검증

2. **계약 상태 로직 검증**
   - `contract_status` 계산 로직이 Service Layer에 존재하는지 확인
   - `PersonCorporateContract`와의 조인 쿼리 최적화

3. **핵심 필드 불일치 수정**
   ```python
   # 템플릿에서 사용하는 필드명 통일
   'name_en' → 백엔드에서 'english_name'으로 매핑
   'rrn' → 백엔드에서 'resident_number'로 매핑
   'hireDate' → 백엔드에서 'hire_date'로 매핑
   ```

### 중기 조치 (Priority 2)

4. **급여 필드 정규화**
   - `transport_allowance` vs `transportation_allowance` 통일
   - `pay_type` vs `salary_type` 통일
   - `bank_name`, `account_number` vs `bank_account` 구조 재검토

5. **학력/경력 필드 정리**
   - `graduation_year` vs `graduation_date` 사용 기준 명확화
   - `career_duties` vs `job_description` 통일

### 장기 조치 (Priority 3)

6. **미사용 DB 컬럼 활용 검토**
   - `chinese_name`, `lunar_birth`, `nationality` 등 필요 여부 판단
   - 불필요 시 스키마에서 제거 고려

7. **DB 스키마 확장**
   - `probation_end`, `resignation_date` 추가 검토
   - `bonus_rate`, `bank_name` 추가 검토

---

## 영향도 분석

### 높음
- **계약 정보**: `hireDate`, `employment_type`, `probation_end`, `resignation_date`
- **개인 정보**: `name_en`, `rrn`, `phone`
- **계약 상태**: `contract_status` (계산 필드)

### 중간
- **급여 정보**: `transport_allowance`, `pay_type`, `bank_name`, `account_number`, `bonus_rate`
- **학력 정보**: `graduation_year`
- **경력 정보**: `career_duties`

### 낮음
- 미사용 DB 컬럼들 (선택 필드)

---

## 테스트 체크리스트

### 필수 테스트

- [ ] 직원 등록 시 모든 필드가 올바르게 DB에 저장되는가?
- [ ] 직원 수정 시 필드 매핑이 정확한가?
- [ ] 계약 상태가 올바르게 표시되는가?
- [ ] camelCase 필드가 백엔드에서 snake_case로 변환되는가?

### 권장 테스트

- [ ] 급여 정보 저장/조회 시 필드명 불일치로 인한 오류 없는가?
- [ ] 학력/경력 동적 폼 저장 시 필드명 매핑이 정확한가?
- [ ] 누락된 필드(probation_end 등)가 제출 시 무시되는가?

---

## 결론

1. **주요 문제**: camelCase vs snake_case 불일치가 가장 큰 이슈
2. **백엔드 매핑 로직**: `form_extractors.py` 또는 Service Layer에서 필드명 변환이 필수
3. **DB 스키마 확장 검토**: 템플릿에만 존재하는 필드들의 DB 추가 필요성 판단
4. **우선순위**: 계약 정보 > 개인 정보 > 급여 정보 순으로 수정

**다음 단계**: 백엔드 코드(`form_extractors.py`, `employee_service.py`) 분석하여 실제 매핑 로직 검증
