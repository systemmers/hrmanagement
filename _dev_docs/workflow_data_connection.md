# 데이터베이스-템플릿 연결 워크플로우

## 개요

| 항목 | 값 |
|------|-----|
| 생성일 | 2025-11-25 |
| 프로젝트 | insacard (인사카드 관리 시스템) |
| 목표 | 데모 데이터 파일과 템플릿 연결 |
| 예상 작업량 | ~400줄 코드 |
| 수정 파일 | 4개 |

---

## 1. 작업 범위

### 1.1 데이터 소스 (생성 완료)
| 파일 | 레코드 | 용도 |
|------|--------|------|
| `employees_extended.json` | 25 | 확장 직원 정보 |
| `education.json` | 29 | 학력 정보 |
| `careers.json` | 28 | 경력 정보 |
| `certificates.json` | 31 | 자격증 정보 |
| `family_members.json` | 40 | 가족 정보 |
| `languages.json` | 30 | 언어 능력 |
| `military.json` | 13 | 병역 정보 |

### 1.2 수정 대상 파일
| 파일 | 현재 상태 | 수정 내용 |
|------|----------|----------|
| `config.py` | 2개 JSON 경로 | +7개 JSON 경로 |
| `models.py` | Employee 9필드 | +6모델, +6레포, +16필드 |
| `app.py` | employee만 전달 | +6레포 인스턴스, +6함수, 라우트 수정 |
| `employee_detail.html` | "정보 없음" | Jinja2 데이터 바인딩 |

---

## 2. 의존성 다이어그램

```
[Phase 1: 설정/모델]
    config.py (Step 1)
         |
         v
    models.py (Steps 2-9)
         |
         v
[Phase 2: 애플리케이션]
    app.py (Steps 10-12)
         |
         v
[Phase 3: 템플릿]
    employee_detail.html (Steps 13-20)
         |
         v
[Phase 4: 검증]
    통합 테스트 (Steps 21-23)
```

---

## 3. 실행 체크리스트

### Phase 1: 설정 및 모델 계층

#### Step 1: config.py - JSON 경로 상수 추가
- [ ] `EDUCATION_JSON = DATA_DIR / "education.json"`
- [ ] `CAREERS_JSON = DATA_DIR / "careers.json"`
- [ ] `CERTIFICATES_JSON = DATA_DIR / "certificates.json"`
- [ ] `FAMILY_MEMBERS_JSON = DATA_DIR / "family_members.json"`
- [ ] `LANGUAGES_JSON = DATA_DIR / "languages.json"`
- [ ] `MILITARY_JSON = DATA_DIR / "military.json"`
- [ ] `EMPLOYEES_EXTENDED_JSON = DATA_DIR / "employees_extended.json"`

#### Step 2-7: models.py - 6개 모델 클래스 추가
- [ ] **Step 2**: Education 클래스
  ```python
  class Education:
      id, employee_id, school, degree, major, graduation_year
  ```
- [ ] **Step 3**: Career 클래스
  ```python
  class Career:
      id, employee_id, company, position, duty, start_date, end_date
  ```
- [ ] **Step 4**: Certificate 클래스
  ```python
  class Certificate:
      id, employee_id, name, issuer, acquired_date, expiry_date, certificate_number
  ```
- [ ] **Step 5**: FamilyMember 클래스
  ```python
  class FamilyMember:
      id, employee_id, relation, name, birth_date, occupation, is_dependent
  ```
- [ ] **Step 6**: Language 클래스
  ```python
  class Language:
      id, employee_id, language, level, test_name, score, acquired_date
  ```
- [ ] **Step 7**: MilitaryService 클래스
  ```python
  class MilitaryService:
      id, employee_id, status, branch, rank, start_date, end_date, exemption_reason
  ```

#### Step 8: models.py - 6개 레포지토리 클래스 추가
- [ ] EducationRepository (`get_by_employee_id` 메서드)
- [ ] CareerRepository (`get_by_employee_id` 메서드)
- [ ] CertificateRepository (`get_by_employee_id` 메서드)
- [ ] FamilyMemberRepository (`get_by_employee_id` 메서드)
- [ ] LanguageRepository (`get_by_employee_id` 메서드)
- [ ] MilitaryServiceRepository (`get_by_employee_id` 메서드)

#### Step 9: models.py - Employee 확장 필드
- [ ] 개인정보: `name_en`, `birth_date`, `gender`, `address`, `emergency_contact`, `emergency_relation`
- [ ] 소속정보: `employee_number`, `team`, `job_title`, `work_location`, `internal_phone`, `company_email`
- [ ] 계약정보: `employment_type`, `contract_period`, `probation_end`, `resignation_date`

---

### Phase 2: 애플리케이션 계층

#### Step 10: app.py - 레포지토리 인스턴스 생성
- [ ] import 문 추가
- [ ] `education_repo = EducationRepository(config.EDUCATION_JSON)`
- [ ] `career_repo = CareerRepository(config.CAREERS_JSON)`
- [ ] `certificate_repo = CertificateRepository(config.CERTIFICATES_JSON)`
- [ ] `family_repo = FamilyMemberRepository(config.FAMILY_MEMBERS_JSON)`
- [ ] `language_repo = LanguageRepository(config.LANGUAGES_JSON)`
- [ ] `military_repo = MilitaryServiceRepository(config.MILITARY_JSON)`

#### Step 11: app.py - Context Processor 레이블 함수
- [ ] `get_degree_label(degree)` - bachelor -> 학사, master -> 석사, doctor -> 박사
- [ ] `get_level_label(level)` - advanced -> 상급, intermediate -> 중급, beginner -> 초급
- [ ] `get_relation_label(relation)` - spouse -> 배우자, child -> 자녀, parent -> 부모
- [ ] `get_military_status_label(status)` - completed -> 군필, exempted -> 면제
- [ ] `get_branch_label(branch)` - army -> 육군, navy -> 해군, airforce -> 공군
- [ ] `get_gender_label(gender)` - male -> 남성, female -> 여성

