# 개인계정 프로필 페이지 비교 분석 보고서

> 작성일: 2025-12-14
> 분석 범위: 개인계정 프로필 상세/수정 페이지, 회사 인사카드 페이지
> 참조 문서: profile-page-comparison-analysis.md (법인 계정 분석)

---

## 1. 분석 개요

### 1.1 분석 대상 페이지

| 구분 | 파일 경로 | 용도 | page_mode |
|------|-----------|------|-----------|
| 프로필 상세 | `profile/detail.html` | 개인 계정 본인 프로필 조회 | `profile` |
| 프로필 수정 | `profile/edit.html` | 개인 계정 본인 프로필 수정 | `profile` |
| 회사 인사카드 목록 | `personal/company_card_list.html` | 계약된 법인 목록 | - |
| 회사 인사카드 상세 | `personal/company_card_detail.html` | 계약된 법인의 인사카드 조회 | `hr_card` |

### 1.2 핵심 파티셜 파일

| 파티셜 | 경로 | 역할 |
|--------|------|------|
| 헤더 카드 | `partials/employee_detail/_employee_header.html` | 프로필 헤더 |
| 기본정보 | `partials/employee_detail/_basic_info.html` | 섹션 1-7 |
| 이력정보 | `partials/employee_detail/_history_info.html` | 섹션 7-13 |

### 1.3 개인계정 아키텍처

```
개인 계정 (account_type='personal')
├── PersonalProfile 모델 (기본 개인정보)
├── PersonalProfileAdapter (어댑터)
├── 사용 가능 섹션
│   ├── basic (개인 기본정보)
│   ├── education (학력정보)
│   ├── career (경력정보)
│   ├── certificate (자격증)
│   ├── language (언어능력)
│   ├── military (병역정보)
│   └── award (수상내역)
└── 법인 전용 섹션 (미사용)
    ├── organization (소속정보)
    ├── contract (계약정보)
    ├── salary (급여정보)
    ├── benefit (복리후생)
    └── insurance (4대보험)
```

### 1.4 라우트 구조

| 라우트 | 파일 | 동작 |
|--------|------|------|
| `/personal/profile` | personal.py:126-131 | `/profile`로 301 리다이렉트 |
| `/personal/profile/edit` GET | personal.py:134-146 | `/profile/edit`로 301 리다이렉트 |
| `/personal/profile/edit` POST | personal.py:148-208 | 개인 프로필 저장 처리 |
| `/profile` | profile/routes.py:18-46 | 통합 프로필 상세 |
| `/profile/edit` | profile/routes.py:49-84 | 통합 프로필 수정 |
| `/personal/company-cards` | personal.py:396-409 | 회사 인사카드 목록 |
| `/personal/company-cards/<id>` | personal.py:412-437 | 회사 인사카드 상세 |

---

## 2. 헤더 섹션 비교

### 2.1 variant 자동 감지 로직

```jinja2
{% set header_variant = variant|default('personal' if page_mode != 'hr_card' else 'corporate') %}
```

- `page_mode != 'hr_card'` → `variant='personal'` (그린 테마)
- `page_mode == 'hr_card'` → `variant='corporate'` (파란 테마)

### 2.2 개인 프로필 메타 정보 (상단 3개 아이콘)

| 위치 | 아이콘 | 데이터 소스 |
|------|--------|-------------|
| 아이콘 1 | 이메일 (`fas fa-envelope`) | `employee.email` |
| 아이콘 2 | 휴대전화 (`fas fa-phone`) | `employee.phone` |
| 아이콘 3 | 주소 (`fas fa-map-marker-alt`) | `employee.address` |

### 2.3 개인 프로필 통계 정보 (하단 4개 항목)

| 위치 | 항목명 | 데이터 소스 |
|------|--------|-------------|
| 통계 1 | 생년월일 | `employee.birth_date` |
| 통계 2 | 계약 수 | `employee.contract_count` |
| 통계 3 | 가입일 | `employee.created_at` |
| 통계 4 | 회원번호 | `USR-{employee.id}` |

### 2.4 개인 vs 법인 헤더 비교

