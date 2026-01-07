# Frontend Domain-Centric Architecture Refactoring Plan

## Overview
HR Management System의 프론트엔드(JS + CSS + 템플릿)를 백엔드와 동일한 도메인 중심 구조로 리팩토링

## User Requirements
- **범위**: JS + CSS + 템플릿 전체
- **접근 방식**: 기존 구조 재구성 (한 번에 전환)
- **우선 도메인**: employee

---

## 1. Target Directory Structure

### JavaScript (`app/static/js/`)
```
js/
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
│   │       └── salary/         # 도메인 전용 컴포넌트
│   ├── contract/
│   │   ├── index.js
│   │   ├── services/
│   │   │   └── contract-service.js
│   │   └── pages/
│   │       ├── list.js
│   │       └── detail.js
│   ├── company/
│   │   ├── index.js
│   │   ├── services/
│   │   │   └── corporate-settings-api.js
│   │   └── pages/
│   │       ├── settings.js
│   │       ├── users.js
│   │       └── organization.js
│   ├── user/
│   │   ├── index.js
│   │   └── pages/
│   │       ├── auth.js
│   │       ├── profile-sync.js
│   │       └── dashboard.js
│   └── platform/
│       ├── index.js
│       └── pages/
│           └── platform.js
├── shared/                     # 공유 자원
│   ├── components/
│   │   ├── data-table/
│   │   ├── filter-bar.js
│   │   ├── toast.js
│   │   ├── accordion.js
│   │   ├── file-upload.js
│   │   └── ...
│   ├── utils/
│   │   ├── api.js
│   │   ├── dom.js
│   │   ├── validation.js
│   │   └── formatting.js
│   ├── core/
│   │   ├── field-registry.js
│   │   └── template-generator.js
│   └── constants/
│       ├── file-upload-constants.js
│       └── ui-constants.js
└── app.js                      # 전역 초기화 (HRApp)
```

### CSS (`app/static/css/`)
```
css/
├── domains/                    # 도메인별 스타일
│   ├── employee/
│   │   ├── list.css
│   │   ├── form.css
│   │   ├── detail.css
│   │   └── salary.css
│   ├── contract/
│   │   ├── list.css
│   │   └── detail.css
│   ├── company/
│   │   ├── settings.css
│   │   ├── users.css
│   │   └── organization.css
│   ├── user/
│   │   ├── profile.css
│   │   ├── dashboard.css
│   │   └── auth.css
│   └── platform/
│       └── dashboard.css
├── shared/                     # 공유 스타일
│   ├── core/
│   │   ├── variables.css       # SSOT
│   │   ├── reset.css
│   │   ├── theme.css
│   │   └── responsive.css
│   ├── layouts/
│   │   ├── header.css
│   │   ├── sidebar.css
│   │   └── main-content.css
│   └── components/
│       ├── button.css
│       ├── forms.css
│       ├── table.css
│       ├── modal.css
│       └── ...
└── _index.css                  # 메인 진입점 (import 관리)
```

### Templates (`app/templates/`)
```
templates/
├── domains/                    # 도메인별 템플릿
│   ├── employee/
│   │   ├── list.html
│   │   ├── form.html
│   │   ├── detail.html
│   │   └── partials/
│   │       ├── _header.html
│   │       ├── _form_sections.html
│   │       └── _detail_sections.html
│   ├── contract/
│   │   ├── list.html
│   │   └── detail.html
│   ├── company/
│   │   ├── settings.html
│   │   ├── users.html
│   │   └── organization.html
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   └── auth/
│   └── platform/
│       └── dashboard.html
├── shared/                     # 공유 템플릿
│   ├── base.html               # 메인 베이스
│   ├── base_public.html
│   ├── base_error.html
│   ├── layouts/
│   │   ├── _sidebar.html
│   │   └── _header.html
│   ├── macros/
│   │   ├── _forms.html
│   │   ├── _cards.html
│   │   └── _alerts.html
│   └── partials/
│       ├── _notification.html
│       └── _salary_modal.html
└── errors/
    ├── 400.html
    ├── 403.html
    ├── 404.html
    └── 500.html
```

---

## 2. Migration Phases

### Phase 1: Directory Structure Creation
**목표**: 새 디렉토리 구조 생성

