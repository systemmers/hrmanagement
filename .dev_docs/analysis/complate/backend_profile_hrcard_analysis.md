# 백엔드 프로필/인사카드 구조 분석

## 분석 개요

프로필과 인사카드의 백엔드 라우트, 서비스, 데이터 구조를 계정 타입별로 분석

작성일: 2025-12-14

## 1. 라우트 구조 비교

### 1.1 개인 계정 (Personal)

#### 프로필 라우트
```python
# 파일: app/blueprints/personal.py

# 프로필 상세 (리다이렉트)
@personal_bp.route('/profile')  # → redirect to profile.view (통합)

# 프로필 수정
@personal_bp.route('/profile/edit', methods=['GET', 'POST'])
- GET: redirect to profile.edit (통합)
- POST: 직접 처리 후 profile.view로 리다이렉트
```

#### 인사카드 라우트 (개인 계정용)
```python
# 계약 회사 목록
@personal_bp.route('/company-cards')
→ 템플릿: personal/company_card_list.html

# 특정 회사 인사카드 상세
@personal_bp.route('/company-cards/<int:contract_id>')
→ 템플릿: personal/company_card_detail.html
→ page_mode: 'hr_card'
```

### 1.2 법인 직원 계정 (Corporate Employee)

#### 프로필 라우트
```python
# 파일: app/blueprints/profile/routes.py

# 통합 프로필 상세
@profile_bp.route('/')
@unified_profile_required
→ 템플릿: profile/detail.html
→ page_mode: 'profile'

# 통합 프로필 수정
@profile_bp.route('/edit', methods=['GET', 'POST'])
@unified_profile_required
- GET: 수정 폼 표시
- POST: employees.employee_edit로 리다이렉트
```

#### 인사카드 라우트
```python
# 파일: app/blueprints/employees/routes.py

# 인사카드 상세
@bp.route('/employees/<int:employee_id>')
→ 함수: employee_detail()
→ 내부: _render_employee_full_view()
→ 템플릿: (통합 템플릿 사용, 구체 이름 미확인)
→ page_mode: 추정 'hr_card' 또는 기본값

# 인사카드 수정
@bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
→ 함수: employee_edit()
→ 템플릿: profile/edit.html
```

### 1.3 법인 관리자 계정 (Corporate Admin)

#### 프로필 라우트
```python
# 파일: app/blueprints/profile/routes.py

# 프로필 생성
@profile_bp.route('/admin/create', methods=['GET', 'POST'])
→ 템플릿: profile/admin_profile_create.html

# 프로필 상세
@profile_bp.route('/')
@unified_profile_required
→ 템플릿: profile/detail.html
→ page_mode: 'profile'

# 프로필 수정
@profile_bp.route('/admin/edit', methods=['GET', 'POST'])
@corporate_admin_only
→ 템플릿: profile/admin_profile_edit.html
```

#### 인사카드 라우트
```
없음 (법인 관리자는 직원이 아니므로 인사카드가 없음)
```

## 2. 서비스 계층 분석

### 2.1 개인 계정 서비스 (PersonalService)

**파일**: `app/services/personal_service.py`

#### 프로필 관련 메서드
```python
# 프로필 조회/수정
get_user_with_profile(user_id) → (User, PersonalProfile)
get_dashboard_data(user_id) → Dict
ensure_profile_exists(user_id, default_name) → PersonalProfile
update_profile(user_id, data) → (success, error_msg)

# 이력 CRUD
get_educations(profile_id) → List[Dict]
add_education(profile_id, data) → Dict
delete_education(education_id, profile_id) → bool

get_careers(profile_id) → List[Dict]
add_career(profile_id, data) → Dict
delete_career(career_id, profile_id) → bool

get_certificates(profile_id) → List[Dict]
add_certificate(profile_id, data) → Dict
delete_certificate(certificate_id, profile_id) → bool

get_languages(profile_id) → List[Dict]
add_language(profile_id, data) → Dict
delete_language(language_id, profile_id) → bool

get_military(profile_id) → Optional[Dict]
save_military(profile_id, data) → Dict
```

