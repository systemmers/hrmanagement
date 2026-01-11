# shared/ 디렉토리 가이드

도메인 간 공유되는 자원들을 모아놓은 디렉토리

## 디렉토리 구조

```
shared/
├── base/             # 기반 클래스 및 패턴
├── constants/        # 상수 정의 (SSOT)
├── repositories/     # 기반 Repository
├── services/         # 공유 서비스
├── utils/            # 유틸리티
├── adapters/         # 외부 서비스 어댑터
└── blueprints/       # 공유 Blueprint
```

## base/ - 기반 클래스

| 파일 | 역할 | 사용처 |
|------|------|--------|
| `service_result.py` | ServiceResult 패턴 | 모든 Service 반환값 |
| `generic_relation_crud.py` | Generic CRUD | 관계형 데이터 처리 |
| `relation_updater.py` | RelationUpdater 기반 | Blueprint 관계 업데이트 |
| `relation_configs.py` | 관계형 설정 | RelationUpdater 설정 |
| `history_service.py` | 히스토리 서비스 | 변경 이력 추적 |
| `dict_serializable_mixin.py` | 직렬화 믹스인 (2026-01-10) | 모델 to_dict/from_dict |

**ServiceResult 패턴**:
```python
from app.shared.base.service_result import ServiceResult

def create_employee(data):
    try:
        employee = Employee(**data)
        db.session.add(employee)
        db.session.commit()
        return ServiceResult.success(employee)
    except Exception as e:
        return ServiceResult.failure(str(e))

# 사용
result = create_employee(data)
if result.is_success:
    employee = result.data
else:
    error = result.error
```

## constants/ - 상수 정의 (SSOT)

| 파일 | 역할 |
|------|------|
| `field_options.py` | 폼 선택 옵션 (Option namedtuple) |
| `field_registry/` | 필드 메타데이터 (순서, 가시성) |
| `status.py` | 상태 상수 (ContractStatus, EmployeeStatus) |
| `messages.py` | 메시지 상수 |
| `session_keys.py` | 세션 키 상수 |
| `sync_fields.py` | 동기화 필드 설정 |
| `system_config.py` | 시스템 설정 |

**상태 상수 사용**:
```python
from app.shared.constants.status import ContractStatus, EmployeeStatus

# 계약 상태
if contract.status == ContractStatus.APPROVED:
    pass

# 직원 상태
if employee.status == EmployeeStatus.ACTIVE:
    pass

# 활성 상태 목록
ContractStatus.ACTIVE_STATUSES  # ['approved', 'termination_requested']
```

**폼 옵션 사용**:
```python
from app.shared.constants.field_options import FieldOptions

# 옵션 목록 조회
FieldOptions.GENDER  # [Option('남', '남성'), Option('여', '여성')]

# 레이블 조회 (레거시 코드 자동 변환)
FieldOptions.get_label_with_legacy(FieldOptions.GENDER, 'male')  # '남성'
```

## repositories/ - 기반 Repository

```
repositories/
├── __init__.py           # BaseRepository export
├── base_repository.py    # BaseRepository[T] 제네릭
└── mixins/
    ├── __init__.py
    └── tenant_filter.py  # 테넌트 필터 믹스인
```

**BaseRepository 사용**:
```python
from app.shared.repositories import BaseRepository
from app.domains.employee.models import Employee

class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

    # 커스텀 메서드 추가
    def find_by_company(self, company_id):
        return self.model.query.filter_by(company_id=company_id).all()
```

**주요 메서드**:
| 메서드 | 설명 |
|--------|------|
| `find_by_id(id)` | ID로 조회 |
| `find_all()` | 전체 조회 |
| `create(data, commit)` | 생성 |
| `update(id, data, commit)` | 수정 |
| `delete(id, commit)` | 삭제 |

## services/ - 공유 서비스

```
services/
├── __init__.py
├── ai/                        # AI 서비스
│   ├── __init__.py
│   ├── base.py                # AI 프로바이더 기반
│   ├── gemini_provider.py     # Gemini API
│   ├── local_llama_provider.py
│   ├── document_ai_provider.py
│   ├── vision_ocr.py          # OCR
│   └── prompts.py             # 프롬프트 템플릿
├── ai_service.py              # AI 서비스 인터페이스
├── file_storage_service.py    # 파일 저장
├── event_listeners.py         # 이벤트 리스너
└── validation/
    ├── __init__.py
    └── profile_validator.py   # 프로필 검증
```

