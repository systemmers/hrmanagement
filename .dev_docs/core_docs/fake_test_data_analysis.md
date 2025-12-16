# HR Management System - 테스트 데이터 생성 분석 문서

## 개요

본 문서는 HR Management System의 포괄적인 테스트 데이터 생성 스크립트 분석 결과입니다.

### 생성 대상
| 구분 | 수량 | 설명 |
|------|------|------|
| 법인 (Company) | 3개 | 조직 구조 포함 |
| 직원 (Employee) | 20명 | 모든 인사기록 포함 |
| 개인 (Personal) | 20명 | 개인 프로필 및 이력 포함 |

---

## 데이터베이스 스키마 분석

### 전체 테이블 구조 (33개 테이블)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Core Entities (핵심 엔티티)                    │
├─────────────────────────────────────────────────────────────────┤
│  users              사용자 인증 (personal/corporate/employee_sub) │
│  companies          법인 정보                                     │
│  organizations      조직 구조 (self-referential tree)            │
│  employees          직원 기본 정보                                │
│  personal_profiles  개인 계정 프로필                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   1:1 Relationships (직원 연결)                   │
├─────────────────────────────────────────────────────────────────┤
│  salaries           급여 정보                                     │
│  benefits           복리후생                                      │
│  insurances         보험 정보                                     │
│  contracts          계약 정보                                     │
│  military_services  병역 정보                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   1:N Relationships (직원 연결)                   │
├─────────────────────────────────────────────────────────────────┤
│  educations         학력 사항                                     │
│  careers            경력 사항                                     │
│  certificates       자격증                                        │
│  languages          어학 능력                                     │
│  family_members     가족 관계                                     │
│  promotions         발령/승진 이력                                │
│  evaluations        인사 평가                                     │
│  trainings          교육 이수                                     │
│  attendances        근태 기록                                     │
│  hr_projects        인사이력 프로젝트                             │
│  project_participations  프로젝트 참여                            │
│  awards             수상 이력                                     │
│  assets             자산 배정                                     │
│  salary_histories   연봉 변경 이력                                │
│  salary_payments    급여 지급 내역                                │
│  attachments        첨부 파일                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Personal Profile Relations                     │
├─────────────────────────────────────────────────────────────────┤
│  personal_educations     개인 학력                               │
│  personal_careers        개인 경력                               │
│  personal_certificates   개인 자격증                             │
│  personal_languages      개인 어학                               │
│  personal_military_services  개인 병역                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Contract & System Tables                       │
├─────────────────────────────────────────────────────────────────┤
│  person_corporate_contracts  개인-법인 계약                      │
│  data_sharing_settings       데이터 공유 설정                    │
│  sync_logs                   동기화 로그                         │
│  notifications               알림                                │
│  notification_preferences    알림 설정                           │
│  audit_logs                  감사 로그                           │
│  system_settings             시스템 설정                         │
│  classification_options      분류 옵션                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 데이터 생성 순서 (의존성 기반)

### Phase 1: 법인 및 조직 구조

```
Company (법인)
    └── Organization (조직)
            ├── 본부 (root)
            │   ├── 팀 1
            │   ├── 팀 2
            │   └── 팀 3
            └── ...
```

**생성 데이터:**
- 법인 3개 (테스트기업 A, B, C)
- 법인당 1개 루트 조직 + 3~5개 하위 조직

### Phase 2: 사용자 및 직원

```
User (사용자)
    ├── account_type: 'corporate' (법인 관리자)
    └── account_type: 'employee_sub' (법인 직원)
            └── Employee (직원)
                    ├── 1:1 Relations
                    │   ├── Salary
                    │   ├── Benefit
                    │   ├── Insurance
                    │   ├── Contract
                    │   └── MilitaryService
                    │
                    └── 1:N Relations
                        ├── Education (1~3개)
                        ├── Career (0~2개)
                        ├── Certificate (0~3개)
                        ├── Language (1~2개)
                        ├── FamilyMember (0~3개)
                        ├── Promotion (1~3개)
                        ├── Evaluation (1~3개)
                        ├── Training (0~3개)
                        ├── Attendance (5~10개)
                        ├── HrProject (0~2개)
                        ├── Award (0~2개)
                        ├── Asset (0~2개)
                        ├── SalaryHistory (1~3개)
                        └── SalaryPayment (3~6개)
```

### Phase 3: 개인 계정

