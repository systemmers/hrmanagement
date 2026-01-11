# app/ 디렉토리 가이드

Flask 애플리케이션의 핵심 모듈들이 위치한 디렉토리입니다.

## 디렉토리 구조 (도메인 중심 아키텍처)

```
app/
├── domains/              # 도메인별 패키지 (8개)
│   ├── employee/         # 직원 도메인 (~65개 파일)
│   ├── contract/         # 계약 도메인
│   ├── company/          # 법인 도메인
│   ├── user/             # 사용자 도메인
│   ├── platform/         # 플랫폼 도메인
│   ├── sync/             # 동기화 도메인
│   ├── attachment/       # 첨부파일 도메인 (2026-01-10 신규)
│   └── businesscard/     # 명함 도메인 (2026-01-09 신규)
├── shared/               # 공유 자원
│   ├── base/             # 기반 클래스
│   ├── constants/        # 상수 (SSOT)
│   ├── repositories/     # BaseRepository
│   ├── services/         # 공유 서비스
│   ├── utils/            # 유틸리티
│   └── adapters/         # 외부 서비스 어댑터
├── templates/            # Jinja2 템플릿
├── static/               # 정적 파일 (CSS, JS, 이미지)
├── __init__.py           # Flask 앱 팩토리
├── extensions.py         # Flask 확장
└── config.py             # 환경별 설정
```

## 도메인 구조 (각 도메인 공통)

```
domains/{domain}/
├── __init__.py           # 도메인 초기화 + 외부 인터페이스
├── models/               # SQLAlchemy 모델
│   └── __init__.py       # 모델 re-export
├── repositories/         # 데이터 접근 계층
│   └── __init__.py       # Repository 인스턴스 export
├── services/             # 비즈니스 로직
│   └── __init__.py       # Service 인스턴스 export
└── blueprints/           # URL 라우팅
    └── __init__.py       # Blueprint 정의
```

## 핵심 파일

| 파일 | 설명 |
|------|------|
| `__init__.py` | Flask 앱 팩토리 (`create_app()`) |
| `extensions.py` | Flask 확장 초기화 |
| `config.py` | 환경별 설정 (Development, Production, Testing) |

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

## 도메인별 주요 파일

### employee/ (직원 도메인)
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `employee.py` | Employee 모델 (핵심) |
| Model | `education.py`, `career.py` 등 | 관계형 모델 (20개) |
| Repository | `employee_repository.py` | 직원 CRUD |
| Service | `employee_service.py` | 직원 비즈니스 로직 |
| Service | `profile_relation_service.py` | 관계형 데이터 SSOT |
| Blueprint | `list_routes.py`, `mutation_routes.py` | 라우팅 |

### contract/ (계약 도메인) - Facade 패턴
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `person_contract.py` | 계약 모델 |
| Service | `contract_service.py` | Facade (외부 인터페이스) |
| Service | `contract_core_service.py` | 조회/검색 |
| Service | `contract_workflow_service.py` | 승인/거절/종료 |
| Service | `contract_settings_service.py` | 설정/로그 |

### company/ (법인 도메인)
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `company.py`, `organization.py` | 법인/조직 모델 |
| Service | `company_service.py` | 법인 CRUD |
| Service | `organization_service.py` | 조직 구조 관리 |
| Service | `corporate_settings_service.py` | 법인 설정 |
| Blueprint | `settings/*.py` | 설정 API (7개 파일) |

### user/ (사용자 도메인)
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `user.py` | 사용자 모델 |
| Model | `personal/profile.py` | 개인 프로필 |
| Service | `user_service.py` | 사용자 관리 |
| Service | `personal_service.py` | 개인 프로필 CRUD |
| Blueprint | `auth.py`, `mypage.py` | 인증, 마이페이지 |

### platform/ (플랫폼 도메인)
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `system_setting.py`, `audit_log.py` | 시스템 모델 |
| Service | `platform_service.py` | 플랫폼 관리 |
| Service | `audit_service.py` | 감사 로깅 |
| Blueprint | `main.py`, `audit_api.py` | 플랫폼 라우팅 |

### sync/ (동기화 도메인) - Facade 패턴
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `sync_log.py` | 동기화 로그 |
| Service | `sync_service.py` | Facade (외부 인터페이스) |
| Service | `sync_basic_service.py` | 기본 동기화 |
| Service | `sync_relation_service.py` | 관계형 동기화 |
| Service | `termination_service.py` | 퇴사 처리 |

### attachment/ (첨부파일 도메인) - 2026-01-10 신규
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `attachment.py` | Attachment 모델 (다형성) |
| Repository | `attachment_repository.py` | 첨부파일 CRUD |
| Service | `attachment_service.py` | 파일 업로드/삭제/조회 |
| Blueprint | `routes.py` | `/api/attachments/*` API |

**API 엔드포인트**:
- `POST /api/attachments` - 파일 업로드
- `DELETE /api/attachments/<id>` - 파일 삭제
- `GET /api/attachments/<owner_type>/<owner_id>` - 파일 목록 조회

**Import 패턴**:
```python
from app.domains.attachment.models import Attachment
from app.domains.attachment.services import attachment_service
```

