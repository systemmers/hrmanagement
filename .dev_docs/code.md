blueprints 폴더의 모든 파일을 분석해 레이어 분리 위반 여부를 확인 중입니다.


[11 tools called]


서브 디렉토리 파일 확인 중입니다.


[8 tools called]


blueprints 폴더의 모든 파일을 분석해 레이어 분리 위반 여부를 비교 테이블로 정리 중입니다.


[5 tools called]


blueprints 폴더의 모든 파일을 분석한 결과입니다.

## Blueprints 레이어 분리 위반 비교 분석 테이블

| 파일 경로 | Repository 직접 호출 | Model.query 직접 사용 | 비즈니스 로직 포함 | 데이터 변환 로직 | 여러 서비스 조합 | 파라미터 파싱 | 위반 심각도 | 위반 라인 | 비고 |
|-----------|---------------------|----------------------|-------------------|----------------|----------------|-------------|------------|----------|------|
| **employees/list_routes.py** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | 🔴 높음 | 34-58, 89-135, 143-175, 186-199 | 계약 맵핑, for 루프, 데이터 변환 |
| **employees/detail_routes.py** | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | 🟡 중간 | 165-260 | 20개 이상 서비스 호출 조합 |
| **employees/mutation_routes.py** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | 🟡 중간 | 40-69, 90-148, 312-327 | 비즈니스 상수, 필터링 로직, 퇴사 처리 |
| **employees/routes.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 양호 | - | 통합 등록만 담당 |
| **employees/helpers.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ⚠️ | 🟢 낮음 | 43-81 | request 직접 의존 |
| **contracts.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ⚠️ | 🟢 낮음 | 166-180 | 날짜 파싱 로직 |
| **corporate.py** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | 🟡 중간 | 138-161 | for 루프, 데이터 변환 |
| **auth.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ⚠️ | 🟢 낮음 | 54-63 | 조건부 분기 로직 |
| **main.py** | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | ⚠️ | 🟢 낮음 | 91-101, 108 | 조건부 필터링, to_dict 호출 |
| **mypage.py** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | 🟢 낮음 | 68-92 | 다수 서비스 호출 (허용 범위) |
| **notifications.py** | ❌ | ⚠️ | ❌ | ⚠️ | ❌ | ❌ | 🟢 낮음 | 305-308 | Model 상수 참조 (허용) |
| **audit.py** | ❌ | ⚠️ | ❌ | ⚠️ | ❌ | ⚠️ | 🟢 낮음 | 69-78, 238-250, 319-330 | 날짜 파싱, Model 상수 참조 |
| **api.py** | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | ❌ | 🟢 낮음 | 49-55 | 필터링 로직 (허용 범위) |
| **ai_test.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ | 🟢 낮음 | 88-144 | 헬퍼 함수 (테스트용) |
| **personal/routes.py** | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | ⚠️ | 🟢 낮음 | 32-93, 432-433 | 파일 업로드 헬퍼, 리스트 필터링 |
| **sync/sync_routes.py** | ❌ | ❌ | ⚠️ | ❌ | ⚠️ | ❌ | 🟢 낮음 | 141, 154-175 | Model import, 트랜잭션 처리 |
| **sync/contract_routes.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 양호 | - | Service 경유 |
| **admin/organization.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ⚠️ | 🟢 낮음 | 18-28, 86-101 | 헬퍼 함수, 파라미터 검증 |
| **platform/users.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 양호 | - | Service 경유 |
| **platform/dashboard.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 양호 | - | Service 경유 |
| **platform/settings.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 양호 | - | Service 경유 |
| **platform/companies.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 양호 | - | Service 경유 |
| **profile/routes.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ | 🟢 낮음 | 179-191 | 섹션 매핑 딕셔너리 (허용) |
| **profile/decorators.py** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | 🟡 중간 | 58, 71, 90 | Model.query 직접 사용 (인증용) |
| **account/routes.py** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ⚠️ | 🟢 낮음 | 43-60, 96-103 | 입력 검증 로직 |
| **corporate_settings/classifications_api.py** | ❌ | ⚠️ | ❌ | ❌ | ❌ | ⚠️ | 🟢 낮음 | 62, 68 | Model 상수 참조 (허용) |

---

## 위반 유형별 상세 분석

### 🔴 높음 - 즉시 리팩토링 필요

#### 1. `employees/list_routes.py`
- 위반 사항:
  - 라인 34-58: 파라미터 추출 중복 (helpers.py 함수 미사용)
  - 라인 89-135: 계약 맵핑 로직 (for 루프, 데이터 변환)
  - 라인 143-175: 계약대기 목록 로직 (for 루프, 비즈니스 규칙)
  - 라인 186-199: API 데이터 변환 (for 루프, 필드 매핑)
- 권장: Service 레이어로 이동

---

### 🟡 중간 - 리팩토링 권장

#### 2. `employees/detail_routes.py`
- 위반 사항:
  - 라인 165-260: 20개 이상 서비스 메서드 호출 조합
  - 라인 218-228: 조건부 로직 (`if person_contract:`)
