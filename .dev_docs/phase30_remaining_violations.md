# Phase 30 Service Layer 레이어 분리 - 미작업 건 문서

## 개요

**작업일**: 2025-01-06
**Phase**: 30 - Service Layer 레이어 분리 리팩토링
**목표**: Blueprint -> Service -> Repository -> Model 아키텍처 규칙 준수

### 작업 결과 요약

| 구분 | 초기 | 최종 | 해결률 |
|------|------|------|--------|
| Model.query | 112건 | 12건 | 89% |
| db.session | 81건 | 18건 | 78% |
| **합계** | 193건 | **30건** | **84%** |

---

## 미작업 건 상세

### 1. 기반 클래스 (의도적 예외) - 16건

#### 1.1 `base/generic_relation_crud.py` (13건)

**위치**: `app/services/base/generic_relation_crud.py`

| 유형 | 건수 | 라인 |
|------|------|------|
| Model.query | 6건 | 124, 148, 185, 206, 223, 237 |
| db.session | 7건 | 164, 167, 189, 191, 209, 249, 252 |

**코드 패턴**:
```python
class GenericRelationCRUD:
    def __init__(self, model):
        self.model = model  # 동적 모델 주입

    def get_all(self, **filter_kwargs):
        # self.model이 런타임에 결정되므로 Repository 패턴 적용 불가
        query = self.model.query.filter_by(**filter_kwargs)
        return query.all()
```

**예외 사유**:
- 제네릭 CRUD 기반 클래스로, 어떤 Model이든 동적으로 처리해야 함
- Education, Career, Certificate 등 다양한 관계형 모델을 동적으로 처리
- 각 모델별 Repository를 생성하면 코드 중복 발생
- 이 클래스 자체가 일종의 "동적 Repository" 역할 수행

**조치**: 현상 유지 (의도적 예외)

---

#### 1.2 `base/history_service.py` (3건)

**위치**: `app/services/base/history_service.py`

| 유형 | 건수 | 라인 |
|------|------|------|
| Model.query | 1건 | 92 |
| db.session | 2건 | 96, 97 |

**예외 사유**:
- 히스토리 추적을 위한 제네릭 기반 클래스
- 다양한 모델의 변경 이력을 동적으로 관리

**조치**: 현상 유지 (의도적 예외)

---

### 2. 이벤트 리스너 (향후 리팩토링 대상) - 6건

#### 2.1 `event_listeners.py`

**위치**: `app/services/event_listeners.py`

| 유형 | 건수 | 라인 |
|------|------|------|
| Model.query | 4건 | 135, 142, 272, 304 |
| db.session | 2건 | 288, 289 |

**현재 코드**:
```python
def on_profile_updated(profile_id, field_name, old_value, new_value):
    # 이벤트 핸들러에서 직접 쿼리
    contracts = PersonCorporateContract.query.filter_by(...)
    settings = DataSharingSettings.query.filter_by(...)
```

**미작업 사유**:
1. 이벤트 리스너는 Service 레이어와 독립적으로 동작
2. SQLAlchemy 이벤트 시스템과 통합되어 있음
3. Repository 주입 시 순환 참조 위험 존재

**조치**: 향후 이벤트 시스템 전체 재설계 시 함께 리팩토링

**예상 작업**:
- 이벤트 핸들러 전용 Repository 주입 패턴 설계
- 순환 참조 방지를 위한 지연 로딩 패턴 적용
- 이벤트 버스 아키텍처 도입 검토

---

### 3. 감사 서비스 (향후 리팩토링 대상) - 3건

#### 3.1 `audit_service.py`

**위치**: `app/services/audit_service.py`

| 유형 | 건수 | 라인 |
|------|------|------|
| Model.query | 1건 | 352 (AuditLog 조회) |
| db.session | 2건 | 119, 120 (add, commit) |

**미작업 사유**:
1. AuditLogRepository가 별도로 필요함
2. 감사 로그는 다른 트랜잭션과 독립적으로 커밋되어야 함 (실패해도 로그는 남아야 함)
3. 현재 세션에서 우선순위가 낮음

**조치**: 향후 AuditLogRepository 생성 후 리팩토링

