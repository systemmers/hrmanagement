# 계정 체계 리팩토링 설계안 (수정본)

> **작성일**: 2026-01-17
> **수정일**: 2026-01-17 (재검토 반영)
> **목표**: employee_sub 계정 유형 제거 (3계정 → 2계정)
> **상태**: 설계안 (승인 대기)

---

## 1. Executive Summary

### 1.1 핵심 발견
- **개인-법인 계약 프로세스가 이미 완전히 구현되어 있음**
- PersonCorporateContract 기반 계약 생성/승인/거절/종료 워크플로우 존재
- personal 계정이 법인과 계약 시 Employee 자동 생성/동기화 구현됨
- **따라서 employee_sub 제거는 "추가 구현"이 아닌 "코드 제거/단순화" 작업**

### 1.2 변경 범위
- employee_sub 계정 유형 제거
- employee_sub 관련 분기 로직 제거
- 기존 employee_sub 사용자 → personal 계정으로 마이그레이션
- **기존 계약 프로세스는 변경 없음**

### 1.3 예상 작업량
- 이전 설계: 7일 (과대 산정)
- **수정 설계: 3-4일** (코드 제거/단순화 + 마이그레이션)

---

## 2. 현재 시스템 분석

### 2.1 계정 유형별 플로우 (현재)

**personal 계정 플로우** (이미 완전 구현):
```
개인 가입 → PersonalProfile 생성 → 법인과 계약 요청/수락
         → 계약 승인 시 Employee 자동 생성 → 데이터 동기화
```

**employee_sub 계정 플로우** (제거 대상):
```
법인이 Employee 등록 → employee_sub 계정 생성 → User.employee_id로 직접 연결
                   → pending_info 상태면 프로필 완성
                   → pending_contract 상태면 계약 대기
```

### 2.2 employee_sub 사용처 분석

| 위치 | 사용 방식 | 제거 후 처리 |
|-----|----------|-------------|
| `User.ACCOUNT_EMPLOYEE_SUB` | 상수 정의 | 제거 |
| `User.employee_id` | Employee 직접 참조 | PCC로 대체 |
| `User.parent_user_id` | 부모 계정 참조 | 제거 (불필요) |
| `auth.py` | 로그인 후 상태 분기 | 단순화 |
| `mypage.py` | HR 카드 표시 분기 | personal만 유지 |
| `decorators.py` | 권한 체크 | personal만 유지 |
| `context_processors.py` | 가시성 체크 | 단순화 |
| `field_registry` | 필드 가시성 | 단순화 |
| `contract_workflow_service.py` | 승인 시 분기 | personal만 유지 |

### 2.3 기존 계약 프로세스 (유지)

`contract_workflow_service.py`의 `approve_contract()`:
```python
# personal 계정 처리 (유지)
if user.account_type == 'personal':
    profile = self.personal_profile_repo.find_by_user_id(user.id)
    if profile:
        employee = sync_service._find_or_create_employee(...)
        user.employee_id = employee.id
        employee.status = EmployeeStatus.ACTIVE
        sync_service.sync_personal_to_employee(...)

# employee_sub 계정 처리 (제거 대상)
else:
    if user.employee_id:
        employee = self.employee_repo.find_by_id(user.employee_id)
        employee.status = EmployeeStatus.ACTIVE
```

---

## 3. 변경 사항

### 3.1 User 모델 변경

```python
# 제거 항목
- ACCOUNT_EMPLOYEE_SUB = 'employee_sub'
- employee_id = db.Column(...)  # 직접 참조 제거
- parent_user_id = db.Column(...)  # 부모 참조 제거
- is_employee_sub_account()  # 메서드 제거
- parent_user = db.relationship(...)
- sub_users = db.relationship(...)

# VALID_ACCOUNT_TYPES 수정
VALID_ACCOUNT_TYPES = [ACCOUNT_PERSONAL, ACCOUNT_CORPORATE, ACCOUNT_PLATFORM]
```

### 3.2 데코레이터 변경 (`decorators.py`)

```python
# 제거
- personal_or_employee_account_required  # 더 이상 필요 없음

# AccountType.personal_types() 수정
def personal_types():
    return [AccountType.PERSONAL]  # employee_sub 제거
```

