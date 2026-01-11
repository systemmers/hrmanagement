# static/ 디렉토리 가이드

프론트엔드 정적 파일 (CSS, JavaScript, 이미지) - 도메인 중심 아키텍처

## 디렉토리 구조

| 폴더 | 역할 |
|------|------|
| `css/` | 스타일시트 (도메인 + 공유) |
| `js/` | JavaScript 모듈 (도메인 + 공유) |
| `images/` | 정적 이미지 |
| `uploads/` | 사용자 업로드 파일 |

## CSS 구조 (도메인 중심)

```
css/
├── domains/                    # 도메인별 스타일
│   ├── employee/               # 직원 도메인
│   │   ├── form.css
│   │   ├── detail.css
│   │   ├── header.css
│   │   ├── list.css
│   │   └── salary.css
│   ├── contract/               # 계약 도메인
│   │   ├── detail.css
│   │   ├── list.css
│   │   └── request.css
│   ├── company/                # 법인 도메인
│   │   ├── add-user.css
│   │   ├── organization.css
│   │   ├── settings.css
│   │   └── users.css
│   ├── attachment/             # 첨부파일 도메인 (2026-01-10 신규)
│   │   └── attachment.css      # 첨부파일 스타일
│   ├── user/                   # 사용자 도메인
│   │   ├── account.css
│   │   ├── company-card-detail.css
│   │   ├── company-card-list.css
│   │   ├── dashboard.css
│   │   ├── profile.css
│   │   ├── register.css
│   │   └── register-select.css
│   ├── platform/               # 플랫폼 도메인
│   │   ├── admin-profile.css
│   │   ├── ai-test.css
│   │   └── platform.css
│   └── businesscard/           # 명함 도메인 (2026-01-09 신규)
│       ├── card.css            # 명함 카드 스타일 (프리미엄 3D 플립)
│       └── variables.css       # 명함 전용 CSS 변수
└── shared/                     # 공유 스타일
    ├── core/                   # 기본 스타일 (SSOT)
    │   ├── variables.css       # CSS 변수 (색상, 간격, 폰트)
    │   ├── reset.css           # 브라우저 리셋
    │   ├── theme.css           # 테마 (personal, employee, platform)
    │   ├── utilities.css       # 유틸리티 클래스
    │   └── responsive.css      # 반응형
    ├── layouts/                # 레이아웃
    │   ├── header.css
    │   ├── sidebar.css
    │   ├── main-content.css
    │   ├── section-nav.css
    │   ├── public-header.css
    │   ├── public-footer.css
    │   └── right-sidebar.css
    └── components/             # 재사용 컴포넌트 (30+ 파일)
        ├── accordion.css
        ├── alert.css
        ├── avatar.css
        ├── badge.css
        ├── button.css
        ├── card.css
        ├── data-table-advanced.css
        ├── details.css
        ├── empty-state.css
        ├── filter.css
        ├── forms.css
        ├── image-upload.css
        ├── info-grid.css
        ├── modal.css
        ├── notification.css
        ├── page-header.css
        ├── quick-links.css
        ├── stats-cards.css
        ├── table.css
        ├── tabs.css
        └── tree-selector.css
```

## JavaScript 구조 (도메인 중심)