#### 인사카드 관련 메서드
```python
# 계약 조회
get_approved_contracts(user_id) → List[Dict]
  # 반환 필드: id, company_id, company_name, company_logo,
  #           position, department, contract_start_date,
  #           contract_end_date, approved_at

# 인사카드 데이터 구성
get_company_card_data(user_id, contract_id) → Optional[Dict]
  # 반환 구조:
  {
    'employee': {...},  # 프로필 기반으로 구성된 employee 데이터
    'contract': {...},
    'company': {...},
    'contract_info': {...},
    # 이력 정보
    'education_list': [],
    'career_list': [],
    'certificate_list': [],
    'language_list': [],
    'military': {},
    'award_list': [],  # 현재 빈 배열
    'family_list': [],  # 현재 빈 배열
    # 인사기록 정보 (개인 계정은 모두 빈 값)
    'salary_history_list': [],
    'salary_payment_list': [],
    'promotion_list': [],
    'evaluation_list': [],
    'training_list': [],
    'attendance_summary': None,
    'asset_list': [],
  }
```

### 2.2 법인 직원 서비스 (Repository 계층)

**파일**: `app/repositories/*_repository.py` (여러 파일로 분산)

#### 주요 Repository
- EmployeeRepository: 직원 기본 정보
- EducationRepository: 학력 정보
- CareerRepository: 경력 정보
- CertificateRepository: 자격증 정보
- LanguageRepository: 어학 정보
- MilitaryServiceRepository: 병역 정보
- FamilyMemberRepository: 가족 정보
- AwardRepository: 수상 정보
- ProjectRepository: 프로젝트 정보
- SalaryHistoryRepository: 급여 이력
- PromotionRepository: 승진 이력
- EvaluationRepository: 평가 정보
- TrainingRepository: 교육 정보
- AttendanceRepository: 근태 정보
- AssetRepository: 비품 정보

#### 데이터 조회 패턴 (employee_detail 함수)
```python
# app/blueprints/employees/routes.py 내 _render_employee_full_view()

# 이력 정보
education_list = education_repo.get_by_employee_id(employee_id)
career_list = career_repo.get_by_employee_id(employee_id)
certificate_list = certificate_repo.get_by_employee_id(employee_id)
language_list = language_repo.get_by_employee_id(employee_id)
military = military_repo.get_by_employee_id(employee_id)
award_list = award_repo.get_by_employee_id(employee_id)
project_list = project_repo.get_by_employee_id(employee_id)
family_list = family_repo.get_by_employee_id(employee_id)

# 인사기록 정보
salary_history_list = salary_history_repo.get_by_employee_id(employee_id)
salary_payment_list = salary_payment_repo.get_by_employee_id(employee_id)
promotion_list = promotion_repo.get_by_employee_id(employee_id)
evaluation_list = evaluation_repo.get_by_employee_id(employee_id)
training_list = training_repo.get_by_employee_id(employee_id)
attendance_summary = attendance_repo.get_summary_by_employee_id(employee_id)
asset_list = asset_repo.get_by_employee_id(employee_id)

# 1:1 관계 (employee 모델에서 직접 접근)
salary = employee.salary
benefit = employee.benefit
contract = employee.contract
insurance = employee.insurance
```

### 2.3 법인 관리자 서비스 (CorporateAdminProfileService)

**파일**: `app/services/corporate_admin_profile_service.py`

```python
# 프로필 관리
has_profile(user_id) → bool
create_profile(user_id, company_id, data) → (success, profile, error)
update_profile(user_id, data) → (success, error)
get_adapter(user_id) → CorporateAdminProfileAdapter
```

## 3. 템플릿 컨텍스트 데이터 구조

### 3.1 개인 계정 - 프로필 상세 (profile.view)

**템플릿**: `profile/detail.html`

