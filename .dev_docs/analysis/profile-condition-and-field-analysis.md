# 법인계정/법인직원 프로필 조건 및 필드 차이 분석

> 작성일: 2025-12-13
> 분석 요청: 법인계정과 법인 직원계정의 프로필 섹션 조건 비교, 상세/수정 페이지 필드 불일치 분석

---

## 1. 핵심 문제 요약

### 1.1 발견된 문제

| 문제 유형 | 상세 내용 | 심각도 |
|-----------|----------|:------:|
| 조건 공유 문제 | 법인 직원 프로필에서 법인 전용 섹션이 표시될 가능성 | HIGH |
| 필드 불일치 | 상세 페이지와 수정 페이지의 필드 수 불일치 | HIGH |
| 데이터 손실 위험 | 수정 폼에 없는 필드는 저장 시 누락될 수 있음 | HIGH |

---

## 2. 계정 유형별 조건 분석

### 2.1 계정 유형 정의

| 계정 유형 | account_type | is_corporate | 어댑터 | 설명 |
|-----------|--------------|:------------:|--------|------|
| 법인 관리자 | `corporate_admin` | `true` | CorporateAdminProfileAdapter | 회사 관리자 |
| 법인 직원 | `corporate` | `true` | EmployeeProfileAdapter | 회사 소속 직원 |
| 개인 계정 | `personal` | `false` | PersonalProfileAdapter | 일반 개인 |

### 2.2 현재 조건 체계

#### 라우트별 page_mode 설정

| 라우트 | 파일 | page_mode | 용도 |
|--------|------|-----------|------|
| `/profile` | profile/routes.py:44 | `profile` | 모든 계정의 프로필 조회 |
| `/profile/edit` | profile/routes.py:82 | `profile` | 모든 계정의 프로필 수정 |
| `/my/company` | mypage.py:109 | `hr_card` | 법인 직원의 인사카드 |
| `/employees/<id>` | employees/routes.py:172 | `hr_card` | 관리자의 직원 상세 |

#### 템플릿 섹션 조건

```jinja2
{# 법인 전용 섹션 조건 #}
{% if page_mode == 'hr_card' %}
    {# 소속정보, 계약정보, 급여정보, 복리후생, 4대보험 #}
{% endif %}

{# 인사기록 조건 #}
{% if page_mode == 'hr_card' and account_type != 'corporate_admin' %}
    {# 근로계약, 인사이동, 근태/비품 #}
{% endif %}
```

### 2.3 문제점 분석

#### 현재 상태

```
법인 직원 → /profile 접근
├── page_mode = 'profile' (라우트에서 설정)
├── is_corporate = true (어댑터에서 반환)
├── account_type = 'corporate' (어댑터에서 반환)
└── 결과: page_mode != 'hr_card' → 법인 전용 섹션 미표시 (정상)
```

#### 잠재적 문제

1. **어댑터의 is_corporate 불일치**
   - `EmployeeProfileAdapter.is_corporate()` → 항상 `True`
   - 법인 직원 프로필에서 개인 계정과 동일한 섹션만 보여야 하는데, `is_corporate` 조건을 사용하는 곳에서 문제 발생 가능

2. **edit.html의 혼합 조건**
   ```jinja2
   {# Line 29: CSS 로드 #}
   {% if is_corporate %}

   {# Line 37: employee role 체크 #}
   {% set is_employee_role = is_corporate and current_user and current_user.role == 'employee' %}

   {# Line 87: 폼 액션 설정 #}
   {% if is_corporate and account_type != 'corporate_admin' %}
   ```

3. **page_mode가 아닌 is_corporate 사용 가능성**
   - 일부 로직에서 `page_mode` 대신 `is_corporate`를 조건으로 사용하면 법인 직원 프로필에서도 법인 전용 요소가 표시될 수 있음

---

## 3. 상세 페이지 vs 수정 페이지 필드 비교