```bash
# JS
mkdir -p app/static/js/domains/{employee,contract,company,user,platform}/{services,pages,components}
mkdir -p app/static/js/shared/{components,utils,core,constants}

# CSS
mkdir -p app/static/css/domains/{employee,contract,company,user,platform}
mkdir -p app/static/css/shared/{core,layouts,components}

# Templates
mkdir -p app/templates/domains/{employee,contract,company,user,platform}/partials
mkdir -p app/templates/shared/{layouts,macros,partials}
```

### Phase 2: Shared Resources Migration
**목표**: 공유 자원 이동

| From | To |
|------|-----|
| `js/components/data-table/` | `js/shared/components/data-table/` |
| `js/components/toast.js` | `js/shared/components/toast.js` |
| `js/components/filter-bar.js` | `js/shared/components/filter-bar.js` |
| `js/utils/*` | `js/shared/utils/*` |
| `js/core/*` | `js/shared/core/*` |
| `js/constants/*` | `js/shared/constants/*` |
| `css/core/*` | `css/shared/core/*` |
| `css/layouts/*` | `css/shared/layouts/*` |
| `css/components/*` | `css/shared/components/*` |
| `templates/macros/*` | `templates/shared/macros/*` |
| `templates/partials/*` | `templates/shared/partials/*` |
| `templates/base*.html` | `templates/shared/` |

### Phase 3: Employee Domain Migration (Priority)
**목표**: employee 도메인 완전 마이그레이션

#### 3.1 JavaScript Files
| From | To |
|------|-----|
| `js/services/employee-service.js` | `js/domains/employee/services/employee-service.js` |
| `js/pages/employee-list.js` | `js/domains/employee/pages/list.js` |
| `js/pages/employee-form.js` | `js/domains/employee/pages/form.js` |
| `js/pages/employee-detail.js` | `js/domains/employee/pages/detail.js` |
| `js/pages/employee/*.js` (11 files) | `js/domains/employee/pages/*.js` |
| `js/components/salary/*` | `js/domains/employee/components/salary/*` |

**index.js 생성**:
```javascript
// js/domains/employee/index.js
export { EmployeeService, searchEmployees } from './services/employee-service.js';
export * from './pages/list.js';
export * from './pages/form.js';
export * from './pages/detail.js';
```

#### 3.2 CSS Files
| From | To |
|------|-----|
| `css/pages/employee-form.css` | `css/domains/employee/form.css` |
| `css/pages/employee-detail.css` | `css/domains/employee/detail.css` |
| `css/components/salary-*.css` | `css/domains/employee/salary.css` |
| `css/components/employee-header.css` | `css/domains/employee/header.css` |

#### 3.3 Template Files
| From | To |
|------|-----|
| `templates/employees/*` | `templates/domains/employee/*` |
| `templates/partials/employee_form/*` | `templates/domains/employee/partials/` |
| `templates/partials/employee_detail/*` | `templates/domains/employee/partials/` |

### Phase 4: Contract Domain Migration
| From | To |
|------|-----|
| `js/services/contract-service.js` | `js/domains/contract/services/` |
| `js/pages/contracts.js` | `js/domains/contract/pages/list.js` |
| `js/pages/contract-detail.js` | `js/domains/contract/pages/detail.js` |
| `js/pages/contract-request.js` | `js/domains/contract/pages/request.js` |
| `css/pages/contract-*.css` | `css/domains/contract/` |
| `css/components/contract.css` | `css/domains/contract/` |
| `templates/contracts/*` | `templates/domains/contract/` |

### Phase 5: Company Domain Migration
| From | To |
|------|-----|
| `js/services/corporate-settings-api.js` | `js/domains/company/services/` |
| `js/pages/corporate-settings.js` | `js/domains/company/pages/settings.js` |
| `js/pages/corporate-users.js` | `js/domains/company/pages/users.js` |
| `js/pages/corporate-register.js` | `js/domains/company/pages/register.js` |
| `js/pages/organization.js` | `js/domains/company/pages/organization.js` |
| `css/pages/organization.css` | `css/domains/company/` |
| `css/pages/corporate-*.css` | `css/domains/company/` |
| `templates/corporate/*` | `templates/domains/company/` |
| `templates/admin/organization.html` | `templates/domains/company/` |

