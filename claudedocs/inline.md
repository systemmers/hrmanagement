# 인라인 편집 시스템 전환 - 구현 워크플로우
C:\Users\sangj\.claude\plans\cozy-gliding-beaver.md
> **Updated**: 2026-01-14 | **Mode**: Safe Mode + 5-Point Check
> **Status**: Phase 0 완료 (95%), Phase 1 진행중

## 1. 현재 진행 상황 요약

### 완료된 항목 (Phase 0)

| 파일 | 상태 | 라인 수 | 비고 |
|------|------|---------|------|
| `inline-edit-manager.js` | **완료** | 1,009줄 | 상태 머신, 싱글톤 패턴 |
| `inline-edit.css` | **완료** | 452줄 | BEM, 섹션 모드 |
| `section_api.py` | **완료** | 560줄 | REST API (8정적+14동적) |
| `_inline_edit.html` | **완료** | 150+줄 | 15개 듀얼모드 매크로 |
| `_basic_info.html` | **완료** | 68개 필드 | 인라인 매크로 적용 |

### 구현된 핵심 기능

```
InlineEditManager.js:
├── 상태: VIEW → EDITING → SAVING → VIEW/ERROR
├── 이벤트: click, input, change, keydown (이벤트 위임)
├── 저장: dirty 필드만 PATCH 전송
├── RRN 자동입력: 주민번호 → 생년월일/성별/나이
├── 주소 자동복사: 주민등록상 → 실제 거주지
└── 권한: employee_sub(본인), corporate(admin/manager)
```

### 페이지 통합 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│              공유 파셜 (인라인 편집 자동 적용)                        │
├─────────────────────────────────────────────────────────────────────┤
│  _basic_info.html, _history_info.html, _hr_records.html            │
└─────────────────────────────────────────────────────────────────────┘
              │               │               │
              ▼               ▼               ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
│ profile/       │ │ mypage/        │ │ personal/        │
│ detail.html    │ │ company_info   │ │ company_card_    │
│ (편집 가능)    │ │ (조회 전용)    │ │ detail.html      │
│                │ │                │ │ (조회 전용)      │
└────────────────┘ └────────────────┘ └──────────────────┘
```

---

## 2. 남은 작업 (Phase 1+)

### Phase 1: 통합 테스트 및 브라우저 검증

**목표**: Phase 0 인프라 기능 검증

| Task | 검증 항목 | 방법 |
|------|----------|------|
| T1.1 | 편집 모드 전환 | Playwright - 버튼 클릭 → CSS 클래스 확인 |
| T1.2 | 필드 저장 | Network 탭 - PATCH 요청 확인 |
| T1.3 | RRN 자동입력 | 주민번호 13자리 입력 → 생년월일/성별/나이 검증 |
| T1.4 | 주소 자동복사 | 편집 모드 진입 시 자동 복사 확인 |
| T1.5 | 권한 제어 | employee_sub 계정으로 접근 테스트 |

### Phase 2-7: 나머지 정적 섹션

| Phase | 섹션 | 파일 | 특이사항 |
|-------|------|------|----------|
| 2 | 소속정보 | _basic_info.html (organization 섹션) | 조직 트리 선택기 |
| 3 | 계약정보 | _basic_info.html (contract 섹션) | 읽기전용 필드 혼합 |
| 4 | 급여정보 | _basic_info.html (salary 섹션) | 금액 포맷팅 |
| 5 | 복리후생 | _basic_info.html (benefit 섹션) | 단순 필드 |
| 6 | 병역정보 | _history_info.html (military 섹션) | 조건부 필드 |
| 7 | 계정정보 | _account_info.html | 보안 필드 |

### Phase 8-13: 동적 테이블 (이력 정보)

| Phase | 섹션 | API 엔드포인트 | CRUD |
|-------|------|---------------|------|
| 8 | 가족정보 | `/api/employees/{id}/families` | 완료 |
| 9 | 학력정보 | `/api/employees/{id}/educations` | 완료 |
| 10 | 경력정보 | `/api/employees/{id}/careers` | 완료 |
| 11 | 자격증 | `/api/employees/{id}/certificates` | 완료 |
| 12 | 언어능력 | `/api/employees/{id}/languages` | 완료 |
| 13 | 수상내역 | `/api/employees/{id}/awards` | 완료 |

### Phase 14-22: HR 릴레이션

| Phase | 섹션 | 첨부파일 | 상태 |
|-------|------|---------|------|
| 14 | 근로계약 이력 | O | 모델 결정 필요 |
| 15 | 연봉계약 이력 | O | API 완료 |
| 16 | 급여 지급 이력 | O | API 완료 |
| 17 | 인사이동/승진 | O | API 완료 |
| 18 | 인사고과 | X | API 완료 |
| 19 | 교육훈련 | O | API 완료 |
| 20 | HR 프로젝트 | X | API 완료 |
| 21 | 비품지급 | X | API 완료 |
| 22 | 근태현황 | X | 정적 섹션 |

---

## 3. Safe Mode 검증 체크리스트

### 구현 순서

| Phase | 섹션 | 복잡도 | 특이사항 |
|-------|------|--------|----------|
| 1 | 개인 기본정보 | 중 | 주민번호 자동계산, 주소검색 |
| 2 | 소속정보 | 낮 | 조직 트리 선택기 |
| 3 | 계약정보 | 중 | 읽기전용 필드 혼합 |
| 4 | 급여정보 | 중 | 금액 포맷팅 |
| 5 | 복리후생 | 낮 | 단순 필드 |
| 6 | 병역정보 | 낮 | 조건부 필드 |
| 7 | 계정정보 | 낮 | 보안 필드 |

### 수정 대상 파일

```
templates/domains/employee/partials/detail/
├── _basic_info.html      # 듀얼 모드 매크로 적용
├── _organization_info.html
├── _contract_info.html
├── _salary_info.html
├── _benefit_info.html
├── _military_info.html
└── _account_info.html