```
js/
├── app.js                      # 메인 앱 (전역 초기화, HRApp)
├── domains/                    # 도메인별 모듈
│   ├── employee/               # 직원 도메인
│   │   ├── index.js            # 외부 인터페이스 (export)
│   │   ├── services/
│   │   │   └── employee-service.js
│   │   ├── pages/
│   │   │   ├── list.js
│   │   │   ├── form.js
│   │   │   ├── detail.js
│   │   │   ├── validators.js
│   │   │   ├── dynamic-sections.js
│   │   │   └── ...
│   │   └── components/
│   │       ├── business-card.js
│   │       └── salary/
│   ├── contract/               # 계약 도메인
│   │   ├── index.js
│   │   ├── services/
│   │   │   └── contract-service.js
│   │   └── pages/
│   │       ├── list.js
│   │       ├── detail.js
│   │       └── request.js
│   ├── company/                # 법인 도메인
│   │   ├── index.js
│   │   ├── services/
│   │   │   └── settings-api.js
│   │   └── pages/
│   │       ├── settings/           # 법인설정 모듈화 (2026-01-10)
│   │       │   ├── settings.js     # 메인 컨트롤러 (116 lines)
│   │       │   ├── shared/
│   │       │   │   └── constants.js
│   │       │   └── tabs/
│   │       │       ├── org-management.js      # 조직 관리 (656 lines)
│   │       │       ├── documents.js           # 문서 관리 (469 lines)
│   │       │       ├── org-type-settings.js   # 조직유형 설정 (448 lines)
│   │       │       ├── patterns-visibility.js # 패턴/가시성 (433 lines)
│   │       │       ├── audit-logs.js          # 감사 로그 (429 lines)
│   │       │       ├── classifications.js     # 분류체계 (355 lines)
│   │       │       └── org-tree.js            # 조직트리 (363 lines)
│   │       ├── users.js
│   │       └── register.js
│   ├── attachment/             # 첨부파일 도메인 (2026-01-10 신규)
│   │   ├── index.js
│   │   └── services/
│   │       └── attachment-api.js
│   ├── user/                   # 사용자 도메인
│   │   ├── index.js
│   │   └── pages/
│   │       ├── auth.js
│   │       ├── dashboard.js
│   │       ├── profile-sync.js
│   │       └── profile/
│   ├── platform/               # 플랫폼 도메인
│   │   ├── index.js
│   │   └── pages/
│   │       ├── platform.js
│   │       ├── admin.js
│   │       └── ai-test-index.js
│   └── businesscard/           # 명함 도메인 (2026-01-09 신규)
│       ├── index.js            # 외부 인터페이스
│       ├── components/
│       │   ├── BusinessCard.js # 명함 카드 컴포넌트
│       │   └── QRGenerator.js  # QR 코드 생성기
│       └── services/
│           └── businesscard-api.js  # API 통신
└── shared/                     # 공유 모듈
    ├── components/             # 재사용 컴포넌트
    │   ├── data-table/         # 고급 테이블 시스템
    │   ├── accordion.js
    │   ├── file-upload.js
    │   ├── filter-bar.js
    │   ├── form-validator.js
    │   ├── notification-dropdown.js
    │   ├── section-nav.js
    │   ├── toast.js
    │   └── tree-selector.js
    ├── utils/                  # 유틸리티
    │   ├── api.js              # API 통신 헬퍼
    │   ├── dom.js
    │   ├── events.js
    │   ├── formatting.js
    │   └── validation.js
    ├── core/                   # 핵심 모듈 (SSOT)
    │   ├── field-registry.js   # 필드 메타데이터
    │   └── template-generator.js
    └── constants/              # JS 상수
        ├── file-upload-constants.js
        └── ui-constants.js
```

## 도메인 구조 규칙

### 도메인별 파일 배치
| 도메인 | JS 위치 | CSS 위치 | 템플릿 위치 |
|--------|---------|----------|-------------|
| employee | `js/domains/employee/` | `css/domains/employee/` | `templates/domains/employee/` |
| contract | `js/domains/contract/` | `css/domains/contract/` | `templates/domains/contract/` |
| company | `js/domains/company/` | `css/domains/company/` | `templates/domains/company/` |
| user | `js/domains/user/` | `css/domains/user/` | `templates/domains/user/` |
| platform | `js/domains/platform/` | `css/domains/platform/` | `templates/domains/platform/` |
| attachment | `js/domains/attachment/` | `css/domains/attachment/` | `templates/domains/attachment/` |
| businesscard | `js/domains/businesscard/` | `css/domains/businesscard/` | `templates/domains/businesscard/` |

### 공유 자원 배치
| 자원 유형 | JS 위치 | CSS 위치 |
|-----------|---------|----------|
| 컴포넌트 | `js/shared/components/` | `css/shared/components/` |
| 유틸리티 | `js/shared/utils/` | - |
| 핵심 모듈 | `js/shared/core/` | `css/shared/core/` |
| 상수 | `js/shared/constants/` | - |
| 레이아웃 | - | `css/shared/layouts/` |

