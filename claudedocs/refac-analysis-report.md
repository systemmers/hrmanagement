# Refactoring Analysis Report

**분석 일자**: 2026-01-08
**대상 문서**: `.dev_docs/dev_plans/refac.md`
**분석 방법**: Sequential Thinking + Codebase Exploration

---

## 1. 요구사항 분석

### 1.1 직원 목록 (Employee List)

| 요구사항 | 상세 |
|---------|------|
| 정렬 셀렉트 스타일 통일 | 필터바 셀렉트 스타일을 표준으로 전체 적용 |
| 정렬 셀렉트 필터바 통합 | 정렬 라벨 제거, "기본순" → "정렬", 오른쪽 정렬 |
| 뷰모드 유지 버그 수정 | 카드형 보기 후 정렬/필터 적용 시 리스트형 전환 방지 |

### 1.2 계정발급 (Account Issuance)

| 요구사항 | 상세 |
|---------|------|
| 사이드바 메뉴 제거 | 직원 관리 > 계정 발급 항목 삭제 |
| 모달 UX 전환 | 계정관리 > 계정추가 버튼 → 모달로 진행 |

### 1.3 계약목록 (Contract List)

| 요구사항 | 상세 |
|---------|------|
| 이니셜 아이콘 제거 | 이름 칼럼 일관성 유지 |
| 취소 아이콘 추가 | 계약진행중(requested) 상태에서 취소 버튼 표시 |
| 계약요청 모달화 | 상단 버튼 클릭 → 모달 프로세스 |

### 1.4 계약요청 (Contract Request)

| 요구사항 | 상세 |
|---------|------|
| 사이드바 메뉴 제거 | (존재 시) 계약요청 메뉴 삭제 |
| 모달 플로우 구현 | 계약대상 선택 → 계약정보 입력 → 계약 요청 |

### 1.5 대기중 (Pending)

| 요구사항 | 상세 |
|---------|------|
| 페이지 제거 | pending_contracts.html 폐기 |
| 계약목록 통합 | 상태 컬럼 추가, 상세보기 기능 |

### 1.6 계정관리 (Account Management)

| 요구사항 | 상세 |
|---------|------|
| 이니셜 아이콘 제거 | 아이디 칼럼 일관성 유지 |
| 상태변경 기능 추가 | 계정탈퇴, 계정휴면, 기타 일반 |
| 수정 기능 구현 | 작업 칼럼 수정 버튼 활성화 |

---

## 2. 현재 구현 상태

### 2.1 직원 목록

**파일 위치**:
- Template: `app/templates/domains/employee/list.html`
- JavaScript: `app/static/js/domains/employee/pages/list.js`
- CSS: `app/static/css/shared/layouts/main-content.css`, `app/static/css/shared/components/filter.css`
- Route: `app/domains/employee/blueprints/list_routes.py`

**현재 구현**:
```
┌─────────────────────────────────────────────────────────┐
│ 페이지 헤더: 제목 | 뷰 토글 | 직원 등록 버튼           │
├─────────────────────────────────────────────────────────┤
│ 필터바: 검색 | 부서 | 직급 | 상태 (filter-bar--simple) │
├─────────────────────────────────────────────────────────┤
│ 정렬바: "정렬:" 라벨 | 정렬 셀렉트 (sort-bar)          │  ← 분리됨
├─────────────────────────────────────────────────────────┤
│ 목록형/카드형 뷰                                        │
└─────────────────────────────────────────────────────────┘
```

**GAP**:
1. 정렬바가 필터바와 분리됨 (`.sort-bar` vs `.filter-bar`)
2. 정렬 셀렉트 스타일이 필터 셀렉트와 다름 (`.sort-select` vs `.filter-select`)
3. 뷰모드 전환 후 URL 파라미터 리로드 시 뷰모드 초기화됨
   - 원인: `FilterBar.apply()`가 `window.location.href` 설정 시 view 파라미터 미포함

### 2.2 계정발급

**파일 위치**:
- Template: `app/templates/domains/employee/account_provision.html`
- JavaScript: `app/static/js/domains/employee/pages/account-provision.js`
- Route: `app/domains/employee/blueprints/mutation_routes.py` (lines 209-268)
- Sidebar: `app/templates/shared/layouts/_sidebar_unified.html` (lines 175-190)

