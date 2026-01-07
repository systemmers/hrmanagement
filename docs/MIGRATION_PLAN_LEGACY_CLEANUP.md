# 레거시 파일 마이그레이션 계획

> **생성일**: 2026-01-07
> **목적**: 레거시 래퍼 파일 제거 및 도메인 구조 완성

---

## 현재 상태 분석

### 1. 래퍼 파일 현황 (삭제 대상)

#### app/services/ 래퍼 파일 (16개)
| 파일 | 크기 | 도메인 위치 |
|------|------|-------------|
| ai_service.py | 231B | shared/services/ai_service.py |
| audit_service.py | 458B | domains/platform/services/ |
| company_service.py | 334B | domains/company/services/ |
| contract_filter_service.py | 438B | domains/contract/services/ |
| contract_service.py | 754B | domains/contract/services/ |
| corporate_admin_profile_service.py | 436B | domains/user/services/ |
| corporate_settings_service.py | 409B | domains/company/services/ |
| notification_service.py | 363B | domains/user/services/ |
| organization_service.py | 369B | domains/company/services/ |
| personal_service.py | 335B | domains/user/services/ |
| platform_service.py | 343B | domains/platform/services/ |
| sync_service.py | 377B | domains/sync/services/ |
| system_setting_service.py | 382B | domains/platform/services/ |
| termination_service.py | 360B | domains/sync/services/ |
| user_employee_link_service.py | 401B | domains/user/services/ |
| user_service.py | 307B | domains/user/services/ |

#### app/services/ 서브디렉토리 래퍼 (2개)
| 디렉토리 | 파일 수 | 도메인 위치 |
|----------|---------|-------------|
| contract/ | 4개 | domains/contract/services/ |
| sync/ | 1개 | domains/sync/services/ |
| ai/ | 1개 | shared/services/ai/ |

#### app/repositories/ 래퍼 파일 (7개)
| 파일 | 크기 | 도메인 위치 |
|------|------|-------------|
| company_repository.py | 363B | domains/company/repositories/ |
| data_sharing_settings_repository.py | 455B | domains/company/repositories/ |
| organization_repository.py | 398B | domains/company/repositories/ |
| person_contract_repository.py | 483B | domains/contract/repositories/ |
| personal_profile_repository.py | 515B | domains/user/repositories/ |
| sync_log_repository.py | 361B | domains/sync/repositories/ |
| user_repository.py | 434B | domains/user/repositories/ |

#### app/repositories/ 서브디렉토리 래퍼 (1개)
| 디렉토리 | 파일 수 | 도메인 위치 |
|----------|---------|-------------|
| contract/ | 1개 | domains/contract/repositories/ |

---

### 2. 공유 모듈 (유지 필요)

#### 유지해야 할 파일
| 파일 | 크기 | 사유 |
|------|------|------|
| app/services/__init__.py | 3KB | 메인 export 허브 |
| app/repositories/__init__.py | 2.6KB | 메인 export 허브 |
| app/repositories/base_repository.py | 14.5KB | cross-domain 기반 클래스 |
| app/repositories/mixins/tenant_filter.py | 3.4KB | cross-domain mixin |
| app/services/validation/profile_validator.py | 9KB | cross-domain 검증 |
| app/services/event_listeners.py | 559B | shared로 re-export |
| app/services/file_storage_service.py | 961B | shared로 re-export |
| app/models/__init__.py | 2.5KB | 메인 export 허브 |

#### 공유 Blueprint (유지)
| 파일 | 크기 | 사유 |
|------|------|------|
| app/blueprints/__init__.py | 2.6KB | Blueprint 등록 |
| app/blueprints/main.py | 4.8KB | 메인 라우트 |
| app/blueprints/api.py | 3KB | API 라우트 |
| app/blueprints/admin/ | 8KB | cross-domain 관리 |
| app/blueprints/profile/ | 25KB | cross-domain 프로필 |
| app/blueprints/ai_test.py | 4.8KB | AI 테스트 |
| app/blueprints/audit.py | 10KB | 감사 UI |

---

## 마이그레이션 전략

### Option A: 래퍼 유지 (하위 호환성)
- **장점**: 기존 코드 변경 없음
- **단점**: 중복 파일 유지
- **권장**: 외부 의존성이 있는 경우

### Option B: 래퍼 제거 + Import 경로 업데이트 (**권장**)
- **장점**: 깔끔한 구조, 중복 제거
- **단점**: 모든 import 경로 수정 필요
- **권장**: 내부 프로젝트, 리팩토링 가능 시

