# 프로필/인사카드 백엔드 분석 보고서

**작성일**: 2025-12-14
**분석 대상**: 3가지 계정 유형별 프로필/인사카드 라우트 및 서비스 레이어

## 1. 개요

프로필 및 인사카드 페이지의 백엔드 데이터 전달 패턴을 분석하여 3가지 계정 유형 간 일관성을 검토합니다.

### 계정 유형

1. **법인 직원** (corporate employee)
   - 통합 프로필: `profile_bp` → `profile/routes.py`
   - 인사카드: `mypage_bp` → `mypage.py`

2. **법인 관리자** (corporate_admin)
   - 프로필: `profile_bp` → `profile/routes.py`

3. **개인 계정** (personal)
   - 프로필: `profile_bp` → `profile/routes.py` (통합)
   - 인사카드: `personal_bp` → `personal.py`

## 2. 라우트별 데이터 전달 패턴 분석

### 2.1 법인 직원 - 통합 프로필 조회 (`profile.view`)

**파일**: `app/blueprints/profile/routes.py`
**라인**: 18-46

**템플릿 컨텍스트**:
```python
context = adapter.to_template_context(variable_name='employee')

# 어댑터에서 추가
context['family_list'] = adapter.get_family_list()
context['project_list'] = adapter.get_project_list()
context['award_list'] = adapter.get_award_list()
context['sections'] = adapter.get_available_sections()
context['page_mode'] = 'profile'

# 템플릿: profile/detail.html
```

**전달 변수**:
- `employee`: 프로필 기본 객체
- `is_corporate`: True
- `account_type`: 'corporate'
- `available_sections`: 섹션 목록
- `basic_info`: 기본정보 dict
- `organization_info`: 소속정보 dict
- `education_list`: 학력 목록
- `career_list`: 경력 목록
- `certificate_list`: 자격증 목록
- `language_list`: 어학 목록
- `military_info`: 병역 정보
- `contract_info`: 계약정보 dict
- `salary_info`: 급여정보 dict
- `benefit_info`: 복리후생 dict
- `insurance_info`: 4대보험 dict
- `family_list`: 가족 목록
- `project_list`: 프로젝트 목록
- `award_list`: 수상 목록
- `sections`: 사용가능 섹션 목록
- `page_mode`: 'profile'

---

### 2.2 법인 직원 - 인사카드 (`mypage.company_info`)

**파일**: `app/blueprints/mypage.py`
**라인**: 23-109

**템플릿 컨텍스트**:
```python
render_template('mypage/company_info.html',
    employee=employee,
    company_info=company_data,
    salary=salary,
    benefit=benefit,
    contract=contract,
    insurance=insurance,
    salary_history_list=salary_history_list,
    salary_payment_list=salary_payment_list,
    promotion_list=promotion_list,
    evaluation_list=evaluation_list,
    training_list=training_list,
    attendance_summary=attendance_summary,
    asset_list=asset_list,
    education_list=education_list,
    career_list=career_list,
    certificate_list=certificate_list,
    family_list=family_list,
    language_list=language_list,
    military=military,
    project_list=project_list,
    award_list=award_list,
    is_readonly=True,
    page_mode='hr_card'
)
```

**전달 변수**:
- `employee`: Employee 모델 객체
- `company_info`: 회사정보 dict (SystemSetting 조회)
- `salary`: Salary 모델 객체
- `benefit`: Benefit 모델 객체
- `contract`: Contract 모델 객체
- `insurance`: Insurance 모델 객체
- `salary_history_list`: 급여이력 목록
- `salary_payment_list`: 급여지급 목록
- `promotion_list`: 승진 목록
- `evaluation_list`: 평가 목록
- `training_list`: 교육 목록
- `attendance_summary`: 근태 요약
- `asset_list`: 비품 목록
- `education_list`: 학력 목록
- `career_list`: 경력 목록
- `certificate_list`: 자격증 목록
- `family_list`: 가족 목록
- `language_list`: 어학 목록
- `military`: Military 모델 객체
- `project_list`: 프로젝트 목록
- `award_list`: 수상 목록
- `is_readonly`: True
- `page_mode`: 'hr_card'

---

