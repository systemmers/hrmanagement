# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HR Management System (인사카드 관리 시스템)** - Flask 기반 인사 관리 웹 애플리케이션

- **계정 체계**: 개인(personal), 법인(corporate), 직원(employee_sub) 3가지 계정 타입
- **핵심 기능**: 직원 관리, 계약 관리, 프로필 관리, 조직 관리, AI 문서 처리

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

### Layer Structure (3-Tier + Repository Pattern)
```
blueprints/       → Routes (URL 라우팅, 요청 처리)
services/         → Business Logic (비즈니스 로직)
    ├── base/         # relation_updater, history
    ├── ai/           # gemini, local_llama, document_ai
    └── profile_relation_service.py  # 관계형 데이터 CRUD (SSOT)
repositories/     → Data Access (BaseRepository 상속)
models/           → SQLAlchemy Models (to_dict, from_dict 필수)
constants/        → 상수 정의
    ├── field_options.py     # SSOT: 폼 선택 옵션 + 레거시 매핑
    └── field_registry/      # SSOT: 필드 순서/메타데이터
utils/            → decorators, helpers, transaction.py
```

### Service Layer (서비스 계층)
```
services/
├── Core Services (데이터 관리)
│   ├── employee_service.py          # 직원 CRUD
│   ├── personal_service.py          # 개인 프로필 CRUD
│   └── company_service.py           # 법인 CRUD
├── Business Logic
│   ├── contract_service.py          # 계약 관리
│   ├── user_service.py              # 사용자 관리
│   ├── organization_service.py      # 조직 구조
│   └── profile_relation_service.py  # 관계형 데이터 SSOT
├── Platform/Admin
│   └── platform_service.py          # 플랫폼 관리
└── AI/Integration
    ├── sync_service.py              # 데이터 동기화
    └── audit_service.py             # 감사 로깅
```

### Layer Call Rules (레이어 호출 규칙)
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

**레이어 분리 완료 상태** (Phase 24, 2025-12-28):
- Blueprint → Repository 직접 호출: 0건
- Blueprint → Model.query: decorators.py만 허용 (인증용)

### Account Type System
| Type | Description | Session Keys |
|------|-------------|--------------|
| `personal` | 개인 계정 | user_id, personal_profile_id |
| `corporate` | 법인 관리자 | user_id, company_id, user_role |
| `employee_sub` | 법인 직원 | user_id, employee_id, company_id |

### Key Decorators (`app/utils/decorators.py`)
```python
@login_required              # 로그인 필수
@corporate_login_required    # 법인 계정만
@personal_login_required     # 개인 계정만
@corporate_admin_required    # 법인 관리자만 (admin/manager)
@api_login_required          # API용 (JSON 응답)
```

## Key Patterns

### SSOT System (Single Source of Truth)

**FieldOptions** (`app/constants/field_options.py`)
- 폼 선택 옵션 중앙 관리 (Option namedtuple: value, label)
- 레거시 매핑 (`LEGACY_MAP`): 영문코드 → DB 저장값(한글) 변환
- 레이블 조회: `get_label()`, `get_label_with_legacy()`

```python
from app.constants.field_options import FieldOptions

# 옵션 조회
FieldOptions.GENDER  # [Option('남', '남성'), Option('여', '여성')]

# 레이블 변환 (레거시 코드 자동 처리)
FieldOptions.get_label_with_legacy(FieldOptions.GENDER, 'male')  # '남성'
```

**FieldRegistry** (`app/constants/field_registry/`)
- 필드 순서/메타데이터 중앙 관리
- 섹션별 필드 정의, 계정타입별 가시성
- 필드명 정규화 (별칭 → 정규 필드명)

```python
from app.constants.field_registry import FieldRegistry

# 정렬된 필드명 목록
FieldRegistry.get_ordered_names('personal_basic', account_type='personal')

# 필드명 정규화
FieldRegistry.normalize_field_name('personal_basic', 'name_en')  # -> 'english_name'
```

### Model Convention
```python
class SomeModel(db.Model):
    def to_dict(self):      # 직렬화 (camelCase 반환, 레이블 변환 포함)
        return {...}

    @staticmethod
    def from_dict(data):    # 역직렬화 (snake_case 변환)
        return SomeModel(...)
```

### Repository Pattern (Generic Type)
```python
# 기본 CRUD: BaseRepository[ModelType] 상속 (IDE 자동완성 지원)
class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

# 1:N 관계: BaseRelationRepository 상속
class EducationRepository(BaseRelationRepository):
    def __init__(self):
        super().__init__(Education)
```

