법인 계정(corporate)을 별도 컬럼으로 추가해 상세/수정 비교표를 업데이트합니다.


[3 tools called]


법인 계정(corporate)을 별도 컬럼으로 추가해 비교표를 업데이트합니다.

## 템플릿 계정별 섹션 조건 비교표 (법인 계정 포함)

### 1. 어댑터별 사용 가능한 섹션 (AVAILABLE_SECTIONS)

| 섹션명 | 법인 계정<br/>(corporate) | 법인 직원<br/>(employee_sub) | 개인 계정<br/>(personal) | 법인 관리자 프로필<br/>(corporate_admin) |
|--------|-------------------------|----------------------------|------------------------|----------------------------------------|
| `basic` | O | O | O | O |
| `organization` | O | O | - | - |
| `contract` | O | O | - | - |
| `salary` | O | O | - | - |
| `benefit` | O | O | - | - |
| `insurance` | O | O | - | - |
| `education` | O | O | O | - |
| `career` | O | O | O | - |
| `certificate` | O | O | O | - |
| `language` | O | O | O | - |
| `military` | O | O | O | - |
| `family` | O | O | O | - |
| `award` | O | O | O | - |
| `project_participation` | O | O | O | - |
| `employment_contract` | O | O | - | - |
| `personnel_movement` | O | O | - | - |
| `attendance_assets` | O | O | - | - |
| `company_info` | - | - | - | O |
| **총 개수** | **14개** | **14개** | **9개** | **2개** |

---

### 2. 템플릿 섹션 표시 조건 (detail.html)

| 섹션 그룹 | 섹션명 | 표시 조건 | 법인 계정<br/>(corporate) | 법인 직원<br/>(employee_sub) | 개인 계정<br/>(personal) | 법인 관리자 프로필<br/>(corporate_admin) |
|-----------|--------|-----------|-------------------------|----------------------------|------------------------|----------------------------------------|
| **기본정보** | 개인 기본정보 | 항상 표시 | O | O | O | O |
| | 소속정보 | `is_corporate == True` | O | O | - | - |
| | 계약정보 | `is_corporate == True` | O | O | - | - |
| | 급여정보 | `is_corporate == True` | O | O | - | - |
| | 복리후생 | `is_corporate == True` | O | O | - | - |
| | 4대보험 | `is_corporate == True` | O | O | - | - |
| **이력정보** | 학력 | 항상 표시 | O | O | O | - |
| | 경력 | 항상 표시 | O | O | O | - |
| | 자격증 | 항상 표시 | O | O | O | - |
| | 언어능력 | 항상 표시 | O | O | O | - |
| | 병역 | 항상 표시 | O | O | O | - |
| | 가족사항 | `account_type != 'corporate_admin'` | O | O | O | - |
| | 수상내역 | 항상 표시 | O | O | O | - |
| | 프로젝트 참여 | `account_type != 'corporate_admin'` | O | O | O | - |
| **인사카드 전용** | 계정정보 | `page_mode == 'hr_card' AND is_corporate AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 근로계약 및 연봉 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 인사이동 및 고과 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 근태 및 비품 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| **회사정보** | 회사정보 | 법인 관리자 프로필 전용 | - | - | - | O |

---

### 3. 템플릿 섹션 표시 조건 (edit.html)

| 섹션 그룹 | 섹션명 | 표시 조건 | 법인 계정<br/>(corporate) | 법인 직원<br/>(employee_sub) | 개인 계정<br/>(personal) | 법인 관리자 프로필<br/>(corporate_admin) |
|-----------|--------|-----------|-------------------------|----------------------------|------------------------|----------------------------------------|
| **기본정보** | 개인 기본정보 | 항상 표시 | O | O | O | O |
| **인사카드 전용** | 계정정보 | `page_mode == 'hr_card' AND is_corporate AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 소속정보 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 계약정보 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 급여정보 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 복리후생 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| | 4대보험 | `page_mode == 'hr_card' AND account_type != 'corporate_admin'` | O (hr_card만) | O (hr_card만) | - | - |
| **공통 섹션** | 가족사항 | `account_type != 'corporate_admin'` | O | O | O | - |
| | 학력정보 | 항상 표시 | O | O | O | - |
| | 경력정보 | 항상 표시 | O | O | O | - |
| | 자격증 | 항상 표시 | O | O | O | - |
| | 언어능력 | 항상 표시 | O | O | O | - |
| | 병역정보 | 항상 표시 | O | O | O | - |
| | 수상내역 | 항상 표시 | O | O | O | - |
| | 프로젝트 참여 | `account_type != 'corporate_admin'` | O | O | O | - |
| **인사카드 전용** | 프로젝트 (인사이력) | `page_mode == 'hr_card' AND account_type != 'corporate_admin' AND NOT is_create_mode` | O (hr_card, 수정만) | O (hr_card, 수정만) | - | - |

