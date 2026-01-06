# app/ 디렉토리 가이드

Flask 애플리케이션의 핵심 모듈들이 위치한 디렉토리입니다.

## 디렉토리 구조

| 폴더 | 역할 | 주요 파일 |
|------|------|----------|
| `blueprints/` | URL 라우팅, 요청 처리 | 모듈별 분할 (employees/, corporate_settings/, platform/) |
| `services/` | 비즈니스 로직 (Facade 패턴) | contract/, sync/, employee/, validation/ |
| `repositories/` | 데이터 접근 (BaseRepository 상속) | mixins/tenant_filter.py |
| `models/` | SQLAlchemy 모델 | to_dict, from_dict 필수 |
| `constants/` | 상수 정의 (SSOT) | status.py, field_options.py, field_registry/ |
| `utils/` | 유틸리티, 데코레이터 | decorators.py, transaction.py, rrn_parser.py |
| `adapters/` | 외부 서비스 어댑터 | AI 서비스 연동 |

## 핵심 파일

| 파일 | 설명 |
|------|------|
| `__init__.py` | Flask 앱 팩토리 (`create_app()`) |
| `extensions.py` | Flask 확장 및 싱글톤 서비스 |
| `config.py` | 환경별 설정 |
| `types.py` | 타입 힌트 정의 |

## 레이어 호출 규칙

```
Blueprint -> Service -> Repository -> Model
```

| 호출 방향 | 허용 | 비고 |
|----------|------|------|
| Blueprint -> Service | O | |
| Blueprint -> Repository | X | 금지 |
| Service -> Repository | O | |
| Service -> Service | O | 순환 참조 주의 |
| Repository -> Model | O | |

## Service Layer (Facade 패턴)

```
services/
├── contract/                        # ContractService Facade
│   ├── __init__.py                  # 외부 인터페이스
│   ├── contract_core_service.py     # 조회/검색
│   ├── contract_workflow_service.py # 승인/거절/종료
│   └── contract_settings_service.py # 설정/로그
├── sync/                            # SyncService Facade
│   ├── __init__.py
│   ├── sync_service.py
│   ├── sync_basic_service.py
│   └── sync_relation_service.py
├── employee/                        # EmployeeService Facade (Phase 28)
│   ├── __init__.py                  # 외부 인터페이스
│   ├── employee_core_service.py     # 직원 조회/검색
│   └── employee_relation_service.py # 관계형 데이터 관리
├── validation/                      # 검증 서비스 (Phase 28)
│   ├── __init__.py
│   └── profile_validator.py         # 프로필 유효성 검증
├── audit_service.py                 # 감사 로깅 (Phase 31: Repository 패턴)
└── base/                            # 공통 기반
    ├── service_result.py            # ServiceResult 패턴
    └── generic_relation_crud.py     # Generic CRUD (CLAUDE.md 예외 문서화)
```

## Blueprint 구조

```
blueprints/
├── employees/                # 직원 관리 (9개 파일)
│   ├── __init__.py           # Blueprint 정의
│   ├── routes.py             # 공통 라우트
│   ├── list_routes.py        # 목록 조회
│   ├── mutation_routes.py    # 생성/수정/삭제
│   ├── detail_routes.py      # 상세 조회
│   ├── files.py              # 파일 업로드 API
│   ├── form_extractors.py    # 폼 데이터 추출
│   ├── relation_updaters.py  # 관계 데이터 업데이트
│   └── helpers.py            # 헬퍼 함수
├── corporate_settings/       # 법인 설정 API (7개 파일)
├── platform/                 # 플랫폼 관리 (5개 파일)
├── sync/                     # 동기화 API (4개 파일)
├── admin/                    # 관리자 기능
│   ├── __init__.py
│   ├── organization.py       # 조직 관리
│   └── audit.py              # 감사 대시보드
├── account/                  # 계정 관리
├── personal/                 # 개인 계정 페이지
├── profile/                  # 프로필 관리
└── 기타 단일 파일 Blueprint
```

## 주요 상수 (SSOT)

**상태 상수** (`constants/status.py`):
```python
from app.constants.status import ContractStatus, EmployeeStatus, AccountStatus

ContractStatus.PENDING              # 'pending' - 승인 대기
ContractStatus.APPROVED             # 'approved' - 승인됨
ContractStatus.REJECTED             # 'rejected' - 거절됨
ContractStatus.TERMINATED           # 'terminated' - 종료됨
ContractStatus.TERMINATION_REQUESTED  # 'termination_requested' - 종료 대기
ContractStatus.ACTIVE_STATUSES      # ['approved', 'termination_requested']

EmployeeStatus.ACTIVE               # 'active' - 재직 중
EmployeeStatus.PENDING_INFO         # 'pending_info' - 정보 입력 대기
EmployeeStatus.RESIGNED             # 'resigned' - 퇴사

AccountStatus.NONE                  # 'none' - 계정 없음
AccountStatus.REQUESTED             # 'requested' - 요청됨
AccountStatus.PENDING               # 'pending' - 대기 중
```

**폼 옵션** (`constants/field_options.py`):
- 선택형 필드 옵션 중앙 관리
- 레거시 매핑 (`LEGACY_MAP`)

**필드 메타데이터** (`constants/field_registry/`):
- 필드 순서, 가시성, 정규화

## 주요 서비스

| 서비스 | 위치 | 역할 |
|--------|------|------|
| `employee_service` | `services/employee_service.py` | 직원 CRUD (레거시, Facade 위임) |
| `employee_core_service` | `services/employee/` | 직원 조회/검색 |
| `employee_relation_service` | `services/employee/` | 직원 관계형 데이터 |
| `contract_service` | `services/contract/` | 계약 관리 Facade |
| `sync_service` | `services/sync/` | 동기화 Facade |
| `personal_service` | `services/personal_service.py` | 개인 프로필 CRUD |
| `profile_relation_service` | `services/profile_relation_service.py` | 관계형 데이터 SSOT |
| `termination_service` | `services/termination_service.py` | 퇴사 처리 |
| `profile_validator` | `services/validation/` | 프로필 유효성 검증 |

## 규칙

- Blueprint에서 Repository 직접 호출 금지
- 트랜잭션 래핑: `atomic_transaction()` 사용
- 서비스 반환: `ServiceResult` 패턴 사용
- 모델 직렬화: `to_dict()`, `from_dict()` 필수
- 상태 값: `constants/status.py` 상수 사용

## CLAUDE.md 규칙 예외

| 파일 | 예외 사항 | 사유 |
|------|----------|------|
| `base/generic_relation_crud.py` | `commit=True` 기본값 | relation_updaters에서 `atomic_transaction()` + `commit=False`로 호출 (55건 검증) |
| `base/generic_relation_crud.py` | `Model.query` 직접 사용 | Generic 패턴 특성상 Repository DI 복잡 |

## Phase 31 Cleanup (2026-01-06)

**삭제된 파일:**
- `utils/data_validator.py` (~500줄) - 미사용
- `utils/init_system_settings.py` (~170줄) - 미사용

**정리된 코드:**
- `audit_service.py`: 미사용 데코레이터 3개 제거 (track_employee_access, track_contract_access, track_sync_operation)
