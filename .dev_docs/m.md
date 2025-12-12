# HR 관리 시스템 프론트엔드/백엔드 통합 마이그레이션 설계서

## 개요

법인 직원(Corporate)과 개인 계정(Personal) 템플릿을 통합하여 유지보수성과 확장성을 향상시키는 마이그레이션 계획

**총 기간**: 15-18일 (3-4주)
**목표**: 코드 중복 50% 감소, 새 계정 타입 추가 시간 80% 단축, 레거시 파일 30% 정리

---

## 현재 상태 요약 (2024-12-12 업데이트)

**실제 완료 범위**:
- Phase 1: CSS 스타일 일관성 개선 (완료)
- Phase 2: 백엔드 서비스 레이어 개선 (부분 완료)
- Phase 3: 파셜 템플릿 스타일 통일 (부분 완료) - **통합 템플릿 미생성**
- Phase 4: 테스트 코드 작성 (미진행)
- Phase 5: claudedocs/ 분석 문서 정리 (완료)

**미완료 핵심 작업**:
1. `profile/detail.html` 통합 템플릿 미생성
2. `profile/edit.html` 통합 템플릿 미생성
3. `profile.py` 통합 블루프린트 미생성
4. 변수 어댑터 레이어 미구현 (`employee` ↔ `profile` 매핑)
5. 레거시 URL 리다이렉트 미설정

**현재 아키텍처**:
```
법인 (Corporate):
├── employees/routes.py
├── templates/employees/*.html (7개 파일 활성 사용 중)
└── partials/employee_form/_*.html (변수: employee)

개인 (Personal):
├── blueprints/personal.py
├── templates/personal/*.html
└── partials/profile_form/_*.html (변수: profile)
```

두 시스템이 **분리 유지**되고 있으며, 완전한 통합을 위해서는 추가 작업 필요.

---

### Phase 구성
| Phase | 기간 | 주요 작업 | 계획 상태 | 실제 상태 |
|-------|------|----------|----------|----------|
| Phase 1 | Day 1-3 | CSS 아키텍처 개선 | 완료 | 스타일 일관성 개선 |
| Phase 2 | Day 4-7 | 백엔드 추상화 레이어 | 완료 | 서비스 레이어 개선 (부분) |
| Phase 3 | Day 8-12 | 템플릿 통합 | 완료 | **파셜 스타일 통일만 완료** |
| Phase 4 | Day 13-15 | 테스트 및 문서화 | 대기 | 미진행 |
| Phase 5 | Day 16-18 | 레거시 정리 | 대기 | claudedocs/ 정리만 완료 |

---

## Phase 1: CSS 아키텍처 개선 (Day 1-3)

### 1.1 디자인 토큰 시스템

**파일 생성**: `app/static/css/core/variables.css`

```css
:root {
  /* 색상 토큰 */
  --color-primary: #2563eb;
  --color-primary-dark: #1e40af;
  --color-secondary: #64748b;
  --color-success: #22c55e;
  --color-danger: #ef4444;

  /* 간격 토큰 */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* 프로필 컴포넌트 */
  --profile-header-padding: var(--space-8);
  --profile-header-bg: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
}

/* 계정 타입별 테마 */
body.account-personal {
  --profile-header-padding: var(--space-6);
}

body.account-corporate {
  --profile-show-business-card: true;
}
```

### 1.2 CSS 디렉토리 구조

```
app/static/css/
├── core/
│   ├── variables.css       # 디자인 토큰 (신규)
│   ├── reset.css           # 리셋 스타일
│   └── utilities.css       # 유틸리티 클래스
├── layouts/
│   ├── section-nav.css     # 섹션 네비게이션
│   ├── right-sidebar.css   # 우측 사이드바
│   └── profile-layout.css  # 통합 프로필 레이아웃 (신규)
├── components/
│   ├── cards.css           # 카드 컴포넌트
│   ├── tables.css          # 테이블
│   ├── profile-header.css  # 프로필 헤더 (통합, 신규)
│   └── forms.css           # 폼 컴포넌트
├── pages/
│   ├── employee-detail.css # 상세 페이지
│   └── employee-form.css   # 폼 페이지
└── variants/
    ├── corporate.css       # 법인 전용 오버라이드 (신규)
    └── personal.css        # 개인 전용 오버라이드 (신규)
```

### 1.3 BEM 네이밍 변환

| 현재 | BEM 변환 |
|------|----------|
| `.card` | `.profile-card` |
| `.card-header` | `.profile-card__header` |
| `.card-body` | `.profile-card__body` |
| `.detail-page-layout` | `.profile-layout` |
| `.employee-header` | `.profile-header` |
| `.employee-header--corporate` | Modifier |
| `.employee-header--personal` | Modifier |

### 1.4 Day별 작업 계획

| Day | 작업 | 산출물 |
|-----|------|--------|
| Day 1 | 디자인 토큰 시스템 구축 | `core/variables.css` |
| Day 2 | CSS 파일 재구성 및 BEM 변환 | `profile-*.css` 시리즈 |
| Day 3 | variants 분리 및 테마 적용 | `corporate.css`, `personal.css` |

---

## Phase 2: 백엔드 추상화 레이어 (Day 4-7)

### 2.1 ProfileComponentFactory

**파일 생성**: `app/components/profile_factory.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ProfileSection:
    id: str
    title: str
    icon: str
    visible: bool
    editable: bool
    fields: List['ProfileField']

@dataclass
class ProfileField:
    name: str
    label: str
    type: str
    value: any
    visible: bool
    editable: bool

class ProfileComponentFactory:
    """계정 타입별 프로필 컴포넌트 생성"""

    @staticmethod
    def get_sections(account_type: str, role: str) -> List[ProfileSection]:
        """계정 타입과 역할에 따른 섹션 구성 반환"""
        config = PROFILE_CONFIG.get(account_type, {})
        role_config = config.get(role, config.get('default', {}))
        return [SectionRegistry.get(sid) for sid in role_config.get('sections', [])]

    @staticmethod
    def get_field_visibility(account_type: str, role: str, field_name: str) -> bool:
        """필드 가시성 결정"""
        pass

    @staticmethod
    def build_context(account_type: str, role: str, data: Dict) -> Dict:
        """템플릿 렌더링용 전체 컨텍스트 빌드"""
        pass
```

### 2.2 설정 파일

**파일 생성**: `app/config/profile_config.py`

