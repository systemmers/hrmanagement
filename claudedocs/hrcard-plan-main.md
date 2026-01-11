# HR Card Migration - 메인 영역

> 분할 계획 2/3: 헤더 카드, 정보 섹션, 인라인 편집
> 생성일: 2026-01-11
> 우선순위: **1순위** (최우선 개발)

---

## 1. 개요

### 1.1 범위
- 헤더 카드 (프로필 + 명함)
- 정보 섹션 (2열 그리드)
- 인라인 편집 (단일 필드 + 테이블형)
- 기존 수정 페이지 삭제

### 1.2 예상 기간
**총 5.0일** (잔여 작업)

### 1.3 진행률
**약 55%** (CSS 거의 완료, JS/API 미완료)

---

## 2. Phase 목록

| Phase | 내용 | 기간 | 진행률 | 상태 |
|-------|------|------|--------|------|
| **01** | CSS Foundation | 0일 | 100% | **완료** |
| **02** | Shared Components (drag-order-manager) | 0.5일 | 80% | 진행중 |
| **03a** | Header Card | 0일 | 90% | 거의완료 |
| **03b** | Info Section | 0일 | 95% | 거의완료 |
| **05** | Inline Edit | 1.5일 | 40% | 미완료 |
| **09** | 기존 수정 삭제 + 인라인 확장 | 2.5일 | 0% | 미완료 |

**핵심 작업**: Phase 05, 09 (총 4.0일)

---

## 3. 상세 작업

### 3.1 Phase 02 잔여: drag-order-manager.js (0.5일)

**범용 드래그 순서 관리자** (`js/shared/components/drag-order-manager.js`):
```javascript
class DragOrderManager {
    constructor(container, options) {
        this.options = {
            handleSelector: '.drag-handle',
            itemSelector: '[data-draggable]',
            apiEndpoint: null,
            onOrderChange: null
        };
    }

    _setupDragEvents() { }  // 드래그 이벤트 설정
    _handleDragStart() { }
    _handleDragOver() { }
    _handleDrop() { }
    _saveOrder() { }        // 순서 저장 API 호출
}
```

### 3.2 Phase 05: Inline Edit (1.5일)

**JavaScript 컴포넌트** (`js/domains/employee/components/inline-edit.js`):
```javascript
class InlineEditManager {
    constructor(sectionElement) {
        this.section = sectionElement;
        this.sectionName = sectionElement.dataset.section;
        this.originalValues = {};
        this.isEditing = false;
    }

    toggleEditMode() {
        if (this.isEditing) {
            this._showViewMode();
        } else {
            this._checkEditPermission();
            this._backupOriginalValues();
            this._showEditMode();
        }
        this.isEditing = !this.isEditing;
    }

    async saveChanges() {
        const data = this._collectFormData();
        const response = await fetch(
            `/api/employees/${this.employeeId}/sections/${this.sectionName}`,
            {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }
        );

        if (response.ok) {
            Toast.success('저장되었습니다.');
            this._showViewMode();
        } else {
            Toast.error('저장에 실패했습니다.');
        }
    }

    cancelEdit() {
        this._restoreOriginalValues();
        this._showViewMode();
        this.isEditing = false;
    }

    _checkEditPermission() { }  // 계정 타입별 권한
    _backupOriginalValues() { }
    _restoreOriginalValues() { }
    _collectFormData() { }
    _showEditMode() { }
    _showViewMode() { }
}
```

**API 엔드포인트** (`PATCH /api/employees/<id>/sections/<section>`):
```python
@bp.route('/api/employees/<int:id>/sections/<section>', methods=['PATCH'])
@corporate_login_required
def update_section(id, section):
    """섹션별 부분 업데이트"""
    allowed_sections = ['personal_info', 'address_info', 'physical_info', 'military_info']
    if section not in allowed_sections:
        return jsonify({'error': 'Invalid section'}), 400

    data = request.get_json()
    # 필드별 검증
    # 권한 검증 (관리자 또는 본인)
    # 업데이트 실행
    # 감사 로깅
    return jsonify({'success': True})
```

### 3.3 Phase 09: 기존 수정 삭제 + 인라인 확장 (2.5일)

#### 3.3.1 테이블형 인라인 편집 JS (1.0일)

**inline-edit-table.js**:
```javascript
class InlineEditTable {
    constructor(tableElement, options) {
        this.table = tableElement;
        this.entityType = tableElement.dataset.entityType; // education, career, etc.
        this.employeeId = tableElement.dataset.employeeId;
    }

    addRow() {
        // 모달 폼 열기
        this._openRowModal();
    }

    editRow(rowId) {
        // 해당 행 데이터로 모달 열기
        const rowData = this._getRowData(rowId);
        this._openRowModal(rowData);
    }

    async deleteRow(rowId) {
        if (!confirm('삭제하시겠습니까?')) return;

        const response = await fetch(
            `/api/employees/${this.employeeId}/${this.entityType}s/${rowId}`,
            { method: 'DELETE' }
        );

        if (response.ok) {
            this._removeRowFromDOM(rowId);
            Toast.success('삭제되었습니다.');
        }
    }

    async saveRow(formData) {
        const method = formData.id ? 'PATCH' : 'POST';
        const url = formData.id
            ? `/api/employees/${this.employeeId}/${this.entityType}s/${formData.id}`
            : `/api/employees/${this.employeeId}/${this.entityType}s`;

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            this._refreshTable();
            Toast.success('저장되었습니다.');
        }
    }

    _openRowModal(data = null) { }
    _getRowData(rowId) { }
    _removeRowFromDOM(rowId) { }
    _refreshTable() { }
}
```