**예상 작업**:
```python
# 신규 Repository 생성
class AuditLogRepository(BaseRepository[AuditLog]):
    def create_log(self, data: Dict, commit: bool = True) -> AuditLog:
        ...

    def find_by_user_id(self, user_id: int) -> List[AuditLog]:
        ...
```

---

### 4. 직원 코어 서비스 (특수 케이스) - 2건

#### 4.1 `employee/employee_core_service.py`

**위치**: `app/services/employee/employee_core_service.py`

| 유형 | 건수 | 라인 |
|------|------|------|
| db.session | 2건 | 140 (flush), 285 (get) |

**현재 코드**:
```python
# ID 생성을 위한 flush
db.session.flush()

# 기존 레코드 확인
existing = db.session.get(Employee, employee_id)
```

**미작업 사유**:
1. `flush()`는 ID 생성 후 즉시 사용해야 하는 특수 케이스
2. `db.session.get()`은 SQLAlchemy 2.0 권장 패턴
3. Repository 메서드로 래핑 시 성능 저하 가능

**조치**: 현상 유지 (특수 케이스)

---

### 5. 동기화 서비스 (부분 리팩토링) - 3건

#### 5.1 `sync/sync_service.py`

**위치**: `app/services/sync/sync_service.py`

| 유형 | 건수 | 라인 |
|------|------|------|
| db.session | 3건 | 243, 298, 402 (1건은 주석) |

**미작업 사유**:
1. 복잡한 동기화 트랜잭션 로직
2. 여러 테이블 간 원자성 보장 필요
3. 일부는 주석 내 설명용 코드

**조치**: 향후 동기화 로직 재설계 시 함께 리팩토링

---

## 향후 작업 계획

### 우선순위 1: AuditLogRepository 생성

```
예상 작업량: 2시간
영향 범위: audit_service.py
```

1. `app/repositories/audit_log_repository.py` 생성
2. `AuditLogRepository` 클래스 구현
3. `audit_service.py` 리팩토링
4. 독립 트랜잭션 패턴 적용

### 우선순위 2: 이벤트 시스템 재설계

```
예상 작업량: 8시간
영향 범위: event_listeners.py, 관련 서비스들
```

1. 이벤트 버스 아키텍처 설계
2. 이벤트 핸들러 전용 Repository 주입 패턴
3. 순환 참조 방지 패턴 적용
4. 기존 이벤트 리스너 마이그레이션

### 우선순위 3: 동기화 서비스 개선

```
예상 작업량: 4시간
영향 범위: sync/sync_service.py
```

1. 트랜잭션 경계 명확화
2. Repository 패턴 완전 적용
3. 원자성 보장 로직 개선

---

## 예외 처리 정책 요약

| 분류 | 파일 | 건수 | 사유 | 조치 |
|------|------|------|------|------|
| 제네릭 기반 | `base/generic_relation_crud.py` | 13 | 동적 모델 처리 | 현상 유지 |
| 제네릭 기반 | `base/history_service.py` | 3 | 동적 모델 처리 | 현상 유지 |
| 이벤트 시스템 | `event_listeners.py` | 6 | 시스템 통합 | 향후 재설계 |
| 감사 로그 | `audit_service.py` | 3 | 독립 트랜잭션 | Repository 추가 예정 |
| 특수 케이스 | `employee_core_service.py` | 2 | 성능/패턴 | 현상 유지 |
| 동기화 | `sync/sync_service.py` | 3 | 복잡 트랜잭션 | 향후 재설계 |

---

## 검증 명령어

### Model.query 위반 확인
```bash
grep -r "\.query\." app/services/ --include="*.py" | grep -v "repository" | wc -l
# 예상 결과: 12
```

### db.session 위반 확인
```bash
grep -r "db\.session\." app/services/ --include="*.py" | wc -l
# 예상 결과: 18
```

---

## 변경 이력

| 날짜 | 작업 | 담당 |
|------|------|------|
| 2025-01-06 | Phase 30 리팩토링 완료 | Claude Code |
| 2025-01-06 | PlatformSettings 레거시 코드 삭제 | Claude Code |
| 2025-01-06 | 미작업 건 문서화 | Claude Code |
