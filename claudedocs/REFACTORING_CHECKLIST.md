 # Backend Architecture Refactoring Checklist

**Project**: D:\projects\hrmanagement
**Created**: 2025-12-20
**Last Updated**: 2025-12-20
**Status**: In Progress

---

## Phase 1A: DictSerializableMixin 확장

### 완료된 모델 (24개)
#### 이전 세션 완료 (8개)
- [x] Education
- [x] Career
- [x] Certificate
- [x] Language
- [x] FamilyMember
- [x] Award
- [x] ProjectParticipation
- [x] MilitaryService

#### 현재 세션 완료 (16개)
- [x] Attendance (`app/models/attendance.py`)
- [x] Training (`app/models/training.py`)
- [x] Salary (`app/models/salary.py`) - property alias 포함
- [x] Evaluation (`app/models/evaluation.py`)
- [x] Promotion (`app/models/promotion.py`)
- [x] Asset (`app/models/asset.py`)
- [x] SalaryHistory (`app/models/salary_history.py`)
- [x] AuditLog (`app/models/audit_log.py`) - JSON 필드 처리
- [x] Attachment (`app/models/attachment.py`)
- [x] Notification (`app/models/notification.py`) - 비즈니스 메서드 유지
- [x] NotificationPreference (`app/models/notification.py`)
- [x] Benefit (`app/models/benefit.py`)
- [x] Insurance (`app/models/insurance.py`)
- [x] Project (`app/models/project.py`)
- [x] SalaryPayment (`app/models/salary_payment.py`)
- [x] HrProject (`app/models/hr_project.py`)
- [x] Contract (`app/models/contract.py`)
- [x] CorporateAdminProfile (`app/models/corporate_admin_profile.py`)
- [x] DataSharingSettings (`app/models/person_contract.py`)
- [x] SyncLog (`app/models/person_contract.py`)

### Mixin 적용 보류 모델 (비즈니스 메서드/camelCase 호환성)
- [ ] Employee - 복잡한 관계 + computed 필드
- [ ] User - 인증 메서드 + 비밀번호 처리
- [ ] Company - 비즈니스 로직 + 파라미터 있는 to_dict
- [ ] Organization - 트리 구조 + 복잡한 관계
- [ ] Profile - 복잡한 관계
- [ ] PersonalProfile - 복잡한 관계
- [ ] PersonCorporateContract - 복잡한 비즈니스 로직 + 파라미터 있는 to_dict
- [ ] ClassificationOption - camelCase to_dict
- [ ] SystemSetting - get_typed_value 메서드
- [ ] CompanySettings - get_typed_value 메서드
- [ ] NumberCategory - 시퀀스 관리 메서드
- [ ] NumberRegistry - 할당/해제 메서드
- [ ] IpRange - IP 계산 메서드
- [ ] IpAssignment - 할당/해제 메서드
- [ ] CompanyDocument - 파라미터 있는 to_dict(include_ai=False)
- [ ] CompanyVisibilitySettings - 비즈니스 메서드 (can_view_*)

### Mixin 기능 확장
- [x] `__dict_json_fields__` 추가 - JSON 자동 파싱 지원

---

## Phase 1B: 매직 스트링 상수화 확장

### 완료된 파일 (24개)

#### Blueprints (19개)
- [x] `app/blueprints/auth.py`
- [x] `app/blueprints/main.py`
- [x] `app/blueprints/corporate.py`
- [x] `app/blueprints/personal.py`
- [x] `app/blueprints/profile/routes.py`
- [x] `app/blueprints/profile/decorators.py`
- [x] `app/blueprints/employees/list_routes.py`
- [x] `app/blueprints/employees/mutation_routes.py`
- [x] `app/blueprints/employees/detail_routes.py`
- [x] `app/blueprints/employees/files.py`
- [x] `app/blueprints/contracts.py`
- [x] `app/blueprints/account/routes.py`
- [x] `app/blueprints/mypage.py`
- [x] `app/blueprints/audit.py`
- [x] `app/blueprints/sync.py`
- [x] `app/blueprints/notifications.py`
- [x] `app/blueprints/corporate_settings_api.py`
- [x] `app/blueprints/admin/organization.py`
- [x] `app/utils/decorators.py`

#### Utils (4개)
- [x] `app/utils/context_processors.py`
- [x] `app/utils/contract_helpers.py`
- [x] `app/utils/personal_helpers.py`
- [x] `app/utils/tenant.py`

#### Services (1개)
- [x] `app/services/audit_service.py`

### 상수 모듈 생성 완료
- [x] `app/constants/__init__.py`
- [x] `app/constants/session_keys.py` - SessionKeys, AccountType, UserRole
- [x] `app/constants/messages.py` - FlashMessages, ErrorMessages

### 남은 파일 (템플릿 - Python 상수 적용 불가)
- [ ] `app/templates/corporate/users.html` (Jinja2 템플릿)
- [ ] `app/templates/dashboard/base_dashboard.html` (Jinja2 템플릿)
- [ ] `app/templates/dashboard/_quick_links_corporate.html` (Jinja2 템플릿)

> 참고: 템플릿 파일은 Python 상수를 직접 사용할 수 없음.
> context_processors를 통해 템플릿에 상수를 주입하는 방식으로 해결 가능

---

## Phase 2: Service 계층 표준화 (32개 Blueprint)

### 목표
- 모든 Blueprint에서 Repository 직접 접근 제거
- Service 계층 경유 강제