**컨텍스트 변수**:
```python
{
  'employee': {  # PersonalProfile 기반 데이터
    'id': int,
    'name': str,
    'english_name': str,
    'chinese_name': str,
    'photo': str,
    'birth_date': str,
    'lunar_birth': bool,
    'gender': str,
    'mobile_phone': str,
    'home_phone': str,
    'email': str,
    'postal_code': str,
    'address': str,
    'detailed_address': str,
    'nationality': str,
    'blood_type': str,
    'religion': str,
    'hobby': str,
    'specialty': str,
    'is_public': bool,
    'resident_number': str,
  },
  'sections': ['basic'],  # 개인 계정은 basic만
  'page_mode': 'profile',
  # 이력 데이터
  'education_list': [],
  'career_list': [],
  'certificate_list': [],
  'language_list': [],
  'military': {},
}
```

### 3.2 개인 계정 - 인사카드 상세 (company_card_detail)

**템플릿**: `personal/company_card_detail.html`

**컨텍스트 변수**:
```python
{
  # 기본 정보
  'contract': {
    'id': int,
    'position': str,
    'department': str,
    'employee_number': str,
    'contract_type': str,
    'contract_start_date': date,
    'contract_end_date': date,
    'approved_at': datetime,
    'contract_date': date,
    'contract_period': str,
    'employee_type': str,
    'work_type': str,
  },
  'company': {
    'id': int,
    'name': str,
    'business_number': str,
    'address': str,
    'phone': str,
  },
  'employee': {  # PersonalProfile 기반으로 구성
    'id': int,
    # 개인 기본정보 (PersonalProfile 필드)
    'name': str,
    'english_name': str,
    'chinese_name': str,
    'photo': str,
    'email': str,
    'phone': str,  # mobile_phone
    'home_phone': str,
    'address': str,
    'detailed_address': str,
    'postal_code': str,
    'actual_address': str,
    'actual_detailed_address': str,
    'birth_date': str,
    'lunar_birth': bool,
    'gender': str,
    'marital_status': str,
    'resident_number': str,
    'nationality': str,
    'emergency_contact': str,
    'emergency_relation': str,
    'blood_type': str,
    'religion': str,
    'hobby': str,
    'specialty': str,
    'disability_info': str,
    # 소속정보 (Contract 기반)
    'department': str,
    'team': str,
    'position': str,
    'job_title': str,
    'employee_number': str,
    'employment_type': str,
    'work_location': str,
    'internal_phone': str,
    'company_email': str,
    'hire_date': date,
    'status': str,
    'contract_period': str,
    'probation_end': date,
    'resignation_date': date,
    # 통계
    'contract_count': int,
    'created_at': str,
  },
  'contract_info': {
    'contract_type': str,
    'start_date': date,
    'end_date': date,
  },
  # 급여/복리후생 (현재 미구현)
  'salary': None,
  'benefit': None,
  'insurance': None,
  # 이력 정보 (PersonalProfile 기반)
  'education_list': [
    {
      'id': int,
      'school_type': str,
      'school_name': str,
      'major': str,
      'graduation_status': str,
      'admission_date': str,
      'graduation_date': str,
    }
  ],
  'career_list': [
    {
      'id': int,
      'company_name': str,
      'department': str,
      'position': str,
      'start_date': str,
      'end_date': str,
      'is_current': bool,
      'duties': str,
    }
  ],
  'certificate_list': [
    {
      'id': int,
      'name': str,
      'issuer': str,
      'acquisition_date': str,
      'expiry_date': str,
    }
  ],
  'language_list': [
    {
      'id': int,
      'language': str,
      'proficiency': str,
      'certification': str,
      'score': str,
    }
  ],
  'military': {
    'service_type': str,
    'branch': str,
    'rank': str,
    'start_date': str,
    'end_date': str,
    'exemption_reason': str,
  },
  'award_list': [],  # 현재 빈 배열
  'family_list': [],  # 현재 빈 배열
  # 인사기록 정보 (개인 계정은 모두 빈 값)
  'salary_history_list': [],
  'salary_payment_list': [],
  'promotion_list': [],
  'evaluation_list': [],
  'training_list': [],
  'attendance_summary': None,
  'asset_list': [],
  # 페이지 모드
  'page_mode': 'hr_card',
}
```