**현재 구현**:
```
사이드바 메뉴:
├── 직원 관리
│   ├── 직원 목록
│   ├── 직원 등록
│   └── 계정 발급  ← 제거 대상
```

**GAP**:
1. 별도 페이지 `/employees/account-provision` 존재
2. 사이드바에 메뉴 노출

### 2.3 계약목록

**파일 위치**:
- Template: `app/templates/domains/contract/company_contracts.html`
- Macros: `app/templates/shared/macros/_contracts.html`
- JavaScript: `app/static/js/domains/contract/pages/company-contracts.js`
- CSS: `app/static/css/domains/contract/contract.css`
- Route: `app/domains/contract/blueprints/contracts.py`

**현재 구현**:
```html
<!-- 이름 칼럼 (lines 364-405 in _contracts.html) -->
<div class="person-info">
    <div class="person-avatar">{{ contract.person_name[:1] }}</div>  ← 제거 대상
    <span class="person-name">{{ contract.person_name }}</span>
</div>
```

**GAP**:
1. 이니셜 아이콘 `.person-avatar` 존재
2. 계약진행중 상태에서 취소 버튼 없음
3. 계약요청이 별도 페이지

### 2.4 대기중

**파일 위치**:
- Template: `app/templates/domains/contract/pending_contracts.html`
- Route: `app/domains/contract/blueprints/contracts.py` (lines 124-139)

**GAP**:
1. 별도 페이지 존재 (폐기 대상)

### 2.5 계정관리

**파일 위치**:
- Template: `app/templates/domains/company/users.html`
- JavaScript: `app/static/js/domains/company/pages/users.js`
- Route: `app/domains/company/blueprints/corporate.py` (lines 101-146)

**현재 구현**:
```html
<!-- 아이디 칼럼 (lines 47-51 in users.html) -->
<div class="d-flex items-center gap-2">
    <div class="user-avatar-small">{{ user.username[:1]|upper }}</div>  ← 제거 대상
    <span>{{ user.username }}</span>
</div>
```

**작업 칼럼 현재 상태**:
```html
<button data-action="edit-user">수정</button>       <!-- 미구현 -->
<button data-action="toggle-user-status">비활성화</button>  <!-- 미구현 -->
```

**GAP**:
1. 이니셜 아이콘 존재
2. 수정/상태변경 기능 미구현
3. 상태변경 옵션 부족 (탈퇴, 휴면 없음)

---

## 3. 수정 계획

### Phase 1: 직원 목록 UI 통합 (High Priority)

#### 1.1 정렬 셀렉트 필터바 통합

**수정 파일**:

| 파일 | 변경 내용 |
|------|----------|
| `app/templates/domains/employee/list.html` | `.sort-bar` 섹션 제거, filter_bar 내 정렬 셀렉트 추가 |
| `app/templates/shared/macros/_filters.html` | `sort_select` 매크로 추가 (오른쪽 정렬 옵션) |
| `app/static/css/shared/components/filter.css` | `.filter-sort` 스타일 추가 |

**변경 전**:
```html
{% call filter_bar(mode='url', css_class='filter-bar--simple') %}
    {{ search_box(...) }}
    {{ filter_select('department', ...) }}
{% endcall %}

<div class="sort-bar">
    <label class="sort-label">정렬:</label>
    <select class="sort-select" id="sortSelect">...</select>
</div>
```

**변경 후**:
```html
{% call filter_bar(mode='url', css_class='filter-bar--simple') %}
    {{ search_box(...) }}
    {{ filter_select('department', ...) }}
    {{ sort_select('sortSelect', sort_options, selected_sort, '정렬', css_class='filter-sort') }}
{% endcall %}
```

#### 1.2 뷰모드 유지 버그 수정

**수정 파일**:

| 파일 | 변경 내용 |
|------|----------|
| `app/static/js/domains/employee/pages/list.js` | URL 파라미터에서 view 읽기 |
| `app/static/js/shared/components/filter-bar.js` | `preserveParams` 옵션 추가 |

**변경 전** (list.js):
```javascript
function initViewToggle() {
    const savedView = localStorage.getItem('employeeViewPreference') || 'list';
    toggleEmployeeView(savedView);
}
```

