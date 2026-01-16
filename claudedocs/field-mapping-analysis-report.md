# 필드명 맵핑 분석 보고서

**분석일**: 2026-01-16
**분석 범위**: 모든 HR Card 섹션 (정적 8개 + 동적 14개)
**분석 대상**: 모델, 서비스, 템플릿, API 레이어 간 필드명 일관성

---

## 0. 수정 완료 요약 (2026-01-16)

### 수정 작업 완료

| 이슈 | 파일 | 수정 내용 | 상태 |
|------|------|----------|------|
| H1 | `inline_edit_service.py` | organization 화이트리스트에 `team`, `job_title`, `internal_phone`, `company_email` 추가. `duty`를 `job_title`로 변경 | **완료** |
| H2 | `inline_edit_service.py` | salary/benefit 섹션이 relation 모델(Salary, Benefit)을 직접 업데이트하도록 `_update_salary()`, `_update_benefit()`, `get_section_data()` 메서드 수정 | **완료** |
| H3 | `_basic_info.html` | 142번 줄 `duty` → `job_title` 수정 | **완료** |

### 수정된 코드 요약

**inline_edit_service.py 변경점**:
```python
# organization 화이트리스트 (수정됨)
'organization': {
    'name': '소속정보',
    'fields': [
        'organization_id', 'department', 'team', 'position', 'job_title',
        'job_grade', 'job_role', 'work_location',
        'internal_phone', 'company_email'
    ]
},

# salary 화이트리스트 (수정됨 - relation 모델 지원)
'salary': {
    'name': '급여정보',
    'model': 'Salary',  # relation 모델 사용
    'fields': [
        'salary_type', 'base_salary', 'position_allowance', ...
    ],
    'readonly_fields': ['total_salary']
},

# benefit 화이트리스트 (수정됨 - relation 모델 지원)
'benefit': {
    'name': '연차 및 복리후생',
    'model': 'Benefit',  # relation 모델 사용
    'fields': [
        'year', 'annual_leave_granted', 'annual_leave_used', ...
    ],
    'readonly_fields': ['annual_leave_remaining']
},
```

---

## 1. 분석 요약

### 1.1 레이어 구조

```
[Template] → [API/Service] → [Model]
   ↑              ↑              ↑
data-field    whitelist      DB Column
```

### 1.2 발견된 이슈 분류

| 심각도 | 건수 | 설명 |
|--------|------|------|
| Critical | 0 | 데이터 손실 가능한 불일치 (이전 세션에서 수정 완료) |
| High | 0 | ~~3건 발견~~ → **모두 수정 완료** |
| Medium | 5 | DictSerializableMixin alias로 해결됨 |
| Low | 8 | 템플릿 표시용 차이 (기능 영향 없음) |

---

## 2. 정적 섹션 분석 (8개)

### 2.1 개인 기본정보 (personal)

**상태**: 수정 완료

| 항목 | 이전 | 현재 (SSOT) | 비고 |
|------|------|------------|------|
| 한자 이름 | name_hanja | chinese_name | 수정 완료 |
| 주민등록번호 | rrn | resident_number | 수정 완료 |
| 비상연락처 | emergency_phone | emergency_contact | 수정 완료 |
| 상세주소 | address_detail | detailed_address | 수정 완료 |
| 실제 상세주소 | actual_address_detail | actual_detailed_address | 수정 완료 |

**inline_edit_service.py 화이트리스트 검증**:
```python
'personal': {
    'fields': [
        'name', 'chinese_name', 'english_name', 'foreign_name',
        'birth_date', 'lunar_birth', 'gender', 'nationality',
        'resident_number', 'postal_code',  # OK
        'phone', 'mobile_phone', 'home_phone', 'email',
        'emergency_contact', 'emergency_relation',  # OK
        'address', 'detailed_address',  # OK
        'actual_address', 'actual_detailed_address', 'actual_postal_code',  # OK
        ...
    ]
}
```

### 2.2 소속정보 (organization)

**상태**: **수정 완료** (2026-01-16)

