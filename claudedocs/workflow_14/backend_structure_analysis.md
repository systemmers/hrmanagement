# 법인 직원과 개인 계정 백엔드 구조 분석 보고서

날짜: 2025-12-11
작성자: Backend Architect
목적: dev_prompt.md #4 요구사항 - 법인 직원과 개인 계정의 백엔드 구조 일치 여부 분석

---

## 1. 구조적 불일치 항목

### 1.1 Blueprint 라우트 구조 차이

#### 법인 직원 (employees)
```
파일: app/blueprints/employees/routes.py
엔드포인트 구조:
- GET  /employees                          # 목록
- GET  /employees/<id>                     # 상세
- GET  /employees/new                      # 생성 폼
- POST /employees                          # 생성 처리
- GET  /employees/<id>/edit                # 수정 폼 (전체)
- POST /employees/<id>/update              # 수정 처리 (전체)
- GET  /employees/<id>/edit/basic          # 수정 폼 (기본정보)
- POST /employees/<id>/update/basic        # 수정 처리 (기본정보)
- GET  /employees/<id>/edit/history        # 수정 폼 (이력정보)
- POST /employees/<id>/update/history      # 수정 처리 (이력정보)
- POST /employees/<id>/delete              # 삭제

특징:
- Repository 패턴 사용
- 멀티테넌시(organization_id) 적용
- 역할별 접근 제어 (admin, manager, employee)
- 3가지 뷰 타입 (full, basic, history)
```

#### 개인 계정 (personal)
```
파일: app/blueprints/personal.py
엔드포인트 구조:
- GET  /personal/register                  # 회원가입 폼
- POST /personal/register                  # 회원가입 처리
- GET  /personal/dashboard                 # 대시보드
- GET  /personal/profile                   # 프로필 조회
- GET  /personal/profile/edit              # 프로필 수정 폼
- POST /personal/profile/edit              # 프로필 수정 처리

# 이력 정보 API (JSON)
- GET    /personal/education               # 학력 목록
- POST   /personal/education               # 학력 추가
- DELETE /personal/education/<id>          # 학력 삭제
- GET    /personal/career                  # 경력 목록
- POST   /personal/career                  # 경력 추가
- DELETE /personal/career/<id>             # 경력 삭제
- GET    /personal/certificate             # 자격증 목록
- POST   /personal/certificate             # 자격증 추가
- DELETE /personal/certificate/<id>        # 자격증 삭제
- GET    /personal/language                # 어학 목록
- POST   /personal/language                # 어학 추가
- DELETE /personal/language/<id>           # 어학 삭제
- GET    /personal/military                # 병역 정보
- POST   /personal/military                # 병역 정보 저장

특징:
- Service 패턴 사용
- 단일 프로필 관리
- JSON API 기반 이력정보 CRUD
- 데코레이터: @personal_login_required, @profile_required_no_inject
```

### 1.2 API 엔드포인트 설계 차이

| 기능 | 법인 직원 | 개인 계정 | 차이점 |
|------|-----------|-----------|--------|
| 프로필 조회 | `/employees/<id>` | `/personal/profile` | URL 패턴 다름 |
| 프로필 수정 폼 | `/employees/<id>/edit` | `/personal/profile/edit` | URL 구조 다름 |
| 프로필 수정 처리 | `POST /employees/<id>/update` | `POST /personal/profile/edit` | HTTP 메서드 일관성 부족 |
| 학력 CRUD | 폼 기반 (전체 페이지) | JSON API | 아키텍처 완전히 다름 |
| 경력 CRUD | 폼 기반 (전체 페이지) | JSON API | 아키텍처 완전히 다름 |
| 자격증 CRUD | 폼 기반 (전체 페이지) | JSON API | 아키텍처 완전히 다름 |

**불일치 심각도: 높음**
- 동일한 도메인(프로필 관리)에 대해 완전히 다른 아키텍처 사용
- 법인 직원: 전통적 폼 기반 다중 페이지
- 개인 계정: 현대적 JSON API + SPA 스타일

---

## 2. 데이터 흐름 차이