### Phase 6: User Domain Migration
| From | To |
|------|-----|
| `js/pages/auth.js` | `js/domains/user/pages/auth.js` |
| `js/pages/dashboard.js` | `js/domains/user/pages/dashboard.js` |
| `js/pages/profile-sync.js` | `js/domains/user/pages/profile-sync.js` |
| `js/pages/profile/*.js` | `js/domains/user/pages/profile/` |
| `css/pages/profile.css` | `css/domains/user/` |
| `css/pages/dashboard.css` | `css/domains/user/` |
| `css/pages/account.css` | `css/domains/user/` |
| `templates/dashboard/*` | `templates/domains/user/dashboard/` |
| `templates/profile/*` | `templates/domains/user/profile/` |
| `templates/personal/*` | `templates/domains/user/personal/` |
| `templates/mypage/*` | `templates/domains/user/mypage/` |
| `templates/account/*` | `templates/domains/user/account/` |
| `templates/auth/*` | `templates/domains/user/auth/` |

### Phase 7: Platform Domain Migration
| From | To |
|------|-----|
| `js/pages/platform.js` | `js/domains/platform/pages/` |
| `js/pages/admin.js` | `js/domains/platform/pages/` |
| `js/pages/ai-test-index.js` | `js/domains/platform/pages/` |
| `css/pages/platform.css` | `css/domains/platform/` |
| `css/pages/ai-test.css` | `css/domains/platform/` |
| `css/pages/admin-profile.css` | `css/domains/platform/` |
| `templates/platform/*` | `templates/domains/platform/` |
| `templates/admin/*` | `templates/domains/platform/admin/` |
| `templates/ai_test/*` | `templates/domains/platform/ai_test/` |

### Phase 8: Import Path Updates
**목표**: 모든 import 경로 업데이트

1. **Template static references** 업데이트:
   ```html
   <!-- Before -->
   <script src="{{ url_for('static', filename='js/pages/employee-list.js') }}"></script>

   <!-- After -->
   <script src="{{ url_for('static', filename='js/domains/employee/pages/list.js') }}"></script>
   ```

2. **JS module imports** 업데이트:
   ```javascript
   // Before
   import { Toast } from '../components/toast.js';

   // After
   import { Toast } from '../../shared/components/toast.js';
   ```

3. **CSS imports** 업데이트:
   ```css
   /* Before */
   @import '../core/variables.css';

   /* After */
   @import '../shared/core/variables.css';
   ```

### Phase 9: Legacy Cleanup
**목표**: 빈 폴더 및 레거시 파일 정리

1. 빈 폴더 삭제
2. 미사용 파일 정리
3. CLAUDE.md 업데이트

---

## 3. File Migration Summary

### JavaScript (68 files)
| Category | Count | Destination |
|----------|-------|-------------|
| Employee | 14 | `domains/employee/` |
| Contract | 4 | `domains/contract/` |
| Company | 4 | `domains/company/` |
| User | 6 | `domains/user/` |
| Platform | 3 | `domains/platform/` |
| Shared Components | 20 | `shared/components/` |
| Shared Utils | 6 | `shared/utils/` |
| Shared Core | 2 | `shared/core/` |
| Shared Constants | 3 | `shared/constants/` |
| App Entry | 1 | `app.js` (유지) |

### CSS (58 files)
| Category | Count | Destination |
|----------|-------|-------------|
| Employee | 5 | `domains/employee/` |
| Contract | 3 | `domains/contract/` |
| Company | 4 | `domains/company/` |
| User | 5 | `domains/user/` |
| Platform | 3 | `domains/platform/` |
| Shared Core | 4 | `shared/core/` |
| Shared Layouts | 6 | `shared/layouts/` |
| Shared Components | 28 | `shared/components/` |

### Templates (~100 files)
| Category | Count | Destination |
|----------|-------|-------------|
| Employee | 15 | `domains/employee/` |
| Contract | 8 | `domains/contract/` |
| Company | 10 | `domains/company/` |
| User | 25 | `domains/user/` |
| Platform | 8 | `domains/platform/` |
| Shared | 20 | `shared/` |
| Errors | 4 | `errors/` |

---

## 4. Critical Files to Modify

### Flask Blueprint Updates
도메인 템플릿 경로 변경에 따른 Blueprint 수정:

```python
# app/domains/employee/blueprints/list_routes.py
# Before
return render_template('employees/list.html', ...)

# After
return render_template('domains/employee/list.html', ...)
```

