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
    └── ai/           # gemini, local_llama, document_ai
repositories/     → Data Access (BaseRepository 상속)
models/           → SQLAlchemy Models (to_dict, from_dict 필수)
constants/        → 상수 정의
    ├── field_options.py     # SSOT: 폼 선택 옵션 + 레거시 매핑
    └── field_registry/      # SSOT: 필드 순서/메타데이터
utils/            → decorators, helpers
```

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

### RelationDataUpdater (관계형 데이터 공통 로직)
```python
from app.services.base.relation_updater import RelationDataUpdater, RelationDataConfig

config = RelationDataConfig(
    model_class=Education,
    repository=education_repo,
    form_prefix='education_',
    required_field='school_name',
    field_mapping={'school_type': 'school_type', ...}
)

updater = RelationDataUpdater()
updater.update(employee_id, form_data, config)
```

### Blueprint Module Split (employees 예시)
```
employees/
├── __init__.py          # Blueprint 정의
├── routes.py            # 공통 라우트
├── list_routes.py       # 목록 조회
├── mutation_routes.py   # 생성/수정/삭제
├── detail_routes.py     # 상세 조회
├── form_extractors.py   # 폼 데이터 추출 (FieldRegistry 기반)
├── relation_updaters.py # 관계 데이터 업데이트 (RelationDataConfig)
└── helpers.py           # 헬퍼 함수
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

### Process
- git > plan > implement > test > debugging 순서
- 지시한 것만 진행, 다른 코드에 영향 금지
- 변경 전 의도 파악이 어려우면 질문
- rules 위반 시 피드백 후 승인 받아 진행
