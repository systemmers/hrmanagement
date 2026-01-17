중앙화, 일반화된 인라인 템플릿으로 모든 계정이 통합되고 입출력값과 로직, 그리고 프로필 기준으로 인사카드에 로드되어 출력되는 값이 동일한지 검토하여라.
현재는 모두 값이 불안정하며 입력, 저장, 출력이 상이하거나 입력되지 않고 있다.

## 문제 분석

### 현재 상황

1. 프로필 라우트 (`profile/routes.py`): 프로필 어댑터를 사용해 통합 컨텍스트 생성
   - `adapter.to_template_context()` 사용
   - 모든 계정 타입에서 동일한 인터페이스 제공

2. 인사카드 라우트 (`employee/blueprints/detail_routes.py`): Employee 객체를 직접 전달
   - 프로필 어댑터 미사용
   - `employee` 객체를 직접 템플릿에 전달

3. 템플릿 (`_basic_info.html`): `employee` 객체를 직접 사용
   - `employee.name`, `employee.email` 등 직접 접근
   - 프로필 어댑터의 통합 인터페이스 미활용

4. 입력/저장 로직 (`InlineEditService`): Employee 모델 필드명 기준
   - `STATIC_SECTIONS`에 필드명 정의
   - 프로필 어댑터와 필드명 일치 여부 불확실

### 문제점

1. 데이터 소스 불일치
   - 프로필: 어댑터 → `get_basic_info()` → 통합 필드명
   - 인사카드: Employee 객체 직접 접근 → 모델 필드명
   - 개인 계정과 법인 계정이 다른 데이터 경로 사용

2. 필드명 불일치 가능성
   - 어댑터: `mobile_phone` (SSOT)
   - 템플릿: `employee.mobile_phone` 또는 `employee.phone` 혼용
   - 서비스: `phone`과 `mobile_phone` 동기화 로직 존재

3. 출력값 불일치
   - 프로필 어댑터의 `get_basic_info()`와 템플릿에서 직접 접근하는 값이 다를 수 있음
   - 예: `phone` vs `mobile_phone`, `foreign_name` 누락 등

### 해결 방안

1. 인사카드 라우트에서 프로필 어댑터 사용
   ```python
   # detail_routes.py 수정
   from app.shared.adapters import create_profile_adapter
   
   adapter = create_profile_adapter(employee, 'employee')
   context = adapter.to_template_context(variable_name='employee')
   ```

2. 템플릿에서 어댑터 데이터 사용
   - `employee.name` → `basic_info.name` 또는 어댑터 메서드 사용
   - 모든 필드를 `basic_info`, `organization_info` 등 어댑터 제공 데이터로 통일

3. 필드명 일관성 검증
   - `InlineEditService.STATIC_SECTIONS`의 필드명과 어댑터의 `get_basic_info()` 필드명 일치 확인
   - SSOT 필드명 기준으로 통일

4. 통합 테스트
   - 모든 계정 타입(corporate, personal, employee_sub)에서 동일한 입력/저장/출력 값 검증

이 문제를 해결하려면 인사카드 라우트와 템플릿을 프로필 어댑터 기반으로 통일해야 합니다. 수정 진행할까요?