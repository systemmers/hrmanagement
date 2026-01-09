# HR Card Demo Migration Plan

> 마이그레이션 계획 문서
> 생성일: 2026-01-08
> 소스: `.dev_docs/demos/hr_card/hr-card.html` (284KB, ~6,100 lines)
Reading Plan(C:\Users\sangj\.claude\plans\fancy-dreaming-lecun.md)
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

### 1.3 예상 기간
**총 11일** (Phase 1~7)

---

## 2. 서브 플랜 구조

### 2.1 플랜 목록

| 번호 | 내용 | 기간 | 위험도 | 의존성 |
|------|------|------|--------|--------|
| **01** | CSS Foundation - 변수 정렬 | 0.5일 | 낮음 | 없음 |
| **02** | Shared Components - Modal/Toast/DragDrop | 2일 | 중간 | 01 |
| **03a** | Header Card - 헤더/명함 | 1일 | 낮음 | 01 |
| **03b** | Info Section - 정보 테이블 | 1일 | 낮음 | 01 |
| **04** | Sidebar Search - 검색 기능 | 1.5일 | 중간 | 02 |
| **05** | Inline Edit - 인라인 편집 | 2.5일 | 높음 | 02, 03 |
| **06** | File Panel - 첨부파일 패널 | 1.5일 | 낮음 | 02 |
| **07** | Data Tables - 테이블 드래그 | 1일 | 낮음 | 02, 06 |

### 2.2 실행 순서 (권장)

```
Day 1:
  [01-css-foundation]

Day 1-3 (병렬 실행):
  [02-shared-components]
  [03a-header-card]
  [03b-info-section]

Day 4-5:
  [06-file-panel] (낮은 위험, 먼저 실행)

Day 5-6:
  [04-sidebar-search]

Day 6-7:
  [07-data-tables]

Day 7-10:
  [05-inline-edit] (가장 복잡, 마지막)
```

---

## 3. 계정 타입별 디자인

### 3.1 테마 시스템

