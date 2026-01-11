# HR Card Migration - 첨부파일 패널 영역

> 분할 계획 3/3: 우측 첨부파일 패널 및 드래그 순서
> 생성일: 2026-01-11
> 수정일: 2026-01-11 (프론트엔드/백엔드 구조 분석 반영)
> 우선순위: **3순위** (메인/사이드바 완료 후)

---

## 1. 개요

### 1.1 범위
- 우측 첨부파일 패널 UI
- 테이블 드래그 순서 변경
- 파일 업로드/삭제 연동
- 백엔드 아키텍처 정비 (신규 추가)

### 1.2 예상 기간
**총 1.1일** (잔여 작업) - 백엔드 정비 0.3일 추가

### 1.3 진행률
**약 65%** (백엔드 일부 미완료 확인, 프론트엔드 일부 잔여)

---

## 2. Phase 목록

| Phase | 내용 | 기간 | 진행률 | 상태 |
|-------|------|------|--------|------|
| **06a** | Backend Architecture Fix - 아키텍처 정비 | 0.3일 | 0% | **신규** |
| **06b** | File Panel - 첨부파일 패널 | 0.2일 | 85% | 진행중 |
| **07** | Data Tables - 테이블 드래그 | 0.3일 | 70% | 진행중 |

**참고**: 순서 변경은 메인 영역의 `drag-order-manager.js` 활용

---

## 3. 프론트엔드/백엔드 구조 분석 (2026-01-11)

### 3.1 아키텍처 불일치 발견

**분석 결과**: 백엔드 100% 완료가 아님 - 아래 갭 존재

| 항목 | 현재 상태 | 기대 상태 | 갭 유형 |
|------|----------|----------|---------|
| REST API 위치 | `employee/blueprints/files.py` | `attachment/blueprints/routes.py` | 도메인 분리 미완료 |
| attachment_service | read/delete만 존재 | create/upload/order 포함 | 메서드 누락 |
| 순서 변경 API | 없음 | `PATCH /api/.../order` | 미구현 |
| 도메인 Blueprint | 없음 | `attachment/blueprints/` | 미생성 |

### 3.2 현재 구현 상태

**API (employee/blueprints/files.py에 구현)**:
| Endpoint | Method | 상태 | 비고 |
|----------|--------|------|------|
| `/api/employees/<id>/attachments` | GET | 구현됨 | 파일 목록 |
| `/api/employees/<id>/attachments` | POST | 구현됨 | 파일 업로드 |
| `/api/attachments/<id>` | DELETE | 구현됨 | 파일 삭제 |
| `/api/employees/<id>/attachments/order` | PATCH | **미구현** | 순서 변경 |

**Attachment 도메인 (app/domains/attachment/)**:
| 파일 | 상태 | 문제점 |
|------|------|--------|
| models/attachment.py | 완료 | owner_type/owner_id 다형성 |
| repositories/attachment_repository.py | 완료 | CRUD 구현 |
| services/attachment_service.py | **일부** | create/upload 메서드 없음 |
| blueprints/ | **없음** | 디렉토리 미생성 |

### 3.3 권장 조치

**Option A: 현행 유지 (권장)**
- `employee/blueprints/files.py`에서 기능 확장
- 순서 변경 API만 추가
- 추가 작업: 0.1일

**Option B: 도메인 분리 완료**
- `attachment/blueprints/routes.py` 신규 생성
- attachment_service에 create/upload 메서드 추가
- 기존 files.py 라우트를 attachment 도메인으로 이동
- 추가 작업: 0.5일

**결정**: Option A 채택 (최소 변경 원칙)

---

## 4. 완료된 항목