### Option C: __init__.py 통합
- **장점**: 파일 수 최소화
- **단점**: __init__.py 비대화
- **권장**: 작은 프로젝트

---

## Option B 실행 계획

### Phase 1: Import 경로 분석 (~30분)

```bash
# 래퍼 파일 사용처 분석
grep -r "from app.services.company_service" app/ tests/
grep -r "from app.repositories.company_repository" app/ tests/
# ... 각 래퍼 파일에 대해 반복
```

### Phase 2: Import 경로 수정 (~2시간)

각 파일의 import 경로를 도메인 경로로 변경:

```python
# Before
from app.services.company_service import company_service
from app.repositories.company_repository import CompanyRepository

# After
from app.domains.company.services import company_service
from app.domains.company.repositories import CompanyRepository
```

### Phase 3: 래퍼 파일 삭제 (~30분)

```bash
# Services 래퍼 삭제
rm app/services/ai_service.py
rm app/services/audit_service.py
rm app/services/company_service.py
# ... 16개 파일

# Services 서브디렉토리 삭제
rm -rf app/services/contract/
rm -rf app/services/sync/
rm -rf app/services/ai/

# Repositories 래퍼 삭제
rm app/repositories/company_repository.py
# ... 7개 파일

# Repositories 서브디렉토리 삭제
rm -rf app/repositories/contract/
```

### Phase 4: __init__.py 업데이트 (~30분)

app/services/__init__.py 및 app/repositories/__init__.py에서
도메인으로 직접 re-export 설정

### Phase 5: 테스트 및 검증 (~1시간)

```bash
# Import 테스트
python -c "from app.domains.company.services import company_service; print('OK')"

# 전체 테스트
pytest tests/ -v --tb=short

# 앱 시작 확인
python run.py
```

---

## 삭제 대상 파일 목록 (총 27개)

### Services 래퍼 파일 (16개)
```
app/services/ai_service.py
app/services/audit_service.py
app/services/company_service.py
app/services/contract_filter_service.py
app/services/contract_service.py
app/services/corporate_admin_profile_service.py
app/services/corporate_settings_service.py
app/services/notification_service.py
app/services/organization_service.py
app/services/personal_service.py
app/services/platform_service.py
app/services/sync_service.py
app/services/system_setting_service.py
app/services/termination_service.py
app/services/user_employee_link_service.py
app/services/user_service.py
```

### Services 서브디렉토리 (3개)
```
app/services/contract/ (4개 파일)
app/services/sync/ (1개 파일)
app/services/ai/ (1개 파일)
```

### Repositories 래퍼 파일 (7개)
```
app/repositories/company_repository.py
app/repositories/data_sharing_settings_repository.py
app/repositories/organization_repository.py
app/repositories/person_contract_repository.py
app/repositories/personal_profile_repository.py
app/repositories/sync_log_repository.py
app/repositories/user_repository.py
```

### Repositories 서브디렉토리 (1개)
```
app/repositories/contract/ (1개 파일)
```

---

## 공유 모듈 재배치 (Optional)

base_repository.py와 mixins를 shared로 이동 고려:

```
app/shared/
├── repositories/
│   ├── base_repository.py      # 이동
│   └── mixins/
│       └── tenant_filter.py    # 이동
└── services/
    └── validation/
        └── profile_validator.py  # 이동
```

---

## 예상 효과

| 항목 | Before | After |
|------|--------|-------|
| 래퍼 파일 수 | 27개 | 0개 |
| 서브디렉토리 | 4개 | 0개 |
| 코드 라인 (예상) | ~800줄 | 0줄 |
| 중복 제거 | - | ~800줄 |

---

## 리스크 및 완화

### 리스크 1: 외부 의존성
- **상황**: 외부 시스템이 레거시 경로 사용
- **완화**: Option A (래퍼 유지) 선택

### 리스크 2: Import 누락
- **상황**: grep으로 찾지 못한 import
- **완화**: 단계별 테스트, 점진적 마이그레이션

### 리스크 3: 순환 참조
- **상황**: 도메인 간 import 시 순환 발생
- **완화**: 지연 import 패턴 사용

---

## 체크리스트

- [ ] Phase 1: Import 경로 분석 완료
- [ ] Phase 2: Import 경로 수정 완료
- [ ] Phase 3: 래퍼 파일 삭제 완료
- [ ] Phase 4: __init__.py 업데이트 완료
- [ ] Phase 5: 테스트 통과 확인
- [ ] 앱 정상 시작 확인
- [ ] 커밋 및 문서화
