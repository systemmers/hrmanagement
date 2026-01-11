# HR Card Demo Migration Plan

> 마이그레이션 계획 문서
> 생성일: 2026-01-08
> **최종 업데이트: 2026-01-11**
> 소스: `.dev_docs/demos/hr_card/hr-card.html` (284KB, ~6,100 lines)

---

## 1. 개요

### 1.1 목표
HR Card 데모 파일의 주요 기능을 현재 Flask HR Management 프로젝트에 마이그레이션

### 1.2 대상 기능
| 기능 | 설명 |
|------|------|
| 사이드바 검색 | 직원 빠른 검색 + 모달 결과 표시 |
| 인라인 편집 | 섹션별 in-place 편집 |
| 첨부파일 패널 | 우측 패널, 필수 파일 관리, 드래그 정렬 |
| 메인 카드 스타일 | 헤더 카드, 정보 섹션, 데이터 테이블 |
| 섹션 네비게이션 이동 | 내부 section-nav → 사이드바 sub-nav로 이동 |
| 기존 수정 페이지 삭제 | 인라인 편집으로 완전 대체, 기존 폼 시스템 제거 |

### 1.3 예상 기간
~~**총 11일** (Phase 1~7)~~ -> ~~**총 5.5일**~~ -> ~~**총 8.5일**~~ -> **총 8.8일** (첨부파일 백엔드 정비 추가)

### 1.4 전체 진행률
**약 55% 완료** (2026-01-11 기준, Phase 08, 09 추가로 재산정)

---

## 2. 서브 플랜 구조

### 2.1 플랜 목록 (업데이트됨)

| 번호 | 내용 | 기간 | 위험도 | 의존성 | 진행률 | 상태 |
|------|------|------|--------|--------|--------|------|
| **01** | CSS Foundation - 변수 정렬 | 0.5일 | 낮음 | 없음 | 100% | **완료** |
| **02** | Shared Components - Modal/Toast/DragDrop | 2일 | 중간 | 01 | 80% | 진행중 |
| **03a** | Header Card - 헤더/명함 | 1일 | 낮음 | 01 | 90% | 거의완료 |
| **03b** | Info Section - 정보 테이블 | 1일 | 낮음 | 01 | 95% | 거의완료 |
| **04** | Sidebar Search - 검색 기능 | 1.5일 | 중간 | 02 | 60% | 진행중 |
| **05** | Inline Edit - 인라인 편집 | 2.5일 | 높음 | 02, 03 | 40% | 미완료 |
| **06a** | File Panel API - 순서 변경 API | 0.1일 | 낮음 | 없음 | 0% | **신규** |
| **06b** | File Panel UI - 첨부파일 패널 | 0.2일 | 낮음 | 02 | 85% | 진행중 |
| **07** | Data Tables - 테이블 드래그 | 1일 | 낮음 | 02, 06 | 70% | 진행중 |
| **08** | Section Nav → Sidebar Migration | 0.5일 | 낮음 | 01 | 0% | 미완료 |
| **09** | 기존 수정 페이지 삭제 + 인라인 확장 | 2.5일 | 높음 | 05 | 0% | 미완료 |

### 2.2 실행 순서 (수정됨)

```
Day 1:
  [완료 확인] Phase 01, 03a, 03b
  [drag-order-manager.js] Phase 02 잔여 (0.5일)

Day 2:
  [sidebar-search.js] Phase 04 잔여 (0.6일)
  [순서 변경 API] Phase 07 잔여 (0.3일)

Day 3-4:
  [inline-edit.js + PATCH API] Phase 05 잔여 (1.5일) - 가장 복잡

Day 4.5:
  [file-panel UI] Phase 06 잔여 (0.2일)

Day 5:
  [section-nav → sidebar] Phase 08 (0.5일)

Day 5.5-8:
  [기존 수정 페이지 삭제 + 인라인 확장] Phase 09 (2.5일)
  - 테이블형 인라인 편집 JS (1.0일)
  - PATCH API 확장 (0.5일)
  - 기존 시스템 삭제 (0.5일)
  - detail 템플릿 수정 (0.5일)

Day 8.5:
  통합 테스트 (0.5일)
```

---

## 3. 현황 분석 (2026-01-11)

### 3.1 완료된 항목

