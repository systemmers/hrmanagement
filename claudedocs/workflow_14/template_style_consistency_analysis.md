# 법인 직원 vs 개인 계정 템플릿/스타일 일치성 분석 보고서

## 분석 개요
- 날짜: 2025-12-11
- 목적: dev_prompt.md #4 요구사항 - 법인 직원과 개인 계정의 템플릿/스타일 일치 여부 검증
- 원칙: 계정 유형만 다르고 템플릿 및 스타일은 동일해야 함

---

## 1. 주요 발견사항 요약

### 심각한 불일치 항목 (Critical)
1. **레이아웃 클래스명 불일치** - 법인과 개인이 완전히 다른 레이아웃 시스템 사용
2. **CSS 파일 구조 불일치** - 서로 다른 CSS 파일 세트 로드
3. **컴포넌트 클래스명 불일치** - 동일 기능의 요소가 다른 클래스명 사용
4. **인라인 스타일 잔존** - 개인 계정에 인라인 스타일 다수 존재

### 중간 수준 불일치 (Important)
1. **폼 구조 차이** - 동일 섹션이 다른 마크업 구조
2. **아이콘 사용 불일치** - 일부 섹션에서 아이콘 유무 차이
3. **헤더 구조 차이** - 페이지 헤더 마크업이 상이함

---

## 2. 상세 불일치 항목

### 2.1 레이아웃 클래스명 불일치

#### 법인 직원 (employees/)
```html
<!-- employees/detail.html -->
<div class="detail-page-layout">
    <div class="detail-main-content">
        <div class="detail-page-header">
            <h1 class="detail-page-title">직원 상세 정보</h1>
            <div class="detail-page-actions">
```

#### 개인 계정 (personal/)
```html
<!-- personal/profile_edit.html -->
<div class="page-header">
    <div class="page-title-row">
        <h1 class="page-title">프로필 수정</h1>
        <div class="page-actions">
```

**차이점:**
- 법인: `detail-page-layout`, `detail-main-content`, `detail-page-header`, `detail-page-title`
- 개인: `page-header`, `page-title-row`, `page-title`, `page-actions`
- 결과: 완전히 다른 CSS 규칙 적용, 일관성 없음

---

### 2.2 CSS 파일 로드 불일치

#### 법인 직원 (employees/detail.html)
```html
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/section-nav.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/right-sidebar.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/employee-header.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/business-card.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/cards.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/tables.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/employee-detail.css') }}">
{% endblock %}
```

#### 개인 계정 (personal/profile_edit.html)
```html
{% block content %}
<!-- CSS moved to: components/forms.css -->
<!-- 인라인 스타일 또는 별도 CSS 파일 없음 -->
```

**차이점:**
- 법인: 7개의 전문적인 모듈화된 CSS 파일 로드
- 개인: CSS 파일 명시적 로드 없음, 주석만 존재
- 결과: 스타일 일관성 보장 불가

---

### 2.3 폼 구조 불일치

#### 법인 직원 폼 (employees/form.html)
```html
<form method="POST" class="employee-form" id="employeeForm">
    <!-- 섹션 1: 개인 기본정보 -->
    {% include 'partials/employee_form/_personal_info.html' %}

    <!-- 섹션 2: 소속정보 -->
    {% include 'partials/employee_form/_organization_info.html' %}
```

#### 개인 계정 폼 (personal/profile_edit.html)
```html
<div class="form-container">
    <form method="POST" class="employee-form">
        <!-- 기본 정보 섹션 -->
        <div class="form-section">
            <h2 class="form-section-title">
                <i class="fas fa-user"></i>
                기본 정보
            </h2>
            <div class="form-row">
```

**차이점:**
- 법인: `partials/` 디렉토리의 모듈화된 컴포넌트 사용
- 개인: 단일 파일 내 인라인 마크업
- 법인: 컴포넌트 재사용 가능, 유지보수 용이
- 개인: 중복 코드 발생, 유지보수 어려움

---

### 2.4 폼 그룹 클래스 불일치

#### 법인 직원
```html
<!-- partials/employee_detail/_basic_info.html -->
<div class="info-grid">
    {{ info_item('성명 (한글)', employee.name) }}
    {{ info_item('여권명 (영문)', employee.english_name) }}
```