### 2.3 법인 관리자 - 프로필 조회 (`profile.view`)

**파일**: `app/blueprints/profile/routes.py`
**라인**: 18-46 (동일한 라우트)

**템플릿 컨텍스트**:
```python
context = adapter.to_template_context(variable_name='employee')

# CorporateAdminProfileAdapter는 법인 전용 필드 미제공
context['sections'] = adapter.get_available_sections()
context['page_mode'] = 'profile'

# 템플릿: profile/detail.html
```

**전달 변수**:
- `employee`: 프로필 기본 객체
- `is_corporate`: True
- `account_type`: 'corporate_admin'
- `available_sections`: ['basic', 'company_info']
- `basic_info`: 기본정보 dict (제한된 필드)
- `organization_info`: 회사정보 dict
- `education_list`: []
- `career_list`: []
- `certificate_list`: []
- `language_list`: []
- `military_info`: None
- `contract_info`: None
- `salary_info`: None
- `benefit_info`: None
- `insurance_info`: None
- `sections`: ['basic', 'company_info']
- `page_mode`: 'profile'

---

### 2.4 개인 계정 - 프로필 조회 (`profile.view`)

**파일**: `app/blueprints/profile/routes.py`
**라인**: 18-46 (동일한 라우트)

**템플릿 컨텍스트**:
```python
context = adapter.to_template_context(variable_name='employee')

# PersonalProfileAdapter는 법인 전용 필드 미제공
context['sections'] = adapter.get_available_sections()
context['page_mode'] = 'profile'

# 템플릿: profile/detail.html
```

**전달 변수**:
- `employee`: 프로필 기본 객체
- `is_corporate`: False
- `account_type`: 'personal'
- `available_sections`: ['basic', 'education', 'career', 'certificate', 'language', 'military', 'award']
- `basic_info`: 기본정보 dict
- `organization_info`: None
- `education_list`: 학력 목록
- `career_list`: 경력 목록
- `certificate_list`: 자격증 목록
- `language_list`: 어학 목록
- `military_info`: 병역 정보
- `contract_info`: None
- `salary_info`: None
- `benefit_info`: None
- `insurance_info`: None
- `sections`: ['basic', 'education', 'career', 'certificate', 'language', 'military', 'award']
- `page_mode`: 'profile'

---

### 2.5 개인 계정 - 회사 인사카드 (`personal.company_card_detail`)

**파일**: `app/blueprints/personal.py`
**라인**: 412-456

**템플릿 컨텍스트**:
```python
render_template('personal/company_card_detail.html',
    contract=card_data['contract'],
    company=card_data['company'],
    employee=card_data.get('employee'),
    contract_info=card_data.get('contract_info'),
    salary=card_data.get('salary'),
    benefit=card_data.get('benefit'),
    insurance=card_data.get('insurance'),
    education_list=card_data.get('education_list', []),
    career_list=card_data.get('career_list', []),
    certificate_list=card_data.get('certificate_list', []),
    language_list=card_data.get('language_list', []),
    military=card_data.get('military'),
    award_list=card_data.get('award_list', []),
    family_list=card_data.get('family_list', []),
    salary_history_list=card_data.get('salary_history_list', []),
    salary_payment_list=card_data.get('salary_payment_list', []),
    promotion_list=card_data.get('promotion_list', []),
    evaluation_list=card_data.get('evaluation_list', []),
    training_list=card_data.get('training_list', []),
    attendance_summary=card_data.get('attendance_summary'),
    asset_list=card_data.get('asset_list', []),
    page_mode='hr_card'
)
```

**전달 변수**:
- `contract`: PersonCorporateContract 계약정보
- `company`: Company 회사정보
- `employee`: 개인 프로필 기반 employee 데이터 dict
- `contract_info`: 계약정보 dict
- `salary`: None (현재 미구현)
- `benefit`: None (현재 미구현)
- `insurance`: None (현재 미구현)
- `education_list`: 학력 목록
- `career_list`: 경력 목록
- `certificate_list`: 자격증 목록
- `language_list`: 어학 목록
- `military`: 병역 정보
- `award_list`: 수상 목록
- `family_list`: 가족 목록
- `salary_history_list`: []
- `salary_payment_list`: []
- `promotion_list`: []
- `evaluation_list`: []
- `training_list`: []
- `attendance_summary`: None
- `asset_list`: []
- `page_mode`: 'hr_card'