| 템플릿 필드 | Service 화이트리스트 | Model 필드 | 상태 |
|------------|---------------------|-----------|------|
| organization_id | organization_id | organization_id | OK |
| team | team | team | **수정됨** |
| position | position | position | OK |
| job_grade | job_grade | job_grade | OK |
| job_title | job_title | job_title | **수정됨** |
| job_role | job_role | job_role | OK |
| work_location | work_location | work_location | OK |
| internal_phone | internal_phone | internal_phone | **수정됨** |
| company_email | company_email | company_email | **수정됨** |

**수정 내용**:
1. `team`, `internal_phone`, `company_email` 화이트리스트에 추가
2. 템플릿 `duty` → `job_title` 수정, 화이트리스트 `duty` → `job_title` 수정

### 2.3 계약정보 (contract)

**상태**: 일부 검토 필요

| 템플릿 필드 | Service | Model (Contract) | Employee | 상태 |
|------------|---------|-----------------|----------|------|
| hire_date | hire_date | - | hire_date | OK |
| status | - | - | status | **누락** |
| employment_type | - | - | employment_type (property) | **특수** |
| contract_type | contract_type | contract_type | - | OK |
| probation_end | probation_end | - | probation_end | OK (Date 타입) |

**이슈**:
- `status`, `employment_type` 화이트리스트에 없음
- `employment_type`은 Employee.contract.employee_type을 반환하는 property

### 2.4 급여정보 (salary)

**상태**: **수정 완료** (2026-01-16)

| 템플릿 필드 | Service 화이트리스트 | Model (Salary) | 상태 |
|------------|---------------------|---------------|------|
| salary_type | salary_type | salary_type | **수정됨** |
| base_salary | base_salary | base_salary | OK |
| position_allowance | position_allowance | position_allowance | **수정됨** |
| meal_allowance | meal_allowance | meal_allowance | **수정됨** |
| transportation_allowance | transportation_allowance | transportation_allowance | **수정됨** |
| total_salary | total_salary (readonly) | total_salary | **수정됨** |
| payment_day | payment_day | payment_day | **수정됨** |
| payment_method | payment_method | payment_method | **수정됨** |

**수정 내용**:
- `model: 'Salary'` 지정으로 relation 모델 직접 업데이트 지원
- `_update_salary()` 메서드가 Salary 모델을 직접 조회/생성/업데이트
- 금액 필드 정수 변환, readonly 필드 제외 처리

### 2.5 복리후생 (benefit)

**상태**: **수정 완료** (2026-01-16)

| 템플릿 필드 | Service 화이트리스트 | Model (Benefit) | 상태 |
|------------|---------------------|----------------|------|
| year | year | year | **수정됨** |
| annual_leave_granted | annual_leave_granted | annual_leave_granted | **수정됨** |
| annual_leave_used | annual_leave_used | annual_leave_used | **수정됨** |
| annual_leave_remaining | annual_leave_remaining (readonly) | annual_leave_remaining | **수정됨** |
| severance_type | severance_type | severance_type | **수정됨** |
| severance_method | severance_method | severance_method | **수정됨** |

**수정 내용**:
- `model: 'Benefit'` 지정으로 relation 모델 직접 업데이트 지원
- `_update_benefit()` 메서드가 Benefit 모델을 직접 조회/생성/업데이트
- 잔여 연차 자동 계산 (granted - used)

### 2.6 병역정보 (military)

**상태**: 검토 필요

| 템플릿 필드 | Service 화이트리스트 | Model (MilitaryService) | 상태 |
|------------|---------------------|------------------------|------|
| military_status | military_status | military_status | OK |
| military_branch | military_branch | branch | **불일치** |
| military_start_date | military_start_date | enlistment_date | **불일치** |
| military_end_date | military_end_date | discharge_date | **불일치** |
| military_rank | military_rank | rank | **불일치** |
| military_duty | - | service_type | **불일치** |
| military_specialty | - | specialty | **누락** |
| exemption_reason | military_exemption_reason | exemption_reason | OK (alias) |

**이슈**:
- 템플릿의 `military_*` 접두사와 MilitaryService 모델 필드명 불일치
- DictSerializableMixin의 `__dict_aliases__`로 일부 해결됨
- 템플릿에서 `military.status`, `military.branch` 형태로 접근 중

### 2.7 근태정보 (attendance)

**상태**: 정적 섹션 (읽기 전용)

### 2.8 계정정보 (account)

**상태**: OK

---

## 3. 동적 섹션 분석 (14개)