### 3.3 법인 직원 - 프로필 상세 (profile.view)

**템플릿**: `profile/detail.html`

**컨텍스트 변수**:
```python
{
  'employee': {  # Employee 모델 기반 (to_dict())
    # 기본 정보
    'id': int,
    'employee_number': str,
    'name': str,
    'photo': str,
    'department': str,
    'position': str,
    'status': str,
    'hire_date': str,
    'phone': str,
    'email': str,
    'organization_id': int,
    'organization': {},
    # 소속 정보
    'team': str,
    'job_title': str,
    'work_location': str,
    'internal_phone': str,
    'company_email': str,
    # 개인 정보
    'english_name': str,
    'chinese_name': str,
    'birth_date': str,
    'lunar_birth': bool,
    'gender': str,
    'mobile_phone': str,
    'home_phone': str,
    'address': str,
    'detailed_address': str,
    'postal_code': str,
    'resident_number': str,
    'nationality': str,
    'blood_type': str,
    'religion': str,
    'hobby': str,
    'specialty': str,
    'disability_info': str,
    'marital_status': str,
    'actual_postal_code': str,
    'actual_address': str,
    'actual_detailed_address': str,
    'emergency_contact': str,
    'emergency_relation': str,
  },
  'sections': ['basic'],  # 법인 직원도 프로필은 basic만
  'page_mode': 'profile',
  # 이력 데이터
  'education_list': [],
  'career_list': [],
  'certificate_list': [],
  'language_list': [],
  'military': {},
}
```

### 3.4 법인 직원 - 인사카드 상세 (employee_detail)

**템플릿**: (통합 템플릿, 구체 이름 미확인)

**컨텍스트 변수**: (_render_employee_full_view 함수 기반)
```python
{
  'employee': {  # Employee 모델 to_dict() 결과
    # 위 3.3 employee 구조와 동일
  },
  # 1:1 관계 (Employee 모델의 relationship)
  'salary': {
    'base_salary': int,
    'allowance': int,
    'total_salary': int,
  },
  'benefit': {
    'health_insurance': bool,
    'pension': bool,
    'etc': str,
  },
  'contract': {
    'contract_type': str,
    'start_date': date,
    'end_date': date,
    'contract_period': str,
  },
  'insurance': {
    'health_insurance_number': str,
    'pension_number': str,
    'employment_insurance': bool,
    'industrial_accident_insurance': bool,
  },
  # 1:N 관계
  'education_list': [],
  'career_list': [],
  'certificate_list': [],
  'language_list': [],
  'military': {},
  'award_list': [],
  'project_list': [],
  'family_list': [],
  # 인사기록 정보
  'salary_history_list': [],
  'salary_payment_list': [],
  'promotion_list': [],
  'evaluation_list': [],
  'training_list': [],
  'attendance_summary': {},
  'asset_list': [],
  # 첨부파일
  'attachment_list': [],
  'business_card_front': {},
  'business_card_back': {},
  # 페이지 모드 (추정)
  'page_mode': 'hr_card',  # 또는 기본값
}
```

### 3.5 법인 관리자 - 프로필 상세 (profile.view)

**템플릿**: `profile/detail.html`

**컨텍스트 변수**:
```python
{
  'employee': {  # CorporateAdminProfile 기반 (어댑터를 통해 구성)
    'id': int,
    'name': str,
    'english_name': str,
    'position': str,
    'department': str,
    'mobile_phone': str,
    'office_phone': str,
    'email': str,
    'bio': str,
    'company_id': int,
    'photo': str,  # 기본 아바타
  },
  'sections': ['basic', 'organization'],  # 관리자는 basic + organization
  'page_mode': 'profile',
  # 소속 회사 정보
  'organization': {
    'id': int,
    'name': str,
    'business_number': str,
    'address': str,
    'phone': str,
  },
}
```

## 4. 섹션별 필드 비교표

### 4.1 기본정보 (개인정보) 섹션

