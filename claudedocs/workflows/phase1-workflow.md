# Phase 1: Foundation System - Implementation Workflow

## Document Info
- Created: 2025-11-29
- Status: Ready to Start
- Prerequisite: Phase 0 COMPLETED
- Estimated Duration: 3-4 weeks

---

## Executive Summary

Phase 1은 HR 관리 시스템의 핵심 인프라를 구축합니다:
1. **인증 시스템** - 사용자 로그인/로그아웃 및 권한 관리
2. **조직 구조** - 트리 형태의 조직도 및 부서 관리
3. **시스템 설정** - 회사 정보 및 시스템 설정 관리

---

## Implementation Order (Dependency-Based)

```
Week 1: Authentication Foundation
├── P1-1: User Model ─────────────────┐
├── P1-2: Login/Logout ───────────────┤ (depends on P1-1)
├── P1-4: Auth Decorators ────────────┤ (depends on P1-2)
└── P1-3: RBAC ───────────────────────┘ (depends on P1-4)

Week 2: Organization Structure
├── P1-5: Organization Model ─────────┐
├── P1-6: Organization UI ────────────┤ (depends on P1-5)
├── P1-7: Tree Selector Component ────┤ (depends on P1-6)
└── P1-8: Position/Grade Management ──┘ (parallel with P1-7)

Week 3: System Settings
├── P1-9: SystemSetting Model ────────┐
├── P1-10: Employee Number Rules ─────┤ (depends on P1-9)
├── P1-11: Email Domain Config ───────┤ (parallel with P1-10)
└── P1-12: Company Information ───────┘ (parallel with P1-11)
```

---

## Week 1: Authentication System

### P1-1: User Model (Priority: Critical)

**Objective**: 사용자 인증을 위한 User 모델 생성

**Dependencies**: None
**Blocking**: P1-2, P1-3, P1-4

**Files to Create**:
```
app/models/user.py
app/repositories/user_repository.py
```

**Implementation Steps**:
1. [ ] User 모델 생성
   ```python
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       username = db.Column(db.String(80), unique=True, nullable=False)
       email = db.Column(db.String(120), unique=True, nullable=False)
       password_hash = db.Column(db.String(256), nullable=False)
       role = db.Column(db.String(20), default='employee')
       employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
       is_active = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       last_login = db.Column(db.DateTime)
   ```
2. [ ] 비밀번호 해싱 메서드 (set_password, check_password)
3. [ ] UserRepository 생성
4. [ ] models/__init__.py에 등록
5. [ ] 데이터베이스 마이그레이션 (ALTER TABLE)

**Validation**:
- [ ] User 생성/조회 정상 동작
- [ ] 비밀번호 해싱 정상 동작
- [ ] Employee 연결 정상 동작

---

### P1-2: Login/Logout Implementation

**Objective**: 로그인/로그아웃 기능 구현

**Dependencies**: P1-1
**Blocking**: P1-3, P1-4

**Files to Create/Modify**:
```
app/blueprints/auth.py (NEW)
app/templates/auth/login.html (NEW)
app/__init__.py (blueprint 등록)
```

**Implementation Steps**:
1. [ ] auth blueprint 생성
2. [ ] 로그인 페이지 템플릿 생성
3. [ ] 로그인 엔드포인트 (POST /auth/login)
4. [ ] 로그아웃 엔드포인트 (GET /auth/logout)
5. [ ] 세션 관리 설정
6. [ ] 로그인 실패 처리

**Validation**:
- [ ] 로그인 성공 시 대시보드 리다이렉트
- [ ] 로그인 실패 시 에러 메시지
- [ ] 로그아웃 시 세션 정리

---

### P1-4: Auth Decorators

**Objective**: 인증 관련 데코레이터 구현

**Dependencies**: P1-2
**Blocking**: P1-3

**Files to Create**:
```
app/utils/decorators.py (NEW)
app/utils/context_processors.py (NEW)
```

**Implementation Steps**:
1. [ ] @login_required 데코레이터
2. [ ] @role_required(role) 데코레이터
3. [ ] current_user 컨텍스트 프로세서
4. [ ] 인증 실패 시 로그인 페이지 리다이렉트

---

### P1-3: Role-Based Access Control (RBAC)

**Objective**: 역할 기반 접근 제어 구현

**Dependencies**: P1-4
**Blocking**: None

**Roles Definition**:
- `admin`: 전체 시스템 접근
- `manager`: 조직 내 직원 관리
- `employee`: 본인 정보 조회/수정

**Implementation Steps**:
1. [ ] 역할별 권한 매트릭스 정의
2. [ ] API 엔드포인트 보호
3. [ ] 템플릿에서 역할 기반 UI 제어
4. [ ] 권한 없는 접근 시 403 처리

---

## Week 2: Organization Structure

### P1-5: Organization Model

**Objective**: 조직 구조 모델 생성 (트리 구조)

**Dependencies**: P1-1 (soft dependency for manager_id)
**Blocking**: P1-6, P1-7