```python
PROFILE_SECTIONS = {
    'basic': {
        'title': '기본정보',
        'icon': 'fas fa-user',
        'order': 1,
        'visibility': {
            'corporate.admin': True,
            'corporate.employee': True,
            'personal.default': True
        }
    },
    'organization': {
        'title': '소속정보',
        'icon': 'fas fa-building',
        'order': 2,
        'visibility': {
            'corporate.admin': True,
            'corporate.employee': True,  # 읽기 전용
            'personal.default': False    # 계약 시에만 표시
        }
    },
    # ... 나머지 섹션
}

ACCOUNT_TYPES = {
    'corporate': {
        'roles': ['admin', 'manager', 'employee'],
        'default_sections': ['basic', 'organization', 'contract', 'education', 'career', 'certificate', 'language', 'project', 'military', 'family', 'salary', 'insurance'],
        'css_variant': 'corporate'
    },
    'personal': {
        'roles': ['default'],
        'default_sections': ['basic', 'education', 'career', 'certificate', 'language', 'military', 'visibility'],
        'css_variant': 'personal'
    }
}
```

### 2.3 컨텍스트 프로세서

**파일 수정**: `app/context_processors.py`

```python
from flask import g
from app.components.profile_factory import ProfileComponentFactory

def register_context_processors(app):
    @app.context_processor
    def profile_context():
        def get_profile_config(account_type: str, role: str) -> dict:
            return ProfileComponentFactory.get_config(account_type, role)

        def has_section(section_id: str) -> bool:
            return ProfileComponentFactory.has_section(
                g.account_type, g.user_role, section_id
            )

        def can_edit_field(field_name: str) -> bool:
            return ProfileComponentFactory.can_edit_field(
                g.account_type, g.user_role, field_name
            )

        return {
            'get_profile_config': get_profile_config,
            'has_section': has_section,
            'can_edit_field': can_edit_field,
            'profile_factory': ProfileComponentFactory
        }
```

### 2.4 Day별 작업 계획

| Day | 작업 | 산출물 |
|-----|------|--------|
| Day 4 | 설정 파일 및 Factory 기본 구조 | `profile_config.py`, `profile_factory.py` |
| Day 5 | ProfileService 통합 | `profile_service.py` |
| Day 6 | 컨텍스트 프로세서 구현 | `context_processors.py` 수정 |
| Day 7 | Blueprint 통합 및 라우트 수정 | `profile.py` 신규 블루프린트 |

---

## Phase 3: 템플릿 통합 (Day 8-12)

### 3.1 통합 템플릿 구조

```
app/templates/
├── profile/
│   ├── detail.html         # 통합 상세 페이지 (신규)
│   ├── edit.html           # 통합 수정 페이지 (신규)
│   └── components/
│       ├── _header.html    # 프로필 헤더
│       └── _section.html   # 범용 섹션 렌더러
├── partials/
│   └── profile/            # 통합 파셜 (신규)
│       ├── _basic_info.html
│       ├── _organization_info.html
│       └── _section_renderer.html
```

### 3.2 통합 detail.html 설계

```jinja2
{% extends "base.html" %}

{% set account_type = profile.account_type %}
{% set view_config = get_profile_config(account_type, user_role) %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/core/variables.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/profile-layout.css') }}">
{% if account_type == 'corporate' %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/variants/corporate.css') }}">
{% else %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/variants/personal.css') }}">
{% endif %}
{% endblock %}

{% block content %}
<body class="account-{{ account_type }}">
<div class="profile-layout">
    {{ section_nav(variant=account_type) }}

    <main class="profile-main">
        {% include 'profile/components/_header.html' %}

        {% for section in view_config.sections %}
            {% if has_section(section.id) %}
                {% include 'partials/profile/_section_renderer.html' %}
            {% endif %}
        {% endfor %}
    </main>
</div>
</body>
{% endblock %}
```

### 3.3 파셜 리팩토링 (조건부 렌더링 제거)

**Before** (현재):
```jinja2
{% if is_corporate %}
    {{ info_item('회사 이메일', employee.company_email) }}
{% endif %}
```

**After** (개선):
```jinja2
{% if has_section('company_email') %}
    {{ info_item('회사 이메일', profile.company_email) }}
{% endif %}
```

### 3.4 레거시 템플릿 제거 계획

| 단계 | 파일 | 조치 |
|------|------|------|
| 1단계 | `profile/detail.html`, `profile/edit.html` | 신규 생성 |
| 2단계 | `employees/detail.html` | 리다이렉트 설정 |
| 2단계 | `personal/profile_detail.html` | 리다이렉트 설정 |
| 3단계 | 레거시 파일 | 삭제 (검증 후) |

### 3.5 Day별 작업 계획

| Day | 작업 | 산출물 |
|-----|------|--------|
| Day 8 | 통합 템플릿 디렉토리 구조 생성 | `profile/` 디렉토리 |
| Day 9 | 통합 detail.html 구현 | `profile/detail.html` |
| Day 10 | 통합 edit.html 구현 | `profile/edit.html` |
| Day 11 | 파셜 리팩토링 | `partials/profile/` |
| Day 12 | 라우트 리다이렉트 및 레거시 정리 | Blueprint 수정 |

---

## Phase 4: 테스트 및 문서화 (Day 13-15)

### 4.1 테스트 계획

**단위 테스트** (`tests/unit/`):
```python
# test_profile_factory.py
def test_corporate_admin_gets_all_sections():
    sections = ProfileComponentFactory.get_sections('corporate', 'admin')
    assert 'salary' in [s.id for s in sections]
    assert 'insurance' in [s.id for s in sections]

def test_personal_hides_corporate_sections():
    sections = ProfileComponentFactory.get_sections('personal', 'default')
    assert 'salary' not in [s.id for s in sections]
    assert 'visibility' in [s.id for s in sections]
```

**통합 테스트** (`tests/integration/`):
```python
# test_profile_rendering.py
def test_corporate_profile_renders_correctly(client, corporate_user):
    response = client.get('/profile/1')
    assert 'profile-header--corporate' in response.data
    assert 'hr_records' in response.data

def test_personal_profile_renders_correctly(client, personal_user):
    response = client.get('/profile/me')
    assert 'profile-header--personal' in response.data
    assert 'visibility_settings' in response.data
```

**E2E 테스트** (Playwright):
```python
# test_profile_e2e.py
def test_personal_profile_edit_flow(page):
    page.goto('/personal/profile')
    page.click('[data-action="edit"]')
    page.fill('#name', '홍길동')
    page.click('[type="submit"]')
    assert page.locator('.toast-success').is_visible()
```

### 4.2 문서화

