# domains/ 디렉토리 가이드

도메인 중심 아키텍처(Domain-Driven Design)를 적용한 비즈니스 로직 패키지

## 도메인 목록 (8개)

| 도메인 | 역할 | 핵심 모델 |
|--------|------|-----------|
| `employee/` | 직원 관리 | Employee, Education, Career 등 |
| `contract/` | 계약 관리 | PersonCorporateContract |
| `company/` | 법인 관리 | Company, Organization |
| `user/` | 사용자 관리 | User, PersonalProfile |
| `platform/` | 플랫폼 관리 | SystemSetting, AuditLog |
| `sync/` | 동기화 관리 | SyncLog |
| `attachment/` | 첨부파일 관리 (2026-01-10) | Attachment |
| `businesscard/` | 명함 관리 (2026-01-09) | Attachment 재사용 |

## 도메인 구조 (공통 패턴)

```
{domain}/
├── __init__.py           # 외부 인터페이스 (re-export)
├── models/
│   ├── __init__.py       # 모델 export
│   └── {model}.py        # SQLAlchemy 모델
├── repositories/
│   ├── __init__.py       # Repository 인스턴스 export
│   └── {model}_repository.py
├── services/
│   ├── __init__.py       # Service 인스턴스 export
│   └── {domain}_service.py
└── blueprints/
    ├── __init__.py       # Blueprint 정의
    └── routes.py         # URL 라우팅
```

## 도메인별 상세

### employee/ (직원 도메인)
```
employee/
├── __init__.py           # 65개+ 파일 통합 export
├── models/               # 20개 모델
│   ├── employee.py       # 핵심 모델
│   ├── education.py
│   ├── career.py
│   ├── family_member.py
│   ├── certificate.py
│   ├── language.py
│   ├── military_service.py
│   ├── training.py
│   ├── award.py
│   ├── evaluation.py
│   ├── insurance.py
│   ├── benefit.py
│   ├── salary.py
│   ├── salary_history.py
│   ├── salary_payment.py
│   ├── promotion.py
│   ├── attendance.py
│   ├── asset.py
│   ├── attachment.py
│   └── project_participation.py
├── repositories/         # 20개 Repository
├── services/
│   ├── employee_service.py           # 직원 CRUD
│   ├── employee_core_service.py      # 조회/검색
│   ├── employee_relation_service.py  # 관계형 데이터
│   ├── profile_relation_service.py   # 관계형 SSOT
│   ├── employee_account_service.py   # 계정 관리
│   └── attachment_service.py         # 첨부파일
└── blueprints/
    ├── __init__.py
    ├── routes.py
    ├── list_routes.py
    ├── mutation_routes.py
    ├── detail_routes.py
    ├── files.py
    ├── file_handlers.py
    ├── form_extractors.py
    ├── relation_updaters.py
    └── helpers.py
```

### contract/ (계약 도메인) - Facade 패턴
```
contract/
├── __init__.py
├── models/
│   ├── person_contract.py      # 계약 모델
│   ├── data_sharing_settings.py
│   └── sync_log.py
├── repositories/
│   └── person_contract_repository.py
├── services/
│   ├── contract_service.py           # Facade (외부 인터페이스)
│   ├── contract_core_service.py      # 조회/검색
│   ├── contract_workflow_service.py  # 승인/거절/종료
│   ├── contract_settings_service.py  # 설정/로그
│   └── contract_filter_service.py    # 필터링
└── blueprints/
    └── contracts.py
```

### company/ (법인 도메인)
```
company/
├── __init__.py
├── models/
│   ├── company.py
│   ├── organization.py
│   ├── classification_option.py
│   ├── company_settings.py
│   ├── company_document.py
│   ├── company_visibility_settings.py
│   ├── number_category.py
│   ├── number_registry.py
│   ├── ip_range.py
│   └── ip_assignment.py
├── repositories/
│   ├── company_repository.py
│   ├── organization_repository.py
│   ├── classification_repository.py
│   ├── company_settings_repository.py
│   ├── company_document_repository.py
│   ├── company_visibility_repository.py
│   ├── number_category_repository.py
│   └── data_sharing_settings_repository.py
├── services/
│   ├── company_service.py
│   ├── organization_service.py
│   └── corporate_settings_service.py
└── blueprints/
    ├── __init__.py
    ├── corporate.py
    ├── admin_organization.py
    └── settings/
        ├── __init__.py
        ├── classifications_api.py
        ├── documents_api.py
        ├── visibility_api.py
        ├── number_categories_api.py
        ├── settings_api.py
        └── helpers.py
```

### user/ (사용자 도메인)
```
user/
├── __init__.py
├── models/
│   ├── user.py
│   ├── notification.py
│   ├── corporate_admin_profile.py
│   └── personal/
│       ├── __init__.py
│       └── profile.py
├── repositories/
│   ├── user_repository.py
│   ├── notification_repository.py
│   ├── personal_profile_repository.py
│   └── corporate_admin_profile_repository.py
├── services/
│   ├── user_service.py
│   ├── personal_service.py
│   ├── notification_service.py
│   ├── user_employee_link_service.py
│   └── corporate_admin_profile_service.py
└── blueprints/
    ├── __init__.py
    ├── auth.py
    ├── mypage.py
    ├── notifications.py
    ├── account/
    │   ├── __init__.py
    │   ├── routes.py
    │   └── helpers.py
    ├── personal/
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── form_extractors.py
    │   └── relation_updaters.py
    └── profile/
        ├── __init__.py
        ├── routes.py
        └── decorators.py
```

