# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HR Management System (인사카드 관리 시스템)** - Flask 기반 인사 관리 웹 애플리케이션

- **계정 체계**: 개인(personal), 법인(corporate), 직원(employee_sub) 3가지 계정 타입
- **핵심 기능**: 직원 관리, 계약 관리, 프로필 관리, 조직 관리, AI 문서 처리
- **규모**: 62개 모델, 45개 Repository, 23개 Service, 17개 Blueprint

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
    ├── employees/    # 모듈 분할된 CRUD
    ├── profile/      # 통합 프로필 (개인/법인)
    ├── account/      # 계정 설정
    ├── admin/        # 관리자 기능
    └── [domain].py   # 도메인별 라우트

services/         → Business Logic (비즈니스 로직)
    ├── base/         # 기본 서비스 (relation_updater, history)
    └── ai/           # AI 제공자 (gemini, local_llama, document_ai)

repositories/     → Data Access (BaseRepository 상속)
models/           → SQLAlchemy Models (to_dict, from_dict 필수)
utils/            → 유틸리티 (decorators, helpers)
constants/        → 상수 정의 (messages, session_keys)
```

### Account Type System
| Type | Description | Session Keys |
|------|-------------|--------------|
| `personal` | 개인 계정 | user_id, personal_profile_id |
| `corporate` | 법인 관리자 | user_id, company_id, user_role |
| `employee_sub` | 법인 직원 | user_id, employee_id, company_id |

### Blueprint Modules
| Blueprint | 경로 | 설명 |
|-----------|------|------|
| auth_bp | /auth/* | 로그인, 회원가입, 비밀번호 |
| corporate_bp | /corporate/* | 법인 계정 관리 |
| personal_bp | /personal/* | 개인 계정 관리 |
| employees_bp | /employees/* | 직원 CRUD (list, mutation, detail) |
| profile_bp | /profile/* | 통합 프로필 (법인/개인) |
| account_bp | /account/* | 계정 설정 (비밀번호, 탈퇴) |
| contracts_bp | /contracts/* | 계약 관리 |
| admin_bp | /admin/* | 관리자 (감사, 조직, 분류) |
| sync_bp | /sync/* | 데이터 동기화 |
| api_bp | /api/* | REST API |
| ai_test_bp | /ai-test/* | AI 테스트 |

### Key Decorators (`app/utils/decorators.py`)
```python
@login_required              # 로그인 필수
@corporate_login_required    # 법인 계정만
@personal_login_required     # 개인 계정만
@corporate_admin_required    # 법인 관리자만 (admin/manager)
@api_login_required          # API용 (JSON 응답)
```

### Frontend Structure
```
static/js/
├── components/        # 재사용 UI
│   ├── data-table/    # 고급 테이블 (column, filter, pagination, selection)
│   ├── salary/        # 급여 계산기 (calculator, allowance-manager)
│   ├── accordion.js, toast.js, form-validator.js, tree-selector.js
│   └── file-upload.js, section-nav.js, notification-dropdown.js
├── pages/             # 페이지별 로직
│   ├── employee/      # 모듈화 (validators, dynamic-sections, helpers)
│   ├── dashboard.js, contracts.js, corporate-settings.js
│   └── auth.js, admin.js, classification-options.js
└── app.js             # 메인 스크립트

static/css/
├── core/              # 기본 (reset, theme, variables, responsive)
├── layouts/           # 레이아웃 (header, sidebar, main-content)
├── components/        # 컴포넌트 (button, card, forms, table, modal)
└── pages/             # 페이지 특정 스타일
```

### Template Structure
```
templates/
├── base.html, base_public.html, base_error.html
├── auth/, account/, corporate/, personal/
├── employees/, contracts/, dashboard/, admin/
├── macros/            # Jinja2 매크로
│   ├── _form_controls.html   # 폼 입력 컴포넌트
│   ├── _navigation.html      # 네비게이션
│   ├── _alerts.html, _cards.html, _accordion.html
│   └── _info_display.html, _contracts.html
└── components/navigation/    # 사이드바
```

## Key Patterns

### Model Convention
```python
class SomeModel(db.Model):
    def to_dict(self):      # 직렬화 (camelCase 반환)
        return {...}

    @staticmethod
    def from_dict(data):    # 역직렬화 (snake_case 변환)
        return SomeModel(...)
```

### Repository Pattern
```python
# 기본 CRUD: BaseRepository 상속
class EmployeeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Employee)

# 1:N 관계: BaseRelationRepository 상속
class EducationRepository(BaseRelationRepository):
    def __init__(self):
        super().__init__(Education)

# 1:1 관계: BaseOneToOneRepository 상속
class SalaryRepository(BaseOneToOneRepository):
    ...
```

### Service Layer
```python
# services/ 에서 비즈니스 로직 처리
# Repository를 주입받아 데이터 접근

class EmployeeService:
    def __init__(self, employee_repo, profile_repo):
        self.employee_repo = employee_repo
        self.profile_repo = profile_repo
```

### Blueprint Module Split (employees 예시)
```
employees/
├── __init__.py          # Blueprint 정의
├── routes.py            # 공통 라우트
├── list_routes.py       # 목록 조회
├── mutation_routes.py   # 생성/수정/삭제
├── detail_routes.py     # 상세 조회
├── helpers.py           # 헬퍼 함수
├── form_extractors.py   # 폼 데이터 추출
├── relation_updaters.py # 관계 데이터 업데이트
└── files.py, file_handlers.py  # 파일 처리
```

## AI Services
```
services/ai/
├── base.py              # 기본 AI 제공자 인터페이스
├── gemini_provider.py   # Google Gemini API
├── local_llama_provider.py  # Local LLaMA
├── document_ai_provider.py  # Google Document AI
├── vision_ocr.py        # 비전/OCR 처리
└── prompts.py           # AI 프롬프트 템플릿
```

## Test Accounts

> 모든 테스트 계정의 비밀번호는 `test1234` 입니다.

### 법인계정 (corporate)
| 법인 | Username | Email | Company ID |
|------|----------|-------|------------|
| 테스트기업 A | admin_testa | admin@testcorp.co.kr | 1 |
| 글로벌기업 | admin_global | admin@globalcorp.co.kr | 2 |

### 개인계정 (personal)
| Username | Email |
|----------|-------|
| personal_junhyuk.kim | junhyuk.kim@gmail.com |
| personal_seojun.lee | seojun.lee@gmail.com |
| personal_doyun.park | doyun.park@gmail.com |

### 법인소속 직원계정 (employee_sub)
| 소속 | Username 패턴 | Email 패턴 |
|------|---------------|------------|
| 테스트기업 A | emp_0001 ~ emp_0010 | *@testcorp.co.kr |
| 글로벌기업 | emp_0021 ~ emp_0035 | *@globalcorp.co.kr |

## Rules

### Communication
- 한국어로 커뮤니케이션
- 이모지 사용 금지

### Code Standards
- 파일당 500~800 라인 이내 유지
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