**Files to Create**:
```
app/models/organization.py (NEW)
app/repositories/organization_repository.py (NEW)
```

**Implementation Steps**:
1. [ ] Organization 모델 생성
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
2. [ ] OrganizationRepository 생성
3. [ ] 트리 조회 메서드 (get_tree, get_ancestors, get_descendants)
4. [ ] Employee 모델에 organization_id 추가

---

### P1-6: Organization Management UI

**Objective**: 조직 관리 화면 구현

**Dependencies**: P1-5
**Blocking**: P1-7

**Files to Create**:
```
app/blueprints/admin/__init__.py (NEW)
app/blueprints/admin/organization.py (NEW)
app/templates/admin/organization.html (NEW)
app/static/js/pages/admin-organization.js (NEW)
```

**Implementation Steps**:
1. [ ] admin blueprint 구조 생성
2. [ ] 조직 목록 페이지
3. [ ] 조직 추가/수정/삭제 기능
4. [ ] 트리 구조 시각화

---

### P1-7: Tree Selector Component

**Objective**: 조직 선택 트리 컴포넌트 구현

**Dependencies**: P1-6
**Blocking**: None

**Files to Create**:
```
app/static/js/components/tree-selector.js (NEW)
app/templates/components/_tree_selector.html (NEW)
```

**Implementation Steps**:
1. [ ] 재사용 가능한 트리 선택기 모듈
2. [ ] 모달 형태의 조직 선택 UI
3. [ ] 검색 기능
4. [ ] employee_form.html에 적용

---

### P1-8: Position/Grade Management

**Objective**: 직급/직책 코드 관리

**Dependencies**: None (parallel with P1-7)
**Blocking**: None

**Implementation Steps**:
1. [ ] 기존 classification_option 활용
2. [ ] 직급 분류 데이터 추가 (인턴~대표)
3. [ ] 직책 분류 데이터 추가 (팀장, 파트장 등)
4. [ ] 관리 화면 구현

---

## Week 3: System Settings

### P1-9: SystemSetting Model

**Objective**: 시스템 설정 모델 생성

**Dependencies**: None
**Blocking**: P1-10, P1-11, P1-12

**Files to Create**:
```
app/models/system_setting.py (NEW)
app/repositories/system_setting_repository.py (NEW)
```

**Implementation Steps**:
1. [ ] SystemSetting 모델 생성
   ```python
   class SystemSetting(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       key = db.Column(db.String(100), unique=True, nullable=False)
       value = db.Column(db.Text)
       value_type = db.Column(db.String(20))  # string, integer, boolean, json
       description = db.Column(db.Text)
       updated_at = db.Column(db.DateTime)
   ```
2. [ ] SystemSettingRepository 생성
3. [ ] 설정 캐싱 메커니즘 (선택)

---

### P1-10: Employee Number Generation Rules

**Objective**: 사번 생성 규칙 설정

**Dependencies**: P1-9
**Blocking**: None

**Implementation Steps**:
1. [ ] 사번 형식 설정 저장
2. [ ] 시작 번호 설정
3. [ ] 연도별 리셋 옵션
4. [ ] 기존 employee_number.py 연동

---

### P1-11: Email Domain Configuration

**Objective**: 회사 이메일 도메인 설정

**Dependencies**: P1-9
**Blocking**: None

**Files to Create**:
```
app/utils/email_generator.py (NEW)
```

**Implementation Steps**:
1. [ ] 이메일 도메인 설정 저장
2. [ ] 이메일 생성 규칙 (firstname.lastname@company.com)
3. [ ] 이메일 자동 생성 로직
4. [ ] 중복 체크 및 대안 제시

---

### P1-12: Company Information

**Objective**: 회사 기본 정보 관리

**Dependencies**: P1-9
**Blocking**: None

**Files to Create**:
```
app/templates/admin/company.html (NEW)
app/blueprints/admin/settings.py (NEW)
```

**Implementation Steps**:
1. [ ] 회사명, 대표자, 주소, 연락처
2. [ ] 사업자등록번호
3. [ ] 로고 이미지
4. [ ] 계약서/문서에 사용될 정보

---

## Dependencies Required

```txt
# requirements.txt additions
Flask-Login==0.6.3
Werkzeug>=3.0.0
```

---

## Security Considerations

- [ ] 비밀번호 해싱 (werkzeug.security)
- [ ] 세션 쿠키 보안 설정 (httponly, secure)
- [ ] CSRF 보호 활성화
- [ ] SQL Injection 방지 (SQLAlchemy ORM)
- [ ] XSS 방지 (Jinja2 auto-escaping)

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

---

## Completion Criteria

- [ ] 모든 구현 단계 완료
- [ ] 모든 테스트 통과
- [ ] 보안 검토 완료
- [ ] API 문서 업데이트
- [ ] CHANGELOG 업데이트

---

## Quick Start Command

Phase 1 시작:
```
/sc:implement P1-1 --start
```

전체 Phase 1 진행:
```
continue
```

