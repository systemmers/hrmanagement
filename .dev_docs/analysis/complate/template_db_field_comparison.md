# Template vs DB Schema Field Comparison Analysis

## 분석 개요

- **분석일**: 2025-12-16
- **분석 대상**: `app/templates/` 템플릿 파일 vs `db_schema.md` DB 스키마
- **분석 목적**: 템플릿 필드명과 DB 컬럼명 불일치 식별

---

## 1. 필드명 불일치 현황

### 1.1 camelCase vs snake_case 불일치

| 템플릿 필드 | DB 컬럼 | 파일 위치 | 상태 |
|-------------|---------|-----------|------|
| `hireDate` | `hire_date` | `_contract_info.html:11` | 백엔드 매핑 존재 |
| `name_en` | `english_name` | `_personal_info.html:139` | 백엔드 매핑 존재 |
| `rrn` | `resident_number` | `_personal_info.html:219` | 백엔드 매핑 존재 |

**분석 결과**: `form_extractors.py`에서 양방향 매핑 처리됨
```python
# form_extractors.py:23
hire_date=form_data.get('hire_date') or form_data.get('hireDate', ''),
# form_extractors.py:36
english_name=form_data.get('english_name') or form_data.get('name_en') or None,
# form_extractors.py:42
resident_number=form_data.get('resident_number') or form_data.get('rrn') or None,
```

---

### 1.2 필드명 완전 불일치 (DB에 없는 필드)

#### Priority 1: 즉시 확인 필요

| 템플릿 필드 | 예상 DB 컬럼 | 파일 위치 | 상태 |
|-------------|--------------|-----------|------|
| `employment_type` | `employee_type` (contracts) | `_contract_info.html:26` | 불일치 |
| `probation_end` | 없음 | `_contract_info.html:44` | DB 컬럼 누락 |
| `resignation_date` | 없음 | `_contract_info.html:50` | DB 컬럼 누락 |
| `transport_allowance` | `transportation_allowance` | `_salary_info.html:66` | 불일치 |
| `bonus_rate` | 없음 | `_salary_info.html:73` | DB 컬럼 누락 |
| `pay_type` | `salary_type` | `_salary_info.html:80` | 불일치 |
| `bank_name` | 없음 (bank_account에 통합) | `_salary_info.html:91` | DB 구조 다름 |
| `account_number` | `bank_account` | `_salary_info.html:101` | 불일치 |
| `education_graduation_year[]` | `graduation_date` | `_education_info.html:45` | 타입 불일치 |
| `career_duties[]` | `job_description` | `_career_info.html:39` | 불일치 |

---

### 1.3 DB에 있지만 템플릿에서 미사용

#### employees 테이블

| DB 컬럼 | 설명 | 우선순위 |
|---------|------|----------|
| `chinese_name` | 한자명 | Low |
| `lunar_birth` | 음력 생일 여부 | Low |
| `nationality` | 국적 | Low |

#### contracts 테이블

| DB 컬럼 | 설명 | 우선순위 |
|---------|------|----------|
| `contract_date` | 계약일 | Medium |
| `work_type` | 근무 형태 | Medium |
| `note` | 비고 | Low |

#### salaries 테이블

| DB 컬럼 | 설명 | 우선순위 |
|---------|------|----------|
| `payment_day` | 지급일 (Default 25) | Low |
| `payment_method` | 지급방법 | Low |
| `monthly_salary` | 월급여 (계산) | Low |
| `total_salary` | 총급여 (계산) | Low |

---

## 2. 상세 분석

### 2.1 계약정보 섹션 (`_contract_info.html`)

```
템플릿 구조:
├── hireDate (입사일) → hire_date ✓ 매핑됨
├── status (재직상태) → status ✓ 일치
├── employment_type (고용형태) → employee_type? ⚠️ 불일치
├── contract_period (계약기간) → contract_period ✓ 일치
├── probation_end (수습종료일) → ❌ DB 없음
└── resignation_date (퇴사일) → ❌ DB 없음
```

**권장 조치**:
1. `employment_type` → `employee_type` 매핑 추가 필요
2. `probation_end`, `resignation_date` 컬럼 추가 검토 또는 템플릿에서 제거

### 2.2 급여정보 섹션 (`_salary_info.html`)

```
템플릿 구조:
├── base_salary → base_salary ✓ 일치
├── position_allowance → position_allowance ✓ 일치
├── meal_allowance → meal_allowance ✓ 일치
├── transport_allowance → transportation_allowance ⚠️ 불일치
├── bonus_rate → ❌ DB 없음
├── pay_type → salary_type ⚠️ 불일치
├── bank_name → ❌ DB 없음 (bank_account에 포함?)
├── account_number → bank_account ⚠️ 불일치
└── 포괄임금 필드들 → ✓ 일치
```