### platform/ (플랫폼 도메인)
```
platform/
├── __init__.py
├── models/
│   ├── system_setting.py
│   └── audit_log.py
├── repositories/
│   ├── system_setting_repository.py
│   └── audit_log_repository.py
├── services/
│   ├── platform_service.py
│   ├── audit_service.py
│   └── system_setting_service.py
└── blueprints/
    ├── __init__.py
    ├── main.py
    ├── ai_test.py
    ├── audit_api.py
    ├── dashboard.py
    ├── companies.py
    ├── users.py
    └── settings.py
```

### sync/ (동기화 도메인) - Facade 패턴
```
sync/
├── __init__.py
├── models/
│   └── (contract 도메인의 SyncLog 참조)
├── repositories/
│   └── sync_log_repository.py
├── services/
│   ├── sync_service.py               # Facade (외부 인터페이스)
│   ├── sync_basic_service.py         # 기본 동기화
│   ├── sync_relation_service.py      # 관계형 동기화
│   └── termination_service.py        # 퇴사 처리
└── blueprints/
    ├── __init__.py
    ├── sync_routes.py
    ├── contract_routes.py
    └── termination_routes.py
```

### attachment/ (첨부파일 도메인) - 2026-01-10 신규
```
attachment/
├── __init__.py
├── models/
│   └── attachment.py                 # Attachment 모델 (독립 도메인)
├── repositories/
│   └── attachment_repository.py      # 첨부파일 CRUD
├── services/
│   └── attachment_service.py         # 파일 업로드/삭제/조회
└── blueprints/
    └── routes.py                     # /api/attachments/* API
```

**API 엔드포인트**:
- `POST /api/attachments` - 파일 업로드
- `DELETE /api/attachments/<id>` - 파일 삭제
- `GET /api/attachments/<owner_type>/<owner_id>` - 파일 목록 조회

**Attachment 모델 특징**:
- `owner_type`: 소유자 타입 (employee, profile, contract 등)
- `owner_id`: 소유자 ID
- `category`: 카테고리 (document, photo, businesscard 등)
- 다형성(Polymorphic) 관계 지원

### businesscard/ (명함 도메인) - 2026-01-09 신규
```
businesscard/
├── __init__.py
├── models/
│   └── (attachment 도메인의 Attachment 재사용)
├── repositories/
│   └── businesscard_repository.py    # 명함 조회/삭제
├── services/
│   └── businesscard_service.py       # 명함 업로드/삭제
└── blueprints/
    └── routes.py                     # /api/businesscard/* API
```

**API 엔드포인트**:
- `POST /api/businesscard/employee/<id>` - 명함 업로드
- `DELETE /api/businesscard/employee/<id>/<side>` - 명함 삭제
- `GET /api/businesscard/employee/<id>` - 명함 조회

**특징**:
- Attachment 모델 재사용 (category='businesscard')
- 앞면(front)/뒷면(back) 구분

## Import 패턴

```python
# 도메인 __init__.py를 통한 import (권장)
from app.domains.employee import Employee, employee_service
from app.domains.company import Company, Organization
from app.domains.contract import contract_service
from app.domains.user import User, user_service
from app.domains.attachment import Attachment, attachment_service
from app.domains.businesscard import businesscard_service

# 하위 모듈 직접 import
from app.domains.employee.models import Employee, Education
from app.domains.employee.services import employee_service, profile_relation_service
from app.domains.employee.repositories import employee_repository
from app.domains.attachment.models import Attachment
from app.domains.attachment.services import attachment_service
```

## Facade 패턴 도메인

`contract/`와 `sync/` 도메인은 Facade 패턴 적용:

```python
# contract/services/__init__.py
from .contract_service import contract_service  # Facade

# Facade 사용 (권장)
from app.domains.contract.services import contract_service
contract_service.approve_contract(contract_id)  # workflow 위임
contract_service.search_contracts(filters)       # core 위임

# 내부 서비스 직접 사용 (도메인 내부에서만)
from app.domains.contract.services.contract_core_service import contract_core_service
```

## 도메인 간 참조 규칙

| 참조 방향 | 허용 | 비고 |
|----------|------|------|
| employee -> contract | O | 계약 정보 조회 |
| contract -> employee | O | 직원 정보 조회 |
| user -> employee | O | 직원 계정 연결 |
| company -> organization | O | 조직 구조 |
| sync -> employee, contract | O | 동기화 대상 |
| platform -> all | O | 관리 기능 |
| attachment -> (독립) | - | 다형성 관계로 독립적 |
| businesscard -> attachment | O | Attachment 모델 재사용 |
| employee -> attachment | O | 직원 첨부파일 |
| user -> attachment | O | 프로필 첨부파일 |

**순환 참조 주의**: Service 간 참조 시 import 순서 고려

## 규칙

1. **도메인 경계 존중**: 다른 도메인의 Repository 직접 호출 금지
2. **Service 레이어 경유**: 도메인 간 통신은 Service를 통해
3. **Model 공유 허용**: Model은 도메인 간 직접 import 가능
4. **Blueprint 독립성**: 각 도메인의 Blueprint는 독립적으로 동작
5. **Attachment 다형성**: owner_type/owner_id로 소유자 참조

## Migration History

**Phase 1 완료 (2026-01-07)**
- 도메인 중심 아키텍처 마이그레이션
- 레거시 래퍼 파일 제거

**Phase 31 완료 (2026-01-10)**
- Attachment 독립 도메인 생성
- owner_type/owner_id 다형성 관계 적용

**BusinessCard 도메인 추가 (2026-01-09)**
- 명함 관리 기능 추가
- Attachment 모델 재사용 (category='businesscard')
