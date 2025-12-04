# HR Management 리팩토링 워크플로우

## 개요

**목적**: 코드 중복 제거 및 모듈화를 통한 코드 품질 개선
**총 예상 작업**: 5 Phase
**분석 기준일**: 2025-12-04

---

## 현재 상태 분석

### 식별된 문제점

| 우선순위 | 문제 | 위치 | 영향도 |
|---------|------|------|--------|
| P1 | 데코레이터 5개 파일 중복 | personal.py, corporate.py, contracts.py, sync.py, admin/audit.py | 높음 |
| P1 | get_current_organization_id() 중복 | main.py, employees.py | 중간 |
| P1 | employees.py 1,268줄 (권장 500-800줄 초과) | app/blueprints/employees.py | 높음 |
| P2 | personal_profile.py 6개 클래스 한 파일 | app/models/personal_profile.py | 중간 |
| P2 | employee_detail() 140줄 (권장 50줄 이하) | employees.py | 중간 |

---

## Phase 1: 데코레이터 통합

### 작업 목록

- [ ] 1.1 `app/utils/decorators.py` 확장
  - [ ] `account_type_required(account_type: str)` 추가
  - [ ] `personal_login_required` 추가
  - [ ] `corporate_login_required` 추가
  - [ ] `corporate_admin_required` 추가
  - [ ] `contract_access_required` 추가

- [ ] 1.2 Blueprint 파일에서 인라인 데코레이터 제거
  - [ ] `app/blueprints/personal.py` - personal_login_required 제거 및 import 변경
  - [ ] `app/blueprints/corporate.py` - corporate_login_required, corporate_admin_required 제거
  - [ ] `app/blueprints/contracts.py` - login_required, personal_account_required, corporate_account_required 제거
  - [ ] `app/blueprints/sync.py` - 동일 데코레이터 제거
  - [ ] `app/blueprints/admin/audit.py` - login_required, admin_required 제거

### 검증 체크리스트

- [ ] 서버 기동 확인 (`python run.py`)
- [ ] 로그인/로그아웃 테스트
- [ ] 개인 계정 접근 테스트
- [ ] 법인 계정 접근 테스트
- [ ] 관리자 권한 테스트

### Git 커밋

```bash
git add app/utils/decorators.py app/blueprints/
git commit -m "refactor: 데코레이터 통합 (5개 파일 중복 제거)

- account_type_required, personal_login_required 등 추가
- personal.py, corporate.py, contracts.py, sync.py, admin/audit.py에서 인라인 데코레이터 제거
- DRY 원칙 적용으로 유지보수성 향상"
```

---

## Phase 2: 멀티테넌시 헬퍼 통합

### 작업 목록

- [ ] 2.1 `app/utils/tenant.py` 신규 생성
  - [ ] `get_current_organization_id()` 함수 구현
  - [ ] `get_current_company_id()` 함수 구현
  - [ ] `get_current_company()` 함수 구현

- [ ] 2.2 Blueprint 파일에서 로컬 함수 제거
  - [ ] `app/blueprints/main.py` - 로컬 함수 제거, import 추가
  - [ ] `app/blueprints/employees.py` - 로컬 함수 제거, import 추가

### 검증 체크리스트

- [ ] 서버 기동 확인
- [ ] 대시보드 접근 테스트 (멀티테넌시 필터링 확인)
- [ ] 직원 목록 조회 테스트
- [ ] 조직 관리 테스트

### Git 커밋

```bash
git add app/utils/tenant.py app/blueprints/main.py app/blueprints/employees.py
git commit -m "refactor: 멀티테넌시 헬퍼 통합 (tenant.py)

- get_current_organization_id() 공용 모듈로 이동
- main.py, employees.py에서 중복 함수 제거"
```

---

## Phase 3: employees.py 분할

### 작업 목록

- [ ] 3.1 디렉토리 구조 생성
  ```
  app/blueprints/employees/
  ├── __init__.py          # Blueprint 등록, 공통 import
  ├── routes.py            # 기본 CRUD 라우트
  ├── files.py             # 파일 업로드/다운로드
  └── helpers.py           # 헬퍼 함수
  ```

