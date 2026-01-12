# templates/ 디렉토리 가이드

Jinja2 템플릿 파일 - 도메인 중심 아키텍처

## 디렉토리 구조

```
templates/
├── domains/                    # 도메인별 템플릿 (7개 도메인)
│   ├── company/                # 법인 도메인
│   │   ├── corporate/          # 법인 관리 페이지
│   │   ├── organization/       # 조직 관리
│   │   └── settings/           # 법인 설정
│   ├── contract/               # 계약 도메인
│   │   └── contracts/          # 계약 페이지
│   ├── employee/               # 직원 도메인
│   │   ├── employees/          # 직원 관리 페이지
│   │   └── partials/           # 직원 전용 부분 템플릿
│   │       ├── detail/         # 상세 페이지용
│   │       └── form/           # 폼 페이지용
│   ├── platform/               # 플랫폼 도메인
│   │   ├── admin/              # 관리자 페이지
│   │   └── ai/                 # AI 테스트
│   ├── user/                   # 사용자 도메인
│   │   ├── auth/               # 인증 (로그인, 회원가입)
│   │   ├── dashboard/          # 대시보드
│   │   ├── mypage/             # 마이페이지
│   │   ├── personal/           # 개인 프로필
│   │   └── profile/            # 프로필 관리
│   ├── attachment/             # 첨부파일 도메인 (2026-01-10 신규)
│   │   └── partials/           # 첨부파일 관련 부분 템플릿
│   └── businesscard/           # 명함 도메인 (2026-01-09 신규)
│       └── partials/
│           └── _card.html      # 명함 카드 컴포넌트
├── errors/                     # 에러 페이지 (400, 403, 404, 500)
├── examples/                   # 예제 페이지
├── shared/                     # 공유 템플릿
│   ├── base.html               # 기본 레이아웃 (로그인 후)
│   ├── base_error.html         # 에러 페이지 레이아웃
│   ├── base_public.html        # 공개 페이지 레이아웃
│   ├── layouts/                # 레이아웃 부분 템플릿
│   │   └── _sidebar_unified.html
│   ├── macros/                 # Jinja2 매크로 (10개)
│   └── partials/               # 공유 부분 템플릿 (6개)
├── index.html
└── landing.html
```

## 도메인별 템플릿

| 도메인 | 폴더 | 주요 페이지 |
|--------|------|-------------|
| company | `domains/company/` | 법인 설정, 조직 관리, 사용자 관리 |
| contract | `domains/contract/` | 계약 목록, 상세, 요청 |
| employee | `domains/employee/` | 직원 목록, 상세, 등록/수정 |
| platform | `domains/platform/` | 관리자 페이지, AI 테스트 |
| user | `domains/user/` | 인증, 대시보드, 마이페이지, 프로필 |
| attachment | `domains/attachment/` | 첨부파일 관련 부분 템플릿 |
| businesscard | `domains/businesscard/` | 명함 카드 컴포넌트 (partials) |

## 공유 자원 (shared/)

### 기본 레이아웃

| 파일 | 설명 | 사용처 |
|------|------|--------|
| `shared/base.html` | 기본 레이아웃 (로그인 후) | 대부분의 페이지 |
| `shared/base_public.html` | 공개 페이지 레이아웃 | 로그인, 회원가입, 랜딩 |
| `shared/base_error.html` | 에러 페이지 레이아웃 | 404, 500 에러 |

### 매크로 (shared/macros/)

| 매크로 | 파일 | 용도 |
|--------|------|------|
| `form_field` | `_forms.html` | 폼 필드 렌더링 |
| `pagination` | `_pagination.html` | 페이지네이션 |
| `avatar` | `_avatar.html` | 아바타 이미지 |
| `contracts_table` | `_contracts.html` | 계약 테이블 |
| `filters` | `_filters.html` | 필터 컴포넌트 |
| `settings` | `_settings.html` | 설정 컴포넌트 |
| `field_renderer` | `_field_renderer.html` | 필드 렌더러 |
| `form_controls` | `_form_controls.html` | 폼 컨트롤 |
| `cards` | `_cards.html` | 카드 컴포넌트 |
| `alerts` | `_alerts.html` | 알림 컴포넌트 |
| `accordion` | `_accordion.html` | 아코디언 |

### 부분 템플릿 (shared/partials/)

| 파일 | 용도 |
|------|------|
| `_contract_header.html` | 계약 헤더 |
| `_contract_info.html` | 계약 정보 |
| `_data_sharing_info.html` | 데이터 공유 정보 |
| `_employment_status.html` | 고용 상태 |
| `_personal_info_display.html` | 개인정보 표시 |
| `_profile_summary.html` | 프로필 요약 |

### 레이아웃 (shared/layouts/)

| 파일 | 용도 |
|------|------|
| `_sidebar_unified.html` | 통합 사이드바 |

## 직원 도메인 부분 템플릿

