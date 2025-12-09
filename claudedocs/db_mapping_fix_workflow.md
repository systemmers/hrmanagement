# DB 매핑 불일치 수정 워크플로우

**생성일**: 2025-12-04
**모드**: Safe Mode (안전 모드)
**기반 문서**: db_mapping_analysis_report.md

---

## 워크플로우 개요

```
Phase 1: CRITICAL 수정 (런타임 오류 해결)
    |
    v
Phase 2: HIGH 수정 (데이터 손실 방지)
    |
    v
Phase 3: 브라우저 검증
    |
    v
Phase 4: Git 커밋
```

---

## Phase 1: CRITICAL 수정

### 1.1 helpers.py Import 오류 수정

**파일**: `app/blueprints/employees/helpers.py`

**변경 사항**:

| 라인 | 변경 전 | 변경 후 |
|------|--------|--------|
| 187 | `from ...models import Family` | `from ...models import FamilyMember` |
| 322 | `from ...models import Military` | `from ...models import MilitaryService` |

**검증**: 서버 재시작 후 Import 오류 없음 확인

### 1.2 helpers.py 필드명 오류 수정

**파일**: `app/blueprints/employees/helpers.py`

#### update_family_data() 수정 (Line 185-211)

| 변경 전 | 변경 후 | 모델 필드 |
|--------|--------|----------|
| `phone=phones[i]` | `contact=phones[i]` | `contact` |
| `cohabiting=cohabitings[i]` | `is_cohabitant=cohabitings[i]` | `is_cohabitant` |
| `Family(...)` | `FamilyMember(...)` | 클래스명 |

#### update_career_data() 수정 (Line 243-267)

| 변경 전 | 변경 후 | 모델 필드 |
|--------|--------|----------|
| `duties=duties[i]` | `job_description=duties[i]` | `job_description` |

#### update_education_data() 수정 (Line 214-240)

| 변경 전 | 변경 후 | 모델 필드 |
|--------|--------|----------|
| `graduation_year=graduation_years[i]` | `graduation_date=graduation_years[i]` | `graduation_date` |
| `gpa=gpas[i]` | (삭제) | 모델에 없음 |

#### update_military_data() 수정 (Line 320-338)

| 변경 전 | 변경 후 | 모델 필드 |
|--------|--------|----------|
| `Military(...)` | `MilitaryService(...)` | 클래스명 |
| `start_date=...` | `enlistment_date=...` | `enlistment_date` |
| `end_date=...` | `discharge_date=...` | `discharge_date` |
| `specialty=...` | (삭제) | 모델에 없음 |

---

## Phase 2: HIGH 수정 (템플릿 필드명 동기화)

### 2.1 가족정보 템플릿 수정

**파일**: `app/templates/partials/employee_form/_family_info.html`

**입력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `name="family_birth[]"` | `name="family_birth_date[]"` |
| `name="family_job[]"` | `name="family_occupation[]"` |

**출력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `{{ member.birth }}` | `{{ member.birth_date }}` |
| `{{ member.job }}` | `{{ member.occupation }}` |

### 2.2 학력정보 템플릿 수정

**파일**: `app/templates/partials/employee_form/_education_info.html`

**입력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `name="education_school[]"` | `name="education_school_name[]"` |
| `name="education_year[]"` | `name="education_graduation_year[]"` |

**출력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `{{ edu.school }}` | `{{ edu.school_name }}` |
| `{{ edu.year }}` | `{{ edu.graduation_year }}` |

### 2.3 경력정보 템플릿 수정

**파일**: `app/templates/partials/employee_form/_career_info.html`

**입력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `name="career_company[]"` | `name="career_company_name[]"` |
| `name="career_duty[]"` | `name="career_duties[]"` |
| `name="career_period[]"` | `name="career_start_date[]"`, `name="career_end_date[]"` (2개 필드로 분리) |

**출력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `{{ career.company }}` | `{{ career.company_name }}` |
| `{{ career.duty }}` | `{{ career.job_description }}` |
| `{{ career.period }}` | `{{ career.start_date }} ~ {{ career.end_date }}` |

### 2.4 자격증정보 템플릿 수정

**파일**: `app/templates/partials/employee_form/_certificate_info.html`

**입력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `name="cert_name[]"` | `name="certificate_name[]"` |
| `name="cert_issuer[]"` | `name="certificate_issuer[]"` |
| `name="cert_date[]"` | `name="certificate_date[]"` |
| `name="cert_number[]"` | `name="certificate_number[]"` |