| 계정 타입 | CSS Selector | 테마 색상 | 용도 |
|----------|--------------|----------|------|
| Corporate | `[data-account-type="corporate"]` | Blue (#2563EB) | 법인 관리자 |
| Personal | `[data-account-type="personal"]` | Green (#059669) | 개인 사용자 |
| Employee Sub | `[data-account-type="employee_sub"]` | Purple (#7C3AED) | 법인 소속 직원 |

### 3.2 컴포넌트별 차이점

| 컴포넌트 | Corporate | Personal | Employee Sub |
|---------|-----------|----------|--------------|
| 헤더 그라데이션 | Blue | Green | Purple |
| 명함 영역 | 표시 | **숨김** | 표시 |
| 인라인 편집 | 전체 섹션 | 개인 정보만 | 읽기 전용 |
| 파일 첨부 | 전체 관리 | 본인 파일 | 읽기 전용 |
| 사이드바 검색 | 전체 직원 | N/A | N/A |
| Status Badge | 표시 | 숨김 | 표시 |

---

## 4. 수정 페이지 전략

### 4.1 병행(Parallel) 전략 채택

인라인 편집과 기존 수정 페이지 **공존**

| 기능 | 인라인 편집 | 기존 수정 페이지 |
|------|------------|-----------------|
| 용도 | 빠른 단일 필드/섹션 수정 | 대량 데이터 입력, 복잡한 수정 |
| UX | 상세보기 -> 즉시 수정 | 전체 폼 -> 일괄 저장 |
| 적용 섹션 | 기본정보, 주소, 신체, 병역 | 학력, 경력, 자격증, 가족 |

### 4.2 섹션별 적용

**인라인 편집 적용**:
- `personal_info` - 기본 인적사항
- `address_info` - 주소 정보
- `physical_info` - 신체 정보
- `military_info` - 병역 정보

**기존 수정 페이지 유지**:
- `education` - 학력 (테이블형, 다중 행)
- `career` - 경력 (테이블형, 다중 행)
- `certificate` - 자격증 (테이블형, 다중 행)
- `family` - 가족관계 (테이블형, 다중 행)

---

## 5. 파일 생성/수정 요약

### 5.1 신규 CSS (6개)

```
css/shared/components/toast.css
css/domains/employee/info-section.css
css/domains/employee/info-table.css
css/domains/employee/inline-edit.css
css/domains/employee/file-panel.css
css/domains/employee/sidebar-search.css
```

### 5.2 확장 CSS (5개)

```
css/shared/core/variables.css           # Demo 호환 변수
css/shared/components/button.css        # btn-dark, btn-header
css/shared/components/data-table-advanced.css  # 드래그, 첨부 컬럼
css/domains/employee/header.css         # status-badge, stats-row
css/domains/employee/business-card.css  # 3D 플립 효과
```

### 5.3 신규 JavaScript (5개)

```
js/shared/components/modal.js
js/shared/components/drag-order-manager.js
js/domains/employee/components/inline-edit.js
js/domains/employee/components/sidebar-search.js
js/domains/employee/components/file-panel.js
```

### 5.4 신규 Template (3개)

```
templates/domains/employee/partials/detail/_file_panel.html
templates/domains/employee/partials/detail/_inline_section.html
templates/shared/macros/_sidebar_search.html
```

### 5.5 신규 Service (1개)

```
app/domains/employee/services/employee_section_service.py
```

### 5.6 Model 확장 (3개)

```python
# Education, Career, Certificate 모델에 추가
display_order = db.Column(db.Integer, default=0)
```

---

## 6. API 엔드포인트

### 6.1 검색 API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/search` | GET | `?q=검색어&limit=10` |

### 6.2 인라인 편집 API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/<id>/sections/<section>` | PATCH | 섹션별 부분 업데이트 |

### 6.3 첨부파일 API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/<id>/attachments` | GET | 첨부파일 목록 |
| `/api/employees/<id>/attachments` | POST | 파일 업로드 |
| `/api/employees/<id>/attachments/<file_id>` | DELETE | 파일 삭제 |
| `/api/employees/<id>/attachments/order` | PATCH | 순서 변경 |

### 6.4 순서 변경 API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/<id>/educations/order` | PATCH | 학력 순서 |
| `/api/employees/<id>/careers/order` | PATCH | 경력 순서 |
| `/api/employees/<id>/certificates/order` | PATCH | 자격증 순서 |

---

## 7. 주요 CSS 패턴

### 7.1 Info Section Card

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

### 7.2 Info Table (2열 그리드)

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

### 7.3 Business Card 3D Flip

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

### 7.4 Status Badge

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

## 8. JavaScript 클래스 구조

### 8.1 InlineEditManager

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

### 8.2 SidebarSearch

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

### 8.3 TableDragOrder

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

## 9. 테스트 전략

### 9.1 단위 테스트

```bash
pytest tests/unit/services/test_employee_section_service.py -v
pytest tests/unit/services/test_attachment_service.py -v
```

### 9.2 통합 테스트

```bash
pytest tests/blueprints/test_employees_api.py -v
pytest tests/blueprints/test_employees_files.py -v
```

### 9.3 E2E 테스트

| 시나리오 | 단계 |
|---------|------|
| 인라인 편집 | 편집 버튼 -> 입력 -> 저장 -> 값 확인 |
| 사이드바 검색 | 입력 -> 결과 대기 -> 선택 -> 페이지 이동 |
| 파일 드래그 순서 | 드래그 -> 드롭 -> 새로고침 -> 순서 유지 |

### 9.4 계정 타입별 검증

1. **Corporate** 계정 로그인 -> 직원 상세 -> 모든 기능 테스트
2. **Personal** 계정 로그인 -> 프로필 -> 제한된 편집 확인
3. **Employee Sub** 계정 로그인 -> 읽기 전용 확인

---

## 10. 안전 점검 체크리스트

### 10.1 Database Safety

- [ ] 마이그레이션 파일 생성 (`display_order` 필드)
- [ ] 롤백 마이그레이션 준비
- [ ] 기존 데이터 영향 없음 확인 (nullable 또는 default 값)

### 10.2 API Safety

- [ ] 인증 데코레이터 적용 (`@corporate_login_required`)
- [ ] 권한 검증 (본인 또는 관리자만 수정)
- [ ] 입력값 검증 (XSS, SQL Injection 방지)
- [ ] CSRF 토큰 포함

### 10.3 Frontend Safety

- [ ] 에러 핸들링 (네트워크 실패, 서버 오류)
- [ ] 로딩 상태 표시
- [ ] 사용자 피드백 (성공/실패 토스트)

### 10.4 Rollback Plan

| 단계 | 롤백 방법 |
|------|----------|
| CSS 변경 | `git revert` |
| JS 변경 | `git revert` |
| DB 마이그레이션 | `alembic downgrade -1` |
| API 변경 | 기능 플래그로 비활성화 |

---

## 11. 규칙 준수 체크리스트

- [ ] 인라인 스타일 사용 금지 -> CSS 파일로 분리
- [ ] 인라인 이벤트 핸들러 금지 -> `addEventListener` 사용
- [ ] 하드코딩 색상 금지 -> CSS 변수 사용
- [ ] Blueprint -> Repository 직접 호출 금지 -> Service 경유
- [ ] 트랜잭션: `atomic_transaction()` 사용

---

## 12. 참고 패턴

### 12.1 기존 패턴 참조

| 패턴 | 참조 파일 |
|------|----------|
| JS 컴포넌트 | `js/shared/components/accordion.js` |
| CSS 컴포넌트 | `css/shared/components/modal.css` |
| Service Facade | `employee_service.py` |
| Blueprint API | `employees/files.py` |

### 12.2 의존성 검증

| 의존성 | 현재 상태 | 필요 조치 |
|--------|----------|----------|
| `theme.css` | 존재 (3개 계정 타입) | 없음 |
| `variables.css` | 존재 | Demo 호환 alias 추가 |
| `data-table-advanced.css` | 존재 | 드래그/첨부 스타일 확장 |
| `toast.js` | 존재 | CSS 분리 필요 |
| `BaseRepository` | 존재 | 없음 |
| `atomic_transaction()` | 존재 | 서비스에서 사용 |

---

## 13. 모니터링 항목

### 13.1 Blockers to Monitor

1. 기존 `toast.js`와 새 CSS 충돌
2. 드래그 앤 드롭 터치 디바이스 호환성
3. 인라인 편집 시 기존 폼 유효성 검증 연동
4. 계정 타입별 권한 로직 복잡도

### 13.2 Critical Path

```
Phase 1 -> Phase 2/3 (병렬) -> Phase 6 -> Phase 4 -> Phase 7 -> Phase 5
```

---

## 14. 관련 문서

- **마스터 플랜**: `~/.claude/plans/fancy-dreaming-lecun.md`
- **서브 플랜**:
  - `~/.claude/plans/hrcard-01-css-foundation.md`
  - `~/.claude/plans/hrcard-02-shared-components.md`
  - `~/.claude/plans/hrcard-03a-header-card.md`
  - `~/.claude/plans/hrcard-03b-info-section.md`
  - `~/.claude/plans/hrcard-04-sidebar-search.md`
  - `~/.claude/plans/hrcard-05-inline-edit.md`
  - `~/.claude/plans/hrcard-06-file-panel.md`
  - `~/.claude/plans/hrcard-07-data-tables.md`