**수정 대상 파일:**
- `app/domains/employee/blueprints/list_routes.py`
- `app/domains/employee/blueprints/detail_routes.py`
- `app/domains/employee/blueprints/mutation_routes.py`
- `app/domains/contract/blueprints/contracts.py`
- `app/domains/company/blueprints/corporate.py`
- `app/domains/company/blueprints/settings/*.py`
- `app/domains/user/blueprints/mypage.py`
- `app/domains/user/blueprints/personal/*.py`
- `app/domains/user/blueprints/profile/*.py`
- `app/domains/platform/blueprints/*.py`

### Base Template Updates
```html
<!-- templates/shared/base.html -->
<!-- CSS imports 업데이트 -->
<!-- JS imports 업데이트 -->
```

---

## 5. Validation Checklist

### Per Phase
- [ ] 파일 이동 완료
- [ ] Import 경로 업데이트
- [ ] 개발 서버 실행 확인
- [ ] 페이지 로드 테스트
- [ ] 콘솔 에러 확인
- [ ] 기능 동작 확인

### Final
- [ ] 모든 페이지 접근 가능
- [ ] 모든 JS 기능 동작
- [ ] 모든 CSS 스타일 적용
- [ ] 파일 업로드 동작
- [ ] API 호출 정상
- [ ] 빈 폴더 정리
- [ ] CLAUDE.md 업데이트

---

## 6. Rollback Strategy
각 Phase 완료 후 git commit으로 복구 지점 생성

```bash
# Phase 완료 시
git add .
git commit -m "refactor(frontend): Phase N - [description]"

# 문제 발생 시
git revert HEAD
```

---

## 7. Estimated Scope
- **총 파일 이동**: ~200개
- **Import 경로 수정**: ~100건
- **Blueprint 수정**: ~15개 파일
- **권장 작업 단위**: Phase별 커밋

---

## 8. Detailed Task List (TodoWrite)

### Phase 1: Directory Structure Creation
```
[ ] 1.1 JS 도메인 디렉토리 생성 (domains/{employee,contract,company,user,platform})
[ ] 1.2 JS shared 디렉토리 생성 (shared/{components,utils,core,constants})
[ ] 1.3 CSS 도메인 디렉토리 생성 (domains/{employee,contract,company,user,platform})
[ ] 1.4 CSS shared 디렉토리 생성 (shared/{core,layouts,components})
[ ] 1.5 Templates 도메인 디렉토리 생성 (domains/{employee,contract,company,user,platform}/partials)
[ ] 1.6 Templates shared 디렉토리 생성 (shared/{layouts,macros,partials})
[ ] 1.7 Git commit: "refactor(frontend): Phase 1 - Create domain directory structure"
```

### Phase 2: Shared Resources Migration
```
[ ] 2.1 JS components 이동 (data-table/, toast.js, filter-bar.js 등 20개)
[ ] 2.2 JS utils 이동 (api.js, dom.js, validation.js 등 6개)
[ ] 2.3 JS core 이동 (field-registry.js, template-generator.js)
[ ] 2.4 JS constants 이동 (3개 파일)
[ ] 2.5 CSS core 이동 (variables.css, reset.css, theme.css, responsive.css)
[ ] 2.6 CSS layouts 이동 (header.css, sidebar.css 등 6개)
[ ] 2.7 CSS components 이동 (button.css, forms.css 등 28개)
[ ] 2.8 Templates base*.html 이동
[ ] 2.9 Templates macros 이동
[ ] 2.10 Templates partials 이동 (공통만)
[ ] 2.11 Import 경로 업데이트 (shared 내부)
[ ] 2.12 개발 서버 테스트
[ ] 2.13 Git commit: "refactor(frontend): Phase 2 - Migrate shared resources"
```

### Phase 3: Employee Domain Migration
```
[ ] 3.1 employee-service.js 이동
[ ] 3.2 employee-list.js -> domains/employee/pages/list.js
[ ] 3.3 employee-form.js -> domains/employee/pages/form.js
[ ] 3.4 employee-detail.js -> domains/employee/pages/detail.js
[ ] 3.5 pages/employee/*.js 이동 (11개 파일)
[ ] 3.6 components/salary/* 이동
[ ] 3.7 domains/employee/index.js 생성
[ ] 3.8 CSS employee-*.css 이동
[ ] 3.9 CSS salary-*.css 이동
[ ] 3.10 Templates employees/* 이동
[ ] 3.11 Templates partials/employee_form/* 이동
[ ] 3.12 Templates partials/employee_detail/* 이동
[ ] 3.13 Blueprint render_template 경로 수정
[ ] 3.14 Template static 참조 경로 수정
[ ] 3.15 JS import 경로 수정
[ ] 3.16 직원 목록 페이지 테스트
[ ] 3.17 직원 등록 폼 테스트
[ ] 3.18 직원 상세 페이지 테스트
[ ] 3.19 Git commit: "refactor(frontend): Phase 3 - Migrate employee domain"
```