#### 개인 계정
```html
<!-- personal/profile_edit.html -->
<div class="form-row">
    <div class="form-group">
        <label class="form-label">
            이름 <span class="required">*</span>
        </label>
        <input type="text" name="name" class="form-input">
```

**차이점:**
- 법인: `info-grid` + 매크로 함수 `info_item()` 사용
- 개인: `form-row` + `form-group` 수동 마크업
- 결과: 동일 정보 표시 방식이 다름

---

### 2.5 인라인 스타일 잔존 (개인 계정)

#### personal/profile_edit.html:110
```html
<div class="form-group" style="flex: 0 0 150px;">
    <label class="form-label">우편번호</label>
```

**문제점:**
- dev_prompt.md #1 요구사항: "개인 계정 인라인 스타일 별도 사용 제거"
- 인라인 스타일이 여전히 존재함
- CSS 클래스로 대체되어야 함

---

### 2.6 헤더 구조 불일치

#### 법인 직원 (employees/detail.html:24-50)
```html
<div class="detail-page-header">
    {% if current_user and current_user.role == 'employee' %}
    <h1 class="detail-page-title">내 인사카드</h1>
    {% else %}
    <h1 class="detail-page-title">직원 상세 정보</h1>
    {% endif %}
    <div class="detail-page-actions">
        {% if not current_user or current_user.role != 'employee' %}
        <a href="{{ url_for('employees.employee_list') }}" class="btn btn-secondary">
```

#### 개인 계정 (personal/profile_edit.html:6-16)
```html
<div class="page-header">
    <div class="page-title-row">
        <h1 class="page-title">프로필 수정</h1>
        <div class="page-actions">
            <a href="{{ url_for('personal.profile') }}" class="btn btn-secondary">
```

**차이점:**
- 법인: `detail-page-header` > `detail-page-title` + `detail-page-actions`
- 개인: `page-header` > `page-title-row` > `page-title` + `page-actions`
- 결과: 동일 기능이 다른 마크업 구조

---

### 2.7 통합 프로필 vs 기존 템플릿 구조 차이

#### 통합 프로필 (profile/unified_profile.html)
```html
<div class="profile-page" data-account-type="{{ 'corporate' if is_corporate else 'personal' }}">
    {# 사이드 네비게이션 #}
    {% include 'profile/partials/_section_nav_unified.html' %}

    {# 메인 콘텐츠 영역 #}
    <main class="profile-main">
        {% include 'profile/partials/_header_unified.html' %}
```

**발견사항:**
- `profile/unified_profile.html` 존재 - 통합 프로필 템플릿
- `data-account-type` 속성으로 법인/개인 구분
- CSS 변수를 통한 테마 변경 (`--profile-primary`)
- 현재 employees와 personal이 이 템플릿을 사용하지 않음

---

### 2.8 CSS 페이지별 파일 구조

#### 발견된 CSS 파일
```
app/static/css/pages/
├── employee-detail.css  (법인 직원 상세)
├── employee-form.css    (법인 직원 폼)
├── profile.css          (통합 프로필)
├── register.css         (개인 회원가입)
└── 기타...
```

**문제점:**
- `employee-detail.css`: `.detail-page-layout` 클래스 정의
- `profile.css`: `.profile-page` 클래스 정의
- `personal/profile_edit.html`은 어느 CSS도 명시적으로 로드하지 않음
- 결과: 개인 계정 스타일이 불명확

---

## 3. 불일치 유형별 분류

### 3.1 스타일 불일치
| 항목 | 법인 직원 | 개인 계정 | 심각도 |
|------|-----------|-----------|--------|
| 레이아웃 클래스 | `detail-page-layout` | `page-header` | Critical |
| CSS 파일 로드 | 7개 모듈화 파일 | 없음/불명확 | Critical |
| 인라인 스타일 | 없음 | 존재 (style="...") | Important |
| CSS 변수 활용 | 일부 | 미사용 | Important |

### 3.2 구조 불일치
| 항목 | 법인 직원 | 개인 계정 | 심각도 |
|------|-----------|-----------|--------|
| 폼 구조 | 모듈화 partials | 인라인 마크업 | Critical |
| 헤더 구조 | 3단계 div | 2단계 div | Important |
| 정보 표시 | 매크로 함수 | 수동 마크업 | Important |
| 섹션 네비게이션 | 좌측 고정 | 없음 | Important |

