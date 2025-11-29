# Phase 1: Foundation System - Detailed Checklist

## Document Info
- Created: 2025-11-29
- Phase Duration: 3-4 weeks
- Status: Not Started
- Prerequisite: Phase 0 complete (recommended)

---

## Task P1-1: User Model

### Objective
사용자 인증을 위한 User 모델 생성

### Pre-conditions
- [ ] 역할(Role) 정의 확정 (admin, manager, employee)
- [ ] Employee 모델과 연결 방식 결정

### Implementation Steps
- [ ] User 모델 생성 (app/models/user.py)
  ```python
  class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(80), unique=True, nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)
      password_hash = db.Column(db.String(256), nullable=False)
      role = db.Column(db.String(20), default='employee')
      employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
      is_active = db.Column(db.Boolean, default=True)
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
      last_login = db.Column(db.DateTime, nullable=True)
  ```
- [ ] 비밀번호 해싱 메서드 추가 (set_password, check_password)
- [ ] User Repository 생성
- [ ] models/__init__.py에 User 등록
- [ ] 데이터베이스 마이그레이션

### Validation
- [ ] User 생성 정상 동작
- [ ] 비밀번호 해싱 정상 동작
- [ ] Employee 연결 정상 동작

### Files to Create
- `app/models/user.py`
- `app/repositories/user_repository.py`

---

## Task P1-2: Login/Logout Implementation

### Objective
로그인/로그아웃 기능 구현

### Pre-conditions
- [ ] User 모델 완성
- [ ] 세션 관리 방식 결정 (Flask-Login vs 세션)

### Implementation Steps
- [ ] auth blueprint 생성 (app/blueprints/auth.py)
- [ ] 로그인 페이지 템플릿 생성
- [ ] 로그인 엔드포인트 구현 (POST /auth/login)
- [ ] 로그아웃 엔드포인트 구현 (GET /auth/logout)
- [ ] 세션 관리 설정
- [ ] 로그인 폼 유효성 검사
- [ ] 로그인 실패 처리 (잘못된 비밀번호, 비활성 계정)
- [ ] 마지막 로그인 시간 업데이트

### Validation
- [ ] 로그인 성공 시 대시보드 리다이렉트
- [ ] 로그인 실패 시 에러 메시지 표시
- [ ] 로그아웃 시 세션 정리
- [ ] 비활성 계정 로그인 차단

### Files to Create/Modify
- `app/blueprints/auth.py` (NEW)
- `app/templates/auth/login.html` (NEW)
- `app/__init__.py` (blueprint 등록)
- `app/config.py` (세션 설정)

---

## Task P1-3: Role-Based Access Control (RBAC)

### Objective
역할 기반 접근 제어 구현

### Pre-conditions
- [ ] 역할별 권한 정의
  - admin: 전체 접근
  - manager: 조직 내 직원 관리
  - employee: 본인 정보 조회/수정

### Implementation Steps
- [ ] 권한 데코레이터 생성 (app/utils/decorators.py)
  ```python
  @login_required
  @role_required('admin')
  @permission_required('edit_employee')
  ```
- [ ] 권한 체크 미들웨어
- [ ] 역할별 메뉴 표시 제어
- [ ] API 엔드포인트 보호
- [ ] 템플릿에서 역할 기반 UI 제어

### Validation
- [ ] admin: 모든 기능 접근 가능
- [ ] manager: 소속 직원만 관리 가능
- [ ] employee: 본인 정보만 접근 가능
- [ ] 권한 없는 접근 시 403 에러

### Files to Create/Modify
- `app/utils/decorators.py` (NEW)
- `app/blueprints/employees.py` (권한 적용)
- `app/templates/base.html` (메뉴 제어)

---

## Task P1-4: Auth Decorators

### Objective
인증 관련 데코레이터 구현

### Implementation Steps
- [ ] @login_required 데코레이터
- [ ] @role_required(role) 데코레이터
- [ ] @permission_required(permission) 데코레이터
- [ ] current_user 컨텍스트 프로세서
- [ ] 인증 실패 시 로그인 페이지 리다이렉트

### Files to Create
- `app/utils/decorators.py`
- `app/utils/context_processors.py`

---

## Task P1-5: Organization Model

### Objective
조직 구조 모델 생성 (트리 구조)

### Pre-conditions
- [ ] 조직 구조 깊이 결정 (회사 > 본부 > 부서 > 팀)
- [ ] 조직 유형 정의

### Implementation Steps
- [ ] Organization 모델 생성
  ```python
  class Organization(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(100), nullable=False)
      code = db.Column(db.String(50), unique=True)
      org_type = db.Column(db.String(50))  # company, division, department, team
      parent_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
      manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
      sort_order = db.Column(db.Integer, default=0)
      is_active = db.Column(db.Boolean, default=True)

      parent = db.relationship('Organization', remote_side=[id], backref='children')
  ```
- [ ] 조직 Repository 생성
- [ ] 트리 조회 메서드 (get_tree, get_ancestors, get_descendants)
- [ ] Employee 모델에 organization_id 추가

### Validation
- [ ] 조직 CRUD 정상 동작
- [ ] 트리 구조 조회 정상 동작
- [ ] 순환 참조 방지

