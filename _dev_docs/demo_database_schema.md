# 인사카드 관리 시스템 - 데모 데이터베이스 스키마

## 1. 개요

인사카드 관리 시스템의 확장 데이터 모델 스키마 정의서입니다.

### 저장 방식
- **형식**: JSON 파일 기반
- **인코딩**: UTF-8
- **위치**: `data/` 폴더

### 파일 구조
```
data/
├── employees.json              # 기본 직원 정보 (기존)
├── employees_extended.json     # 확장 직원 정보 (신규)
├── classification_options.json # 분류 옵션 (기존)
├── education.json              # 학력 정보 (신규)
├── careers.json                # 경력 정보 (신규)
├── certificates.json           # 자격증 정보 (신규)
├── family_members.json         # 가족 정보 (신규)
├── languages.json              # 언어 능력 (신규)
└── military.json               # 병역 정보 (신규)
```

---

## 2. 기본 테이블 (기존)

### 2.1 employees.json

**설명**: 직원 기본 정보

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 직원 고유 ID | 1 |
| name | string | Y | 이름 (한글) | "김철수" |
| photo | string | Y | 프로필 이미지 경로 | "/static/images/face/face_01_m.png" |
| department | string | Y | 부서 | "개발팀" |
| position | string | Y | 직급 | "과장" |
| status | string | Y | 재직 상태 | "active" |
| hireDate | string | Y | 입사일 (YYYY-MM-DD) | "2020-03-15" |
| phone | string | Y | 휴대폰 | "010-1234-5678" |
| email | string | Y | 이메일 | "chulsoo.kim@company.com" |

**status 값**:
- `active`: 정상 (재직)
- `warning`: 대기 (휴직)
- `expired`: 만료 (퇴직)

---

### 2.2 classification_options.json

**설명**: 드롭다운 선택 옵션

```json
{
  "departments": ["string"],
  "positions": ["string"],
  "statuses": [{"value": "string", "label": "string"}]
}
```

| 필드명 | 타입 | 설명 |
|--------|------|------|
| departments | string[] | 부서 목록 |
| positions | string[] | 직급 목록 |
| statuses | object[] | 상태 목록 (value/label 쌍) |

---

## 3. 확장 테이블 (신규)

### 3.1 employees_extended.json

**설명**: 확장 필드 포함 직원 정보 (기존 employees.json 대체 가능)

**기본 필드** (기존과 동일)
| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| id | integer | Y | 직원 고유 ID |
| name | string | Y | 이름 |
| photo | string | Y | 프로필 이미지 |
| department | string | Y | 부서 |
| position | string | Y | 직급 |
| status | string | Y | 재직 상태 |
| hireDate | string | Y | 입사일 |
| phone | string | Y | 휴대폰 |
| email | string | Y | 이메일 |

**개인정보 확장 필드**
| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| name_en | string | N | 영문 이름 | "Chulsoo Kim" |
| birth_date | string | N | 생년월일 (YYYY-MM-DD) | "1985-05-20" |
| gender | string | N | 성별 (male/female) | "male" |
| address | string | N | 주소 | "서울시 강남구 테헤란로 123" |
| emergency_contact | string | N | 비상연락처 | "010-9999-1234" |
| emergency_relation | string | N | 비상연락처 관계 | "배우자" |

**소속정보 확장 필드**
| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| employee_number | string | N | 사번 | "EMP-2020-001" |
| team | string | N | 팀 | "프론트엔드팀" |
| job_title | string | N | 직책 | "팀장" |
| work_location | string | N | 근무지 | "본사" |
| internal_phone | string | N | 내선번호 | "1234" |
| company_email | string | N | 회사 이메일 | "chulsoo.kim@company.co.kr" |

**계약정보 확장 필드**
| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| employment_type | string | N | 고용형태 | "regular" |
| contract_period | string | N | 계약기간 | "2024.01.01 ~ 2024.12.31" |
| probation_end | string | N | 수습종료일 | "2020-06-15" |
| resignation_date | string | N | 퇴사일 | null |

**employment_type 값**:
- `regular`: 정규직
- `contract`: 계약직
- `parttime`: 파트타임
- `intern`: 인턴

---

### 3.2 education.json

**설명**: 학력 정보 (1:N 관계)

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 학력 레코드 ID | 1 |
| employee_id | integer | Y | 직원 ID (FK) | 1 |
| school | string | Y | 학교명 | "서울대학교" |
| degree | string | Y | 학위 | "bachelor" |
| major | string | N | 전공 | "컴퓨터공학" |
| graduation_year | string | N | 졸업년도 | "2010" |
| graduation_status | string | N | 졸업 상태 | "graduated" |

**degree 값**:
- `highschool`: 고등학교
- `associate`: 전문학사
- `bachelor`: 학사
- `master`: 석사
- `doctor`: 박사