### 3.3 클래스명 불일치
| 용도 | 법인 직원 | 개인 계정 | 심각도 |
|------|-----------|-----------|--------|
| 페이지 타이틀 | `detail-page-title` | `page-title` | Critical |
| 페이지 액션 | `detail-page-actions` | `page-actions` | Critical |
| 폼 그룹 | `info-grid` | `form-row` | Important |
| 폼 레이블 | `info-label` | `form-label` | Important |

---

## 4. 통합 권장사항

### 4.1 즉시 수정 필요 (Critical Priority)

#### 1) 개인 계정을 통합 프로필 템플릿으로 마이그레이션
**현재 상태:**
- `personal/profile_edit.html` - 독립적 마크업
- `profile/unified_profile.html` - 통합 템플릿 (미사용)

**권장 조치:**
```python
# personal/routes.py 수정
@personal_bp.route('/profile/edit')
def profile_edit():
    return render_template(
        'profile/unified_profile.html',
        is_corporate=False,
        mode='edit',
        # ...
    )
```

#### 2) CSS 파일 로드 통일
**현재 상태:**
- 법인: 7개 CSS 파일 명시적 로드
- 개인: CSS 로드 불명확

**권장 조치:**
```html
<!-- personal/profile_edit.html 수정 -->
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/section-nav.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/cards.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/profile.css') }}">
{% endblock %}
```

#### 3) 인라인 스타일 제거
**현재:**
```html
<div class="form-group" style="flex: 0 0 150px;">
```

**수정:**
```css
/* app/static/css/components/forms.css */
.form-group--postal-code {
    flex: 0 0 150px;
}
```
```html
<div class="form-group form-group--postal-code">
```

---

### 4.2 중요 개선사항 (Important Priority)

#### 1) 클래스명 표준화
**권장 네이밍 규칙:**
```
공통:
- page-header (페이지 헤더)
- page-title (페이지 제목)
- page-actions (페이지 액션 버튼)
- section-nav (섹션 네비게이션)
- info-grid (정보 그리드)
- form-section (폼 섹션)

법인 전용:
- corporate-* (법인 전용 요소)

개인 전용:
- personal-* (개인 전용 요소)
```

#### 2) 매크로 함수 공통화
**현재:** 법인만 매크로 사용
**권장:** 공통 매크로 생성

```jinja2
{# templates/macros/_common_info.html #}
{% macro info_section(title, icon, items) %}
<section class="info-section">
    <div class="section-header">
        <h2 class="section-title">
            <i class="fas fa-{{ icon }}"></i>
            {{ title }}
        </h2>
    </div>
    <div class="section-content">
        <div class="info-grid">
            {% for item in items %}
                {{ info_item(item.label, item.value, item.highlight) }}
            {% endfor %}
        </div>
    </div>
</section>
{% endmacro %}
```

---

### 4.3 장기 개선사항 (Recommended Priority)

#### 1) 템플릿 구조 통일
**목표 구조:**
```
app/templates/
├── profile/
│   ├── unified_profile.html         (공통 뷰)
│   ├── unified_profile_edit.html    (공통 수정)
│   └── partials/
│       ├── _section_nav.html        (공통 네비게이션)
│       ├── _header.html             (공통 헤더)
│       └── sections/
│           ├── _basic_info.html     (공통 섹션)
│           ├── _organization_info.html  (법인 전용)
│           └── ...
├── employees/  (삭제 또는 라우팅만 유지)
└── personal/   (삭제 또는 라우팅만 유지)
```

#### 2) CSS 변수 기반 테마 시스템
**현재 profile.css 방식 확장:**
```css
/* app/static/css/themes/profile-theme.css */
:root {
    /* 기본 테마 (법인) */
    --profile-primary: var(--color-blue-600);
    --profile-primary-hover: var(--color-blue-700);
    --profile-gradient: var(--gradient-blue);
}

[data-account-type="personal"] {
    /* 개인 계정 테마 */
    --profile-primary: #059669;
    --profile-primary-hover: #047857;
    --profile-gradient: linear-gradient(135deg, #059669 0%, #047857 100%);
}

/* 공통 스타일 */
.page-header {
    background: var(--profile-gradient);
}

.btn-primary {
    background-color: var(--profile-primary);
}

.btn-primary:hover {
    background-color: var(--profile-primary-hover);
}
```