**생성할 문서**:
1. `docs/architecture/profile-system.md` - 아키텍처 개요
2. `docs/components/profile-factory.md` - ProfileComponentFactory 사용법
3. `docs/migration/account-template-migration.md` - 마이그레이션 가이드

### 4.3 Day별 작업 계획

| Day | 작업 | 산출물 |
|-----|------|--------|
| Day 13 | 단위 테스트 작성 | `tests/unit/test_profile_*.py` |
| Day 14 | 통합/E2E 테스트 작성 | `tests/integration/`, `tests/e2e/` |
| Day 15 | 문서화 및 최종 검증 | `docs/` |

---

## 롤백 전략

### 단계별 롤백 포인트

| Phase | 롤백 방법 | 예상 시간 |
|-------|----------|----------|
| Phase 1 | CSS 파일 되돌리기 | 5분 |
| Phase 2 | 설정 파일 비활성화 | 10분 |
| Phase 3 | 레거시 템플릿 복원 | 15분 |
| Phase 4 | 테스트 제외 | 즉시 |
| Phase 5 | 백업 브랜치에서 레거시 파일 복원 | 5분 |

### 긴급 롤백 절차

```bash
# 1. 신규 블루프린트 비활성화
# app/__init__.py에서 profile 블루프린트 주석 처리

# 2. 레거시 라우트 복원
git checkout HEAD~1 -- app/blueprints/employees.py
git checkout HEAD~1 -- app/blueprints/personal.py

# 3. 서버 재시작
flask run
```

---

## 수정 대상 파일 목록

### 신규 생성
- `app/static/css/core/variables.css`
- `app/static/css/variants/corporate.css`
- `app/static/css/variants/personal.css`
- `app/components/profile_factory.py`
- `app/config/profile_config.py`
- `app/templates/profile/detail.html`
- `app/templates/profile/edit.html`
- `app/blueprints/profile.py`

### 수정
- `app/context_processors.py`
- `app/__init__.py` (블루프린트 등록)
- `app/templates/macros/_navigation.html`
- `app/static/css/layouts/section-nav.css`
- `app/static/css/components/employee-header.css`

### 삭제 (Phase 3 완료 후)
- `app/templates/employees/detail.html` (리다이렉트로 대체)
- `app/templates/personal/profile_detail.html` (리다이렉트로 대체)

---

## 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 코드 중복 감소 | 50% | LOC 비교 |
| CSS 번들 크기 | 30% 감소 | 빌드 크기 측정 |
| 테스트 커버리지 | 80% | pytest-cov |
| 페이지 로드 시간 | 유지 또는 개선 | Lighthouse |

---

## 다음 단계

### 완료된 작업
1. Phase 1: CSS 스타일 일관성 개선
2. Phase 2: 백엔드 서비스 레이어 개선 (PersonalService, Repository 패턴)
3. Phase 3: 파셜 템플릿 스타일 통일 (partials/employee_form/, partials/profile_form/)
4. Phase 5 (부분): claudedocs/ 분석 문서 정리 완료

### 미완료 핵심 작업 (템플릿 통합)
다음 작업들이 **미완료** 상태입니다:

| 작업 | 설명 | 예상 시간 |
|------|------|----------|
| `profile/detail.html` | 법인/개인 통합 상세 페이지 | 4시간 |
| `profile/edit.html` | 법인/개인 통합 수정 페이지 | 4시간 |
| `profile.py` 블루프린트 | 통합 라우트 및 컨트롤러 | 3시간 |
| 변수 어댑터 | `employee` ↔ `profile` 매핑 | 2시간 |
| 레거시 리다이렉트 | 기존 URL → 신규 URL 301 | 1시간 |
| 테스트 코드 | 92개 테스트 케이스 | 8시간 |

**총 예상 추가 작업**: 22시간 (2-3일)

### 선택지

**A. 완전한 통합 진행** - **선택됨 (2024-12-12)**
- 위 미완료 작업 모두 수행
- 단일 `profile/` 시스템으로 통합
- 코드 중복 50% 감소 목표 달성

**B. 현재 상태 유지**
- 두 시스템 분리 유지 (법인/개인)
- 스타일 일관성만 유지된 상태
- 추가 개발 없이 안정화

---

## Phase 3 재작업: 템플릿 통합 구현 계획

### 작업 순서

#### Step 1: 변수 어댑터 레이어 (2시간)
```
파일: app/adapters/profile_adapter.py (수정)

기능:
- Employee → dict 변환 (법인)
- PersonalProfile → dict 변환 (개인)
- 통합 변수명 사용: employee/profile → unified_profile
```

#### Step 2: 통합 블루프린트 생성 (3시간)
```
파일: app/blueprints/profile.py (신규)

라우트:
- GET /profile/<account_type>/<id> → 상세 페이지
- GET /profile/<account_type>/<id>/edit → 수정 페이지
- POST /profile/<account_type>/<id>/edit → 수정 처리
```

#### Step 3: 통합 상세 템플릿 (4시간)
```
파일: app/templates/profile/detail.html (신규)

구조:
- account_type 기반 조건부 렌더링
- partials/employee_detail/* 재사용
- section_nav variant 동적 설정
```

#### Step 4: 통합 수정 템플릿 (4시간)
```
파일: app/templates/profile/edit.html (신규)

구조:
- partials/employee_form/* 재사용
- profile 변수 → employee 변수 매핑
- 섹션별 가시성 제어
```

#### Step 5: 레거시 리다이렉트 (1시간)
```
파일: app/blueprints/employees/routes.py, app/blueprints/personal.py (수정)

- /employees/<id> → /profile/corporate/<id> (301)
- /personal/profile → /profile/personal/me (301)
```

#### Step 6: 테스트 및 검증 (8시간)
```
- 단위 테스트 작성
- 통합 테스트 작성
- E2E 테스트 (Playwright)
```

### 수정 대상 파일 목록

**신규 생성:**
- `app/blueprints/profile.py`
- `app/templates/profile/detail.html`
- `app/templates/profile/edit.html`
- `app/templates/profile/components/_header.html`

**수정:**
- `app/adapters/profile_adapter.py`
- `app/blueprints/employees/routes.py`
- `app/blueprints/personal.py`
- `app/__init__.py` (블루프린트 등록)

**삭제 (통합 완료 후):**
- `app/templates/employees/detail.html`
- `app/templates/employees/form.html`
- `app/templates/personal/profile_edit.html`
- `app/templates/partials/profile_form/` 디렉토리

---

## 리스크 분석 및 누락 방지 체크리스트

### 1. 데이터 무결성 리스크

#### 1.1 모델 필드 불일치 (Critical)

**발견된 필드명 불일치**:

