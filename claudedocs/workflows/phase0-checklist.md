# Phase 0: Immediate Improvements - Detailed Checklist

## Document Info
- Created: 2025-11-29
- Phase Duration: 1-2 weeks
- Status: Not Started
- Prerequisite: None

---

## Task P0-1: Add Missing Form Sections

### Objective
직원 등록 폼에 누락된 섹션 추가 (급여정보, 4대보험, 언어능력, 프로젝트)

### Pre-conditions
- [ ] 현재 employee_form.html 구조 확인
- [ ] 기존 모델 필드 확인 (Salary, Insurance, Language, Project)
- [ ] 기존 JavaScript 동적 폼 패턴 확인

### Implementation Steps

#### 급여정보 섹션
- [ ] employee_form.html에 급여정보 섹션 HTML 추가
- [ ] 네비게이션 메뉴에 급여정보 항목 추가
- [ ] 폼 제출 로직에 급여 데이터 처리 추가
- [ ] employees.py blueprint에 급여 저장 로직 추가

#### 4대보험 섹션
- [ ] employee_form.html에 4대보험 섹션 HTML 추가
- [ ] 네비게이션 메뉴에 4대보험 항목 추가
- [ ] 폼 제출 로직에 보험 데이터 처리 추가
- [ ] employees.py blueprint에 보험 저장 로직 추가

#### 언어능력 섹션
- [ ] employee_form.html에 언어능력 섹션 HTML 추가
- [ ] 동적 추가/삭제 JavaScript 구현
- [ ] 네비게이션 메뉴에 언어능력 항목 추가
- [ ] employees.py blueprint에 언어 저장 로직 추가

#### 프로젝트 섹션
- [ ] employee_form.html에 프로젝트 섹션 HTML 추가
- [ ] 동적 추가/삭제 JavaScript 구현
- [ ] 네비게이션 메뉴에 프로젝트 항목 추가
- [ ] employees.py blueprint에 프로젝트 저장 로직 추가

### Validation
- [ ] 새 섹션들이 올바르게 렌더링되는지 확인
- [ ] 폼 제출 시 데이터가 DB에 저장되는지 확인
- [ ] 수정 모드에서 기존 데이터가 로드되는지 확인
- [ ] 동적 항목 추가/삭제가 정상 작동하는지 확인

### Files to Modify
- `app/templates/employee_form.html`
- `app/blueprints/employees.py`
- `app/static/js/pages/employee-form.js`

---

## Task P0-2: Daum Address API Integration

### Objective
주소 입력 필드에 다음 주소 API 연동

### Pre-conditions
- [ ] 다음 주소 API 문서 확인
- [ ] 현재 주소 입력 UI 확인

### Implementation Steps
- [ ] Daum 주소 API 스크립트 추가 (CDN)
- [ ] 주소 검색 버튼 UI 추가
- [ ] 주소 검색 모달 JavaScript 구현
- [ ] 검색 결과를 주소, 우편번호 필드에 자동 입력
- [ ] 상세주소 입력 필드 포커스 처리

### Validation
- [ ] 주소 검색 모달 정상 표시
- [ ] 검색 결과 선택 시 필드 자동 입력
- [ ] 모바일에서 정상 동작

### Files to Modify
- `app/templates/employee_form.html`
- `app/templates/base.html` (스크립트 추가)
- `app/static/js/pages/employee-form.js`

---

## Task P0-3: Employee Number Auto-generation

### Objective
사번 자동생성 로직 구현 (규칙: EMP-YYYY-NNN)

### Pre-conditions
- [ ] 현재 사번 필드 확인
- [ ] 기존 사번 형식 확인

### Implementation Steps
- [ ] 사번 생성 유틸리티 함수 작성 (utils/employee_number.py)
- [ ] 연도별 시퀀스 관리 로직
- [ ] 직원 생성 시 자동 사번 부여
- [ ] 사번 중복 체크 로직
- [ ] 수동 입력 옵션 유지 (자동생성 체크박스)