### Transaction Management (트랜잭션 관리 SSOT)
```python
from app.utils.transaction import atomic_transaction, transactional

# 컨텍스트 매니저 방식 (권장)
with atomic_transaction():
    service.delete_all(id, commit=False)
    service.add(id, data, commit=False)
    # 모든 작업 성공 시 자동 commit, 실패 시 자동 rollback

# 데코레이터 방식
@transactional
def update_all_relations(employee_id, form_data):
    service.delete_all(id, commit=False)
    service.add(id, data, commit=False)
```

**트랜잭션 규칙**:
- 모든 트랜잭션 래핑은 `atomic_transaction()` 사용 (SSOT)
- `try/except/commit/rollback` 직접 작성 금지
- 블록 내 모든 호출은 `commit=False` 사용 필수

### RelationUpdater Pattern (관계형 데이터 업데이트)

**employees Blueprint**: `EmployeeRelationUpdater`
```python
from app.blueprints.employees.relation_updaters import (
    employee_relation_updater,
    update_family_data,      # 래퍼 함수 (기존 API 호환)
    update_education_data,
)

# 클래스 직접 사용
employee_relation_updater.update_family(employee_id, form_data)

# 래퍼 함수 사용 (권장)
update_family_data(employee_id, form_data)
```

**personal Blueprint**: `ProfileRelationUpdater`
```python
from app.blueprints.personal.relation_updaters import (
    profile_relation_updater,
    update_profile_relations,  # 전체 업데이트
)

profile_relation_updater.update_educations(profile_id, form_data)
update_profile_relations(profile_id, form_data)  # 전체
```

**Service Layer**: `profile_relation_service` (SSOT)
```python
from app.services.profile_relation_service import profile_relation_service

# owner_type: 'profile' (개인) | 'employee' (법인직원)
profile_relation_service.add_education(owner_id, data, owner_type='employee', commit=False)
profile_relation_service.delete_all_educations(owner_id, owner_type='employee', commit=False)
```

### Blueprint Module Split (employees 예시)
```
employees/
├── __init__.py          # Blueprint 정의
├── routes.py            # 공통 라우트
├── list_routes.py       # 목록 조회
├── mutation_routes.py   # 생성/수정/삭제
├── detail_routes.py     # 상세 조회
├── files.py             # 파일 업로드 API (8개 라우트)
├── form_extractors.py   # 폼 데이터 추출 (FieldRegistry 기반)
├── relation_updaters.py # 관계 데이터 업데이트 (RelationDataConfig)
└── helpers.py           # 헬퍼 함수

admin/
├── __init__.py          # Blueprint 정의
├── organization.py      # 조직 관리
└── audit.py             # 감사 대시보드 (1개 UI 라우트)
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
- 뉴브랜치 요청시 "hrm-projekt-yymmddnn" 형식으로 생성


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

### Development Principles (개발 원칙)

**DRY (Don't Repeat Yourself)**
- 동일 패턴 2회 이상 반복 시 함수/클래스로 추출
- 트랜잭션 래핑: `atomic_transaction()` 사용 (직접 try/except 금지)
- 폼 추출: `extract_*_list()` 함수 재사용

**SSOT (Single Source of Truth)**
| 항목 | SSOT 위치 |
|------|----------|
| 트랜잭션 관리 | `app/utils/transaction.py` |
| 관계형 데이터 CRUD | `app/services/profile_relation_service.py` |
| 폼 선택 옵션 | `app/constants/field_options.py` |
| 필드 메타데이터 | `app/constants/field_registry/` |
| CSS 변수 | `app/static/css/core/variables.css` |
| 법인 데이터 관리 | `app/services/company_service.py` |
| 플랫폼 관리 | `app/services/platform_service.py` |
| 계약 관리 | `app/services/contract_service.py` |

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
- employees와 personal Blueprint 패턴 일관성 유지

### Anti-Patterns (금지 패턴)

```python
# 1. 트랜잭션 직접 래핑 (금지)
try:
    repo.delete(id, commit=False)
    repo.create(data, commit=False)
    db.session.commit()
except:
    db.session.rollback()
    raise

# 올바른 방법:
with atomic_transaction():
    service.delete(id, commit=False)
    service.add(data, commit=False)

# 2. Blueprint에서 Repository 직접 호출 (금지)
@bp.route('/update')
def update():
    education_repo.delete_by_employee_id(id)  # 금지!

# 올바른 방법:
@bp.route('/update')
def update():
    update_education_data(employee_id, request.form)  # Service 경유

# 3. 동일 패턴 복사-붙여넣기 (금지)
def update_family():
    try: ... except: db.session.rollback()
def update_education():
    try: ... except: db.session.rollback()  # 중복!

# 올바른 방법:
def update_family():
    with atomic_transaction(): ...
def update_education():
    with atomic_transaction(): ...  # 공통 패턴 재사용

# 4. 하드코딩 색상/값 (금지)
color: #3b82f6;  # 금지!

# 올바른 방법:
color: var(--color-primary-500);
```

### Principle Violation Checklist (원칙 위반 점검)

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
