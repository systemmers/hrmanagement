# HR Management 플랫폼 아키텍처 전환 계획

> **문서명**: conversion
> **생성일**: 2025-12-01
> **최종 수정**: 2025-12-01
> **분석 대상**: dev_note.md #10 - 개인/법인 계정 분리 플랫폼 구조
> **현재 상태**: 법인 내부 직원 관리 시스템 (SQLite, 단일 테넌시)
> **목표 상태**: 개인-법인 독립 계정 플랫폼 (PostgreSQL, 멀티 테넌시)

---

## 목차

1. [현재 아키텍처 분석](#1-현재-아키텍처-분석)
2. [목표 아키텍처](#2-목표-아키텍처)
3. [GAP 분석 및 필요 변경사항](#3-gap-분석-및-필요-변경사항)
4. [구현 복잡도 평가](#4-구현-복잡도-평가)
5. [권장 접근 방식](#5-권장-접근-방식)
6. [결정 사항](#6-결정-사항)
7. [핵심 파일 목록](#7-핵심-파일-목록)
8. [상세 워크플로우](#8-상세-워크플로우)
9. [투두리스트](#9-투두리스트)
10. [체크리스트](#10-체크리스트)
11. [진행 추적](#11-진행-추적)
12. [Phase 0: DB 시스템 변경](#12-phase-0-db-시스템-변경)

---

## 1. 현재 아키텍처 분석

### 1.1 핵심 모델 구조

```
User (인증)
├── role: admin | manager | employee
├── employee_id (FK) → Employee (1:1 선택적)
└── 단일 테넌시

Employee (직원 정보 - 27개 필드)
├── 기본정보 + 개인정보 + 소속정보 혼재
├── organization_id (FK) → Organization (단일)
└── 1:N 관계 23개 (학력, 경력, 자격증 등)

Organization (조직 트리)
├── org_type: company | division | department | team | unit
├── parent_id (Self-referential)
└── 트리 구조
```

### 1.2 현재 구조의 한계

| 항목 | 현재 상태 | 문제점 |
|------|----------|--------|
| 계정 유형 | role만 구분 | 개인/법인 계정 구분 없음 |
| 소속 관계 | Employee.organization_id 단일 | 다중 회사 소속 불가 |
| 개인정보 | Employee에 혼재 | 법인과 개인정보 분리 안됨 |
| 계약 관계 | Contract 7개 필드만 | 개인-법인 계약 모델링 없음 |
| 데이터 공유 | 없음 | 동기화/권한 메커니즘 부재 |
| 법인 정보 | Organization만 | 사업자등록번호 등 법인 고유정보 없음 |

---

## 2. 목표 아키텍처

### 2.1 서비스 구조 요구사항

```
플랫폼
├── 개인 계정 (일반 회원)
│   ├── 회원가입 → 독립 계정
│   ├── 기본정보, 이력정보, 첨부서류 관리
│   ├── 여러 회사에 소속 가능
│   └── 정보 동기화 설정 (실시간 vs 1회성)
│
├── 법인 계정 (기업)
│   ├── 법인 회원가입
│   ├── 법인정보, 세팅 관리
│   ├── 직원 계정 생성 가능 (하위 계정)
│   └── 계약된 개인 정보 접근
│
└── 계약 관계
    ├── 개인 ↔ 법인 계약 요청/승인
    ├── 계약 시 정보 공유 허용
    ├── 퇴사 시 연결 종료 (3년 보관)
    └── 경력증명서 등 문서 요청
```

### 2.2 핵심 기능 요구사항

1. **개인 계정 독립성**
   - 독립적인 기본정보/이력 관리
   - 여러 회사와 계약 가능
   - 정보 변경 시 법인에 동기화

2. **법인 계정 기능**
   - 법인 고유정보 관리
   - 직원 계정 생성/관리 (하위 계정)
   - 계약된 개인 정보 자동 수집

3. **계약 기반 연결**
   - 계약 요청 → 승인 → 정보 공유
   - 퇴사 시 연결 해제
   - 법정 보관 기간 (3년) 정책

4. **데이터 동기화**
   - 실시간 동기화 vs 1회성 제공 선택
   - 공유 범위 설정 가능

---

## 3. GAP 분석 및 필요 변경사항

### 3.1 신규 모델 필요

```python
# 1. Company (법인 전용)
Company:
  - business_number (사업자번호)
  - name, representative, industry
  - address, phone, email, website
  - organization_id (FK) - 트리 루트

# 2. User 확장
User (수정):
  + account_type: personal | corporate | employee_sub
  + company_id (FK) - 법인 계정일 때
  + parent_user_id (FK) - 하위 직원 계정일 때

# 3. PersonalProfile (개인정보 분리)
PersonalProfile:
  - user_id (FK) - personal 계정
  - 개인 고유정보 (학력, 경력, 자격증 등)
  - 회사 소속정보 제외

# 4. PersonCorporateContract (계약 관계)
PersonCorporateContract:
  - person_user_id, company_id
  - status: requested | approved | terminated
  - contract_documents[]
  - data_sharing_settings

# 5. DataSharingSettings (동기화 설정)
DataSharingSettings:
  - contract_id
  - is_realtime_sync
  - shared_fields (JSON)

# 6. SyncLog (동기화 이력)
SyncLog:
  - entity_type, field_name
  - old_value, new_value
  - sync_type: auto | manual
```

### 3.2 기존 모델 변경

| 모델 | 변경 사항 |
|------|----------|
| User | account_type, company_id, parent_user_id 추가 |
| Employee | 개인정보 → PersonalProfile로 분리 |
| Organization | company_id 추가 (법인 연결) |
| Contract | PersonCorporateContract와 연동 |

### 3.3 마이그레이션 전략

```
Phase 1: 신규 모델 추가 (기존 유지)
├── Company, PersonalProfile 생성
├── PersonCorporateContract, DataSharingSettings 생성
└── User 필드 추가 (nullable)

Phase 2: 데이터 분리
├── Employee 개인정보 → PersonalProfile
├── Organization company 레벨 → Company
└── 기존 User 분류 (personal/corporate)

Phase 3: 라우트/뷰 분리
├── /personal/* - 개인 계정 전용
├── /corporate/* - 법인 계정 전용
└── /contract/* - 계약 관리

Phase 4: 동기화 로직 구현
├── 정보 변경 이벤트 처리
├── 실시간 vs 1회성 분기
└── 퇴사 처리 자동화
```

---

## 4. 구현 복잡도 평가

### 4.1 작업 규모

| 영역 | 복잡도 | 예상 작업량 |
|------|--------|------------|
| 데이터 모델 | 높음 | 6개 신규 + 4개 수정 |
| 마이그레이션 | 높음 | 기존 데이터 분리/변환 |
| 인증/권한 | 중간 | 계정 유형별 분기 |
| 라우트/뷰 | 높음 | 완전 분리 필요 |
| 동기화 | 높음 | 이벤트 기반 설계 |
| 프론트엔드 | 중간 | 계정별 UI 분리 |

### 4.2 위험 요소

1. **데이터 무결성**: 기존 Employee 데이터 분리 시 손실 위험
2. **호환성**: 기존 기능 유지하면서 새 구조 적용
3. **복잡도**: 동기화 로직의 엣지 케이스 처리
4. **테스트**: 광범위한 테스트 필요

---

## 5. 권장 접근 방식

### 5.1 점진적 전환 (권장)

```
현재 시스템 유지 + 새 구조 병행 운영

Step 0: SQLite → PostgreSQL 마이그레이션 (선행 필수)
Step 1: Company, PersonalProfile 모델 추가
Step 2: 신규 가입자에게만 새 구조 적용
Step 3: 기존 사용자 점진적 마이그레이션
Step 4: 레거시 구조 단계적 제거
```

### 5.2 DB 시스템 변경 선행 근거

멀티 테넌시 구현 전 PostgreSQL 전환이 필수인 이유:

| 항목 | SQLite | PostgreSQL |
|------|--------|------------|
| 스키마 분리 | 불가 | 가능 (schema-level) |
| 동시 쓰기 | 제한적 | 완전 지원 |
| Row-Level Security | 없음 | 네이티브 지원 |
| 확장성 | 단일 파일 | 분산 가능 |
| 트랜잭션 격리 | 기본 | 고급 격리 수준 |

**권장 순서**: DB 변경 → 멀티 테넌시 (이중 작업 방지)

### 5.3 대안: 완전 재설계

```
새 프로젝트로 시작 → 데이터 마이그레이션

장점: 깔끔한 구조
단점: 시간/비용 높음, 서비스 중단 필요
```

---

## 6. 결정 사항

사용자 선택 결과:

| 항목 | 선택 | 설명 |
|------|------|------|
| 구현 범위 | **분석만** | 현재는 분석 보고서만, 구현은 나중에 |
| 전환 전략 | **점진적 전환** | 현재 시스템 유지하며 새 구조 병행 |
| 우선순위 | **법인 모델** | Company 모델과 법인 계정 시스템 우선 |

### 향후 구현 로드맵

```
Phase 0: DB 시스템 변경 (선행 필수)
├── PostgreSQL 환경 구성
├── SQLAlchemy DATABASE_URL 변경
├── 기존 데이터 마이그레이션
├── Alembic 설정
└── 검증 테스트

Phase 1: Company 모델
├── Company 모델 생성 (사업자번호, 법인정보)
├── Organization과 Company 연결
├── User.account_type 필드 추가
└── 법인 계정 회원가입/인증

Phase 2: 개인 프로필 분리
├── PersonalProfile 모델 생성
├── Employee 개인정보 분리
└── 개인 계정 회원가입/인증

Phase 3: 계약 관계
├── PersonCorporateContract 모델
├── 계약 요청/승인 워크플로우
└── 정보 공유 권한 설정

Phase 4: 동기화
├── DataSharingSettings 모델
├── 실시간/1회성 동기화 로직
└── 퇴사 처리 자동화
```

---

## 7. 핵심 파일 목록

### 수정 필요 파일
- `app/models/user.py` - 계정 유형 확장
- `app/models/employee.py` - 개인정보 분리
- `app/models/organization.py` - 법인 연결
- `app/blueprints/auth.py` - 계정 유형별 인증
- `app/utils/decorators.py` - 권한 체계 확장

### 신규 생성 파일
- `app/models/company.py` - 법인 모델
- `app/models/personal_profile.py` - 개인 프로필
- `app/models/contract_relation.py` - 계약 관계
- `app/models/data_sharing.py` - 동기화 설정
- `app/blueprints/personal.py` - 개인 계정 라우트
- `app/blueprints/corporate.py` - 법인 계정 라우트

---

## 8. 상세 워크플로우

### Phase 0: DB 시스템 변경 (SQLite → PostgreSQL)

```
Phase 0 워크플로우 (선행 필수)
├── 0.1 PostgreSQL 환경 구성
│   ├── PostgreSQL 설치 (로컬 또는 Docker)
│   ├── 데이터베이스 생성 (hrmanagement_db)
│   ├── 사용자 권한 설정
│   └── 접속 테스트
│
├── 0.2 프로젝트 설정 변경
│   ├── psycopg2-binary 패키지 설치
│   ├── config.py DATABASE_URL 변경
│   ├── .env 파일 PostgreSQL 설정 추가
│   └── SQLAlchemy dialect 확인
│
├── 0.3 Alembic 마이그레이션 설정
│   ├── alembic init migrations
│   ├── alembic.ini 설정
│   ├── env.py 모델 연결
│   └── 초기 마이그레이션 생성
│
├── 0.4 데이터 마이그레이션
│   ├── SQLite 데이터 덤프 스크립트 작성
│   ├── PostgreSQL 스키마 생성
│   ├── 데이터 import 스크립트 작성
│   ├── FK 제약조건 순서 처리
│   └── 시퀀스 동기화
│
├── 0.5 검증 및 테스트
│   ├── 데이터 무결성 검증
│   ├── 기존 기능 회귀 테스트
│   ├── CRUD 동작 확인
│   └── 성능 비교 테스트
│
└── 0.6 배포 준비
    ├── 프로덕션 PostgreSQL 환경 구성
    ├── 백업/복구 절차 수립
    └── 롤백 계획 문서화
```

### Phase 1: Company 모델 구현

```
Phase 1 워크플로우
├── 1.1 데이터베이스 설계
│   ├── Company 모델 스키마 정의
│   ├── User 모델 확장 필드 정의
│   └── 마이그레이션 스크립트 준비
│
├── 1.2 모델 구현
│   ├── app/models/company.py 생성
│   ├── app/models/user.py 수정 (account_type, company_id)
│   └── app/models/__init__.py 업데이트
│
├── 1.3 Repository 구현
│   ├── app/repositories/company_repo.py 생성
│   └── CRUD 메서드 구현
│
├── 1.4 Blueprint 구현
│   ├── app/blueprints/corporate.py 생성
│   ├── 법인 회원가입 라우트
│   ├── 법인 정보 관리 라우트
│   └── app/__init__.py에 Blueprint 등록
│
├── 1.5 템플릿 구현
│   ├── templates/corporate/register.html
│   ├── templates/corporate/dashboard.html
│   └── templates/corporate/settings.html
│
└── 1.6 테스트 및 검증
    ├── 법인 계정 회원가입 테스트
    ├── 법인 정보 CRUD 테스트
    └── 기존 기능 회귀 테스트
```

### Phase 2: 개인 프로필 분리

```
Phase 2 워크플로우
├── 2.1 PersonalProfile 모델
│   ├── app/models/personal_profile.py 생성
│   ├── Employee에서 개인정보 필드 분리 정의
│   └── 마이그레이션 스크립트
│
├── 2.2 개인 계정 시스템
│   ├── app/blueprints/personal.py 생성
│   ├── 개인 회원가입 라우트
│   └── 개인 정보 관리 라우트
│
├── 2.3 데이터 마이그레이션
│   ├── 기존 Employee → PersonalProfile 데이터 복사
│   ├── User.account_type 설정
│   └── 데이터 무결성 검증
│
└── 2.4 UI 분리
    ├── 개인 계정 전용 템플릿
    ├── 사이드바/네비게이션 분기
    └── 권한별 뷰 제어
```

### Phase 3: 계약 관계 구현

```
Phase 3 워크플로우
├── 3.1 계약 모델
│   ├── app/models/contract_relation.py 생성
│   ├── PersonCorporateContract 모델
│   └── 계약 상태 enum 정의
│
├── 3.2 계약 워크플로우
│   ├── 계약 요청 기능
│   ├── 계약 승인/거절 기능
│   ├── 계약 종료 기능
│   └── 계약 이력 관리
│
├── 3.3 권한 연동
│   ├── 계약 기반 정보 접근 권한
│   ├── decorators.py 확장
│   └── 뷰 레벨 권한 제어
│
└── 3.4 알림 시스템
    ├── 계약 요청 알림
    ├── 승인/거절 알림
    └── 만료 예정 알림
```

### Phase 4: 동기화 시스템

```
Phase 4 워크플로우
├── 4.1 동기화 모델
│   ├── app/models/data_sharing.py 생성
│   ├── DataSharingSettings 모델
│   └── SyncLog 모델
│
├── 4.2 동기화 로직
│   ├── 실시간 동기화 이벤트 핸들러
│   ├── 1회성 제공 로직
│   └── 동기화 스케줄러
│
├── 4.3 퇴사 처리
│   ├── 계약 종료 시 권한 해제
│   ├── 데이터 보관 정책 (3년)
│   └── 자동 아카이브 기능
│
└── 4.4 감사 로그
    ├── 정보 접근 로그
    ├── 동기화 이력 로그
    └── 보고서 생성 기능
```

---

## 9. 투두리스트

### Phase 0: DB 시스템 변경 (SQLite → PostgreSQL)

- [ ] 0.1.1 PostgreSQL 설치 (로컬 또는 Docker 선택)
- [ ] 0.1.2 hrmanagement_db 데이터베이스 생성
- [ ] 0.1.3 사용자 생성 및 권한 설정
- [ ] 0.1.4 접속 테스트 (psql 또는 클라이언트)
- [ ] 0.2.1 psycopg2-binary 패키지 설치 (requirements.txt)
- [ ] 0.2.2 config.py SQLALCHEMY_DATABASE_URI 변경
- [ ] 0.2.3 .env 파일에 DATABASE_URL 추가
- [ ] 0.2.4 SQLAlchemy PostgreSQL dialect 동작 확인
- [ ] 0.3.1 Alembic 초기화 (alembic init migrations)
- [ ] 0.3.2 alembic.ini 설정 (sqlalchemy.url)
- [ ] 0.3.3 env.py에 모델 메타데이터 연결
- [ ] 0.3.4 초기 마이그레이션 생성 (alembic revision --autogenerate)
- [ ] 0.4.1 SQLite 데이터 덤프 스크립트 작성
- [ ] 0.4.2 PostgreSQL 스키마 생성 (alembic upgrade head)
- [ ] 0.4.3 데이터 import 스크립트 작성
- [ ] 0.4.4 FK 제약조건 순서 처리 (참조 무결성)
- [ ] 0.4.5 시퀀스 동기화 (auto increment 값 맞춤)
- [ ] 0.5.1 데이터 무결성 검증 (레코드 수, 관계 확인)
- [ ] 0.5.2 기존 기능 회귀 테스트
- [ ] 0.5.3 CRUD 동작 확인 (모든 주요 기능)
- [ ] 0.5.4 성능 비교 테스트
- [ ] 0.6.1 프로덕션 PostgreSQL 환경 구성 문서화
- [ ] 0.6.2 백업/복구 절차 수립
- [ ] 0.6.3 롤백 계획 문서화

### Phase 1: Company 모델

- [ ] 1.1.1 Company 테이블 스키마 설계
- [ ] 1.1.2 User 테이블 확장 필드 설계
- [ ] 1.1.3 ERD 다이어그램 업데이트
- [ ] 1.2.1 app/models/company.py 생성
- [ ] 1.2.2 User 모델에 account_type 필드 추가
- [ ] 1.2.3 User 모델에 company_id FK 추가
- [ ] 1.2.4 models/__init__.py 업데이트
- [ ] 1.3.1 CompanyRepository 클래스 생성
- [ ] 1.3.2 create, get, update, delete 메서드
- [ ] 1.4.1 corporate_bp Blueprint 생성
- [ ] 1.4.2 /corporate/register 라우트
- [ ] 1.4.3 /corporate/dashboard 라우트
- [ ] 1.4.4 /corporate/settings 라우트
- [ ] 1.4.5 app/__init__.py Blueprint 등록
- [ ] 1.5.1 corporate/register.html 템플릿
- [ ] 1.5.2 corporate/dashboard.html 템플릿
- [ ] 1.5.3 corporate/settings.html 템플릿
- [ ] 1.6.1 법인 회원가입 테스트
- [ ] 1.6.2 법인 정보 CRUD 테스트
- [ ] 1.6.3 기존 기능 회귀 테스트

### Phase 2: 개인 프로필

- [ ] 2.1.1 PersonalProfile 모델 설계
- [ ] 2.1.2 Employee 필드 분리 매핑
- [ ] 2.1.3 마이그레이션 스크립트 작성
- [ ] 2.2.1 personal_bp Blueprint 생성
- [ ] 2.2.2 개인 회원가입 라우트
- [ ] 2.2.3 개인 정보 관리 라우트
- [ ] 2.3.1 데이터 마이그레이션 실행
- [ ] 2.3.2 데이터 무결성 검증
- [ ] 2.4.1 개인 계정 템플릿 생성
- [ ] 2.4.2 네비게이션 분기 구현

### Phase 3: 계약 관계

- [ ] 3.1.1 PersonCorporateContract 모델
- [ ] 3.1.2 계약 상태 enum 정의
- [ ] 3.2.1 계약 요청 기능
- [ ] 3.2.2 계약 승인/거절 기능
- [ ] 3.2.3 계약 종료 기능
- [ ] 3.3.1 계약 기반 권한 데코레이터
- [ ] 3.3.2 뷰 레벨 권한 제어
- [ ] 3.4.1 계약 알림 시스템

### Phase 4: 동기화

- [ ] 4.1.1 DataSharingSettings 모델
- [ ] 4.1.2 SyncLog 모델
- [ ] 4.2.1 실시간 동기화 구현
- [ ] 4.2.2 1회성 제공 구현
- [ ] 4.3.1 퇴사 처리 로직
- [ ] 4.3.2 데이터 아카이브 기능
- [ ] 4.4.1 감사 로그 시스템

---

## 10. 체크리스트

### 구현 전 체크리스트

- [ ] 기존 데이터베이스 백업 완료
- [ ] 개발 브랜치 생성 (feature/platform-architecture)
- [ ] 테스트 환경 준비
- [ ] 마이그레이션 롤백 계획 수립

### Phase 0 완료 체크리스트 (DB 전환)

- [ ] PostgreSQL 서버 정상 동작
- [ ] 데이터베이스 연결 설정 완료
- [ ] Alembic 마이그레이션 시스템 동작
- [ ] SQLite 전체 데이터 PostgreSQL 이전 완료
- [ ] 데이터 무결성 검증 (레코드 수 일치)
- [ ] FK 관계 무결성 확인
- [ ] 시퀀스 값 동기화 완료
- [ ] 기존 로그인/인증 정상 동작
- [ ] 직원 CRUD 정상 동작
- [ ] 조직 트리 정상 동작
- [ ] 검색 기능 정상 동작
- [ ] 개발 환경 .env 파일 설정 완료
- [ ] 프로덕션 환경 설정 문서화
- [ ] 롤백 절차 테스트 완료

### Phase 1 완료 체크리스트

- [ ] Company 모델 정상 동작
- [ ] User.account_type 정상 동작
- [ ] 법인 회원가입 정상 동작
- [ ] 기존 admin/manager/employee 기능 유지
- [ ] 단위 테스트 통과
- [ ] 브라우저 테스트 통과

### Phase 2 완료 체크리스트

- [ ] PersonalProfile 모델 정상 동작
- [ ] 개인 회원가입 정상 동작
- [ ] 데이터 마이그레이션 완료
- [ ] 데이터 무결성 검증 완료
- [ ] 기존 기능 회귀 테스트 통과

### Phase 3 완료 체크리스트

- [ ] 계약 요청/승인 워크플로우 정상
- [ ] 계약 기반 권한 제어 정상
- [ ] 알림 시스템 정상 동작
- [ ] 엣지 케이스 처리 완료

### Phase 4 완료 체크리스트

- [ ] 실시간 동기화 정상 동작
- [ ] 퇴사 처리 자동화 정상
- [ ] 감사 로그 정상 기록
- [ ] 성능 테스트 통과

### 배포 전 체크리스트

- [ ] 전체 통합 테스트 통과
- [ ] 보안 취약점 점검 완료
- [ ] 성능 테스트 완료
- [ ] 문서화 완료
- [ ] 롤백 계획 검증

---

## 11. 진행 추적

### 현재 상태

| Phase | 상태 | 진행률 | 다음 단계 |
|-------|------|--------|----------|
| Phase 0 | **완료** | 100% | - |
| Phase 1 | 대기 | 0% | Company 모델 구현 시작 |
| Phase 2 | 대기 | 0% | Phase 1 완료 후 |
| Phase 3 | 대기 | 0% | Phase 2 완료 후 |
| Phase 4 | 대기 | 0% | Phase 3 완료 후 |

### 의존성 맵

```
Phase 0 (DB 전환: SQLite → PostgreSQL) [선행 필수]
    │
    └──→ Phase 1 (Company 모델)
             │
             ├──→ Phase 2 (개인 프로필) ──→ Phase 3 (계약 관계) ──→ Phase 4 (동기화)
             │
             └──→ 랜딩페이지 (병렬 가능)
```

### Phase 0 세부 의존성

```
0.1 PostgreSQL 환경 구성 (선행)
    │
    └──→ 0.2 프로젝트 설정 변경
             │
             ├──→ 0.3 Alembic 설정
             │         │
             │         └──→ 0.4 데이터 마이그레이션
             │                   │
             │                   └──→ 0.5 검증 테스트
             │                             │
             │                             └──→ 0.6 배포 준비
             │
             └──→ 개발 환경 테스트 (병렬 가능)
```

### 위험 추적

| 위험 | 영향도 | 발생 가능성 | 완화 전략 |
|------|--------|------------|----------|
| DB 마이그레이션 실패 | 높음 | 중간 | SQLite 백업 유지, 롤백 스크립트 준비 |
| PostgreSQL 성능 차이 | 중간 | 낮음 | 인덱스 최적화, 쿼리 분석 |
| 데이터 손실 | 높음 | 중간 | 마이그레이션 전 백업, 단계별 검증 |
| 기존 기능 장애 | 높음 | 중간 | 회귀 테스트, 점진적 배포 |
| 동기화 성능 | 중간 | 높음 | 비동기 처리, 배치 최적화 |
| 권한 누락 | 높음 | 낮음 | 체계적 권한 매트릭스 정의 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-12-01 | 1.0 | 초기 분석 및 계획 문서 생성 | Claude |
| 2025-12-01 | 1.1 | Phase 0 (DB 시스템 변경) 추가, 의존성 맵 업데이트 | Claude |
| 2025-12-02 | 1.2 | Phase 0 구현 완료: Docker Compose, Alembic, 마이그레이션 스크립트 | Claude |
| 2025-12-02 | 1.3 | Phase 0 실행 완료: PostgreSQL 마이그레이션 성공, 검증 완료 | Claude |

---

## 12. Phase 0: DB 시스템 변경

### 12.1 개요

멀티 테넌시 아키텍처 구현을 위한 선행 작업으로 SQLite에서 PostgreSQL로 데이터베이스 시스템을 변경합니다.

**변경 근거**:
- SQLite는 스키마 분리 미지원 (멀티 테넌시 핵심 기능)
- SQLite 동시 쓰기 제한 (다중 사용자 환경 부적합)
- PostgreSQL Row-Level Security (테넌트별 데이터 격리)
- PostgreSQL 확장성 (대규모 서비스 대응)

### 12.2 기술 스택 변경

```
변경 전                          변경 후
─────────────────────────────────────────────────────
SQLite                    →     PostgreSQL 15+
sqlite3 (built-in)        →     psycopg2-binary
파일 기반 (instance/)     →     서버 기반 (TCP/IP)
단일 파일 백업            →     pg_dump / pg_restore
수동 스키마 관리          →     Alembic 마이그레이션
```

### 12.3 설정 변경 사항

#### config.py 변경

```python
# 변경 전 (SQLite)
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/hrmanagement.db'

# 변경 후 (PostgreSQL)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://user:password@localhost:5432/hrmanagement_db'
```

#### .env 파일 추가

```env
# PostgreSQL 연결 정보
DATABASE_URL=postgresql://hrm_user:secure_password@localhost:5432/hrmanagement_db

# 개발/테스트/프로덕션 분리
DEV_DATABASE_URL=postgresql://hrm_user:dev_password@localhost:5432/hrmanagement_dev
TEST_DATABASE_URL=postgresql://hrm_user:test_password@localhost:5432/hrmanagement_test
```

#### requirements.txt 추가

```txt
psycopg2-binary==2.9.9
alembic==1.13.1
```

### 12.4 PostgreSQL 환경 구성

#### Docker Compose (권장)

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: hrm_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: hrmanagement_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 로컬 설치 (Windows)

```powershell
# PostgreSQL 설치 후
psql -U postgres
CREATE USER hrm_user WITH PASSWORD 'secure_password';
CREATE DATABASE hrmanagement_db OWNER hrm_user;
GRANT ALL PRIVILEGES ON DATABASE hrmanagement_db TO hrm_user;
```

### 12.5 Alembic 설정

```bash
# 초기화
alembic init migrations

# alembic.ini 수정
sqlalchemy.url = postgresql://hrm_user:secure_password@localhost:5432/hrmanagement_db

# env.py 수정 - 모델 메타데이터 연결
from app.extensions import db
target_metadata = db.metadata

# 초기 마이그레이션 생성
alembic revision --autogenerate -m "Initial schema"

# 마이그레이션 적용
alembic upgrade head
```

### 12.6 데이터 마이그레이션 스크립트

```python
# scripts/migrate_sqlite_to_postgres.py
"""
SQLite → PostgreSQL 데이터 마이그레이션 스크립트

사용법:
  python scripts/migrate_sqlite_to_postgres.py

주의:
  - 실행 전 PostgreSQL 스키마가 생성되어 있어야 함 (alembic upgrade head)
  - FK 제약조건 순서 고려하여 테이블 순서 지정
"""

import sqlite3
import psycopg2
from datetime import datetime

# 테이블 마이그레이션 순서 (FK 의존성 고려)
TABLE_ORDER = [
    'organization',
    'user',
    'employee',
    'education',
    'career',
    'certification',
    'language_skill',
    'military_service',
    # ... 기타 테이블
]

def migrate_table(sqlite_conn, pg_conn, table_name):
    """단일 테이블 마이그레이션"""
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    # 데이터 조회
    sqlite_cur.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cur.fetchall()

    if not rows:
        return 0

    # 컬럼 정보 조회
    columns = [desc[0] for desc in sqlite_cur.description]

    # PostgreSQL INSERT
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)
    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    for row in rows:
        pg_cur.execute(insert_sql, row)

    pg_conn.commit()
    return len(rows)

def sync_sequences(pg_conn):
    """시퀀스 값 동기화 (auto increment)"""
    pg_cur = pg_conn.cursor()

    for table in TABLE_ORDER:
        pg_cur.execute(f"""
            SELECT setval(pg_get_serial_sequence('{table}', 'id'),
                          COALESCE((SELECT MAX(id) FROM {table}), 1))
        """)

    pg_conn.commit()

def main():
    sqlite_conn = sqlite3.connect('instance/hrmanagement.db')
    pg_conn = psycopg2.connect(
        host='localhost',
        database='hrmanagement_db',
        user='hrm_user',
        password='secure_password'
    )

    print("=== SQLite → PostgreSQL 마이그레이션 시작 ===")

    for table in TABLE_ORDER:
        count = migrate_table(sqlite_conn, pg_conn, table)
        print(f"{table}: {count}건 마이그레이션 완료")

    print("시퀀스 동기화 중...")
    sync_sequences(pg_conn)

    print("=== 마이그레이션 완료 ===")

    sqlite_conn.close()
    pg_conn.close()

if __name__ == '__main__':
    main()
```

### 12.7 검증 체크리스트

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| 연결 테스트 | Flask 서버 시작 | 정상 시작, 오류 없음 |
| 레코드 수 | COUNT(*) 비교 | SQLite = PostgreSQL |
| FK 무결성 | JOIN 쿼리 테스트 | 모든 관계 정상 |
| 시퀀스 | INSERT 후 ID 확인 | 기존 MAX(id) + 1 |
| 인증 | 로그인 테스트 | 기존 계정 정상 동작 |
| CRUD | 직원 등록/수정/삭제 | 모든 동작 정상 |
| 검색 | 직원 검색 | 결과 일치 |
| 트리 | 조직 트리 조회 | 계층 구조 정상 |

### 12.8 롤백 계획

```bash
# 롤백 절차

1. Flask 서버 중지

2. config.py DATABASE_URL 원복
   SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/hrmanagement.db'

3. requirements.txt에서 psycopg2-binary 제거 (선택)

4. Flask 서버 재시작

5. SQLite 데이터 확인 (백업본)
```

### 12.9 PostgreSQL 운영 가이드

#### 백업

```bash
# 전체 백업
pg_dump -U hrm_user -h localhost hrmanagement_db > backup_$(date +%Y%m%d).sql

# 복원
psql -U hrm_user -h localhost hrmanagement_db < backup_20251201.sql
```

#### 모니터링

```sql
-- 활성 연결 확인
SELECT * FROM pg_stat_activity WHERE datname = 'hrmanagement_db';

-- 테이블 크기 확인
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- 느린 쿼리 확인 (pg_stat_statements 확장 필요)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```
