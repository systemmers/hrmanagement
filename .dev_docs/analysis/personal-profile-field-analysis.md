# 개인계정 프로필 상세/수정 필드 비교 분석

> 작성일: 2025-12-14
> 분석 대상: 개인계정(account_type='personal') 프로필 페이지
> 참조 문서: profile-condition-and-field-analysis.md (법인 계정 분석)

---

## 1. 개인계정 아키텍처 요약

### 1.1 라우트 구조

| 라우트 | 파일 | 동작 |
|--------|------|------|
| `/personal/profile` | personal.py:126-131 | `/profile`로 301 리다이렉트 |
| `/personal/profile/edit` GET | personal.py:134-146 | `/profile/edit`로 301 리다이렉트 |
| `/personal/profile/edit` POST | personal.py:148-208 | 개인 프로필 저장 처리 |
| `/profile` | profile/routes.py:18-46 | 통합 프로필 상세 (page_mode='profile') |
| `/profile/edit` | profile/routes.py:49-84 | 통합 프로필 수정 (page_mode='profile') |

### 1.2 데이터 모델

| 모델 | 테이블 | 설명 |
|------|--------|------|
| PersonalProfile | personal_profiles | 기본 개인정보 |
| PersonalEducation | personal_educations | 학력정보 |
| PersonalCareer | personal_careers | 경력정보 |
| PersonalCertificate | personal_certificates | 자격증 |
| PersonalLanguage | personal_languages | 언어능력 |
| PersonalMilitaryService | personal_military_services | 병역정보 |
| PersonalAward | personal_awards | 수상내역 |

### 1.3 어댑터 사용

- **어댑터**: `PersonalProfileAdapter`
- **사용 가능 섹션**: `['basic', 'education', 'career', 'certificate', 'language', 'military', 'award']`
- **is_corporate**: 항상 `False`
- **account_type**: `'personal'`

---

## 2. 상세 페이지 vs 수정 페이지 필드 비교

### 2.1 개인 기본정보 섹션

#### 상세 페이지 (`_basic_info.html`)
| 필드 | 변수명 | 라인 |
|------|--------|------|
| 성명 (한글) | employee.name | 14 |
| 여권명 (영문) | employee.english_name | 15 |
| 주민등록번호 | employee.resident_number | 16 |
| 생년월일 | employee.birth_date | 17 |
| 성별 | employee.gender | 18 |
| 결혼여부 | employee.marital_status | 21-24 |
| 휴대전화 | employee.phone | 25 |
| 개인 이메일 | employee.email | 26 |
| 비상연락처 | employee.emergency_contact | 27-31 |
| 혈액형 | employee.blood_type | 34 |
| 종교 | employee.religion | 35 |
| 취미 | employee.hobby | 36 |
| 특기 | employee.specialty | 37 |
| 장애정보 | employee.disability_info | 38 |
| 주민등록상 주소 | employee.address | 41 |
| 상세주소 | employee.detailed_address | 42 |
| 실제 거주지 | employee.actual_address | 47 |
| 실거주 상세주소 | employee.actual_detailed_address | 48 |

#### 수정 페이지 (`_personal_info.html`)
| 필드 | name 속성 | 라인 |
|------|-----------|------|
| 이름 | name | 67 |
| 영문 이름 | name_en | 74 |
| 생년월일 | birth_date | 81 |
| 성별 | gender | 87 |
| 결혼여부 | marital_status | 96 |
| 휴대전화 | phone | 107 |
| 이메일 | email | 114 |
| 주소 | address | 122 |
| 상세주소 | detailed_address | 133 |
| 비상연락처 | emergency_contact | 140 |
| 비상연락처 관계 | emergency_relation | 147 |
| 주민등록번호 | rrn | 154 |
| 혈액형 | blood_type | 164 |
| 종교 | religion | 175 |
| 취미 | hobby | 182 |
| 특기 | specialty | 189 |
| 장애정보 | disability_info | 196 |
| 실제 거주지 | actual_address | 209 |
| 실거주 상세주소 | actual_detailed_address | 220 |