```
User (사용자)
    └── account_type: 'personal' (개인)
            └── PersonalProfile (개인 프로필)
                    ├── PersonalEducation (1~3개)
                    ├── PersonalCareer (0~3개)
                    ├── PersonalCertificate (0~3개)
                    ├── PersonalLanguage (1~2개)
                    └── PersonalMilitaryService (0~1개)
```

### Phase 4: 개인-법인 계약

```
PersonCorporateContract (개인-법인 계약)
    ├── personal_profile_id → PersonalProfile
    ├── company_id → Company
    └── DataSharingSettings (데이터 공유 설정)
            └── contract_id → PersonCorporateContract
```

---

## 테스트 계정 정보

### 법인 관리자 계정 (Corporate)

| 법인명 | 이메일 | 비밀번호 | Company ID |
|--------|--------|----------|------------|
| 테스트기업 A | corp_a@test.com | corp1234 | 1 |
| 테스트기업 B | corp_b@test.com | corp1234 | 2 |
| 테스트기업 C | corp_c@test.com | corp1234 | 3 |

### 법인 소속 직원 계정 (Employee Sub)

| 소속 법인 | 이메일 패턴 | 비밀번호 | 수량 |
|-----------|-------------|----------|------|
| 테스트기업 A | emp_a1@test.com ~ emp_a7@test.com | emp1234 | 7명 |
| 테스트기업 B | emp_b1@test.com ~ emp_b7@test.com | emp1234 | 7명 |
| 테스트기업 C | emp_c1@test.com ~ emp_c6@test.com | emp1234 | 6명 |

### 개인 계정 (Personal)

| 이메일 패턴 | 비밀번호 | 수량 |
|-------------|----------|------|
| personal1@test.com ~ personal20@test.com | personal1234 | 20명 |

---

## 생성 데이터 상세

### 직원 기본 정보 (employees)

| 필드 | 생성 방식 |
|------|-----------|
| employee_number | EMP-YYYY-NNNN 형식 |
| name | 한국식 성 + 이름 조합 |
| department | 랜덤 부서 (개발팀, 기획팀, 영업팀 등) |
| position | 랜덤 직급 (사원~상무) |
| status | 재직/휴직/퇴직 (가중치 적용) |
| hire_date | 최근 10년 내 랜덤 |
| phone | 010-XXXX-XXXX 형식 |
| email | 영문명@회사도메인 |
| birth_date | 1970~2000년 랜덤 |
| gender | 남/여 랜덤 |
| address | 한국 주요 도시 주소 |
| resident_number | YYMMDD-XXXXXXX 형식 |

### 학력 정보 (educations)

| 필드 | 생성 방식 |
|------|-----------|
| school_type | 고등학교/전문대학/대학교/대학원 |
| school_name | 한국 주요 대학교명 |
| major | 전공 (컴퓨터공학, 경영학 등) |
| degree | 졸업/수료/재학/중퇴 |
| admission_date | 논리적 순서 보장 |
| graduation_date | admission_date + 2~4년 |

### 경력 정보 (careers)

| 필드 | 생성 방식 |
|------|-----------|
| company_name | 한국 기업명 |
| department | 부서명 |
| position | 직급명 |
| job_description | 업무 내용 |
| start_date | 날짜 (이전 직장) |
| end_date | 퇴사일 |
| resignation_reason | 퇴사 사유 |

### 급여 정보 (salaries)

| 필드 | 생성 방식 |
|------|-----------|
| base_salary | 3,000만원 ~ 1억원 |
| annual_salary | base_salary * 12 + 보너스 |
| payment_date | 매월 25일 |
| payment_method | 계좌이체 |
| bank_name | 한국 주요 은행 |
| account_number | 은행별 계좌번호 형식 |

### 인사 평가 (evaluations)

| 필드 | 생성 방식 |
|------|-----------|
| evaluation_period | 연도-상반기/하반기 |
| evaluation_type | 정기평가/수시평가/특별평가 |
| evaluator | 평가자명 |
| score | 1~5 (가중치 적용) |
| grade | S/A/B/C/D |
| comments | 평가 코멘트 |

### 발령/승진 이력 (promotions)

| 필드 | 생성 방식 |
|------|-----------|
| promotion_type | 승진/전보/파견/복직 |
| before_department | 이전 부서 |
| after_department | 이후 부서 |
| before_position | 이전 직급 |
| after_position | 이후 직급 |
| effective_date | 발령일 |

---

## 스크립트 실행 방법

### 기본 실행

```bash
cd D:\projects\hrmanagement
python scripts/generate_fake_test_data.py
```

### 옵션