| 필드명 | 개인 계정 | 법인 직원 | 법인 관리자 | 비고 |
|--------|----------|----------|-----------|------|
| name | O | O | O | 이름 |
| english_name | O | O | O | 영문명 |
| chinese_name | O | O | X | 한문명 |
| photo | O | O | O | 사진 |
| birth_date | O | O | X | 생년월일 |
| lunar_birth | O | O | X | 음력여부 |
| gender | O | O | X | 성별 |
| resident_number | O | O | X | 주민번호 |
| mobile_phone | O | O | O | 휴대전화 |
| home_phone | O | O | X | 자택전화 |
| email | O | O | O | 이메일 |
| address | O | O | X | 주소 |
| detailed_address | O | O | X | 상세주소 |
| postal_code | O | O | X | 우편번호 |
| actual_address | X | O | X | 실거주지 주소 |
| actual_detailed_address | X | O | X | 실거주지 상세주소 |
| nationality | O | O | X | 국적 |
| blood_type | O | O | X | 혈액형 |
| religion | O | O | X | 종교 |
| hobby | O | O | X | 취미 |
| specialty | O | O | X | 특기 |
| marital_status | X | O | X | 결혼여부 |
| emergency_contact | X | O | X | 비상연락처 |
| emergency_relation | X | O | X | 비상연락처 관계 |
| disability_info | X | O | X | 장애정보 |
| is_public | O | X | X | 공개여부 |
| office_phone | X | X | O | 사무실 전화 |
| position | X | X | O | 직급 (관리자는 basic) |
| department | X | X | O | 부서 (관리자는 basic) |
| bio | X | X | O | 소개 |

### 4.2 소속정보 섹션

| 필드명 | 개인 계정 | 법인 직원 | 법인 관리자 | 비고 |
|--------|----------|----------|-----------|------|
| department | 인사카드 | O | O | 부서 |
| team | 인사카드 | O | X | 팀 |
| position | 인사카드 | O | X | 직급 |
| job_title | 인사카드 | O | X | 직책 |
| employee_number | 인사카드 | O | X | 사번 |
| employment_type | 인사카드 | O | X | 고용형태 |
| work_location | 인사카드 | O | X | 근무지 |
| internal_phone | 인사카드 | O | X | 내선번호 |
| company_email | 인사카드 | O | X | 회사 이메일 |
| hire_date | 인사카드 | O | X | 입사일 |
| status | 인사카드 | O | X | 재직상태 |
| contract_period | 인사카드 | X | X | 계약기간 |
| probation_end | 인사카드 | X | X | 수습종료일 |
| resignation_date | 인사카드 | X | X | 퇴사일 |
| company_name | X | X | O | 회사명 (organization) |
| business_number | X | X | O | 사업자번호 (organization) |

### 4.3 이력 섹션

| 섹션 | 개인 계정 프로필 | 개인 계정 인사카드 | 법인 직원 프로필 | 법인 직원 인사카드 | 법인 관리자 |
|------|----------------|------------------|----------------|------------------|----------|
| 학력 | O | O | O | O | X |
| 경력 | O | O | O | O | X |
| 자격증 | O | O | O | O | X |
| 어학 | O | O | O | O | X |
| 병역 | O | O | O | O | X |
| 수상 | X | X (빈값) | O | O | X |
| 프로젝트 | X | X (빈값) | O | O | X |
| 가족정보 | X | X (빈값) | X | O | X |

### 4.4 인사기록 섹션 (인사카드 전용)

| 섹션 | 개인 계정 인사카드 | 법인 직원 인사카드 | 비고 |
|------|------------------|------------------|------|
| 계약정보 | O (Contract 기반) | O (Contract 모델) | |
| 급여정보 | X (None) | O (Salary 모델) | |
| 복리후생 | X (None) | O (Benefit 모델) | |
| 4대보험 | X (None) | O (Insurance 모델) | |
| 급여이력 | X (빈 배열) | O | salary_history_list |
| 급여지급 | X (빈 배열) | O | salary_payment_list |
| 승진이력 | X (빈 배열) | O | promotion_list |
| 평가기록 | X (빈 배열) | O | evaluation_list |
| 교육이력 | X (빈 배열) | O | training_list |
| 근태요약 | X (None) | O | attendance_summary |
| 비품목록 | X (빈 배열) | O | asset_list |