### 체크리스트

#### 직접 Repository 접근 패턴 검색
- [ ] `employee_repo.` 직접 호출 → `employee_service.` 변경
- [ ] `education_repo.` 직접 호출 → Service 경유
- [ ] `career_repo.` 직접 호출 → Service 경유
- [ ] 기타 Repository 직접 호출 제거

#### Blueprint별 점검
- [ ] employees Blueprint
- [ ] profile Blueprint
- [ ] contracts Blueprint
- [ ] organization Blueprint
- [ ] hr Blueprint
- [ ] reports Blueprint
- [ ] api Blueprint

---

## Phase 3: Dual Data Model 해결 (Profile 통합)

### 현재 상태 분석
- [ ] PersonalProfile 사용처 전체 파악
- [ ] Profile 사용처 전체 파악
- [ ] 데이터 스키마 차이점 분석

### 마이그레이션 계획
- [ ] PersonalProfile → Profile 데이터 매핑 정의
- [ ] 마이그레이션 스크립트 작성
- [ ] 테스트 환경에서 검증

### 코드 변경
- [ ] PersonalProfileRepository → ProfileRepository 통합
- [ ] PersonalService Profile 참조 변경
- [ ] 템플릿 참조 변경
- [ ] PersonalProfile 모델 Deprecation

### 검증
- [ ] 개인 계정 로그인 테스트
- [ ] 프로필 조회/수정 테스트
- [ ] 계약 관련 기능 테스트

---

## Phase 4: 테스트 코드 작성

### Unit Tests

#### Models
- [ ] `tests/unit/models/test_education.py`
- [ ] `tests/unit/models/test_career.py`
- [ ] `tests/unit/models/test_employee.py`
- [ ] `tests/unit/models/test_user.py`

#### Services
- [ ] `tests/unit/services/test_employee_service.py`
- [ ] `tests/unit/services/test_personal_service.py`
- [ ] `tests/unit/services/test_contract_service.py`

#### Utils
- [ ] `tests/unit/utils/test_decorators.py`
- [ ] `tests/unit/utils/test_tenant.py`

### Integration Tests

#### Repositories
- [ ] `tests/integration/test_education_repository.py`
- [ ] `tests/integration/test_employee_repository.py`
- [ ] `tests/integration/test_profile_repository.py`

#### API Endpoints
- [ ] `tests/integration/test_auth_api.py`
- [ ] `tests/integration/test_employee_api.py`
- [ ] `tests/integration/test_profile_api.py`

### E2E Tests
- [ ] `tests/e2e/test_login_flow.py`
- [ ] `tests/e2e/test_employee_crud.py`
- [ ] `tests/e2e/test_profile_management.py`

---

## Phase 5: SOLID 원칙 적용 (의존성 주입)

### 분석
- [ ] 현재 Service-Repository 결합 패턴 분석
- [ ] DI 프레임워크 선정 (Flask-Injector 등)

### 구현
- [ ] DI Container 설정
- [ ] Repository 인터페이스 정의
- [ ] Service 생성자 주입 패턴 적용
- [ ] Blueprint에서 Service 주입

### 검증
- [ ] 모든 기능 동작 확인
- [ ] 테스트 용이성 개선 확인

---

## 진행 상태 요약

| Phase | 항목 | 완료 | 전체 | 진행률 |
|-------|------|------|------|--------|
| 1A | Mixin 확장 | 24 | 40 | 60% |
| 1B | 상수화 확장 | 24 | 24 | 100% |
| 2 | Service 표준화 | 0 | 32 | 0% |
| 3 | Dual Model 해결 | 0 | 4 | 0% |
| 4 | 테스트 작성 | 0 | 20+ | 0% |
| 5 | SOLID 적용 | 0 | 5 | 0% |

> Phase 1B 완료: 모든 Python 파일에서 session.get() 상수화 완료
> 남은 3개 템플릿 파일은 context_processors로 해결 가능

---

## 기술적 결정 사항

### DictSerializableMixin 적용 기준
1. **적용 대상**: 단순한 to_dict/from_dict 패턴을 가진 모델
2. **보류 대상**:
   - 복잡한 비즈니스 메서드가 있는 모델 (User, Employee)
   - to_dict()에서 camelCase 키를 사용하는 모델 (ClassificationOption)
   - 파라미터가 있는 to_dict() 메서드 (Company.to_dict(include_stats))
   - 관계 객체를 직렬화하는 모델
   - 권한 검증 비즈니스 로직 (CompanyVisibilitySettings.can_view_*)

### Mixin 확장 기능
- `__dict_aliases__`: 필드 별칭 지원 (template 호환성)
- `__dict_excludes__`: 제외 필드 (password_hash 등)
- `__dict_computed__`: 계산 필드 (런타임 값)
- `__dict_camel_mapping__`: camelCase 입력 매핑
- `__dict_json_fields__`: JSON 자동 파싱 필드

---

## 다음 작업

1. **완료**: Phase 1A Mixin 적용 (적용 가능한 24개 모델 완료)
2. **완료**: Phase 1B - 상수화 확장 (24개 Python 파일 완료)
3. **다음**: Phase 2 - Service 계층 표준화 (Repository 직접 접근 제거)
4. **중기**: Phase 3 - Dual Data Model 해결 (Profile 통합)
5. **장기**: Phase 4, 5 - 테스트 작성 + SOLID 적용