#### 비교 결과

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
| 비상연락처 관계 | O (inline) | O | OK |
| 혈액형 | O | O | OK |
| 종교 | O | O | OK |
| 취미 | O | O | OK |
| 특기 | O | O | OK |
| 장애정보 | O | O | OK |
| 주소 | O | O | OK |
| 상세주소 | O | O | OK |
| 실제 거주지 | O | O | OK |
| 실거주 상세주소 | O | O | OK |

**결과**: 19개 필드 완전 일치

---

### 2.2 학력정보 섹션

#### 상세 페이지 (`_history_info.html` 라인 7-54)
| 컬럼 | 변수명 |
|------|--------|
| 학력구분 | edu.degree |
| 학교명 | edu.school |
| 졸업년월 | edu.graduation_year |
| 학부/학과 | edu.major |
| 전공 | edu.major |
| 학점 | edu.gpa |
| 졸업유무 | (고정: 졸업) |
| 비고 | edu.note |

#### 수정 페이지 (`_education_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 학교명 | education_school_name[] |
| 학위 | education_degree[] |
| 전공 | education_major[] |
| 졸업년도 | education_graduation_year[] |
| 학점 | education_gpa[] |
| 졸업유무 | education_graduation_status[] |
| 비고 | education_note[] |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 학력구분/학위 | O | O | OK |
| 학교명 | O | O | OK |
| 졸업년월/년도 | O | O | OK |
| 학부/학과 | O | - | **MISSING** |
| 전공 | O | O | OK |
| 학점 | O | O | OK |
| 졸업유무 | O | O | OK |
| 비고 | O | O | OK |

**결과**: 상세 8컬럼 vs 수정 7필드 (1개 누락: 학부/학과)

**참고**: 상세 페이지에서 학부/학과와 전공이 모두 `edu.major`를 표시하고 있어 중복임

---

### 2.3 경력정보 섹션

#### 상세 페이지 (`_history_info.html` 라인 56-111)
| 컬럼 | 변수명 |
|------|--------|
| 직장명 | career.company |
| 입사일 | career.start_date |
| 퇴사일 | career.end_date |
| 경력 | (계산값 `-`) |
| 부서 | career.department |
| 직급 | career.position |
| 담당업무 | career.duty |
| 연봉 | career.salary |

#### 수정 페이지 (`_career_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 회사명 | career_company_name[] |
| 부서 | career_department[] |
| 직급/직책 | career_position[] |
| 담당업무 | career_duties[] |
| 연봉 | career_salary[] |
| 입사일 | career_start_date[] |
| 퇴사일 | career_end_date[] |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 직장명/회사명 | O | O | OK |
| 입사일 | O | O | OK |
| 퇴사일 | O | O | OK |
| 경력 (계산값) | O | - | N/A (계산값) |
| 부서 | O | O | OK |
| 직급/직책 | O | O | OK |
| 담당업무 | O | O | OK |
| 연봉 | O | O | OK |

**결과**: 7개 필드 완전 일치 (경력은 계산값으로 제외)

---

### 2.4 자격증 및 면허 섹션

#### 상세 페이지 (`_history_info.html` 라인 113-156)
| 컬럼 | 변수명 |
|------|--------|
| 구분 | (고정: 자격증) |
| 종류 | cert.name |
| 등급/점수 | cert.certificate_number |
| 발행처 | cert.issuer |
| 취득일 | cert.acquired_date |
| 비고 | cert.expiry_date |

#### 수정 페이지 (`_certificate_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 자격증명 | certificate_name[] |
| 발급기관 | certificate_issuer[] |
| 등급/점수 | certificate_grade[] |
| 취득일 | certificate_date[] |
| 자격번호 | certificate_number[] |
| 만료일 | certificate_expiry_date[] |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 구분 | O (고정값) | - | N/A |
| 종류/자격증명 | O | O | OK |
| 등급/점수 | O | O | OK |
| 자격번호 | - | O | 수정에만 존재 |
| 발행처/발급기관 | O | O | OK |
| 취득일 | O | O | OK |
| 비고/만료일 | O | O | OK |

**결과**: 구조 상이하나 데이터는 커버됨. 상세 페이지에서 `등급/점수`로 `certificate_number`를 표시 중 (의미 불일치)

---

### 2.5 언어능력 섹션