### 4.1 Backend (70% - 수정됨)
| 항목 | 상태 | 비고 |
|------|------|------|
| Attachment 모델 | 완료 | owner_type/owner_id 다형성 |
| attachment_repository.py | 완료 | CRUD 구현 |
| attachment_service.py | 일부 | read/delete만, upload 없음 |
| GET /api/employees/<id>/attachments | 완료 | files.py에 구현 |
| POST /api/employees/<id>/attachments | 완료 | files.py에 구현 |
| DELETE /api/attachments/<id> | 완료 | files.py에 구현 |
| PATCH /api/.../order | **미완료** | 순서 변경 API |

### 4.2 CSS (100%)
| 파일 | 상태 | 경로 |
|------|------|------|
| attachment.css | 완료 | `css/shared/components/` |
| data-table-advanced.css | 완료 | 드래그/첨부 컬럼 포함 |

### 4.3 Styleguide (100%)
| 파일 | 상태 |
|------|------|
| attachment.html | 완료 |

---

## 5. 잔여 작업

### 5.1 Phase 06a: 순서 변경 API 추가 (0.1일) - 신규

**files.py에 추가할 엔드포인트**:
```python
@bp.route('/api/employees/<int:employee_id>/attachments/order', methods=['PATCH'])
@manager_or_admin_required
def update_attachment_order(employee_id):
    """첨부파일 순서 변경 API"""
    data = request.get_json()
    order = data.get('order', [])

    with atomic_transaction():
        for index, attachment_id in enumerate(order):
            attachment = Attachment.query.get(attachment_id)
            if attachment and attachment.owner_id == employee_id:
                attachment.display_order = index

    return api_success(message='순서가 변경되었습니다.')
```

**Attachment 모델 수정**:
```python
# display_order 필드 추가
display_order = db.Column(db.Integer, default=0)
```

**마이그레이션**:
```bash
alembic revision --autogenerate -m "add display_order to attachment"
alembic upgrade head
```

### 5.2 Phase 06b: file-panel.js (0.2일)

**우측 패널 UI** (`js/domains/employee/components/file-panel.js`):
```javascript
class FilePanel {
    constructor(panelElement, options) {
        this.panel = panelElement;
        this.employeeId = panelElement.dataset.employeeId;
        this.options = {
            uploadUrl: `/api/employees/${this.employeeId}/attachments`,
            deleteUrl: '/api/attachments',
            categories: ['required', 'optional', 'etc']
        };
    }

    async loadFiles() {
        const response = await fetch(this.options.uploadUrl);
        const files = await response.json();
        this._renderFileList(files);
    }

    async uploadFile(file, category) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', category);

        const response = await fetch(this.options.uploadUrl, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            Toast.success('파일이 업로드되었습니다.');
            this.loadFiles();
        }
    }

    async deleteFile(fileId) {
        if (!confirm('파일을 삭제하시겠습니까?')) return;

        const response = await fetch(`${this.options.deleteUrl}/${fileId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            Toast.success('파일이 삭제되었습니다.');
            this.loadFiles();
        }
    }

    _renderFileList(files) { }
    _setupDropZone() { }
    _setupDragOrder() { }  // drag-order-manager 연동
}
```

### 5.3 Phase 07: 관계형 테이블 순서 변경 API (0.3일)

**API 엔드포인트** (학력/경력/자격증):
| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/employees/<id>/educations/order` | PATCH | 학력 순서 |
| `/api/employees/<id>/careers/order` | PATCH | 경력 순서 |
| `/api/employees/<id>/certificates/order` | PATCH | 자격증 순서 |

**요청 형식**:
```json
{
  "order": [3, 1, 2]  // 새 순서의 ID 배열
}
```

**구현** (mutation_routes.py에 추가):
```python
@bp.route('/api/employees/<int:id>/educations/order', methods=['PATCH'])
@corporate_login_required
def update_education_order(id):
    """학력 순서 변경"""
    data = request.get_json()
    order = data.get('order', [])

    with atomic_transaction():
        for index, edu_id in enumerate(order):
            education = Education.query.get(edu_id)
            if education and education.employee_id == id:
                education.display_order = index

    return jsonify({'success': True})
```

