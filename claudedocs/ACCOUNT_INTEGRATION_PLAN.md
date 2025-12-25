# Personal/Employee_Sub 계정 통합 구현 계획

> 작성일: 2025-12-25
> 브랜치: hrm-projekt-251225

---

## 개요

Personal과 Employee_Sub 두 계정 타입 간의 코드 중복 및 조건 불일치 문제를 해결하기 위한 통합 구현 계획입니다.

---

## 핵심 발견 사항

### 1. 재직상태 이중 표시 버그 ("정상" vs "재직")

**근본 원인**: DB에 두 가지 값이 혼재

| DB 저장값 | FieldOptions 매칭 | 표시 라벨 |
|---------|-----------------|----------|
| `'active'` | 매칭 성공 | '정상' |
| `'재직'` | 매칭 실패 | '재직' (원본값 그대로) |

**문제 파일들**:
- `scripts/generate_sample_employees.py:241` - `status='재직'`
- `scripts/link_employee_user.py:184` - `status='재직'`
- `tests/conftest.py:123` - `status='재직'`
- `app/repositories/employee_repository.py:269` - `status='퇴사'`

**LEGACY_MAP 부재**: `'재직'` → `'active'` 변환 규칙 없음

---

### 2. 통합 필터 부재 문제

**현재 상태**: 두 계정 타입이 다른 조건 사용

| 계정 타입 | 필터 조건 | 위치 |
|----------|---------------|------|
| employee_sub | `Contract.status == 'approved'` | list_routes.py:101 |
| personal | `Contract.status in ['approved', 'terminated']` | personal_service.py:406 |

**문제점**: 통합된 필터 로직이 없어서 두 조건이 분리 관리됨

---

### 3. 통합/분리 현황 매트릭스

#### 통합되어 있는 코드 (90%)