| 데이터 의미 | Employee 필드명 | PersonalProfile 필드명 | 조치 필요 |
|------------|-----------------|----------------------|----------|
| 휴대전화 | phone | mobile_phone | 매핑 필요 |
| 졸업상태 | graduation_status | status | 매핑 필요 |
| 직무설명 | job_description | responsibilities | 매핑 필요 |
| 퇴직사유 | resignation_reason | reason_for_leaving | 매핑 필요 |
| 자격증명 | certificate_name | name | 매핑 필요 |
| 취득날짜 | acquisition_date | issue_date | 매핑 필요 |
| 언어명 | language_name | language | 매핑 필요 |
| 시험명 | exam_name | test_name | 매핑 필요 |
| 능력수준 | level | proficiency | 매핑 필요 |
| 입대날짜 | enlistment_date | start_date | 매핑 필요 |
| 전역날짜 | discharge_date | end_date | 매핑 필요 |
| 참고사항 | note | notes | 매핑 필요 |

**조치**: `profile_factory.py`에 필드 매핑 레이어 구현

```python
FIELD_MAPPING = {
    'phone': 'mobile_phone',
    'graduation_status': 'status',
    'job_description': 'responsibilities',
    'certificate_name': 'name',
    'acquisition_date': 'issue_date',
    # ...
}
```

#### 1.2 법인 전용 필드 (15개) - 개인 계정에서 누락 방지

| 필드명 | 용도 | 마이그레이션 시 처리 |
|--------|------|-------------------|
| employee_number | 사번 | active_contract에서 제공 |
| department | 부서 | active_contract에서 제공 |
| position | 직급 | active_contract에서 제공 |
| status | 재직상태 | 계약 상태로 대체 |
| hire_date | 입사일 | 계약 시작일로 대체 |
| company_email | 회사 이메일 | 법인 전용 유지 |
| internal_phone | 내선번호 | 법인 전용 유지 |
| team | 팀명 | active_contract에서 제공 |
| job_title | 직책 | active_contract에서 제공 |
| work_location | 근무지 | 법인 전용 유지 |
| marital_status | 결혼여부 | 공통 필드로 확장 필요 |
| organization_id | 조직 FK | 법인 전용 유지 |

#### 1.3 개인 전용 필드 (3개) - 법인에서 누락 방지

| 필드명 | 용도 | 마이그레이션 시 처리 |
|--------|------|-------------------|
| user_id | User FK | 법인 하위계정도 user_id 가짐 |
| is_public | 공개설정 | 개인 전용 유지 |
| created_at/updated_at | 메타 | 공통으로 확장 권장 |

---

### 2. 기능 누락 리스크

#### 2.1 API 엔드포인트 보존 체크리스트

**개인 계정 API** (반드시 유지):

| 엔드포인트 | 메서드 | 기능 | 확인 |
|-----------|--------|------|-----|
| `/personal/register` | GET, POST | 회원가입 | [ ] |
| `/personal/dashboard` | GET | 대시보드 | [ ] |
| `/personal/profile` | GET | 프로필 조회 | [ ] |
| `/personal/profile/edit` | GET, POST | 프로필 수정 | [ ] |
| `/personal/education` | GET, POST, DELETE | 학력 CRUD | [ ] |
| `/personal/career` | GET, POST, DELETE | 경력 CRUD | [ ] |
| `/personal/certificate` | GET, POST, DELETE | 자격증 CRUD | [ ] |
| `/personal/language` | GET, POST, DELETE | 어학 CRUD | [ ] |
| `/personal/military` | GET, POST | 병역 CRUD | [ ] |
| `/personal/contract-history` | GET | 계약 이력 | [ ] |

**법인 직원 API** (반드시 유지):

| 엔드포인트 | 메서드 | 기능 | 확인 |
|-----------|--------|------|-----|
| `/employees/` | GET | 직원 목록 | [ ] |
| `/employees/<id>` | GET | 직원 상세 | [ ] |
| `/employees/new` | GET, POST | 직원 등록 | [ ] |
| `/employees/<id>/edit` | GET, POST | 직원 수정 | [ ] |
| `/employees/<id>/delete` | POST | 직원 삭제 | [ ] |
| `/employees/api/search` | GET | 직원 검색 | [ ] |

#### 2.2 권한 체크 누락 방지

**데코레이터 매핑**:

| 데코레이터 | 현재 사용처 | 통합 후 |
|-----------|-----------|---------|
| `@personal_login_required` | personal.py | `@profile_login_required(account_type='personal')` |
| `@corporate_login_required` | corporate.py | `@profile_login_required(account_type='corporate')` |
| `@personal_account_required` | contracts.py | 유지 |
| `@corporate_account_required` | contracts.py | 유지 |
| `@admin_required` | api.py | 유지 |
| `@profile_required_no_inject` | personal.py | 통합 |

#### 2.3 조건부 렌더링 플래그 일관성

**필수 컨텍스트 변수 체크리스트**:

| 변수 | 타입 | 기본값 | 사용처 | 확인 |
|------|------|-------|-------|-----|
| `is_corporate` | bool | true | 모든 상세/폼 | [ ] |
| `is_employee_role` | bool | false | 폼 템플릿 | [ ] |
| `variant` | str | 'full' | section_nav | [ ] |
| `action` | str | 'view' | 폼 템플릿 | [ ] |
| `active_contract` | obj/None | None | 개인 프로필 | [ ] |
| `can_edit_business_card` | bool | false | 상세 템플릿 | [ ] |
| `header_variant` | str | 'corporate' | 헤더 컴포넌트 | [ ] |

---

### 3. UI/UX 일관성 리스크

#### 3.1 섹션별 표시 여부 매트릭스

| 섹션 | 법인 관리자 | 법인 직원 | 개인 (계약無) | 개인 (계약有) |
|------|-----------|----------|-------------|-------------|
| 개인 기본정보 | O | O | O | O |
| 소속정보 | O (편집) | O (읽기) | X | O (읽기) |
| 계약정보 | O | X | X | X |
| 급여정보 | O | X | X | X |
| 복리후생 | O | X | X | X |
| 4대보험 | O | X | X | X |
| 학력정보 | O | O | O | O |
| 경력정보 | O | O | O | O |
| 자격증 | O | O | O | O |
| 언어능력 | O | O | O | O |
| 병역정보 | O | O | O | O |
| 프로젝트 | O | X | X | X |
| 수상내역 | O | X | X | X |
| 가족사항 | O | X | X | X |
| 인사기록 | O | X | X | X |
| 공개설정 | X | X | O | O |