## 5. 권한 체계

### 5.1 개인 계정

**프로필 (profile.view, profile.edit)**:
- 자신의 프로필만 조회/수정 가능
- 데코레이터: `@personal_login_required` (personal.py), `@unified_profile_required` (profile/routes.py)
- 표시 섹션: 기본정보(개인정보)만
- page_mode: 'profile'

**인사카드 (company_card_detail)**:
- 자신이 계약한 회사의 인사카드만 조회 가능
- 수정 불가 (읽기 전용)
- 데코레이터: `@personal_login_required`
- 표시 섹션: 기본정보 + 이력 정보 + 인사기록 정보 (일부는 빈 값)
- page_mode: 'hr_card'

### 5.2 법인 직원 계정

**프로필 (profile.view, profile.edit)**:
- 자신의 프로필만 조회/수정 가능
- 데코레이터: `@unified_profile_required`
- 표시 섹션: 기본정보(개인정보)만
- page_mode: 'profile'

**인사카드 (employee_detail, employee_edit)**:
- role=employee: 자신의 인사카드만 조회/수정 가능
- role=admin/manager: 자사 소속 직원 인사카드 조회/수정 가능
- 데코레이터: `@login_required`
- 표시 섹션: 기본정보 + 소속정보 + 이력정보 + 인사기록 정보 (전체)
- page_mode: 'hr_card' (추정)

### 5.3 법인 관리자 계정

**프로필 (profile.view, admin_profile_edit)**:
- 자신의 프로필만 조회/수정 가능
- 데코레이터: `@corporate_admin_only`
- 표시 섹션: 기본정보(개인정보) + 소속정보(회사 정보)
- page_mode: 'profile'

**인사카드**:
- 없음 (관리자는 직원이 아니므로 인사카드가 없음)

## 6. 데이터 흐름 다이어그램

### 6.1 개인 계정 - 프로필 조회

```
사용자 요청
  ↓
personal.profile → redirect → profile.view
  ↓
@unified_profile_required 데코레이터
  ↓
PersonalProfileAdapter 생성 (g.profile)
  ↓
adapter.to_template_context(variable_name='employee')
  ↓
PersonalProfile 모델 → Dict 변환
  ↓
템플릿: profile/detail.html
  - employee: PersonalProfile 데이터
  - sections: ['basic']
  - page_mode: 'profile'
```

### 6.2 개인 계정 - 인사카드 조회

```
사용자 요청
  ↓
personal.company_card_detail(contract_id)
  ↓
@personal_login_required
  ↓
personal_service.get_company_card_data(user_id, contract_id)
  ↓
PersonCorporateContract 조회 (권한 확인)
  ↓
PersonalProfile 조회 → employee 데이터 구성
  ↓
이력 데이터 조회 (education, career, certificate, language, military)
  ↓
템플릿: personal/company_card_detail.html
  - employee: PersonalProfile 기반 dict
  - contract: PersonCorporateContract 데이터
  - company: Company 데이터
  - education_list, career_list 등
  - 인사기록: 모두 빈 값 또는 None
  - page_mode: 'hr_card'
```

### 6.3 법인 직원 - 프로필 조회

```
사용자 요청
  ↓
profile.view
  ↓
@unified_profile_required 데코레이터
  ↓
CorporateEmployeeProfileAdapter 생성 (g.profile)
  ↓
adapter.to_template_context(variable_name='employee')
  ↓
Employee 모델 → to_dict() → Dict 변환
  ↓
템플릿: profile/detail.html
  - employee: Employee 데이터
  - sections: ['basic']
  - page_mode: 'profile'
```

### 6.4 법인 직원 - 인사카드 조회

