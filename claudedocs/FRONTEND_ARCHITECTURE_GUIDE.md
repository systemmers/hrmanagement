# Frontend Architecture Guide

프로젝트: HR Management System
통합일: 2025-12-23
소스: frontend_architecture_analysis.md, frontend_template_analysis.md, template_db_field_comparison.md

---

## 1. 아키텍처 개요

### 디렉토리 구조
```
app/static/
├── css/
│   ├── core/           # 핵심 시스템 (변수, 리셋, 테마, 유틸리티, 반응형)
│   ├── layouts/        # 레이아웃 컴포넌트 (헤더, 사이드바, 푸터)
│   ├── components/     # 재사용 컴포넌트 (버튼, 모달, 카드, 테이블)
│   └── pages/          # 페이지별 스타일
└── js/
    ├── utils/          # 유틸리티 (API, 포맷팅, DOM, 이벤트, 유효성검사)
    ├── components/     # 재사용 컴포넌트 (data-table/, salary/)
    ├── pages/          # 페이지별 스크립트 (employee/, profile/)
    └── services/       # 비즈니스 로직
```

### 품질 수준
| 항목 | 상태 | 비고 |
|------|------|------|
| 모듈화 | 양호 | Phase 7 리팩토링 완료 |
| 주석 일관성 | 우수 | CSS 91%, JS 100% 헤더 주석 |
| SoC | 양호 | 명확한 디렉토리 구조 |
| 중앙화 | 우수 | CSS 변수, 유틸리티 함수 체계적 관리 |

---

## 2. CSS 시스템

### 디자인 토큰 (variables.css)
```css
:root {
    /* 색상 팔레트 - 15단계 그레이 */
    --color-gray-25: #fcfcfc;
    --color-gray-900: #1a1a1a;

    /* 타이포그래피 - 11단계 */
    --text-2xs: 0.6875rem;  /* 11px */
    --text-6xl: 3rem;       /* 48px */

    /* 간격 - 15단계 */
    --space-0-5: 0.125rem;  /* 2px */
    --space-24: 6rem;       /* 96px */

    /* 모서리 - 7단계 */
    --radius-xs: 0.1875rem; /* 3px */
    --radius-full: 9999px;

    /* 그림자 - 6단계 */
    --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
    --shadow-2xl: 0 12px 40px rgba(0, 0, 0, 0.2);

    /* 전환 - 3단계 */
    --transition-fast: 120ms cubic-bezier(0.4, 0.0, 0.2, 1);
    --transition-slow: 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

### 테마 시스템 (theme.css)
```css
/* Corporate (기본) */
:root { --theme-primary: var(--color-blue-600); }