static/js/domains/employee/pages/
└── detail.js             # InlineEditManager 통합
```

### HTML 구조 변경

**Before (읽기 전용)**
```html
<td class="info-table__value">홍길동</td>
```

**After (듀얼 모드)**
```html
<td class="info-table__value" data-field="name">
    <span class="inline-edit__view">홍길동</span>
    <div class="inline-edit__edit">
        <input type="text" name="name" value="홍길동">
    </div>
</td>
```

---

## Phase 8-9+: 동적 섹션 (10일)

### 대상 섹션

#### 이력 정보 (기존)

| Phase | 섹션 | 복잡도 | API 엔드포인트 |
|-------|------|--------|---------------|
| 8 | 가족정보 | 높 | `/api/employees/{id}/families/{item_id}` |
| 9 | 학력정보 | 높 | `/api/employees/{id}/educations/{item_id}` |
| 10 | 경력정보 | 높 | `/api/employees/{id}/careers/{item_id}` |
| 11 | 자격증 | 높 | `/api/employees/{id}/certificates/{item_id}` |
| 12 | 언어능력 | 중 | `/api/employees/{id}/languages/{item_id}` |
| 13 | 수상내역 | 중 | `/api/employees/{id}/awards/{item_id}` |

#### 인사관리 릴레이션 (추가)

| Phase | 섹션 | 복잡도 | API 엔드포인트 | 첨부파일 | 모델 |
|-------|------|--------|---------------|---------|------|
| 14 | 근로계약 이력 | 높 | `/api/employees/{id}/employment-contracts/{item_id}` | O | Contract (기존) |
| 15 | 연봉계약 이력 | 중 | `/api/employees/{id}/salary-histories/{item_id}` | O | SalaryHistory |
| 16 | 급여 지급 이력 | 높 | `/api/employees/{id}/salary-payments/{item_id}` | O | SalaryPayment |
| 17 | 인사이동/승진 | 중 | `/api/employees/{id}/promotions/{item_id}` | O | Promotion |
| 18 | 인사고과 | 중 | `/api/employees/{id}/evaluations/{item_id}` | X | Evaluation |
| 19 | 교육훈련 | 중 | `/api/employees/{id}/trainings/{item_id}` | O | Training |
| 20 | HR 프로젝트 | 중 | `/api/employees/{id}/hr-projects/{item_id}` | X | HrProject |
| 21 | 비품지급 | 낮 | `/api/employees/{id}/assets/{item_id}` | X | Asset |
| 22 | 근태현황 | 낮 | `/api/employees/{id}/attendance` | X | Attendance (정적) |

**HR 릴레이션 현황 분석 (2026-01-14):**

| 항목 | 현재 상태 | 필요 작업 |
|------|----------|----------|
| Repository | 모두 존재 (employee_relation_service.py) | - |
| 조회 메서드 | get_*_list() 모두 존재 | - |
| 수정 메서드 | 미존재 | update_*(), get_*_by_id() 추가 |
| 모델 | DictSerializableMixin 적용 완료 | - |
| 템플릿 | _hr_records.html (8개 테이블) | data-field 속성 추가 |

**Phase 14 특이사항 (근로계약 이력):**
- 현재 템플릿: employee.hire_date 하드코딩 표시
- Contract 모델 활용 또는 신규 EmploymentContract 모델 생성 필요
- 계약구분, 계약기간, 직원구분, 근무형태 필드 추가 검토

### API 설계

```yaml
Collection (목록):
  GET    /api/employees/{id}/{section}      # 목록 조회
  POST   /api/employees/{id}/{section}      # 항목 추가

Resource (개별):
  GET    /api/employees/{id}/{section}/{item_id}    # 단건 조회
  PATCH  /api/employees/{id}/{section}/{item_id}    # 부분 수정
  DELETE /api/employees/{id}/{section}/{item_id}    # 삭제

Bulk:
  PATCH  /api/employees/{id}/{section}/order        # 순서 변경
```

### 서비스 레이어 확장

**권장 구조**: `employee_relation_service.py` 확장 (이미 HR 릴레이션 Repository 속성 보유)

```python
# employee_relation_service.py 확장 (HR 릴레이션)
# 기존 Repository 속성 활용: salary_history_repo, promotion_repo, evaluation_repo,
#                          training_repo, asset_repo, salary_payment_repo, hr_project_repo

# ========================================
# 개별 항목 조회 (PATCH API용)
# ========================================

def get_salary_history_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """연봉계약 이력 단건 조회"""
    model = self.salary_history_repo.find_by_id(item_id)
    if model and model.employee_id == employee_id:
        return model.to_dict()
    return None

def get_promotion_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """인사이동/승진 단건 조회"""

def get_evaluation_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """인사고과 단건 조회"""