### 3.1 이력 정보 (Protected Sections)

#### 3.1.1 가족정보 (families)

| 템플릿 | Model Alias | Model Column | 상태 |
|--------|-------------|--------------|------|
| family.phone | phone | contact | alias 처리 |
| family.living_together | living_together | is_cohabitant | alias 처리 |

**상태**: DictSerializableMixin alias로 해결됨

#### 3.1.2 학력정보 (educations)

| 템플릿 | Model Alias | Model Column | 상태 |
|--------|-------------|--------------|------|
| edu.school | school | school_name | alias 처리 |
| edu.graduation_year | graduation_year | (computed) | computed 처리 |

**상태**: OK

#### 3.1.3 경력정보 (careers)

| 템플릿 | Model Alias | Model Column | 상태 |
|--------|-------------|--------------|------|
| career.company | company | company_name | alias 처리 |
| career.duty | duty | job_description | alias 처리 |

**상태**: OK

#### 3.1.4 자격증 (certificates)

| 템플릿 | Model Alias | Model Column | 상태 |
|--------|-------------|--------------|------|
| cert.name | name | certificate_name | alias 처리 |
| cert.issuer | issuer | issuing_organization | alias 처리 |
| cert.acquired_date | acquired_date | acquisition_date | alias 처리 |

**상태**: OK

#### 3.1.5 언어능력 (languages)

| 템플릿 | Model Alias | Model Column | 상태 |
|--------|-------------|--------------|------|
| lang.language | language | language_name | alias 처리 |
| lang.test_name | test_name | exam_name | alias 처리 |
| lang.acquired_date | acquired_date | acquisition_date | alias 처리 |

**상태**: OK

#### 3.1.6 수상내역 (awards)

| 템플릿 | Model Column | 상태 |
|--------|-------------|------|
| award.award_date | award_date | OK |
| award.award_name | award_name | OK |
| award.institution | institution | OK |
| award.description | (없음) | **누락** |
| award.notes | note (alias) | OK |

**이슈**: Award 모델에 `description` 필드 없음

### 3.2 HR 릴레이션 (Non-Protected Sections)

#### 3.2.1 근로계약 이력 (employment-contracts)

| 템플릿 | Model (EmploymentContract) | 상태 |
|--------|---------------------------|------|
| contract.contract_date | contract_date | OK |
| contract.contract_type | contract_type | OK |
| contract.start_date | start_date | OK |
| contract.end_date | end_date | OK |
| contract.employee_type | employee_type | OK |
| contract.work_type | work_type | OK |
| contract.note | note | OK |

**상태**: OK

#### 3.2.2 연봉계약 이력 (salary-histories)

| 템플릿 | Model (SalaryHistory) | 상태 |
|--------|----------------------|------|
| history.contract_year | contract_year | OK |
| history.annual_salary | annual_salary | OK |
| history.bonus | bonus | OK |
| history.total_amount | total_amount | OK |
| history.contract_period | contract_period | OK |

**상태**: OK

#### 3.2.3 기타 HR 섹션

| 섹션 | 모델 | 상태 |
|------|------|------|
| salary-payments | SalaryPayment | OK |
| promotions | Promotion | OK |
| evaluations | Evaluation | OK |
| trainings | Training | OK |
| hr-projects | HrProject | OK |
| assets | Asset | OK |
| projects (참여이력) | ProjectParticipation | OK |

---

## 4. 발견된 이슈 상세

### 4.1 High Priority (즉시 수정 필요)

#### H1. 소속정보 화이트리스트 누락
**위치**: `inline_edit_service.py:62-67`
**현재**:
```python
'organization': {
    'fields': [
        'organization_id', 'department', 'position', 'duty',
        'job_grade', 'job_role', 'work_location'
    ]
}
```
**수정 필요**:
```python
'organization': {
    'fields': [
        'organization_id', 'department', 'team', 'position',
        'job_grade', 'job_title', 'job_role', 'work_location',
        'internal_phone', 'company_email'
    ]
}
```

#### H2. 급여정보/복리후생 화이트리스트 문제
**위치**: `inline_edit_service.py:76-89`
**이슈**: 관계 모델(Salary, Benefit) 필드 업데이트 로직 없음
**해결책**:
1. 관계 모델 필드를 별도로 처리하거나
2. Employee 모델에 property 추가하여 프록시 처리

