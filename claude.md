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
blueprints/     → Routes (URL 라우팅, 요청 처리)
    ├── employees/   # 모듈 분할된 CRUD (list_routes, mutation_routes, detail_routes)
    ├── profile/     # 통합 프로필 (개인/법인 인터페이스 통합)
    └── [domain].py  # 도메인별 라우트

services/       → Business Logic (비즈니스 로직)
repositories/   → Data Access (BaseRepository, BaseRelationRepository 상속)
models/         → SQLAlchemy Models (to_dict, from_dict 메서드 필수)
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

### Frontend Structure
```
static/js/
├── components/    # 재사용 UI (data-table, salary-calculator, toast)
├── services/      # API 통신 (employee-service, contract-service)
├── pages/         # 페이지별 로직
│   └── employee/  # 모듈화된 직원 폼 (validators, dynamic-sections)
└── utils/         # 공통 유틸 (api.js, validation.js)
```

### Template Macros (`templates/macros/`)
- `_form_controls.html`: 폼 입력 컴포넌트
- `_navigation.html`: 사이드바/섹션 네비게이션
- `_alerts.html`: 알림 메시지

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
# 1:N 관계: BaseRelationRepository 상속
class EducationRepository(BaseRelationRepository):
    def __init__(self):
        super().__init__(Education)

# 1:1 관계: BaseOneToOneRepository 상속
class SalaryRepository(BaseOneToOneRepository):
    ...
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
└── form_extractors.py   # 폼 데이터 추출
```

## Test Accounts

### 개인계정 (personal)
| Email | Password |
|-------|----------|
| personal1@test.com | personal1234 |
| personal2@test.com | personal1234 |
| personal3@test.com | personal1234 |

### 법인계정 (corporate)
| 법인 | Email | Password | Company ID |
|------|-------|----------|------------|
| 테스트기업 A | corp_a@test.com | corp1234 | 1 |
| 테스트기업 B | corp_b@test.com | corp1234 | 3 |

### 법인소속 직원계정 (employee_sub)
| 소속 | Email | Password |
|------|-------|----------|
| 법인 A | emp_a1@test.com ~ emp_a5@test.com | emp1234 |
| 법인 B | emp_b1@test.com ~ emp_b3@test.com | emp1234 |

### 기존 테스트 계정
| Email | Password | 유형 |
|-------|----------|------|
| testuser@example.com | test1234 | 일반 직원 |
| company@example.com | admin1234 | 관리자 |

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
