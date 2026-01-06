# templates/ 디렉토리 가이드

Jinja2 템플릿 파일

## 디렉토리 구조

| 폴더 | 역할 |
|------|------|
| `auth/` | 인증 관련 (로그인, 회원가입) |
| `employees/` | 직원 관리 |
| `contracts/` | 계약 관리 |
| `corporate/` | 법인 관리 |
| `dashboard/` | 대시보드 |
| `admin/` | 관리자 기능 |
| `platform/` | 플랫폼 관리 |
| `profile/` | 프로필 관리 |
| `personal/` | 개인 계정 페이지 |
| `mypage/` | 마이페이지 |
| `components/` | 재사용 컴포넌트 |
| `macros/` | Jinja2 매크로 |
| `partials/` | 부분 템플릿 |

## 기본 레이아웃

| 파일 | 설명 | 사용처 |
|------|------|--------|
| `base.html` | 기본 레이아웃 (로그인 후) | 대부분의 페이지 |
| `base_public.html` | 공개 페이지 레이아웃 | 로그인, 회원가입 |
| `base_error.html` | 에러 페이지 레이아웃 | 404, 500 에러 |

## 매크로 (macros/)

| 매크로 | 파일 | 용도 |
|--------|------|------|
| `form_field` | `_forms.html` | 폼 필드 렌더링 |
| `pagination` | `_pagination.html` | 페이지네이션 |
| `avatar` | `_avatar.html` | 아바타 이미지 |
| `contracts_table` | `_contracts.html` | 계약 테이블 |
| `navigation` | `_navigation.html` | 네비게이션 |
| `filters` | `_filters.html` | 필터 컴포넌트 (Phase 28) |
| `settings` | `_settings.html` | 설정 컴포넌트 (Phase 28) |
| `field_renderer` | `_field_renderer.html` | 필드 렌더러 |
| `form_controls` | `_form_controls.html` | 폼 컨트롤 |
| `cards` | `_cards.html` | 카드 컴포넌트 |
| `alerts` | `_alerts.html` | 알림 컴포넌트 |
| `accordion` | `_accordion.html` | 아코디언 |

## 컴포넌트 (components/)

```
components/
├── navigation/
│   ├── _header.html           # 헤더
│   └── _sidebar_unified.html  # 통합 사이드바
├── forms/
│   ├── _select.html           # 선택 필드
│   └── _input.html            # 입력 필드
└── modals/
    └── _confirm.html          # 확인 모달
```

## 부분 템플릿 (partials/)

```
partials/
├── employee_detail/           # 직원 상세
│   ├── _employee_header.html
│   ├── _basic_info.html
│   ├── _personal_info.html
│   └── _hr_records.html
├── employee_form/             # 직원 폼
│   ├── _personal_info.html
│   ├── _organization_info.html
│   ├── _contract_info.html
│   ├── _education_info.html
│   ├── _career_info.html
│   ├── _family_info.html
│   ├── _military_info.html
│   └── _award_info.html
└── profile/                   # 프로필
    ├── _basic_info.html
    └── _education_list.html
```

## 계약 템플릿 (contracts/)

```
contracts/
├── company_list.html          # 법인 계약 목록
├── personal_list.html         # 개인 계약 목록
├── pending_list.html          # 대기 계약 목록
├── company_pending.html       # 법인 대기 계약
├── contract_detail.html       # 계약 상세
└── request_contract.html      # 계약 요청
```

## 법인 템플릿 (corporate/)

```
corporate/
├── settings.html              # 법인 설정
├── users.html                 # 사용자 관리
├── dashboard.html             # 대시보드
└── partials/
    └── settings/              # 설정 부분 템플릿
```

## 규칙

### 템플릿 규칙
- **매크로**: `macros/` 폴더에 정의
- **부분 템플릿**: `partials/` 또는 `_` 접두사 사용
- **인라인 스타일 금지**: 외부 CSS 사용
- **인라인 스크립트 금지**: 외부 JS 사용
- **컴포넌트 재사용**: `components/` 또는 `macros/` 활용

### 네이밍 규칙
```
_filename.html    # 부분 템플릿 (include용)
filename.html     # 독립 페이지
```

### 블록 구조
```jinja2
{% extends "base.html" %}

{% block title %}페이지 제목{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/page.css') }}">
{% endblock %}

{% block content %}
<!-- 페이지 콘텐츠 -->
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/page.js') }}"></script>
{% endblock %}
```

### 매크로 사용
```jinja2
{% from "macros/_forms.html" import form_field %}
{% from "macros/_avatar.html" import avatar %}
{% from "macros/_filters.html" import render_filter_bar %}
{% from "macros/_contracts.html" import contracts_table %}

{{ form_field('name', '이름', required=True) }}
{{ avatar(employee.photo_url, size='lg') }}
{{ render_filter_bar(filters) }}
```

## 템플릿 상속 계층

```
base.html (또는 base_public.html)
    └── 각 페이지 템플릿
        └── partials/_*.html (include)
            └── macros/_*.html (매크로 호출)
```

## 폼 필드 패턴

```jinja2
<!-- FieldOptions 사용 -->
{% for option in field_options.GENDER %}
<option value="{{ option.value }}">{{ option.label }}</option>
{% endfor %}

<!-- FieldRegistry 사용 -->
{% for field in field_registry.get_ordered_names('personal_basic') %}
{% include 'partials/_field_' + field + '.html' %}
{% endfor %}
```

## 필터 컴포넌트 패턴 (Phase 28)

```jinja2
<!-- 필터바 매크로 사용 -->
{% from "macros/_filters.html" import render_filter_bar, render_filter_chips %}

{{ render_filter_bar(
    filters=filters,
    action_url=url_for('employees.list'),
    method='GET'
) }}

{{ render_filter_chips(active_filters) }}
```

## 새 템플릿 추가 규칙

1. **페이지 템플릿**: 해당 Blueprint 폴더에 생성
2. **부분 템플릿**: `partials/` 또는 해당 폴더에 `_` 접두사로 생성
3. **재사용 매크로**: `macros/` 폴더에 추가
4. **관련 CSS/JS**: `static/css/pages/`, `static/js/pages/`에 생성