#### H3. 병역정보 필드명 불일치
**위치**: `_history_info.html:241-307`
**이슈**: 템플릿 `military_*` vs MilitaryService 모델 필드명
**현재 동작**: MilitaryService.`__dict_aliases__`로 일부 해결됨
**권장**: 템플릿에서 `military.` 접두사로 접근하므로 정상 동작

### 4.2 Medium Priority

#### M1. Award.description 필드 누락
**위치**: `_history_info.html:336`
**이슈**: 템플릿에서 `award.description` 사용하나 모델에 없음
**영향**: 빈 값 표시됨
**해결책**: Award 모델에 description 필드 추가 (마이그레이션 필요)

#### M2. duty vs job_title 불일치
**위치**: `_basic_info.html:142`
**현재**: `inline_row('직책', 'duty', employee.job_title, ...)`
**이슈**: 필드명 `duty`로 전송되나 모델은 `job_title`
**해결책**: 템플릿에서 `job_title` 사용으로 변경

### 4.3 Low Priority (DictSerializableMixin으로 해결됨)

- FamilyMember: phone → contact
- Education: school → school_name
- Career: company → company_name, duty → job_description
- Certificate: name → certificate_name, issuer → issuing_organization
- Language: language → language_name, test_name → exam_name
- MilitaryService: status → military_status, start_date → enlistment_date

---

## 5. 권장 조치 사항

### 5.1 즉시 조치 (High Priority)

1. **inline_edit_service.py 화이트리스트 보완**
   - organization 섹션: `team`, `job_title`, `internal_phone`, `company_email` 추가
   - salary 섹션: 관계 모델 필드 처리 로직 추가
   - benefit 섹션: 관계 모델 필드 처리 로직 추가

2. **_basic_info.html duty → job_title 수정**
   - `inline_row('직책', 'duty', ...)` → `inline_row('직책', 'job_title', ...)`

### 5.2 중기 조치 (Medium Priority)

1. **Award 모델에 description 필드 추가**
   ```python
   description = db.Column(db.Text, nullable=True)
   ```

2. **section_api.py와 inline_edit_service.py 동기화**
   - 두 파일의 섹션 설정이 분리되어 있어 유지보수 어려움
   - SSOT 원칙에 따라 하나로 통합 권장

### 5.3 장기 조치 (Low Priority)

1. **관계 모델 인라인 편집 지원**
   - Salary, Benefit, Contract, MilitaryService 모델의 인라인 편집
   - 현재는 Employee 필드만 지원

2. **필드 유효성 검사 통합**
   - 각 섹션별 필드 유효성 검사 로직 중앙화

---

## 6. 테스트 체크리스트

### 6.1 정적 섹션 인라인 편집 테스트

| 섹션 | 계정 | 테스트 항목 | 상태 |
|------|------|------------|------|
| personal | employee_sub | 이름, 연락처, 주소 수정 | 테스트 완료 |
| personal | corporate | 모든 필드 수정 | 미테스트 |
| organization | corporate | 소속, 직급 수정 | 미테스트 |
| salary | corporate | 급여 정보 수정 | 미테스트 |
| military | employee_sub | 병역 정보 수정 | 미테스트 |

### 6.2 동적 섹션 CRUD 테스트

| 섹션 | 추가 | 수정 | 삭제 | 상태 |
|------|------|------|------|------|
| families | - | - | - | 미테스트 |
| educations | - | - | - | 미테스트 |
| careers | - | - | - | 미테스트 |
| certificates | - | - | - | 미테스트 |
| languages | - | - | - | 미테스트 |
| awards | - | - | - | 미테스트 |

---

## 7. 결론

### 7.1 현재 상태

- **개인 기본정보**: 이전 세션에서 필드명 통일 완료, 정상 동작 확인
- **기타 정적 섹션**: 화이트리스트 보완 필요
- **동적 섹션**: DictSerializableMixin alias 덕분에 대부분 정상 동작

### 7.2 다음 단계

1. H1, H2, H3 이슈 수정 (즉시)
2. 수정 후 브라우저 테스트 수행
3. 나머지 섹션 인라인 편집 활성화 (Phase 2-7)

---

**작성자**: Claude Code Analysis
**버전**: 1.0