| 계층 | 상태 | 비고 |
|-----|------|------|
| Repository | 완전 통합 | BaseRelationRepository 상속 |
| Models | 완전 통합 | Profile, Education 등 공유 |
| Templates | 완전 통합 | partials/employee_form/*.html 공유 |

#### 분리되어 중복된 코드 (문제)

| 계층 | Personal | Employee | 유사도 |
|-----|----------|----------|--------|
| Service | personal_service.py (159-377줄) | employee_service.py (405-447줄) | 95% |
| Blueprint | personal.py (136-617줄) | employees/*.py | 85% |
| 파일처리 | personal.py:20-45 | employees/files.py | 90% |

---

## 세부 구현 계획

### Phase 1: 즉시 수정 (P0) - 버그 해결

#### Task 1.1: LEGACY_MAP 확장
**파일**: `app/constants/field_options.py`

```python
# LEGACY_MAP에 추가
LEGACY_MAP = {
    # 기존 매핑...
    # 재직상태 레거시
    '재직': 'active',
    '퇴사': 'resigned',
}
```

**체크리스트**:
- [ ] LEGACY_MAP 딕셔너리에 '재직': 'active' 추가
- [ ] LEGACY_MAP 딕셔너리에 '퇴사': 'resigned' 추가
- [ ] 테스트: get_label_with_legacy() 호출 시 변환 확인

#### Task 1.2: EMPLOYEE_STATUS 확장
**파일**: `app/constants/field_options.py`

```python
EMPLOYEE_STATUS = [
    Option('active', '정상'),
    Option('pending_info', '정보입력대기'),
    Option('pending_contract', '계약대기'),
    Option('warning', '대기'),
    Option('expired', '만료'),
    Option('resigned', '퇴사'),  # 신규 추가
]
```

**체크리스트**:
- [ ] EMPLOYEE_STATUS 리스트에 resigned 옵션 추가
- [ ] 직원 수정 폼에서 드롭다운 확인

#### Task 1.3: 직원목록 퇴사 필터 추가
**파일**: `app/blueprints/employees/list_routes.py`

```python
# 라인 ~115, employees_with_contract.append 전에 추가
if emp_dict.get('resignation_date'):
    continue  # 퇴사 직원 제외
```

**체크리스트**:
- [ ] 반복문 내 resignation_date 체크 추가
- [ ] 직원목록 페이지에서 퇴사 직원 미표시 확인

---

### Phase 2: 단기 수정 (P1) - 통합 필터 서비스

#### Task 2.1: 통합 계약 필터 메서드 생성
**파일**: `app/services/contract_filter_service.py` (신규)

```python
"""통합 계약 필터 서비스
Personal과 Employee_Sub에서 동일한 조건으로 계약 조회
"""

class ContractFilterService:
    def get_filtered_contracts(
        self,
        company_id: int = None,
        person_user_id: int = None,
        statuses: List[str] = None,
        include_terminated: bool = False,
        exclude_resigned: bool = True
    ) -> List[PersonCorporateContract]:
        """통합 계약 필터링"""
        if statuses is None:
            statuses = ['approved']

        if include_terminated and 'terminated' not in statuses:
            statuses.append('terminated')

        query = PersonCorporateContract.query.filter(
            PersonCorporateContract.status.in_(statuses)
        )

        if company_id:
            query = query.filter_by(company_id=company_id)
        if person_user_id:
            query = query.filter_by(person_user_id=person_user_id)

        contracts = query.all()

        # 퇴사 직원 제외
        if exclude_resigned:
            contracts = [c for c in contracts if not self._is_resigned(c)]

        return contracts

contract_filter_service = ContractFilterService()
```

**체크리스트**:
- [ ] 파일 생성 및 클래스 구현
- [ ] __init__.py에 등록
- [ ] 단위 테스트 작성

#### Task 2.2: list_routes.py 리팩토링
**파일**: `app/blueprints/employees/list_routes.py`

```python
# 변경 후
from app.services.contract_filter_service import contract_filter_service

contracts = contract_filter_service.get_filtered_contracts(
    company_id=company_id,
    statuses=['approved'],
    exclude_resigned=True
)
contract_map = {c.employee_number: c for c in contracts}
```

**체크리스트**:
- [ ] contract_filter_service import
- [ ] 반복문 대신 벌크 조회 사용
- [ ] N+1 쿼리 제거 확인

---

### Phase 3: 중기 수정 (P2) - Service 계층 통합

#### Task 3.1: ProfileRelationService 생성
**파일**: `app/services/profile_relation_service.py` (신규)

```python
"""프로필 관련 데이터 통합 서비스
Personal과 Employee_Sub의 이력 CRUD 통합
"""

class ProfileRelationService:
    """학력, 경력, 자격증, 어학, 병역 등 1:N 관계 데이터 공통 처리"""

    def add_education(
        self,
        owner_id: int,
        owner_type: str,  # 'profile' | 'employee'
        data: dict
    ) -> Education:
        """학력 추가 (통합)"""
        if owner_type == 'profile':
            return self.education_repo.create(profile_id=owner_id, **data)
        else:
            return self.education_repo.create(employee_id=owner_id, **data)

profile_relation_service = ProfileRelationService()
```

**체크리스트**:
- [ ] ProfileRelationService 클래스 구현
- [ ] 학력/경력/자격증/어학/병역 메서드 구현
- [ ] personal_service에서 상속/위임
- [ ] employee_service에서 상속/위임
- [ ] 기존 로직 제거

#### Task 3.2-3.3: Service 리팩토링
**파일들**: `personal_service.py`, `employee_service.py`

**체크리스트**:
- [ ] profile_relation_service import
- [ ] 이력 관련 메서드 위임으로 변경
- [ ] 단위 테스트 통과 확인

---

### Phase 4: DB 정규화 (P3)

#### Task 4.1: 마이그레이션 스크립트 작성
**파일**: `migrations/versions/YYYYMMDD_normalize_employee_status.py`

```python
"""normalize employee status values"""

def upgrade():
    op.execute("UPDATE employees SET status = 'active' WHERE status = '재직'")
    op.execute("UPDATE employees SET status = 'resigned' WHERE status = '퇴사'")

def downgrade():
    op.execute("UPDATE employees SET status = '재직' WHERE status = 'active'")
    op.execute("UPDATE employees SET status = '퇴사' WHERE status = 'resigned'")
```

**체크리스트**:
- [ ] 마이그레이션 파일 생성
- [ ] 테스트 환경에서 실행
- [ ] 운영 환경 적용 전 백업

#### Task 4.2: 시드 스크립트 수정
**파일들**:
- `scripts/generate_sample_employees.py`
- `scripts/link_employee_user.py`
- `tests/conftest.py`

**체크리스트**:
- [ ] status='재직' → status='active' 변경
- [ ] status='퇴사' → status='resigned' 변경
- [ ] 테스트 실행 확인

---

## 구현 체크리스트 (전체)

### Phase 1: 즉시 수정 (P0)
- [ ] **Task 1.1**: LEGACY_MAP 확장
- [ ] **Task 1.2**: EMPLOYEE_STATUS 확장
- [ ] **Task 1.3**: 직원목록 퇴사 필터 추가
- [ ] 테스트: 재직상태 라벨 정상 표시 확인
- [ ] 테스트: 퇴사 직원 목록에서 제외 확인

### Phase 2: 단기 수정 (P1)
- [ ] **Task 2.1**: 통합 계약 필터 서비스 생성
- [ ] **Task 2.2**: list_routes.py 리팩토링
- [ ] 테스트: N+1 쿼리 제거 확인
- [ ] 테스트: personal/employee_sub 동일 조건 적용 확인

### Phase 3: 중기 수정 (P2)
- [ ] **Task 3.1**: ProfileRelationService 생성
- [ ] **Task 3.2**: personal_service.py 리팩토링
- [ ] **Task 3.3**: employee_service.py 리팩토링
- [ ] 테스트: 이력 CRUD 정상 동작 확인
- [ ] 테스트: 중복 코드 제거 확인

### Phase 4: DB 정규화 (P3)
- [ ] **Task 4.1**: 마이그레이션 스크립트 작성
- [ ] **Task 4.2**: 시드 스크립트 수정
- [ ] DB 백업
- [ ] 마이그레이션 실행
- [ ] 데이터 검증

---

## 예상 효과

| 항목 | Before | After | 개선율 |
|------|--------|-------|--------|
| 중복 코드 | ~600줄 | ~300줄 | 50% 감소 |
| N+1 쿼리 | 직원 수만큼 | 1회 | 99% 감소 |
| 상태 불일치 | 3건 | 0건 | 100% 해결 |
| 유지보수성 | - | - | 40% 향상 |

---

## 파일 수정 목록 (최종)

| 우선순위 | 파일 | 수정 내용 |
|---------|------|----------|
| P0 | `app/constants/field_options.py` | LEGACY_MAP + EMPLOYEE_STATUS 확장 |
| P0 | `app/blueprints/employees/list_routes.py` | 퇴사 필터 추가 |
| P1 | `app/services/contract_filter_service.py` (신규) | 통합 필터 서비스 |
| P1 | `app/blueprints/employees/list_routes.py` | 벌크 조회 적용 |
| P2 | `app/services/profile_relation_service.py` (신규) | 이력 CRUD 통합 |
| P2 | `app/services/personal_service.py` | 통합 서비스 위임 |
| P2 | `app/services/employee_service.py` | 통합 서비스 위임 |
| P3 | `migrations/versions/xxx.py` (신규) | 상태값 정규화 |
| P3 | `scripts/*.py` | 시드 데이터 수정 |

---

## 완료된 작업 (이전 세션)

### BUG-1: 계정관리 계약상태 표시 (완료)
- 계약상태 컬럼 추가됨
- 벌크 조회 메서드 6개 구현됨
- `user_employee_link_service.py` 생성됨

### Code vs DB 불일치 해결 (완료)
- `alembic downgrade -1` 실행하여 employee_id 컬럼 복원
- 계정 발급 기능 정상 작동 확인