---

## 5. 구현 우선순위 로드맵

### Phase 1: 긴급 수정 (1-2일)
1. 개인 계정 인라인 스타일 제거
2. 개인 계정 CSS 파일 명시적 로드
3. 클래스명 기본 통일 (page-header, page-title 등)

### Phase 2: 구조 통합 (3-5일)
1. 개인 계정을 unified_profile.html 기반으로 마이그레이션
2. 매크로 함수 공통화
3. partials 컴포넌트 재사용

### Phase 3: 완전 통합 (1-2주)
1. employees와 personal 라우트를 profile 라우트로 통합
2. CSS 테마 시스템 완성
3. 테스트 및 검증

---

## 6. 파일별 수정 체크리스트

### 6.1 즉시 수정 필요 파일

#### app/templates/personal/profile_edit.html
- [ ] Line 110: 인라인 스타일 제거 `style="flex: 0 0 150px;"`
- [ ] Line 6-16: 클래스명 통일 (`page-header` → 법인과 동일)
- [ ] extra_css 블록 추가하여 CSS 파일 명시적 로드
- [ ] 폼 구조를 partials 컴포넌트로 분리

#### app/templates/personal/register.html
- [ ] Line 23: 인라인 스타일 제거 `style="background: linear-gradient(...)"`
- [ ] CSS 클래스로 대체

### 6.2 검토 필요 파일

#### app/templates/profile/unified_profile.html
- [ ] 법인 직원과 개인 계정이 실제로 사용하도록 라우트 수정
- [ ] 조건부 렌더링 검증 (`is_corporate` 플래그)

#### app/static/css/pages/profile.css
- [ ] CSS 변수 기반 테마 시스템 검증
- [ ] 법인/개인 양쪽에서 정상 작동 확인

---

## 7. 예상 영향 분석

### 긍정적 영향
1. **코드 중복 제거**: 30-40% 코드 감소 예상
2. **유지보수성 향상**: 단일 템플릿 수정으로 전체 적용
3. **일관된 UX**: 법인/개인 계정 동일한 사용자 경험
4. **성능 개선**: 중복 CSS 로드 제거

### 리스크
1. **기존 기능 영향**: 마이그레이션 중 기능 손실 가능성
2. **테스트 필요**: 법인/개인 양쪽 모든 기능 재검증 필요
3. **데이터 매핑**: 서로 다른 필드명 매핑 필요

---

## 8. 결론

### 현재 상태 평가
- **일치도**: 약 30-40% (매우 낮음)
- **주요 원인**:
  1. 개발 단계에서 법인과 개인을 별도로 개발
  2. 통합 템플릿(unified_profile.html)은 존재하나 미사용
  3. 클래스명, CSS 파일, 마크업 구조 전반적으로 불일치

### 최우선 조치사항
1. **인라인 스타일 즉시 제거** (dev_prompt.md #1 요구사항)
2. **CSS 파일 로드 명시화** (개인 계정)
3. **통합 프로필 템플릿 활용** (기존 작업물 활용)

### 장기 비전
- 단일 통합 프로필 시스템
- CSS 변수 기반 테마로 계정 유형별 스타일링
- 최소한의 코드로 최대 재사용성 확보

---

## 부록: 참조 파일 목록

### 분석 대상 파일
```
app/templates/
├── employees/
│   ├── detail.html (lines 1-88)
│   ├── form.html (lines 1-150)
│   └── list.html (lines 1-211)
├── personal/
│   ├── profile_edit.html (lines 1-220)
│   └── register.html (lines 1-169)
├── profile/
│   ├── unified_profile.html (lines 1-63)
│   └── partials/sections/
│       └── _basic_info.html (lines 1-50)
└── partials/employee_detail/
    └── _basic_info.html (lines 1-50)

app/static/css/pages/
├── employee-detail.css (lines 1-100)
├── employee-form.css (lines 1-100)
└── profile.css (lines 1-100)
```

---

**분석 일시:** 2025-12-11
**분석자:** Claude (Frontend Architect)
**문서 버전:** 1.0