```
domains/employee/partials/
├── detail/                     # 상세 페이지용
│   ├── _basic_info.html
│   ├── _contract_info.html
│   ├── _employee_header.html
│   ├── _hr_records.html
│   └── _personal_info.html
└── form/                       # 폼 페이지용
    ├── _address_info.html
    ├── _award_info.html
    ├── _career_info.html
    ├── _certificate_info.html
    ├── _contract_info.html
    ├── _disability_info.html
    ├── _education_info.html
    ├── _family_info.html
    ├── _language_info.html
    ├── _military_info.html
    ├── _organization_info.html
    ├── _personal_info.html
    ├── _photo_upload.html
    ├── _position_history_info.html
    ├── _training_info.html
    └── _veteran_info.html
```

## 규칙

### 템플릿 규칙
- **매크로**: `shared/macros/` 폴더에 정의
- **공유 부분 템플릿**: `shared/partials/` 폴더에 정의
- **도메인 부분 템플릿**: `domains/{domain}/partials/` 폴더에 정의
- **인라인 스타일 금지**: 외부 CSS 사용
- **인라인 스크립트 금지**: 외부 JS 사용

### 네이밍 규칙
```
_filename.html    # 부분 템플릿 (include용)
filename.html     # 독립 페이지
```

### 블록 구조
```jinja2
{% extends "shared/base.html" %}

{% block title %}페이지 제목{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/domains/employee/form.css') }}">
{% endblock %}

{% block content %}
<!-- 페이지 콘텐츠 -->
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/domains/employee/pages/form.js') }}"></script>
{% endblock %}
```

### 매크로 사용
```jinja2
{% from "shared/macros/_forms.html" import form_field %}
{% from "shared/macros/_avatar.html" import avatar %}
{% from "shared/macros/_filters.html" import render_filter_bar %}
{% from "shared/macros/_contracts.html" import contracts_table %}

{{ form_field('name', '이름', required=True) }}
{{ avatar(employee.photo_url, size='lg') }}
{{ render_filter_bar(filters) }}
```

### Include 패턴
```jinja2
<!-- 공유 부분 템플릿 -->
{% include 'shared/partials/_profile_summary.html' %}
{% include 'shared/layouts/_sidebar_unified.html' %}

<!-- 도메인 부분 템플릿 -->
{% include 'domains/employee/partials/detail/_basic_info.html' %}
{% include 'domains/employee/partials/form/_education_info.html' %}
```

## 템플릿 상속 계층

```
shared/base.html (또는 shared/base_public.html, shared/base_error.html)
    └── domains/{domain}/pages/*.html (페이지 템플릿)
        ├── domains/{domain}/partials/_*.html (도메인 부분 템플릿)
        ├── shared/partials/_*.html (공유 부분 템플릿)
        └── shared/macros/_*.html (매크로 호출)
```

## 폼 필드 패턴

```jinja2
<!-- FieldOptions 사용 -->
{% for option in field_options.GENDER %}
<option value="{{ option.value }}">{{ option.label }}</option>
{% endfor %}

<!-- FieldRegistry 사용 -->
{% for field in field_registry.get_ordered_names('personal_basic') %}
{% include 'domains/employee/partials/form/_field_' + field + '.html' %}
{% endfor %}
```

## 필터 컴포넌트 패턴

```jinja2
{% from "shared/macros/_filters.html" import render_filter_bar, render_filter_chips %}

{{ render_filter_bar(
    filters=filters,
    action_url=url_for('employees.list'),
    method='GET'
) }}

{{ render_filter_chips(active_filters) }}
```

## 새 템플릿 추가 규칙

1. **페이지 템플릿**: 해당 도메인 폴더에 생성 (`domains/{domain}/`)
2. **도메인 부분 템플릿**: 도메인 partials 폴더에 `_` 접두사로 생성 (`domains/{domain}/partials/`)
3. **공유 부분 템플릿**: `shared/partials/`에 `_` 접두사로 생성
4. **재사용 매크로**: `shared/macros/` 폴더에 추가
5. **관련 CSS/JS**: 도메인 폴더에 생성 (`static/css/domains/{domain}/`, `static/js/domains/{domain}/`)

## Migration History

**Phase 1 완료 (2026-01-07)**
- 도메인 중심 구조로 전환: company, contract, employee, platform, user
- 레거시 폴더 정리: macros/, partials/, components/ 삭제 (root level)
- base.html 이동: root → shared/base.html
- 매크로 이동: macros/ → shared/macros/
- 부분 템플릿 이동: partials/ → shared/partials/
- 직원 부분 템플릿 이동: partials/employee_* → domains/employee/partials/

**BusinessCard 도메인 추가 (2026-01-09)**
- 명함 카드 컴포넌트 추가 (partials/_card.html)

**Attachment 도메인 추가 (2026-01-10)**
- 첨부파일 관련 부분 템플릿 추가