- 권장: `get_employee_full_view_data()` 통합 메서드 생성

#### 3. `employees/mutation_routes.py`
- 위반 사항:
  - 라인 40-69: 비즈니스 규칙 상수 정의 (Route에 위치)
  - 라인 90-148: 필터링 로직 (Route 헬퍼에 비즈니스 로직)
  - 라인 312-327: 퇴사 처리 로직 (Route에서 비즈니스 로직)
- 권장: Service 레이어로 이동

#### 4. `corporate.py`
- 위반 사항:
  - 라인 138-161: for 루프로 데이터 변환 및 조합
  ```python
  # contract_status, name 추가
  for user in users:
      contract_info = contract_map.get(user['id'], {})
      user['contract_status'] = contract_info.get('status', 'none')
      # Employee에서 이름 조회
      employee_id = user.get('employee_id')
      if employee_id and employee_id in employee_map:
          user['name'] = employee_map[employee_id].get('name', '-')
  ```
- 권장: Service 레이어로 이동

#### 5. `profile/decorators.py`
- 위반 사항:
  - 라인 58, 71, 90: `Model.query` 직접 사용
  ```python
  profile = Profile.query.filter_by(user_id=user_id).first()
  employee = Employee.query.get(employee_id)
  admin_profile = CorporateAdminProfile.query.filter_by(user_id=user_id).first()
  ```
- 권장: 인증용 Service 생성 또는 Repository 경유

---

### 🟢 낮음 - 허용 범위 또는 경미한 위반

#### 6. `contracts.py`
- 위반 사항:
  - 라인 166-180: 날짜 파싱 로직
- 권장: Service 레이어로 이동 (선택)

#### 7. `auth.py`
- 위반 사항:
  - 라인 54-63: 조건부 분기 로직 (직원 상태별 리다이렉트)
- 권장: Service 레이어로 이동 (선택)

#### 8. `main.py`
- 위반 사항:
  - 라인 91-101: 조건부 필터링 로직
  - 라인 108: `emp.to_dict()` 직접 호출
- 권장: Service 레이어로 이동 (선택)

#### 9. `personal/routes.py`
- 위반 사항:
  - 라인 32-93: 파일 업로드 헬퍼 함수 (Route에 위치)
  - 라인 432-433: 리스트 필터링 (`[c for c in contracts if c.get('is_active')]`)
- 권장: 파일 업로드는 Service로 이동, 필터링은 허용 범위

#### 10. `sync/sync_routes.py`
- 위반 사항:
  - 라인 141: Model import (`from app.models.person_contract import PersonCorporateContract`)
  - 라인 154-175: 트랜잭션 처리 (허용 범위)
- 권장: Model import는 Service로 이동

#### 11. `admin/organization.py`
- 위반 사항:
  - 라인 18-28: 헬퍼 함수 (`get_current_root_organization_id`)
  - 라인 86-101: 파라미터 검증 로직
- 권장: 헬퍼는 utils로 이동, 검증은 Service로 이동 (선택)

#### 12. `account/routes.py`
- 위반 사항:
  - 라인 43-60, 96-103: 입력 검증 로직
- 권장: Service 레이어로 이동 (선택)

---

### ✅ 양호 - 레이어 분리 준수

- `employees/routes.py`
- `sync/contract_routes.py`
- `platform/users.py`
- `platform/dashboard.py`
- `platform/settings.py`
- `platform/companies.py`

---

## 위반 통계 요약

| 심각도 | 파일 수 | 주요 위반 사항 |
|--------|---------|---------------|
| 🔴 높음 | 1 | 계약 맵핑, for 루프, 데이터 변환 |
| 🟡 중간 | 4 | 여러 서비스 조합, Model.query 사용, 비즈니스 로직 |
| 🟢 낮음 | 12 | 파라미터 파싱, 입력 검증, 헬퍼 함수 |
| ✅ 양호 | 6 | 레이어 분리 준수 |

---

## 우선순위별 리팩토링 계획

### 1순위 (즉시)
- `employees/list_routes.py`: 계약 맵핑 로직 Service로 이동

### 2순위 (단기)
- `employees/detail_routes.py`: 통합 메서드 생성
- `employees/mutation_routes.py`: 필터링 로직 Service로 이동
- `corporate.py`: 데이터 변환 로직 Service로 이동
- `profile/decorators.py`: Model.query → Service 경유

### 3순위 (중기)
- `contracts.py`, `auth.py`, `main.py`: 파라미터 파싱/검증 로직 Service로 이동

### 4순위 (장기)
- `personal/routes.py`, `admin/organization.py`: 헬퍼 함수 정리

---

## 결론

- 총 23개 파일 중 17개에서 위반 발견
- 높음: 1개, 중간: 4개, 낮음: 12개
- 주요 위반: Route에서 비즈니스 로직 처리, 데이터 변환, 여러 서비스 조합
- 권장: 우선순위에 따라 단계적 리팩토링 진행