**변경 후** (list.js):
```javascript
function initViewToggle() {
    // URL 파라미터 우선, localStorage 백업
    const urlParams = new URLSearchParams(window.location.search);
    const urlView = urlParams.get('view');
    const savedView = urlView || localStorage.getItem('employeeViewPreference') || 'list';
    toggleEmployeeView(savedView);
}

function toggleEmployeeView(view) {
    // ... 기존 로직 ...

    // URL 파라미터 업데이트 (리로드 없이)
    const url = new URL(window.location);
    url.searchParams.set('view', view);
    window.history.replaceState({}, '', url);
}
```

**변경 후** (filter-bar.js):
```javascript
applyUrlMode() {
    const url = new URL(window.location);

    // 기존 view 파라미터 유지
    const currentView = url.searchParams.get('view');

    // 새 필터 적용
    Object.entries(filters).forEach(([key, value]) => {
        // ...
    });

    // view 파라미터 복원
    if (currentView) {
        url.searchParams.set('view', currentView);
    }

    window.location.href = url.toString();
}
```

---

### Phase 2: 사이드바 정리 (Low Priority - Phase 3, 4 완료 후)

**수정 파일**:
- `app/templates/shared/layouts/_sidebar_unified.html`

**변경 내용**:
```html
<!-- 제거: 직원 관리 > 계정 발급 -->
<!-- 제거: 계약 관리 > 계약 요청 (존재 시) -->
```

---

### Phase 3: 계약목록 개선 (High Priority)

#### 3.1 이니셜 아이콘 제거

**수정 파일**:
- `app/templates/shared/macros/_contracts.html` (lines 364-405)

**변경 전**:
```html
<div class="person-info">
    <div class="person-avatar">{{ contract.person_name[:1] }}</div>
    <span class="person-name">{{ contract.person_name }}</span>
</div>
```

**변경 후**:
```html
<span class="person-name">{{ contract.person_name or '이름 없음' }}</span>
```

#### 3.2 계약진행중 취소 아이콘 추가

**수정 파일**:
- `app/templates/shared/macros/_contracts.html` (액션 셀)
- `app/static/js/domains/contract/pages/company-contracts.js`

**변경 내용**:
```html
<!-- 액션 셀 -->
{% if contract.status == 'requested' and contract.requested_by == 'company' %}
<button class="btn-icon btn-icon-danger"
        data-action="cancel-contract"
        data-contract-id="{{ contract.id }}"
        title="계약 요청 취소">
    <i class="fas fa-times-circle"></i>
</button>
{% endif %}
```

```javascript
// company-contracts.js
import { cancelContractRequest } from '../services/contract-service.js';

document.addEventListener('click', async (e) => {
    const cancelBtn = e.target.closest('[data-action="cancel-contract"]');
    if (cancelBtn) {
        const contractId = cancelBtn.dataset.contractId;
        await cancelContractRequest(contractId, {
            confirmMessage: '이 계약 요청을 취소하시겠습니까?'
        });
    }
});
```

#### 3.3 계약요청 모달화

**신규 파일**:
- `app/templates/domains/contract/modals/_contract_request_modal.html`
- `app/static/js/domains/contract/contract-request-modal.js`

**모달 구조**:
```html
<div class="modal" id="contract-request-modal">
    <div class="modal-dialog modal-lg">
        <!-- Step 1: 계약 대상 선택 -->
        <div class="modal-step" data-step="1">
            <h3>계약 대상 선택</h3>
            <div class="target-tabs">
                <button data-target-type="employee">직원 계정</button>
                <button data-target-type="personal">개인 계정</button>
            </div>
            <div class="target-list"><!-- 대상 목록 --></div>
        </div>

        <!-- Step 2: 계약 정보 입력 -->
        <div class="modal-step d-none" data-step="2">
            <h3>계약 정보 입력</h3>
            <form id="contract-info-form">
                <select name="contract_type">...</select>
                <input name="contract_start_date" type="date">
                <input name="contract_end_date" type="date">
                <input name="department">
                <input name="position">
                <textarea name="notes"></textarea>
            </form>
        </div>

        <!-- Step 3: 확인 -->
        <div class="modal-step d-none" data-step="3">
            <h3>계약 요청 확인</h3>
            <div class="contract-summary"><!-- 요약 --></div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
            <button class="btn-prev">이전</button>
            <button class="btn-next">다음</button>
            <button class="btn-submit d-none">계약 요청</button>
        </div>
    </div>
</div>
```