- [ ] 3.2 `employees/__init__.py` 생성
  - [ ] Blueprint 정의 및 등록
  - [ ] 하위 모듈 import

- [ ] 3.3 `employees/helpers.py` 생성
  - [ ] `verify_employee_access()` 이동
  - [ ] `extract_employee_from_form()` 이동
  - [ ] `allowed_file()` 이동
  - [ ] `_update_family_data()` 등 헬퍼 함수 이동

- [ ] 3.4 `employees/routes.py` 생성
  - [ ] `employee_list()` 이동
  - [ ] `employee_detail()` 이동
  - [ ] `employee_new()` 이동
  - [ ] `employee_edit()` 이동
  - [ ] `employee_delete()` 이동

- [ ] 3.5 `employees/files.py` 생성
  - [ ] `upload_attachment()` 이동
  - [ ] `get_attachments()` 이동
  - [ ] `delete_attachment()` 이동
  - [ ] `upload_profile_photo()` 이동
  - [ ] `get_profile_photo()` 이동
  - [ ] `delete_profile_photo()` 이동
  - [ ] `upload_business_card()` 이동
  - [ ] `delete_business_card()` 이동

- [ ] 3.6 `app/__init__.py` 수정
  - [ ] Blueprint 등록 경로 변경

- [ ] 3.7 기존 `app/blueprints/employees.py` 삭제

### 검증 체크리스트

- [ ] 서버 기동 확인
- [ ] 직원 목록 조회 테스트
- [ ] 직원 상세 조회 테스트
- [ ] 직원 생성 테스트
- [ ] 직원 수정 테스트
- [ ] 직원 삭제 테스트
- [ ] 파일 업로드 테스트 (첨부파일, 프로필 사진, 명함)
- [ ] 파일 다운로드 테스트
- [ ] 파일 삭제 테스트

### Git 커밋

```bash
git add app/blueprints/employees/ app/__init__.py
git rm app/blueprints/employees.py
git commit -m "refactor: employees.py 모듈 분할 (1,268줄 -> 3개 파일)

- employees/routes.py: CRUD 라우트 (~400줄)
- employees/files.py: 파일 업로드/다운로드 (~350줄)
- employees/helpers.py: 헬퍼 함수 (~300줄)
- 단일 책임 원칙(SRP) 적용"
```

---

## Phase 4: 복잡한 함수 리팩토링

### 작업 목록

- [ ] 4.1 `employee_detail()` 분할 (140줄 -> 50줄 이하)
  - [ ] `_verify_employee_access()` 헬퍼 추출
  - [ ] `_load_employee_basic_data()` 헬퍼 추출
  - [ ] `_load_employee_history_data()` 헬퍼 추출
  - [ ] `_load_employee_full_data()` 헬퍼 추출

- [ ] 4.2 `extract_employee_from_form()` 개선 (100줄 -> 60줄 이하)
  - [ ] `EMPLOYEE_FIELD_MAPPING` 상수 정의
  - [ ] 필드 매핑 테이블 기반 로직으로 변경

### 검증 체크리스트

- [ ] 직원 상세 조회 테스트 (모든 권한 레벨)
- [ ] 직원 생성/수정 테스트 (모든 필드)
- [ ] 폼 데이터 추출 정확성 확인

### Git 커밋

```bash
git add app/blueprints/employees/
git commit -m "refactor: 복잡한 함수 분할

- employee_detail() 140줄 -> 50줄 이하
- extract_employee_from_form() 매핑 테이블 기반으로 개선"
```

---

## Phase 5: personal_profile.py 분할

### 작업 목록

- [ ] 5.1 디렉토리 구조 생성
  ```
  app/models/personal/
  ├── __init__.py              # 모든 모델 re-export
  ├── profile.py               # PersonalProfile
  ├── education.py             # PersonalEducation
  ├── career.py                # PersonalCareer
  ├── certificate.py           # PersonalCertificate
  ├── language.py              # PersonalLanguage
  └── military_service.py      # PersonalMilitaryService
  ```

- [ ] 5.2 `personal/__init__.py` 생성
  - [ ] 모든 모델 클래스 re-export (기존 import 호환성 유지)