#### 3.2 필드별 편집 권한 매트릭스

| 필드 카테고리 | 법인 관리자 | 법인 직원 | 개인 |
|-------------|-----------|----------|------|
| 이름/영문명/한자 | 편집 | 편집 | 편집 |
| 주민등록번호 | 편집 | 읽기 | 편집 |
| 연락처 (개인) | 편집 | 편집 | 편집 |
| 연락처 (회사) | 편집 | 읽기 | X |
| 주소 | 편집 | 편집 | 편집 |
| 소속정보 | 편집 | 읽기 | X |
| 급여정보 | 편집 | X | X |
| 학력/경력/자격 | 편집 | 편집 | 편집 |

---

### 4. 상세 테스트 계획

#### 4.1 단위 테스트 (42개)

**ProfileComponentFactory 테스트** (12개):
```python
# tests/unit/test_profile_factory.py

class TestProfileComponentFactory:
    # 섹션 조회 테스트 (6개)
    def test_corporate_admin_gets_all_14_sections(self): ...
    def test_corporate_employee_gets_limited_sections(self): ...
    def test_personal_default_gets_7_sections(self): ...
    def test_personal_with_contract_shows_organization(self): ...
    def test_section_order_is_correct(self): ...
    def test_invalid_account_type_raises_error(self): ...

    # 필드 가시성 테스트 (4개)
    def test_salary_visible_only_for_admin(self): ...
    def test_company_email_hidden_for_personal(self): ...
    def test_is_public_hidden_for_corporate(self): ...
    def test_field_mapping_works_correctly(self): ...

    # 편집 권한 테스트 (2개)
    def test_employee_cannot_edit_organization(self): ...
    def test_personal_can_edit_own_profile(self): ...
```

**컨텍스트 프로세서 테스트** (8개):
```python
# tests/unit/test_context_processors.py

class TestProfileContextProcessor:
    def test_get_profile_config_returns_dict(self): ...
    def test_has_section_returns_boolean(self): ...
    def test_can_edit_field_returns_boolean(self): ...
    def test_profile_factory_available_in_context(self): ...
    def test_caching_works_per_request(self): ...
    def test_g_variables_set_correctly(self): ...
    def test_missing_account_type_uses_default(self): ...
    def test_missing_role_uses_default(self): ...
```

**필드 매핑 테스트** (6개):
```python
# tests/unit/test_field_mapping.py

class TestFieldMapping:
    def test_education_status_mapping(self): ...
    def test_career_responsibilities_mapping(self): ...
    def test_certificate_name_mapping(self): ...
    def test_language_proficiency_mapping(self): ...
    def test_military_date_mapping(self): ...
    def test_notes_plural_mapping(self): ...
```

**설정 파일 테스트** (4개):
```python
# tests/unit/test_profile_config.py

class TestProfileConfig:
    def test_all_sections_have_required_keys(self): ...
    def test_account_types_have_valid_sections(self): ...
    def test_visibility_matrix_is_complete(self): ...
    def test_no_duplicate_section_ids(self): ...
```

**어댑터 테스트** (12개):
```python
# tests/unit/test_profile_adapter.py

class TestPersonalProfileAdapter:
    def test_get_basic_info_returns_all_fields(self): ...
    def test_phone_fallback_to_mobile_phone(self): ...
    def test_gender_normalization(self): ...
    def test_empty_fields_return_none(self): ...
    def test_active_contract_integration(self): ...
    def test_terminated_contract_snapshot(self): ...

class TestEmployeeAdapter:
    def test_to_dict_includes_all_fields(self): ...
    def test_organization_relation_loaded(self): ...
    def test_related_collections_accessible(self): ...
    def test_employee_number_format_valid(self): ...
    def test_status_badge_class_correct(self): ...
    def test_tenure_calculation_correct(self): ...
```

#### 4.2 통합 테스트 (24개)

**프로필 조회 테스트** (8개):
```python
# tests/integration/test_profile_view.py

class TestProfileView:
    # 법인 계정
    def test_corporate_admin_views_employee(self): ...
    def test_corporate_admin_views_all_sections(self): ...
    def test_corporate_employee_views_own_limited(self): ...
    def test_corporate_employee_cannot_view_salary(self): ...

    # 개인 계정
    def test_personal_views_own_profile(self): ...
    def test_personal_without_contract_no_org(self): ...
    def test_personal_with_contract_shows_org(self): ...
    def test_terminated_contract_history_readonly(self): ...
```

**프로필 수정 테스트** (8개):
```python
# tests/integration/test_profile_edit.py

class TestProfileEdit:
    # 법인 계정
    def test_admin_can_edit_all_fields(self): ...
    def test_admin_can_add_education(self): ...
    def test_employee_cannot_edit_organization(self): ...
    def test_employee_can_edit_contact(self): ...

    # 개인 계정
    def test_personal_can_edit_profile(self): ...
    def test_personal_can_add_career(self): ...
    def test_personal_photo_upload_works(self): ...
    def test_personal_visibility_toggle_works(self): ...
```

**API 엔드포인트 테스트** (8개):
```python
# tests/integration/test_profile_api.py

class TestProfileAPI:
    def test_education_crud_personal(self): ...
    def test_education_crud_corporate(self): ...
    def test_career_crud_personal(self): ...
    def test_career_crud_corporate(self): ...
    def test_certificate_crud_personal(self): ...
    def test_language_crud_personal(self): ...
    def test_military_save_personal(self): ...
    def test_api_returns_json_format(self): ...
```

#### 4.3 E2E 테스트 (16개, Playwright)

**개인 계정 시나리오** (8개):
```python
# tests/e2e/test_personal_flow.py

class TestPersonalFlow:
    def test_register_and_create_profile(self): ...
    def test_view_profile_detail(self): ...
    def test_edit_basic_info(self): ...
    def test_add_education_record(self): ...
    def test_add_career_record(self): ...
    def test_add_certificate(self): ...
    def test_upload_profile_photo(self): ...
    def test_toggle_public_visibility(self): ...
```

**법인 계정 시나리오** (8개):
```python
# tests/e2e/test_corporate_flow.py

class TestCorporateFlow:
    def test_admin_view_employee_list(self): ...
    def test_admin_create_employee(self): ...
    def test_admin_edit_employee(self): ...
    def test_admin_view_salary_info(self): ...
    def test_employee_view_own_card(self): ...
    def test_employee_edit_contact_only(self): ...
    def test_section_nav_scrolls_correctly(self): ...
    def test_business_card_upload(self): ...
```

#### 4.4 회귀 테스트 (10개)