| 옵션 | 설명 |
|------|------|
| `--dry-run` | 실제 DB 변경 없이 생성될 데이터 미리보기 |
| `--clear` | 기존 테스트 데이터 삭제 후 새로 생성 |
| `--status` | 현재 DB 상태만 확인 |

### 실행 예시

```bash
# 미리보기 (DB 변경 없음)
python scripts/generate_fake_test_data.py --dry-run

# 현재 상태 확인
python scripts/generate_fake_test_data.py --status

# 기존 데이터 삭제 후 새로 생성
python scripts/generate_fake_test_data.py --clear
```

---

## 데이터 관계도

```
                                    ┌─────────────┐
                                    │   Company   │
                                    │  (법인 3개)  │
                                    └──────┬──────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
            ┌───────▼───────┐      ┌───────▼───────┐      ┌───────▼───────┐
            │ Organization  │      │ Organization  │      │ Organization  │
            │  (조직 구조)   │      │  (조직 구조)   │      │  (조직 구조)   │
            └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
                    │                      │                      │
            ┌───────▼───────┐      ┌───────▼───────┐      ┌───────▼───────┐
            │   Employee    │      │   Employee    │      │   Employee    │
            │   (7명)       │      │   (7명)       │      │   (6명)       │
            └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
                    │
    ┌───────────────┼───────────────┬───────────────┬───────────────┐
    │               │               │               │               │
┌───▼───┐     ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
│Salary │     │ Education │   │  Career   │   │Certificate│   │ Language  │
│(1:1)  │     │  (1~3개)  │   │  (0~2개)  │   │  (0~3개)  │   │  (1~2개)  │
└───────┘     └───────────┘   └───────────┘   └───────────┘   └───────────┘
    │
┌───▼───┐     ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│Benefit│     │ Promotion │   │Evaluation │   │ Training  │   │Attendance │
│(1:1)  │     │  (1~3개)  │   │  (1~3개)  │   │  (0~3개)  │   │ (5~10개)  │
└───────┘     └───────────┘   └───────────┘   └───────────┘   └───────────┘


                    ┌─────────────┐
                    │    User     │
                    │(personal)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Personal   │
                    │   Profile   │
                    │  (20명)     │
                    └──────┬──────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
┌───▼────────────┐  ┌──────▼──────┐  ┌────────────▼───┐
│PersonalEducation│  │PersonalCareer│  │PersonalCertificate│
└────────────────┘  └─────────────┘  └──────────────────┘


            ┌───────────────────────────────────┐
            │    PersonCorporateContract        │
            │       (개인-법인 계약)             │
            └─────────────┬─────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼───────┐                   ┌───────▼───────┐
│PersonalProfile│                   │   Company     │
│   (개인)      │                   │   (법인)      │
└───────────────┘                   └───────────────┘
```

---

## 검증 체크리스트

### 데이터 무결성

- [ ] 모든 FK 관계 정상 연결
- [ ] employee_number 고유성 보장
- [ ] 날짜 논리적 순서 (입학 < 졸업, 입사 < 퇴사)
- [ ] 급여 금액 현실적 범위

### 테스트 시나리오

- [ ] 법인 관리자 로그인 테스트
- [ ] 직원 계정 로그인 테스트
- [ ] 개인 계정 로그인 테스트
- [ ] 직원 목록 조회 (페이지네이션)
- [ ] 직원 상세 조회 (모든 탭)
- [ ] 개인-법인 계약 조회

---

## 참고 사항

### 기존 테스트 계정 호환성

기존에 사용 중인 테스트 계정과 충돌하지 않도록 설계:

| 기존 계정 | 새 테스트 데이터 |
|-----------|------------------|
| testuser@example.com | 유지 (충돌 없음) |
| company@example.com | 유지 (충돌 없음) |
| personal1~3@test.com | 확장 (20명으로) |
| corp_a/b@test.com | 확장 (3개 법인) |
| emp_a/b*@test.com | 확장 (20명으로) |

### 스크립트 특징

1. **멱등성**: 기존 데이터 있으면 스킵 처리
2. **트랜잭션**: 전체 성공 또는 전체 롤백
3. **진행 표시**: 단계별 진행 상황 출력
4. **건조 실행**: `--dry-run`으로 미리보기 가능

---

## 문서 정보

- **생성일**: 2025-12-16
- **버전**: 1.0
- **관련 스크립트**: `scripts/generate_fake_test_data.py`
- **관련 스키마**: `.dev_docs/core_docs/db_schema.md`