## CSS 규칙

### 변수 사용 (SSOT)
- **CSS 변수**: `shared/core/variables.css`에서 정의
- **하드코딩 색상 금지**: `var(--color-*)` 사용
- **인라인 스타일 금지**: 외부 CSS 파일 사용

```css
/* 올바른 방법 */
color: var(--color-primary-500);
background: var(--color-gray-100);

/* 금지 */
color: #3b82f6;
background: #f3f4f6;
```

### CSS 변수 참조
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

## JavaScript 규칙

### 모듈 import 패턴
```javascript
// 도메인 모듈에서 공유 자원 import
import { Toast } from '../../shared/components/toast.js';
import { api } from '../../shared/utils/api.js';
import { FieldRegistry } from '../../shared/core/field-registry.js';

// 같은 도메인 내 import
import { EmployeeService } from '../services/employee-service.js';
```

### 도메인 index.js 패턴
```javascript
// domains/employee/index.js
export { EmployeeService } from './services/employee-service.js';
export * from './pages/list.js';
export * from './pages/form.js';
```

### 기타 규칙
- **인라인 스크립트 금지**: 외부 JS 파일 사용
- **인라인 이벤트 핸들러 금지**: `addEventListener` 사용
- **API 통신**: `shared/utils/api.js` 또는 도메인 services 사용
- **DOM 조작**: `classList.add/remove` 사용 (`style.display` 금지)

## 핵심 컴포넌트

| 컴포넌트 | 위치 | 설명 |
|---------|------|------|
| DataTable | `shared/components/data-table/` | 정렬, 필터, 페이지네이션 |
| FilterBar | `shared/components/filter-bar.js` | 고급 필터 시스템 |
| Salary Calculator | `domains/employee/components/salary/` | 급여 계산 |
| Toast | `shared/components/toast.js` | 알림 메시지 |
| Dynamic Sections | `domains/employee/pages/dynamic-sections.js` | 동적 섹션 관리 |
| TreeSelector | `shared/components/tree-selector.js` | 조직 트리 선택 |
| FileUpload | `shared/components/file-upload.js` | 파일 업로드 |

## 새 파일 추가 규칙

1. **도메인 파일**: 해당 도메인 폴더에 생성 (`domains/{domain}/`)
2. **공유 컴포넌트**: `shared/components/`에 생성
3. **공유 유틸리티**: `shared/utils/`에 생성
4. **base.html**에서 CSS/JS 참조 추가 또는 페이지별 `extra_css`/`extra_js` 블록 사용

## 템플릿 참조 패턴

```html
<!-- 도메인 CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/domains/employee/form.css') }}">

<!-- 공유 CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/shared/components/modal.css') }}">

<!-- 도메인 JS -->
<script src="{{ url_for('static', filename='js/domains/employee/pages/form.js') }}"></script>

<!-- 공유 JS -->
<script src="{{ url_for('static', filename='js/shared/components/toast.js') }}"></script>
```

## Migration History

**Phase 1-9 완료 (2026-01-07)**
- 도메인 중심 구조로 전환: employee, contract, company, user, platform
- 공유 자원 분리: shared/components, shared/utils, shared/core, shared/constants
- 레거시 폴더 정리: pages/, services/, components/, utils/, core/, constants/ 삭제

**BusinessCard 도메인 추가 (2026-01-09)**
- 명함 카드 컴포넌트 추가
- 프리미엄 3D 플립 CSS 스타일

**Attachment 도메인 추가 (2026-01-10)**
- 첨부파일 관리 JS/CSS 추가

**Company Settings 모듈화 (2026-01-10)**
- settings.js 분리: 3,094 라인 → 9개 모듈
- 메인 컨트롤러: 116 라인
- 탭별 모듈: org-management, documents, org-type-settings, patterns-visibility, audit-logs, classifications, org-tree