```python
# tests/regression/test_migration_regression.py

class TestMigrationRegression:
    # 기존 기능 보존
    def test_legacy_url_redirects_work(self): ...
    def test_existing_data_displays_correctly(self): ...
    def test_session_variables_preserved(self): ...
    def test_flash_messages_work(self): ...
    def test_form_validation_unchanged(self): ...

    # CSS 호환성
    def test_legacy_css_classes_still_work(self): ...
    def test_responsive_design_unchanged(self): ...
    def test_print_styles_work(self): ...

    # 권한 보존
    def test_permission_checks_unchanged(self): ...
    def test_login_redirect_unchanged(self): ...
```

---

### 5. 마이그레이션 실행 체크리스트

#### Phase 1 완료 체크리스트 (CSS)

- [ ] `variables.css` 생성 및 디자인 토큰 정의
- [ ] 기존 CSS에서 하드코딩된 값 토큰으로 대체
- [ ] BEM 네이밍 변환 완료
- [ ] `corporate.css` / `personal.css` 분리
- [ ] 브라우저 테스트 (Chrome, Firefox, Safari, Edge)
- [ ] 반응형 테스트 (모바일, 태블릿, 데스크톱)
- [ ] 다크 모드 호환성 확인 (해당 시)

#### Phase 2 완료 체크리스트 (백엔드)

- [ ] `profile_config.py` 모든 섹션 정의 완료
- [ ] `profile_factory.py` 모든 메서드 구현
- [ ] 필드 매핑 레이어 구현
- [ ] 컨텍스트 프로세서 등록
- [ ] 기존 서비스와 통합 테스트
- [ ] API 응답 형식 호환성 확인
- [ ] 세션 변수 유지 확인

#### Phase 3 완료 체크리스트 (템플릿)

- [ ] `profile/detail.html` 법인 계정 테스트
- [ ] `profile/detail.html` 개인 계정 테스트
- [ ] `profile/edit.html` 법인 관리자 테스트
- [ ] `profile/edit.html` 법인 직원 테스트
- [ ] `profile/edit.html` 개인 계정 테스트
- [ ] 모든 14개 섹션 렌더링 확인
- [ ] 모든 플래그 조합 테스트 (8개 시나리오)
- [ ] 폼 제출 및 데이터 저장 확인
- [ ] 레거시 URL 리다이렉트 동작
- [ ] 에러 페이지 처리

#### Phase 4 완료 체크리스트 (테스트/문서화)

- [ ] 단위 테스트 42개 통과
- [ ] 통합 테스트 24개 통과
- [ ] E2E 테스트 16개 통과
- [ ] 회귀 테스트 10개 통과
- [ ] 테스트 커버리지 80% 이상
- [ ] 아키텍처 문서 작성
- [ ] 컴포넌트 문서 작성
- [ ] 마이그레이션 가이드 작성
- [ ] CHANGELOG 업데이트

---

### 6. 비상 롤백 시나리오

#### 시나리오 1: CSS 렌더링 깨짐
```
증상: 페이지 레이아웃이 깨지거나 스타일 누락
조치:
1. variants/*.css 주석 처리
2. base.html에서 variables.css 제거
3. 기존 CSS 직접 로드로 복원
예상 시간: 5분
```

#### 시나리오 2: 데이터 표시 오류
```
증상: 필드가 비어있거나 잘못된 값 표시
조치:
1. profile_factory.py 비활성화
2. 기존 is_corporate 플래그 직접 사용으로 복원
3. 어댑터 매핑 우회
예상 시간: 15분
```

#### 시나리오 3: 권한 오류
```
증상: 접근 권한 오류 또는 페이지 403
조치:
1. 신규 데코레이터 제거
2. 기존 @personal_login_required 등 복원
3. 블루프린트 라우트 복원
예상 시간: 20분
```

#### 시나리오 4: 전체 롤백
```
git checkout HEAD~N -- app/
git checkout HEAD~N -- templates/
git checkout HEAD~N -- static/css/
flask run
예상 시간: 10분 (N = 커밋 수)
```

---

### 7. 데이터 무결성 검증 쿼리

#### 마이그레이션 전 데이터 스냅샷
```sql
-- 직원 수 확인
SELECT COUNT(*) AS employee_count FROM employees;

-- 개인 프로필 수 확인
SELECT COUNT(*) AS profile_count FROM personal_profiles;

-- 학력 정보 수
SELECT
    (SELECT COUNT(*) FROM educations) AS employee_edu,
    (SELECT COUNT(*) FROM personal_educations) AS personal_edu;

-- 경력 정보 수
SELECT
    (SELECT COUNT(*) FROM careers) AS employee_career,
    (SELECT COUNT(*) FROM personal_careers) AS personal_career;
```

#### 마이그레이션 후 검증
```sql
-- 데이터 손실 없음 확인
SELECT
    'employees' AS table_name,
    COUNT(*) AS count,
    CASE WHEN COUNT(*) = {pre_count} THEN 'OK' ELSE 'MISMATCH' END AS status
FROM employees
UNION ALL
SELECT
    'personal_profiles',
    COUNT(*),
    CASE WHEN COUNT(*) = {pre_count} THEN 'OK' ELSE 'MISMATCH' END
FROM personal_profiles;
```

---

### 8. 모니터링 항목

#### 마이그레이션 중 모니터링
- [ ] 에러 로그 (500 에러 급증 여부)
- [ ] 페이지 로드 시간 (2초 이내 유지)
- [ ] API 응답 시간 (500ms 이내 유지)
- [ ] 메모리 사용량 (급증 여부)
- [ ] 데이터베이스 쿼리 수 (N+1 문제 발생 여부)

#### 마이그레이션 후 모니터링 (1주일)
- [ ] 사용자 불만 접수
- [ ] 기능 오류 보고
- [ ] 성능 저하 보고
- [ ] 접근성 이슈 보고

---

## Phase 5: 레거시 정리 (Day 16-18)

통합 템플릿 시스템이 안정화된 후, 레거시 파일을 체계적으로 정리하여 코드베이스를 최적화합니다.

### 5.1 레거시 템플릿 파일 정리

#### 5.1.1 삭제 대상 템플릿

**상세 페이지 관련** (통합 `profile/detail.html`로 대체):
| 파일 | 상태 | 대체 파일 | 조치 |
|------|------|----------|------|
| `employees/detail.html` | 레거시 | `profile/detail.html` | 삭제 |
| `personal/profile_detail.html` | 레거시 | `profile/detail.html` | 삭제 |
| `personal/profile_view.html` | 레거시 (있을 경우) | `profile/detail.html` | 삭제 |