---

### 4. 계정 유형별 섹션 요약 (프로필 모드)

| 섹션 그룹 | 섹션명 | 법인 계정<br/>(corporate, profile) | 법인 직원<br/>(employee_sub, profile) | 개인 계정<br/>(personal, profile) | 법인 관리자 프로필<br/>(corporate_admin, profile) |
|-----------|--------|----------------------------------|-------------------------------------|----------------------------------|------------------------------------------------|
| **기본정보** | 개인 기본정보 | O | O | O | O |
| | 소속정보 | O | O | - | - |
| | 계약정보 | O | O | - | - |
| | 급여정보 | O | O | - | - |
| | 복리후생 | O | O | - | - |
| | 4대보험 | O | O | - | - |
| **이력정보** | 학력 | O | O | O | - |
| | 경력 | O | O | O | - |
| | 자격증 | O | O | O | - |
| | 언어능력 | O | O | O | - |
| | 병역 | O | O | O | - |
| | 가족사항 | O | O | O | - |
| | 수상내역 | O | O | O | - |
| | 프로젝트 참여 | O | O | O | - |
| **회사정보** | 회사정보 | - | - | - | O |
| **총 개수** | | **14개** | **14개** | **9개** | **2개** |

---

### 5. 계정 유형별 섹션 요약 (인사카드 모드)

| 섹션 그룹 | 섹션명 | 법인 계정<br/>(corporate, hr_card) | 법인 직원<br/>(employee_sub, hr_card) | 개인 계정<br/>(personal, hr_card) | 법인 관리자 프로필<br/>(corporate_admin, hr_card) |
|-----------|--------|----------------------------------|-------------------------------------|----------------------------------|------------------------------------------------|
| **기본정보** | 개인 기본정보 | O | O | - | - |
| | 소속정보 | O | O | - | - |
| | 계약정보 | O | O | - | - |
| | 급여정보 | O | O | - | - |
| | 복리후생 | O | O | - | - |
| | 4대보험 | O | O | - | - |
| **이력정보** | 학력 | O | O | - | - |
| | 경력 | O | O | - | - |
| | 자격증 | O | O | - | - |
| | 언어능력 | O | O | - | - |
| | 병역 | O | O | - | - |
| | 가족사항 | O | O | - | - |
| | 수상내역 | O | O | - | - |
| | 프로젝트 참여 | O | O | - | - |
| **인사카드 전용** | 계정정보 | O | O | - | - |
| | 근로계약 및 연봉 | O | O | - | - |
| | 인사이동 및 고과 | O | O | - | - |
| | 근태 및 비품 | O | O | - | - |
| **총 개수** | | **18개** | **18개** | **0개** | **0개** |

---

### 6. 주요 조건 변수