### 2.1 법인 직원 데이터 흐름
```
요청 → Blueprint → Helper 함수 → Repository → DB
     ← Template  ← Model 객체  ← Repository ←

구성요소:
1. Blueprint (employees/routes.py)
2. Helper 함수 (employees/helpers.py)
   - extract_employee_from_form()
   - update_education_data()
   - update_career_data()
3. Repository (employee_repo, education_repo, etc.)
4. Model (Employee, Education, Career, etc.)
5. Template (Jinja2, 전체 페이지 렌더링)

특징:
- Repository 패턴 철저히 적용
- ORM 직접 사용 제거
- Helper 함수로 로직 분리
- 멀티테넌시 적용 (organization_id)
```

### 2.2 개인 계정 데이터 흐름
```
요청 → Blueprint → Service → Repository → DB
     ← JSON      ← Service  ← Repository ←

구성요소:
1. Blueprint (personal.py)
2. Service (personal_service.py)
   - validate_registration()
   - register()
   - get_user_with_profile()
   - update_profile()
   - add_education(), delete_education()
3. Repository (PersonalProfileRepository, PersonalEducationRepository)
4. Model (PersonalProfile, PersonalEducation, etc.)
5. Template + JSON API (하이브리드)

특징:
- Service 계층 존재
- Repository 패턴 적용
- JSON API + 템플릿 혼합
- 단일 사용자 관리 (멀티테넌시 불필요)
```

### 2.3 데이터 흐름 차이 분석

| 계층 | 법인 직원 | 개인 계정 | 일치 여부 |
|------|-----------|-----------|-----------|
| Blueprint | O | O | ✓ 유사 |
| Helper/Service | Helper 함수 | Service 클래스 | X 패턴 다름 |
| Repository | O | O | ✓ 동일 |
| Model | Employee | PersonalProfile | X 이름 다름 |
| 응답 형식 | HTML (Jinja2) | HTML + JSON | X 혼합 사용 |

**불일치 심각도: 중간**
- Repository 패턴은 공통 적용 (긍정적)
- Helper vs Service 차이는 명명 문제일 수 있음
- 응답 형식 차이는 프론트엔드 전략 차이

---

## 3. 서비스 계층 비교

### 3.1 PersonalService (개인 계정)
```python
파일: app/services/personal_service.py

클래스 구조:
class PersonalService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = PersonalProfileRepository()
        self.education_repo = PersonalEducationRepository()
        # ... 기타 Repository

    # 회원가입
    def validate_registration()
    def register()

    # 프로필 관리
    def get_user_with_profile()
    def get_dashboard_data()
    def ensure_profile_exists()
    def update_profile()

    # 학력 CRUD
    def get_educations()
    def add_education()
    def delete_education()

    # 경력, 자격증, 어학, 병역 CRUD
    # ... (동일 패턴 반복)

특징:
- Repository 집약
- 비즈니스 로직 캡슐화
- 명확한 메서드 네이밍
- 싱글톤 패턴 (personal_service)
```

### 3.2 법인 직원 (Helper 함수)
```python
파일: app/blueprints/employees/helpers.py

함수 구조:
- verify_employee_access()           # 권한 검증
- extract_employee_from_form()       # 폼 데이터 추출
- extract_basic_fields_from_form()   # 기본 정보 추출
- update_family_data()               # 가족 정보 업데이트
- update_education_data()            # 학력 업데이트
- update_career_data()               # 경력 업데이트
# ... 기타 업데이트 함수

특징:
- 절차적 함수
- 상태 없음 (stateless)
- Blueprint에서 직접 호출
- Repository는 전역 extensions에서 import
```

### 3.3 CorporateAdminProfileService (법인 관리자)
```python
파일: app/services/corporate_admin_profile_service.py

클래스 구조:
class CorporateAdminProfileService:
    def __init__(self):
        self.profile_repo = CorporateAdminProfileRepository()
        self.user_repo = UserRepository()

    # 프로필 조회
    def get_profile_by_user_id()
    def get_user_with_profile()
    def get_adapter()
    def get_dashboard_data()

    # 프로필 생성/수정
    def ensure_profile_exists()
    def create_profile()
    def update_profile()

    # 프로필 상태 관리
    def deactivate_profile()
    def activate_profile()

    # 유틸리티
    def is_corporate_admin()
    def has_profile()

특징:
- PersonalService와 유사한 구조
- Repository 집약
- 싱글톤 패턴 (corporate_admin_profile_service)
- 법인 직원에는 이런 Service 없음!
```

### 3.4 서비스 계층 불일치