**수정 페이지 관련** (통합 `profile/edit.html`로 대체):
| 파일 | 상태 | 대체 파일 | 조치 |
|------|------|----------|------|
| `employees/form.html` | 레거시 | `profile/edit.html` | 삭제 |
| `personal/profile_edit.html` | 레거시 | `profile/edit.html` | 삭제 |
| `partials/profile_form/_*.html` | 레거시 | `partials/employee_form/_*.html` | 삭제 |

#### 5.1.2 삭제 대상 파셜 템플릿

**레거시 프로필 폼 파셜** (`partials/profile_form/` 디렉토리 전체):
```
partials/profile_form/
├── _address_info.html       # 삭제 (employee_form 통합)
├── _contact_info.html       # 삭제 (employee_form 통합)
├── _other_info.html         # 삭제 (employee_form 통합)
├── _personal_basic_info.html # 삭제 (employee_form 통합)
└── _submit_section.html     # 삭제 (profile/components/_form_submit.html로 대체)
```

**레거시 상세 파셜**:
| 파일 | 조치 | 이유 |
|------|------|------|
| `partials/personal_detail/_*.html` | 삭제 | `partials/employee_detail/` 통합 사용 |
| 중복 헤더 컴포넌트 | 삭제 | `profile/components/_header.html` 통합 |

#### 5.1.3 유지 대상 파셜 (공통 사용)

```
partials/
├── employee_detail/          # 유지 - 법인/개인 공통 사용
│   ├── _basic_info.html
│   ├── _organization_info.html
│   ├── _history_info.html
│   └── _hr_records.html
├── employee_form/            # 유지 - 법인/개인 공통 사용
│   ├── _personal_info.html
│   ├── _education_info.html
│   ├── _career_info.html
│   ├── _certificate_info.html
│   ├── _language_info.html
│   └── _military_info.html
└── profile/                  # 유지 - 신규 통합 컴포넌트
    ├── _macros.html
    └── _section_renderer.html
```

---

### 5.2 CSS 파일 정리

#### 5.2.1 삭제 대상 CSS

| 파일 | 상태 | 대체 | 조치 |
|------|------|------|------|
| `css/pages/personal-profile.css` | 레거시 | `variants/personal.css` | 삭제 |
| `css/pages/employee-detail-old.css` | 레거시 | `pages/employee-detail.css` | 삭제 |
| 인라인 스타일 블록 | 레거시 | CSS 파일 분리 | 정리 |

#### 5.2.2 통합 대상 CSS

**Before** (분산):
```
css/
├── employee-header.css      # 법인 전용
├── personal-header.css      # 개인 전용 (중복)
└── profile-header.css       # 신규 (미사용)
```

**After** (통합):
```
css/
├── components/
│   └── profile-header.css   # 통합 (법인/개인 공통)
└── variants/
    ├── corporate.css        # 법인 오버라이드만
    └── personal.css         # 개인 오버라이드만
```

#### 5.2.3 CSS 정리 체크리스트

- [ ] 중복 CSS 클래스 통합 (`employee-header` → `profile-header`)
- [ ] 미사용 CSS 클래스 제거
- [ ] 인라인 스타일을 CSS 파일로 이동
- [ ] CSS 변수 미적용 하드코딩 값 정리
- [ ] 미디어 쿼리 중복 제거

---

### 5.3 JavaScript 파일 정리

#### 5.3.1 삭제 대상 JS

| 파일 | 상태 | 대체 | 조치 |
|------|------|------|------|
| `js/pages/personal-profile.js` | 레거시 | `js/pages/employee/` | 삭제 |
| `js/personal-form-handler.js` | 레거시 | `js/services/` | 삭제 |
| 중복 유틸리티 함수 | 레거시 | `js/utils/` | 통합 |

#### 5.3.2 통합 대상 JS

**Before** (분산):
```
js/
├── employee-form.js         # 법인 폼
├── personal-form.js         # 개인 폼 (중복 로직)
└── profile-common.js        # 공통 (미완성)
```

**After** (통합):
```
js/
├── pages/
│   └── employee/
│       ├── index.js         # 통합 진입점
│       ├── helpers.js       # 공통 헬퍼
│       └── form-handler.js  # 통합 폼 핸들러
└── utils/
    ├── api.js               # API 유틸
    └── formatting.js        # 포맷팅 유틸
```

---

### 5.4 Blueprint 라우트 정리

#### 5.4.1 리다이렉트 설정

레거시 URL을 신규 통합 URL로 리다이렉트:

```python
# app/blueprints/employees.py

@employees_bp.route('/<int:employee_id>/detail')
def employee_detail_legacy(employee_id):
    """레거시 URL 리다이렉트"""
    return redirect(url_for('profile.detail',
                          account_type='corporate',
                          profile_id=employee_id),
                   code=301)
```

```python
# app/blueprints/personal.py

@personal_bp.route('/profile_detail')
@personal_login_required
def profile_detail_legacy():
    """레거시 URL 리다이렉트"""
    return redirect(url_for('profile.detail',
                          account_type='personal',
                          profile_id='me'),
                   code=301)
```

#### 5.4.2 라우트 정리 매트릭스

| 레거시 URL | 신규 URL | HTTP Code |
|-----------|----------|-----------|
| `/employees/<id>` | `/profile/corporate/<id>` | 301 |
| `/employees/<id>/edit` | `/profile/corporate/<id>/edit` | 301 |
| `/personal/profile` | `/profile/personal/me` | 301 |
| `/personal/profile/edit` | `/profile/personal/me/edit` | 301 |

#### 5.4.3 삭제 대상 라우트

레거시 리다이렉트 유지 기간 (3개월) 후 삭제 예정:
- `employee_detail_legacy()`
- `profile_detail_legacy()`
- `profile_edit_legacy()`

---

### 5.5 설정 파일 정리

#### 5.5.1 레거시 설정 정리

| 파일/설정 | 상태 | 조치 |
|----------|------|------|
| `PERSONAL_PROFILE_SECTIONS` | 레거시 | `PROFILE_SECTIONS`로 통합 |
| `EMPLOYEE_DETAIL_CONFIG` | 레거시 | `ACCOUNT_TYPES`로 통합 |
| 하드코딩된 섹션 목록 | 레거시 | `profile_config.py` 참조로 변경 |

#### 5.5.2 환경변수 정리

불필요한 환경변수 제거:
```
# 삭제 대상
PERSONAL_PROFILE_ENABLED=true  # 항상 활성화
LEGACY_TEMPLATE_MODE=false     # 레거시 모드 제거

# 유지
PROFILE_SYSTEM_VERSION=2.0     # 버전 관리용
```