#### CSS (95% 완료)
| 파일 | 상태 | 경로 |
|------|------|------|
| variables.css | 완료 | HR Card 호환 변수 21줄 포함 |
| info-section.css | 완료 | `css/shared/components/` |
| inline-edit.css | 완료 | `css/shared/components/` |
| sidebar-search.css | 완료 | `css/shared/components/` |
| attachment.css | 완료 | `css/shared/components/` |
| info-grid.css | 완료 | `css/shared/components/` |
| mobile-nav.css | 완료 | `css/shared/components/` |
| modal.css | 완료 | `css/shared/components/` |
| header.css | 완료 | `css/domains/employee/` |
| business-card.css | 완료 | `css/domains/employee/` |
| data-table-advanced.css | 완료 | `css/shared/components/` |

#### JavaScript (50% 완료)
| 파일 | 상태 | 경로 |
|------|------|------|
| toast.js | 완료 | `js/shared/components/` |
| data-table-advanced.js | 완료 | `js/shared/components/data-table/` |
| business-card.js | 완료 | `js/domains/employee/components/` |
| filter-bar.js | 완료 | `js/shared/components/` |
| accordion.js | 완료 | `js/shared/components/` |

#### API (80% 완료)
| Endpoint | 상태 | 비고 |
|----------|------|------|
| GET /api/employees (목록+검색) | 완료 | search 파라미터 지원 |
| GET/POST /api/employees/<id>/attachments | 완료 | Attachment 도메인 |
| DELETE /api/attachments/<id> | 완료 | Attachment 도메인 |
| POST/DELETE /api/employees/<id>/business-card | 완료 | 명함 관리 |

#### Backend (90% 완료)
| 서비스/도메인 | 상태 | 비고 |
|--------------|------|------|
| employee_service.py | 완료 | Facade 패턴 |
| employee_core_service.py | 완료 | search_employees() 구현 |
| employee_relation_service.py | 완료 | 관계형 데이터 CRUD |
| Attachment 도메인 | 완료 | Phase 31 완료 |

### 3.2 미완료 항목 (잔여 작업)

#### JavaScript 컴포넌트 (필요)
| 파일 | 우선순위 | 예상 소요 | 설명 |
|------|----------|----------|------|
| inline-edit.js | 높음 | 1.2일 | 섹션별 편집 모드, 원본 백업/복원, API 연동 |
| sidebar-search.js | 중간 | 0.6일 | 디바운스 검색, 모달 결과, 페이지 이동 |
| drag-order-manager.js | 중간 | 0.5일 | 범용 드래그 순서 관리자 |
| file-panel.js | 낮음 | 0.2일 | 우측 패널 UI 연동 (백엔드 완성) |

#### API (필요)
| Endpoint | 우선순위 | 예상 소요 | 설명 |
|----------|----------|----------|------|
| PATCH /api/employees/<id>/sections/<section> | 높음 | 0.3일 | 인라인 편집용 섹션별 부분 업데이트 |
| PATCH /api/employees/<id>/educations/order | 중간 | 0.1일 | 학력 순서 변경 |
| PATCH /api/employees/<id>/careers/order | 중간 | 0.1일 | 경력 순서 변경 |
| PATCH /api/employees/<id>/certificates/order | 중간 | 0.1일 | 자격증 순서 변경 |

#### Styleguide (진행중)
| 파일 | 상태 |
|------|------|
| attachment.html | 완료 |
| info-section.html | 완료 |
| info-table.html | 완료 |
| inline-edit.html | 완료 |
| mobile-nav.html | 완료 |
| sidebar-search.html | 완료 |
| sub-nav.html | 완료 |

---

## 4. 계정 타입별 디자인

### 4.1 테마 시스템