#### 상세 페이지 (`_history_info.html` 라인 158-199)
| 컬럼 | 변수명 |
|------|--------|
| 언어 | lang.language |
| 수준 | lang.level |
| 시험명 | lang.test_name |
| 점수 | lang.score |
| 취득일 | lang.acquired_date |

#### 수정 페이지 (`_language_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 언어 | language_name[] |
| 수준 | language_level[] |
| 시험명 | language_test_name[] |
| 점수/급수 | language_score[] |
| 취득일 | language_test_date[] |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 언어 | O | O | OK |
| 수준 | O | O | OK |
| 시험명 | O | O | OK |
| 점수/급수 | O | O | OK |
| 취득일 | O | O | OK |

**결과**: 5개 필드 완전 일치

---

### 2.6 병역정보 섹션

#### 상세 페이지 (`_history_info.html` 라인 201-236)
| 필드 | 변수명 |
|------|--------|
| 병역구분 | military.status |
| 군별 | military.branch |
| 복무기간 | military.start_date ~ military.end_date |
| 계급 | military.rank |
| 보직 | military.duty |
| 병과 | military.specialty |
| 면제사유 | military.exemption_reason |

#### 수정 페이지 (`_military_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 병역사항 | military_status |
| 군별 | military_branch |
| 계급 | military_rank |
| 복무기간 | military_period |
| 보직 | military_duty |
| 병과 | military_specialty |
| 면제사유 | military_exemption_reason |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 병역구분/병역사항 | O | O | OK |
| 군별 | O | O | OK |
| 복무기간 | O (start~end) | O (period) | **형식 상이** |
| 계급 | O | O | OK |
| 보직 | O | O | OK |
| 병과 | O | O | OK |
| 면제사유 | O | O | OK |

**결과**: 7개 필드 일치, 복무기간 형식만 상이 (상세: start_date~end_date, 수정: period 텍스트)

---

### 2.7 가족정보 섹션

#### 상세 페이지 (`_basic_info.html` 라인 200-243)
| 컬럼 | 변수명 |
|------|--------|
| 관계 | family.relation |
| 성명 | family.name |
| 생년월일 | family.birth_date |
| 직업 | family.occupation |
| 연락처 | family.phone |
| 동거여부 | family.living_together |

#### 수정 페이지 (`_family_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 관계 | family_relation[] |
| 성명 | family_name[] |
| 생년월일 | family_birth_date[] |
| 직업 | family_occupation[] |
| 연락처 | family_phone[] |
| 동거여부 | family_living_together[] |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 관계 | O | O | OK |
| 성명 | O | O | OK |
| 생년월일 | O | O | OK |
| 직업 | O | O | OK |
| 연락처 | O | O | OK |
| 동거여부 | O | O | OK |

**결과**: 6개 필드 완전 일치

---

### 2.8 수상내역 섹션

#### 상세 페이지 (`_history_info.html` 라인 238-279)
| 컬럼 | 변수명 |
|------|--------|
| 수상일 | award.award_date |
| 수상명 | award.award_name |
| 수여기관 | award.institution |
| 수상내용 | award.description |
| 비고 | award.notes |

#### 수정 페이지 (`_award_info.html`)
| 필드 | name 속성 |
|------|-----------|
| 수상명 | award_name[] |
| 수상일 | award_date[] |
| 수여기관 | award_institution[] |
| 수상내용 | award_description[] |
| 비고 | award_notes[] |

#### 비교 결과

| 필드 | 상세 페이지 | 수정 페이지 | 상태 |
|------|:-----------:|:-----------:|:----:|
| 수상일 | O | O | OK |
| 수상명 | O | O | OK |
| 수여기관 | O | O | OK |
| 수상내용 | O | O | OK |
| 비고 | O | O | OK |

**결과**: 5개 필드 완전 일치

---

## 3. 불일치 요약

### 3.1 전체 비교 결과

| 섹션 | 상세 페이지 | 수정 페이지 | 일치율 | 상태 |
|------|:-----------:|:-----------:|:------:|:----:|
| 개인 기본정보 | 19 | 19 | 100% | OK |
| 학력정보 | 8 | 7 | 87.5% | PARTIAL |
| 경력정보 | 7 | 7 | 100% | OK |
| 자격증 | 6 | 6 | 100% | OK (구조 상이) |
| 언어능력 | 5 | 5 | 100% | OK |
| 병역정보 | 7 | 7 | 100% | OK (형식 상이) |
| 가족정보 | 6 | 6 | 100% | OK |
| 수상내역 | 5 | 5 | 100% | OK |