**권장 조치**:
1. `transport_allowance` → `transportation_allowance` 통일
2. `pay_type` → `salary_type` 통일
3. `bank_name` + `account_number` → `bank_account` 저장 로직 확인
4. `bonus_rate` 컬럼 추가 또는 계산 로직 확인

### 2.3 학력정보 섹션 (`_education_info.html`)

```
템플릿 필드:
├── education_school_name[] → school_name ✓ 일치
├── education_degree[] → degree ✓ 일치
├── education_major[] → major ✓ 일치
├── education_graduation_year[] → graduation_date ⚠️ 타입 불일치
├── education_gpa[] → gpa ✓ 일치
├── education_graduation_status[] → graduation_status ✓ 일치
└── education_note[] → note ✓ 일치
```

**권장 조치**:
- `graduation_year` (연도만) vs `graduation_date` (날짜) 통일 필요
- 템플릿에서 `value="{{ edu.graduation_year }}"` 사용 중이나 DB는 `graduation_date`

### 2.4 경력정보 섹션 (`_career_info.html`)

```
템플릿 필드:
├── career_company_name[] → company_name ✓ 일치
├── career_department[] → department ✓ 일치
├── career_position[] → position ✓ 일치
├── career_duties[] → job_description ⚠️ 불일치
├── career_salary[] → salary ✓ 일치
├── career_start_date[] → start_date ✓ 일치
└── career_end_date[] → end_date ✓ 일치
```

**권장 조치**:
- `career_duties` → `job_description` 매핑 추가 필요

---

## 3. 백엔드 매핑 현황 (form_extractors.py)

### 현재 처리되는 매핑

```python
# 처리됨 ✓
'hire_date' or 'hireDate'
'english_name' or 'name_en'
'resident_number' or 'rrn'
```

### 누락된 매핑 (추가 필요)

```python
# 추가 필요 ⚠️
'employee_type' or 'employment_type'  # contracts
'salary_type' or 'pay_type'           # salaries
'transportation_allowance' or 'transport_allowance'  # salaries
'job_description' or 'career_duties'  # careers
'bank_account' or 'account_number'    # salaries
```

---

## 4. 권장 조치 요약

### 우선순위 High (즉시 수정)

| 항목 | 현재 | 권장 | 영향 범위 |
|------|------|------|-----------|
| 고용형태 필드 | `employment_type` | `employee_type` | 계약정보 저장 |
| 교통비 필드 | `transport_allowance` | `transportation_allowance` | 급여정보 저장 |
| 급여방식 필드 | `pay_type` | `salary_type` | 급여정보 저장 |
| 담당업무 필드 | `career_duties` | `job_description` | 경력정보 저장 |

### 우선순위 Medium (검토 필요)

| 항목 | 현재 상태 | 권장 조치 |
|------|-----------|-----------|
| 수습종료일 | 템플릿에만 존재 | DB 컬럼 추가 또는 템플릿 제거 |
| 퇴사일 | 템플릿에만 존재 | DB 컬럼 추가 또는 템플릿 제거 |
| 상여금률 | 템플릿에만 존재 | DB 컬럼 추가 또는 계산 로직 |
| 은행명/계좌 | 분리된 구조 | 저장 로직 확인 |
| 졸업년도 | year vs date | 데이터 타입 통일 |

### 우선순위 Low (향후 개선)

| 항목 | 설명 |
|------|------|
| 한자명 | DB에 있으나 템플릿 미사용 |
| 음력 생일 | DB에 있으나 템플릿 미사용 |
| 국적 | DB에 있으나 템플릿 미사용 |

---

## 5. 검증 방법

### 테스트 시나리오

1. **계약정보 저장 테스트**
   - 고용형태 선택 후 저장 → DB `contracts.employee_type` 확인

2. **급여정보 저장 테스트**
   - 교통비, 급여방식 입력 후 저장 → DB 값 확인

3. **경력정보 저장 테스트**
   - 담당업무 입력 후 저장 → DB `careers.job_description` 확인

### 검증 쿼리

```sql
-- 계약정보 확인
SELECT id, employee_type, contract_period FROM contracts WHERE employee_id = ?;

-- 급여정보 확인
SELECT id, transportation_allowance, salary_type, bank_account FROM salaries WHERE employee_id = ?;

-- 경력정보 확인
SELECT id, job_description FROM careers WHERE employee_id = ?;
```

---

## 6. 결론

### 요약

- **총 불일치 항목**: 10개
- **백엔드 매핑 필요**: 5개
- **DB 스키마 변경 검토**: 3개
- **데이터 타입 불일치**: 1개
- **미사용 DB 컬럼**: 6개

### 다음 단계

1. `form_extractors.py`에 누락된 필드 매핑 추가
2. `mutation_routes.py`에서 관련 데이터 저장 로직 확인
3. DB 스키마 변경이 필요한 경우 마이그레이션 계획 수립
4. 테스트 데이터로 실제 저장/조회 동작 검증
