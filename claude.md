# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Last Updated**: 2026-01-16
> **Phase**: Domain Migration Phase 4 Complete (Attachment + Required Document)

## Project Overview

**HR Management System** - Flask 기반 인사 관리 웹 애플리케이션

- **계정 체계**: 개인(personal), 법인(corporate), 직원(employee_sub) 3가지 계정 타입
- **핵심 기능**: 직원 관리, 계약 관리, 프로필 관리, 조직 관리, AI 문서 처리, 첨부파일 관리

## Commands

```bash
# 개발 서버 실행 (포트 5200)
python run.py

# 환경변수 로드 필수 (.env 파일)
# DATABASE_URL=postgresql://... (필수)
# GEMINI_API_KEY=... (AI 기능용)

# 데이터베이스 마이그레이션
alembic upgrade head
alembic revision --autogenerate -m "migration message"
```

## Architecture

### Domain Structure (8개 도메인)
```
app/domains/
├── employee/                   # 직원 도메인 (~70개 파일)
│   ├── models/                 # 21개 모델 (Employee, Education, Career 등)
│   ├── repositories/           # 22개 Repository
│   ├── services/               # 7개 Service (Facade 패턴)
│   │   ├── employee_service.py           # Facade (외부 인터페이스)
│   │   ├── employee_core_service.py      # 조회/검색
│   │   ├── employee_relation_service.py  # 관계형 데이터
│   │   ├── profile_relation_service.py   # 관계형 SSOT
│   │   ├── employee_account_service.py   # 계정 관리
│   │   ├── inline_edit_service.py        # 인라인 편집
│   │   └── validation_service.py         # 섹션 검증
│   └── blueprints/             # employees_bp
├── contract/                   # 계약 도메인
│   ├── models/                 # PersonCorporateContract, DataSharingSettings, SyncLog
│   ├── repositories/           # PersonContractRepository
│   ├── services/               # Facade 패턴
│   │   ├── contract_service.py           # Facade (외부 인터페이스)
│   │   ├── contract_core_service.py      # 조회/검색
│   │   ├── contract_workflow_service.py  # 승인/거절/종료
│   │   ├── contract_settings_service.py  # 설정/로그
│   │   └── contract_filter_service.py    # 필터링
│   └── blueprints/             # contracts_bp
├── company/                    # 법인 도메인
│   ├── models/                 # 10개 모델 (Company, Organization 등)
│   ├── repositories/           # 9개 Repository
│   ├── services/               # 4개 Service
│   │   ├── company_service.py
│   │   ├── organization_service.py
│   │   ├── organization_type_config_service.py
│   │   └── corporate_settings_service.py
│   └── blueprints/             # corporate_bp, settings/*
├── user/                       # 사용자 도메인
│   ├── models/                 # User, CorporateAdminProfile, Notification, Profile
│   ├── repositories/           # 4개 Repository
│   ├── services/               # 5개 Service
│   │   ├── user_service.py
│   │   ├── personal_service.py
│   │   ├── notification_service.py
│   │   ├── user_employee_link_service.py
│   │   └── corporate_admin_profile_service.py
│   └── blueprints/             # auth_bp, mypage_bp, account/, personal/, profile/
├── platform/                   # 플랫폼 도메인
│   ├── models/                 # SystemSetting, AuditLog
│   ├── repositories/           # 2개 Repository
│   ├── services/               # 3개 Service
│   │   ├── platform_service.py
│   │   ├── audit_service.py
│   │   └── system_setting_service.py
│   └── blueprints/             # main, dashboard, companies, users, ai_test
├── sync/                       # 동기화 도메인
│   ├── repositories/           # SyncLogRepository
│   ├── services/               # Facade 패턴
│   │   ├── sync_service.py               # Facade (외부 인터페이스)
│   │   ├── sync_basic_service.py         # 기본 동기화
│   │   ├── sync_relation_service.py      # 관계형 동기화
│   │   └── termination_service.py        # 퇴사 처리
│   └── blueprints/             # sync_routes, contract_routes, termination_routes
├── attachment/                 # 첨부파일 도메인 (Phase 4 완료)
│   ├── models/                 # Attachment, RequiredDocument
│   ├── repositories/           # 2개 Repository
│   ├── services/               # 2개 Service
│   │   ├── attachment_service.py         # 파일 업로드/삭제/조회 (SSOT)
│   │   └── required_document_service.py  # 필수문서 관리
│   └── blueprints/             # /api/attachments/*, /api/required-documents/*
└── businesscard/               # 명함 도메인
    ├── repositories/           # BusinesscardRepository
    ├── services/               # BusinesscardService
    └── blueprints/             # /api/businesscard/*
```