### Validation
- [ ] 신규 직원 등록 시 사번 자동 생성
- [ ] 연도가 바뀌면 시퀀스 리셋
- [ ] 중복 사번 방지

### Files to Create/Modify
- `app/utils/employee_number.py` (NEW)
- `app/blueprints/employees.py`
- `app/templates/employee_form.html`

---

## Task P0-4: File Upload Functionality

### Objective
프로필 사진 및 첨부파일 업로드 기능 구현

### Pre-conditions
- [ ] 업로드 파일 저장 경로 결정 (static/uploads/)
- [ ] 허용 파일 형식 정의
- [ ] 파일 크기 제한 정의

### Implementation Steps

#### Backend
- [ ] 파일 업로드 유틸리티 작성 (utils/file_upload.py)
- [ ] 업로드 엔드포인트 생성 (/api/upload)
- [ ] 파일 검증 로직 (형식, 크기)
- [ ] 파일명 충돌 방지 (UUID 사용)
- [ ] 보안 검증 (파일 확장자 화이트리스트)

#### Frontend
- [ ] 파일 선택 UI 개선
- [ ] 드래그 앤 드롭 지원 (선택)
- [ ] 업로드 진행률 표시
- [ ] 미리보기 기능 (이미지)
- [ ] 삭제 기능

### Validation
- [ ] 이미지 파일 업로드 정상 동작
- [ ] 비허용 파일 형식 거부
- [ ] 파일 크기 초과 시 에러 메시지
- [ ] 업로드된 파일 접근 가능

### Files to Create/Modify
- `app/utils/file_upload.py` (NEW)
- `app/blueprints/api.py`
- `app/templates/employee_form.html`
- `app/static/js/pages/employee-form.js`
- `app/config.py` (업로드 설정 추가)

---

## Task P0-5: Employee List Improvements

### Objective
직원 목록 정렬/필터 기능 개선

### Pre-conditions
- [ ] 현재 employee_list.html 기능 확인
- [ ] 필터링 대상 필드 정의

### Implementation Steps
- [ ] 테이블 헤더 클릭 정렬 구현
- [ ] 필터 옵션 추가 (부서, 직급, 재직상태)
- [ ] 검색 기능 개선
- [ ] 페이지네이션 개선
- [ ] 정렬/필터 상태 URL 파라미터 유지

### Validation
- [ ] 각 컬럼 정렬 정상 동작
- [ ] 필터 조합 정상 동작
- [ ] 페이지 이동 시 필터 유지

### Files to Modify
- `app/templates/employee_list.html`
- `app/blueprints/employees.py`
- `app/static/js/pages/employee-list.js` (필요시)

---

## Testing Checklist

### Manual Testing
- [ ] 모든 새 섹션 폼 입력 테스트
- [ ] 주소 검색 기능 테스트
- [ ] 사번 자동생성 테스트
- [ ] 파일 업로드 테스트
- [ ] 직원 목록 정렬/필터 테스트

### Browser Compatibility
- [ ] Chrome
- [ ] Firefox
- [ ] Safari (선택)
- [ ] Edge

### Responsive Design
- [ ] Desktop (1920px)
- [ ] Tablet (768px)
- [ ] Mobile (375px)

---

## Completion Criteria

- [ ] 모든 구현 단계 완료
- [ ] 모든 유효성 검사 통과
- [ ] 테스트 체크리스트 완료
- [ ] 코드 리뷰 완료
- [ ] CHANGELOG 업데이트
- [ ] 문서 업데이트

---

## Notes

### Dependencies
- 없음 (현재 스택으로 구현 가능)

### Risks
- 파일 업로드 보안 취약점 주의
- 대용량 파일 처리 시 메모리 관리

### Rollback Plan
- Git을 통한 롤백 가능
- 각 Task별 별도 커밋 권장