---

## 3. 필드 네이밍 및 구조 비교

### 3.1 프로필 페이지 (`page_mode='profile'`)

| 필드명 | 법인 직원 | 법인 관리자 | 개인 계정 | 데이터 타입 |
|--------|----------|------------|----------|------------|
| `employee` | ProfileContext 객체 | ProfileContext 객체 | ProfileContext 객체 | 통합 객체 |
| `is_corporate` | True | True | False | Boolean |
| `account_type` | 'corporate' | 'corporate_admin' | 'personal' | String |
| `basic_info` | Dict (전체 필드) | Dict (제한 필드) | Dict (전체 필드) | Dict |
| `organization_info` | Dict | Dict (회사정보) | None | Dict/None |
| `education_list` | List[Dict] | [] | List[Dict] | List |
| `career_list` | List[Dict] | [] | List[Dict] | List |
| `certificate_list` | List[Dict] | [] | List[Dict] | List |
| `language_list` | List[Dict] | [] | List[Dict] | List |
| `military_info` | Dict/None | None | Dict/None | Dict/None |
| `contract_info` | Dict/None | None | None | Dict/None |
| `salary_info` | Dict/None | None | None | Dict/None |
| `benefit_info` | Dict/None | None | None | Dict/None |
| `insurance_info` | Dict/None | None | None | Dict/None |
| `family_list` | List[Dict] | - | - | List |
| `project_list` | List[Dict] | - | - | List |
| `award_list` | List[Dict] | - | List[Dict] | List |
| `sections` | List[String] | List[String] | List[String] | List |
| `page_mode` | 'profile' | 'profile' | 'profile' | String |

**일관성 분석**:
- 통합 프로필은 `to_template_context()` 메서드로 일관성 확보
- `employee` 변수명 통일 (기존 파셜 호환성)
- 어댑터 패턴으로 타입별 차이 추상화
- 필드 네이밍 및 타입 일관성 유지

---

### 3.2 인사카드 페이지 (`page_mode='hr_card'`)

| 필드명 | 법인 직원 | 개인 계정 | 일치 여부 |
|--------|----------|----------|----------|
| `employee` | Employee 모델 객체 | Dict (개인 프로필 기반) | 불일치 (타입) |
| `company_info` | Dict | - | - |
| `company` | - | Company 객체 | 네이밍 불일치 |
| `contract` | Contract 객체 | PersonCorporateContract 객체 | 타입 불일치 |
| `contract_info` | - | Dict | - |
| `salary` | Salary 객체 | None | 일치 (None 허용) |
| `benefit` | Benefit 객체 | None | 일치 (None 허용) |
| `insurance` | Insurance 객체 | None | 일치 (None 허용) |
| `education_list` | List | List | 일치 |
| `career_list` | List | List | 일치 |
| `certificate_list` | List | List | 일치 |
| `language_list` | List | List | 일치 |
| `military` | Military 객체 | Dict | 타입 불일치 |
| `family_list` | List | List | 일치 |
| `project_list` | List | - | - |
| `award_list` | List | List | 일치 |
| `salary_history_list` | List | [] | 일치 (빈 배열) |
| `salary_payment_list` | List | [] | 일치 (빈 배열) |
| `promotion_list` | List | [] | 일치 (빈 배열) |
| `evaluation_list` | List | [] | 일치 (빈 배열) |
| `training_list` | List | [] | 일치 (빈 배열) |
| `attendance_summary` | Object/None | None | 일치 (None 허용) |
| `asset_list` | List | [] | 일치 (빈 배열) |
| `is_readonly` | True | - | 필드 누락 |
| `page_mode` | 'hr_card' | 'hr_card' | 일치 |

**불일치 항목**:

1. **회사 정보 필드**:
   - 법인 직원: `company_info` (Dict)
   - 개인 계정: `company` (Company 객체)
   - 네이밍 및 타입 불일치