### Import Pattern
```python
# 도메인에서 import (필수 - 유일한 경로)
from app.domains.employee.models import Employee
from app.domains.employee.services import employee_service
from app.domains.company.models import Company, Organization
from app.domains.contract.services import contract_service
from app.domains.user.models import User
from app.domains.platform.services import platform_service
from app.domains.attachment.services import attachment_service  # 첨부파일 SSOT
from app.domains.attachment.services import required_document_service  # 필수문서
from app.domains.businesscard.services import businesscard_service

# 공유 자원 import
from app.shared.repositories import BaseRepository
from app.shared.utils import decorators, transaction
from app.shared.constants import FieldOptions, ContractStatus
from app.shared.services.ai import ai_service
```

### Layer Structure (3-Tier + Repository Pattern)
```
app/
├── domains/              # 도메인별 패키지 (8개)
│   └── {domain}/
│       ├── models/       # SQLAlchemy 모델
│       ├── repositories/ # 데이터 접근 계층
│       ├── services/     # 비즈니스 로직
│       └── blueprints/   # URL 라우팅
├── shared/               # 공유 자원
│   ├── base/             # ServiceResult, GenericRelationCRUD, RelationUpdater
│   ├── constants/        # field_options, status, field_registry
│   ├── repositories/     # BaseRepository, mixins
│   ├── services/         # ai_service, file_storage, validation
│   ├── utils/            # decorators, transaction, helpers
│   ├── adapters/         # 외부 서비스 어댑터
│   └── models/           # 공유 믹스인
├── templates/            # Jinja2 템플릿
├── static/               # CSS, JS, 이미지
└── extensions.py         # Flask 확장
```

### Layer Call Rules
```
Blueprint → Service → Repository → Model
    ↓           ↓           ↓
 form_data   Dict/Model    Model
```

| 호출 방향 | 허용 | 금지 |
|----------|------|------|
| Blueprint → Service | O | - |
| Blueprint → Repository | X | 직접 호출 금지 |
| Service → Repository | O | - |
| Service → Service | O | 순환 참조 주의 |
| Repository → Model | O | - |

### Account Type System
| Type | Description | Session Keys |
|------|-------------|--------------|
| `personal` | 개인 계정 | user_id, personal_profile_id |
| `corporate` | 법인 관리자 | user_id, company_id, user_role |
| `employee_sub` | 법인 직원 | user_id, employee_id, company_id |

### Key Decorators (`app/shared/utils/decorators.py`)
```python
@login_required              # 로그인 필수
@corporate_login_required    # 법인 계정만
@personal_login_required     # 개인 계정만
@corporate_admin_required    # 법인 관리자만 (admin/manager)
@api_login_required          # API용 (JSON 응답)
```

## Key Patterns

### SSOT System (Single Source of Truth)

| 항목 | SSOT 위치 |
|------|----------|
| 트랜잭션 관리 | `app/shared/utils/transaction.py` |
| 관계형 데이터 CRUD | `app/domains/employee/services/profile_relation_service.py` |
| 폼 선택 옵션 | `app/shared/constants/field_options.py` |
| 필드 메타데이터 | `app/shared/constants/field_registry/` |
| 상태 상수 | `app/shared/constants/status.py` |
| CSS 변수 | `app/static/css/core/variables.css` |
| 첨부파일 관리 | `app/domains/attachment/services/attachment_service.py` |
| 필수문서 관리 | `app/domains/attachment/services/required_document_service.py` |
| 직원 관리 | `app/domains/employee/services/` (Facade) |
| 계약 관리 | `app/domains/contract/services/` (Facade) |
| 동기화 관리 | `app/domains/sync/services/` (Facade) |