### 3.3 상수 변경 (`field_options.py`, `session_keys.py`, `field_registry`)

```python
# field_options.py - ACCOUNT_TYPE 옵션에서 제거
Option('employee_sub', '법인직원'),  # 제거

# session_keys.py - 상수 제거
EMPLOYEE_SUB = 'employee_sub'  # 제거

# field_registry/base.py - 가시성에서 제거
EMPLOYEE_SUB = 'employee_sub'  # 제거
```

### 3.4 서비스 변경

**contract_workflow_service.py**:
```python
def approve_contract(self, contract_id: int, user_id: int):
    # employee_sub 분기 제거
    # personal 계정 로직만 유지
    if user.account_type == 'personal':
        # 기존 로직 유지
        ...
```

**user_service.py**:
```python
# 제거
def get_employee_sub_users_with_employee(...)  # 더 이상 필요 없음
```

### 3.5 블루프린트 변경

**auth.py**:
```python
# 로그인 후 분기 단순화
if user.employee_id and user.account_type == 'employee_sub':  # 제거
    # 이 분기 전체 제거
```

**mypage.py**:
```python
# personal 계정은 이미 company_card_list로 리다이렉트
# employee_sub 분기 제거
```

---

## 4. 마이그레이션 전략

### 4.1 데이터 마이그레이션

```python
def migrate_employee_sub_to_personal():
    """기존 employee_sub 계정을 personal로 전환"""

    employee_sub_users = User.query.filter_by(account_type='employee_sub').all()

    for user in employee_sub_users:
        # 1. 기존 계약 확인 또는 생성
        employee = Employee.query.get(user.employee_id) if user.employee_id else None

        if employee:
            # 계약이 없으면 자동 생성 (approved 상태)
            contract = PersonCorporateContract.query.filter_by(
                person_user_id=user.id,
                company_id=user.company_id,
                status='approved'
            ).first()

            if not contract:
                contract = PersonCorporateContract(
                    person_user_id=user.id,
                    company_id=user.company_id,
                    employee_number=employee.employee_number,
                    status='approved',
                    approved_at=datetime.utcnow(),
                    notes='employee_sub 마이그레이션 자동 생성'
                )
                db.session.add(contract)

        # 2. PersonalProfile 생성 (없으면)
        if not user.personal_profile:
            profile = PersonalProfile(
                user_id=user.id,
                name=employee.name if employee else user.username,
                email=user.email,
                mobile_phone=employee.mobile_phone if employee else None,
                # 기타 필드 동기화
            )
            db.session.add(profile)

        # 3. User 전환
        user.account_type = 'personal'

    db.session.commit()
```

### 4.2 Alembic 마이그레이션

```python
"""remove employee_sub account type

Revision ID: xxx_remove_employee_sub
"""

def upgrade():
    # Phase 1: 데이터 마이그레이션 (Python 스크립트로 별도 실행)
    # migrate_employee_sub_to_personal() 실행

    # Phase 2: 컬럼 제거 (데이터 마이그레이션 후)
    # 주의: employee_id는 personal 계정에서도 사용 중 (계약 승인 시 설정됨)
    # 따라서 employee_id는 유지하거나, PCC.employee_id로 완전 이전 후 제거

    # parent_user_id는 바로 제거 가능
    op.drop_constraint('fk_users_parent_user_id', 'users', type_='foreignkey')
    op.drop_column('users', 'parent_user_id')

def downgrade():
    op.add_column('users', sa.Column('parent_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_parent_user_id', 'users', 'users', ['parent_user_id'], ['id'])
```

### 4.3 User.employee_id 처리 전략

**현재 상황**:
- personal 계정: 계약 승인 시 `user.employee_id = employee.id` 설정됨
- employee_sub 계정: 생성 시 직접 설정됨

**옵션 1: employee_id 유지** (권장)
- 계약 승인 시 employee_id 설정 로직 유지
- 조회 편의성 유지
- 단순한 변경

**옵션 2: employee_id 완전 제거**
- PCC.employee_number로만 Employee 조회
- 추가 JOIN 필요
- 더 깔끔하지만 성능 영향

**권장**: 옵션 1 (employee_id 유지)

---