| 변수명 | 법인 계정<br/>(corporate) | 법인 직원<br/>(employee_sub) | 개인 계정<br/>(personal) | 법인 관리자 프로필<br/>(corporate_admin) |
|--------|-------------------------|----------------------------|------------------------|----------------------------------------|
| `account_type` | `'corporate'` | `'employee_sub'` | `'personal'` | `'corporate_admin'` |
| `is_corporate` | `True` | `True` | `False` | `True` |
| `page_mode` | `'profile'` 또는 `'hr_card'` | `'profile'` 또는 `'hr_card'` | `'profile'`만 | `'profile'`만 |
| `is_create_mode` | `True` 또는 `False` | `True` 또는 `False` | `True` 또는 `False` | `True` 또는 `False` |
| `employee_id` | 있을 수도 없을 수도 있음 | 필수 | 없음 | 없음 |
| `user_role` | `'admin'` 또는 `'manager'` | `'employee'` | `'user'` | `'admin'` |

---

### 7. 섹션 표시 로직 요약

| 조건 | 법인 계정<br/>(corporate) | 법인 직원<br/>(employee_sub) | 개인 계정<br/>(personal) | 법인 관리자 프로필<br/>(corporate_admin) |
|------|-------------------------|----------------------------|------------------------|----------------------------------------|
| **프로필 모드** | 14개 섹션 | 14개 섹션 | 9개 섹션 | 2개 섹션 |
| **인사카드 모드** | 18개 섹션 | 18개 섹션 | 사용 불가 | 사용 불가 |
| **공통 섹션** | 개인 기본정보, 학력, 경력, 자격증, 언어능력, 병역, 가족사항, 수상내역, 프로젝트 참여 | 개인 기본정보, 학력, 경력, 자격증, 언어능력, 병역, 가족사항, 수상내역, 프로젝트 참여 | 개인 기본정보, 학력, 경력, 자격증, 언어능력, 병역, 가족사항, 수상내역, 프로젝트 참여 | 개인 기본정보, 회사정보 |
| **법인 전용 섹션** | 소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 계정정보, 인사기록 | 소속정보, 계약정보, 급여정보, 복리후생, 4대보험, 계정정보, 인사기록 | - | 소속정보 (회사정보) |
| **인사카드 전용 섹션** | 계정정보, 근로계약, 인사이동, 근태 | 계정정보, 근로계약, 인사이동, 근태 | - | - |

---

### 8. 계정 유형별 특징

| 특징 | 법인 계정<br/>(corporate) | 법인 직원<br/>(employee_sub) | 개인 계정<br/>(personal) | 법인 관리자 프로필<br/>(corporate_admin) |
|------|-------------------------|----------------------------|------------------------|----------------------------------------|
| **용도** | 법인 관리자 계정 (admin/manager) | 법인 직원 계정 (employee) | 개인 계정 | 법인 관리자 프로필 |
| **employee_id** | 선택적 (있을 수도 없을 수도) | 필수 | 없음 | 없음 |
| **프로필 모델** | Employee (있을 경우) | Employee | Profile | CorporateAdminProfile |
| **인사카드 모드** | 사용 가능 | 사용 가능 | 사용 불가 | 사용 불가 |
| **관리 기능** | 직원 관리, 조직 관리 | 본인 정보만 | 본인 정보만 | 회사 정보만 |

법인 계정(corporate)을 별도 컬럼으로 추가해 비교표를 업데이트했습니다.



----



섹션 필터 로직의 통합 여부 확인 중.


[5 tools called]


템플릿에서 섹션 필터링 사용 방식 확인 중.


[4 tools called]


템플릿의 섹션 필터링 로직 확인 중.


[4 tools called]


섹션 필터링 로직의 통합 여부 분석 결과입니다.

## 섹션 필터링 로직 통합 현황 분석

### 1. 통합된 부분

#### A. ProfileAdapter 계층 (부분 통합)

**위치**: `app/adapters/profile_adapter.py`