#### 3.3.2 PATCH API 확장 (0.5일)

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/<id>/educations` | POST | 학력 추가 |
| `/api/employees/<id>/educations/<row_id>` | PATCH | 학력 수정 |
| `/api/employees/<id>/educations/<row_id>` | DELETE | 학력 삭제 |

(경력, 자격증, 가족, 어학, 수상 동일 패턴)

#### 3.3.3 기존 시스템 삭제 (0.5일)

**삭제할 라우트** (`detail_routes.py`, `mutation_routes.py`):
- `GET /employees/<id>/edit`
- `GET /employees/<id>/edit/basic`
- `GET /employees/<id>/edit/history`
- `POST /employees/<id>/update`
- `POST /employees/<id>/update/basic`
- `POST /employees/<id>/update/history`

**삭제할 템플릿** (`templates/domains/employee/partials/form/`):
- 16개 파일 전체 삭제

#### 3.3.4 detail 템플릿 수정 (0.5일)

- `_basic_info.html` - 인라인 편집 마크업 통합
- `_history_info.html` - 테이블형 편집 버튼 추가
- `_hr_records.html` - 테이블형 편집 버튼 추가

---

## 4. 의존성 다이어그램

```
Phase 01 (완료)
    ↓
Phase 02 (drag-order-manager) ─────┐
    ↓                              ↓
Phase 03a/03b (거의완료)      Phase 05 (인라인 편집)
                                   ↓
                              Phase 09 (기존 삭제 + 확장)
```

---

## 5. 실행 순서

```
Day 1:
  [drag-order-manager.js] Phase 02 잔여 (0.5일)
  - 드래그 이벤트 설정
  - 순서 저장 API 연동

Day 1.5-3:
  [inline-edit.js + PATCH API] Phase 05 (1.5일)
  - InlineEditManager 클래스 구현
  - 섹션별 PATCH API 구현
  - 권한 검증 로직

Day 3-5.5:
  [기존 수정 삭제 + 인라인 확장] Phase 09 (2.5일)
  - inline-edit-table.js 구현 (1.0일)
  - 관계형 데이터 API 확장 (0.5일)
  - 기존 라우트/템플릿 삭제 (0.5일)
  - detail 템플릿 수정 (0.5일)
```

---

## 6. 테스트 체크리스트

### 6.1 Inline Edit (단일 필드)
- [ ] 편집 버튼 클릭 시 편집 모드 전환
- [ ] 취소 시 원본 값 복원
- [ ] 저장 시 API 호출 및 성공 토스트
- [ ] Corporate 계정만 편집 가능
- [ ] Employee Sub 계정 읽기 전용

### 6.2 Inline Edit (테이블형)
- [ ] 행 추가 모달 동작
- [ ] 행 수정 모달 동작
- [ ] 행 삭제 확인 및 API 호출
- [ ] 드래그 순서 변경 동작

### 6.3 기존 시스템 삭제 확인
- [ ] `/employees/<id>/edit` 라우트 404
- [ ] form/ 템플릿 디렉토리 삭제 확인
- [ ] 기존 폼 관련 JS 삭제 확인

---

## 7. 파일 목록

### 7.1 생성할 파일
| 파일 | 경로 |
|------|------|
| drag-order-manager.js | `js/shared/components/` |
| inline-edit.js | `js/domains/employee/components/` |
| inline-edit-table.js | `js/domains/employee/components/` |
| section_api.py | `app/domains/employee/blueprints/` |

### 7.2 수정할 파일
| 파일 | 수정 내용 |
|------|----------|
| detail_routes.py | edit 라우트 삭제 |
| mutation_routes.py | update 라우트 삭제 |
| _basic_info.html | 인라인 편집 마크업 추가 |
| _history_info.html | 테이블형 편집 버튼 추가 |

### 7.3 삭제할 파일
| 경로 | 파일 수 |
|------|--------|
| `templates/domains/employee/partials/form/` | 16개 전체 |

---

## 8. 위험 요소

| 위험 | 영향도 | 완화 방안 |
|------|--------|----------|
| 기존 폼 삭제 시 누락 | 높음 | 삭제 전 기능 목록 점검 |
| 인라인 편집 권한 로직 | 중간 | 기존 decorators 재사용 |
| 테이블형 편집 복잡도 | 높음 | 단계별 구현 (추가→수정→삭제→순서) |