## 5. 영향받는 파일 목록 (수정본)

### 5.1 핵심 변경 (12개 파일)

| 파일 | 변경 내용 | 우선순위 |
|-----|----------|---------|
| `app/domains/user/models/user.py` | ACCOUNT_EMPLOYEE_SUB 상수/메서드 제거 | 높음 |
| `app/shared/constants/field_options.py` | ACCOUNT_TYPE 옵션 제거 | 높음 |
| `app/shared/constants/session_keys.py` | EMPLOYEE_SUB 상수 제거 | 높음 |
| `app/shared/constants/field_registry/base.py` | 가시성 옵션 제거 | 높음 |
| `app/shared/utils/decorators.py` | 데코레이터 단순화 | 높음 |
| `app/shared/utils/context_processors.py` | 가시성 체크 단순화 | 중간 |
| `app/domains/user/blueprints/auth.py` | 분기 로직 제거 | 중간 |
| `app/domains/user/blueprints/mypage.py` | 분기 로직 단순화 | 중간 |
| `app/domains/contract/services/contract_workflow_service.py` | employee_sub 분기 제거 | 중간 |
| `app/domains/user/services/user_service.py` | 관련 메서드 제거 | 낮음 |
| `app/domains/user/repositories/user_repository.py` | 관련 메서드 제거 | 낮음 |
| `app/domains/employee/services/employee_account_service.py` | 계정 생성 로직 수정 | 낮음 |

### 5.2 분기 로직 제거 (단순 수정, 8개 파일)

| 파일 | 변경 내용 |
|-----|----------|
| `app/domains/user/blueprints/profile/routes.py` | employee_sub 분기 제거 |
| `app/domains/user/blueprints/profile/decorators.py` | 어댑터 분기 제거 |
| `app/domains/employee/blueprints/list_routes.py` | 분기 제거 |
| `app/domains/employee/blueprints/section_api.py` | 권한 체크 단순화 |
| `app/domains/employee/services/inline_edit_service.py` | 권한 체크 단순화 |
| `app/domains/contract/blueprints/contracts.py` | 분기 제거 |
| `app/domains/company/blueprints/corporate.py` | 주석 수정 |
| `app/domains/platform/blueprints/main.py` | 분기 제거 |

### 5.3 테스트 파일 (5개)

| 파일 | 변경 내용 |
|-----|----------|
| `tests/unit/models/test_user_model.py` | employee_sub 테스트 제거 |
| `tests/unit/services/test_user_service.py` | 관련 테스트 제거 |
| `tests/unit/services/test_contract_workflow_service.py` | employee_sub 테스트 수정 |
| `tests/blueprints/test_profile_routes.py` | employee_sub 테스트 제거 |
| 기타 통합 테스트 | 분기 테스트 수정 |

### 5.4 스크립트 파일 (정리 대상)

| 파일 | 처리 |
|-----|------|
| `scripts/link_employee_user.py` | 삭제 또는 아카이브 |
| `scripts/generate_fake_test_data.py` | employee_sub 생성 로직 제거 |
| `scripts/generate_excel_test_db.py` | employee_sub 생성 로직 제거 |
| `scripts/test_multitenancy_accounts.py` | employee_sub 테스트 제거 |

---

## 6. 구현 계획 (수정본)

### Phase 1: 모델/상수 변경 (0.5일)

1. User 모델 수정
   - ACCOUNT_EMPLOYEE_SUB 상수 제거
   - is_employee_sub_account() 메서드 제거
   - VALID_ACCOUNT_TYPES 수정

2. 상수 파일 수정
   - field_options.py
   - session_keys.py
   - field_registry/base.py

### Phase 2: 서비스/데코레이터 변경 (1일)

1. decorators.py 단순화
2. context_processors.py 단순화
3. contract_workflow_service.py employee_sub 분기 제거
4. user_service.py, user_repository.py 관련 메서드 제거

### Phase 3: 블루프린트 변경 (1일)

1. auth.py 분기 제거
2. mypage.py 단순화
3. 기타 분기 로직 제거

### Phase 4: 마이그레이션 + 테스트 (1일)

1. 마이그레이션 스크립트 작성/실행
2. Alembic 마이그레이션
3. 테스트 파일 수정/실행
4. 스크립트 정리