| 계정 타입 | CSS Selector | 테마 색상 | 용도 |
|----------|--------------|----------|------|
| Corporate | `[data-account-type="corporate"]` | Blue (#2563EB) | 법인 관리자 |
| Personal | `[data-account-type="personal"]` | Green (#059669) | 개인 사용자 |
| Employee Sub | `[data-account-type="employee_sub"]` | Purple (#7C3AED) | 법인 소속 직원 |

### 4.2 컴포넌트별 차이점

| 컴포넌트 | Corporate | Personal | Employee Sub |
|---------|-----------|----------|--------------|
| 헤더 그라데이션 | Blue | Green | Purple |
| 명함 영역 | 표시 | **숨김** | 표시 |
| 인라인 편집 | 전체 섹션 | 개인 정보만 | 읽기 전용 |
| 파일 첨부 | 전체 관리 | 본인 파일 | 읽기 전용 |
| 사이드바 검색 | 전체 직원 | N/A | N/A |
| Status Badge | 표시 | 숨김 | 표시 |

---

## 5. 수정 페이지 전략

### 5.1 ~~병행(Parallel) 전략~~ → 대체(Replace) 전략 채택

인라인 편집이 기존 수정 페이지를 **완전 대체**

| 항목 | 이전 | 이후 |
|------|------|------|
| 기본정보 수정 | 기존 폼 | 인라인 편집 |
| 학력/경력/자격증 | 기존 폼 | 테이블형 인라인 편집 |
| 기존 수정 페이지 | 유지 | **삭제** |

### 5.2 삭제 대상 목록

**라우트** (`detail_routes.py`, `mutation_routes.py`):
| 라우트 | 메서드 | 설명 |
|--------|--------|------|
| `/employees/<id>/edit` | GET | 전체 수정 페이지 |
| `/employees/<id>/edit/basic` | GET | 기본정보 수정 |
| `/employees/<id>/edit/history` | GET | 이력 수정 |
| `/employees/<id>/update` | POST | 전체 업데이트 |
| `/employees/<id>/update/basic` | POST | 기본정보 업데이트 |
| `/employees/<id>/update/history` | POST | 이력 업데이트 |

**템플릿** (`templates/domains/employee/partials/form/`): 16개 파일
- `_personal_info.html`, `_organization_info.html`, `_contract_info.html`
- `_education_info.html`, `_career_info.html`, `_certificate_info.html`
- `_family_info.html`, `_military_info.html`, `_language_info.html`
- `_salary_info.html`, `_benefit_info.html`, `_award_info.html`
- `_project_info.html`, `_project_participation_info.html`
- `_account_info.html`, `_submit_section.html`

### 5.3 인라인 편집 확장 섹션

**기본 인라인 편집** (단일 필드):
- `personal_info` - 기본 인적사항
- `address_info` - 주소 정보
- `physical_info` - 신체 정보
- `military_info` - 병역 정보

**테이블형 인라인 편집** (행 추가/수정/삭제/순서변경):
- `education` - 학력
- `career` - 경력
- `certificate` - 자격증
- `family` - 가족관계
- `language` - 어학
- `award` - 수상

### 5.4 테이블형 인라인 편집 UI

```
┌─────────────────────────────────────────────────┐
│ 학력정보                         [+ 추가] [편집] │
├─────────────────────────────────────────────────┤
│ ⋮ 서울대학교 | 컴퓨터공학 | 학사 | 2015 [삭제]  │
│ ⋮ 카이스트  | 인공지능  | 석사 | 2017 [삭제]  │
└─────────────────────────────────────────────────┘
```
- `⋮` 드래그 핸들 (순서 변경)
- `[+ 추가]` 새 행 추가 (모달 또는 인라인 폼)
- `[편집]` 전체 편집 모드 토글
- `[삭제]` 개별 행 삭제

---

## 6. 파일 생성/수정 요약 (업데이트됨)

### 6.1 CSS 파일 현황

#### 신규 CSS (6개) - **모두 완료**

| 파일 | 상태 | 실제 경로 |
|------|------|----------|
| info-section.css | 완료 | `css/shared/components/info-section.css` |
| info-grid.css | 완료 | `css/shared/components/info-grid.css` |
| inline-edit.css | 완료 | `css/shared/components/inline-edit.css` |
| sidebar-search.css | 완료 | `css/shared/components/sidebar-search.css` |
| attachment.css | 완료 | `css/shared/components/attachment.css` |
| mobile-nav.css | 완료 | `css/shared/components/mobile-nav.css` |

#### 확장 CSS (5개) - **모두 완료**

| 파일 | 상태 | 비고 |
|------|------|------|
| variables.css | 완료 | HR Card 호환 변수 21줄 포함 |
| button.css | 완료 | btn-dark, btn-header |
| data-table-advanced.css | 완료 | 드래그, 첨부 컬럼 |
| header.css | 완료 | status-badge, stats-row |
| business-card.css | 완료 | 3D 플립 효과 |

### 6.2 JavaScript 파일 현황

| 파일 | 상태 | 경로/비고 |
|------|------|----------|
| toast.js | 완료 | `js/shared/components/toast.js` |
| data-table/*.js | 완료 | 7개 모듈 완성 |
| business-card.js | 완료 | `js/domains/employee/components/` |
| **drag-order-manager.js** | **미완료** | 범용 드래그 순서 관리자 필요 |
| **inline-edit.js** | **미완료** | 섹션별 편집 관리자 필요 |
| **sidebar-search.js** | **미완료** | 검색 컴포넌트 필요 |
| **file-panel.js** | **미완료** | 우측 패널 UI 필요 |

### 6.3 Template 파일 현황

| 파일 | 상태 | 비고 |
|------|------|------|
| _file_panel.html | 미완료 | 우측 첨부파일 패널 |
| _inline_section.html | 미완료 | 인라인 편집 섹션 템플릿 |
| _sidebar_search.html | 미완료 | 사이드바 검색 매크로 |

### 6.4 Service 파일 현황

| 파일 | 상태 | 비고 |
|------|------|------|
| employee_section_service.py | 미완료 | 섹션별 부분 업데이트 서비스 |
| attachment_service.py | 완료 | `app/domains/attachment/services/` |

### 6.5 Model 확장

```python
# Education, Career, Certificate 모델에 추가 필요
display_order = db.Column(db.Integer, default=0)
```
**상태**: 미확인 - 마이그레이션 필요 여부 점검 필요

---

## 7. API 엔드포인트 (업데이트됨)

### 7.1 검색 API

| Endpoint | Method | 상태 | 비고 |
|----------|--------|------|------|
| `/api/employees` | GET | **완료** | `?search=검색어` 파라미터 지원 |

### 7.2 인라인 편집 API

| Endpoint | Method | 상태 | 비고 |
|----------|--------|------|------|
| `/api/employees/<id>/sections/<section>` | PATCH | **미완료** | 섹션별 부분 업데이트 |

### 7.3 첨부파일 API

| Endpoint | Method | 상태 | 비고 |
|----------|--------|------|------|
| `/api/employees/<id>/attachments` | GET | **완료** | Attachment 도메인 |
| `/api/employees/<id>/attachments` | POST | **완료** | Attachment 도메인 |
| `/api/attachments/<file_id>` | DELETE | **완료** | Attachment 도메인 |
| `/api/employees/<id>/attachments/order` | PATCH | **미완료** | 순서 변경 |

### 7.4 순서 변경 API

| Endpoint | Method | 상태 | 비고 |
|----------|--------|------|------|
| `/api/employees/<id>/educations/order` | PATCH | **미완료** | 학력 순서 |
| `/api/employees/<id>/careers/order` | PATCH | **미완료** | 경력 순서 |
| `/api/employees/<id>/certificates/order` | PATCH | **미완료** | 자격증 순서 |

---

## 8. 주요 CSS 패턴

### 8.1 Info Section Card

```css
.info-section {
    background: var(--color-pure-white);
    border-radius: var(--radius-xl);
    border: 1px solid var(--color-gray-200);
    margin-bottom: var(--space-6);
    overflow: hidden;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-5) var(--space-6);
    border-bottom: 1px solid var(--color-gray-200);
}
```

### 8.2 Info Table (2열 그리드)

```css
.info-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
}

.info-label {
    width: 140px;
    padding: var(--space-4);
    background: var(--color-gray-50);
}

.info-value {
    flex: 1;
    padding: var(--space-4);
}
```

### 8.3 Business Card 3D Flip

```css
.business-card-flip {
    perspective: 1000px;
}

.business-card-inner {
    transform-style: preserve-3d;
    transition: transform 0.6s;
}

.business-card-flip:hover .business-card-inner {
    transform: rotateY(180deg);
}
```

### 8.4 Status Badge

```css
.status-badge.active {
    background: rgba(16, 185, 129, 0.25);
    color: #6EE7B7;
}

.status-badge.resigned {
    background: rgba(239, 68, 68, 0.25);
    color: #FCA5A5;
}
```

---

## 9. JavaScript 클래스 구조

### 9.1 InlineEditManager

```javascript
class InlineEditManager {
    constructor(sectionElement) { }

    toggleEditMode() { }      // 편집 모드 전환
    saveChanges() { }         // API 호출 + 저장
    cancelEdit() { }          // 원본 값 복원

    _checkEditPermission() { }  // 계정 타입별 권한
    _backupOriginalValues() { }
    _restoreOriginalValues() { }
}
```

### 9.2 SidebarSearch

```javascript
class SidebarSearch {
    constructor(inputElement, options) {
        this.options = {
            debounceMs: 300,
            minChars: 2,
            maxResults: 10,
            apiUrl: '/api/employees/search'
        };
    }

    _search() { }           // API 검색
    _renderResults() { }    // 결과 렌더링
    _openModal() { }        // 모달 열기
    _closeModal() { }       // 모달 닫기
}
```

### 9.3 TableDragOrder

```javascript
class TableDragOrder {
    constructor(tableElement, options) {
        this.options = {
            handleSelector: '.drag-handle',
            rowSelector: 'tbody tr',
            apiEndpoint: null
        };
    }

    _setupDragEvents() { }  // 드래그 이벤트 설정
    _saveOrder() { }        // 순서 저장 API 호출
}
```

---

## 10. 테스트 전략

### 10.1 단위 테스트

```bash
pytest tests/unit/services/test_employee_section_service.py -v
pytest tests/unit/services/test_attachment_service.py -v
```

### 10.2 통합 테스트

```bash
pytest tests/blueprints/test_employees_api.py -v
pytest tests/blueprints/test_employees_files.py -v
```

### 10.3 E2E 테스트

| 시나리오 | 단계 |
|---------|------|
| 인라인 편집 | 편집 버튼 -> 입력 -> 저장 -> 값 확인 |
| 사이드바 검색 | 입력 -> 결과 대기 -> 선택 -> 페이지 이동 |
| 파일 드래그 순서 | 드래그 -> 드롭 -> 새로고침 -> 순서 유지 |

### 10.4 계정 타입별 검증

1. **Corporate** 계정 로그인 -> 직원 상세 -> 모든 기능 테스트
2. **Personal** 계정 로그인 -> 프로필 -> 제한된 편집 확인
3. **Employee Sub** 계정 로그인 -> 읽기 전용 확인

---

## 11. 안전 점검 체크리스트

### 11.1 Database Safety

- [ ] 마이그레이션 파일 생성 (`display_order` 필드)
- [ ] 롤백 마이그레이션 준비
- [ ] 기존 데이터 영향 없음 확인 (nullable 또는 default 값)

### 11.2 API Safety

- [x] 인증 데코레이터 적용 (`@corporate_login_required`) - 기존 API 완료
- [ ] 권한 검증 (본인 또는 관리자만 수정) - 신규 API 필요
- [ ] 입력값 검증 (XSS, SQL Injection 방지)
- [x] CSRF 토큰 포함 - 기존 구현

### 11.3 Frontend Safety

- [ ] 에러 핸들링 (네트워크 실패, 서버 오류)
- [ ] 로딩 상태 표시
- [x] 사용자 피드백 (성공/실패 토스트) - toast.js 완료

### 11.4 Rollback Plan

| 단계 | 롤백 방법 |
|------|----------|
| CSS 변경 | `git revert` |
| JS 변경 | `git revert` |
| DB 마이그레이션 | `alembic downgrade -1` |
| API 변경 | 기능 플래그로 비활성화 |

---

## 12. 규칙 준수 체크리스트

- [x] 인라인 스타일 사용 금지 -> CSS 파일로 분리
- [x] 인라인 이벤트 핸들러 금지 -> `addEventListener` 사용
- [x] 하드코딩 색상 금지 -> CSS 변수 사용
- [x] Blueprint -> Repository 직접 호출 금지 -> Service 경유
- [x] 트랜잭션: `atomic_transaction()` 사용

---

## 13. 참고 패턴

### 13.1 기존 패턴 참조

| 패턴 | 참조 파일 |
|------|----------|
| JS 컴포넌트 | `js/shared/components/accordion.js` |
| CSS 컴포넌트 | `css/shared/components/modal.css` |
| Service Facade | `employee_service.py` |
| Blueprint API | `employees/files.py` |

### 13.2 의존성 검증 (업데이트됨)

| 의존성 | 현재 상태 | 필요 조치 |
|--------|----------|----------|
| `theme.css` | 완료 (3개 계정 타입) | 없음 |
| `variables.css` | 완료 | HR Card 호환 변수 포함 |
| `data-table-advanced.css` | 완료 | 드래그/첨부 스타일 포함 |
| `toast.js` | 완료 | CSS 이미 분리됨 |
| `BaseRepository` | 완료 | 없음 |
| `atomic_transaction()` | 완료 | 서비스에서 사용 중 |
| `Attachment 도메인` | 완료 | Phase 31 완료 |

---

## 14. 모니터링 항목

### 14.1 Blockers to Monitor

1. ~~기존 `toast.js`와 새 CSS 충돌~~ -> 해결됨
2. 드래그 앤 드롭 터치 디바이스 호환성
3. 인라인 편집 시 기존 폼 유효성 검증 연동
4. 계정 타입별 권한 로직 복잡도

### 14.2 Critical Path (수정됨)

```
[완료] Phase 01 -> [완료] Phase 03a/03b
                -> [진행중] Phase 02 (drag-order-manager.js)
                -> [진행중] Phase 04 (sidebar-search.js)
                -> [진행중] Phase 06 (file-panel.js)
                -> [진행중] Phase 07 (순서 API)
                -> [미완료] Phase 05 (inline-edit.js + API) <- 가장 복잡
```

---

## 15. 잔여 작업 상세

### 15.1 우선순위 1: inline-edit.js + PATCH API (1.5일)

**JavaScript 컴포넌트 (`js/domains/employee/components/inline-edit.js`)**:
- 섹션별 편집 모드 토글 (edit-mode 클래스)
- 원본 값 백업/복원 (취소 시 복원)
- API 호출 및 저장 (PATCH 요청)
- 계정 타입별 권한 체크 (corporate만 편집 가능)
- 성공/실패 토스트 표시

**API 엔드포인트 (`PATCH /api/employees/<id>/sections/<section>`)**:
- 섹션: personal_info, address_info, physical_info, military_info
- 필드별 검증
- 권한 검증 (관리자 또는 본인)
- 감사 로깅

### 15.2 우선순위 2: sidebar-search.js (0.6일)

**JavaScript 컴포넌트 (`js/domains/employee/components/sidebar-search.js`)**:
- 디바운스 검색 (300ms)
- 최소 2글자 이상 입력 시 검색
- 모달로 결과 표시
- 결과 클릭 시 해당 직원 상세 페이지 이동
- 검색 결과 없음 표시

**화면 연결 방식**:
```javascript
// 검색 결과 클릭 시 직원 상세 페이지로 이동
function selectEmployee(empId) {
    closeModal('search-result-modal');
    window.location.href = `/employees/${empId}`;
}
```

### 15.3 우선순위 3: drag-order-manager.js (0.5일)

**범용 드래그 순서 관리자 (`js/shared/components/drag-order-manager.js`)**:
- 테이블/리스트 공용 (data-draggable 속성)
- 드래그 핸들 지원 (.drag-handle)
- 순서 변경 API 호출 (configurable endpoint)
- 성공/실패 피드백

### 15.4 우선순위 4: 순서 변경 API (0.3일)

**API 엔드포인트**:
- `PATCH /api/employees/<id>/educations/order`
- `PATCH /api/employees/<id>/careers/order`
- `PATCH /api/employees/<id>/certificates/order`

**요청 형식**:
```json
{
  "order": [3, 1, 2]  // 새 순서의 ID 배열
}
```

### 15.5 우선순위 5: file-panel.js (0.2일)

**우측 패널 UI (`js/domains/employee/components/file-panel.js`)**:
- 파일 목록 렌더링 (기존 API 활용)
- 드래그 정렬 (drag-order-manager 활용)
- 업로드 Zone 연동
- 삭제 확인 모달

### 15.6 우선순위 6: Section Nav → Sidebar Migration (0.5일)

**CSS (`css/shared/layouts/section-nav.css` 확장)**:
- `.employee-card-nav` 스타일 (프로필 카드)
- `.sub-nav` 확장/축소 애니메이션
- 라이트/다크 테마 변형

**JavaScript (`js/shared/components/sidebar-nav.js`)**:
- 카드 클릭 시 확장/축소 토글
- 섹션 항목 클릭 시 해당 섹션으로 스크롤
- active 상태 관리

**Template**:
- 사이드바에 `employee-card-nav` 마크업 추가
- 섹션 목록 동적 생성 (Jinja2 매크로)

### 15.7 우선순위 7: 기존 수정 페이지 삭제 + 인라인 확장 (2.5일)

**Phase 09-A: 테이블형 인라인 편집 JS (1.0일)**
- `inline-edit-table.js` 신규 생성
- 행 추가/수정/삭제 기능
- drag-order-manager.js 연동 (순서 변경)
- 모달 기반 행 편집 폼

**Phase 09-B: PATCH API 확장 (0.5일)**
| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/<id>/educations` | POST | 학력 추가 |
| `/api/employees/<id>/educations/<row_id>` | PATCH | 학력 수정 |
| `/api/employees/<id>/educations/<row_id>` | DELETE | 학력 삭제 |
(경력, 자격증, 가족, 어학, 수상 동일 패턴)

**Phase 09-C: 기존 시스템 삭제 (0.5일)**
- 라우트: `detail_routes.py`에서 edit 라우트 삭제
- 라우트: `mutation_routes.py`에서 update 라우트 삭제
- 템플릿: `partials/form/` 디렉토리 삭제

**Phase 09-D: detail 템플릿 수정 (0.5일)**
- `_basic_info.html`, `_history_info.html` 등에 인라인 편집 마크업 통합
- 테이블형 섹션에 편집 버튼 추가

---

## 16. 관련 문서

### 16.1 영역별 분할 계획 (우선순위 순)

| 우선순위 | 영역 | 파일 | 기간 | 비고 |
|---------|------|------|------|------|
| **1순위** | 메인 | `claudedocs/hrcard-plan-main.md` | 5.0일 | 인라인 편집, 기존 폼 삭제 |
| **2순위** | 사이드바 | `claudedocs/hrcard-plan-sidebar.md` | 1.1일 | 검색, 섹션 네비게이션 |
| **3순위** | 첨부파일 | `claudedocs/hrcard-plan-attachment.md` | 1.1일 | 파일 패널, 드래그 순서, **백엔드 정비 추가** |

### 16.2 권장 실행 순서

```
Week 1 (Day 1-5):
  [1순위] 메인 영역 (5.0일)
  ├─ Phase 02: drag-order-manager.js (0.5일)
  ├─ Phase 05: inline-edit.js (1.5일)
  └─ Phase 09: 기존 삭제 + 확장 (2.5일)

  [3순위 - 병렬 진행] Phase 06a (0.1일)
  └─ 첨부파일 순서 API (메인 영역과 병렬 가능)

Week 2 (Day 5-6.5):
  [2순위] 사이드바 영역 (1.1일)
  ├─ Phase 04: sidebar-search.js (0.6일)
  └─ Phase 08: section-nav migration (0.5일)

  [3순위] 첨부파일 영역 (1.0일)
  ├─ Phase 06b: file-panel.js (0.2일)
  └─ Phase 07: 순서 변경 API (0.3일)

Day 7.5-8.8:
  통합 테스트 (0.5일)
```

**Note**: 첨부파일 영역 Phase 06a (백엔드 순서 API)는 메인 영역과 병렬 진행 가능

### 16.3 기존 서브 플랜 (참조용)
- `~/.claude/plans/hrcard-01-css-foundation.md`
- `~/.claude/plans/hrcard-02-shared-components.md`
- `~/.claude/plans/hrcard-03a-header-card.md`
- `~/.claude/plans/hrcard-03b-info-section.md`
- `~/.claude/plans/hrcard-04-sidebar-search.md`
- `~/.claude/plans/hrcard-05-inline-edit.md`
- `~/.claude/plans/hrcard-06-file-panel.md`
- `~/.claude/plans/hrcard-07-data-tables.md`

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-08 | 최초 작성 |
| 2026-01-11 | 현황 분석 및 진행률 업데이트, 잔여 작업 상세 추가 |
| 2026-01-11 | Phase 08 (Section Nav Migration), Phase 09 (기존 수정 삭제 + 인라인 확장) 추가 |
| 2026-01-11 | 수정 페이지 전략 변경: 병행 → 대체 (인라인 편집이 기존 폼 완전 대체) |
| 2026-01-11 | sidebar-search.js 화면 연결 방식 명시 (`/employees/<id>` 이동) |
| 2026-01-11 | 예상 기간 수정: 5.5일 → 8.5일 (+3.0일) |