2. **employee 필드**:
   - 법인 직원: Employee 모델 객체
   - 개인 계정: Dict (개인 프로필 기반 가공 데이터)
   - 타입 불일치 (객체 vs Dict)

3. **military 필드**:
   - 법인 직원: Military 모델 객체
   - 개인 계정: Dict (to_dict() 결과)
   - 타입 불일치

4. **is_readonly 필드**:
   - 법인 직원: True
   - 개인 계정: 누락
   - 개인 계정 템플릿에 필요시 추가 필요

5. **contract_info 필드**:
   - 법인 직원: 없음
   - 개인 계정: Dict (계약정보 별도 제공)
   - 필드 추가 제공 (중복 가능성)

---

## 4. 서비스 레이어 데이터 반환 패턴

### 4.1 EmployeeService (법인 직원)

**파일**: `app/services/employee_service.py`

**데이터 접근 방식**:
- Repository 패턴 사용
- Employee 모델 객체 직접 반환
- 관계형 데이터는 ORM relationships 사용
- 템플릿에서 `.to_dict()` 호출 필요

**특징**:
- 멀티테넌시 접근 제어 (`verify_access`)
- CRUD 메서드 표준화
- 폼 데이터 → 모델 변환 메서드 (`_extract_employee_from_form`)
- 관계형 데이터 일괄/개별 업데이트 지원

---

### 4.2 PersonalService (개인 계정)

**파일**: `app/services/personal_service.py`

**데이터 접근 방식**:
- Repository 패턴 사용
- PersonalProfile 모델 객체 반환
- 인사카드용 데이터는 `get_company_card_data()`에서 Dict 가공 후 반환

**인사카드 데이터 구성** (`get_company_card_data`):
```python
# 라인 271-421
card_data = {
    'employee': employee_data,  # Dict (가공된 데이터)
    'contract': {...},          # Dict
    'company': {...},           # Dict
    'contract_info': {...},     # Dict
    'education_list': [...],    # List[Dict]
    'career_list': [...],       # List[Dict]
    'certificate_list': [...],  # List[Dict]
    'language_list': [...],     # List[Dict]
    'military': {...},          # Dict/None
    'award_list': [...],        # List (현재 빈 배열)
    'family_list': [...],       # List (현재 빈 배열)
    'salary_history_list': [],  # 미구현
    'salary_payment_list': [],  # 미구현
    'promotion_list': [],       # 미구현
    'evaluation_list': [],      # 미구현
    'training_list': [],        # 미구현
    'attendance_summary': None, # 미구현
    'asset_list': [],           # 미구현
}
```

**employee 데이터 필드** (라인 305-355):
```python
employee_data = {
    # 개인 기본정보 필드 (PersonalProfile)
    'name', 'english_name', 'chinese_name', 'photo', 'email',
    'phone', 'home_phone', 'address', 'detailed_address', 'postal_code',
    'actual_address', 'actual_detailed_address',
    'birth_date', 'lunar_birth', 'gender', 'marital_status',
    'resident_number', 'nationality', 'emergency_contact', 'emergency_relation',
    'blood_type', 'religion', 'hobby', 'specialty', 'disability_info',

    # 소속정보 (계약 기반)
    'department', 'team', 'position', 'job_title', 'employee_number',
    'employment_type', 'work_location', 'internal_phone', 'company_email',
    'hire_date', 'status',

    # 계약 관련 추가 필드
    'contract_period', 'probation_end', 'resignation_date',

    # 통계
    'contract_count', 'created_at'
}
```

**특징**:
- 개인 프로필 + 계약정보 조합하여 employee 구조 생성
- 모든 데이터를 Dict로 가공하여 반환
- 템플릿 파셜 호환성을 위해 법인 직원과 동일한 필드 구조 유지
- 미구현 인사기록 필드는 빈 배열로 제공

---

### 4.3 CorporateAdminProfileService (법인 관리자)

**파일**: `app/services/corporate_admin_profile_service.py`

**데이터 접근 방식**:
- Repository 패턴 사용
- CorporateAdminProfile 모델 객체 반환
- 어댑터로 감싸서 통합 프로필 시스템과 통합