### Phase 4: Contract Domain Migration
```
[ ] 4.1 contract-service.js 이동
[ ] 4.2 contracts.js -> domains/contract/pages/list.js
[ ] 4.3 contract-detail.js -> domains/contract/pages/detail.js
[ ] 4.4 contract-request.js -> domains/contract/pages/request.js
[ ] 4.5 domains/contract/index.js 생성
[ ] 4.6 CSS contract-*.css 이동
[ ] 4.7 Templates contracts/* 이동
[ ] 4.8 Blueprint render_template 경로 수정
[ ] 4.9 계약 목록 페이지 테스트
[ ] 4.10 계약 상세 페이지 테스트
[ ] 4.11 Git commit: "refactor(frontend): Phase 4 - Migrate contract domain"
```

### Phase 5: Company Domain Migration
```
[ ] 5.1 corporate-settings-api.js 이동
[ ] 5.2 corporate-settings.js 이동
[ ] 5.3 corporate-users.js 이동
[ ] 5.4 corporate-register.js 이동
[ ] 5.5 organization.js 이동
[ ] 5.6 domains/company/index.js 생성
[ ] 5.7 CSS corporate-*.css, organization.css 이동
[ ] 5.8 Templates corporate/* 이동
[ ] 5.9 Templates admin/organization.html 이동
[ ] 5.10 Blueprint render_template 경로 수정
[ ] 5.11 법인 설정 페이지 테스트
[ ] 5.12 조직 관리 페이지 테스트
[ ] 5.13 Git commit: "refactor(frontend): Phase 5 - Migrate company domain"
```

### Phase 6: User Domain Migration
```
[ ] 6.1 auth.js 이동
[ ] 6.2 dashboard.js 이동
[ ] 6.3 profile-sync.js 이동
[ ] 6.4 pages/profile/*.js 이동
[ ] 6.5 domains/user/index.js 생성
[ ] 6.6 CSS profile.css, dashboard.css, account.css 이동
[ ] 6.7 Templates dashboard/* 이동
[ ] 6.8 Templates profile/* 이동
[ ] 6.9 Templates personal/* 이동
[ ] 6.10 Templates mypage/* 이동
[ ] 6.11 Templates account/* 이동
[ ] 6.12 Templates auth/* 이동
[ ] 6.13 Blueprint render_template 경로 수정
[ ] 6.14 대시보드 페이지 테스트
[ ] 6.15 프로필 페이지 테스트
[ ] 6.16 로그인/회원가입 테스트
[ ] 6.17 Git commit: "refactor(frontend): Phase 6 - Migrate user domain"
```

### Phase 7: Platform Domain Migration
```
[ ] 7.1 platform.js 이동
[ ] 7.2 admin.js 이동
[ ] 7.3 ai-test-index.js 이동
[ ] 7.4 domains/platform/index.js 생성
[ ] 7.5 CSS platform.css, ai-test.css, admin-profile.css 이동
[ ] 7.6 Templates platform/* 이동
[ ] 7.7 Templates admin/* 이동 (organization 제외)
[ ] 7.8 Templates ai_test/* 이동
[ ] 7.9 Blueprint render_template 경로 수정
[ ] 7.10 플랫폼 관리 페이지 테스트
[ ] 7.11 Git commit: "refactor(frontend): Phase 7 - Migrate platform domain"
```

### Phase 8: Import Path Updates & Validation
```
[ ] 8.1 전체 Template static 참조 검증 (grep 'url_for.*static')
[ ] 8.2 전체 JS import 경로 검증 (grep 'import.*from')
[ ] 8.3 전체 CSS @import 검증
[ ] 8.4 Base template 업데이트
[ ] 8.5 콘솔 에러 전체 점검
[ ] 8.6 Git commit: "refactor(frontend): Phase 8 - Update all import paths"
```