**AI 서비스 사용**:
```python
from app.shared.services.ai_service import ai_service

# 문서 분석
result = ai_service.analyze_document(file_path)

# OCR
text = ai_service.extract_text_from_image(image_path)
```

**파일 저장 서비스**:
```python
from app.shared.services.file_storage_service import file_storage_service

# 파일 저장
path = file_storage_service.save_file(file, 'employees/photos')

# 파일 삭제
file_storage_service.delete_file(path)
```

## utils/ - 유틸리티

```
utils/
├── __init__.py
├── decorators.py          # 데코레이터 (핵심)
├── transaction.py         # 트랜잭션 관리 (SSOT)
├── tenant.py              # 테넌트 유틸리티
├── corporate_helpers.py   # 법인 헬퍼
├── personal_helpers.py    # 개인 헬퍼
├── date_helpers.py        # 날짜 헬퍼
├── file_helpers.py        # 파일 헬퍼
├── form_helpers.py        # 폼 헬퍼
├── object_helpers.py      # 객체 헬퍼
├── api_helpers.py         # API 헬퍼
├── contract_helpers.py    # 계약 헬퍼
├── template_helpers.py    # 템플릿 헬퍼
├── employee_number.py     # 사번 생성
├── rrn_parser.py          # 주민번호 파서
├── context_processors.py  # 컨텍스트 프로세서
└── exceptions.py          # 커스텀 예외
```

**데코레이터 (decorators.py)**:
```python
from app.shared.utils.decorators import (
    login_required,
    corporate_login_required,
    personal_login_required,
    corporate_admin_required,
    api_login_required
)

@app.route('/employees')
@corporate_login_required
def employee_list():
    pass

@app.route('/api/employees')
@api_login_required
def api_employee_list():
    pass
```

**트랜잭션 관리 (transaction.py)** - SSOT:
```python
from app.shared.utils.transaction import atomic_transaction, transactional

# 컨텍스트 매니저 방식 (권장)
with atomic_transaction():
    service.delete_all(id, commit=False)
    service.create(data, commit=False)
    # 성공 시 자동 commit, 실패 시 자동 rollback

# 데코레이터 방식
@transactional
def update_all(id, data):
    service.delete_all(id, commit=False)
    service.create(data, commit=False)
```

## adapters/ - 외부 서비스 어댑터

```
adapters/
├── __init__.py
└── profile_adapter.py    # 프로필 어댑터
```

외부 시스템과의 통합을 위한 어댑터 패턴

## blueprints/ - 공유 Blueprint

```
blueprints/
├── __init__.py
└── api.py               # 공통 API Blueprint
```

도메인에 속하지 않는 공통 API 라우트

## Import 패턴

```python
# 기반 클래스
from app.shared.base.service_result import ServiceResult
from app.shared.repositories import BaseRepository

# 상수
from app.shared.constants.status import ContractStatus
from app.shared.constants.field_options import FieldOptions

# 유틸리티
from app.shared.utils.decorators import login_required
from app.shared.utils.transaction import atomic_transaction

# 서비스
from app.shared.services.ai_service import ai_service
from app.shared.services.file_storage_service import file_storage_service
```

## 규칙

1. **SSOT 준수**: 상수는 반드시 `constants/`에서 정의
2. **트랜잭션**: `atomic_transaction()` 사용 필수
3. **데코레이터**: 인증은 `decorators.py` 사용
4. **도메인 독립**: shared는 특정 도메인에 의존하지 않음
5. **직렬화**: `DictSerializableMixin` 사용 권장

**DictSerializableMixin 사용**:
```python
from app.shared.base.dict_serializable_mixin import DictSerializableMixin

class Attachment(db.Model, DictSerializableMixin):
    # to_dict(), from_dict() 자동 제공
    pass
```

## Migration History

**Phase 1 완료 (2026-01-07)**
- 공유 자원 구조화
- base/, constants/, repositories/, services/, utils/ 분리

**Phase 2 완료 (2026-01-10)**
- DictSerializableMixin을 shared/base로 이동
- 도메인 간 공유 믹스인 중앙화