| 항목 | 법인 직원 | 개인 계정 | 법인 관리자 |
|------|-----------|-----------|-------------|
| 서비스 클래스 | ❌ 없음 | ✓ PersonalService | ✓ CorporateAdminProfileService |
| Helper 함수 | ✓ helpers.py | ❌ 없음 | ❌ 없음 |
| Repository 접근 | 전역 extensions | Service 내부 | Service 내부 |
| 비즈니스 로직 위치 | Blueprint + Helper | Service | Service |
| 패턴 일관성 | 절차적 | 객체지향 | 객체지향 |

**불일치 심각도: 높음**
- 법인 직원만 Service 계층 없음
- 개인 계정과 법인 관리자는 유사한 패턴
- 아키텍처 일관성 심각하게 부족

---

## 4. 어댑터 패턴 비교

### 4.1 어댑터 구조
```python
파일: app/adapters/profile_adapter.py

추상 클래스:
- ProfileAdapter (ABC)
  - 공통 인터페이스 정의
  - 18개 추상 메서드

구현 클래스:
1. EmployeeProfileAdapter
   - Employee 모델 래핑
   - AVAILABLE_SECTIONS: 14개 섹션
   - 법인 전용 메서드 포함 (get_salary_info, get_insurance_info, etc.)

2. PersonalProfileAdapter
   - PersonalProfile 모델 래핑
   - AVAILABLE_SECTIONS: 6개 섹션
   - 법인 전용 메서드는 None 반환

3. CorporateAdminProfileAdapter
   - CorporateAdminProfile 모델 래핑
   - AVAILABLE_SECTIONS: 2개 섹션 (basic, company_info)
   - 경량 프로필 (이력 정보 없음)
```

### 4.2 어댑터 메서드 비교

| 메서드 | Employee | Personal | CorporateAdmin |
|--------|----------|----------|----------------|
| get_basic_info() | ✓ 전체 | ✓ 전체 | ✓ 최소한 |
| get_organization_info() | ✓ 법인정보 | ❌ None | ✓ 회사정보 |
| get_contract_info() | ✓ 계약 | ❌ None | ❌ None |
| get_salary_info() | ✓ 급여 | ❌ None | ❌ None |
| get_benefit_info() | ✓ 복리후생 | ❌ None | ❌ None |
| get_insurance_info() | ✓ 4대보험 | ❌ None | ❌ None |
| get_education_list() | ✓ Education | ✓ PersonalEducation | ❌ [] |
| get_career_list() | ✓ Career | ✓ PersonalCareer | ❌ [] |
| get_certificate_list() | ✓ Certificate | ✓ PersonalCertificate | ❌ [] |
| get_language_list() | ✓ Language | ✓ PersonalLanguage | ❌ [] |
| get_military_info() | ✓ MilitaryService | ✓ PersonalMilitaryService | ❌ None |

### 4.3 어댑터 일관성 평가

**긍정적 측면:**
- 추상 인터페이스로 공통 구조 강제
- 템플릿에서 동일한 메서드 호출 가능
- 데이터 모델 차이를 잘 추상화

**문제점:**
- 어댑터는 통일되어 있으나, 이를 사용하는 Blueprint가 다름
- EmployeeProfileAdapter는 profile/ Blueprint에서 사용
- PersonalProfileAdapter는 personal.py Blueprint에서 사용
- 어댑터 생성 방식 불일치:
  - Employee: `adapter = EmployeeProfileAdapter(employee)` (직접 생성)
  - Personal: `adapter = PersonalProfileAdapter(profile_obj)` (직접 생성)
  - CorporateAdmin: `adapter = corporate_admin_profile_service.get_adapter(user_id)` (Service 통해)

**불일치 심각도: 중간**
- 어댑터 자체는 잘 설계됨
- 사용 방식이 일관되지 않음

---

## 5. 모델 구조 비교

### 5.1 Employee vs PersonalProfile 필드 비교