---

### Phase 4: 대기중 페이지 제거 (Medium Priority)

**폐기 파일**:
- `app/templates/domains/contract/pending_contracts.html` → deprecated 주석 추가

**수정 파일**:
- `app/templates/domains/contract/company_contracts.html` - 상태 필터 추가
- `app/domains/contract/blueprints/contracts.py` - 라우트 리다이렉트

**변경 내용**:
```python
# contracts.py
@contracts_bp.route('/company/pending')
def company_pending():
    # 기존 페이지 대신 계약목록으로 리다이렉트
    return redirect(url_for('contracts.company_contracts', status='requested'))
```

---

### Phase 5: 계정관리 개선 (High Priority)

#### 5.1 아이디 칼럼 이니셜 아이콘 제거

**수정 파일**:
- `app/templates/domains/company/users.html` (lines 47-51)

**변경 전**:
```html
<div class="d-flex items-center gap-2">
    <div class="user-avatar-small">{{ user.username[:1]|upper }}</div>
    <span>{{ user.username }}</span>
</div>
```

**변경 후**:
```html
<span>{{ user.username }}</span>
```

#### 5.2 상태변경 기능 구현

**신규/수정 파일**:
- `app/domains/user/blueprints/account/routes.py` - API 추가
- `app/domains/user/services/user_service.py` - 상태변경 로직
- `app/templates/domains/company/users.html` - 드롭다운 UI
- `app/static/js/domains/company/pages/users.js` - 이벤트 핸들러

**상태 옵션**:
```python
ACCOUNT_STATUS_OPTIONS = [
    ('active', '활성'),
    ('dormant', '휴면'),
    ('withdrawn', '탈퇴'),
]
```

**API 엔드포인트**:
```python
@account_bp.route('/corporate/users/<int:user_id>/status', methods=['PATCH'])
@corporate_admin_required
def update_user_status(user_id):
    data = request.get_json()
    new_status = data.get('status')
    reason = data.get('reason')

    result = user_service.update_account_status(user_id, new_status, reason)
    return jsonify(result)
```

**UI 드롭다운**:
```html
<div class="dropdown">
    <button class="btn-icon" data-toggle="dropdown">
        <i class="fas fa-ellipsis-v"></i>
    </button>
    <div class="dropdown-menu">
        <a data-action="edit-user" data-user-id="{{ user.id }}">수정</a>
        <hr>
        <a data-action="change-status" data-user-id="{{ user.id }}" data-status="active">활성화</a>
        <a data-action="change-status" data-user-id="{{ user.id }}" data-status="dormant">휴면 처리</a>
        <a data-action="change-status" data-user-id="{{ user.id }}" data-status="withdrawn">계정 탈퇴</a>
    </div>
</div>
```

---

## 4. 우선순위 및 일정

### 권장 구현 순서

| Sprint | Task | 복잡도 | 영향범위 |
|--------|------|--------|---------|
| **Sprint 1** | 1.2 뷰모드 버그 수정 | 3 | Medium |
| | 1.1 정렬 셀렉트 통합 | 2 | Low |
| | 3.1 계약목록 이니셜 제거 | 1 | Low |
| | 5.1 계정관리 이니셜 제거 | 1 | Low |
| **Sprint 2** | 3.2 취소 아이콘 추가 | 2 | Low |
| | 5.2 상태변경 기능 | 4 | Medium |
| **Sprint 3** | 3.3 계약요청 모달화 | 5 | High |
| | 4.1 대기중 페이지 제거 | 4 | High |
| **Sprint 4** | 2.1 사이드바 메뉴 정리 | 1 | Low |

### 리스크 관리

| 리스크 | 완화 전략 |
|--------|----------|
| 계약요청 모달화 복잡도 | 기존 페이지 유지하면서 점진적 전환 |
| 뷰모드 버그 수정 영향 | 직원 목록 전용 옵션으로 분리 |
| 상태변경 모델 확장 | is_active 외 별도 status 필드 고려 |