---

### 5.6 Day별 작업 계획

| Day | 작업 | 산출물 | 검증 |
|-----|------|--------|------|
| Day 16 | 템플릿 레거시 삭제 | 템플릿 파일 정리 | 모든 페이지 렌더링 확인 |
| Day 17 | CSS/JS 정리 및 통합 | 정적 파일 최적화 | 스타일/기능 동작 확인 |
| Day 18 | 라우트 리다이렉트 및 설정 정리 | Blueprint 정리 | URL 리다이렉트 테스트 |

---

### 5.7 레거시 정리 실행 절차

#### Step 1: 백업 생성 (필수)
```bash
# 레거시 파일 백업
git checkout -b backup/legacy-templates-$(date +%Y%m%d)
git add -A
git commit -m "backup: 레거시 정리 전 백업"
git push origin backup/legacy-templates-$(date +%Y%m%d)

# 메인 브랜치로 복귀
git checkout main
```

#### Step 2: 템플릿 삭제
```bash
# 레거시 상세 페이지
rm app/templates/employees/detail.html
rm app/templates/personal/profile_detail.html

# 레거시 폼 페이지
rm app/templates/employees/form.html
rm app/templates/personal/profile_edit.html

# 레거시 파셜 디렉토리
rm -rf app/templates/partials/profile_form/
rm -rf app/templates/partials/personal_detail/
```

#### Step 3: CSS/JS 정리
```bash
# 레거시 CSS 삭제
rm app/static/css/pages/personal-profile.css
rm app/static/css/employee-header.css  # 통합 완료 후

# 레거시 JS 삭제
rm app/static/js/personal-form.js
rm app/static/js/employee-form.js  # 통합 완료 후
```

#### Step 4: 검증 테스트 실행
```bash
# 단위 테스트
pytest tests/unit/ -v

# 통합 테스트
pytest tests/integration/ -v

# E2E 테스트
pytest tests/e2e/ -v

# 전체 회귀 테스트
pytest tests/regression/ -v
```

#### Step 5: 커밋 및 배포
```bash
git add -A
git commit -m "chore: Phase 5 레거시 파일 정리 완료

- 레거시 템플릿 삭제 (employees/detail.html, personal/profile_*.html)
- 레거시 파셜 디렉토리 정리 (profile_form/, personal_detail/)
- CSS/JS 파일 통합 및 정리
- 라우트 리다이렉트 설정
- 테스트 통과 확인"

git push origin main
```

---

### 5.8 레거시 정리 체크리스트

#### 템플릿 정리
- [ ] `employees/detail.html` 삭제
- [ ] `personal/profile_detail.html` 삭제
- [ ] `employees/form.html` 삭제
- [ ] `personal/profile_edit.html` 삭제
- [ ] `partials/profile_form/` 디렉토리 삭제
- [ ] `partials/personal_detail/` 디렉토리 삭제
- [ ] 모든 템플릿 import 참조 업데이트

#### CSS 정리
- [ ] 중복 CSS 파일 삭제
- [ ] 미사용 CSS 클래스 제거
- [ ] CSS 변수 통합 적용
- [ ] 번들 크기 최적화 확인

#### JavaScript 정리
- [ ] 중복 JS 파일 삭제
- [ ] 공통 함수 통합
- [ ] 미사용 함수 제거
- [ ] 번들 크기 최적화 확인

#### 라우트 정리
- [ ] 레거시 URL 리다이렉트 설정
- [ ] 신규 라우트 동작 확인
- [ ] SEO 영향 검토 (301 리다이렉트)
- [ ] 북마크/링크 호환성 확인

#### 검증
- [ ] 모든 테스트 통과
- [ ] 프로덕션 환경 테스트
- [ ] 성능 지표 유지 확인
- [ ] 사용자 피드백 수집

---

### 5.9 레거시 정리 롤백

#### 즉시 롤백 (5분)
```bash
# 백업 브랜치에서 파일 복원
git checkout backup/legacy-templates-YYYYMMDD -- app/templates/
git checkout backup/legacy-templates-YYYYMMDD -- app/static/

# 서버 재시작
flask run
```

#### 부분 롤백 (특정 파일)
```bash
# 특정 템플릿만 복원
git checkout backup/legacy-templates-YYYYMMDD -- app/templates/employees/detail.html

# 특정 CSS만 복원
git checkout backup/legacy-templates-YYYYMMDD -- app/static/css/employee-header.css
```

---

### 5.10 레거시 정리 후 최종 구조

```
app/templates/
├── profile/                      # 통합 프로필 시스템
│   ├── detail.html              # 통합 상세 페이지
│   ├── edit.html                # 통합 수정 페이지
│   └── components/
│       ├── _header.html         # 통합 헤더
│       └── _form_submit.html    # 통합 제출 버튼
├── partials/
│   ├── employee_detail/         # 상세 파셜 (공통)
│   ├── employee_form/           # 폼 파셜 (공통)
│   └── profile/                 # 프로필 공통 컴포넌트
│       ├── _macros.html
│       └── _section_renderer.html
├── employees/
│   └── list.html               # 직원 목록 (유지)
├── personal/
│   ├── dashboard.html          # 대시보드 (유지)
│   ├── register.html           # 회원가입 (유지)
│   └── contract_history_list.html  # 계약 이력 (유지)
└── contracts/                   # 계약 관련 (유지)

app/static/css/
├── core/
│   └── variables.css           # 디자인 토큰
├── layouts/
│   └── profile-layout.css      # 프로필 레이아웃
├── components/
│   └── profile-header.css      # 통합 헤더 스타일
├── pages/
│   └── employee-detail.css     # 상세 페이지 스타일
└── variants/
    ├── corporate.css           # 법인 오버라이드
    └── personal.css            # 개인 오버라이드

app/static/js/
├── pages/
│   └── employee/               # 통합 JS
│       ├── index.js
│       └── helpers.js
├── services/
│   └── employee-service.js     # API 서비스
└── utils/
    ├── api.js
    └── formatting.js
```

---

### 5.11 성공 지표 (레거시 정리)

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 템플릿 파일 수 | 30% 감소 | `find templates/ -name "*.html" \| wc -l` |
| CSS 파일 크기 | 20% 감소 | 번들 크기 측정 |
| JS 파일 크기 | 15% 감소 | 번들 크기 측정 |
| 중복 코드 | 0개 | 코드 분석 도구 |
| 레거시 URL 호환 | 100% | 리다이렉트 테스트 |