| 필드 카테고리 | Employee | PersonalProfile | 일치 여부 |
|--------------|----------|-----------------|-----------|
| **기본 식별** | id, employee_number, name, photo | id, user_id, name, photo | △ 부분 일치 |
| **다국어 이름** | english_name, chinese_name | english_name, chinese_name | ✓ 동일 |
| **생년월일** | birth_date, lunar_birth, gender | birth_date, lunar_birth, gender | ✓ 동일 |
| **연락처** | mobile_phone, home_phone, email, phone | mobile_phone, home_phone, email | △ phone 차이 |
| **주소** | address, detailed_address, postal_code | address, detailed_address, postal_code | ✓ 동일 |
| **신분정보** | resident_number, nationality | resident_number, nationality | ✓ 동일 |
| **기타정보** | blood_type, religion, hobby, specialty, disability_info | blood_type, religion, hobby, specialty, disability_info | ✓ 동일 |
| **소속정보** | department, position, team, job_title, work_location, internal_phone, company_email, organization_id | ❌ 없음 | ✗ 법인 전용 |
| **고용정보** | status, hire_date | ❌ 없음 | ✗ 법인 전용 |
| **메타정보** | ❌ 없음 | created_at, updated_at, is_public | △ 개인 전용 |

### 5.2 관계형 데이터 비교

| 관계 | Employee | PersonalProfile |
|------|----------|-----------------|
| **학력** | Education | PersonalEducation |
| **경력** | Career | PersonalCareer |
| **자격증** | Certificate | PersonalCertificate |
| **어학** | Language | PersonalLanguage |
| **병역** | MilitaryService | PersonalMilitaryService |
| **가족** | FamilyMember | ❌ 없음 |
| **급여** | Salary, SalaryHistory, SalaryPayment | ❌ 없음 |
| **계약** | Contract | ❌ 없음 |
| **복리후생** | Benefit | ❌ 없음 |
| **보험** | Insurance | ❌ 없음 |
| **인사평가** | Promotion, Evaluation, Training | ❌ 없음 |
| **근태** | Attendance | ❌ 없음 |
| **프로젝트** | Project | ❌ 없음 |
| **수상** | Award | ❌ 없음 |
| **비품** | Asset | ❌ 없음 |
| **첨부파일** | Attachment | ❌ 없음 |

### 5.3 모델 설계 평가

**공통 필드 (17개):**
- 이름 관련: name, english_name, chinese_name
- 생년월일: birth_date, lunar_birth, gender
- 연락처: mobile_phone, home_phone, email
- 주소: address, detailed_address, postal_code
- 기타: nationality, blood_type, religion, hobby, specialty, disability_info

**개인 계정만 있는 필드 (3개):**
- user_id (User 연결)
- created_at, updated_at (메타정보)
- is_public (프로필 공개 설정)

**법인 직원만 있는 필드 (11개):**
- employee_number (사번)
- organization_id (조직 연결)
- department, position, team, job_title (소속정보)
- status, hire_date (고용정보)
- work_location, internal_phone, company_email (근무지 정보)

**평가:**
- 기본 개인정보 필드는 거의 일치 (긍정적)
- Employee가 더 많은 정보 포함 (법인 특성)
- PersonalProfile이 더 간단하고 경량 (개인 특성)
- 관계형 데이터는 명명만 다를 뿐 구조 유사

**필드 매핑 일관성: 양호**

---

## 6. 통합/리팩토링 권장사항

### 6.1 즉시 해결 필요 (High Priority)

#### A. 법인 직원 Service 계층 추가
```
문제:
- PersonalService, CorporateAdminProfileService는 있으나
- EmployeeService가 없음
- 법인 직원만 Helper 함수 사용 (일관성 부족)

해결:
1. EmployeeService 클래스 생성
   - app/services/employee_service.py
   - PersonalService와 유사한 구조
   - Repository 집약

2. employees/helpers.py 로직 이관
   - verify_employee_access() → EmployeeService
   - update_education_data() → EmployeeService
   - extract_employee_from_form() → EmployeeService

3. Blueprint에서 Service 사용
   - from app.services.employee_service import employee_service
   - employee_service.get_by_id()
   - employee_service.update_education()

장점:
- 아키텍처 일관성 확보
- 비즈니스 로직 중앙화
- 테스트 용이성 증가
```

#### B. API 엔드포인트 패턴 통일
```
문제:
- 법인 직원: 폼 기반 전체 페이지
- 개인 계정: JSON API
- 사용자 경험 일관성 부족

해결 방안 1 (권장): JSON API 통일
1. 법인 직원도 JSON API 도입
   - POST /employees/<id>/education
   - DELETE /employees/<id>/education/<edu_id>
   - PUT /employees/<id>/career/<career_id>

2. 프론트엔드 동적화
   - 현재 템플릿에 JavaScript 추가
   - fetch API로 CRUD 처리
   - SPA 스타일 UI 개선

장점:
- 현대적 UX
- 부분 업데이트 가능
- 네트워크 효율성

해결 방안 2 (보수적): 폼 기반 통일
1. 개인 계정도 폼 기반으로 변경
   - GET /personal/education/edit
   - POST /personal/education/update

단점:
- 구식 UX
- 전체 페이지 새로고침
- 비권장
```