```
사용자 요청
  ↓
employees.employee_detail(employee_id)
  ↓
@login_required + 권한 확인 (본인 또는 관리자)
  ↓
employee_repo.get_by_id(employee_id)
  ↓
_render_employee_full_view(employee_id, employee)
  ↓
다중 Repository 조회:
  - education_repo.get_by_employee_id()
  - career_repo.get_by_employee_id()
  - certificate_repo.get_by_employee_id()
  - language_repo.get_by_employee_id()
  - military_repo.get_by_employee_id()
  - award_repo.get_by_employee_id()
  - project_repo.get_by_employee_id()
  - family_repo.get_by_employee_id()
  - salary_history_repo.get_by_employee_id()
  - salary_payment_repo.get_by_employee_id()
  - promotion_repo.get_by_employee_id()
  - evaluation_repo.get_by_employee_id()
  - training_repo.get_by_employee_id()
  - attendance_repo.get_summary_by_employee_id()
  - asset_repo.get_by_employee_id()
  - attachment_repo.get_by_employee_id()
  ↓
1:1 관계 (employee 모델에서 직접 접근):
  - employee.salary
  - employee.benefit
  - employee.contract
  - employee.insurance
  ↓
템플릿: (통합 템플릿)
  - employee: Employee to_dict()
  - 모든 이력 데이터
  - 모든 인사기록 데이터
  - page_mode: 'hr_card' (추정)
```

### 6.5 법인 관리자 - 프로필 조회

```
사용자 요청
  ↓
profile.view
  ↓
@unified_profile_required 데코레이터
  ↓
CorporateAdminProfileAdapter 생성 (g.profile)
  ↓
adapter.to_template_context(variable_name='employee')
  ↓
CorporateAdminProfile 모델 → Dict 변환
  ↓
adapter.get_organization_info() → Company 데이터
  ↓
템플릿: profile/detail.html
  - employee: CorporateAdminProfile 데이터
  - organization: Company 데이터
  - sections: ['basic', 'organization']
  - page_mode: 'profile'
```

## 7. 핵심 차이점 요약

### 7.1 프로필 vs 인사카드 차이

| 구분 | 프로필 (Profile) | 인사카드 (HR Card) |
|------|----------------|------------------|
| 목적 | 개인정보 조회/수정 | 법인 소속 정보 포함 전체 조회 |
| 표시 섹션 | 기본정보(개인정보)만 | 기본정보 + 소속정보 + 이력정보 + 인사기록 정보 |
| page_mode | 'profile' | 'hr_card' |
| 수정 권한 | 본인만 | 본인 + 관리자 |
| 이력 데이터 | O (학력, 경력, 자격증, 어학, 병역) | O (전체 + 수상, 프로젝트, 가족) |
| 인사기록 데이터 | X | O (법인만, 개인은 빈 값) |

### 7.2 계정 타입별 차이

| 항목 | 개인 계정 | 법인 직원 | 법인 관리자 |
|------|----------|----------|-----------|
| 프로필 데이터 소스 | PersonalProfile | Employee | CorporateAdminProfile |
| 인사카드 존재 | O (계약 회사별) | O (자사) | X |
| 소속정보 섹션 | 인사카드에만 (Contract 기반) | 프로필/인사카드 모두 | 프로필에 회사 정보 |
| 인사기록 섹션 | X (빈 값) | O (전체) | X |
| 수상/프로젝트 | X (빈 값) | O | X |
| 가족정보 | X (빈 값) | O (인사카드만) | X |

### 7.3 템플릿 재사용 전략

**공통 템플릿**:
- `profile/detail.html`: 모든 계정 타입의 프로필 상세
- `profile/edit.html`: 모든 계정 타입의 프로필 수정 (법인 직원은 인사카드 수정에도 사용)
- 파셜 템플릿 (`partials/employee_detail/`): 인사카드 섹션 공유

**계정 타입별 템플릿**:
- `personal/company_card_detail.html`: 개인 계정 인사카드 (파셜 include)
- `profile/admin_profile_create.html`: 법인 관리자 프로필 생성
- `profile/admin_profile_edit.html`: 법인 관리자 프로필 수정