**총 예상 시간: 3.5일**

---

## 7. 위험 요소 및 완화

| 위험 | 영향도 | 완화 전략 |
|-----|-------|----------|
| 기존 employee_sub 사용자 세션 무효화 | 중간 | 재로그인 안내, 점진적 롤아웃 |
| 마이그레이션 데이터 누락 | 높음 | 백업, 검증 쿼리, 롤백 스크립트 |
| 테스트 누락 | 중간 | 기존 테스트 전체 실행 |

---

## 8. 법인이 직원 먼저 등록하는 시나리오

### 현재 (employee_sub 사용)
```
법인 → Employee 등록 → employee_sub 계정 생성 → 계정정보 직원에게 전달
```

### 변경 후 (계약 기반)
```
법인 → Employee 등록 → 이메일로 초대 발송 → 개인이 personal 가입
    → 초대 수락 (계약 승인) → Employee-User 연결
```

**구현 필요 사항**:
- 법인이 Employee 등록 시 "초대 발송" 기능 추가
- 초대 이메일 템플릿
- 초대 수락 플로우 (기존 계약 승인 활용)

**참고**: 이 기능은 별도 Phase로 구현 가능 (employee_sub 제거와 독립)

---

## 9. 결론

### 9.1 이전 설계안과의 차이

| 항목 | 이전 설계 | 수정 설계 |
|-----|----------|----------|
| 성격 | 새로운 시스템 설계 | 기존 코드 제거/단순화 |
| 계약 프로세스 | 신규 구현 필요 | 이미 구현됨 (변경 없음) |
| 영향 파일 | 55개+ | 25개 |
| 예상 시간 | 7일 | 3.5일 |

### 9.2 추천 사항

employee_sub 제거를 **추천**합니다.

**장점**:
- 코드 단순화 (분기 로직 제거)
- 계정 체계 명확화 (2개 유형만)
- 유지보수 용이성 향상
- 기존 계약 프로세스 100% 활용

**작업량**:
- 대부분 코드 제거/단순화
- 새로운 로직 추가 최소화

### 9.3 다음 단계

1. 이 설계안 검토 및 승인
2. Phase 1 시작 (모델/상수 변경)
3. 개발 환경에서 마이그레이션 테스트
4. 프로덕션 배포

---

## Appendix: employee_sub 사용 현황 (grep 결과)

### 앱 코드 (제거/수정 대상)
```
app/domains/user/models/user.py
app/domains/user/services/user_service.py
app/domains/user/services/user_employee_link_service.py
app/domains/user/repositories/user_repository.py
app/domains/user/blueprints/auth.py
app/domains/user/blueprints/mypage.py
app/domains/user/blueprints/profile/routes.py
app/domains/user/blueprints/profile/decorators.py
app/domains/contract/services/contract_workflow_service.py
app/domains/contract/services/contract_core_service.py
app/domains/contract/services/contract_filter_service.py
app/domains/contract/blueprints/contracts.py
app/domains/contract/models/person_contract.py
app/domains/employee/services/employee_account_service.py
app/domains/employee/services/inline_edit_service.py
app/domains/employee/blueprints/list_routes.py
app/domains/employee/blueprints/mutation_routes.py
app/domains/employee/blueprints/section_api.py
app/domains/company/blueprints/corporate.py
app/domains/platform/blueprints/main.py
app/shared/utils/decorators.py
app/shared/utils/context_processors.py
app/shared/utils/tenant.py
app/shared/constants/session_keys.py
app/shared/constants/field_options.py
app/shared/constants/field_registry/base.py
app/shared/blueprints/api.py
```

### 스크립트 (정리/삭제)
```
scripts/link_employee_user.py
scripts/generate_fake_test_data.py
scripts/generate_excel_test_db.py
scripts/test_multitenancy_accounts.py
scripts/setup_balanced_test_data.py
scripts/check_data_integrity.py
scripts/test_login_playwright.py
```

### 테스트 (수정)
```
tests/unit/models/test_user_model.py
tests/unit/services/test_user_service.py
tests/unit/services/test_contract_workflow_service.py
tests/blueprints/test_profile_routes.py
```