### 5.4 Model 확장 (필요시)

```python
# Education, Career, Certificate 모델에 추가
display_order = db.Column(db.Integer, default=0)
```

**마이그레이션**:
```bash
alembic revision --autogenerate -m "add display_order to relation models"
alembic upgrade head
```

---

## 6. 의존성

| 항목 | 의존 대상 | 상태 |
|------|----------|------|
| Phase 06a | Attachment 모델 | 진행가능 |
| Phase 06b | Phase 02 (drag-order-manager) | 진행중 |
| Phase 07 | Phase 02 (drag-order-manager) | 진행중 |

**참고**: 메인 영역의 `drag-order-manager.js` 완료 후 진행 권장

---

## 7. 실행 순서

```
[Phase 06a - 메인 영역과 병렬 진행 가능]

Day 0.1:
  [순서 API 추가] Phase 06a (0.1일)
  - Attachment 모델에 display_order 필드 추가
  - files.py에 attachments/order API 추가
  - DB 마이그레이션

[메인 영역 Phase 02 완료 후]

Day 0.2:
  [file-panel.js] Phase 06b (0.2일)
  - FilePanel 클래스 구현
  - 파일 목록 렌더링
  - 업로드/삭제 연동
  - drag-order-manager 연동

Day 0.3:
  [순서 변경 API] Phase 07 (0.3일)
  - educations/order API
  - careers/order API
  - certificates/order API

Day 0.5:
  통합 테스트
```

---

## 8. 테스트 체크리스트

### 8.1 File Panel
- [ ] 파일 목록 렌더링
- [ ] 파일 업로드 (드래그 앤 드롭)
- [ ] 파일 업로드 (클릭 선택)
- [ ] 파일 삭제 확인 모달
- [ ] 카테고리별 파일 분류 (필수/선택/기타)

### 8.2 Drag Order
- [ ] 드래그 핸들 표시
- [ ] 드래그 앤 드롭 순서 변경
- [ ] 순서 변경 API 호출
- [ ] 페이지 새로고침 후 순서 유지

### 8.3 계정 타입별 동작
- [ ] Corporate: 전체 파일 관리
- [ ] Personal: 본인 파일만
- [ ] Employee Sub: 읽기 전용

---

## 9. 파일 목록

### 9.1 생성할 파일
| 파일 | 경로 |
|------|------|
| file-panel.js | `js/domains/employee/components/` |

### 9.2 수정할 파일
| 파일 | 수정 내용 |
|------|----------|
| files.py | 첨부파일 순서 변경 API 추가 |
| mutation_routes.py | 학력/경력/자격증 순서 변경 API 추가 |
| Attachment 모델 | display_order 필드 추가 |
| Education 모델 | display_order 필드 추가 |
| Career 모델 | display_order 필드 추가 |
| Certificate 모델 | display_order 필드 추가 |

---

## 10. 우선순위 고려사항

### 10.1 독립 실행 가능 여부
- **Phase 06a**: 독립 실행 가능 (모델 수정, API 추가)
- **Phase 06b, 07**: `drag-order-manager.js` 완료 후

### 10.2 빠른 완료 전략
- Phase 06a는 메인 영역과 **병렬 진행 가능**
- Phase 06b, 07은 Phase 02 완료 직후 착수

### 10.3 병렬 진행 옵션
- Phase 06a (순서 API) - 메인 영역과 병렬 진행 가능
- Phase 07 (관계형 테이블 순서) - 메인 영역과 병렬 진행 가능
- Phase 06b (file-panel.js) - drag-order-manager 완료 후 진행

---

## 11. 변경 이력

| 일자 | 내용 |
|------|------|
| 2026-01-11 | 최초 작성 |
| 2026-01-11 | 프론트엔드/백엔드 구조 분석 결과 반영 - Phase 06a 추가, 예상 기간 수정 (0.8일→1.1일) |
