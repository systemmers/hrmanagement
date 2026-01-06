# Domain Migration Plan (도메인 마이그레이션 계획)

> 작성일: 2026-01-06
> 현재 Phase: 1 완료 (Employee 도메인)

---

## 목차
1. [현황 요약](#1-현황-요약)
2. [마이그레이션 원칙](#2-마이그레이션-원칙)
3. [Phase별 상세 계획](#3-phase별-상세-계획)
4. [레거시 파일 삭제 계획](#4-레거시-파일-삭제-계획)
5. [검증 체크리스트](#5-검증-체크리스트)

---

## 1. 현황 요약

### 1.1 전체 통계

| 도메인 | Models | Repos | Services | Blueprints | 완료율 |
|--------|--------|-------|----------|------------|--------|
| Employee | 25/25 | 24/24 | 6/6 | 9/9 | **100%** |
| Contract | 0/3 | 1/1 | 4/5 | 1/2 | **40%** |
| Company | 0/10 | 8/8 | 3/3 | 0/7 | **35%** |
| User | 0/4 | 4/4 | 5/5 | 0/8 | **40%** |
| Platform | 0/2 | 2/2 | 3/3 | 0/5 | **50%** |
| Sync | 0/1 | 1/1 | 1/4 | 0/4 | **20%** |

### 1.2 레거시 파일 현황

```
app/
├── models/           18개 파일 (삭제 대상)
├── repositories/     18개 파일 (삭제 대상)
├── services/         20개 파일 (삭제 대상)
└── blueprints/       38개 파일 (삭제 대상)
```

---

## 2. 마이그레이션 원칙

### 2.1 레이어별 마이그레이션 순서

```
1. Models      → 도메인 models/ 폴더로 이동
2. Repositories → 도메인 repositories/ 폴더로 이동
3. Services    → 도메인 services/ 폴더로 이동
4. Blueprints  → 도메인 blueprints/ 폴더로 이동
5. __init__.py → lazy import 설정 (하위호환성)
6. 테스트 검증 → 전체 기능 테스트
7. 레거시 삭제 → 기존 파일 제거
```

### 2.2 하위호환성 전략

```python
# app/models/__init__.py - lazy import 패턴
def __getattr__(name):
    if name == 'Company':
        from app.domains.company.models import Company
        return Company
    raise AttributeError(f"module has no attribute '{name}'")
```

### 2.3 삭제 조건

레거시 파일 삭제 전 필수 조건:
1. 도메인 모듈에 동일 기능 구현 완료
2. `__init__.py`에 lazy import 설정 완료
3. 모든 import 경로 정상 동작 확인
4. 테스트 통과 (수동/자동)

---

## 3. Phase별 상세 계획

### Phase 2: Contract 도메인

**목표**: 계약 관련 모든 모듈을 `app/domains/contract/`로 통합

#### 3.2.1 Models 마이그레이션

| 레거시 파일 | 도메인 대상 | 모델 목록 |
|------------|------------|----------|
| `app/models/person_contract.py` | `contract/models/` | PersonCorporateContract, DataSharingSettings, SyncLog |

**작업 내용**:
```
app/domains/contract/models/
├── __init__.py                    # 신규
├── person_contract.py             # 이동
├── data_sharing_settings.py       # 분리
└── sync_log.py                    # 분리 → sync 도메인으로 이동
```

#### 3.2.2 Services 마이그레이션

| 레거시 파일 | 도메인 대상 | 상태 |
|------------|------------|------|
| `app/services/contract_service.py` | `contract/services/` | 이동 필요 |
| `app/services/contract_filter_service.py` | `contract/services/` | 이미 존재 (중복) |

#### 3.2.3 Blueprints 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/blueprints/contracts.py` | `contract/blueprints/contracts.py` |

**현재 상태**: 이미 `app/domains/contract/blueprints/contracts.py` 존재 - 중복 확인 필요

#### 3.2.4 삭제 대상

Phase 2 완료 후 삭제:
```
DELETE app/models/person_contract.py
DELETE app/services/contract_service.py
DELETE app/services/contract_filter_service.py
DELETE app/blueprints/contracts.py
```

---

### Phase 3: Company 도메인

**목표**: 법인 관련 모든 모듈을 `app/domains/company/`로 통합

#### 3.3.1 Models 마이그레이션

| 레거시 파일 | 도메인 대상 | 비고 |
|------------|------------|------|
| `app/models/company.py` | `company/models/company.py` | |
| `app/models/organization.py` | `company/models/organization.py` | |
| `app/models/classification_option.py` | `company/models/classification_option.py` | |
| `app/models/company_settings.py` | `company/models/company_settings.py` | |
| `app/models/company_document.py` | `company/models/company_document.py` | |
| `app/models/company_visibility_settings.py` | `company/models/company_visibility_settings.py` | |
| `app/models/number_category.py` | `company/models/number_category.py` | |
| `app/models/number_registry.py` | `company/models/number_registry.py` | |
| `app/models/ip_range.py` | `company/models/ip_range.py` | |
| `app/models/ip_assignment.py` | `company/models/ip_assignment.py` | |

**도메인 구조**:
```
app/domains/company/models/
├── __init__.py
├── company.py
├── organization.py
├── classification_option.py
├── company_settings.py
├── company_document.py
├── company_visibility_settings.py
├── number_category.py
├── number_registry.py
├── ip_range.py
└── ip_assignment.py
```

#### 3.3.2 Repositories 마이그레이션

**현재 상태**: 이미 도메인에 존재 (8개)
- 레거시 중복 파일 삭제만 필요

#### 3.3.3 Services 마이그레이션

**현재 상태**: 이미 도메인에 존재 (3개)
- 레거시 중복 파일 삭제만 필요

#### 3.3.4 Blueprints 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/blueprints/corporate.py` | `company/blueprints/corporate.py` |
| `app/blueprints/corporate_settings/__init__.py` | `company/blueprints/settings/__init__.py` |
| `app/blueprints/corporate_settings/classifications_api.py` | `company/blueprints/settings/classifications_api.py` |
| `app/blueprints/corporate_settings/documents_api.py` | `company/blueprints/settings/documents_api.py` |
| `app/blueprints/corporate_settings/helpers.py` | `company/blueprints/settings/helpers.py` |
| `app/blueprints/corporate_settings/number_categories_api.py` | `company/blueprints/settings/number_categories_api.py` |
| `app/blueprints/corporate_settings/settings_api.py` | `company/blueprints/settings/settings_api.py` |
| `app/blueprints/corporate_settings/visibility_api.py` | `company/blueprints/settings/visibility_api.py` |

**도메인 구조**:
```
app/domains/company/blueprints/
├── __init__.py
├── corporate.py
└── settings/
    ├── __init__.py
    ├── classifications_api.py
    ├── documents_api.py
    ├── helpers.py
    ├── number_categories_api.py
    ├── settings_api.py
    └── visibility_api.py
```

#### 3.3.5 삭제 대상

Phase 3 완료 후 삭제:
```
DELETE app/models/company.py
DELETE app/models/organization.py
DELETE app/models/classification_option.py
DELETE app/models/company_settings.py
DELETE app/models/company_document.py
DELETE app/models/company_visibility_settings.py
DELETE app/models/number_category.py
DELETE app/models/number_registry.py
DELETE app/models/ip_range.py
DELETE app/models/ip_assignment.py
DELETE app/repositories/classification_repository.py
DELETE app/repositories/company_document_repository.py
DELETE app/repositories/company_repository.py
DELETE app/repositories/company_settings_repository.py
DELETE app/repositories/company_visibility_repository.py
DELETE app/repositories/number_category_repository.py
DELETE app/repositories/organization_repository.py
DELETE app/repositories/data_sharing_settings_repository.py
DELETE app/services/company_service.py
DELETE app/services/organization_service.py
DELETE app/services/corporate_settings_service.py
DELETE app/blueprints/corporate.py
DELETE app/blueprints/corporate_settings/ (전체 디렉토리)
```

---

### Phase 4: User 도메인

**목표**: 사용자/인증 관련 모든 모듈을 `app/domains/user/`로 통합

#### 3.4.1 Models 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/models/user.py` | `user/models/user.py` |
| `app/models/corporate_admin_profile.py` | `user/models/corporate_admin_profile.py` |
| `app/models/notification.py` | `user/models/notification.py` |
| `app/models/personal_profile.py` | `user/models/personal_profile.py` |

**도메인 구조**:
```
app/domains/user/models/
├── __init__.py
├── user.py
├── corporate_admin_profile.py
├── notification.py
└── personal_profile.py
```

#### 3.4.2 Repositories/Services

**현재 상태**: 이미 도메인에 존재
- 레거시 중복 파일 삭제만 필요

#### 3.4.3 Blueprints 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/blueprints/auth.py` | `user/blueprints/auth.py` |
| `app/blueprints/account/` | `user/blueprints/account/` |
| `app/blueprints/personal/` | `user/blueprints/personal/` |
| `app/blueprints/profile/` | `user/blueprints/profile/` |
| `app/blueprints/mypage.py` | `user/blueprints/mypage.py` |
| `app/blueprints/notifications.py` | `user/blueprints/notifications.py` |

**도메인 구조**:
```
app/domains/user/blueprints/
├── __init__.py
├── auth.py
├── mypage.py
├── notifications.py
├── account/
│   ├── __init__.py
│   ├── helpers.py
│   └── routes.py
├── personal/
│   ├── __init__.py
│   ├── form_extractors.py
│   ├── relation_updaters.py
│   └── routes.py
└── profile/
    ├── __init__.py
    ├── decorators.py
    └── routes.py
```

#### 3.4.4 삭제 대상

Phase 4 완료 후 삭제:
```
DELETE app/models/user.py
DELETE app/models/corporate_admin_profile.py
DELETE app/models/notification.py
DELETE app/models/personal_profile.py
DELETE app/repositories/corporate_admin_profile_repository.py
DELETE app/repositories/notification_repository.py
DELETE app/repositories/personal_profile_repository.py
DELETE app/repositories/user_repository.py
DELETE app/services/corporate_admin_profile_service.py
DELETE app/services/notification_service.py
DELETE app/services/personal_service.py
DELETE app/services/user_service.py
DELETE app/services/user_employee_link_service.py
DELETE app/blueprints/auth.py
DELETE app/blueprints/account/ (전체 디렉토리)
DELETE app/blueprints/personal/ (전체 디렉토리)
DELETE app/blueprints/profile/ (전체 디렉토리)
DELETE app/blueprints/mypage.py
DELETE app/blueprints/notifications.py
```

---

### Phase 5: Platform 도메인

**목표**: 플랫폼 관리 모듈을 `app/domains/platform/`으로 통합

#### 3.5.1 Models 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/models/system_setting.py` | `platform/models/system_setting.py` |
| `app/models/audit_log.py` | `platform/models/audit_log.py` |
| `app/models/project.py` | `platform/models/project.py` |

**도메인 구조**:
```
app/domains/platform/models/
├── __init__.py
├── system_setting.py
├── audit_log.py
└── project.py
```

#### 3.5.2 Blueprints 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/blueprints/platform/__init__.py` | `platform/blueprints/__init__.py` |
| `app/blueprints/platform/companies.py` | `platform/blueprints/companies.py` |
| `app/blueprints/platform/dashboard.py` | `platform/blueprints/dashboard.py` |
| `app/blueprints/platform/settings.py` | `platform/blueprints/settings.py` |
| `app/blueprints/platform/users.py` | `platform/blueprints/users.py` |
| `app/blueprints/admin/audit.py` | `platform/blueprints/audit.py` |
| `app/blueprints/admin/organization.py` | → Company 도메인 |
| `app/blueprints/audit.py` | `platform/blueprints/audit_api.py` |

**도메인 구조**:
```
app/domains/platform/blueprints/
├── __init__.py
├── companies.py
├── dashboard.py
├── settings.py
├── users.py
├── audit.py
└── audit_api.py
```

#### 3.5.3 삭제 대상

Phase 5 완료 후 삭제:
```
DELETE app/models/system_setting.py
DELETE app/models/audit_log.py
DELETE app/models/project.py
DELETE app/repositories/audit_log_repository.py
DELETE app/repositories/system_setting_repository.py
DELETE app/repositories/project_repository.py
DELETE app/services/audit_service.py
DELETE app/services/platform_service.py
DELETE app/services/system_setting_service.py
DELETE app/blueprints/platform/ (전체 디렉토리)
DELETE app/blueprints/admin/audit.py
DELETE app/blueprints/audit.py
```

---

### Phase 6: Sync 도메인

**목표**: 동기화 관련 모듈을 `app/domains/sync/`로 통합

#### 3.6.1 Models/Services 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| (SyncLog from person_contract.py) | `sync/models/sync_log.py` |
| `app/services/sync_service.py` | `sync/services/sync_service.py` |
| `app/services/sync_basic_service.py` | `sync/services/sync_basic_service.py` |
| `app/services/sync_relation_service.py` | `sync/services/sync_relation_service.py` |
| `app/services/termination_service.py` | 이미 존재 |

#### 3.6.2 Blueprints 마이그레이션

| 레거시 파일 | 도메인 대상 |
|------------|------------|
| `app/blueprints/sync/__init__.py` | `sync/blueprints/__init__.py` |
| `app/blueprints/sync/contract_routes.py` | `sync/blueprints/contract_routes.py` |
| `app/blueprints/sync/sync_routes.py` | `sync/blueprints/sync_routes.py` |
| `app/blueprints/sync/termination_routes.py` | `sync/blueprints/termination_routes.py` |

**도메인 구조**:
```
app/domains/sync/
├── models/
│   ├── __init__.py
│   └── sync_log.py
├── repositories/
│   ├── __init__.py
│   └── sync_log_repository.py
├── services/
│   ├── __init__.py
│   ├── sync_service.py
│   ├── sync_basic_service.py
│   ├── sync_relation_service.py
│   └── termination_service.py
└── blueprints/
    ├── __init__.py
    ├── contract_routes.py
    ├── sync_routes.py
    └── termination_routes.py
```

#### 3.6.3 삭제 대상

Phase 6 완료 후 삭제:
```
DELETE app/repositories/sync_log_repository.py
DELETE app/services/sync_service.py
DELETE app/services/sync_basic_service.py
DELETE app/services/sync_relation_service.py
DELETE app/services/termination_service.py
DELETE app/blueprints/sync/ (전체 디렉토리)
```

---

### Phase 7: 정리 및 최종화

**목표**: 레거시 디렉토리 정리 및 최종 구조 확정

#### 3.7.1 공통 모듈 정리

삭제하지 않을 파일 (공용):
```
KEEP app/repositories/base_repository.py  → app/shared/base_repository.py로 이동
KEEP app/services/ai_service.py           → app/adapters/ai/로 이동
KEEP app/services/file_storage_service.py → app/shared/services/로 이동
KEEP app/services/event_listeners.py      → app/shared/services/로 이동
```

#### 3.7.2 Blueprints 공통

삭제하지 않을 파일:
```
KEEP app/blueprints/__init__.py   → Blueprint 등록 유지
KEEP app/blueprints/main.py       → 메인 라우트
KEEP app/blueprints/api.py        → API 공통
KEEP app/blueprints/ai_test.py    → 테스트용 (선택적 삭제)
KEEP app/blueprints/admin/__init__.py → Admin 그룹
```

#### 3.7.3 __init__.py 파일 업데이트

모든 Phase 완료 후 `__init__.py` 파일 정리:
```python
# app/models/__init__.py - 최종 형태
from app.domains.employee.models import *
from app.domains.contract.models import *
from app.domains.company.models import *
from app.domains.user.models import *
from app.domains.platform.models import *
from app.domains.sync.models import *
```

---

## 4. 레거시 파일 삭제 계획

### 4.1 삭제 순서 (Phase 완료 후)

#### Phase 2 완료 후 (Contract)
```bash
# Models
rm app/models/person_contract.py

# Services (중복 확인 후)
rm app/services/contract_service.py
rm app/services/contract_filter_service.py

# Blueprints
rm app/blueprints/contracts.py
```

#### Phase 3 완료 후 (Company)
```bash
# Models (10개)
rm app/models/company.py
rm app/models/organization.py
rm app/models/classification_option.py
rm app/models/company_settings.py
rm app/models/company_document.py
rm app/models/company_visibility_settings.py
rm app/models/number_category.py
rm app/models/number_registry.py
rm app/models/ip_range.py
rm app/models/ip_assignment.py

# Repositories (8개)
rm app/repositories/classification_repository.py
rm app/repositories/company_document_repository.py
rm app/repositories/company_repository.py
rm app/repositories/company_settings_repository.py
rm app/repositories/company_visibility_repository.py
rm app/repositories/number_category_repository.py
rm app/repositories/organization_repository.py
rm app/repositories/data_sharing_settings_repository.py

# Services (3개)
rm app/services/company_service.py
rm app/services/organization_service.py
rm app/services/corporate_settings_service.py

# Blueprints (디렉토리)
rm app/blueprints/corporate.py
rm -rf app/blueprints/corporate_settings/
```

#### Phase 4 완료 후 (User)
```bash
# Models (4개)
rm app/models/user.py
rm app/models/corporate_admin_profile.py
rm app/models/notification.py
rm app/models/personal_profile.py

# Repositories (4개)
rm app/repositories/corporate_admin_profile_repository.py
rm app/repositories/notification_repository.py
rm app/repositories/personal_profile_repository.py
rm app/repositories/user_repository.py

# Services (5개)
rm app/services/corporate_admin_profile_service.py
rm app/services/notification_service.py
rm app/services/personal_service.py
rm app/services/user_service.py
rm app/services/user_employee_link_service.py

# Blueprints (디렉토리)
rm app/blueprints/auth.py
rm -rf app/blueprints/account/
rm -rf app/blueprints/personal/
rm -rf app/blueprints/profile/
rm app/blueprints/mypage.py
rm app/blueprints/notifications.py
```

#### Phase 5 완료 후 (Platform)
```bash
# Models (3개)
rm app/models/system_setting.py
rm app/models/audit_log.py
rm app/models/project.py

# Repositories (3개)
rm app/repositories/audit_log_repository.py
rm app/repositories/system_setting_repository.py
rm app/repositories/project_repository.py

# Services (3개)
rm app/services/audit_service.py
rm app/services/platform_service.py
rm app/services/system_setting_service.py

# Blueprints (디렉토리)
rm -rf app/blueprints/platform/
rm app/blueprints/admin/audit.py
rm app/blueprints/audit.py
```

#### Phase 6 완료 후 (Sync)
```bash
# Repositories (1개)
rm app/repositories/sync_log_repository.py

# Services (4개)
rm app/services/sync_service.py
rm app/services/sync_basic_service.py
rm app/services/sync_relation_service.py
rm app/services/termination_service.py

# Blueprints (디렉토리)
rm -rf app/blueprints/sync/
```

#### Phase 7 완료 후 (최종 정리)
```bash
# 공용 모듈 이동 후 삭제
mv app/repositories/base_repository.py app/shared/
rm app/repositories/base_repository.py

# 빈 디렉토리 정리
# (models, repositories, services 디렉토리에 __init__.py만 남김)
```

### 4.2 삭제 전 체크리스트

각 파일 삭제 전 확인사항:

- [ ] 도메인 모듈에 동일 기능 구현 완료
- [ ] `__init__.py`에 re-export 설정 완료
- [ ] import 경로 테스트 통과
- [ ] 애플리케이션 시작 정상
- [ ] 주요 기능 수동 테스트 통과

### 4.3 삭제 통계 요약

| Phase | Models | Repos | Services | Blueprints | 총 삭제 |
|-------|--------|-------|----------|------------|---------|
| 2 | 1 | 0 | 2 | 1 | **4** |
| 3 | 10 | 8 | 3 | 8 | **29** |
| 4 | 4 | 4 | 5 | 10 | **23** |
| 5 | 3 | 3 | 3 | 6 | **15** |
| 6 | 0 | 1 | 4 | 4 | **9** |
| 7 | 0 | 1 | 2 | 0 | **3** |
| **Total** | **18** | **17** | **19** | **29** | **83** |

---

## 5. 검증 체크리스트

### 5.1 Phase별 검증

#### 마이그레이션 완료 검증
```bash
# 1. 서버 시작 테스트
python run.py

# 2. Import 테스트
python -c "from app.domains.[domain].models import *"
python -c "from app.models import [Model]"  # 하위호환성

# 3. 주요 기능 테스트
# - 로그인/로그아웃
# - 직원 목록/상세
# - 계약 목록
# - 법인 설정
```

#### 레거시 삭제 후 검증
```bash
# 1. 삭제된 파일 import 시도 (에러 없이 도메인에서 가져와야 함)
python -c "from app.models.company import Company"  # 동작해야 함

# 2. grep으로 직접 import 확인
grep -r "from app.models.company import" app/
# → app/domains/로 리다이렉트되어야 함
```

### 5.2 최종 구조 검증

마이그레이션 완료 후 예상 구조:
```
app/
├── domains/              # 모든 도메인 코드
│   ├── employee/         # 100% 완료
│   ├── contract/         # 100% 완료
│   ├── company/          # 100% 완료
│   ├── user/             # 100% 완료
│   ├── platform/         # 100% 완료
│   └── sync/             # 100% 완료
├── shared/               # 공용 모듈
│   ├── base_repository.py
│   └── services/
├── adapters/             # 외부 연동
│   └── ai/
├── constants/            # 상수 정의
├── utils/                # 유틸리티
├── models/__init__.py    # re-export only
├── repositories/__init__.py  # re-export only
├── services/__init__.py  # re-export only
└── blueprints/           # 공용 라우트만
    ├── __init__.py
    ├── main.py
    └── api.py
```

---

## 변경 이력

| 날짜 | Phase | 작업 내용 |
|------|-------|----------|
| 2025-01-06 | 1 | Employee 도메인 마이그레이션 완료 |
| - | 2 | Contract 도메인 (예정) |
| - | 3 | Company 도메인 (예정) |
| - | 4 | User 도메인 (예정) |
| - | 5 | Platform 도메인 (예정) |
| - | 6 | Sync 도메인 (예정) |
| - | 7 | 최종 정리 (예정) |
