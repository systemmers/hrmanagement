# static/ 디렉토리 가이드

프론트엔드 정적 파일 (CSS, JavaScript, 이미지)

## 디렉토리 구조

| 폴더 | 역할 |
|------|------|
| `css/` | 스타일시트 |
| `js/` | JavaScript 모듈 |
| `images/` | 정적 이미지 |
| `uploads/` | 사용자 업로드 파일 |

## CSS 구조 (SSOT)

```
css/
├── core/                   # 기본 스타일
│   ├── variables.css       # CSS 변수 SSOT (색상, 간격, 폰트)
│   ├── reset.css           # 브라우저 리셋
│   ├── theme.css           # 테마 (personal, employee, platform)
│   └── responsive.css      # 반응형
├── layouts/                # 레이아웃
│   ├── header.css
│   ├── sidebar.css
│   ├── main-content.css
│   ├── section-nav.css     # 섹션 네비게이션
│   ├── public-header.css   # 공개 헤더
│   └── public-footer.css   # 공개 푸터
├── components/             # 컴포넌트 (30+ 파일)
│   ├── button.css
│   ├── forms.css
│   ├── table.css
│   ├── modal.css
│   ├── filter.css          # 필터 컴포넌트 (Phase 28)
│   ├── page-header.css     # 페이지 헤더
│   ├── data-table-advanced.css
│   ├── badge.css
│   ├── card.css
│   ├── contract.css        # 계약 관련
│   ├── dashboard.css
│   ├── employee-header.css
│   ├── info-grid.css
│   ├── notification.css
│   ├── salary-allowance.css
│   ├── salary-modal.css
│   ├── stats-cards.css
│   ├── tabs.css
│   └── tree-selector.css
└── pages/                  # 페이지별 (15+ 파일)
    ├── login.css
    ├── employee-form.css
    ├── employee-detail.css
    ├── profile.css
    ├── dashboard.css
    ├── contract-detail.css
    ├── contract-request.css
    ├── company-card-list.css
    ├── company-card-detail.css
    ├── organization.css
    ├── platform.css
    ├── landing.css
    ├── ai-test.css
    ├── admin-profile.css
    └── register-select.css
```

## JavaScript 구조

```
js/
├── app.js                  # 메인 앱 (전역 초기화)
├── core/                   # 핵심 모듈 (SSOT)
│   ├── field-registry.js   # 필드 메타데이터
│   └── template-generator.js
├── components/             # 재사용 컴포넌트
│   ├── data-table/         # 고급 테이블 시스템
│   ├── salary/             # 급여 계산기
│   ├── filter.js           # 필터 컴포넌트
│   ├── filter-bar.js       # 필터바 (Phase 28)
│   ├── toast.js            # 토스트 알림
│   ├── accordion.js        # 아코디언
│   ├── file-upload.js      # 파일 업로드
│   ├── business-card.js    # 명함 컴포넌트
│   ├── notification-dropdown.js
│   ├── section-nav.js      # 섹션 네비게이션
│   └── tree-selector.js    # 트리 선택기
├── pages/                  # 페이지별 스크립트
│   ├── employee/           # 직원 관련
│   │   ├── validators.js
│   │   ├── dynamic-sections.js
│   │   └── templates.js
│   ├── employee-list.js
│   ├── contracts.js
│   ├── corporate-settings.js
│   ├── platform.js         # 플랫폼 페이지 (Phase 28)
│   └── profile/            # 프로필 관련
├── services/               # API 통신
│   └── contract-service.js
├── utils/                  # 유틸리티
│   ├── format.js
│   ├── api.js              # API 통신 헬퍼
│   └── validation.js
└── constants/              # JS 상수
```

## 규칙

### CSS 규칙
- **CSS 변수**: `core/variables.css`에서 정의 (SSOT)
- **하드코딩 색상 금지**: `var(--color-*)` 사용
- **인라인 스타일 금지**: 외부 CSS 파일 사용
- **클래스명**: BEM 또는 기능 기반 네이밍

```css
/* 올바른 방법 */
color: var(--color-primary-500);
background: var(--color-gray-100);

/* 금지 */
color: #3b82f6;
background: #f3f4f6;
```

### JavaScript 규칙
- **인라인 스크립트 금지**: 외부 JS 파일 사용
- **인라인 이벤트 핸들러 금지**: `addEventListener` 사용
- **API 통신**: `services/` 또는 `utils/api.js` 사용
- **DOM 조작**: `classList.add/remove` 사용 (`style.display` 금지)

```javascript
// 올바른 방법
element.classList.add('hidden');
element.classList.remove('hidden');

// 금지
element.style.display = 'none';
element.style.display = 'block';
```

## 핵심 컴포넌트

| 컴포넌트 | 위치 | 설명 |
|---------|------|------|
| DataTable | `components/data-table/` | 정렬, 필터, 페이지네이션 |
| FilterBar | `components/filter-bar.js` | 고급 필터 시스템 |
| Salary Calculator | `components/salary/` | 급여 계산 |
| Toast | `components/toast.js` | 알림 메시지 |
| Dynamic Sections | `pages/employee/dynamic-sections.js` | 동적 섹션 관리 |
| TreeSelector | `components/tree-selector.js` | 조직 트리 선택 |
| FileUpload | `components/file-upload.js` | 파일 업로드 |

## CSS 변수 참조

```css
/* 색상 */
--color-primary-500: #3b82f6;
--color-success-500: #10b981;
--color-error-500: #ef4444;
--color-warning-500: #f59e0b;

/* 테마 색상 */
--personal-primary: #10b981;    /* 개인 계정 */
--employee-primary: #3b82f6;    /* 법인 직원 */
--platform-primary: #6366f1;    /* 플랫폼 */

/* 간격 */
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;

/* 레이아웃 */
--sidebar-width: 260px;
--header-height: 64px;
```

## 새 파일 추가 규칙

1. **CSS 파일**: `components/` 또는 `pages/` 하위에 생성
2. **JS 파일**: 기능에 따라 적절한 폴더에 배치
3. **base.html**에서 CSS/JS 참조 추가 또는 페이지별 `extra_css`/`extra_js` 블록 사용

## 백엔드 도메인과의 연관

| 백엔드 도메인 | 프론트엔드 위치 |
|--------------|----------------|
| `employee` | `pages/employee/`, `pages/employee-list.js` |
| `contract` | `pages/contracts.js`, `services/contract-service.js` |
| `company` | `pages/corporate-settings.js`, `pages/organization.js` |
| `user` | `pages/profile/`, `pages/auth.js` |
| `platform` | `pages/platform.js`, `pages/ai-test-index.js` |

프론트엔드는 현재 도메인 구조 없이 기능별로 분류되어 있으며, 향후 도메인 중심 리팩토링 계획 있음.