- [ ] 5.3 각 모델 파일 생성
  - [ ] `profile.py` - PersonalProfile 클래스
  - [ ] `education.py` - PersonalEducation 클래스
  - [ ] `career.py` - PersonalCareer 클래스
  - [ ] `certificate.py` - PersonalCertificate 클래스
  - [ ] `language.py` - PersonalLanguage 클래스
  - [ ] `military_service.py` - PersonalMilitaryService 클래스

- [ ] 5.4 기존 `app/models/personal_profile.py` 삭제

- [ ] 5.5 Import 경로 업데이트 (필요시)
  - [ ] `app/blueprints/personal.py` 확인
  - [ ] 기타 import 하는 파일 확인

### 검증 체크리스트

- [ ] 서버 기동 확인
- [ ] 개인 프로필 조회 테스트
- [ ] 개인 프로필 수정 테스트
- [ ] 학력/경력/자격증/어학/병역 CRUD 테스트

### Git 커밋

```bash
git add app/models/personal/
git rm app/models/personal_profile.py
git commit -m "refactor: personal_profile.py 모델 분할 (6개 클래스 -> 6개 파일)

- 각 모델을 독립 파일로 분리
- __init__.py에서 re-export로 기존 import 호환성 유지
- 단일 책임 원칙(SRP) 적용"
```

---

## 최종 검증

### 회귀 테스트 체크리스트

- [ ] 로그인/로그아웃 (개인/법인/관리자)
- [ ] 대시보드 접근 (멀티테넌시 필터링)
- [ ] 직원 CRUD 전체 플로우
- [ ] 파일 업로드/다운로드
- [ ] 개인 프로필 관리
- [ ] 조직 관리
- [ ] 계약 관리

### 최종 커밋

```bash
git push origin feature/phase5-notification
```

---

## 수정 파일 요약

### 신규 생성

| 파일 | 설명 |
|------|------|
| `app/utils/tenant.py` | 멀티테넌시 헬퍼 함수 |
| `app/blueprints/employees/__init__.py` | Blueprint 등록 |
| `app/blueprints/employees/routes.py` | CRUD 라우트 |
| `app/blueprints/employees/files.py` | 파일 관리 |
| `app/blueprints/employees/helpers.py` | 헬퍼 함수 |
| `app/models/personal/__init__.py` | 모델 re-export |
| `app/models/personal/profile.py` | PersonalProfile |
| `app/models/personal/education.py` | PersonalEducation |
| `app/models/personal/career.py` | PersonalCareer |
| `app/models/personal/certificate.py` | PersonalCertificate |
| `app/models/personal/language.py` | PersonalLanguage |
| `app/models/personal/military_service.py` | PersonalMilitaryService |

### 수정

| 파일 | 변경 내용 |
|------|----------|
| `app/utils/decorators.py` | 5개 데코레이터 추가 |
| `app/blueprints/main.py` | 로컬 함수 제거, import 변경 |
| `app/blueprints/personal.py` | 인라인 데코레이터 제거 |
| `app/blueprints/corporate.py` | 인라인 데코레이터 제거 |
| `app/blueprints/contracts.py` | 인라인 데코레이터 제거 |
| `app/blueprints/sync.py` | 인라인 데코레이터 제거 |
| `app/blueprints/admin/audit.py` | 인라인 데코레이터 제거 |
| `app/__init__.py` | Blueprint 등록 경로 변경 |

### 삭제

| 파일 | 사유 |
|------|------|
| `app/blueprints/employees.py` | 모듈로 분할됨 |
| `app/models/personal_profile.py` | 모듈로 분할됨 |

---

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| Import 경로 변경으로 인한 오류 | 높음 | Phase별 점진적 적용, 즉시 테스트 |
| Blueprint 등록 오류 | 높음 | `__init__.py` 패턴 검증 |
| 세션 데이터 접근 오류 | 중간 | 기존 패턴 유지, 래퍼 함수 사용 |

---

## 작성 정보

- **작성일**: 2025-12-04
- **작성자**: Claude Code (Refactoring Agent)
- **프로젝트**: HR Management System
- **브랜치**: feature/phase5-notification