**특징**:
- 경량 프로필 (기본정보 + 회사정보만)
- `get_adapter()` 메서드로 어댑터 생성
- 학력/경력/자격증 등 이력 정보 미제공

---

## 5. 어댑터 패턴 분석

### 5.1 ProfileAdapter (추상 어댑터)

**파일**: `app/adapters/profile_adapter.py`
**라인**: 14-144

**인터페이스**:
```python
- get_basic_info() → Dict
- get_organization_info() → Dict/None
- get_contract_info() → Dict/None
- get_salary_info() → Dict/None
- get_benefit_info() → Dict/None
- get_insurance_info() → Dict/None
- get_education_list() → List[Dict]
- get_career_list() → List[Dict]
- get_certificate_list() → List[Dict]
- get_language_list() → List[Dict]
- get_military_info() → Dict/None
- is_corporate() → bool
- get_available_sections() → List[str]
- get_profile_id() → int
- get_display_name() → str
- get_photo_url() → str
- get_account_type() → str
- to_template_context(variable_name='profile') → Dict
```

**to_template_context() 메서드**:
- 모든 어댑터 메서드 호출하여 통합 컨텍스트 생성
- `variable_name` 파라미터로 템플릿 변수명 지정 가능
- `employee` 또는 `profile` 변수로 전달

---

### 5.2 EmployeeProfileAdapter (법인 직원)

**라인**: 147-322

**AVAILABLE_SECTIONS**:
```python
['basic', 'organization', 'contract', 'salary', 'benefit', 'insurance',
 'education', 'career', 'certificate', 'language', 'military',
 'employment_contract', 'personnel_movement', 'attendance_assets']
```

**추가 메서드** (법인 전용):
- `get_family_list()`
- `get_salary_history_list()`
- `get_promotion_list()`
- `get_evaluation_list()`
- `get_training_list()`
- `get_attendance_list()`
- `get_project_list()`
- `get_award_list()`
- `get_asset_list()`

**데이터 반환**:
- ORM relationships 사용 (`.all()`)
- 각 모델의 `.to_dict()` 호출
- 모든 데이터를 Dict로 변환하여 반환

---

### 5.3 PersonalProfileAdapter (개인 계정)

**라인**: 324-448

**AVAILABLE_SECTIONS**:
```python
['basic', 'education', 'career', 'certificate', 'language', 'military', 'award']
```

**법인 전용 메서드 반환값**:
- `get_organization_info()` → None
- `get_contract_info()` → None
- `get_salary_info()` → None
- `get_benefit_info()` → None
- `get_insurance_info()` → None

**추가 메서드**:
- `get_award_list()` (PersonalAward 사용)
- `get_user_id()` (연결된 User ID)

---

### 5.4 CorporateAdminProfileAdapter (법인 관리자)

**라인**: 450-583

**AVAILABLE_SECTIONS**:
```python
['basic', 'company_info']
```

**제한된 필드**:
```python
basic_info = {
    'id', 'name', 'english_name', 'mobile_phone', 'email',
    'photo', 'position', 'department', 'office_phone', 'bio'
}
```

**모든 이력 메서드 반환값**:
- `get_education_list()` → []
- `get_career_list()` → []
- `get_certificate_list()` → []
- `get_language_list()` → []
- `get_military_info()` → None

**추가 메서드**:
- `is_admin()` → True
- `get_user_id()`
- `get_company_id()`

---

## 6. 불일치 및 개선 사항

### 6.1 인사카드 페이지 불일치 항목

#### 우선순위 1: 타입 불일치

**1-1. employee 필드 타입 불일치**

- **현재 상태**:
  - 법인 직원: Employee 모델 객체
  - 개인 계정: Dict (개인 프로필 기반 가공 데이터)

- **문제점**:
  - 템플릿에서 `employee.name` 접근시 객체 속성 vs Dict 키로 접근 방식 차이
  - `.to_dict()` 필요 여부 불일치
  - 타입 체크 로직 필요

- **권장 해결책**:
  - 법인 직원도 Dict로 변환하여 전달 (일관성)
  - 또는 개인 계정도 객체로 변환 (현재 어댑터 패턴과 충돌)

**1-2. military 필드 타입 불일치**