#### Step 12: app.py - employee_detail 라우트 수정
- [ ] 관계 데이터 조회 추가
- [ ] 템플릿에 전달할 변수 추가:
  ```python
  return render_template('employee_detail.html',
      employee=employee,
      education_list=education_repo.get_by_employee_id(employee_id),
      career_list=career_repo.get_by_employee_id(employee_id),
      certificate_list=certificate_repo.get_by_employee_id(employee_id),
      family_list=family_repo.get_by_employee_id(employee_id),
      language_list=language_repo.get_by_employee_id(employee_id),
      military=military_repo.get_by_employee_id(employee_id)
  )
  ```

---

### Phase 3: 프레젠테이션 계층

#### Step 13-14: 개인/소속 정보 섹션
- [ ] **Step 13**: 개인기본정보 - employee 확장 필드 바인딩
  - 영문명, 생년월일, 성별, 주소, 비상연락처
- [ ] **Step 14**: 소속정보 - employee 확장 필드 바인딩
  - 사원번호, 팀, 직책, 근무지, 내선번호, 회사이메일

#### Step 15-18: 관계 데이터 루프 바인딩
- [ ] **Step 15**: 학력정보 섹션 - `{% for edu in education_list %}`
- [ ] **Step 16**: 경력정보 섹션 - `{% for career in career_list %}`
- [ ] **Step 17**: 자격/면허 섹션 - `{% for cert in certificate_list %}`
- [ ] **Step 18**: 언어능력 섹션 - `{% for lang in language_list %}`

#### Step 19-20: 특수 섹션
- [ ] **Step 19**: 병역정보 섹션 - `{% if military %}` 단일 객체
- [ ] **Step 20**: 가족관계 섹션 - `{% for member in family_list %}`

---

### Phase 4: 검증

#### Step 21: 서버 실행 테스트
- [ ] Flask 서버 정상 실행 확인
- [ ] import 오류 없음 확인
- [ ] JSON 파일 로드 성공 확인

#### Step 22: 데이터 표시 확인
- [ ] 직원 ID 1 (김철수) - 모든 관계 데이터 있음
- [ ] 직원 ID 5 (최영호) - 부서장, 다양한 데이터
- [ ] 직원 ID 10 (박지혜) - 관리팀 팀장

#### Step 23: 빈 데이터 처리 확인
- [ ] 경력 없는 신입직원 - "등록된 경력 정보가 없습니다"
- [ ] 자격증 없는 직원 - 적절한 안내 메시지
- [ ] 여성 직원 - 병역정보 섹션 적절히 처리

---

## 4. Git 워크플로우

### 브랜치 전략
```bash
# 1. 기능 브랜치 생성
git checkout -b feature/data-template-connection

# 2. Phase별 커밋
git commit -m "feat(config): add JSON file path constants"
git commit -m "feat(models): add 6 model classes for relation data"
git commit -m "feat(models): add 6 repository classes"
git commit -m "feat(models): extend Employee class with 16 fields"
git commit -m "feat(app): add repositories and label functions"
git commit -m "feat(app): modify employee_detail route"
git commit -m "feat(template): bind data to employee_detail sections"

# 3. 머지
git checkout main
git merge feature/data-template-connection
```

### 커밋 메시지 형식
```
<type>(<scope>): <description>

Types: feat, fix, refactor, docs, style, test
Scopes: config, models, app, template
```

---

## 5. 롤백 전략

| Phase | 롤백 대상 | 복원 명령 |
|-------|----------|----------|
| Phase 1 | config.py, models.py | `git checkout HEAD~2 -- config.py models.py` |
| Phase 2 | app.py | `git checkout HEAD~1 -- app.py` |
| Phase 3 | employee_detail.html | `git checkout HEAD~1 -- templates/employee_detail.html` |

---

## 6. 진행 상태 추적

### Todo List
| # | Task | Status | Active Form |
|---|------|--------|-------------|
| 1 | config.py JSON 경로 상수 추가 | pending | config.py에 JSON 경로 상수 추가 중 |
| 2 | models.py 6개 모델 클래스 추가 | pending | models.py에 모델 클래스 추가 중 |
| 3 | models.py 6개 레포지토리 클래스 추가 | pending | models.py에 레포지토리 클래스 추가 중 |
| 4 | models.py Employee 확장 필드 추가 | pending | Employee 클래스 확장 필드 추가 중 |
| 5 | app.py 레포지토리 인스턴스 생성 | pending | app.py에 레포지토리 인스턴스 생성 중 |
| 6 | app.py Context processor 레이블 함수 추가 | pending | Context processor에 레이블 함수 추가 중 |
| 7 | app.py employee_detail 라우트 수정 | pending | employee_detail 라우트 수정 중 |
| 8 | employee_detail.html 데이터 바인딩 | pending | employee_detail.html 데이터 바인딩 적용 중 |
| 9 | 통합 테스트 및 검증 | pending | 통합 테스트 진행 중 |

---

## 7. 참조 파일

| 파일 경로 | 용도 |
|----------|------|
| `C:\workspace\insacard\config.py` | 설정 파일 |
| `C:\workspace\insacard\models.py` | 모델/레포지토리 |
| `C:\workspace\insacard\app.py` | Flask 애플리케이션 |
| `C:\workspace\insacard\templates\employee_detail.html` | 상세 페이지 템플릿 |
| `C:\workspace\insacard\data\*.json` | 데이터 소스 |
| `C:\workspace\insacard\_dev_docs\demo_database_schema.md` | 스키마 문서 |