---

## 5. 파일 영향 분석

### 수정 대상 파일 목록

```
app/
├── templates/
│   ├── domains/
│   │   ├── employee/
│   │   │   └── list.html                    [Phase 1.1]
│   │   ├── contract/
│   │   │   ├── company_contracts.html       [Phase 3.2, 3.3, 4]
│   │   │   ├── pending_contracts.html       [Phase 4 - deprecated]
│   │   │   └── modals/
│   │   │       └── _contract_request_modal.html [Phase 3.3 - NEW]
│   │   └── company/
│   │       └── users.html                   [Phase 5.1, 5.2]
│   └── shared/
│       ├── layouts/
│       │   └── _sidebar_unified.html        [Phase 2]
│       └── macros/
│           ├── _filters.html                [Phase 1.1]
│           └── _contracts.html              [Phase 3.1, 3.2]
├── static/
│   ├── js/
│   │   ├── domains/
│   │   │   ├── employee/pages/
│   │   │   │   └── list.js                  [Phase 1.2]
│   │   │   ├── contract/
│   │   │   │   ├── pages/company-contracts.js [Phase 3.2]
│   │   │   │   └── contract-request-modal.js  [Phase 3.3 - NEW]
│   │   │   └── company/pages/
│   │   │       └── users.js                 [Phase 5.2]
│   │   └── shared/components/
│   │       └── filter-bar.js                [Phase 1.2]
│   └── css/
│       └── shared/components/
│           └── filter.css                   [Phase 1.1]
└── domains/
    ├── contract/blueprints/
    │   └── contracts.py                     [Phase 4]
    └── user/
        ├── blueprints/account/
        │   └── routes.py                    [Phase 5.2]
        └── services/
            └── user_service.py              [Phase 5.2]
```

### 신규 생성 파일

| 파일 | Phase | 용도 |
|------|-------|------|
| `modals/_contract_request_modal.html` | 3.3 | 계약요청 모달 템플릿 |
| `contract-request-modal.js` | 3.3 | 계약요청 모달 로직 |

### 폐기 예정 파일

| 파일 | Phase | 대체 방안 |
|------|-------|----------|
| `pending_contracts.html` | 4 | 계약목록 상태 필터로 대체 |

---

## 6. 검증 체크리스트

### Phase 1 검증
- [ ] 정렬 셀렉트가 필터바 내에 표시됨
- [ ] 정렬 셀렉트 스타일이 필터 셀렉트와 동일함
- [ ] 정렬 라벨이 없고 "정렬" placeholder 표시
- [ ] 카드형 보기에서 정렬 변경 시 카드형 유지
- [ ] 카드형 보기에서 필터 변경 시 카드형 유지

### Phase 3 검증
- [ ] 계약목록 이름 칼럼에 이니셜 아이콘 없음
- [ ] 계약진행중(requested) 행에 취소 버튼 표시
- [ ] 취소 버튼 클릭 시 확인 모달 표시
- [ ] 취소 성공 시 상태 업데이트
- [ ] 계약 요청 버튼 클릭 시 모달 표시
- [ ] 모달 3단계 플로우 정상 동작

### Phase 5 검증
- [ ] 계정관리 아이디 칼럼에 이니셜 아이콘 없음
- [ ] 작업 칼럼 드롭다운 메뉴 표시
- [ ] 수정 버튼 동작
- [ ] 상태변경 옵션 (활성, 휴면, 탈퇴) 표시
- [ ] 상태변경 성공 시 목록 업데이트

---

## 7. 결론

refac.md 요구사항 분석 결과, 총 **9개 태스크**로 분류되며 **4개 Sprint**로 구현 권장합니다.

**즉시 착수 가능** (Sprint 1):
- 뷰모드 버그 수정 (Critical)
- UI 이니셜 아이콘 제거 (간단)

**기능 개선** (Sprint 2):
- 취소 아이콘 추가
- 상태변경 기능

**UX 전환** (Sprint 3-4):
- 계약요청 모달화
- 대기중 페이지 제거
- 사이드바 정리

핵심은 **점진적 마이그레이션**으로, 기존 기능을 유지하면서 새 UX를 병행 제공한 후 안정화 후 레거시 제거하는 전략입니다.