def get_training_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """교육훈련 단건 조회"""

def get_hr_project_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """HR프로젝트 단건 조회"""

def get_asset_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """비품지급 단건 조회"""

def get_salary_payment_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
    """급여지급 단건 조회"""

# ========================================
# 개별 항목 수정 (PATCH API용)
# ========================================

def update_salary_history(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """연봉계약 이력 수정"""
    model = self.salary_history_repo.find_by_id(item_id)
    if not model or model.employee_id != employee_id:
        return False, "항목을 찾을 수 없습니다."
    for key, value in data.items():
        if hasattr(model, key):
            setattr(model, key, value)
    if commit:
        db.session.commit()
    return True, None

def update_promotion(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """인사이동/승진 수정"""

def update_evaluation(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """인사고과 수정"""

def update_training(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """교육훈련 수정"""

def update_hr_project(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """HR프로젝트 수정"""

def update_asset(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """비품지급 수정"""

def update_salary_payment(self, item_id: int, data: Dict, employee_id: int, commit=True) -> Tuple[bool, Optional[str]]:
    """급여지급 수정"""

# ========================================
# 개별 항목 생성 (POST API용)
# ========================================

def create_salary_history(self, employee_id: int, data: Dict, commit=True) -> Dict:
    """연봉계약 이력 생성"""
    data['employee_id'] = employee_id
    model = SalaryHistory(**data)
    return self.salary_history_repo.create(model, commit=commit).to_dict()

# ... 다른 create_* 메서드들 ...

# ========================================
# 개별 항목 삭제 (DELETE API용)
# ========================================

def delete_salary_history(self, item_id: int, employee_id: int, commit=True) -> bool:
    """연봉계약 이력 삭제"""
    model = self.salary_history_repo.find_by_id(item_id)
    if not model or model.employee_id != employee_id:
        return False
    return self.salary_history_repo.delete(item_id, commit=commit)

# ... 다른 delete_* 메서드들 ...
```

**profile_relation_service.py 확장 (이력 정보)**
```python
# Phase 8-13용 (가족/학력/경력/자격증/언어/수상)
# 기존 generic_relation_crud.py 패턴 확장

def get_education_by_id(self, edu_id, employee_id, owner_type):
    """개별 학력 항목 조회"""
    return self._education.get_by_id(edu_id, employee_id, owner_type)

def update_education_item(self, edu_id, data, employee_id, owner_type, commit=True):
    """개별 학력 항목 수정 (PATCH용)"""
    return self._education.update_item(edu_id, data, employee_id, owner_type, commit)
```

---

## 권한 및 보안

### 접근 제어

| 계정 타입 | 권한 |
|----------|------|
| employee_sub | 본인 데이터만 CRUD |
| corporate (manager/admin) | 자사 직원 CRUD |
| personal | employee 엔드포인트 접근 불가 |

### 개인계약 연동 보호

```python
# 개인계약 연동 직원의 이력 정보는 법인에서 수정 불가
PROTECTED_SECTIONS = ['educations', 'careers', 'certificates', 'languages', 'families', 'awards']

def _is_section_protected(employee_id, section):
    if section not in PROTECTED_SECTIONS:
        return False
    return user_employee_link_service.has_approved_personal_contract(employee_id, company_id)
```

---

## 에러 처리

### HTTP 상태 코드

| 코드 | 용도 |
|------|------|
| 200 | 조회/수정 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 403 | 권한 없음 (개인계약 보호 포함) |
| 404 | 리소스 없음 |
| 422 | 유효성 검사 실패 |
| 500 | 서버 오류 |

### 에러 응답 포맷

```json
{
    "success": false,
    "error": "유효성 검사 실패",
    "errors": {
        "school_name": "학교명은 필수입니다.",
        "graduation_date": "올바른 날짜 형식이 아닙니다."
    }
}
```

---

## CSS 확장

### 추가 스타일 (inline-edit.css)

```css
/* 섹션 편집 모드 */
.info-section--editing .inline-edit__view { display: none; }
.info-section--editing .inline-edit__edit { display: flex; }

/* 저장 중 상태 */
.info-section--saving { opacity: 0.7; pointer-events: none; }

/* 더티 필드 */
.inline-edit__input--dirty { border-color: var(--color-warning-400); }

/* 에러 필드 */
.inline-edit__input--invalid { border-color: var(--color-error-500); }
```

---

## 구현 일정

| Phase | 기간 | 내용 |
|-------|------|------|
| 0 | 2일 | 인프라 (매니저, 매크로, API 기반) |
| 1 | 1일 | 개인 기본정보 |
| 2-7 | 4일 | 소속/계약/급여/복리후생/병역/계정 |
| 8-13 | 4일 | 가족/학력/경력/자격증/언어/수상 (이력 정보) |
| 14-21 | 5일 | HR 릴레이션 (근로계약/연봉/급여지급/인사이동/고과/교육/프로젝트/비품) |
| 최종 | 1일 | 기존 폼 페이지 제거, 통합 테스트 |

**총 예상: 17일**

---

## 검증 방법

### 기능 테스트

1. **모드 전환**: 수정 버튼 → 편집 모드 → 저장/취소 → 읽기 모드
2. **API 통신**: PATCH 요청 → 성공 응답 → UI 반영
3. **에러 처리**: 유효성 실패 → 인라인 에러 표시 → Toast
4. **권한 검사**: 개인계약 연동 직원 → 보호 필드 수정 불가
5. **동적 섹션**: 항목 추가/수정/삭제/순서 변경

### 회귀 테스트

- 직원 목록 페이지 정상 동작
- 상세 페이지 읽기 모드 정상
- 파일 업로드/첨부 기능
- 명함 카드 표시
- 섹션 네비게이션

---

## 주요 파일 목록

### 수정 대상

| 파일 | 변경 내용 |
|------|----------|
| `detail.js` | InlineEditManager 통합 |
| `partials/detail/*.html` (7개) | 듀얼 모드 매크로 적용 |
| `inline-edit.css` | 추가 상태 클래스 |
| `profile_relation_service.py` | update_*, get_*_by_id 메서드 추가 |
| `generic_relation_crud.py` | update(), get_by_id() 메서드 추가 |
| `blueprints/__init__.py` | section_api Blueprint 등록 |

### 신규 생성

| 파일 | 역할 |
|------|------|
| `inline-edit-manager.js` | 인라인 편집 상태 관리 |
| `_inline_edit.html` | 듀얼 모드 Jinja2 매크로 |
| `section_api.py` | 섹션별 PATCH API |
| `inline_edit_service.py` | 인라인 편집 서비스 |
| `validation_service.py` | 유효성 검사 서비스 |

### 삭제 대상 (구현 완료 후)

```
templates/domains/employee/partials/form/   # 16개 파일
static/js/domains/employee/pages/form.js    # 폼 전용 JS
```

---

## 구현 워크플로우 체크리스트

> **Safe Mode 활성화** - 모든 작업에 대해 5가지 검증 항목 적용
> - DEPENDENCY: 의존성 검증
> - RULES: 프로젝트 규칙 준수
> - TEST: 테스트 가능성 확인
> - LEGACY: 레거시 코드 호환성
> - PATTERN: 기존 패턴 일관성

---

### Phase 0 체크리스트: 인프라 구축

#### 0.1 InlineEditManager.js 생성 - **완료**

**파일 위치**: `app/static/js/shared/components/inline-edit-manager.js` (1,009줄)

| 검증 항목 | 체크 | 상세 내용 |
|----------|------|----------|
| DEPENDENCY | [x] | Toast, api.js, inline-edit.css 존재 확인 |
| RULES | [x] | ES6 모듈, BEM 클래스, 이벤트 위임 |
| TEST | [ ] | 상태 전환, API 호출, 롤백 테스트 가능 |
| LEGACY | [x] | SECTION_CONFIG, TABLE_CONFIG 재사용 |
| PATTERN | [x] | 상태 머신, 싱글톤 패턴 적용 |

- [x] **의존성 체크**
  - [x] `Toast` (shared/components/toast.js) - 이미 detail.js에서 사용 중
  - [x] `api.js` (shared/utils/api.js) - 이미 존재
  - [x] 기존 `inline-edit.css` 클래스 활용 (.inline-edit--active, --loading, --error, --success)
- [x] **규칙 체크**
  - [x] ES6 모듈 export 패턴 준수 (class export)
  - [x] BEM 클래스명 사용
  - [x] 이벤트 위임 패턴 사용 (detail.js 패턴 참조)
- [x] **레거시 체크**
  - [x] `SECTION_CONFIG` (detail.js:241-267) - 섹션별 버튼 설정 재사용
  - [x] `TABLE_CONFIG` (detail.js:269-286) - 테이블별 설정 재사용
  - [x] `handleSectionEdit()`, `handleSectionAdd()` 핸들러 확장
- [x] **패턴 체크**
  - [x] 상태 머신 패턴 (VIEW → EDITING → SAVING → VIEW/ERROR)
  - [x] 이벤트 콜백 패턴
  - [x] 싱글톤 인스턴스 (getInlineEditManager() 팩토리)
- [ ] **테스트 체크** (Phase 1에서 수행)
  - [ ] 단위 테스트: 상태 전환 로직
  - [ ] 통합 테스트: API 호출 및 응답 처리
  - [ ] E2E 테스트: 브라우저에서 편집 모드 전환

#### 0.2 inline-edit.css 확장 - **완료**

**파일 위치**: `app/static/css/shared/components/inline-edit.css` (452줄)

| 검증 항목 | 체크 | 상세 내용 |
|----------|------|----------|
| DEPENDENCY | [x] | variables.css CSS 변수 존재 |
| RULES | [x] | BEM 네이밍, CSS 변수 사용 |
| TEST | [ ] | 각 상태 클래스 시각적 검증 |
| LEGACY | [x] | 기존 .inline-edit 클래스 확장 |
| PATTERN | [x] | BEM modifier 패턴 |

- [x] **의존성 체크**
  - [x] CSS 변수 (variables.css) - 이미 사용 중
  - [x] 기존 클래스 (.inline-edit, .inline-edit__view, .inline-edit__edit)
- [x] **규칙 체크**
  - [x] BEM 네이밍 준수
  - [x] CSS 변수 사용 (하드코딩 색상 금지)
- [x] **추가 스타일**
  - [x] `.info-section--editing` (섹션 편집 모드)
  - [x] `.info-section--saving` (저장 중)
  - [x] `.inline-edit__input--dirty` (변경된 필드)
  - [x] `.inline-edit__input--invalid` (에러 필드)
  - [x] `.inline-edit--address` (주소 검색 필드)
  - [x] `.inline-edit--date-lunar` (날짜+음력 필드)
  - [x] `.inline-edit--organization` (조직 트리 선택기)
- [ ] **테스트 체크** (Phase 1에서 수행)
  - [ ] 스타일가이드에서 각 상태 시각 확인
  - [ ] 반응형 레이아웃 확인

#### 0.3 _inline_edit.html 매크로 생성 - **완료**

**파일 위치**: `app/templates/shared/macros/_inline_edit.html` (150+줄)

| 검증 항목 | 체크 | 상세 내용 |
|----------|------|----------|
| DEPENDENCY | [x] | _info_display.html, FieldOptions 존재 |
| RULES | [x] | Jinja2 매크로 네이밍, _ 접두사 |
| TEST | [ ] | 각 필드 타입별 렌더링 확인 |
| LEGACY | [x] | info_table_row 패턴 참조 |
| PATTERN | [x] | 듀얼 모드 구조 |

- [x] **의존성 체크**
  - [x] `_info_display.html` - info_table_row 매크로 참조
  - [x] `FieldOptions` - 옵션 렌더링
- [x] **규칙 체크**
  - [x] Jinja2 매크로 네이밍 (`inline_field`, `inline_select`, `inline_row` 등)
  - [x] `_` 접두사 (부분 템플릿)
- [x] **패턴 체크**
  - [x] 듀얼 모드 구조 (view + edit)
  - [x] data-field 속성 필수
  - [x] data-original 속성 (롤백용)
- [x] **구현된 매크로 (15개)**
  - [x] `inline_text_field` - 텍스트 필드
  - [x] `inline_select_field` - 셀렉트 필드
  - [x] `inline_date_field` - 날짜 필드
  - [x] `inline_date_lunar_field` - 날짜+음력 필드
  - [x] `inline_number_field` - 숫자 필드
  - [x] `inline_number_suffix_field` - 숫자+단위 필드
  - [x] `inline_rrn_field` - 주민번호 필드 (마스킹)
  - [x] `inline_address_field` - 주소 검색 필드
  - [x] `inline_organization_field` - 조직 트리 선택기
  - [x] `inline_phone_field` - 전화번호 필드
  - [x] `inline_email_field` - 이메일 필드
  - [x] `inline_readonly_field` - 읽기전용 필드
  - [x] `inline_badge_field` - 배지 표시 필드
  - [x] `inline_link_field` - 링크 필드
  - [x] `inline_custom_field` - 커스텀 필드
- [ ] **테스트 체크** (Phase 1에서 수행)
  - [ ] text, select, date, number 필드 타입 검증
  - [ ] 읽기전용 필드 렌더링 확인

#### 0.4 section_api.py 생성 - **완료**

**파일 위치**: `app/domains/employee/blueprints/section_api.py` (560줄)

| 검증 항목 | 체크 | 상세 내용 |
|----------|------|----------|
| DEPENDENCY | [x] | employee_service, decorators.py, atomic_transaction |
| RULES | [x] | Blueprint 네이밍, HTTP 상태 코드 |
| TEST | [ ] | PATCH/POST/DELETE API 테스트 |
| LEGACY | [x] | files.py, mutation_routes.py 패턴 참조 |
| PATTERN | [x] | RESTful API, JSON 응답 |

- [x] **의존성 체크**
  - [x] `employee_service` Facade 패턴
  - [x] `decorators.py` - @api_login_required, @corporate_login_required
  - [x] `atomic_transaction()` - 트랜잭션 관리
- [x] **규칙 체크**
  - [x] Blueprint 이름: `employee_section_api_bp`
  - [x] URL prefix: `/api/employees`
  - [x] HTTP 상태 코드 준수 (200, 400, 403, 404, 422)
- [x] **레거시 체크**
  - [x] `files.py` API 패턴 참조
  - [x] `mutation_routes.py` 권한 검사 패턴 참조
- [x] **보안 체크**
  - [x] 개인계약 연동 보호 (PROTECTED_SECTIONS)
  - [x] 테넌트 격리 (company_id 검증)
- [x] **구현된 API 엔드포인트**
  - [x] **정적 섹션 (8개)**: basic, organization, contract, salary, benefit, insurance, military, account
  - [x] **동적 섹션 (14개)**: families, educations, careers, certificates, languages, awards, employment-contracts, salary-histories, salary-payments, promotions, evaluations, trainings, hr-projects, assets
- [ ] **테스트 체크** (Phase 1에서 수행)
  - [ ] 정적 섹션 PATCH 테스트
  - [ ] 동적 섹션 CRUD 테스트
  - [ ] 권한 거부 시 403 응답 확인
  - [ ] 유효성 실패 시 422 응답 확인

#### 0.5 inline_edit_service.py - **미생성 (section_api.py에 통합)**

> **참고**: 별도 서비스 파일 대신 `section_api.py`에서 기존 서비스들을 직접 호출하는 방식으로 구현됨
> - `employee_core_service` - 기본 정보 업데이트
> - `employee_relation_service` - HR 릴레이션 업데이트
> - `profile_relation_service` - 이력 정보 업데이트 (SSOT)

#### 0.6 validation_service.py - **미생성 (기존 검증 패턴 활용)**

> **참고**: 별도 검증 서비스 대신 기존 검증 패턴 활용
> - `profile_validator.py` - 프로필 검증 (기존)
> - section_api.py 내 인라인 검증 로직

---

### Phase 0 완료 검증 체크리스트

| 파일 | 상태 | 라인 수 | 검증 항목 |
|------|------|---------|----------|
| inline-edit-manager.js | **완료** | 1,009줄 | 상태 전환, API 호출, RRN 자동입력, 주소 복사 |
| inline-edit.css | **완료** | 452줄 | BEM 스타일 클래스, 섹션 모드, 특수 필드 |
| _inline_edit.html | **완료** | 150+줄 | 15개 듀얼모드 매크로 |
| section_api.py | **완료** | 560줄 | 8정적 + 14동적 API 엔드포인트 |
| _basic_info.html | **완료** | 68개 필드 | 인라인 매크로 적용 |
| blueprints/__init__.py | **완료** | - | Blueprint 등록 |

**Phase 0 완료 기준 (95% 달성):**
- [x] 핵심 4개 파일 생성/수정 완료
- [x] detail.js에서 InlineEditManager import 가능
- [x] `/api/employees/{id}/sections/basic` PATCH API 엔드포인트 구현
- [ ] **남은 작업**: 브라우저 통합 테스트 (Phase 1)

---

### Phase 1-7 체크리스트: 정적 섹션

#### 공통 체크리스트
- [ ] **템플릿 변경**
  - [ ] `_inline_edit.html` 매크로 import
  - [ ] `info_table_row` → `inline_row` 매크로 교체
  - [ ] 섹션 헤더에 `data-section` 속성 추가
  - [ ] 저장/취소 버튼 추가
- [ ] **테스트 체크**
  - [ ] 읽기 모드 정상 표시
  - [ ] 편집 모드 전환
  - [ ] 저장 API 호출
  - [ ] 취소 시 롤백
  - [ ] 에러 표시

#### Phase 1: 개인 기본정보 (_basic_info.html)
- [ ] **특수 필드 처리**
  - [ ] 주민번호 - 마스킹/언마스킹
  - [ ] 생년월일 - 음력 배지 처리
  - [ ] 주소 - 주소검색 API 연동

#### Phase 2-7: 나머지 정적 섹션
- [ ] Phase 2: 소속정보 - 조직 트리 선택기
- [ ] Phase 3: 계약정보 - 읽기전용 필드 혼합
- [ ] Phase 4: 급여정보 - 금액 포맷팅
- [ ] Phase 5: 복리후생 - 단순 필드
- [ ] Phase 6: 병역정보 - 조건부 필드
- [ ] Phase 7: 계정정보 - 보안 필드

---

### Phase 8-21 체크리스트: 동적 섹션

#### 공통 체크리스트 (테이블 섹션)
- [ ] **CRUD API**
  - [ ] GET - 목록 조회
  - [ ] POST - 항목 추가
  - [ ] PATCH - 부분 수정
  - [ ] DELETE - 삭제
- [ ] **UI 컴포넌트**
  - [ ] 행 편집 모달 또는 인라인 폼
  - [ ] 드래그 앤 드롭 순서 변경
  - [ ] 첨부파일 연동 (hasAttach=true 섹션)
- [ ] **서비스 레이어**
  - [ ] `get_{section}_by_id()` 메서드 추가
  - [ ] `update_{section}()` PATCH 메서드 추가

#### Phase 8-13: 이력 정보 (profile_relation_service 확장)
- [ ] 가족정보, 학력정보, 경력정보, 자격증, 언어능력, 수상내역

#### Phase 14-21: HR 릴레이션 (employee_relation_service 확장)

**Phase 14: 근로계약 이력 (employment-contract-table)**
- [ ] **모델 검토**: Contract 모델 확장 또는 신규 EmploymentContract 모델
- [ ] **필드**: 계약일, 계약구분, 계약기간 시작/종료, 직원구분, 근무형태, 비고
- [ ] **서비스**: get_employment_contract_by_id(), update_employment_contract(), create_employment_contract(), delete_employment_contract()
- [ ] **첨부파일**: hasAttach=true - attachment 도메인 연동

**Phase 15: 연봉계약 이력 (salary-history-table)**
- [ ] **모델**: SalaryHistory (기존)
- [ ] **필드**: contract_year, annual_salary, bonus, total_amount, contract_period, note
- [ ] **서비스**: get_salary_history_by_id(), update_salary_history(), create_salary_history(), delete_salary_history()
- [ ] **첨부파일**: hasAttach=true

**Phase 16: 급여 지급 이력 (salary-payment-table)**
- [ ] **모델**: SalaryPayment (기존)
- [ ] **필드**: payment_date, payment_period, base_salary, allowances, gross_pay, insurance, income_tax, total_deduction, net_pay, note
- [ ] **서비스**: get_salary_payment_by_id(), update_salary_payment(), create_salary_payment(), delete_salary_payment()
- [ ] **첨부파일**: hasAttach=true

**Phase 17: 인사이동/승진 (promotion-table)**
- [ ] **모델**: Promotion (기존)
- [ ] **필드**: effective_date, promotion_type, from_department, to_department, from_position, to_position, job_role, reason, note
- [ ] **서비스**: get_promotion_by_id(), update_promotion(), create_promotion(), delete_promotion()
- [ ] **첨부파일**: hasAttach=true

**Phase 18: 인사고과 (evaluation-table)**
- [ ] **모델**: Evaluation (기존)
- [ ] **필드**: year, q1_grade, q2_grade, q3_grade, q4_grade, overall_grade, salary_negotiation, note
- [ ] **서비스**: get_evaluation_by_id(), update_evaluation(), create_evaluation(), delete_evaluation()
- [ ] **첨부파일**: hasAttach=false

**Phase 19: 교육훈련 (training-table)**
- [ ] **모델**: Training (기존)
- [ ] **필드**: training_date, training_name, institution, hours, completion_status, note
- [ ] **서비스**: get_training_by_id(), update_training(), create_training(), delete_training()
- [ ] **첨부파일**: hasAttach=true

**Phase 20: HR 프로젝트 (hr-project-table)**
- [ ] **모델**: HrProject (기존)
- [ ] **필드**: project_name, start_date, end_date, duration, duty, role, client
- [ ] **서비스**: get_hr_project_by_id(), update_hr_project(), create_hr_project(), delete_hr_project()
- [ ] **첨부파일**: hasAttach=false

**Phase 21: 비품지급 (asset-table)**
- [ ] **모델**: Asset (기존)
- [ ] **필드**: issue_date, item_name, model, serial_number, status, note
- [ ] **서비스**: get_asset_by_id(), update_asset(), create_asset(), delete_asset()
- [ ] **첨부파일**: hasAttach=false

**Phase 22: 근태현황 (정적 섹션)**
- [ ] **모델**: Attendance (기존) - 요약 정보
- [ ] **필드**: total_work_days, total_absent_days, total_late_count, total_early_leave, total_annual_used
- [ ] **처리 방식**: 정적 섹션 (info-table), 단일 API 호출

---

### 최종 체크리스트

#### 통합 테스트
- [ ] 모든 섹션 인라인 편집 동작
- [ ] 권한별 접근 제어 (corporate, employee_sub)
- [ ] 개인계약 연동 보호 필드
- [ ] 에러 처리 및 Toast 표시
- [ ] 네트워크 오류 복구

#### 회귀 테스트
- [ ] 직원 목록 페이지 정상
- [ ] 상세 페이지 읽기 모드 정상
- [ ] 파일 업로드/첨부 기능
- [ ] 명함 카드 표시
- [ ] 섹션 네비게이션

#### 정리 작업
- [ ] `templates/domains/employee/partials/form/` 삭제 (16개 파일)
- [ ] `static/js/domains/employee/pages/form.js` 삭제
- [ ] `edit.html` 라우트 제거
- [ ] 문서 업데이트 (CLAUDE.md)

---

## HR 릴레이션 계획 리뷰 (2026-01-14)

### 현재 구현 상태 분석

**템플릿 (_hr_records.html)**:
| 테이블 ID | 섹션명 | 첨부파일 | 현재 상태 |
|----------|--------|---------|----------|
| employment-contract-table | 근로계약 이력 | O | 하드코딩 (employee.hire_date) |
| salary-history-table | 연봉계약 이력 | O | salary_history_list 바인딩 |
| salary-payment-table | 급여 지급 이력 | O | salary_payment_list 바인딩 |
| promotion-table | 인사이동/승진 | O | promotion_list 바인딩 |
| evaluation-table | 인사고과 | X | evaluation_list 바인딩 |
| training-table | 교육훈련 | O | training_list 바인딩 |
| hr-project-table | 프로젝트 | X | hr_project_list 바인딩 |
| asset-table | 비품지급 | X | asset_list 바인딩 |

**서비스 레이어 (employee_relation_service.py)**:
| 기능 | 메서드 | 상태 |
|------|--------|------|
| Repository 속성 | salary_history_repo, promotion_repo 등 | 존재 |
| 목록 조회 | get_salary_history_list() 등 | 존재 |
| 단건 조회 | get_salary_history_by_id() | **누락** |
| 수정 | update_salary_history() | **누락** |
| 생성 | create_salary_history() | **누락** |
| 삭제 | delete_salary_history() | **누락** |

### 이슈 및 권장사항

**1. Phase 14 (근로계약 이력) - 높은 복잡도**
- **현재 문제**: 템플릿이 `employee.hire_date` 하드코딩 표시
- **선택지 A**: 기존 `Contract` 모델 확장 (contract_type 필드 추가)
- **선택지 B**: 신규 `EmploymentContract` 모델 생성
- **권장**: 선택지 B - 데이터 분리 및 이력 관리 용이

**2. 첨부파일 연동**
- 5개 섹션이 hasAttach=true (근로계약, 연봉계약, 급여지급, 인사이동, 교육훈련)
- `attachment_service` 연동 필요
- 행 편집 모달에 첨부파일 업로드 UI 포함 필요

**3. 서비스 레이어 구조**
- **원래 계획**: employee_service.py 확장
- **권장 변경**: employee_relation_service.py 확장 (이미 Repository 속성 보유)
- **이유**: 코드 응집도 향상, 기존 구조 활용

**4. API 엔드포인트 일관성**
- section_api.py에 통합 vs 개별 파일 분리
- **권장**: section_api.py에 통합 (RESTful 구조 유지)

**5. 드래그 앤 드롭 순서 변경**
- 모든 테이블에 `data-draggable="true"` 적용됨
- 순서 변경 API 필요: `PATCH /api/employees/{id}/{section}/order`
- 모델에 `order` 또는 `sort_order` 필드 추가 필요 (일부 모델만)

### 위험 요소

| 위험 | 영향도 | 대응 방안 |
|------|--------|----------|
| Phase 14 모델 결정 지연 | 높 | Phase 14 시작 전 모델 구조 확정 |
| 첨부파일 연동 복잡도 | 중 | attachment_service 패턴 재사용 |
| 기존 데이터 마이그레이션 | 중 | 빈 테이블이므로 영향 없음 |
| 드래그 순서 필드 추가 | 낮 | Alembic 마이그레이션으로 처리 |

### 수정된 일정

| Phase | 기간 | 내용 |
|-------|------|------|
| 0 | 2일 | 인프라 (매니저, 매크로, API 기반) |
| 1 | 1일 | 개인 기본정보 |
| 2-7 | 4일 | 소속/계약/급여/복리후생/병역/계정 |
| 8-13 | 4일 | 가족/학력/경력/자격증/언어/수상 (이력 정보) |
| 14 | 1일 | 근로계약 이력 (모델 결정 포함) |
| 15-21 | 4일 | 연봉/급여지급/인사이동/고과/교육/프로젝트/비품 |
| 22 | 0.5일 | 근태현황 (정적 섹션) |
| 최종 | 1일 | 기존 폼 페이지 제거, 통합 테스트 |

**총 예상: 17.5일** (기존 17일 + Phase 22 추가)






     ---


     
● 발견된 오류 이슈 유형 보고

  1. 필드 화이트리스트 누락 (H1)
  ┌────────────────────────┬─────────────────────────────────────────────────────────────────────────┬──────────────────────────┐
  │          위치          │                                  문제                                   │           해결           │
  ├────────────────────────┼─────────────────────────────────────────────────────────────────────────┼──────────────────────────┤
  │ inline_edit_service.py │ organization 섹션에 team, job_title, internal_phone, company_email 누락 │ 화이트리스트에 필드 추가 │
  └────────────────────────┴─────────────────────────────────────────────────────────────────────────┴──────────────────────────┘
  원인: 초기 구현 시 Employee 모델의 모든 필드를 화이트리스트에 포함하지 않음

  ---
  2. Relation 모델 업데이트 로직 누락 (H2)
  위치: inline_edit_service.py
  문제: Salary/Benefit 섹션이 Employee 필드만 업데이트, 관계 모델 미처리
  해결: _update_salary, _update_benefit 메서드에 relation 모델 업데이트 로직 추가
  원인: 정적 섹션 업데이트가 Employee 모델 필드만 고려하고, 1:1 관계 모델(Salary, Benefit)을 별도 처리하지 않음

  ---
  3. 템플릿-서비스 필드명 불일치 (H3)
  ┌──────────────────┬────────────────────────┬───────────────────────────────┐
  │       위치       │          문제          │             해결              │
  ├──────────────────┼────────────────────────┼───────────────────────────────┤
  │ _basic_info.html │ data-field="duty" 사용 │ data-field="job_title"로 수정 │
  └──────────────────┴────────────────────────┴───────────────────────────────┘
  원인: 템플릿에서 레거시 필드명(duty) 사용, 서비스는 모델 필드명(job_title) 기대

  ---
  4. 브라우저 테스트 중 발견된 이슈
  ┌───────────────┬─────────────────────────────────────────────────────────┬────────────────────────────────────┐
  │     유형      │                          문제                           │                상태                │
  ├───────────────┼─────────────────────────────────────────────────────────┼────────────────────────────────────┤
  │ CSRF 토큰     │ 직접 fetch() 호출 시 CSRF 토큰 누락으로 400 에러        │ 앱의 api.js 유틸리티 사용으로 해결 │
  ├───────────────┼─────────────────────────────────────────────────────────┼────────────────────────────────────┤
  │ HTTP 메서드   │ GET /api/employees/{id}/sections/{section} 미지원 (405) │ 설계상 PATCH만 지원, 정상          │
  ├───────────────┼─────────────────────────────────────────────────────────┼────────────────────────────────────┤
  │ 브라우저 캐시 │ 저장 후 페이지에 이전 값 표시                           │ 새로고침으로 해결, 정상 동작       │
  └───────────────┴─────────────────────────────────────────────────────────┴────────────────────────────────────┘
  ---
  이슈 유형 분류
  ┌──────────────────────┬──────┬────────┬───────────────────────────────────────────┐
  │         분류         │ 빈도 │ 심각도 │                 예방 방법                 │
  ├──────────────────────┼──────┼────────┼───────────────────────────────────────────┤
  │ 필드 동기화 누락     │ 높음 │ 높음   │ 모델 필드 추가 시 화이트리스트 체크리스트 │
  ├──────────────────────┼──────┼────────┼───────────────────────────────────────────┤
  │ Relation 모델 미처리 │ 중간 │ 높음   │ 1:1 관계 모델 업데이트 패턴 표준화        │
  ├──────────────────────┼──────┼────────┼───────────────────────────────────────────┤
  │ 템플릿-서비스 불일치 │ 중간 │ 중간   │ SSOT 필드명 레지스트리 활용               │
  └──────────────────────┴──────┴────────┴───────────────────────────────────────────┘
  ---
  다음 단계로 진행하겠습니다.