### 6.2 중기 개선 (Medium Priority)

#### C. 통합 프로필 라우트 확장
```
현황:
- app/blueprints/profile/routes.py
- 통합 프로필 조회는 구현됨
- 수정 기능은 TODO 상태

개선:
1. 통합 프로필 수정 구현
   - @profile_bp.route('/edit')
   - 계정 유형별 분기 처리
   - 공통 템플릿 사용

2. 통합 API 엔드포인트 추가
   - PUT /profile/section/<section_name>
   - DELETE /profile/<resource>/<id>
   - POST /profile/<resource>

3. 개인 계정을 통합 라우트로 마이그레이션
   - personal.py 라우트 점진적 이관
   - 기존 URL은 리다이렉트로 유지
```

#### D. Adapter 사용 일관성 개선
```
문제:
- 어댑터 생성 방식이 제각각
- 직접 생성 vs Service 통해 생성

해결:
1. AdapterFactory 도입
   - app/adapters/factory.py
   - create_profile_adapter(user_id)
   - 계정 유형 자동 판별

2. Service에서 Adapter 반환 통일
   - EmployeeService.get_adapter(employee_id)
   - PersonalService.get_adapter(user_id)
   - CorporateAdminProfileService.get_adapter(user_id)

3. Blueprint에서 일관된 사용
   - adapter = service.get_adapter(id)
   - context = adapter.get_all_data()
```

### 6.3 장기 개선 (Low Priority)

#### E. 모델 구조 재설계 검토
```
현황:
- Employee와 PersonalProfile이 분리
- 공통 필드 중복

검토 사항:
1. Profile 추상 모델 도입
   - BaseProfile (추상 클래스)
   - 공통 필드 17개 포함
   - EmployeeProfile extends BaseProfile
   - PersonalProfile extends BaseProfile

장점:
- DRY 원칙 준수
- 마이그레이션 로직 공유

단점:
- DB 마이그레이션 복잡
- 기존 코드 대규모 수정 필요

결론: 현재 시점에서는 비권장
- 어댑터 패턴으로 이미 추상화됨
- 리스크 대비 효과 낮음
```

#### F. Repository 인터페이스 표준화
```
현황:
- Repository 패턴 적용은 잘 됨
- 메서드 네이밍이 약간씩 다름

개선:
1. BaseRepository 추상 클래스
   - get_by_id(id)
   - get_all()
   - create(data)
   - update(id, data)
   - delete(id)

2. 공통 쿼리 메서드
   - filter_by(**kwargs)
   - paginate(page, per_page)

3. 모든 Repository가 상속
   - EmployeeRepository extends BaseRepository
   - PersonalProfileRepository extends BaseRepository
```

---

## 7. 우선순위별 실행 계획

### Phase 1: 아키텍처 일관성 확보 (1-2주)
```
1. EmployeeService 구현
   - app/services/employee_service.py 생성
   - helpers.py 로직 이관
   - Blueprint 수정

2. Service 계층 표준화
   - 공통 인터페이스 정의
   - 에러 핸들링 통일
   - 트랜잭션 관리 통일

검증:
- 단위 테스트 작성
- 기존 기능 동작 확인
- 코드 리뷰
```

### Phase 2: API 현대화 (2-3주)
```
1. 법인 직원 JSON API 추가
   - POST /employees/<id>/education
   - POST /employees/<id>/career
   - PUT /employees/<id>/education/<edu_id>
   - DELETE /employees/<id>/education/<edu_id>

2. 프론트엔드 동적화
   - JavaScript 모듈화
   - fetch API 래퍼
   - 에러 핸들링 UI

3. 개인 계정과 패턴 통일
   - 동일한 JSON 구조
   - 동일한 에러 응답

검증:
- API 통합 테스트
- E2E 테스트
- 성능 테스트
```