### 3.2 발견된 문제점

| 구분 | 문제 | 위치 | 심각도 |
|------|------|------|:------:|
| 중복 표시 | 학부/학과와 전공이 모두 edu.major 표시 | `_history_info.html:34-35` | LOW |
| 필드 의미 불일치 | 등급/점수 컬럼에 certificate_number 표시 | `_history_info.html:137` | MEDIUM |
| 형식 상이 | 복무기간 입력 형식 (start~end vs period) | 상세/수정 불일치 | LOW |

### 3.3 필드명 불일치

| 섹션 | 상세 페이지 변수 | 수정 페이지 name | 차이 |
|------|-----------------|------------------|------|
| 자격증 | cert.acquired_date | certificate_date[] | 필드명 다름 |
| 언어 | lang.acquired_date | language_test_date[] | 필드명 다름 |

---

## 4. PersonalProfile 모델 필드 vs 템플릿 필드

### 4.1 PersonalProfile 모델 필드 목록

```python
# 기본 개인정보
name, english_name, chinese_name, photo
birth_date, lunar_birth, gender
mobile_phone, home_phone, email
postal_code, address, detailed_address
resident_number, nationality
blood_type, religion, hobby, specialty, disability_info, marital_status
actual_postal_code, actual_address, actual_detailed_address
emergency_contact, emergency_relation
is_public, created_at, updated_at
```

### 4.2 모델 필드 vs 수정 폼 필드 비교

| 모델 필드 | 수정 폼 | 상태 |
|-----------|---------|:----:|
| name | name | OK |
| english_name | name_en | OK (변환 필요) |
| chinese_name | - | **MISSING** |
| photo | photoFile | OK |
| birth_date | birth_date | OK |
| lunar_birth | - | **MISSING** |
| gender | gender | OK |
| mobile_phone | phone | OK (변환 필요) |
| home_phone | - | **MISSING** |
| email | email | OK |
| postal_code | postal_code (hidden) | OK |
| address | address | OK |
| detailed_address | detailed_address | OK |
| resident_number | rrn | OK (변환 필요) |
| nationality | - | **MISSING** |
| blood_type | blood_type | OK |
| religion | religion | OK |
| hobby | hobby | OK |
| specialty | specialty | OK |
| disability_info | disability_info | OK |
| marital_status | marital_status | OK |
| actual_postal_code | actual_postal_code (hidden) | OK |
| actual_address | actual_address | OK |
| actual_detailed_address | actual_detailed_address | OK |
| emergency_contact | emergency_contact | OK |
| emergency_relation | emergency_relation | OK |
| is_public | - | **MISSING** |

### 4.3 수정 폼에 누락된 모델 필드

| 필드 | 설명 | 우선순위 |
|------|------|:--------:|
| chinese_name | 한자 이름 | LOW |
| lunar_birth | 음력 생일 여부 | LOW |
| home_phone | 자택 전화 | LOW |
| nationality | 국적 | MEDIUM |
| is_public | 프로필 공개 여부 | HIGH |

---

## 5. 개인계정 POST 처리 분석

### 5.1 personal.py의 profile_edit POST 처리 (라인 177-199)

```python
data = {
    'name': request.form.get('name', profile_obj.name).strip(),
    'english_name': request.form.get('english_name', '').strip() or None,
    'chinese_name': request.form.get('chinese_name', '').strip() or None,
    'resident_number': request.form.get('resident_number', '').strip() or None,
    'birth_date': request.form.get('birth_date', '').strip() or None,
    'lunar_birth': request.form.get('lunar_birth') == 'true',
    'gender': request.form.get('gender', '').strip() or None,
    'mobile_phone': request.form.get('mobile_phone', '').strip() or None,
    'home_phone': request.form.get('home_phone', '').strip() or None,
    'email': request.form.get('email', '').strip() or None,
    'postal_code': request.form.get('postal_code', '').strip() or None,
    'address': request.form.get('address', '').strip() or None,
    'detailed_address': request.form.get('detailed_address', '').strip() or None,
    'nationality': request.form.get('nationality', '').strip() or None,
    'blood_type': request.form.get('blood_type', '').strip() or None,
    'religion': request.form.get('religion', '').strip() or None,
    'hobby': request.form.get('hobby', '').strip() or None,
    'specialty': request.form.get('specialty', '').strip() or None,
    'is_public': request.form.get('is_public') == 'true',
    'photo': photo_path,
}
```