/* Personal 계정 (녹색) */
[data-account-type="personal"] { --theme-primary: #059669; }

/* Employee Sub 계정 (보라색) */
[data-account-type="employee_sub"] { --theme-primary: #7C3AED; }
```

---

## 3. JS 모듈 시스템

### Index 패턴 (중앙 진입점)
```javascript
// utils/index.js
export { formatNumber, formatDate } from './formatting.js';
export { $, $$, show, hide } from './dom.js';
export { debounce, throttle } from './events.js';
```

적용 사례:
- utils/index.js
- components/salary/index.js
- components/data-table/index.js
- pages/employee/index.js

### 하위 호환성 래퍼
```javascript
// components/data-table-advanced.js (래퍼)
/**
 * 하위 호환성 유지용. 새 코드에서는 './data-table/index.js' 사용
 */
export { DataTableAdvanced } from './data-table/index.js';
```

### 전역 네임스페이스 (권장 구조)
```javascript
window.HRApp = {
    version: '1.0.0',
    components: { DataTableAdvanced, TreeSelector },
    utils: { toast, filter, api },
    services: { employee, contract, organization }
};
```

---

## 4. 템플릿 구조

### 파셜 구조
```
partials/employee_detail/
├── _employee_header.html   # 변형: corporate, personal
├── _basic_info.html        # 섹션 1-7 (조건부 표시)
├── _history_info.html      # 섹션 8-14 (조건부 표시)
└── _hr_records.html        # 섹션 15-17 (인사카드 전용)
```

### page_mode 조건
| 섹션 | 조건 | 표시 |
|------|------|------|
| 소속정보 (2) | `page_mode == 'hr_card'` | 인사카드만 |
| 계약정보 (3) | `page_mode == 'hr_card'` | 인사카드만 |
| 급여정보 (4) | `page_mode == 'hr_card'` | 인사카드만 |
| 복리후생 (5) | `page_mode == 'hr_card'` | 인사카드만 |
| 4대보험 (6) | `page_mode == 'hr_card'` | 인사카드만 |
| 근로계약 (15-17) | `page_mode == 'hr_card'` | 인사카드만 |

### 헬퍼 함수 일람
| 함수명 | 용도 | 위치 |
|--------|------|------|
| `get_gender_label()` | 성별 라벨 | template_helpers.py |
| `get_marital_status_label()` | 결혼여부 라벨 | template_helpers.py |
| `get_employment_type_label()` | 근무형태 라벨 | template_helpers.py |
| `get_degree_label()` | 학력구분 라벨 | template_helpers.py |
| `get_relation_label()` | 가족 관계 라벨 | template_helpers.py |
| `get_level_label()` | 언어 수준 라벨 | template_helpers.py |
| `get_military_status_label()` | 병역구분 라벨 | template_helpers.py |
| `get_branch_label()` | 군별 라벨 | template_helpers.py |
| `calculate_tenure()` | 재직기간 계산 | template_helpers.py |
| `format_phone()` | 전화번호 포맷팅 | template_helpers.py |

---

## 5. 필드 매핑 이슈 (Template vs DB)

### 해결된 필드 매핑 (2025-12 검증)

| 템플릿 필드 | DB 컬럼 | 해결 방법 | 위치 |
|-------------|---------|----------|------|
| `employment_type` | `employee_type` | @property 별칭 | Employee 모델 |
| `transport_allowance` | `transportation_allowance` | __dict_aliases__ + @property | Salary 모델 |
| `pay_type` | `salary_type` | __dict_aliases__ + @property | Salary 모델 |
| `career_duties` | `job_description` | __dict_aliases__ + relation_updaters | Career 모델 |
| `resignation_date` | resignation_date | DB 컬럼 존재 | Employee 모델 |

### 해결된 필드 - DB 컬럼 추가 완료 (2025-12-23)

| 필드 | 파일 위치 | 조치 | 마이그레이션 |
|------|-----------|------|-------------|
| `probation_end` | `_contract_info.html:42-44`, `_basic_info.html:113` | Employee 모델에 DB 컬럼 추가 완료 | `9315d80ecc3e` |
| `bonus_rate` | `_salary_info.html:72-74` | Salary 모델에 DB 컬럼 추가 완료 | `9315d80ecc3e` |

---

## 6. 개선 로드맵

### 즉시 수정 (심각도: High) - 완료

#### 1. Employee 모델 probation_end 컬럼 추가 - **완료**
- **파일**: `app/models/employee.py:33`
- **변경**: `probation_end = db.Column(db.Date, nullable=True)`
- **마이그레이션**: `20251223_190332_add_probation_end_bonus_rate.py`
- **상태**: 적용 완료

#### 2. Salary 모델 bonus_rate 컬럼 추가 - **완료**
- **파일**: `app/models/salary.py:73`
- **변경**: `bonus_rate = db.Column(db.Integer, default=0)`
- **마이그레이션**: `20251223_190332_add_probation_end_bonus_rate.py`
- **상태**: 적용 완료

### 단기 개선 - 완료

#### 3. 전역 변수 정리 - **완료**
- **파일**: `app/static/js/app.js:114-160`
- **작업**: 9개 전역 함수에 deprecated 경고 래퍼 추가
- **제거 예정**: 2025-03 이후
- **마이그레이션 가이드**: 주석에 HRApp 네임스페이스 사용 방법 명시

#### 4. Services 레이어 확장 - **완료**
- **파일**: `app/static/js/services/organization-service.js` (신규 생성)
- **구현**: OrganizationService 클래스 + OrganizationApi 싱글턴 객체
- **메서드**: getTree, get, create, update, delete

#### 5. 하드코딩 필드 동적화 - **완료**
- **파일**: `app/constants/field_options.py`
- **추가 옵션**:
  - `WORKING_HOURS`: 주 40/35/30/20/15시간
  - `BREAK_TIME`: 60분/30분/없음
- **context_processor**: `get_all()` 메서드에 등록 완료

### 중기 개선 - 완료

#### 6. CSS 하드코딩 색상값 제거 - **완료**
- **파일**: `app/static/css/components/alert.css`, `badge.css`
- **변환**: 하드코딩 색상 → CSS 변수 (42개 변환)
  - `#dcfce7` → `var(--color-success-100)`
  - `#fee2e2` → `var(--color-error-100)`
  - `#166534` → `var(--color-success-700)`
  - 등

#### 7. JSDoc 주석 추가 - **완료**
- **파일**: `app/static/js/components/accordion.js`
- **추가**: @typedef, @class, @param, @returns, @private 주석 추가
- **효과**: IDE 자동완성 및 문서화 지원

#### 8. 접근성 개선 - **완료**
- **파일**: `app/templates/partials/employee_detail/_employee_header.html`
- **작업**: 11개 아이콘에 `aria-hidden="true"` 속성 추가
- **대상**: fa-user, fa-building, fa-id-badge, fa-calendar-check, fa-envelope, fa-phone, fa-map-marker-alt, fa-id-card(2), fa-sync-alt, fa-upload, fa-trash

### 장기 개선 - 준비 완료

#### 9. 하위 호환성 래퍼 제거 준비 - **완료**
- **대상 파일**:
  - `app/static/js/components/data-table-advanced.js` (래퍼)
  - `app/static/js/components/salary-calculator.js` (래퍼)
- **작업**: @deprecated JSDoc 추가, console.warn 경고 추가
- **제거 예정**: 2025-03 이후
- **마이그레이션**: 주석에 새 import 경로 명시

#### 10. 템플릿 매크로 추출 - **완료**
- **파일**: `app/templates/macros/_alerts.html`
- **작업**: `icon_for_category()` 매크로 추출
- **효과**: 4개 매크로에서 중복 아이콘 선택 로직 제거 (DRY 원칙)

---

## 7. 스타일 클래스 규칙

### 공통 클래스 패턴
| 클래스명 | 용도 |
|---------|------|
| `.content-section` | 섹션 컨테이너 |
| `.card`, `.card-header`, `.card-body` | 카드 |
| `.info-grid`, `.info-item`, `.info-label`, `.info-value` | 정보 그리드 |
| `.table-container`, `.table-empty` | 테이블 |
| `.badge` | 상태/구분 표시 |

### Badge 스타일 규칙
| 상태 | 클래스 |
|------|--------|
| 성공/가입/동거 | `.badge-success` |
| 경고/미가입 | `.badge-secondary` |
| 위험/미이수 | `.badge-danger` |
| 정보/신규 | `.badge-info` |

---

## 8. 데이터 바인딩 규칙

### 객체 명명 패턴
| 데이터 유형 | 객체명 | 예시 |
|------------|--------|------|
| 단일 객체 | `{entity}` | employee, contract, salary |
| 리스트 | `{entity}_list` | family_list, career_list |
| 요약 | `{entity}_summary` | attendance_summary |

### 빈 데이터 처리
- 필드: `{{ field or '-' }}` (통일 권장)
- 테이블: `.table-empty` 클래스 + 안내 메시지

---

## 참고

이 문서는 다음 분석 결과를 통합한 것입니다:
- frontend_architecture_analysis.md (810줄)
- frontend_template_analysis.md (975줄)
- template_db_field_comparison.md (254줄)

원본 파일은 상세한 분석 내용을 포함하고 있으며, 필요시 참조하시기 바랍니다.

---

**검증일**: 2025-12-23
**실행일**: 2025-12-23
**검증 범위**: 필드 매핑 이슈 (섹션 5), 개선 로드맵 구체화 (섹션 6)
**검증 결과**: Frontend 구조 검증 완료, 5개 필드 매핑 해결 확인, 2개 미해결 필드 식별
**실행 결과**: 개선 로드맵 11개 항목 전체 완료
- Phase 1 (즉시 수정): 3/3 완료
- Phase 2 (단기 개선): 3/3 완료
- Phase 3 (중기 개선): 3/3 완료
- Phase 4 (장기 개선): 2/2 완료