**graduation_status 값**:
- `graduated`: 졸업
- `expected`: 졸업예정
- `dropout`: 중퇴
- `enrolled`: 재학중

---

### 3.3 careers.json

**설명**: 경력 정보 (1:N 관계)

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 경력 레코드 ID | 1 |
| employee_id | integer | Y | 직원 ID (FK) | 1 |
| company | string | Y | 회사명 | "삼성전자" |
| position | string | N | 직급/직책 | "주임" |
| duty | string | N | 담당업무 | "웹 개발" |
| start_date | string | Y | 시작일 (YYYY-MM) | "2010-03" |
| end_date | string | N | 종료일 (YYYY-MM) | "2015-02" |
| is_current | boolean | N | 현재 재직 여부 | false |

---

### 3.4 certificates.json

**설명**: 자격증 및 면허 정보 (1:N 관계)

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 자격증 레코드 ID | 1 |
| employee_id | integer | Y | 직원 ID (FK) | 1 |
| name | string | Y | 자격증명 | "정보처리기사" |
| issuer | string | N | 발급기관 | "한국산업인력공단" |
| acquired_date | string | N | 취득일 (YYYY-MM-DD) | "2009-11-15" |
| expiry_date | string | N | 만료일 | null |
| certificate_number | string | N | 자격번호 | "12345678" |

---

### 3.5 family_members.json

**설명**: 가족 정보 (1:N 관계)

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 가족 레코드 ID | 1 |
| employee_id | integer | Y | 직원 ID (FK) | 1 |
| relation | string | Y | 관계 | "spouse" |
| name | string | Y | 이름 | "이미영" |
| birth_date | string | N | 생년월일 | "1987-03-15" |
| occupation | string | N | 직업 | "교사" |
| is_dependent | boolean | N | 부양가족 여부 | true |

**relation 값**:
- `spouse`: 배우자
- `child`: 자녀
- `parent`: 부모
- `sibling`: 형제/자매

---

### 3.6 languages.json

**설명**: 언어 능력 정보 (1:N 관계)

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 언어 레코드 ID | 1 |
| employee_id | integer | Y | 직원 ID (FK) | 1 |
| language | string | Y | 언어명 | "영어" |
| level | string | N | 수준 | "advanced" |
| test_name | string | N | 시험명 | "TOEIC" |
| score | string | N | 점수 | "950" |
| acquired_date | string | N | 취득일 | "2019-06-15" |

**level 값**:
- `native`: 원어민
- `advanced`: 상급
- `intermediate`: 중급
- `beginner`: 초급

---

### 3.7 military.json

**설명**: 병역 정보 (1:1 관계, 남성만 해당)

| 필드명 | 타입 | 필수 | 설명 | 예시 |
|--------|------|------|------|------|
| id | integer | Y | 병역 레코드 ID | 1 |
| employee_id | integer | Y | 직원 ID (FK) | 1 |
| status | string | Y | 병역사항 | "completed" |
| branch | string | N | 군별 | "army" |
| rank | string | N | 계급 | "병장" |
| start_date | string | N | 입대일 | "2005-03-01" |
| end_date | string | N | 전역일 | "2007-03-01" |
| exemption_reason | string | N | 면제 사유 | null |

**status 값**:
- `completed`: 군필
- `exempted`: 면제
- `serving`: 복무중
- `not_applicable`: 해당없음

**branch 값**:
- `army`: 육군
- `navy`: 해군
- `airforce`: 공군
- `marine`: 해병대
- `auxiliary`: 보충역

---

## 4. 관계도 (ERD)

```
                    ┌──────────────────────┐
                    │   employees_extended │
                    │         (25)         │
                    └──────────┬───────────┘
                               │
          ┌─────────┬─────────┼─────────┬─────────┬─────────┐
          │         │         │         │         │         │
          ▼         ▼         ▼         ▼         ▼         ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │education│ │ careers │ │certific.│ │ family  │ │languages│ │military │
    │  (~30)  │ │  (~40)  │ │  (~35)  │ │  (~50)  │ │  (~30)  │ │  (~15)  │
    └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

---

## 5. 인덱스 및 제약조건

### 5.1 기본키 (PK)
- 모든 테이블: `id` 필드

### 5.2 외래키 (FK)
- 모든 하위 테이블: `employee_id` -> `employees_extended.id`

### 5.3 유니크 제약
- `employees_extended.employee_number`: 사번 중복 불가
- `employees_extended.email`: 이메일 중복 불가

### 5.4 JSON 파일 기반 제약
- 실제 FK 검증은 애플리케이션 레벨에서 수행
- ID 자동 증가는 Repository 클래스에서 처리

---

## 6. 버전 정보

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-11-25 | 초기 스키마 정의 |