### 2.5 언어능력 템플릿 수정

**파일**: `app/templates/partials/employee_form/_language_info.html`

**입력 필드 수정**:
| 변경 전 | 변경 후 |
|--------|--------|
| `name="language_cert[]"` | `name="language_test_name[]"` |
| `name="language_cert_date[]"` | `name="language_test_date[]"` |

---

## Phase 3: 브라우저 검증

### 검증 체크리스트

- [ ] 서버 시작 (오류 없음)
- [ ] 직원 목록 페이지 접근
- [ ] 직원 신규 등록 폼 열기
- [ ] 모든 섹션 입력 후 저장
- [ ] 저장된 직원 상세 페이지 확인
- [ ] 직원 수정 폼 열기
- [ ] 기존 데이터 로드 확인
- [ ] 데이터 수정 후 저장
- [ ] 변경사항 반영 확인

### 테스트 데이터

```
이름: 테스트 직원
가족: 배우자 - 홍길동 - 1990-01-15 - 회사원
학력: 한국대학교 - 학사 - 컴퓨터공학 - 2015
경력: ABC회사 - 대리 - 웹개발 - 2015-03-01 ~ 2020-12-31
자격증: 정보처리기사 - 한국산업인력공단 - 2016-05-20
언어: 영어 - 상급 - TOEIC 900
병역: 군필 - 육군 - 병장 - 2010-01-01 ~ 2011-12-31
```

---

## Phase 4: Git 커밋

### 커밋 메시지

```
fix(db-mapping): 폼-DB 필드 매핑 불일치 수정

CRITICAL 수정:
- helpers.py: Family->FamilyMember, Military->MilitaryService Import 오류 수정
- helpers.py: 모델 필드명 불일치 수정 (contact, is_cohabitant, job_description 등)

HIGH 수정:
- _family_info.html: 입출력 필드명 동기화
- _education_info.html: 입출력 필드명 동기화
- _career_info.html: 입출력 필드명 동기화, 기간 필드 분리
- _certificate_info.html: 입출력 필드명 동기화
- _language_info.html: 입출력 필드명 동기화

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 안전 모드 주의사항

1. **각 Phase 완료 후 검증**: 다음 Phase로 진행 전 현재 Phase 검증 완료
2. **점진적 수정**: 한 번에 하나의 파일만 수정
3. **롤백 준비**: 수정 전 git stash 또는 백업 생성
4. **서버 재시작**: 각 수정 후 서버 재시작하여 오류 확인
5. **브라우저 캐시**: 템플릿 수정 후 브라우저 캐시 클리어

---

## 영향 범위

### 수정 대상 파일 (7개)

| 파일 | Phase | 수정 유형 |
|------|-------|----------|
| `app/blueprints/employees/helpers.py` | 1 | Import, 필드명 |
| `app/templates/partials/employee_form/_family_info.html` | 2 | 필드명 |
| `app/templates/partials/employee_form/_education_info.html` | 2 | 필드명 |
| `app/templates/partials/employee_form/_career_info.html` | 2 | 필드명, 구조 |
| `app/templates/partials/employee_form/_certificate_info.html` | 2 | 필드명 |
| `app/templates/partials/employee_form/_language_info.html` | 2 | 필드명 |

### 영향받는 기능

- 직원 등록
- 직원 수정
- 직원 상세 조회

### 영향받지 않는 기능

- 직원 목록 조회
- 직원 삭제
- 조직 관리
- 사용자 관리

---

## 예상 소요 시간

| Phase | 작업 | 예상 시간 |
|-------|------|----------|
| Phase 1 | CRITICAL 수정 | 10분 |
| Phase 2 | HIGH 수정 | 20분 |
| Phase 3 | 브라우저 검증 | 15분 |
| Phase 4 | Git 커밋 | 5분 |
| **합계** | | **50분** |

---

## 후속 작업 (별도 워크플로우)

다음 작업은 본 워크플로우 완료 후 별도 진행:

1. **4대보험 처리 구현**: Insurance 모델 확장 + update_insurance_data() 구현
2. **급여정보 처리 구현**: Salary 모델 확장 + update_salary_data() 구현
3. **계약정보 처리 구현**: Employee 모델 확장 + update_contract_data() 구현