**통합된 기능**:
1. `get_available_sections()` - 어댑터별 섹션 목록 정의
   - `EmployeeProfileAdapter`: 14개 섹션
   - `PersonalProfileAdapter`: 9개 섹션
   - `CorporateAdminProfileAdapter`: 2개 섹션

2. `is_section_visible(section_name)` - 섹션 가시성 체크
   ```python
   def is_section_visible(self, section_name: str) -> bool:
       return section_name in self.get_available_sections()
   ```

3. `get_section_visibility()` - 모든 섹션의 가시성 딕셔너리 반환
   ```python
   def get_section_visibility(self) -> Dict[str, bool]:
       available = set(self.get_available_sections())
       return {section: section in available for section in all_sections}
   ```

**문제점**:
- 템플릿에서 거의 사용되지 않음
- `page_mode` 조건이 반영되지 않음
- `account_type`만 고려하고 `page_mode`는 미고려

---

#### B. FieldRegistry 계층 (필드 레벨 통합)

**위치**: `app/constants/field_registry/base.py`

**통합된 기능**:
1. `SectionDefinition.is_visible_for(account_type)` - 섹션 가시성 체크
   ```python
   def is_visible_for(self, account_type: str) -> bool:
       if self.visibility == Visibility.CORPORATE:
           return account_type in ('corporate', 'employee_sub')
       # ...
   ```

2. `FieldDefinition.is_visible_for(account_type)` - 필드 가시성 체크

**문제점**:
- FieldRegistry는 필드 순서/정의 관리용
- 템플릿 섹션 표시 조건과는 별개
- `page_mode` 조건 미지원

---

#### C. Context Processor (템플릿 헬퍼)

**위치**: `app/utils/context_processors.py`

**통합된 기능**:
1. `is_section_visible(section, account_type)` - 템플릿 헬퍼 함수
   ```python
   def is_section_visible(section, account_type):
       visibility = section.get('visibility', 'all')
       if visibility == 'corporate':
           return account_type in ('corporate', 'employee_sub')
   ```

**문제점**:
- 템플릿에서 사용되지 않음
- `page_mode` 조건 미지원

---

### 2. 분산된 부분 (주요 문제)

#### A. 템플릿 직접 조건문 (분산)

**위치**: `app/templates/profile/detail.html`, `edit.html`

**현재 상태**:
```jinja2
{# detail.html - 직접 조건문 사용 #}
{% if page_mode == 'hr_card' and is_corporate and account_type != 'corporate_admin' %}
    {% include 'partials/employee_form/_account_info.html' %}
{% endif %}

{% if page_mode == 'hr_card' and account_type != 'corporate_admin' %}
    {% include 'partials/employee_detail/_hr_records.html' %}
{% endif %}
```

**문제점**:
- 어댑터의 `get_available_sections()` 미사용
- 조건 로직이 템플릿에 분산
- 중복 조건문 반복
- `page_mode` 조건이 어댑터에 반영되지 않음

---

#### B. 어댑터와 템플릿 불일치

| 항목 | 어댑터 (AVAILABLE_SECTIONS) | 템플릿 (실제 사용) | 불일치 |
|------|---------------------------|------------------|--------|
| **계정정보** | 포함 안 됨 | `page_mode == 'hr_card'` 조건으로 표시 | 불일치 |
| **인사기록** | `employment_contract`, `personnel_movement`, `attendance_assets` 포함 | `page_mode == 'hr_card'` 조건으로 표시 | 불일치 |
| **프로젝트** | `hr_project` 포함 | `page_mode == 'hr_card' AND NOT is_create_mode` 조건 | 불일치 |

---

### 3. 통합 현황 요약