| 항목 | 개인 (personal) | 법인 (corporate) |
|------|:---------------:|:----------------:|
| 테마 색상 | 그린 (#34D399) | 파란 (#3B82F6) |
| 명함 영역 | X | O |
| 메타 아이콘 1 | 이메일 | 소속/부서 |
| 메타 아이콘 2 | 휴대전화 | 직급 |
| 메타 아이콘 3 | 주소 | 재직상태 |
| 통계 1 | 생년월일 | 입사일 |
| 통계 2 | 계약 수 | 재직기간 |
| 통계 3 | 가입일 | 연차 잔여 |
| 통계 4 | 회원번호 (USR-XXX) | 사번 (EMP-XXX) |

---

## 3. 기본정보 섹션 상세 (`_basic_info.html`)

### 3.1 섹션별 표시 조건 매트릭스

| 섹션 번호 | 섹션명 | 개인 (profile) | 법인 (hr_card) | 조건문 |
|:---------:|--------|:--------------:|:--------------:|--------|
| 1 | 개인 기본정보 | O | O | 없음 (항상 표시) |
| 2 | 소속정보 | X | O | `page_mode == 'hr_card'` |
| 3 | 계약정보 | X | O | `page_mode == 'hr_card'` |
| 4 | 급여정보 | X | O | `page_mode == 'hr_card'` |
| 5 | 연차 및 복리후생 | X | O | `page_mode == 'hr_card'` |
| 6 | 4대보험 | X | O | `page_mode == 'hr_card'` |
| 7 | 가족정보 | O | O | 없음 (항상 표시) |

### 3.2 섹션 1: 개인 기본정보 (19개 필드)

| 필드명 | 데이터 소스 | 타입 | 비고 |
|--------|-------------|------|------|
| 성명 (한글) | `employee.name` | text | |
| 여권명 (영문) | `employee.english_name` | text | |
| 주민등록번호 | `employee.resident_number` | text | 마스킹 필요 |
| 생년월일 | `employee.birth_date` | date | |
| 성별 | `employee.gender` | select | `get_gender_label()` |
| 결혼여부 | `employee.marital_status` | select | `get_marital_status_label()` |
| 휴대전화 | `employee.phone` | tel | `format_phone()` |
| 개인 이메일 | `employee.email` | email | highlight=true |
| 비상연락처 | `employee.emergency_contact` | text | 관계 포함 |
| 혈액형 | `employee.blood_type` | select | |
| 종교 | `employee.religion` | text | |
| 취미 | `employee.hobby` | text | |
| 특기 | `employee.specialty` | text | |
| 장애정보 | `employee.disability_info` | text | |
| 주민등록상 주소 | `employee.address` | text | |
| 상세주소 | `employee.detailed_address` | text | |
| 실제 거주지 | `employee.actual_address` | text | 항상 표시 |
| 실거주 상세주소 | `employee.actual_detailed_address` | text | |
| 비상연락처 관계 | `employee.emergency_relation` | text | inline |

### 3.3 섹션 7: 가족정보 테이블 (6개 컬럼)

| 컬럼명 | 데이터 소스 | 타입 |
|--------|-------------|------|
| 관계 | `family.relation` | select |
| 성명 | `family.name` | text |
| 생년월일 | `family.birth_date` | date |
| 직업 | `family.occupation` | text |
| 연락처 | `family.phone` | tel |
| 동거여부 | `family.living_together` | badge |

---

## 4. 이력정보 섹션 상세 (`_history_info.html`)

### 4.1 섹션별 표시 조건

| 섹션 번호 | 섹션명 | 개인 | 법인 | 조건문 |
|:---------:|--------|:----:|:----:|--------|
| 7 | 학력정보 | O | O | 없음 |
| 8 | 경력정보 | O | O | 없음 |
| 9 | 자격증 및 면허 | O | O | 없음 |
| 10 | 언어능력 | O | O | 없음 |
| 11 | 병역정보 | O | O | 없음 |
| 12 | 수상내역 | O | O | 없음 |
| 13 | 유사사업 참여경력 | X | O | `page_mode == 'hr_card'` |

### 4.2 섹션 7: 학력정보 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 학력구분 | `edu.degree` | `get_degree_label()` |
| 학교명 | `edu.school` | |
| 졸업년월 | `edu.graduation_year` | |
| 학부/학과 | `edu.major` | 중복 (전공과 동일) |
| 전공 | `edu.major` | 중복 (학부/학과와 동일) |
| 학점 | `edu.gpa` | |
| 졸업유무 | 고정값 | 졸업 badge |
| 비고 | `edu.note` | |

### 4.3 섹션 8: 경력정보 테이블 (8개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 직장명 | `career.company` | |
| 입사일 | `career.start_date` | |
| 퇴사일 | `career.end_date` | 기본값: 재직중 |
| 경력 | - | 계산 필요 |
| 부서 | `career.department` | |
| 직급 | `career.position` | |
| 담당업무 | `career.duty` | |
| 연봉 | `career.salary` | 포맷: {:,}원 |

### 4.4 섹션 9: 자격증 및 면허 테이블 (6개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 구분 | 고정값 | 자격증 |
| 종류 | `cert.name` | |
| 등급/점수 | `cert.certificate_number` | 의미 불일치 |
| 발행처 | `cert.issuer` | |
| 취득일 | `cert.acquired_date` | |
| 비고 | `cert.expiry_date` | 만료일 표시 |

### 4.5 섹션 10: 언어능력 테이블 (5개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 언어 | `lang.language` | |
| 수준 | `lang.level` | `get_level_label()` |
| 시험명 | `lang.test_name` | |
| 점수 | `lang.score` | |
| 취득일 | `lang.acquired_date` | |

### 4.6 섹션 11: 병역정보 (7개 필드)

| 필드명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 병역구분 | `military.status` | `get_military_status_label()` |
| 군별 | `military.branch` | `get_branch_label()` |
| 복무기간 | `military.start_date ~ end_date` | |
| 계급 | `military.rank` | |
| 보직 | `military.duty` | |
| 병과 | `military.specialty` | |
| 면제사유 | `military.exemption_reason` | 조건부 표시 |

### 4.7 섹션 12: 수상내역 테이블 (5개 컬럼)

| 컬럼명 | 데이터 소스 | 비고 |
|--------|-------------|------|
| 수상일 | `award.award_date` | 역순 정렬 |
| 수상명 | `award.award_name` | |
| 수여기관 | `award.institution` | |
| 수상내용 | `award.description` | |
| 비고 | `award.notes` | |

---

## 5. 회사 인사카드 페이지 (`company_card_detail.html`)

### 5.1 페이지 특성

| 항목 | 값 |
|------|-----|
| 조회 주체 | 개인 계정 |
| 데이터 출처 | PersonCorporateContract |
| 헤더 variant | corporate (override) |
| 수정 가능 | X (읽기 전용) |
| page_mode | `hr_card` |

### 5.2 데이터 출처

```python
# personal_service.py:get_company_card_data()
return {
    'employee': employee_data,      # PersonalProfile 기반
    'contract': contract_data,       # PersonCorporateContract
    'company': company_data,         # Company
    'contract_info': contract_info,  # 계약 정보
    'salary': None,                  # 미구현
    'benefit': None,                 # 미구현
    'insurance': None,               # 미구현
}
```

### 5.3 섹션 구성

| 섹션 | 섹션명 | 표시 조건 | 데이터 출처 |
|:----:|--------|-----------| ------------|
| - | 헤더 카드 | `employee` 존재 시 | PersonalProfile |
| 1 | 개인 기본정보 | 항상 | _basic_info.html (섹션1만) |
| 2 | 소속정보 | 항상 | contract |
| 3 | 계약정보 | 항상 | contract |
| 4 | 급여정보 | `salary` 존재 시 | (미구현) |
| 5 | 연차 및 복리후생 | `benefit` 존재 시 | (미구현) |
| 6 | 4대보험 | `insurance` 존재 시 | (미구현) |
| 7 | 근로계약 및 연봉 | 항상 (빈 테이블) | (미구현) |
| 8 | 인사이동 및 고과 | 항상 (빈 테이블) | (미구현) |
| 9 | 근태 및 비품 | 항상 (빈 테이블) | (미구현) |

### 5.4 회사 인사카드 vs 법인 인사카드 차이점

| 항목 | 회사 인사카드 (개인 조회) | 법인 인사카드 (관리자 조회) |
|------|:-------------------------:|:---------------------------:|
| 수정 가능 | X | O |
| 헤더 variant | corporate | corporate |
| 기본정보 | PersonalProfile | Employee |
| 소속정보 | contract 기반 | Employee 기반 |
| 급여/복리후생/4대보험 | 미구현 | 구현됨 |
| 인사기록 | 미구현 (빈 테이블) | 구현됨 |

---

## 6. 전체 필드 수 요약

### 6.1 개인 프로필 페이지 (`page_mode='profile'`)

| 섹션 | 필드/컬럼 수 |
|------|:-----------:|
| 헤더 | 7 |
| 개인 기본정보 | 19 |
| 가족정보 | 6 |
| 학력정보 | 8 |
| 경력정보 | 8 |
| 자격증 및 면허 | 6 |
| 언어능력 | 5 |
| 병역정보 | 7 |
| 수상내역 | 5 |
| **총계** | **약 71개** |

### 6.2 회사 인사카드 페이지 (개인이 조회)

| 섹션 | 필드/컬럼 수 | 구현 상태 |
|------|:-----------:|:---------:|
| 헤더 | 7 | O |
| 개인 기본정보 | 19 | O |
| 소속정보 | 약 6 | O (간소화) |
| 계약정보 | 약 5 | O (간소화) |
| 급여정보 | - | X (미구현) |
| 연차 및 복리후생 | - | X (미구현) |
| 4대보험 | - | X (미구현) |
| 근로계약 및 연봉 | - | X (빈 테이블) |
| 인사이동 및 고과 | - | X (빈 테이블) |
| 근태 및 비품 | - | X (빈 테이블) |
| **총계 (구현된 것만)** | **약 37개** | - |

### 6.3 개인 vs 법인 비교

| 구분 | 개인 프로필 | 법인 인사카드 | 차이 |
|------|:-----------:|:------------:|:----:|
| 총 섹션 수 | 8 | 14 | -6 |
| 총 필드 수 | 약 71개 | 약 165개 | -94 |
| 법인 전용 섹션 | X | O | - |
| 인사기록 섹션 | X | O | - |

---

## 7. 상세/수정 페이지 필드 비교 결과

### 7.1 전체 비교 결과 요약

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

### 7.2 발견된 문제점

| 구분 | 문제 | 위치 | 심각도 |
|------|------|------|:------:|
| 중복 표시 | 학부/학과와 전공이 모두 edu.major 표시 | `_history_info.html:34-35` | LOW |
| 필드 의미 불일치 | 등급/점수 컬럼에 certificate_number 표시 | `_history_info.html:137` | MEDIUM |
| 형식 상이 | 복무기간 입력 형식 (start~end vs period) | 상세/수정 불일치 | LOW |
| POST 필드명 불일치 | english_name vs name_en 등 | personal.py | HIGH |

### 7.3 POST 처리와 폼 필드 불일치 (Critical)

| POST 처리 필드 | 수정 폼 name | 불일치 |
|----------------|--------------|:------:|
| `english_name` | `name_en` | **불일치** |
| `resident_number` | `rrn` | **불일치** |
| `mobile_phone` | `phone` | **불일치** |
| `chinese_name` | - | 폼 없음 |
| `lunar_birth` | - | 폼 없음 |
| `home_phone` | - | 폼 없음 |
| `nationality` | - | 폼 없음 |
| `is_public` | - | 폼 없음 |

---

## 8. 발견된 문제점 및 개선 제안

### 8.1 데이터 일관성 문제

| 문제 | 상세 | 권장 조치 | 우선순위 |
|------|------|-----------|:--------:|
| POST 필드명 불일치 | `english_name` vs `name_en` 등 | 필드명 통일 필요 | HIGH |
| 학력정보 중복 컬럼 | 학부/학과, 전공 동일 데이터 | 컬럼 통합 또는 분리 | LOW |
| 자격증 필드 의미 불일치 | 등급/점수에 certificate_number 표시 | 컬럼명/데이터 일치 | MEDIUM |

### 8.2 누락 필드

| 필드 | 설명 | 위치 | 우선순위 |
|------|------|------|:--------:|
| is_public | 프로필 공개 여부 | 수정 폼 | HIGH |
| nationality | 국적 | 수정 폼 | MEDIUM |
| chinese_name | 한자 이름 | 수정 폼 | LOW |
| lunar_birth | 음력 생일 여부 | 수정 폼 | LOW |
| home_phone | 자택 전화 | 수정 폼 | LOW |

### 8.3 UX 개선 제안

| 항목 | 현재 상태 | 개선 방안 |
|------|-----------|-----------|
| 회사 인사카드 | 급여/복리후생/4대보험 미구현 | 법인이 공유하는 정보에 따라 표시 검토 |
| 경력 컬럼 | 계산값 없이 `-` 표시 | 자동 계산 구현 |
| 병역 복무기간 | 상세/수정 형식 불일치 | 형식 통일 |

### 8.4 코드 구조 개선

| 항목 | 현재 상태 | 개선 방안 |
|------|-----------|-----------|
| 회사 인사카드 | 인사기록 섹션 빈 테이블 | 데이터 없을 시 섹션 숨김 검토 |
| POST 처리 | 폼 필드명과 불일치 | 필드명 매핑 수정 |

---

## 9. 관련 파일 목록

### 9.1 템플릿 파일

```
app/templates/
├── profile/
│   ├── detail.html           # 통합 프로필 상세
│   └── edit.html             # 통합 프로필 수정
├── personal/
│   ├── company_card_list.html    # 회사 인사카드 목록
│   └── company_card_detail.html  # 회사 인사카드 상세
└── partials/
    └── employee_detail/
        ├── _employee_header.html  # 헤더 카드
        ├── _basic_info.html       # 기본정보 섹션
        └── _history_info.html     # 이력정보 섹션
```

### 9.2 라우트/서비스 파일

```
app/blueprints/
├── personal.py               # 개인 계정 라우트
└── profile/
    └── routes.py             # 통합 프로필 라우트

app/services/
└── personal_service.py       # 개인 계정 서비스

app/adapters/
└── profile_adapter.py        # 프로필 어댑터
```

### 9.3 모델 파일

```
app/models/
└── personal/
    ├── profile.py            # PersonalProfile
    ├── education.py          # PersonalEducation
    ├── career.py             # PersonalCareer
    ├── certificate.py        # PersonalCertificate
    ├── language.py           # PersonalLanguage
    ├── military.py           # PersonalMilitaryService
    └── award.py              # PersonalAward
```

---

## 10. 수정 대상 파일 목록

| 파일 | 수정 내용 | 우선순위 |
|------|----------|:--------:|
| `blueprints/personal.py` | POST 필드명 매핑 수정 | HIGH |
| `partials/employee_form/_personal_info.html` | nationality, is_public 필드 추가 | MEDIUM |
| `partials/employee_detail/_history_info.html` | 학력 중복 표시 수정 | LOW |
| `partials/employee_detail/_history_info.html` | 자격증 등급/점수 표시 수정 | MEDIUM |
| `personal/company_card_detail.html` | 빈 섹션 숨김 처리 | LOW |

---

## 11. 검증 체크리스트

### 11.1 필드 데이터 저장 검증

- [ ] 이름 수정 후 저장 → 정상 저장 확인
- [ ] 영문이름 수정 후 저장 → name_en → english_name 매핑 확인
- [ ] 주민번호 수정 후 저장 → rrn → resident_number 매핑 확인
- [ ] 휴대전화 수정 후 저장 → phone → mobile_phone 매핑 확인
- [ ] 학력/경력/자격증 추가/수정 후 저장 확인

### 11.2 개인계정 vs 법인계정 분리 검증

- [ ] 개인계정 `/profile` 접근 시 개인 섹션만 표시
- [ ] 개인계정 `/profile/edit` 접근 시 개인 필드만 표시
- [ ] 법인 전용 섹션(소속정보, 급여 등) 미표시 확인

### 11.3 회사 인사카드 검증

- [ ] 개인계정이 `/personal/company-cards` 접근 시 계약된 법인 목록 표시
- [ ] 개인계정이 `/personal/company-cards/<id>` 접근 시 인사카드 상세 표시
- [ ] 헤더 카드 정상 표시 (employee 데이터 포함)
- [ ] 읽기 전용 모드 확인 (수정 버튼 없음)

---

*문서 끝*