### Phase 3: 통합 라우트 완성 (1주)
```
1. 통합 프로필 수정 구현
   - unified_profile_edit.html 템플릿
   - PUT /profile/update API
   - 계정 유형별 분기

2. 개인 계정 마이그레이션
   - personal.py 라우트 이관
   - 리다이렉트 규칙 설정
   - 하위 호환성 유지

검증:
- 회귀 테스트
- URL 리다이렉트 검증
- 권한 체크
```

### Phase 4: 어댑터 개선 (1주)
```
1. AdapterFactory 구현
   - 자동 타입 판별
   - 캐싱 전략

2. Service에서 Adapter 반환 표준화
   - 모든 Service에 get_adapter() 추가
   - Blueprint 수정

검증:
- 어댑터 팩토리 테스트
- 성능 테스트 (캐싱 효과)
```

---

## 8. 리스크 및 고려사항

### 8.1 기술적 리스크

**데이터베이스 마이그레이션:**
- 현재: 수정 불필요 (스키마 변경 없음)
- Phase 1-4는 애플리케이션 레벨 변경만 해당

**하위 호환성:**
- 기존 URL 유지 필요
- 리다이렉트 규칙으로 대응
- API 버저닝 고려

**성능 영향:**
- Service 계층 추가로 약간의 오버헤드
- 어댑터 캐싱으로 완화 가능
- JSON API는 오히려 성능 향상

### 8.2 조직적 고려사항

**개발 리소스:**
- Phase 1-4 총 5-7주 소요 예상
- 1명 풀타임 기준

**테스트 범위:**
- 단위 테스트: 모든 Service 메서드
- 통합 테스트: API 엔드포인트
- E2E 테스트: 핵심 사용자 흐름

**배포 전략:**
- Phase별 점진적 배포
- Feature Flag 활용
- 롤백 계획 준비

### 8.3 대안 평가

**Option A: 현재 상태 유지**
- 장점: 리스크 없음
- 단점: 기술 부채 증가, 유지보수 어려움

**Option B: 전면 재설계**
- 장점: 완벽한 일관성
- 단점: 시간/비용 과다, 리스크 높음

**Option C: 점진적 개선 (권장)**
- 장점: 리스크 관리, 단계별 가치 제공
- 단점: 기간 소요

---

## 9. 결론 및 권고

### 9.1 현황 종합

**긍정적 측면:**
1. Repository 패턴 일관되게 적용
2. Adapter 패턴으로 모델 차이 추상화
3. 기본 개인정보 필드 일치도 높음

**부정적 측면:**
1. 법인 직원만 Service 계층 없음 (아키텍처 불일치)
2. API 설계 완전히 다름 (폼 vs JSON)
3. 데이터 흐름 패턴 불일치

### 9.2 최종 권고사항

**즉시 실행 (High Priority):**
1. EmployeeService 구현 → 아키텍처 일관성 확보
2. API 엔드포인트 패턴 통일 → 사용자 경험 개선

**중기 실행 (Medium Priority):**
3. 통합 프로필 라우트 완성
4. Adapter 사용 일관성 개선

**장기 검토 (Low Priority):**
5. 모델 구조 재설계 (현시점 비권장)
6. Repository 인터페이스 표준화

### 9.3 기대 효과

**개발자 경험:**
- 코드 이해도 향상
- 유지보수 용이성 증가
- 신규 기능 개발 속도 향상

**사용자 경험:**
- 일관된 UI/UX
- 빠른 응답 속도 (JSON API)
- 부드러운 인터랙션

**시스템 품질:**
- 테스트 커버리지 향상
- 버그 감소
- 기술 부채 해소

---

## 10. 부록: 파일 경로 참조

### Blueprint
- 법인 직원: `app/blueprints/employees/routes.py`
- 개인 계정: `app/blueprints/personal.py`
- 통합 프로필: `app/blueprints/profile/routes.py`

### Service
- 개인 계정: `app/services/personal_service.py`
- 법인 관리자: `app/services/corporate_admin_profile_service.py`
- 법인 직원: ❌ 없음 (생성 필요)

### Repository
- Employee 관련: `app/repositories/employee_repository.py` 등
- Personal 관련: `app/repositories/personal_profile_repository.py` 등

### Model
- Employee: `app/models/employee.py`
- PersonalProfile: `app/models/personal/profile.py`

### Adapter
- 전체: `app/adapters/profile_adapter.py`
  - EmployeeProfileAdapter
  - PersonalProfileAdapter
  - CorporateAdminProfileAdapter

---

**보고서 종료**