### 5.2 POST 처리와 수정 폼 불일치

| POST 처리 필드 | 수정 폼 name | 불일치 |
|----------------|--------------|:------:|
| english_name | name_en | **불일치** |
| resident_number | rrn | **불일치** |
| mobile_phone | phone | **불일치** |
| chinese_name | - | 폼 없음 |
| lunar_birth | - | 폼 없음 |
| home_phone | - | 폼 없음 |
| nationality | - | 폼 없음 |
| is_public | - | 폼 없음 |

---

## 6. 권장 수정 사항

### 6.1 우선순위: HIGH

#### POST 처리 필드명 매핑 수정

`personal.py` 또는 수정 폼에서 필드명 통일 필요:

```python
# 현재 수정 폼의 name 속성에 맞게 POST 처리 수정
data = {
    'name': request.form.get('name', ...),
    'english_name': request.form.get('name_en', '').strip() or None,  # name_en으로 변경
    'resident_number': request.form.get('rrn', '').strip() or None,   # rrn으로 변경
    'mobile_phone': request.form.get('phone', '').strip() or None,    # phone으로 변경
    ...
}
```

또는 수정 폼의 name 속성을 모델 필드명과 일치시킴:

```html
<input type="text" name="english_name" ...>  <!-- name_en -> english_name -->
<input type="text" name="resident_number" ...>  <!-- rrn -> resident_number -->
<input type="tel" name="mobile_phone" ...>  <!-- phone -> mobile_phone -->
```

### 6.2 우선순위: MEDIUM

#### 수정 폼에 누락 필드 추가

```html
<!-- nationality -->
<div class="form-group">
    <label for="nationality" class="form-label">국적</label>
    <input type="text" id="nationality" name="nationality" class="form-input"
           value="{{ employee.nationality if employee else '' }}"
           placeholder="대한민국">
</div>

<!-- is_public -->
<div class="form-group">
    <label class="form-label">프로필 공개</label>
    <select name="is_public" class="form-input">
        <option value="false" {% if not (employee and employee.is_public) %}selected{% endif %}>비공개</option>
        <option value="true" {% if employee and employee.is_public %}selected{% endif %}>공개</option>
    </select>
</div>
```

### 6.3 우선순위: LOW

#### 상세 페이지 중복 표시 수정

`_history_info.html` 학력정보 테이블 수정:
- 학부/학과 컬럼: `edu.department` 또는 별도 필드 추가
- 또는 중복 컬럼 제거

---

## 7. 수정 대상 파일 목록

| 파일 | 수정 내용 | 우선순위 |
|------|----------|:--------:|
| `blueprints/personal.py` | POST 필드명 매핑 수정 | HIGH |
| `partials/employee_form/_personal_info.html` | nationality, is_public 필드 추가 | MEDIUM |
| `partials/employee_detail/_history_info.html` | 학력 중복 표시 수정 | LOW |
| `partials/employee_detail/_history_info.html` | 자격증 등급/점수 표시 수정 | MEDIUM |

---

## 8. 검증 체크리스트

### 8.1 필드 데이터 저장 검증

- [ ] 이름 수정 후 저장 → 정상 저장 확인
- [ ] 영문이름 수정 후 저장 → name_en → english_name 매핑 확인
- [ ] 주민번호 수정 후 저장 → rrn → resident_number 매핑 확인
- [ ] 휴대전화 수정 후 저장 → phone → mobile_phone 매핑 확인
- [ ] 학력/경력/자격증 추가/수정 후 저장 확인

### 8.2 개인계정 vs 법인계정 분리 검증

- [ ] 개인계정 `/profile` 접근 시 개인 섹션만 표시
- [ ] 개인계정 `/profile/edit` 접근 시 개인 필드만 표시
- [ ] 법인 전용 섹션(소속정보, 급여 등) 미표시 확인

---

*문서 끝*