- **현재 상태**:
  - 법인 직원: Military 모델 객체
  - 개인 계정: Dict

- **권장 해결책**:
  - 법인 직원도 `military.to_dict()` 호출 후 전달
  - 또는 템플릿에서 `.to_dict() if military else None` 처리

#### 우선순위 2: 네이밍 불일치

**2-1. 회사 정보 필드 네이밍**

- **현재 상태**:
  - 법인 직원: `company_info` (Dict)
  - 개인 계정: `company` (Company 객체)

- **권장 해결책**:
  - `company_info`로 통일
  - 둘 다 Dict 타입으로 변환

#### 우선순위 3: 필드 누락

**3-1. is_readonly 필드**

- **현재 상태**:
  - 법인 직원: `is_readonly=True`
  - 개인 계정: 없음

- **권장 해결책**:
  - 개인 계정 인사카드에도 `is_readonly=True` 추가
  - 템플릿에서 편집 버튼 표시 제어용

**3-2. contract_info 중복**

- **현재 상태**:
  - 법인 직원: 없음
  - 개인 계정: `contract_info` (별도 제공)

- **권장 해결책**:
  - 법인 직원도 `contract_info` 제공 (contract와 중복이지만 일관성)
  - 또는 개인 계정에서 제거 (contract로 통합)

#### 우선순위 4: 미구현 필드

**4-1. 개인 계정 인사기록 데이터**

- **현재 상태**:
  - `salary_history_list`: []
  - `salary_payment_list`: []
  - `promotion_list`: []
  - `evaluation_list`: []
  - `training_list`: []
  - `attendance_summary`: None
  - `asset_list`: []

- **확인 필요**:
  - 개인 계정용 인사기록 데이터 모델 존재 여부
  - 계약별 인사기록 데이터 제공 여부
  - 템플릿에서 빈 배열 처리 로직

---

### 6.2 프로필 페이지 일관성 평가

**긍정적 측면**:
- 어댑터 패턴으로 3가지 계정 타입 통합 성공
- `to_template_context()` 메서드로 일관된 컨텍스트 생성
- `employee` 변수명 통일 (기존 파셜 호환)
- 필드 네이밍 및 타입 일관성 우수

**개선 여지**:
- 법인 관리자의 제한된 필드 (설계 의도에 따름)
- 어댑터에서 추가하는 `family_list`, `project_list`, `award_list` 통일성 검토

---

## 7. 리팩토링 우선순위 제안

### Phase 1: 타입 일관성 확보

1. `mypage.py` 인사카드 라우트 수정:
   - `employee` 객체를 Dict로 변환 후 전달
   - `military` 객체를 Dict로 변환

2. `personal.py` 인사카드 라우트 수정:
   - `company` → `company_info` 네이밍 통일
   - `is_readonly=True` 추가

### Phase 2: 인사카드 데이터 구조 표준화

3. 인사카드 서비스 메서드 생성:
   - `EmployeeService.get_hr_card_data(employee_id)` → Dict
   - `PersonalService.get_company_card_data()` 리팩토링
   - 동일한 구조의 Dict 반환

### Phase 3: 템플릿 파셜 최적화

4. 공유 파셜 템플릿 수정:
   - 타입 체크 로직 제거
   - Dict 접근 방식 통일
   - 조건부 렌더링 일관성 확보

### Phase 4: 문서화

5. 데이터 스키마 문서화:
   - 프로필 컨텍스트 스키마
   - 인사카드 컨텍스트 스키마
   - 필드별 타입 및 설명

---

## 8. 코드 예시: 개선 방안

### 8.1 법인 직원 인사카드 데이터 구조 통일

**현재** (`mypage.py`):
```python
return render_template('mypage/company_info.html',
    employee=employee,  # Employee 객체
    company_info=company_data,
    military=military,  # Military 객체
    ...
)
```

**개선안**:
```python
return render_template('mypage/company_info.html',
    employee=employee.to_dict(),  # Dict로 변환
    company_info=company_data,
    military=military.to_dict() if military else None,  # Dict로 변환
    is_readonly=True,  # 명시적 추가
    ...
)
```

### 8.2 개인 계정 인사카드 네이밍 통일