### Phase 9: Legacy Cleanup
```
[ ] 9.1 빈 폴더 삭제 (js/pages/, js/services/, js/components/, js/utils/ 등)
[ ] 9.2 빈 폴더 삭제 (css/pages/, css/components/, css/layouts/, css/core/)
[ ] 9.3 빈 폴더 삭제 (templates/employees/, templates/contracts/ 등)
[ ] 9.4 app/static/CLAUDE.md 업데이트
[ ] 9.5 app/CLAUDE.md 업데이트
[ ] 9.6 프로젝트 CLAUDE.md 업데이트
[ ] 9.7 최종 통합 테스트
[ ] 9.8 Git commit: "refactor(frontend): Phase 9 - Legacy cleanup and docs update"
```

---

## 9. Test Checklist (--test-check)

### Phase별 테스트 체크리스트

#### Phase 2 테스트 (Shared Resources)
```
[ ] 개발 서버 시작 확인 (python run.py)
[ ] 메인 페이지 로드 (/)
[ ] 콘솔 에러 없음 확인
[ ] CSS 스타일 정상 적용 확인
[ ] Toast 알림 동작 확인
```

#### Phase 3 테스트 (Employee Domain)
```
[ ] 직원 목록 페이지 (/employees)
  [ ] 페이지 로드
  [ ] 테이블 렌더링
  [ ] 필터 동작
  [ ] 정렬 동작
  [ ] 뷰 토글 (목록/카드)
[ ] 직원 등록 폼 (/employees/new)
  [ ] 폼 렌더링
  [ ] 동적 섹션 추가/삭제
  [ ] 유효성 검사
  [ ] 파일 업로드
  [ ] 제출 동작
[ ] 직원 상세 페이지 (/employees/<id>)
  [ ] 정보 표시
  [ ] 탭 전환
  [ ] 수정 버튼 동작
[ ] 급여 계산기 모달 동작
```

#### Phase 4 테스트 (Contract Domain)
```
[ ] 계약 목록 페이지 (/contracts)
  [ ] 페이지 로드
  [ ] 필터 동작
  [ ] 상태별 조회
[ ] 계약 상세 페이지 (/contracts/<id>)
  [ ] 정보 표시
  [ ] 승인/거절 버튼
[ ] 계약 요청 기능
```

#### Phase 5 테스트 (Company Domain)
```
[ ] 법인 설정 페이지 (/corporate/settings)
  [ ] 탭 전환
  [ ] 설정 저장
  [ ] 분류 옵션 관리
[ ] 조직 관리 페이지 (/admin/organization)
  [ ] 트리 렌더링
  [ ] 노드 추가/수정/삭제
[ ] 사용자 관리 페이지 (/corporate/users)
```

#### Phase 6 테스트 (User Domain)
```
[ ] 로그인 페이지 (/auth/login)
[ ] 회원가입 페이지
[ ] 대시보드 (/dashboard)
  [ ] 통계 카드
  [ ] 퀵 링크
[ ] 프로필 페이지
  [ ] 정보 표시
  [ ] 수정 기능
[ ] 마이페이지
```

#### Phase 7 테스트 (Platform Domain)
```
[ ] 플랫폼 관리 대시보드 (/platform)
[ ] 감사 로그 페이지
[ ] AI 테스트 페이지
```

### 통합 테스트 체크리스트 (Final)
```
[ ] 모든 페이지 404 없이 접근 가능
[ ] 모든 JS 파일 로드 성공 (Network 탭 확인)
[ ] 모든 CSS 파일 로드 성공
[ ] 콘솔 에러 0건
[ ] API 호출 정상 (AJAX/Fetch)
[ ] 파일 업로드 동작
[ ] 폼 제출 동작
[ ] 토스트 알림 동작
[ ] 모달 열기/닫기 동작
[ ] 반응형 레이아웃 (모바일/태블릿/데스크톱)
```

---

## 10. Safety Checklist (--safe)

### 작업 전 확인사항
```
[ ] 현재 브랜치 확인 (git branch)
[ ] 작업 브랜치 생성 (git checkout -b hrm-projekt-YYMMDD-frontend-domain-migration)
[ ] 변경사항 없음 확인 (git status)
[ ] 백업 커밋 생성 (선택사항)
```

### Phase별 안전 체크
```
[ ] Phase 완료 후 즉시 git commit
[ ] 커밋 메시지에 Phase 번호 명시
[ ] 테스트 실패 시 git stash 또는 git checkout -- <file>
[ ] 심각한 문제 시 git reset --hard HEAD~1
```