**page_mode 활용**:
- 'profile': 기본정보만 표시
- 'hr_card': 기본정보 + 소속정보 + 이력정보 + 인사기록 정보 표시

## 8. API 엔드포인트 요약

### 8.1 개인 계정

```
GET  /personal/profile                          → redirect to /profile/
GET  /personal/profile/edit                     → redirect to /profile/edit
POST /personal/profile/edit                     → 프로필 수정 처리

GET  /personal/company-cards                    → 계약 회사 목록
GET  /personal/company-cards/<contract_id>      → 특정 회사 인사카드 상세

# 이력 API
GET    /personal/education                      → 학력 목록
POST   /personal/education                      → 학력 추가
DELETE /personal/education/<education_id>       → 학력 삭제
(career, certificate, language, military도 동일 패턴)
```

### 8.2 법인 직원

```
# 통합 프로필
GET  /profile/                                  → 프로필 상세
GET  /profile/edit                              → 프로필 수정 폼
POST /profile/edit                              → redirect to employees.employee_edit

# 인사카드
GET  /employees/<employee_id>                   → 인사카드 상세
GET  /employees/<employee_id>/edit              → 인사카드 수정 폼
POST /employees/<employee_id>/update            → 인사카드 수정 처리

# 법인 전용 API
GET  /profile/corporate/salary-history          → 급여 이력
GET  /profile/corporate/promotions              → 승진 이력
GET  /profile/corporate/evaluations             → 평가 기록
GET  /profile/corporate/trainings               → 교육 이력
GET  /profile/corporate/attendances             → 근태 기록
GET  /profile/corporate/assets                  → 비품 목록
GET  /profile/corporate/family                  → 가족 정보
```

### 8.3 법인 관리자

```
# 프로필
GET  /profile/                                  → 프로필 상세
GET  /profile/admin/create                      → 프로필 생성 폼
POST /profile/admin/create                      → 프로필 생성 처리
GET  /profile/admin/edit                        → 프로필 수정 폼
POST /profile/admin/edit                        → 프로필 수정 처리

# API
GET  /profile/api/admin/profile                 → 프로필 조회 API
PUT  /profile/api/admin/profile                 → 프로필 수정 API
GET  /profile/api/admin/company                 → 소속 회사 정보 API
```

## 9. 개선 권장사항

### 9.1 데이터 구조 일관성

**현재 문제**:
- 개인 계정 인사카드의 employee 데이터가 PersonalProfile 기반으로 수동 구성됨
- 법인 직원 인사카드의 employee 데이터가 Employee 모델 기반
- 필드명이 일부 불일치 (phone vs mobile_phone)

**권장 개선**:
- Adapter 패턴을 개인 계정 인사카드에도 적용하여 일관된 데이터 구조 제공
- 공통 인터페이스 정의로 템플릿에서 동일한 필드명 사용 가능

### 9.2 인사기록 데이터 처리

**현재 문제**:
- 개인 계정 인사카드에서 인사기록 섹션이 모두 빈 값으로 전달됨
- 템플릿에서 빈 값 체크 필요

**권장 개선**:
- page_mode나 섹션 설정으로 인사기록 섹션 자체를 표시/숨김 처리
- 불필요한 빈 데이터 전달 제거

### 9.3 템플릿 명확화

**현재 문제**:
- 법인 직원 인사카드 상세의 템플릿 이름이 코드에 명시되지 않음
- _render_employee_full_view 함수에서 템플릿 렌더링 로직 확인 필요

**권장 개선**:
- 템플릿 경로를 명시적으로 관리
- 프로필/인사카드 템플릿 분리 또는 통합 여부 명확화

### 9.4 page_mode 표준화

**현재 문제**:
- 법인 직원 인사카드에서 page_mode 전달 여부 불명확
- 개인 계정 인사카드는 'hr_card'로 명시

**권장 개선**:
- 모든 인사카드 라우트에서 page_mode='hr_card' 명시적으로 전달
- 템플릿에서 page_mode 기반 섹션 표시/숨김 로직 일관성 확보