**현재** (`personal.py`):
```python
return render_template('personal/company_card_detail.html',
    company=card_data['company'],  # 네이밍 불일치
    ...
)
```

**개선안**:
```python
card_data = {
    'company_info': {  # company → company_info로 변경
        'id': company.id,
        'name': company.name,
        'business_number': getattr(company, 'business_number', None),
        'address': getattr(company, 'address', None),
        'phone': getattr(company, 'phone', None),
    },
    ...
}

return render_template('personal/company_card_detail.html',
    company_info=card_data['company_info'],
    is_readonly=True,  # 추가
    ...
)
```

### 8.3 서비스 레이어 메서드 추가

**EmployeeService에 추가**:
```python
def get_hr_card_data(self, employee_id: int) -> Optional[Dict]:
    """
    인사카드용 데이터 조회

    Returns:
        Dict: 템플릿 렌더링용 표준화된 데이터
    """
    if not self.verify_access(employee_id):
        return None

    employee = self.employee_repo.get_by_id(employee_id)
    if not employee:
        return None

    # 회사 정보 조회
    company_data = self._get_company_info(employee.company_id)

    return {
        'employee': employee.to_dict(),  # Dict로 변환
        'company_info': company_data,
        'contract': employee.contract.to_dict() if employee.contract else None,
        'salary': employee.salary.to_dict() if employee.salary else None,
        'benefit': employee.benefit.to_dict() if employee.benefit else None,
        'insurance': employee.insurance.to_dict() if employee.insurance else None,
        'education_list': [edu.to_dict() for edu in employee.educations.all()],
        'career_list': [career.to_dict() for career in employee.careers.all()],
        'certificate_list': [cert.to_dict() for cert in employee.certificates.all()],
        'language_list': [lang.to_dict() for lang in employee.languages.all()],
        'military': employee.military_service.to_dict() if employee.military_service else None,
        'family_list': [member.to_dict() for member in employee.family_members.all()],
        'project_list': [proj.to_dict() for proj in employee.projects.all()],
        'award_list': [award.to_dict() for award in employee.awards.all()],
        # 인사기록
        'salary_history_list': [hist.to_dict() for hist in employee.salary_histories.all()],
        'salary_payment_list': [pay.to_dict() for pay in employee.salary_payments.all()],
        'promotion_list': [promo.to_dict() for promo in employee.promotions.all()],
        'evaluation_list': [eval_.to_dict() for eval_ in employee.evaluations.all()],
        'training_list': [train.to_dict() for train in employee.trainings.all()],
        'attendance_summary': self._get_attendance_summary(employee_id),
        'asset_list': [asset.to_dict() for asset in employee.assets.all()],
    }
```

**라우트 수정**:
```python
@mypage_bp.route('/company')
@login_required
def company_info():
    employee_id = session.get('employee_id')

    if not employee_id:
        flash('계정에 연결된 직원 정보가 없습니다.', 'warning')
        return redirect(url_for('main.index'))

    # 서비스 메서드 사용
    card_data = employee_service.get_hr_card_data(employee_id)

    if not card_data:
        flash('직원 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    return render_template('mypage/company_info.html',
                           **card_data,
                           is_readonly=True,
                           page_mode='hr_card')
```

---

## 9. 결론

### 주요 발견 사항

1. **프로필 페이지**: 어댑터 패턴 적용으로 높은 일관성 확보
2. **인사카드 페이지**: 타입 및 네이밍 불일치 존재
3. **서비스 레이어**: 데이터 반환 방식 차이 (객체 vs Dict)

### 우선 개선 항목

1. 인사카드 `employee` 필드 타입 통일 (객체 → Dict)
2. 회사 정보 필드 네이밍 통일 (`company_info`)
3. `is_readonly` 필드 추가
4. 서비스 메서드 표준화 (`get_hr_card_data`)

### 장기 개선 항목

1. 인사카드 전용 어댑터 패턴 검토
2. 개인 계정 인사기록 데이터 모델 설계
3. 데이터 스키마 문서화
4. 템플릿 파셜 최적화

---

**분석 완료일**: 2025-12-14
**다음 단계**: 리팩토링 계획 수립 및 우선순위 협의