### FieldOptions (`app/shared/constants/field_options.py`)
```python
from app.shared.constants.field_options import FieldOptions

# 옵션 조회
FieldOptions.GENDER  # [Option('남', '남성'), Option('여', '여성')]

# 레이블 변환 (레거시 코드 자동 처리)
FieldOptions.get_label_with_legacy(FieldOptions.GENDER, 'male')  # '남성'
```

### FieldRegistry (`app/shared/constants/field_registry/`)
```python
from app.shared.constants.field_registry import FieldRegistry

# 정렬된 필드명 목록
FieldRegistry.get_ordered_names('personal_basic', account_type='personal')

# 필드명 정규화
FieldRegistry.normalize_field_name('personal_basic', 'name_en')  # -> 'english_name'
```

### Repository Pattern (Generic Type)
```python
from app.shared.repositories import BaseRepository, BaseRelationRepository

# 기본 CRUD: BaseRepository[ModelType] 상속
class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

# 1:N 관계: BaseRelationRepository 상속
class EducationRepository(BaseRelationRepository):
    def __init__(self):
        super().__init__(Education)
```

### Transaction Management (SSOT)
```python
from app.shared.utils.transaction import atomic_transaction, transactional

# 컨텍스트 매니저 방식 (권장)
with atomic_transaction():
    service.delete_all(id, commit=False)
    service.add(id, data, commit=False)
    # 성공 시 자동 commit, 실패 시 자동 rollback

# 데코레이터 방식
@transactional
def update_all_relations(employee_id, form_data):
    service.delete_all(id, commit=False)
    service.add(id, data, commit=False)
```

### RelationUpdater Pattern
```python
# employees Blueprint
from app.domains.employee.blueprints.relation_updaters import (
    employee_relation_updater,
    update_family_data,
    update_education_data,
)
update_family_data(employee_id, form_data)

# personal Blueprint
from app.domains.user.blueprints.personal.relation_updaters import (
    profile_relation_updater,
    update_profile_relations,
)
update_profile_relations(profile_id, form_data)

# Service Layer (SSOT)
from app.domains.employee.services import profile_relation_service
profile_relation_service.add_education(owner_id, data, owner_type='employee', commit=False)
```

### Attachment Service Pattern (Phase 4)
```python
from app.domains.attachment.services import attachment_service

# 파일 업로드
attachment_service.upload_file(file, owner_type='employee', owner_id=1, category='document')

# 파일 목록 조회
attachments = attachment_service.get_by_owner('employee', employee_id)

# 카테고리별 조회
photo = attachment_service.get_one_by_category(employee_id, 'photo')

# 파일 삭제
attachment_service.delete(attachment_id)
```

### Required Document Service Pattern (Phase 4)
```python
from app.domains.attachment.services import required_document_service

# 계약 기반 필수문서 생성
required_document_service.create_from_contract(contract_id)

# 상태 확인
status = required_document_service.get_completion_status(contract_id)
# {'total': 5, 'completed': 3, 'pending': 2, 'completion_rate': 60.0}
```

## Blueprint Structure

### employee/blueprints/
```
├── __init__.py          # Blueprint 정의
├── routes.py            # 공통 라우트
├── list_routes.py       # 목록 조회
├── mutation_routes.py   # 생성/수정/삭제
├── detail_routes.py     # 상세 조회
├── section_api.py       # 섹션별 API
├── files.py             # 파일 업로드 API
├── file_handlers.py     # 파일 처리
├── form_extractors.py   # 폼 데이터 추출
├── relation_updaters.py # 관계 데이터 업데이트
└── helpers.py           # 헬퍼 함수
```

### company/blueprints/
```
├── corporate.py         # 법인 페이지
├── admin_organization.py # 조직 관리
└── settings/            # 법인 설정 API
    ├── classifications_api.py
    ├── documents_api.py
    ├── visibility_api.py
    ├── number_categories_api.py
    ├── organization_types_api.py
    └── settings_api.py
```

### user/blueprints/
```
├── auth.py              # 인증 (로그인/회원가입)
├── mypage.py            # 마이페이지
├── notifications.py     # 알림
├── account/             # 계정 설정
├── personal/            # 개인 프로필 (form_extractors, relation_updaters)
└── profile/             # 통합 프로필 뷰
```