### 롤백 절차
```bash
# 특정 Phase 롤백
git log --oneline -10  # 커밋 확인
git revert <commit-hash>

# 전체 롤백
git reset --hard origin/main  # 주의: 모든 변경 손실
```

### 금지 사항
```
[ ] production 브랜치에 직접 작업 금지
[ ] 테스트 없이 다음 Phase 진행 금지
[ ] 여러 Phase 동시 작업 금지
[ ] 커밋 없이 대량 파일 이동 금지
```

---

## 11. Execution Commands Reference

### Phase 1: Directory Creation
```bash
# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path @(
  "app/static/js/domains/employee/services",
  "app/static/js/domains/employee/pages",
  "app/static/js/domains/employee/components",
  "app/static/js/domains/contract/services",
  "app/static/js/domains/contract/pages",
  "app/static/js/domains/company/services",
  "app/static/js/domains/company/pages",
  "app/static/js/domains/user/pages",
  "app/static/js/domains/platform/pages",
  "app/static/js/shared/components",
  "app/static/js/shared/utils",
  "app/static/js/shared/core",
  "app/static/js/shared/constants",
  "app/static/css/domains/employee",
  "app/static/css/domains/contract",
  "app/static/css/domains/company",
  "app/static/css/domains/user",
  "app/static/css/domains/platform",
  "app/static/css/shared/core",
  "app/static/css/shared/layouts",
  "app/static/css/shared/components",
  "app/templates/domains/employee/partials",
  "app/templates/domains/contract/partials",
  "app/templates/domains/company/partials",
  "app/templates/domains/user/partials",
  "app/templates/domains/platform/partials",
  "app/templates/shared/layouts",
  "app/templates/shared/macros",
  "app/templates/shared/partials"
)
```

### Phase 2: File Move Commands (Example)
```bash
# JS Components
Move-Item "app/static/js/components/data-table" "app/static/js/shared/components/" -Force
Move-Item "app/static/js/components/toast.js" "app/static/js/shared/components/"
Move-Item "app/static/js/components/filter-bar.js" "app/static/js/shared/components/"
# ... (추가 파일들)

# JS Utils
Move-Item "app/static/js/utils/*" "app/static/js/shared/utils/"

# JS Core
Move-Item "app/static/js/core/*" "app/static/js/shared/core/"
```

### Git Commit Template
```bash
git add .
git commit -m "refactor(frontend): Phase N - Description

- 파일 이동: XX개
- Import 경로 수정: YY건
- 테스트: 통과

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## 12. Progress Tracking

### Overall Progress
| Phase | Status | Files | Tests |
|-------|--------|-------|-------|
| 1. Directory Creation | Pending | 0/0 | N/A |
| 2. Shared Resources | Pending | 0/60 | 0/5 |
| 3. Employee Domain | Pending | 0/34 | 0/15 |
| 4. Contract Domain | Pending | 0/10 | 0/6 |
| 5. Company Domain | Pending | 0/15 | 0/6 |
| 6. User Domain | Pending | 0/40 | 0/8 |
| 7. Platform Domain | Pending | 0/12 | 0/4 |
| 8. Import Updates | Pending | 0/100 | 0/5 |
| 9. Cleanup | Pending | 0/10 | 0/10 |
| **Total** | **0%** | **0/281** | **0/59** |

---

## 13. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Import 경로 누락 | High | Medium | grep으로 전체 검색 후 수정 |
| 템플릿 경로 오류 | High | High | Phase별 테스트 필수 |
| JS 모듈 로드 실패 | Medium | High | 콘솔 에러 즉시 확인 |
| CSS 스타일 깨짐 | Medium | Medium | 시각적 검증 병행 |
| 롤백 어려움 | Low | High | Phase별 커밋으로 방지 |

---

## 14. Dependencies

```
Phase 1 (Directory Creation)
    |
    v
Phase 2 (Shared Resources) -----> Phase 3-7 (Domain Migration)
                                       |
                                       v
                                  Phase 8 (Import Updates)
                                       |
                                       v
                                  Phase 9 (Cleanup)
```

**병렬 실행 가능**: Phase 3-7은 서로 독립적이므로 병렬 진행 가능 (단, 테스트 복잡도 증가)
