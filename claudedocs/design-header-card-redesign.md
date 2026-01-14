# Header Card Redesign - Design Specification

## Overview

모든 계정 타입(personal, corporate, employee_sub)의 헤더카드를 통합 재설계하는 디자인 명세서입니다.

**목표**:
- 계정 타입별 일관된 시각적 경험 제공
- 테마 시스템을 활용한 동적 스타일링
- 반응형 레이아웃 최적화
- 명함 카드 통합 개선

---

## 1. Current State Analysis (현재 상태 분석)

### 1.1 기존 구현 파일

| 구분 | 파일 위치 | 역할 |
|------|----------|------|
| Template | `templates/domains/employee/partials/detail/_employee_header.html` | 통합 헤더 템플릿 |
| CSS | `static/css/domains/employee/header.css` | 헤더 스타일 (203 lines) |
| Theme | `static/css/shared/core/theme.css` | 계정별 테마 변수 |
| Variables | `static/css/shared/core/variables.css` | 디자인 시스템 변수 |

### 1.2 현재 계정 타입별 구현

| 계정 타입 | 테마 색상 | 표시 정보 | 명함 영역 |
|----------|----------|----------|----------|
| corporate | Blue (#2563EB) | 소속정보, 고용정보 | O (업로드/삭제) |
| employee_sub | Purple (#7C3AED) | 소속정보, 고용정보 | O (업로드/삭제) |
| personal | Green (#059669) | 연락처, 개인정보 | X |

### 1.3 현재 문제점

1. **테마 시스템 미활용**: `--theme-*` 변수 대신 하드코딩된 색상 사용
2. **variant 기반 분기**: CSS 클래스 기반 대신 inline variant 로직
3. **명함 영역 불일치**: personal에서 명함 조회 불가 (계약된 법인 명함)
4. **반응형 제한**: 태블릿 사이즈 최적화 부족

---

## 2. Redesign Goals (재설계 목표)

### 2.1 핵심 원칙

1. **Theme-First Design**: `--theme-*` CSS 변수 기반 동적 스타일링
2. **Component Composition**: 재사용 가능한 서브 컴포넌트 분리
3. **Progressive Enhancement**: 기본 기능 → 확장 기능 점진적 적용
4. **Accessibility**: WCAG 2.1 AA 준수

### 2.2 기능 요구사항

| 요구사항 | 우선순위 | 설명 |
|---------|---------|------|
| 테마 자동 적용 | P0 | `data-account-type` 기반 자동 테마 전환 |
| 통합 헤더 구조 | P0 | 모든 계정에서 일관된 레이아웃 |
| 명함 조회 확장 | P1 | personal에서 계약 법인 명함 조회 |
| 반응형 최적화 | P1 | 모바일/태블릿/데스크톱 최적화 |
| 애니메이션 개선 | P2 | 부드러운 전환 효과 |

---

## 3. Component Architecture (컴포넌트 아키텍처)

### 3.1 컴포넌트 구조

```
ProfileHeaderCard (통합 헤더 컴포넌트)
├── ProfileAvatar (아바타 컴포넌트)
│   ├── 사진 이미지
│   └── Initial 폴백
├── ProfileInfo (정보 영역)
│   ├── ProfileName (이름 + 영문명)
│   ├── ProfileMeta (메타 정보 - variant별)
│   │   ├── corporate: 부서, 직책, 상태
│   │   ├── employee_sub: 부서, 직책, 상태
│   │   └── personal: 이메일, 전화, 주소
│   └── ProfileStats (통계 그리드 - variant별)
│       ├── corporate: 입사일, 재직기간, 연차, 사번
│       ├── employee_sub: 입사일, 재직기간, 연차, 사번
│       └── personal: 생년월일, 계약수, 가입일, 회원번호
└── ProfileCard (선택적 - 명함/액션 영역)
    ├── BusinessCard (명함 컴포넌트)
    └── CardActions (업로드/삭제 버튼)
```

### 3.2 데이터 흐름

```
┌─────────────────────────────────────────────────────────┐
│  Template Context                                       │
│  ┌─────────────────────────────────────────────────────│
│  │ employee/profile: 프로필 데이터                      │
│  │ account_type: 계정 타입 (자동 감지)                   │
│  │ variant: 'corporate' | 'personal' (자동 감지)        │
│  │ business_card_*: 명함 첨부파일 (선택)                │
│  │ can_edit_*: 편집 권한 (선택)                        │
│  └─────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  CSS Theme System                                       │
│  ┌─────────────────────────────────────────────────────│
│  │ [data-account-type="corporate"]                     │
│  │   --theme-gradient: blue-600 → blue-800             │
│  │   --theme-primary: blue-600                         │
│  │                                                     │
│  │ [data-account-type="personal"]                      │
│  │   --theme-gradient: personal-500 → personal-700     │
│  │   --theme-primary: personal-500                     │
│  │                                                     │
│  │ [data-account-type="employee_sub"]                  │
│  │   --theme-gradient: employee-500 → employee-700     │
│  │   --theme-primary: employee-500                     │
│  └─────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────┘
```

---

## 4. Visual Design (시각 디자인)

### 4.1 레이아웃 스펙

```
┌─────────────────────────────────────────────────────────────────┐
│  PROFILE HEADER CARD                                           │
│  ┌────────────────────────────────────────┬──────────────────┐ │
│  │  LEFT SECTION (flex: 1)                │  RIGHT SECTION   │ │
│  │  ┌──────┐  ┌─────────────────────────┐ │  (명함 영역)     │ │
│  │  │      │  │ Name                     │ │  ┌────────────┐ │ │
│  │  │ 120px│  │ ENGLISH NAME             │ │  │            │ │ │
│  │  │      │  │                          │ │  │  Business  │ │ │
│  │  │Avatar│  │ [Icon] Meta Item 1       │ │  │    Card    │ │ │
│  │  │      │  │ [Icon] Meta Item 2       │ │  │            │ │ │
│  │  │      │  │ [Icon] Meta Item 3       │ │  │            │ │ │
│  │  └──────┘  │                          │ │  └────────────┘ │ │
│  │            │ ┌──────────────────────┐ │ │  [Actions]      │ │
│  │            │ │ Stats Grid (4 cols)  │ │ │                 │ │
│  │            │ │ Stat1 Stat2 Stat3 Stat4│ │                 │ │
│  │            │ └──────────────────────┘ │ │                 │ │
│  │            └─────────────────────────┘ │                  │ │
│  └────────────────────────────────────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

Desktop: 1200px+
├── Left Section: flex: 1, min-width: 0
├── Right Section: flex: 0 0 380px (명함 포함 시)
└── Gap: 24px (var(--space-6))

Tablet: 768px - 1199px
├── Left Section: 100% width
├── Right Section: 100% width (아래로 이동)
└── Gap: 16px (var(--space-4))

Mobile: < 768px
├── 세로 스택 레이아웃
├── Avatar: 80px, centered
└── Stats Grid: 2 columns
```

### 4.2 색상 시스템

```css
/* 테마 그라디언트 배경 */
.profile-header {
    background: var(--theme-gradient);
}

/* 계정 타입별 그라디언트 */
:root {
    --theme-gradient: linear-gradient(135deg, var(--color-blue-600) 0%, var(--color-blue-800) 100%);
}

[data-account-type="personal"] {
    --theme-gradient: linear-gradient(135deg, var(--color-personal-500) 0%, var(--color-personal-700) 100%);
}

[data-account-type="employee_sub"] {
    --theme-gradient: linear-gradient(135deg, var(--color-employee-500) 0%, var(--color-employee-700) 100%);
}
```

### 4.3 타이포그래피

| 요소 | 크기 | 무게 | 색상 |
|------|------|------|------|
| 이름 | var(--text-3xl) / 24px | 700 | --color-pure-white |
| 영문명 | var(--text-lg) / 16px | 400 | opacity: 0.9 |
| 메타 항목 | var(--text-base) / 14px | 400 | --color-pure-white |
| 통계 라벨 | var(--text-sm) / 13px | 400 | opacity: 0.8 |
| 통계 값 | var(--text-xl) / 18px | 600 | --color-pure-white |

### 4.4 간격 시스템

| 요소 | 값 | CSS 변수 |
|------|------|----------|
| 헤더 패딩 | 32px | var(--space-8) |
| 섹션 간격 | 24px | var(--space-6) |
| 메타 항목 간격 | 24px | var(--space-6) |
| 통계 그리드 간격 | 16px | var(--space-4) |
| 아바타-정보 간격 | 24px | var(--space-6) |

---

## 5. CSS Architecture (CSS 아키텍처)

### 5.1 새로운 CSS 변수 추가

```css
/* static/css/shared/core/variables.css - 추가 */
:root {
    /* Profile Header - 레이아웃 */
    --profile-header-padding: var(--space-8);
    --profile-header-padding-mobile: var(--space-5);
    --profile-header-gap: var(--space-6);
    --profile-header-radius: var(--radius-xl);

    /* Profile Avatar */
    --profile-avatar-size: 120px;
    --profile-avatar-size-mobile: 80px;
    --profile-avatar-border-width: 4px;
    --profile-avatar-border-color: var(--color-white-opacity-30);

    /* Profile Stats */
    --profile-stats-columns: 4;
    --profile-stats-columns-mobile: 2;
    --profile-stats-gap: var(--space-4);

    /* Profile Card (명함 영역) */
    --profile-card-width: 380px;
    --profile-card-width-tablet: 100%;
}
```

### 5.2 theme.css 확장

```css
/* static/css/shared/core/theme.css - 추가 */

/* Profile Header 테마 변수 */
:root {
    --theme-header-bg: var(--theme-gradient);
    --theme-header-text: var(--color-pure-white);
    --theme-header-text-muted: var(--color-white-opacity-80);
    --theme-header-border: var(--color-white-opacity-20);
    --theme-header-avatar-border: var(--color-white-opacity-30);
}

[data-account-type="personal"] {
    --theme-header-avatar-border: var(--color-white-opacity-40);
}
```

### 5.3 컴포넌트 CSS 구조

```
static/css/shared/components/
└── profile-header.css (신규)
    ├── .profile-header (컨테이너)
    ├── .profile-header__content (내부 레이아웃)
    ├── .profile-header__left (좌측 영역)
    ├── .profile-header__right (우측 영역)
    ├── .profile-header__avatar (아바타)
    ├── .profile-header__info (정보 영역)
    ├── .profile-header__name (이름)
    ├── .profile-header__meta (메타 정보)
    ├── .profile-header__stats (통계 그리드)
    └── Responsive Styles
```

---

## 6. Template Structure (템플릿 구조)

### 6.1 새로운 템플릿 구조

```
templates/shared/components/
└── _profile_header.html (신규 - 통합 컴포넌트)

templates/shared/components/profile-header/
├── _avatar.html (아바타 서브 컴포넌트)
├── _meta_corporate.html (법인 메타 정보)
├── _meta_personal.html (개인 메타 정보)
├── _stats_corporate.html (법인 통계)
├── _stats_personal.html (개인 통계)
└── _card_section.html (명함 섹션)
```

### 6.2 통합 템플릿 인터페이스

```jinja2
{#
    통합 프로필 헤더 컴포넌트

    Parameters:
    - profile: 프로필/직원 데이터 객체 (필수)
    - account_type: 계정 타입 (자동 감지)
    - variant: 'corporate' | 'personal' (자동 감지)
    - show_business_card: 명함 표시 여부 (기본: variant == 'corporate')
    - business_card_front: 명함 앞면 첨부파일
    - business_card_back: 명함 뒷면 첨부파일
    - can_edit_business_card: 명함 편집 권한
    - custom_stats: 커스텀 통계 항목 (선택)
    - custom_meta: 커스텀 메타 항목 (선택)
    - extra_classes: 추가 CSS 클래스 (선택)
#}
{% include 'shared/components/_profile_header.html' %}
```

---

## 7. Migration Plan (마이그레이션 계획)

### 7.1 Phase 1: CSS 변수 확장 (Low Risk)

1. `variables.css`에 Profile Header 변수 추가
2. `theme.css`에 Header 테마 변수 추가
3. 기존 `header.css` 유지 (fallback)

### 7.2 Phase 2: 새 컴포넌트 생성 (Medium Risk)

1. `profile-header.css` 신규 생성
2. `_profile_header.html` 통합 템플릿 생성
3. 서브 컴포넌트 템플릿 생성

### 7.3 Phase 3: 기존 페이지 마이그레이션 (High Risk)

1. `profile/detail.html` - 새 컴포넌트 적용
2. `mypage/company_info.html` - 새 컴포넌트 적용
3. `personal/company_card_detail.html` - 새 컴포넌트 적용
4. 기존 `_employee_header.html` deprecated 표시

### 7.4 Phase 4: 정리 (Low Risk)

1. 기존 `header.css` 레거시 코드 제거
2. 기존 `_employee_header.html` 제거
3. 문서 업데이트

---

## 8. Responsive Breakpoints (반응형 중단점)

### 8.1 브레이크포인트 정의

| 이름 | 범위 | 레이아웃 |
|------|------|----------|
| Desktop | 1200px+ | 2열 (정보 + 명함) |
| Tablet | 768px - 1199px | 1열 (명함 아래로) |
| Mobile | < 768px | 1열 (세로 스택) |

### 8.2 반응형 동작

```css
/* Desktop (기본) */
.profile-header__content {
    display: flex;
    align-items: center;
    gap: var(--profile-header-gap);
}

.profile-header__left {
    flex: 1;
    min-width: 0;
}

.profile-header__right {
    flex: 0 0 var(--profile-card-width);
}

/* Tablet */
@media (max-width: 1199px) {
    .profile-header__content {
        flex-direction: column;
    }

    .profile-header__right {
        width: 100%;
        flex: none;
    }
}

/* Mobile */
@media (max-width: 767px) {
    .profile-header {
        padding: var(--profile-header-padding-mobile);
    }

    .profile-header__left {
        flex-direction: column;
        text-align: center;
    }

    .profile-header__avatar {
        width: var(--profile-avatar-size-mobile);
        height: var(--profile-avatar-size-mobile);
    }

    .profile-header__stats {
        grid-template-columns: repeat(var(--profile-stats-columns-mobile), 1fr);
    }
}
```

---

## 9. Accessibility (접근성)

### 9.1 WCAG 2.1 AA 준수 항목

| 항목 | 요구사항 | 구현 방법 |
|------|---------|----------|
| 색상 대비 | 4.5:1 이상 | 흰색 텍스트 on 그라디언트 |
| 키보드 접근 | 모든 인터랙티브 요소 | focus-visible 스타일 |
| 스크린 리더 | 의미론적 마크업 | ARIA labels |
| Motion Reduce | 애니메이션 비활성화 | prefers-reduced-motion |

### 9.2 ARIA 레이블

```html
<div class="profile-header" role="banner" aria-label="프로필 정보">
    <img class="profile-header__avatar-img" alt="[이름]의 프로필 사진" />
    <div class="profile-header__stats" role="list" aria-label="프로필 통계">
        <div class="stat-item" role="listitem">...</div>
    </div>
</div>
```

---

## 10. File Changes Summary (파일 변경 요약)

### 10.1 신규 생성 파일

| 파일 | 역할 |
|------|------|
| `css/shared/components/profile-header.css` | 프로필 헤더 스타일 |
| `templates/shared/components/_profile_header.html` | 통합 헤더 템플릿 |
| `templates/shared/components/profile-header/_avatar.html` | 아바타 컴포넌트 |
| `templates/shared/components/profile-header/_meta_corporate.html` | 법인 메타 |
| `templates/shared/components/profile-header/_meta_personal.html` | 개인 메타 |
| `templates/shared/components/profile-header/_stats_corporate.html` | 법인 통계 |
| `templates/shared/components/profile-header/_stats_personal.html` | 개인 통계 |
| `templates/shared/components/profile-header/_card_section.html` | 명함 섹션 |

### 10.2 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `css/shared/core/variables.css` | Profile Header 변수 추가 |
| `css/shared/core/theme.css` | Header 테마 변수 추가 |
| `templates/domains/user/profile/detail.html` | 새 컴포넌트 적용 |
| `templates/domains/user/mypage/company_info.html` | 새 컴포넌트 적용 |
| `templates/domains/user/personal/company_card_detail.html` | 새 컴포넌트 적용 |

### 10.3 Deprecated 파일

| 파일 | 상태 |
|------|------|
| `templates/domains/employee/partials/detail/_employee_header.html` | Deprecated (Phase 4에서 제거) |
| `css/domains/employee/header.css` | 일부 코드 deprecated |

---

## 11. Testing Checklist (테스트 체크리스트)

### 11.1 기능 테스트

- [ ] Corporate 계정 헤더 렌더링
- [ ] Personal 계정 헤더 렌더링
- [ ] Employee Sub 계정 헤더 렌더링
- [ ] 명함 표시/숨김 토글
- [ ] 명함 업로드 버튼 동작
- [ ] 명함 삭제 버튼 동작

### 11.2 반응형 테스트

- [ ] Desktop (1200px+) 레이아웃
- [ ] Tablet (768px - 1199px) 레이아웃
- [ ] Mobile (< 768px) 레이아웃
- [ ] Portrait/Landscape 전환

### 11.3 접근성 테스트

- [ ] 키보드 네비게이션
- [ ] 스크린 리더 호환성
- [ ] 색상 대비 검증
- [ ] Motion Reduce 동작

### 11.4 브라우저 테스트

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## 12. Appendix (부록)

### A. CSS 변수 전체 목록

```css
/* Profile Header Variables */
--profile-header-padding: var(--space-8);
--profile-header-padding-mobile: var(--space-5);
--profile-header-gap: var(--space-6);
--profile-header-radius: var(--radius-xl);
--profile-avatar-size: 120px;
--profile-avatar-size-mobile: 80px;
--profile-avatar-border-width: 4px;
--profile-avatar-border-color: var(--color-white-opacity-30);
--profile-stats-columns: 4;
--profile-stats-columns-mobile: 2;
--profile-stats-gap: var(--space-4);
--profile-card-width: 380px;
--profile-card-width-tablet: 100%;

/* Theme Variables (per account type) */
--theme-header-bg: var(--theme-gradient);
--theme-header-text: var(--color-pure-white);
--theme-header-text-muted: var(--color-white-opacity-80);
--theme-header-border: var(--color-white-opacity-20);
--theme-header-avatar-border: var(--color-white-opacity-30);
```

### B. BEM 클래스 명명 규칙

```
.profile-header                    /* Block */
.profile-header--compact           /* Block Modifier */
.profile-header__content           /* Element */
.profile-header__left              /* Element */
.profile-header__right             /* Element */
.profile-header__avatar            /* Element */
.profile-header__avatar--large     /* Element Modifier */
.profile-header__info              /* Element */
.profile-header__name              /* Element */
.profile-header__meta              /* Element */
.profile-header__stats             /* Element */
.profile-header__card              /* Element */
```

### C. 관련 문서 링크

- [CLAUDE.md](/CLAUDE.md) - 프로젝트 가이드
- [Theme System](/app/static/css/shared/core/theme.css) - 테마 시스템
- [CSS Variables](/app/static/css/shared/core/variables.css) - CSS 변수
- [BusinessCard Domain](/app/domains/businesscard/) - 명함 도메인

---

**작성일**: 2026-01-14
**작성자**: Claude (Design Mode)
**버전**: 1.0