## Frontend Structure
```
static/js/
├── core/              # field-registry.js, template-generator.js
├── components/        # data-table/, salary/, accordion.js, toast.js
└── pages/employee/    # validators.js, dynamic-sections.js, templates.js

static/css/
├── core/              # reset, theme, variables, responsive
├── layouts/           # header, sidebar, main-content
└── components/        # button, card, forms, table, modal
```

## Test Accounts

> 모든 테스트 계정의 비밀번호는 `test1234` 입니다.

| 타입 | Username | Email | 비고 |
|------|----------|-------|------|
| 법인 | admin_testa | admin@testcorp.co.kr | Company ID: 1 |
| 법인 | admin_global | admin@globalcorp.co.kr | Company ID: 2 |
| 개인 | personal_junhyuk.kim | junhyuk.kim@gmail.com | - |
| 직원 | emp_0001 ~ emp_0010 | *@testcorp.co.kr | 테스트기업 A |
| 직원 | emp_0021 ~ emp_0035 | *@globalcorp.co.kr | 글로벌기업 |

## Rules

### git
- 새 브랜치 요청시 "hrm-projekt-yymmddnn" 형식으로 생성

### Communication
- 한국어로 커뮤니케이션
- 이모지 사용 금지

### Code Standards
- 파일당 최대 500~800 라인 이내 유지
- DRY 원칙 준수, 코드 중복 금지
- snake_case (Python), camelCase (JavaScript) 일관성
- 하드코딩 금지 (상수화 또는 환경변수 사용)
- 인라인 스타일/스크립트 금지
- 승인하지 않은 작업 금지

### Development Principles

**DRY (Don't Repeat Yourself)**
- 동일 패턴 2회 이상 반복 시 함수/클래스로 추출
- 트랜잭션 래핑: `atomic_transaction()` 사용 (직접 try/except 금지)
- 폼 추출: `extract_*_list()` 함수 재사용

**SSOT (Single Source of Truth)**
- 각 기능의 SSOT 위치 확인 후 작업
- 중복 구현 금지

**SRP (Single Responsibility Principle)**
| 모듈 | 책임 |
|------|------|
| `form_extractors.py` | 폼 데이터 추출 (Dict 생성) |
| `relation_updaters.py` | 데이터 저장 (Service 호출) |
| `*_service.py` | 비즈니스 로직 (CRUD 조합) |
| `*_repository.py` | 데이터 접근 (단일 Model CRUD) |

**레이어 분리**
- Blueprint에서 Repository 직접 호출 금지
- Blueprint → Service → Repository 순서 준수

### Anti-Patterns (금지 패턴)

```python
# 1. 트랜잭션 직접 래핑 (금지)
try:
    repo.delete(id, commit=False)
    db.session.commit()
except:
    db.session.rollback()
    raise
# 올바른 방법:
with atomic_transaction():
    service.delete(id, commit=False)

# 2. Blueprint에서 Repository 직접 호출 (금지)
@bp.route('/update')
def update():
    education_repo.delete_by_employee_id(id)  # 금지!
# 올바른 방법:
    update_education_data(employee_id, request.form)

# 3. 하드코딩 색상/값 (금지)
color: #3b82f6;  # 금지!
# 올바른 방법:
color: var(--color-primary-500);

# 4. 첨부파일 직접 관리 (금지)
employee.attachments.append(...)  # 금지!
# 올바른 방법:
attachment_service.upload_file(file, owner_type='employee', owner_id=id)
```

### Principle Violation Checklist

코드 작성/수정 시 아래 항목 점검:

- [ ] **DRY**: 동일 패턴이 2곳 이상 중복되는가?
- [ ] **SSOT**: 해당 기능의 SSOT가 이미 존재하는가?
- [ ] **SRP**: 한 모듈이 여러 책임을 가지는가?
- [ ] **레이어 분리**: Blueprint에서 Repository를 직접 호출하는가?
- [ ] **트랜잭션**: `try/except/commit/rollback`을 직접 작성했는가?
- [ ] **일관성**: employees와 personal의 패턴이 다른가?
- [ ] **오버엔지니어링**: 불필요한 추상화나 과도한 계층을 추가하는가?

### Process
- git > plan > implement > test > debugging 순서
- 다른 코드에 영향 금지
- 변경 전 의도 파악이 어려우면 질문
- rules 위반 시 피드백 후 승인 받아 진행