| 필터링 레벨 | 통합 여부 | 위치 | 사용 여부 | 문제점 |
|------------|----------|------|----------|--------|
| **어댑터 레벨** | 부분 통합 | `ProfileAdapter.get_available_sections()` | 미사용 | `page_mode` 미반영 |
| **FieldRegistry 레벨** | 통합됨 | `SectionDefinition.is_visible_for()` | 미사용 | 필드 정의용, 섹션 표시와 별개 |
| **Context Processor** | 통합됨 | `is_section_visible()` | 미사용 | 템플릿에서 사용 안 함 |
| **템플릿 레벨** | 분산됨 | `detail.html`, `edit.html` | 사용 중 | 직접 조건문, 중복 로직 |

---

### 4. 주요 문제점

#### 문제 1: 이중 필터링 시스템

**현재 상태**:
- 어댑터: `AVAILABLE_SECTIONS` 정의 (사용 안 됨)
- 템플릿: 직접 조건문 사용 (실제 동작)

**영향**:
- 어댑터 수정해도 템플릿에 반영 안 됨
- 조건 변경 시 여러 곳 수정 필요
- 일관성 저하

---

#### 문제 2: `page_mode` 조건 미반영

**현재 상태**:
- 어댑터: `account_type`만 고려
- 템플릿: `page_mode` 조건 직접 체크

**예시**:
```python
# 어댑터 (page_mode 무시)
AVAILABLE_SECTIONS = ['basic', 'organization', 'contract', ...]

# 템플릿 (page_mode 직접 체크)
{% if page_mode == 'hr_card' and account_type != 'corporate_admin' %}
    {% include 'partials/employee_form/_account_info.html' %}
{% endif %}
```

---

#### 문제 3: 중복 조건 로직

**발견된 중복**:
1. `account_type != 'corporate_admin'` - 8회 반복
2. `page_mode == 'hr_card'` - 6회 반복
3. `is_corporate` - 2회 반복

**위치**:
- `detail.html`: 3곳
- `edit.html`: 13곳

---

### 5. 통합 제안

#### 제안 1: 어댑터에 `page_mode` 지원 추가

```python
class ProfileAdapter(ABC):
    def get_available_sections(self, page_mode: str = 'profile') -> List[str]:
        """page_mode를 고려한 섹션 목록 반환"""
        base_sections = self._get_base_sections()
        if page_mode == 'hr_card':
            return base_sections + self._get_hr_card_sections()
        return base_sections
```

---

#### 제안 2: 템플릿에서 어댑터 메서드 사용

```jinja2
{# 현재 (분산) #}
{% if page_mode == 'hr_card' and is_corporate and account_type != 'corporate_admin' %}
    {% include 'partials/employee_form/_account_info.html' %}
{% endif %}

{# 개선안 (통합) #}
{% if adapter.is_section_visible('account_info', page_mode=page_mode) %}
    {% include 'partials/employee_form/_account_info.html' %}
{% endif %}
```

---

#### 제안 3: 섹션 필터 서비스 생성

```python
class SectionFilterService:
    """섹션 필터링 중앙 관리"""
    
    @staticmethod
    def is_section_visible(
        section_name: str,
        account_type: str,
        page_mode: str = 'profile',
        is_corporate: bool = False
    ) -> bool:
        """통합 섹션 가시성 체크"""
        # 모든 조건을 한 곳에서 관리
```

---

### 6. 결론

**통합 현황**: 부분 통합 (약 30%)

**통합된 부분**:
- 어댑터의 `AVAILABLE_SECTIONS` 정의
- `is_section_visible()` 메서드 (미사용)
- FieldRegistry의 가시성 체크 (필드 레벨)

**분산된 부분**:
- 템플릿의 직접 조건문 (실제 동작)
- `page_mode` 조건 처리
- `account_type` 조건 중복

**권장 사항**:
1. 어댑터에 `page_mode` 지원 추가
2. 템플릿에서 어댑터 메서드 사용으로 전환
3. 섹션 필터 서비스로 중앙화
4. 기존 템플릿 조건문을 단계적으로 제거

현재는 어댑터에 섹션 정의가 있으나 템플릿에서 직접 조건문을 사용해 분산되어 있습니다.