### 3.1 개인 기본정보 (일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 이름 | O | O | OK |
| 영문이름 | O | O | OK |
| 주민등록번호 | O | O | OK |
| 생년월일 | O | O | OK |
| 성별 | O | O | OK |
| 결혼여부 | O | O | OK |
| 휴대전화 | O | O | OK |
| 이메일 | O | O | OK |
| 비상연락처 | O | O | OK |
| 비상연락처 관계 | O | O | OK |
| 혈액형 | O | O | OK |
| 종교 | O | O | OK |
| 취미 | O | O | OK |
| 특기 | O | O | OK |
| 장애정보 | O | O | OK |
| 주소 | O | O | OK |
| 상세주소 | O | O | OK |
| 실제 거주지 | O | O | OK |
| 실거주 상세주소 | O | O | OK |

**결과**: 18개 필드 일치

---

### 3.2 학력정보 (불일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 학력구분/학위 | O | O | OK |
| 학교명 | O | O | OK |
| 졸업년월/졸업년도 | O | O | OK |
| 학부/학과 | O | - | MISSING |
| 전공 | O | O | OK |
| 학점 | O | - | MISSING |
| 졸업유무 | O | - | MISSING |
| 비고 | O | - | MISSING |

**결과**: 상세 8컬럼 vs 수정 4필드 (4개 누락)

---

### 3.3 경력정보 (불일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 직장명/회사명 | O | O | OK |
| 입사일 | O | O | OK |
| 퇴사일 | O | O | OK |
| 경력 (계산값) | O | - | MISSING |
| 부서 | O | - | MISSING |
| 직급/직책 | O | O | OK |
| 담당업무 | O | O | OK |
| 연봉 | O | - | MISSING |

**결과**: 상세 8컬럼 vs 수정 5필드 (3개 누락)

---

### 3.4 자격증 및 면허 (불일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 구분 | O (고정값) | - | N/A |
| 종류/자격증명 | O | O | OK |
| 등급/점수 | O | - | MISSING |
| 자격번호 | - | O | OK |
| 발행처/발급기관 | O | O | OK |
| 취득일 | O | O | OK |
| 비고/만료일 | O | - | MISSING |

**결과**: 상세 6컬럼 vs 수정 4필드 (컬럼 구성 상이)

---

### 3.5 언어능력 (일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 언어 | O | O | OK |
| 수준 | O | O | OK |
| 시험명 | O | O | OK |
| 점수/급수 | O | O | OK |
| 취득일 | O | O | OK |

**결과**: 5개 필드 일치

---

### 3.6 가족정보 (불일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 관계 | O | O | OK |
| 성명 | O | O | OK |
| 생년월일 | O | O | OK |
| 직업 | O | O | OK |
| 연락처 | O | - | MISSING |
| 동거여부 | O | - | MISSING |

**결과**: 상세 6컬럼 vs 수정 4필드 (2개 누락)

---

### 3.7 병역정보 (일치)

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 병역구분/병역사항 | O | O | OK |
| 군별 | O | O | OK |
| 복무기간 | O | O | OK |
| 계급 | O | O | OK |
| 보직 | O | O | OK |
| 병과 | O | O | OK |
| 면제사유 | O | O | OK |

**결과**: 7개 필드 일치

---

## 4. 불일치 요약

### 4.1 수정 페이지에 누락된 필드

| 섹션 | 누락 필드 | 수정 필요 파일 |
|------|----------|----------------|
| 학력정보 | 학부/학과, 학점, 졸업유무, 비고 | `_education_info.html` |
| 경력정보 | 부서, 연봉 | `_career_info.html` |
| 자격증 | 등급/점수, 비고/만료일 | `_certificate_info.html` |
| 가족정보 | 연락처, 동거여부 | `_family_info.html` |

### 4.2 필드명 불일치

| 섹션 | 상세 페이지 | 수정 페이지 | 비고 |
|------|------------|------------|------|
| 학력 | school | school_name | 필드명 다름 |
| 학력 | graduation_year | graduation_year | 일치 |
| 경력 | company | company_name | 필드명 다름 |
| 경력 | duty | job_description | 필드명 다름 |
| 자격증 | name | certificate_name | 필드명 다름 |
| 자격증 | issuer | issuing_organization | 필드명 다름 |
| 자격증 | acquired_date | acquisition_date | 필드명 다름 |

---

## 5. 권장 수정 사항

### 5.1 조건 분리 (우선순위: HIGH)

법인 직원이 프로필 페이지에서 개인 계정과 동일한 섹션만 보이도록 조건 명확화:

```jinja2
{# 현재 조건 #}
{% if page_mode == 'hr_card' %}

{# 권장 조건 (명시적) #}
{% if page_mode == 'hr_card' and not is_profile_view %}
```

또는 라우트에서 명시적 플래그 추가:

```python
# profile/routes.py
context['show_corporate_sections'] = False  # 프로필에서는 항상 숨김
```

### 5.2 수정 폼 필드 추가 (우선순위: HIGH)

#### `_education_info.html` 수정

```html
{# 추가 필요 필드 #}
<div class="form-group">
    <label class="form-label">학부/학과</label>
    <input type="text" name="education_department[]" class="form-input"
           value="{{ edu.department }}" placeholder="학부/학과명">
</div>
<div class="form-group">
    <label class="form-label">학점</label>
    <input type="text" name="education_gpa[]" class="form-input"
           value="{{ edu.gpa }}" placeholder="4.0/4.5">
</div>
<div class="form-group">
    <label class="form-label">졸업유무</label>
    <select name="education_graduation_status[]" class="form-input">
        <option value="graduated">졸업</option>
        <option value="enrolled">재학</option>
        <option value="leave">휴학</option>
        <option value="dropout">중퇴</option>
    </select>
</div>
<div class="form-group">
    <label class="form-label">비고</label>
    <input type="text" name="education_note[]" class="form-input"
           value="{{ edu.note }}" placeholder="비고">
</div>
```

#### `_family_info.html` 수정

```html
{# 추가 필요 필드 #}
<div class="form-group">
    <label class="form-label">연락처</label>
    <input type="tel" name="family_phone[]" class="form-input"
           value="{{ member.phone }}" placeholder="010-0000-0000">
</div>
<div class="form-group">
    <label class="form-label">동거여부</label>
    <select name="family_living_together[]" class="form-input">
        <option value="true">동거</option>
        <option value="false">별거</option>
    </select>
</div>
```

#### `_career_info.html` 수정

```html
{# 추가 필요 필드 #}
<div class="form-group">
    <label class="form-label">부서</label>
    <input type="text" name="career_department[]" class="form-input"
           value="{{ career.department }}" placeholder="부서명">
</div>
<div class="form-group">
    <label class="form-label">연봉</label>
    <input type="number" name="career_salary[]" class="form-input"
           value="{{ career.salary }}" placeholder="연봉 (원)">
</div>
```

### 5.3 필드명 통일 (우선순위: MEDIUM)

모델과 폼 필드명 일관성 확보:

| 섹션 | 권장 필드명 | 현재 폼 | 현재 모델 |
|------|------------|---------|----------|
| 학력 | school | school_name | school |
| 경력 | company | company_name | company |
| 경력 | duty | career_duties | duty |
| 자격증 | name | certificate_name | name |
| 자격증 | issuer | certificate_issuer | issuer |

---

## 6. 수정 대상 파일 목록

| 파일 | 수정 내용 |
|------|----------|
| `partials/employee_form/_education_info.html` | 학점, 졸업유무, 비고 필드 추가 |
| `partials/employee_form/_family_info.html` | 연락처, 동거여부 필드 추가 |
| `partials/employee_form/_career_info.html` | 부서, 연봉 필드 추가 |
| `partials/employee_form/_certificate_info.html` | 만료일 필드 추가 |
| `blueprints/employees/routes.py` | POST 처리에서 새 필드 처리 |
| `blueprints/personal.py` | POST 처리에서 새 필드 처리 |

---

## 7. 검증 체크리스트

### 7.1 조건 검증

- [ ] 법인 직원이 `/profile`에 접근 시 법인 전용 섹션 미표시 확인
- [ ] 법인 직원이 `/my/company`에 접근 시 법인 전용 섹션 표시 확인
- [ ] 개인 계정이 `/profile`에 접근 시 개인 섹션만 표시 확인
- [ ] 법인 관리자가 `/profile`에 접근 시 기본 섹션만 표시 확인

### 7.2 필드 검증

- [ ] 상세 페이지의 모든 필드가 수정 페이지에 존재
- [ ] 수정 후 저장 시 모든 데이터 정상 저장
- [ ] 필드명 불일치로 인한 데이터 누락 없음

---

*문서 끝*