### Files to Create/Modify
- `app/models/organization.py` (NEW)
- `app/repositories/organization_repository.py` (NEW)
- `app/models/employee.py` (organization_id 추가)

---

## Task P1-6: Organization Management UI

### Objective
조직 관리 화면 구현

### Implementation Steps
- [ ] admin blueprint 생성 (app/blueprints/admin/)
- [ ] 조직 목록 페이지
- [ ] 조직 추가/수정/삭제 기능
- [ ] 트리 구조 시각화 (jsTree 또는 커스텀)
- [ ] 드래그 앤 드롭 순서 변경 (선택)

### Files to Create
- `app/blueprints/admin/__init__.py`
- `app/blueprints/admin/organization.py`
- `app/templates/admin/organization.html`
- `app/static/js/pages/admin-organization.js`

---

## Task P1-7: Tree Selector Component

### Objective
조직 선택 트리 컴포넌트 구현

### Implementation Steps
- [ ] 재사용 가능한 트리 선택기 JavaScript 모듈
- [ ] 모달 형태의 조직 선택 UI
- [ ] 선택된 조직 표시
- [ ] 검색 기능
- [ ] employee_form.html에 적용

### Files to Create/Modify
- `app/static/js/components/tree-selector.js` (NEW)
- `app/templates/components/_tree_selector.html` (NEW)
- `app/templates/employee_form.html`

---

## Task P1-8: Position/Grade Management

### Objective
직급/직책 코드 관리

### Implementation Steps
- [ ] 기존 classification_option.py 활용
- [ ] 직급 분류 데이터 추가 (인턴~대표)
- [ ] 직책 분류 데이터 추가 (팀장, 파트장 등)
- [ ] 관리 화면 구현
- [ ] employee_form.html 드롭다운 연동

### Files to Modify
- `app/models/classification_option.py`
- `app/templates/admin/classification.html`
- `app/templates/employee_form.html`

---

## Task P1-9: SystemSetting Model

### Objective
시스템 설정 모델 생성

### Implementation Steps
- [ ] SystemSetting 모델 생성
  ```python
  class SystemSetting(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      key = db.Column(db.String(100), unique=True, nullable=False)
      value = db.Column(db.Text)
      value_type = db.Column(db.String(20))  # string, integer, boolean, json
      description = db.Column(db.Text)
      updated_at = db.Column(db.DateTime)
  ```
- [ ] 설정 Repository 생성
- [ ] 캐싱 메커니즘 (선택)

### Files to Create
- `app/models/system_setting.py`
- `app/repositories/system_setting_repository.py`

---

## Task P1-10: Employee Number Generation Rules

### Objective
사번 생성 규칙 설정

### Implementation Steps
- [ ] 사번 형식 설정 (예: EMP-{YYYY}-{NNN})
- [ ] 시작 번호 설정
- [ ] 연도별 리셋 옵션
- [ ] 설정 UI

### Files to Modify
- `app/utils/employee_number.py`
- `app/templates/admin/settings.html`

---

## Task P1-11: Email Domain Configuration

### Objective
회사 이메일 도메인 설정

### Implementation Steps
- [ ] 이메일 도메인 설정 저장
- [ ] 이메일 생성 규칙 (예: {firstname}.{lastname}@company.com)
- [ ] 이메일 자동 생성 로직
- [ ] 중복 체크 및 대안 제시

### Files to Modify
- `app/utils/email_generator.py` (NEW)
- `app/templates/admin/settings.html`

---

## Task P1-12: Company Information

### Objective
회사 기본 정보 관리

### Implementation Steps
- [ ] 회사명, 대표자, 주소, 연락처
- [ ] 사업자등록번호
- [ ] 로고 이미지
- [ ] 계약서/문서에 사용될 정보

### Files to Create/Modify
- `app/templates/admin/company.html` (NEW)
- `app/blueprints/admin/settings.py`

---

## Testing Checklist

### Unit Tests
- [ ] User 모델 테스트
- [ ] 인증 로직 테스트
- [ ] 권한 데코레이터 테스트
- [ ] Organization 모델 테스트

### Integration Tests
- [ ] 로그인 플로우 테스트
- [ ] 권한 체크 테스트
- [ ] 조직 CRUD 테스트

### Security Tests
- [ ] SQL Injection 방지 확인
- [ ] XSS 방지 확인
- [ ] CSRF 토큰 적용 확인
- [ ] 비밀번호 해싱 확인
- [ ] 세션 보안 확인

---

## Completion Criteria

- [ ] 모든 구현 단계 완료
- [ ] 모든 테스트 통과
- [ ] 보안 검토 완료
- [ ] 코드 리뷰 완료
- [ ] API 문서 업데이트
- [ ] CHANGELOG 업데이트

---

## Notes

### Dependencies to Add
```
Flask-Login==0.6.3
Werkzeug>=3.0.0
```

### Security Considerations
- 비밀번호는 반드시 해싱 (werkzeug.security)
- 세션 쿠키 보안 설정 (httponly, secure)
- CSRF 보호 활성화
- 로그인 시도 제한 (선택)

### Rollback Plan
- 데이터베이스 마이그레이션 롤백 스크립트 준비
- 기능별 feature branch 유지