### businesscard/ (명함 도메인) - 2026-01-09 신규
| 구분 | 파일 | 역할 |
|------|------|------|
| Model | `Attachment` 재사용 | 명함 첨부파일 (category 기반) |
| Repository | `businesscard_repository.py` | 명함 첨부파일 조회/삭제 |
| Service | `businesscard_service.py` | 명함 업로드/삭제 비즈니스 로직 |
| Blueprint | `routes.py` | `/api/businesscard/*` API |

**API 엔드포인트**:
- `POST /api/businesscard/employee/<id>` - 명함 업로드
- `DELETE /api/businesscard/employee/<id>/<side>` - 명함 삭제
- `GET /api/businesscard/employee/<id>` - 명함 조회

**Import 패턴**:
```python
from app.domains.businesscard.services import businesscard_service
from app.domains.businesscard.repositories import businesscard_repository
```

## 공유 자원 (shared/)

```
shared/
├── base/                          # 기반 클래스
│   ├── service_result.py          # ServiceResult 패턴
│   ├── generic_relation_crud.py   # Generic CRUD
│   ├── relation_updater.py        # RelationUpdater 기반
│   ├── relation_configs.py        # 관계형 설정
│   ├── history_service.py         # 히스토리 서비스
│   └── dict_serializable_mixin.py # 직렬화 믹스인 (2026-01-10)
├── constants/                     # 상수 (SSOT)
│   ├── field_options.py           # 폼 선택 옵션
│   ├── field_registry/            # 필드 메타데이터
│   ├── status.py                  # 상태 상수
│   ├── messages.py                # 메시지 상수
│   └── session_keys.py            # 세션 키 상수
├── repositories/                  # 기반 Repository
│   ├── base_repository.py         # BaseRepository[T]
│   └── mixins/tenant_filter.py    # 테넌트 필터 믹스인
├── services/                      # 공유 서비스
│   ├── ai/                        # AI 서비스
│   │   ├── gemini_provider.py
│   │   ├── local_llama_provider.py
│   │   └── document_ai_provider.py
│   ├── ai_service.py              # AI 서비스 인터페이스
│   ├── file_storage_service.py    # 파일 저장
│   ├── event_listeners.py         # 이벤트 리스너
│   └── validation/                # 검증 서비스
│       └── profile_validator.py
├── utils/                         # 유틸리티
│   ├── decorators.py              # 데코레이터 (login_required 등)
│   ├── transaction.py             # 트랜잭션 관리 (SSOT)
│   ├── tenant.py                  # 테넌트 유틸리티
│   └── helpers.py                 # 각종 헬퍼
├── adapters/                      # 외부 서비스 어댑터
│   └── profile_adapter.py
└── blueprints/                    # 공유 Blueprint
    └── api.py                     # 공통 API
```

## 주요 상수 (SSOT)

**상태 상수** (`shared/constants/status.py`):
```python
from app.shared.constants.status import ContractStatus, EmployeeStatus, AccountStatus

ContractStatus.PENDING              # 'pending'
ContractStatus.APPROVED             # 'approved'
ContractStatus.ACTIVE_STATUSES      # ['approved', 'termination_requested']

EmployeeStatus.ACTIVE               # 'active'
EmployeeStatus.RESIGNED             # 'resigned'
```

**폼 옵션** (`shared/constants/field_options.py`):
```python
from app.shared.constants.field_options import FieldOptions

FieldOptions.GENDER  # [Option('남', '남성'), Option('여', '여성')]
FieldOptions.get_label_with_legacy(FieldOptions.GENDER, 'male')  # '남성'
```

## Import 패턴

```python
# 도메인에서 import (권장)
from app.domains.employee.models import Employee
from app.domains.employee.services import employee_service
from app.domains.company.models import Company, Organization
from app.domains.contract.services import contract_service

# 공유 자원 import
from app.shared.repositories import BaseRepository
from app.shared.utils.decorators import login_required
from app.shared.utils.transaction import atomic_transaction
from app.shared.constants.status import ContractStatus
```

## 규칙

- Blueprint에서 Repository 직접 호출 금지
- 트랜잭션 래핑: `atomic_transaction()` 사용 (SSOT)
- 서비스 반환: `ServiceResult` 패턴 사용
- 모델 직렬화: `to_dict()`, `from_dict()` 필수
- 상태 값: `shared/constants/status.py` 상수 사용

## CLAUDE.md 규칙 예외

| 파일 | 예외 사항 | 사유 |
|------|----------|------|
| `shared/base/generic_relation_crud.py` | `commit=True` 기본값 | relation_updaters에서 `atomic_transaction()` + `commit=False`로 호출 |
| `shared/base/generic_relation_crud.py` | `Model.query` 직접 사용 | Generic 패턴 특성상 Repository DI 복잡 |

## Migration History

**Phase 1 완료 (2026-01-07)**
- 레거시 래퍼 파일 제거: `app/models/__init__.py`, `app/repositories/__init__.py`, `app/services/__init__.py`
- Blueprint 도메인 이동: admin, profile, personal 등
- 공유 자원 구조화: `app/shared/` 생성
- Import 경로 정규화: 167개 파일 업데이트

**BusinessCard 도메인 추가 (2026-01-09)**
- 명함 관리 기능 추가
- Attachment 모델 재사용 (category='businesscard')

**Phase 31 완료 (2026-01-10)**
- Attachment 독립 도메인 생성
- owner_type/owner_id 다형성 관계 적용
- DictSerializableMixin을 shared/base로 이동
