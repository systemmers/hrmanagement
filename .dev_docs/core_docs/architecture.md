# HR Management System - 아키텍처 문서

## 목차
1. [개요](#개요)
2. [전체 디렉토리 구조](#전체-디렉토리-구조)
3. [레이어 아키텍처](#레이어-아키텍처)
4. [주요 컴포넌트 및 모듈](#주요-컴포넌트-및-모듈)
5. [디자인 패턴](#디자인-패턴)
6. [의존성 흐름](#의존성-흐름)
7. [멀티테넌시 구조](#멀티테넌시-구조)
8. [인증/권한 시스템](#인증권한-시스템)
9. [데이터 흐름](#데이터-흐름)
10. [기술 스택](#기술-스택)
11. [개선 권장 사항](#개선-권장-사항)

---

## 개요

HR Management System은 Flask 기반의 인사관리 플랫폼으로, 법인과 개인 계정을 모두 지원하는 멀티테넌시 SaaS 아키텍처를 채택하고 있습니다.

**핵심 특징:**
- 3-Tier 레이어 아키텍처 (Presentation, Business, Data Access)
- App Factory 패턴 기반 Flask 애플리케이션
- Repository Pattern + Service Layer Pattern
- PostgreSQL 기반 관계형 데이터베이스
- Jinja2 템플릿 + Vanilla JavaScript (컴포넌트 방식)

---

## 전체 디렉토리 구조

```
D:/projects/hrmanagement/
├── app/                          # 애플리케이션 메인 패키지
│   ├── __init__.py              # App Factory (create_app)
│   ├── config.py                # 환경별 설정 (Development, Production, Testing)
│   ├── database.py              # SQLAlchemy 인스턴스
│   ├── extensions.py            # Flask 확장 초기화
│   ├── forms.py                 # WTForms 폼 정의
│   │
│   ├── blueprints/              # Flask Blueprints (라우팅 레이어)
│   │   ├── __init__.py          # Blueprint 등록
│   │   ├── main.py              # 메인 페이지, 검색
│   │   ├── auth.py              # 인증 (로그인, 로그아웃)
│   │   ├── admin.py             # 관리자 기능
│   │   ├── employees/           # 직원 CRUD (모듈 분할)
│   │   ├── corporate.py         # 법인 계정 기능
│   │   ├── personal.py          # 개인 계정 기능
│   │   ├── contracts.py         # 계약 관리
│   │   ├── profile.py           # 통합 프로필 (법인/개인)
│   │   ├── account.py           # 계정 관리
│   │   ├── mypage.py            # 마이페이지 (일반 직원)
│   │   ├── classification.py   # 분류 옵션 관리
│   │   ├── api.py               # REST API
│   │   ├── sync.py              # 데이터 동기화
│   │   ├── audit.py             # 감사 로그
│   │   ├── notifications.py    # 알림 시스템
│   │   └── ai_test.py           # AI 테스트 (프로토타입)
│   │
│   ├── services/                # 서비스 레이어 (비즈니스 로직)
│   │   ├── __init__.py
│   │   ├── employee_service.py           # 직원 관리 로직
│   │   ├── employee_account_service.py   # 직원 계정 관리
│   │   ├── contract_service.py           # 계약 관리 로직
│   │   ├── personal_service.py           # 개인 계정 로직
│   │   ├── corporate_admin_profile_service.py  # 법인 관리자 프로필
│   │   ├── sync_service.py               # 데이터 동기화 로직
│   │   ├── sync_basic_service.py         # 기본 동기화
│   │   ├── sync_relation_service.py      # 관계형 동기화
│   │   ├── sync_snapshot_service.py      # 스냅샷 동기화
│   │   ├── termination_service.py        # 퇴직 처리
│   │   ├── audit_service.py              # 감사 로그
│   │   ├── notification_service.py       # 알림 발송
│   │   ├── file_storage_service.py       # 파일 저장
│   │   ├── event_listeners.py            # 이벤트 리스너
│   │   ├── ai_service.py                 # AI 서비스 (Gemini API)
│   │   └── ai/                           # AI 서비스 모듈
│   │
│   ├── repositories/            # 레포지토리 레이어 (데이터 접근)
│   │   ├── __init__.py
│   │   ├── base_repository.py            # 공통 CRUD 기본 클래스
│   │   ├── employee_repository.py        # 직원 데이터 접근
│   │   ├── classification_repository.py  # 분류 옵션
│   │   ├── user_repository.py            # 사용자 계정
│   │   ├── company_repository.py         # 법인 정보
│   │   ├── organization_repository.py    # 조직 구조
│   │   ├── person_contract_repository.py # 개인-법인 계약
│   │   ├── personal_profile_repository.py # 개인 프로필
│   │   ├── corporate_admin_profile_repository.py # 법인 관리자 프로필
│   │   └── [기타 도메인 레포지토리...]
│   │
│   ├── models/                  # SQLAlchemy 모델 (도메인 엔티티)
│   │   ├── __init__.py          # 모든 모델 export
│   │   ├── employee.py          # 직원 모델
│   │   ├── user.py              # 사용자 계정 모델
│   │   ├── company.py           # 법인 모델
│   │   ├── organization.py      # 조직 구조 모델
│   │   ├── person_contract.py   # 개인-법인 계약
│   │   ├── personal_profile.py  # 개인 프로필
│   │   ├── corporate_admin_profile.py # 법인 관리자 프로필
│   │   ├── contract.py          # 근로계약
│   │   ├── salary.py, benefit.py, insurance.py
│   │   ├── education.py, career.py, certificate.py
│   │   ├── family_member.py, language.py, military_service.py
│   │   ├── promotion.py, evaluation.py, training.py
│   │   ├── attendance.py, asset.py, award.py
│   │   ├── hr_project.py, project_participation.py
│   │   ├── salary_history.py, salary_payment.py
│   │   ├── attachment.py
│   │   ├── notification.py
│   │   ├── audit_log.py
│   │   ├── classification_option.py
│   │   ├── system_setting.py
│   │   ├── domains/             # 도메인별 모델 그룹
│   │   └── personal/            # 개인 계정 전용 모델
│   │
│   ├── utils/                   # 유틸리티 모듈
│   │   ├── decorators.py        # 인증/권한 데코레이터
│   │   ├── context_processors.py # 템플릿 컨텍스트
│   │   ├── template_helpers.py  # 템플릿 헬퍼 함수
│   │   ├── employee_number.py   # 사번 생성
│   │   ├── tenant.py            # 멀티테넌시 유틸
│   │   ├── api_helpers.py       # API 헬퍼
│   │   ├── contract_helpers.py  # 계약 관련 헬퍼
│   │   ├── corporate_helpers.py # 법인 관련 헬퍼
│   │   └── personal_helpers.py  # 개인 계정 헬퍼
│   │
│   ├── adapters/                # 어댑터 레이어 (프로필 통합)
│   │   ├── __init__.py
│   │   └── profile_adapter.py   # 법인/개인 프로필 통합 어댑터
│   │
│   ├── components/              # 재사용 가능한 컴포넌트
│   │
│   ├── profile_config/          # 프로필 설정
│   │
│   ├── templates/               # Jinja2 템플릿 (뷰 레이어)
│   │   ├── base.html            # 기본 레이아웃
│   │   ├── auth/                # 인증 페이지
│   │   ├── dashboard/           # 대시보드
│   │   ├── employees/           # 직원 관리 UI
│   │   ├── profile/             # 통합 프로필 UI
│   │   ├── corporate/           # 법인 계정 UI
│   │   ├── personal/            # 개인 계정 UI
│   │   ├── contracts/           # 계약 관리 UI
│   │   ├── account/             # 계정 설정 UI
│   │   ├── mypage/              # 마이페이지 UI
│   │   ├── admin/               # 관리자 UI
│   │   ├── ai_test/             # AI 테스트 UI
│   │   ├── errors/              # 에러 페이지 (403, 404, 500)
│   │   ├── macros/              # 재사용 매크로
│   │   ├── partials/            # 부분 템플릿
│   │   └── components/          # UI 컴포넌트
│   │
│   └── static/                  # 정적 파일
│       ├── css/                 # 스타일시트
│       ├── js/                  # JavaScript
│       │   ├── app.js           # 앱 초기화
│       │   ├── components/      # 재사용 컴포넌트
│       │   │   ├── data-table/  # 데이터 테이블 컴포넌트
│       │   │   ├── salary/      # 급여 계산기
│       │   │   ├── file-upload.js
│       │   │   ├── filter.js
│       │   │   ├── section-nav.js
│       │   │   ├── toast.js
│       │   │   ├── tree-selector.js
│       │   │   ├── form-validator.js
│       │   │   ├── business-card.js
│       │   │   └── notification-dropdown.js
│       │   ├── pages/           # 페이지별 로직
│       │   │   ├── employee/    # 직원 관리 페이지
│       │   │   ├── profile/     # 프로필 페이지
│       │   │   ├── employee-list.js
│       │   │   ├── employee-form.js
│       │   │   ├── employee-detail.js
│       │   │   ├── contract-detail.js
│       │   │   ├── contracts.js
│       │   │   ├── corporate-users.js
│       │   │   ├── corporate-register.js
│       │   │   ├── auth.js
│       │   │   ├── dashboard.js
│       │   │   ├── organization.js
│       │   │   ├── admin.js
│       │   │   ├── classification-options.js
│       │   │   ├── ai-test-index.js
│       │   │   ├── ai-test-compare.js
│       │   │   └── error.js
│       │   ├── services/        # 프론트엔드 서비스 레이어
│       │   │   ├── employee-service.js
│       │   │   └── contract-service.js
│       │   └── utils/           # 유틸리티
│       │       ├── api.js       # API 통신
│       │       ├── dom.js       # DOM 조작
│       │       ├── events.js    # 이벤트 핸들링
│       │       ├── validation.js # 검증
│       │       ├── formatting.js # 포맷팅
│       │       ├── contract-api.js # 계약 API (deprecated)
│       │       └── index.js     # 유틸 통합 export
│       ├── images/              # 이미지 파일
│       └── uploads/             # 업로드된 파일
│
├── migrations/                  # Alembic 데이터베이스 마이그레이션
│   └── versions/
│
├── tests/                       # 테스트 코드
│   ├── unit/                    # 단위 테스트
│   │   ├── repositories/
│   │   └── services/
│   ├── integration/             # 통합 테스트
│   └── regression/              # 회귀 테스트
│
├── scripts/                     # 유틸리티 스크립트
│   ├── init-db/                 # DB 초기화
│   ├── migration/               # 마이그레이션 스크립트
│   └── archive/                 # 아카이브
│
├── data/                        # 데이터 파일
│   ├── backup/                  # 백업 데이터
│   └── db_files/                # DB 파일
│
├── backups/                     # 백업 아카이브
│
├── docs/                        # 문서
│   └── migration/
│
├── instance/                    # 인스턴스별 설정
│
├── .dev_docs/                   # 개발 문서
│   ├── dev_note.md
│   ├── dev_prompt.md
│   └── analysis/
│
├── requirements.txt             # Python 의존성
├── .env                         # 환경변수 (gitignore)
└── run.py                       # 애플리케이션 실행 진입점
```

---

## 레이어 아키텍처

본 프로젝트는 **3-Tier 레이어 아키텍처**를 기반으로 설계되었습니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (Flask Blueprints + Jinja2 Templates + JavaScript)         │
│                                                              │
│  - blueprints/      : 라우팅 및 HTTP 요청/응답 처리        │
│  - templates/       : HTML 뷰 렌더링                        │
│  - static/js/       : 클라이언트 사이드 로직               │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                     │
│                     (Service Layer)                          │
│                                                              │
│  - services/        : 비즈니스 로직 구현                   │
│  - utils/           : 헬퍼 함수 및 유틸리티                │
│  - adapters/        : 통합 어댑터 (법인/개인 프로필)       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│                (Repository Pattern)                          │
│                                                              │
│  - repositories/    : 데이터베이스 CRUD 추상화             │
│  - models/          : SQLAlchemy ORM 모델                   │
│  - database.py      : DB 연결 및 세션 관리                 │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                          │
│                      (PostgreSQL)                            │
└─────────────────────────────────────────────────────────────┘
```

### 레이어별 책임

#### 1. Presentation Layer (표현 계층)
- **역할**: HTTP 요청/응답 처리, 뷰 렌더링, 클라이언트 사이드 로직
- **구성요소**:
  - `blueprints/`: Flask Blueprint를 통한 라우팅 및 엔드포인트 정의
  - `templates/`: Jinja2 템플릿을 통한 서버 사이드 렌더링
  - `static/js/`: Vanilla JavaScript 기반 프론트엔드 로직
- **원칙**:
  - 비즈니스 로직 금지 (서비스 레이어 호출만)
  - 얇은 컨트롤러 유지
  - 입력 검증은 WTForms 활용

#### 2. Business Logic Layer (비즈니스 로직 계층)
- **역할**: 핵심 비즈니스 규칙 및 로직 구현
- **구성요소**:
  - `services/`: 도메인별 서비스 클래스 (트랜잭션 관리, 비즈니스 규칙 적용)
  - `utils/`: 공통 유틸리티 및 헬퍼 함수
  - `adapters/`: 레거시/멀티 소스 통합 어댑터
- **원칙**:
  - 레포지토리를 통해서만 데이터 접근
  - 트랜잭션 경계 설정
  - 도메인 이벤트 발행 및 처리

#### 3. Data Access Layer (데이터 접근 계층)
- **역할**: 데이터베이스 CRUD 연산 추상화
- **구성요소**:
  - `repositories/`: Repository Pattern 구현 (BaseRepository 상속)
  - `models/`: SQLAlchemy ORM 모델 정의
- **원칙**:
  - 모든 DB 쿼리는 레포지토리를 통해서만 실행
  - 모델은 순수 데이터 구조 + 기본 메서드만 포함
  - 복잡한 쿼리는 레포지토리에서 캡슐화

---

## 주요 컴포넌트 및 모듈

### 1. Backend 구조

#### 1.1 Flask App Factory Pattern
```python
# app/__init__.py
def create_app(config_name=None):
    """
    앱 팩토리 함수
    - 환경별 설정 로드 (development, production, testing)
    - 데이터베이스 초기화
    - 확장 초기화 (WTForms, CSRF 등)
    - Blueprint 등록
    - 에러 핸들러 등록
    """
```

**장점:**
- 환경별 설정 분리 (config.py)
- 테스트 용이성 (TestingConfig)
- 순환 의존성 해결

#### 1.2 Blueprint 구조
프로젝트는 **기능별 Blueprint 분리** 전략을 사용합니다.

| Blueprint | URL Prefix | 역할 |
|-----------|-----------|------|
| `auth_bp` | `/auth/*` | 인증 (로그인/로그아웃) |
| `admin_bp` | `/admin/*` | 관리자 기능 |
| `corporate_bp` | `/corporate/*` | 법인 계정 기능 |
| `personal_bp` | `/personal/*` | 개인 계정 기능 |
| `contracts_bp` | `/contracts/*` | 계약 관리 |
| `profile_bp` | `/profile/*` | 통합 프로필 |
| `account_bp` | `/account/*` | 계정 설정 |
| `mypage_bp` | `/my/*` | 마이페이지 (일반 직원) |
| `employees_bp` | `/employees/*` | 직원 CRUD |
| `main_bp` | `/`, `/search` | 메인 페이지, 검색 |
| `api_bp` | `/api/*` | REST API |
| `sync_bp` | `/api/sync/*` | 데이터 동기화 |
| `audit_bp` | `/api/audit/*` | 감사 로그 |
| `notifications_bp` | `/api/notifications/*` | 알림 시스템 |
| `classification_bp` | `/classification-options` | 분류 옵션 관리 |
| `ai_test_bp` | `/ai-test/*` | AI 테스트 (프로토타입) |

**모듈 분할 사례: employees Blueprint**
```
app/blueprints/employees/
├── __init__.py           # Blueprint 정의 및 라우터 통합
├── list_routes.py        # 목록 조회 라우트
└── mutation_routes.py    # 생성/수정/삭제 라우트
```

#### 1.3 Service Layer Pattern
비즈니스 로직을 서비스 레이어로 분리하여 관리합니다.

**주요 서비스:**
- `EmployeeService`: 직원 관리 (생성, 수정, 삭제, 조회)
- `EmployeeAccountService`: 직원 계정 관리
- `ContractService`: 계약 관리 로직
- `PersonalService`: 개인 계정 로직
- `CorporateAdminProfileService`: 법인 관리자 프로필
- `SyncService`: 데이터 동기화 (개인↔법인)
- `TerminationService`: 퇴직 처리
- `AuditService`: 감사 로그 기록
- `NotificationService`: 알림 발송
- `FileStorageService`: 파일 업로드/다운로드
- `AIService`: AI 기능 (Gemini API)

**서비스 레이어 패턴 예시:**
```python
# app/services/employee_service.py
class EmployeeService:
    def __init__(self):
        self.employee_repo = EmployeeRepository()
        self.education_repo = EducationRepository()
        # ... 다른 레포지토리들

    def create_employee(self, data: dict) -> Employee:
        """직원 생성 (트랜잭션 관리)"""
        # 1. 비즈니스 검증
        # 2. 레포지토리를 통한 데이터 생성
        # 3. 연관 데이터 처리
        # 4. 이벤트 발행
        # 5. 트랜잭션 커밋
```

#### 1.4 Repository Pattern
모든 데이터 접근은 레포지토리를 통해 추상화됩니다.

**BaseRepository:**
```python
# app/repositories/base_repository.py
class BaseRepository:
    """공통 CRUD 메서드를 제공하는 기본 레포지토리"""
    def __init__(self, model_class):
        self.model = model_class

    def find_all(self):
        """모든 레코드 조회"""

    def find_by_id(self, id):
        """ID로 단일 레코드 조회"""

    def create(self, data):
        """레코드 생성"""

    def update(self, id, data):
        """레코드 수정"""

    def delete(self, id):
        """레코드 삭제"""
```

**도메인별 레포지토리 확장:**
```python
# app/repositories/employee_repository.py
class EmployeeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Employee)

    def find_by_department(self, department):
        """부서별 직원 조회 (커스텀 쿼리)"""
        return self.model.query.filter_by(department=department).all()
```

#### 1.5 Models (Domain Entities)
SQLAlchemy ORM을 사용한 도메인 모델 정의.

**주요 모델:**
- **계정 관련**: `User`, `Company`, `Organization`
- **직원 관리**: `Employee`, `Education`, `Career`, `Certificate`, `FamilyMember`, `Language`, `MilitaryService`
- **급여/복리후생**: `Salary`, `SalaryHistory`, `SalaryPayment`, `Benefit`, `Insurance`
- **계약**: `Contract`, `PersonCorporateContract`, `DataSharingSettings`
- **인사평가**: `Promotion`, `Evaluation`, `Training`
- **근태/자산**: `Attendance`, `Asset`, `Award`
- **프로젝트**: `HrProject`, `ProjectParticipation`
- **개인 계정**: `PersonalProfile`, `PersonalEducation`, `PersonalCareer`, `PersonalCertificate`, `PersonalLanguage`, `PersonalMilitaryService`
- **법인 관리자**: `CorporateAdminProfile`
- **시스템**: `Notification`, `NotificationPreference`, `AuditLog`, `SyncLog`, `Attachment`, `ClassificationOption`, `SystemSetting`

**관계 설정 예시:**
```python
# Employee ↔ Education (1:N)
educations = db.relationship('Education', backref='employee', lazy='dynamic', cascade='all, delete-orphan')

# Employee ↔ Salary (1:1)
salary = db.relationship('Salary', backref='employee', uselist=False, cascade='all, delete-orphan')

# Company ↔ Organization (1:1)
root_organization = db.relationship('Organization', foreign_keys=[root_organization_id], backref=db.backref('company', uselist=False))
```

### 2. Frontend 구조

#### 2.1 템플릿 구조 (Jinja2)
```
templates/
├── base.html                   # 기본 레이아웃 (네비게이션, 푸터)
├── macros/                     # 재사용 가능한 매크로
│   └── _navigation.html
├── partials/                   # 부분 템플릿
├── components/                 # UI 컴포넌트
└── [기능별 디렉토리]/
    ├── list.html               # 목록 페이지
    ├── form.html               # 생성/수정 폼
    └── detail.html             # 상세 페이지
```

**템플릿 상속 구조:**
```jinja2
base.html
  ↓ extends
employees/list.html
  ↓ includes
macros/_navigation.html
partials/employee_form/_basic_info.html
```

#### 2.2 JavaScript 컴포넌트 아키텍처
Vanilla JavaScript 기반 모듈화된 컴포넌트 구조.

**디렉토리 구조:**
```
static/js/
├── app.js                      # 앱 초기화 및 전역 설정
├── components/                 # 재사용 가능한 UI 컴포넌트
│   ├── data-table/             # 고급 데이터 테이블
│   │   ├── index.js            # 메인 모듈
│   │   ├── column-manager.js   # 컬럼 관리
│   │   ├── filter-manager.js   # 필터링
│   │   ├── pagination-manager.js # 페이지네이션
│   │   ├── selection-manager.js  # 선택 관리
│   │   ├── cell-renderer.js    # 셀 렌더링
│   │   ├── excel-exporter.js   # 엑셀 내보내기
│   │   └── storage-manager.js  # 로컬 스토리지
│   ├── salary/                 # 급여 계산기
│   ├── file-upload.js
│   ├── filter.js
│   ├── section-nav.js
│   ├── toast.js                # 토스트 알림
│   ├── tree-selector.js        # 트리 선택기 (조직도)
│   ├── form-validator.js       # 폼 검증
│   ├── business-card.js        # 명함 관리
│   └── notification-dropdown.js # 알림 드롭다운
├── pages/                      # 페이지별 진입점 스크립트
│   ├── employee/               # 직원 관리 페이지
│   │   ├── index.js            # 메인 진입점
│   │   ├── validators.js       # 검증 로직
│   │   ├── section-nav-init.js # 섹션 내비게이션
│   │   ├── file-upload-init.js # 파일 업로드 초기화
│   │   ├── dynamic-sections.js # 동적 섹션 관리
│   │   ├── address-search.js   # 주소 검색
│   │   ├── helpers.js          # 헬퍼 함수
│   │   ├── templates.js        # HTML 템플릿
│   │   ├── photo-upload.js     # 사진 업로드
│   │   ├── business-card.js    # 명함 관리
│   │   └── account-section.js  # 계정 섹션
│   ├── profile/                # 프로필 페이지
│   ├── employee-list.js
│   ├── employee-form.js
│   ├── employee-detail.js
│   ├── contract-detail.js
│   └── [기타 페이지...]
├── services/                   # 프론트엔드 서비스 레이어
│   ├── employee-service.js     # 직원 관련 API 호출
│   └── contract-service.js     # 계약 관련 API 호출
└── utils/                      # 유틸리티
    ├── api.js                  # API 통신 헬퍼
    ├── dom.js                  # DOM 조작
    ├── events.js               # 이벤트 핸들링
    ├── validation.js           # 클라이언트 검증
    ├── formatting.js           # 데이터 포맷팅
    └── index.js                # 유틸 통합 export
```

**컴포넌트 패턴 예시:**
```javascript
// components/toast.js
export class Toast {
    constructor(options) {
        this.container = options.container || document.body;
    }

    show(message, type = 'info') {
        // 토스트 메시지 표시 로직
    }

    hide() {
        // 토스트 메시지 숨김 로직
    }
}

// pages/employee-list.js
import { Toast } from '../components/toast.js';

document.addEventListener('DOMContentLoaded', () => {
    const toast = new Toast();
    toast.show('직원 목록을 불러왔습니다.', 'success');
});
```

---

## 디자인 패턴

### 1. Factory Pattern (App Factory)
```python
# app/__init__.py
def create_app(config_name=None):
    """
    앱 팩토리 패턴
    - 환경별 설정 분리
    - 테스트 용이성
    - 순환 의존성 방지
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 의존성 주입
    db.init_app(app)
    register_blueprints(app)

    return app
```

**장점:**
- 환경별 설정 분리 (개발/운영/테스트)
- 테스트 시 Mock 설정 주입 용이
- 순환 import 방지

### 2. Repository Pattern
```python
# app/repositories/base_repository.py
class BaseRepository:
    """데이터 접근 추상화"""
    def __init__(self, model_class):
        self.model = model_class

    def find_all(self):
        return self.model.query.all()

    def find_by_id(self, id):
        return self.model.query.get(id)

# app/repositories/employee_repository.py
class EmployeeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Employee)

    def find_by_department(self, department):
        """커스텀 쿼리 메서드"""
        return self.model.query.filter_by(department=department).all()
```

**장점:**
- 데이터 접근 로직 캡슐화
- 테스트 시 Mock Repository 주입 용이
- 쿼리 재사용성 및 유지보수성 향상

### 3. Service Layer Pattern
```python
# app/services/employee_service.py
class EmployeeService:
    """비즈니스 로직 계층"""
    def __init__(self):
        self.employee_repo = EmployeeRepository()
        self.education_repo = EducationRepository()

    def create_employee(self, data):
        """
        직원 생성 (트랜잭션 관리)
        1. 비즈니스 검증
        2. 데이터 생성
        3. 연관 데이터 처리
        4. 이벤트 발행
        """
        try:
            employee = self.employee_repo.create(data)
            # 교육 이력 추가
            for edu_data in data.get('educations', []):
                self.education_repo.create({**edu_data, 'employee_id': employee.id})
            db.session.commit()
            return employee
        except Exception as e:
            db.session.rollback()
            raise
```

**장점:**
- 비즈니스 로직 중앙화
- 트랜잭션 경계 명확화
- 복잡한 비즈니스 규칙 캡슐화

### 4. Decorator Pattern (인증/권한)
```python
# app/utils/decorators.py
def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def corporate_admin_required(f):
    """법인 관리자 권한 필수"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('account_type') != 'corporate':
            abort(403)
        if session.get('user_role') not in ('admin', 'manager'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# 사용 예시
@corporate_bp.route('/users')
@corporate_admin_required
def manage_users():
    """법인 관리자만 접근 가능"""
    pass
```

**데코레이터 종류:**
- `@login_required`: 로그인 필수
- `@admin_required`: 관리자 전용
- `@role_required('admin', 'manager')`: 특정 역할 필수
- `@corporate_login_required`: 법인 계정 전용
- `@personal_login_required`: 개인 계정 전용
- `@corporate_admin_required`: 법인 관리자 전용
- `@self_or_admin_required`: 본인 또는 관리자
- `@contract_access_required`: 계약 당사자만 접근

**장점:**
- 횡단 관심사 분리 (Cross-Cutting Concerns)
- 코드 중복 제거
- 라우트별 권한 제어 명확화

### 5. Adapter Pattern (프로필 통합)
```python
# app/adapters/profile_adapter.py
class ProfileAdapter:
    """
    법인 직원 프로필 ↔ 개인 프로필 통합 어댑터
    - 다양한 소스에서 프로필 정보를 통합
    - 계정 타입에 따라 적절한 데이터 반환
    """
    def get_unified_profile(self, user_id, account_type):
        """통합 프로필 조회"""
        if account_type == 'corporate':
            return self._get_corporate_profile(user_id)
        elif account_type == 'personal':
            return self._get_personal_profile(user_id)
```

**장점:**
- 레거시 시스템 통합
- 인터페이스 호환성 제공
- 다양한 데이터 소스 추상화

### 6. Event Listener Pattern
```python
# app/services/event_listeners.py
class SyncEventManager:
    """데이터 동기화 이벤트 관리"""
    @staticmethod
    def after_employee_update(mapper, connection, target):
        """직원 정보 변경 후 개인 프로필 동기화"""
        # 이벤트 처리 로직
        pass

def init_event_listeners(app):
    """SQLAlchemy 이벤트 리스너 등록"""
    from sqlalchemy import event
    event.listen(Employee, 'after_update', SyncEventManager.after_employee_update)
```

**장점:**
- 느슨한 결합 (Loose Coupling)
- 이벤트 기반 아키텍처 구현
- 동기화 로직 분리

---

## 의존성 흐름

### Backend 의존성 다이어그램

```
┌────────────────┐
│   Blueprint    │  (라우팅, HTTP 요청/응답)
│  (Controller)  │
└────────┬───────┘
         │ 호출
         ↓
┌────────────────┐
│    Service     │  (비즈니스 로직, 트랜잭션 관리)
│  (EmployeeSvc) │
└────────┬───────┘
         │ 호출
         ↓
┌────────────────┐
│   Repository   │  (데이터 접근 추상화, CRUD)
│  (EmployeeRepo)│
└────────┬───────┘
         │ 쿼리
         ↓
┌────────────────┐
│     Model      │  (ORM 엔티티, 데이터 구조)
│   (Employee)   │
└────────┬───────┘
         │ 매핑
         ↓
┌────────────────┐
│   Database     │  (PostgreSQL)
│   (Postgres)   │
└────────────────┘
```

### 의존성 규칙
1. **상위 레이어는 하위 레이어만 의존**
   - Blueprint → Service → Repository → Model
   - 역방향 의존성 금지
2. **인터페이스를 통한 의존성 주입**
   - Service는 Repository 인터페이스에 의존
   - 테스트 시 Mock 주입 가능
3. **순환 의존성 방지**
   - App Factory 패턴 활용
   - Late Import 사용

### 실제 호출 흐름 예시
```python
# 1. Blueprint (employees/mutation_routes.py)
@employees_bp.route('/create', methods=['POST'])
@corporate_login_required
def create_employee():
    data = request.get_json()
    employee = employee_service.create_employee(data)  # 서비스 호출
    return jsonify(employee.to_dict())

# 2. Service (employee_service.py)
class EmployeeService:
    def create_employee(self, data):
        # 비즈니스 검증
        self._validate_employee_data(data)

        # 레포지토리 호출
        employee = self.employee_repo.create(data)

        # 연관 데이터 처리
        for edu in data.get('educations', []):
            self.education_repo.create({**edu, 'employee_id': employee.id})

        # 트랜잭션 커밋
        db.session.commit()
        return employee

# 3. Repository (employee_repository.py)
class EmployeeRepository(BaseRepository):
    def create(self, data):
        employee = Employee.from_dict(data)
        db.session.add(employee)
        return employee

# 4. Model (employee.py)
class Employee(db.Model):
    @classmethod
    def from_dict(cls, data):
        return cls(name=data['name'], ...)
```

---

## 멀티테넌시 구조

본 시스템은 **법인 계정 기반 멀티테넌시**를 구현하고 있습니다.

### 테넌트 격리 전략

```
┌─────────────────────────────────────────┐
│          Platform Level                  │
│  (HRM Platform - Multi-Tenant SaaS)      │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴──────────┐
       │                  │
┌──────▼──────┐   ┌──────▼──────┐
│  Company A  │   │  Company B  │  (Tenant 격리)
│  (Tenant 1) │   │  (Tenant 2) │
└──────┬──────┘   └──────┬──────┘
       │                  │
┌──────▼──────┐   ┌──────▼──────┐
│Organization │   │Organization │  (조직 구조)
│    Tree     │   │    Tree     │
└──────┬──────┘   └──────┬──────┘
       │                  │
┌──────▼──────┐   ┌──────▼──────┐
│ Employees   │   │ Employees   │  (직원 데이터)
│   (격리)    │   │   (격리)    │
└─────────────┘   └─────────────┘
```

### 핵심 모델 관계

```python
# Company (법인) - 테넌트의 최상위 엔티티
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_number = db.Column(db.String(20), unique=True)  # 사업자등록번호
    root_organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    # 조직 구조의 루트 노드와 연결

# Organization (조직) - 계층 구조
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))  # 자기 참조
    # 트리 구조 형성

# Employee (직원) - 조직에 소속
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    # 특정 조직에 소속
```

### 테넌트 격리 메커니즘

#### 1. 세션 기반 테넌트 식별
```python
# 로그인 시 세션에 테넌트 정보 저장
session['company_id'] = user.company_id
session['account_type'] = 'corporate'
```

#### 2. 데코레이터를 통한 테넌트 필터링
```python
@corporate_login_required
def view_employees():
    """현재 로그인한 법인의 직원만 조회"""
    company_id = session.get('company_id')
    employees = Employee.query.join(Organization).filter(
        Organization.company_id == company_id
    ).all()
```

#### 3. Repository 레벨 테넌트 필터
```python
class EmployeeRepository:
    def find_by_company(self, company_id):
        """특정 법인의 직원만 조회"""
        return Employee.query.join(Organization).filter(
            Organization.company_id == company_id
        ).all()
```

### 데이터 격리 보장
1. **DB 레벨**: 외래 키 제약 조건으로 데이터 무결성 보장
2. **Application 레벨**: 모든 쿼리에 company_id 필터 적용
3. **UI 레벨**: 세션 정보 기반 UI 렌더링

---

## 인증/권한 시스템

### 인증 구조

```
┌─────────────────────────────────────────┐
│         Authentication Flow              │
└─────────────────────────────────────────┘

1. Login Request
   ↓
2. User Model 조회 (email/password 검증)
   ↓
3. Session 생성
   - session['user_id']
   - session['account_type']  # 'corporate' or 'personal'
   - session['user_role']     # 'admin', 'manager', 'employee'
   - session['company_id']    # 법인 계정인 경우
   ↓
4. Redirect to Dashboard
```

### 계정 타입
```python
# User Model
class User(db.Model):
    ACCOUNT_TYPE_CORPORATE = 'corporate'  # 법인 계정
    ACCOUNT_TYPE_PERSONAL = 'personal'    # 개인 계정
    ACCOUNT_TYPE_EMPLOYEE_SUB = 'employee_sub'  # 직원 서브 계정
```

### 역할 (Role)
```python
USER_ROLE_ADMIN = 'admin'        # 최고 관리자
USER_ROLE_MANAGER = 'manager'    # 중간 관리자
USER_ROLE_EMPLOYEE = 'employee'  # 일반 직원
```

### 권한 매트릭스

| 기능 | Admin | Manager | Employee |
|------|-------|---------|----------|
| 직원 생성/수정/삭제 | ✅ | ✅ | ❌ |
| 직원 조회 | ✅ | ✅ | 본인만 |
| 급여 정보 열람 | ✅ | ✅ | 본인만 |
| 계약 승인/거절 | ✅ | ✅ | 본인만 |
| 조직 관리 | ✅ | ✅ | ❌ |
| 법인 설정 | ✅ | ❌ | ❌ |
| 사용자 관리 | ✅ | ❌ | ❌ |

### 데코레이터 사용 패턴

```python
# 1. 로그인 필수
@login_required
def view_profile():
    pass

# 2. 법인 계정 전용
@corporate_login_required
def corporate_dashboard():
    pass

# 3. 개인 계정 전용
@personal_login_required
def personal_dashboard():
    pass

# 4. 관리자 전용
@admin_required
def manage_company():
    pass

# 5. 관리자 또는 매니저
@role_required('admin', 'manager')
def manage_employees():
    pass

# 6. 본인 또는 관리자
@self_or_admin_required('employee_id')
def view_employee_detail(employee_id):
    pass

# 7. 법인 관리자 전용
@corporate_admin_required
def manage_corporate_users():
    pass

# 8. 계약 당사자만 접근
@contract_access_required
def view_contract(contract_id):
    pass
```

---

## 데이터 흐름

### 1. 직원 생성 요청 (Create Employee)

```
[Client] → [Blueprint] → [Service] → [Repository] → [Database]
   ↓           ↓             ↓            ↓            ↓
 HTTP       라우팅      비즈니스       CRUD        INSERT
Request     검증         로직         쿼리         실행

← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
JSON Response (201 Created)
```

**상세 흐름:**
```
1. Client (JavaScript)
   - POST /employees/create
   - Body: { name, department, ... }

2. Blueprint (employees/mutation_routes.py)
   - @corporate_login_required 검증
   - request.get_json() 파싱
   - employee_service.create_employee(data) 호출

3. Service (employee_service.py)
   - 비즈니스 검증 (_validate_employee_data)
   - 사번 생성 (employee_number)
   - employee_repo.create(data)
   - 연관 데이터 생성 (education, career, ...)
   - db.session.commit()

4. Repository (employee_repository.py)
   - Employee.from_dict(data)
   - db.session.add(employee)
   - return employee

5. Model (employee.py)
   - ORM 객체 생성
   - 유효성 검증 (nullable, constraints)

6. Database (PostgreSQL)
   - INSERT INTO employees (...) VALUES (...)
   - 트랜잭션 커밋
```

### 2. 직원 목록 조회 (List Employees)

```
[Client] → [Blueprint] → [Service] → [Repository] → [Database]
   ↓           ↓             ↓            ↓            ↓
 HTTP       라우팅        필터링       쿼리         SELECT
Request     페이징       정렬         빌드         실행

← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
JSON Response (200 OK)
```

**상세 흐름:**
```
1. Client (JavaScript)
   - GET /employees/list?page=1&size=20&department=개발팀

2. Blueprint (employees/list_routes.py)
   - @corporate_login_required 검증
   - 쿼리 파라미터 파싱
   - employee_service.list_employees(filters) 호출

3. Service (employee_service.py)
   - 테넌트 필터링 (company_id)
   - 페이징 처리
   - employee_repo.find_with_filters(filters)

4. Repository (employee_repository.py)
   - Query 빌드 (filter, order_by, limit, offset)
   - db.session.execute(query)
   - return [employee.to_dict() for employee in results]

5. Database (PostgreSQL)
   - SELECT * FROM employees WHERE company_id = ? LIMIT ? OFFSET ?
   - 결과 반환
```

### 3. 개인-법인 데이터 동기화 (Sync)

```
[법인 직원 데이터] ←→ [개인 프로필 데이터]
        ↓                      ↓
   [SyncService]      [PersonalService]
        ↓                      ↓
   [SyncLog]           [DataSharingSettings]
```

**동기화 흐름:**
```
1. 법인에서 직원 정보 수정
   ↓
2. SQLAlchemy Event Listener 트리거
   - after_update(Employee)
   ↓
3. SyncEventManager.after_employee_update()
   - 개인 계정 연결 확인 (PersonCorporateContract)
   - DataSharingSettings 확인 (동기화 허용 필드)
   ↓
4. SyncService.sync_to_personal()
   - 허용된 필드만 개인 프로필로 복사
   - SyncLog 기록
   ↓
5. PersonalProfile 업데이트
   - 개인 계정 데이터 동기화 완료
```

---

## 기술 스택

### Backend
| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| **Framework** | Flask | 2.3.0+ | 웹 애플리케이션 프레임워크 |
| **ORM** | SQLAlchemy | 2.0.0+ | 데이터베이스 ORM |
| **Database** | PostgreSQL | - | 관계형 데이터베이스 |
| **Migration** | Alembic | 1.13.1+ | DB 스키마 마이그레이션 |
| **Forms** | WTForms | 3.0.0+ | 폼 검증 |
| **WSGI Server** | Gunicorn | 21.0.0+ | 프로덕션 서버 |
| **AI** | Google Gemini API | 0.8.0+ | AI 서비스 (텍스트 생성) |
| **OCR** | Google Cloud Vision | 3.7.0+ | 광학 문자 인식 |
| **Document AI** | Google Cloud Document AI | 2.20.0+ | 문서 처리 |
| **PDF** | PyMuPDF | 1.23.0+ | PDF 처리 |
| **HTTP Client** | Requests | 2.31.0+ | HTTP 요청 (Local LLM) |
| **Configuration** | python-dotenv | 1.0.0+ | 환경변수 관리 |

### Frontend
| 구분 | 기술 | 용도 |
|------|------|------|
| **Template Engine** | Jinja2 | 서버 사이드 렌더링 |
| **JavaScript** | Vanilla JS (ES6+) | 클라이언트 사이드 로직 |
| **CSS Framework** | Custom CSS | 스타일링 |
| **Module System** | ES Modules | JavaScript 모듈화 |

### Infrastructure
| 구분 | 기술 | 용도 |
|------|------|------|
| **Web Server** | Nginx (권장) | 리버스 프록시, 정적 파일 서빙 |
| **Database** | PostgreSQL | 데이터 저장 |
| **Session** | Flask Session (Server-side) | 세션 관리 |
| **File Storage** | 로컬 파일 시스템 | 업로드 파일 저장 |

### Development Tools
| 구분 | 기술 | 용도 |
|------|------|------|
| **Version Control** | Git | 소스 코드 버전 관리 |
| **Testing** | pytest (계획) | 단위/통합 테스트 |
| **Code Quality** | - | 정적 분석 (미적용) |

---

## 개선 권장 사항

### 1. 아키텍처 개선

#### 1.1 API 레이어 분리
**현재 상황:**
- Blueprint에 웹 페이지 라우트와 API 엔드포인트가 혼재

**개선 방안:**
```python
# 현재
@employees_bp.route('/list')
def list_employees_page():
    """HTML 페이지 반환"""
    return render_template('employees/list.html')

@employees_bp.route('/api/list')
def list_employees_api():
    """JSON 응답 반환"""
    return jsonify(employees)

# 개선안
# blueprints/api/v1/employees.py
@api_v1_bp.route('/employees')
def list_employees():
    """REST API 전용"""
    return jsonify(employees)

# blueprints/web/employees.py
@web_bp.route('/employees')
def employees_page():
    """웹 페이지 전용"""
    return render_template('employees/list.html')
```

**기대 효과:**
- API 버전 관리 용이 (/api/v1, /api/v2)
- 웹 페이지와 API 로직 분리
- RESTful API 설계 명확화

#### 1.2 DTO (Data Transfer Object) 패턴 도입
**현재 상황:**
- 딕셔너리 기반 데이터 전달
- 타입 안정성 부족

**개선 방안:**
```python
# dtos/employee_dto.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateEmployeeDTO:
    name: str
    department: str
    position: Optional[str] = None
    email: Optional[str] = None

    def validate(self):
        """검증 로직"""
        if not self.name:
            raise ValueError("이름은 필수입니다.")

# Service에서 사용
def create_employee(self, dto: CreateEmployeeDTO):
    dto.validate()
    employee = self.employee_repo.create(dto.__dict__)
```

**기대 효과:**
- 타입 안정성 향상
- 검증 로직 캡슐화
- IDE 자동완성 지원

#### 1.3 의존성 주입 (Dependency Injection) 컨테이너
**현재 상황:**
- 수동 의존성 생성 (직접 인스턴스화)

**개선 방안:**
```python
# dependency_injection.py
from flask_injector import FlaskInjector
from injector import singleton

def configure(binder):
    binder.bind(EmployeeRepository, to=EmployeeRepository, scope=singleton)
    binder.bind(EmployeeService, to=EmployeeService, scope=singleton)

# app/__init__.py
FlaskInjector(app=app, modules=[configure])

# Blueprint에서 사용
@employees_bp.route('/list')
def list_employees(employee_service: EmployeeService):
    """자동 주입"""
    employees = employee_service.list_employees()
```

**기대 효과:**
- 테스트 용이성 (Mock 주입)
- 싱글톤 관리 자동화
- 의존성 명시적 선언

### 2. 데이터베이스 개선

#### 2.1 인덱스 최적화
**분석 필요 영역:**
```sql
-- 자주 사용되는 쿼리 패턴 분석
-- 1. 법인별 직원 조회
SELECT * FROM employees
WHERE organization_id IN (SELECT id FROM organizations WHERE company_id = ?)
-- → organizations.company_id에 인덱스 필요

-- 2. 부서별 직원 검색
SELECT * FROM employees WHERE department = ?
-- → employees.department에 인덱스 필요

-- 3. 사번 검색
SELECT * FROM employees WHERE employee_number = ?
-- → employees.employee_number에 UNIQUE 인덱스 (이미 존재)
```

**권장 인덱스:**
```python
# models/employee.py
class Employee(db.Model):
    __table_args__ = (
        db.Index('ix_employee_department', 'department'),
        db.Index('ix_employee_status', 'status'),
        db.Index('ix_employee_hire_date', 'hire_date'),
    )
```

#### 2.2 쿼리 최적화 (N+1 문제 해결)
**현재 상황:**
```python
# N+1 문제 발생
employees = Employee.query.all()
for emp in employees:
    print(emp.organization.name)  # 각 직원마다 쿼리 실행
```

**개선 방안:**
```python
# Eager Loading 사용
employees = Employee.query.options(
    db.joinedload(Employee.organization)
).all()
```

#### 2.3 데이터베이스 파티셔닝 (대규모 데이터 대비)
**미래 확장 대비:**
- 법인별 테이블 파티셔닝
- 날짜별 로그 테이블 파티셔닝

### 3. 보안 개선

#### 3.1 CSRF 토큰 검증 강화
**현재:**
- WTForms CSRF 활성화

**개선:**
- AJAX 요청에도 CSRF 토큰 포함
```javascript
// static/js/utils/api.js
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/employees', {
    headers: {
        'X-CSRFToken': csrfToken
    }
});
```

#### 3.2 SQL Injection 방지
**현재:**
- SQLAlchemy ORM 사용으로 기본 방어

**추가 개선:**
- Raw SQL 사용 금지
- 파라미터 바인딩 강제

#### 3.3 민감 정보 암호화
**개선 필요:**
```python
# models/employee.py
from cryptography.fernet import Fernet

class Employee(db.Model):
    _resident_number = db.Column('resident_number', db.String(200))  # 암호화 저장

    @property
    def resident_number(self):
        """복호화하여 반환"""
        return decrypt(self._resident_number)

    @resident_number.setter
    def resident_number(self, value):
        """암호화하여 저장"""
        self._resident_number = encrypt(value)
```

### 4. 성능 개선

#### 4.1 캐싱 도입
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)
def get_classification_options():
    """분류 옵션 캐싱 (5분)"""
    return ClassificationOption.query.all()
```

#### 4.2 페이지네이션 최적화
```python
# Repository에서 페이지네이션 처리
def find_paginated(self, page=1, per_page=20, filters=None):
    query = self.model.query
    if filters:
        query = query.filter_by(**filters)
    return query.paginate(page=page, per_page=per_page)
```

#### 4.3 정적 파일 CDN 배포
- CSS/JS/이미지를 CDN으로 서빙
- 번들링 및 압축 (Webpack 도입 고려)

### 5. 테스트 개선

#### 5.1 단위 테스트 커버리지 확대
**현재:**
- tests/ 디렉토리 존재하나 미흡

**목표:**
- 서비스 레이어 80% 이상 커버리지
- 레포지토리 90% 이상 커버리지

```python
# tests/unit/services/test_employee_service.py
import pytest
from app.services import EmployeeService

def test_create_employee(mock_employee_repo):
    service = EmployeeService()
    service.employee_repo = mock_employee_repo

    employee = service.create_employee({'name': '홍길동'})
    assert employee.name == '홍길동'
```

#### 5.2 통합 테스트 추가
```python
# tests/integration/test_employee_flow.py
def test_employee_crud_flow(client):
    # 1. 생성
    resp = client.post('/employees/create', json={'name': '홍길동'})
    assert resp.status_code == 201

    # 2. 조회
    employee_id = resp.json['id']
    resp = client.get(f'/employees/{employee_id}')
    assert resp.json['name'] == '홍길동'

    # 3. 수정
    resp = client.put(f'/employees/{employee_id}', json={'name': '김철수'})
    assert resp.status_code == 200

    # 4. 삭제
    resp = client.delete(f'/employees/{employee_id}')
    assert resp.status_code == 204
```

### 6. 코드 품질 개선

#### 6.1 정적 분석 도구 도입
```bash
# Linting
pip install pylint flake8

# Type Checking
pip install mypy

# .pylintrc
[MASTER]
max-line-length=120
```

#### 6.2 코드 리뷰 체크리스트
- [ ] 레이어 아키텍처 준수
- [ ] 데코레이터 적절히 사용
- [ ] 트랜잭션 경계 명확
- [ ] 에러 핸들링 포함
- [ ] 로깅 적절히 기록

### 7. 모니터링 및 로깅

#### 7.1 구조화된 로깅
```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

logger.info("직원 생성", extra={
    'employee_id': employee.id,
    'user_id': session.get('user_id'),
    'action': 'create_employee'
})
```

#### 7.2 성능 모니터링
```python
from flask import g
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start_time
    logger.info(f"Request took {diff:.2f}s", extra={
        'path': request.path,
        'method': request.method,
        'duration': diff
    })
    return response
```

### 8. 문서화 개선

#### 8.1 API 문서 자동화
```python
# Flask-RESTX 또는 OpenAPI 도입
from flask_restx import Api, Resource

api = Api(app, version='1.0', title='HR Management API')

@api.route('/employees')
class EmployeeList(Resource):
    @api.doc('list_employees')
    def get(self):
        """직원 목록 조회"""
        pass
```

#### 8.2 코드 주석 및 Docstring 표준화
```python
def create_employee(self, data: dict) -> Employee:
    """
    직원을 생성합니다.

    Args:
        data (dict): 직원 정보 딕셔너리
            - name (str, required): 직원 이름
            - department (str, optional): 부서명

    Returns:
        Employee: 생성된 직원 객체

    Raises:
        ValueError: 필수 필드가 누락된 경우
        DatabaseError: DB 저장 실패 시

    Example:
        >>> service.create_employee({'name': '홍길동', 'department': '개발팀'})
        <Employee id=1 name='홍길동'>
    """
```

---

## 결론

본 HR Management System은 **3-Tier 레이어 아키텍처**, **Repository Pattern**, **Service Layer Pattern**, **Factory Pattern** 등 검증된 디자인 패턴을 기반으로 설계되었습니다.

**강점:**
1. 명확한 레이어 분리 (Presentation, Business, Data Access)
2. 멀티테넌시 구조 구현 (법인별 데이터 격리)
3. 유연한 권한 시스템 (데코레이터 기반)
4. 확장 가능한 컴포넌트 구조 (Frontend/Backend 모두)

**개선 영역:**
1. API 레이어 분리 및 REST 표준화
2. 의존성 주입 컨테이너 도입
3. 테스트 커버리지 확대
4. 성능 최적화 (캐싱, 인덱싱)
5. 보안 강화 (암호화, CSRF)
6. 모니터링 및 로깅 체계화

본 문서는 프로젝트의 현재 아키텍처를 정확히 반영하고 있으며, 향후 리팩토링 및 확장 시 참고 자료로 활용할 수 있습니다.

---

**문서 버전:** 1.0
**작성일:** 2025-12-16
**최종 수정일:** 2025-12-16
