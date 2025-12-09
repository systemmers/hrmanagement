# 법인 개인계정 vs 일반 개인계정 인터페이스 분석

## 1. 계정 유형 정의

### 1.1 계정 구조 (user.py)
```
ACCOUNT_PERSONAL   - 일반 개인계정 (독립형 이력서/프로필 관리)
ACCOUNT_CORPORATE  - 법인 관리자 계정
ACCOUNT_EMPLOYEE_SUB - 법인 소속 직원 계정 (법인 개인계정)
```

### 1.2 데이터 관계
| 계정 유형 | company_id | parent_user_id | 특징 |
|-----------|------------|----------------|------|
| PERSONAL | NULL | NULL | 독립형, 회사 소속 없음 |
| CORPORATE | 자사 ID | NULL | 법인 관리자 |
| EMPLOYEE_SUB | 소속 회사 ID | 관리자 ID | 법인 소속 직원 |

---

## 2. 블루프린트 비교

### 2.1 일반 개인계정 (personal_bp)
**파일**: `app/blueprints/personal.py`
**URL 프리픽스**: `/personal`

| 라우트 | 기능 |
|--------|------|
| /register | 개인 회원가입 |
| /dashboard | 개인 대시보드 |
| /profile | 프로필 조회 |
| /profile/edit | 프로필 수정 |
| /education, /career, /certificate, /language | 이력 CRUD API |

### 2.2 법인 개인계정 (mypage_bp)
**파일**: `app/blueprints/mypage.py`
**URL 프리픽스**: `/my`

| 라우트 | 기능 |
|--------|------|
| /company | 회사 인사카드 조회 |

---

## 3. 템플릿 구조 비교

### 3.1 일반 개인계정 템플릿
```
app/templates/personal/
  |- dashboard.html      # 개인 대시보드
  |- profile.html        # 프로필 조회
  |- profile_edit.html   # 프로필 수정
  |- register.html       # 회원가입
```

### 3.2 법인 개인계정 템플릿
```
app/templates/mypage/
  |- company_info.html           # 회사 인사카드 (513 lines)
  |- _section_nav_company.html   # 섹션 네비게이션

app/templates/partials/employee_detail/
  |- _employee_header.html          # 법인용 헤더 (명함 포함)
  |- _employee_header_personal.html # 개인용 헤더 (명함 없음)
  |- _section_nav.html              # 전체 섹션 네비
```

---

## 4. UI/UX 차이점 분석

### 4.1 대시보드 비교

| 요소 | 일반 개인계정 | 법인 개인계정 |
|------|---------------|---------------|
| 레이아웃 | 프로필 카드 중심 | N/A (인사카드로 대체) |
| 컬러 | 녹색 (#10b981) | 기본 파랑 (--color-primary) |
| 통계 | 학력/경력/자격증/언어 개수 | N/A |
| 주요 기능 | 프로필 공개 설정, 이력 관리 | 인사카드 조회 |

### 4.2 프로필/인사카드 비교

| 요소 | 일반 개인계정 (profile.html) | 법인 개인계정 (company_info.html) |
|------|------------------------------|----------------------------------|
| **헤더** | 간단한 프로필 (이름, 연락처) | 상세 정보 + 명함 |
| **섹션** | 학력, 경력, 자격증, 언어, 병역 | 소속, 계약, 급여, 4대보험, 인사기록 |
| **네비게이션** | 단순 탭 | 그룹화된 사이드 네비 |
| **데이터** | 이력서형 (교육/경력 중심) | HR형 (급여/복리후생/보험 중심) |

### 4.3 섹션 구조 비교

#### 일반 개인계정 섹션
1. 기본 정보 (이름, 연락처, 생년월일)
2. 학력 정보
3. 경력 정보
4. 자격증/면허
5. 언어 능력
6. 병역 사항

#### 법인 개인계정 섹션
**그룹 1: 소속 및 계약**
- 소속정보 (부서, 직급, 입사일)
- 계약정보 (계약 유형, 기간)

**그룹 2: 급여 및 복리후생**
- 급여정보 (기본급, 수당)
- 연차/복리후생
- 4대보험

**그룹 3: 인사기록**
- 근로계약/연봉
- 인사이동/고과
- 근태/비품

### 4.4 헤더 컴포넌트 비교

| 요소 | 개인용 헤더 | 법인용 헤더 |
|------|-------------|-------------|
| 사진 | O | O |
| 이름 | O | O |
| 영문명 | O (조건부) | O |
| 연락처 | O | X (소속정보 대체) |
| 부서/직급 | X | O |
| 입사일/재직기간 | X | O |
| 연차 잔여 | X | O |
| 사번 | X | O |
| 명함 | X | O (업로드/삭제 가능) |

---

## 5. 통합 방안 검토

### 5.1 목표
- 법인 개인계정(company_info.html) 구조를 표준으로 채택
- 일반 개인계정도 동일한 UI/UX 적용
- 데이터 차이는 조건부 렌더링으로 처리

### 5.2 통합 설계 원칙

#### A. 공통 레이아웃 구조
```
[헤더 영역]
  |- 프로필 사진
  |- 기본 정보 (이름, 연락처)
  |- 명함 영역 (법인만 표시)

[사이드 네비게이션]
  |- 그룹화된 섹션 메뉴

[콘텐츠 영역]
  |- 섹션별 정보 카드
```

#### B. 섹션 통합 구조 (제안)

| 그룹 | 섹션 | 개인 | 법인 | 비고 |
|------|------|------|------|------|
| **기본정보** | 개인 기본정보 | O | O | 공통 |
| | 소속정보 | X | O | 법인만 |
| | 계약정보 | X | O | 법인만 |
| **급여/복리** | 급여정보 | X | O | 법인만 |
| | 연차/복리후생 | X | O | 법인만 |
| | 4대보험 | X | O | 법인만 |
| **이력/경력** | 학력정보 | O | O | 공통 |
| | 경력정보 | O | O | 공통 |
| | 자격증/면허 | O | O | 공통 |
| | 언어능력 | O | O | 공통 |
| | 병역/프로젝트 | O | O | 공통 |
| **인사기록** | 근로계약/연봉 | X | O | 법인만 |
| | 인사이동/고과 | X | O | 법인만 |
| | 근태/비품 | X | O | 법인만 |

### 5.3 템플릿 통합 방안

#### Option A: 단일 템플릿 + 조건부 렌더링 (권장)
```jinja2
{# 통합 profile_detail.html #}
{% if is_corporate_employee %}
  {% include 'partials/employee_detail/_employee_header.html' %}
{% else %}
  {% include 'partials/employee_detail/_employee_header_personal.html' %}
{% endif %}

{# 공통 섹션 #}
{% include 'partials/_basic_info.html' %}
{% include 'partials/_education_info.html' %}
{% include 'partials/_career_info.html' %}
...

{# 법인 전용 섹션 #}
{% if is_corporate_employee %}
  {% include 'partials/_organization_info.html' %}
  {% include 'partials/_salary_info.html' %}
  {% include 'partials/_insurance_info.html' %}
{% endif %}
```

#### Option B: 공통 Base 템플릿 상속
```
base_profile.html (공통 레이아웃)
  |- personal_profile.html (개인용 확장)
  |- corporate_profile.html (법인용 확장)
```

### 5.4 CSS 통합 방안

#### 현재 상태
- 개인: 녹색 (#10b981) 테마
- 법인: 파랑 (--color-primary) 테마

#### 통합 제안
```css
/* 통합 색상 변수 */
:root {
  --color-primary: #3b82f6;      /* 기본: 파랑 */
  --color-personal: #10b981;     /* 개인 강조: 녹색 */
}

/* 계정 타입별 테마 적용 */
.account-personal {
  --theme-color: var(--color-personal);
}
.account-corporate {
  --theme-color: var(--color-primary);
}
```

### 5.5 라우트 통합 방안

#### 현재 라우트
```
/personal/profile      -> personal/profile.html
/my/company           -> mypage/company_info.html
```

#### 통합 제안
```
/profile              -> 통합 프로필 (자동 분기)
  |- 개인: 기본 이력서 뷰
  |- 법인: 인사카드 뷰

/profile/edit         -> 통합 편집 폼
```

---

## 6. 구현 우선순위

### Phase 1: 템플릿 구조 통합 (HIGH)
1. [ ] 통합 섹션 네비게이션 컴포넌트 생성
2. [ ] 조건부 헤더 렌더링 구현
3. [ ] 공통 섹션 partial 정리

### Phase 2: 라우트 통합 (MEDIUM)
1. [ ] 통합 프로필 라우트 생성
2. [ ] 계정 타입별 자동 분기 로직
3. [ ] 기존 라우트 리다이렉트

### Phase 3: CSS/테마 통합 (MEDIUM)
1. [ ] 통합 CSS 변수 체계 구축
2. [ ] 계정 타입별 테마 클래스 적용
3. [ ] 기존 하드코딩 색상 정리

### Phase 4: 기능 통합 (LOW)
1. [ ] 개인계정에 명함 기능 추가 (선택적)
2. [ ] 법인계정에 이력서 내보내기 추가
3. [ ] 통합 검색 기능

---

## 7. 결론 및 권장사항

### 7.1 핵심 권장사항
1. **법인 개인계정(company_info.html) 구조를 표준으로 채택**
   - 그룹화된 섹션 네비게이션
   - 상세한 헤더 정보 구조
   - 확장 가능한 섹션 구조

2. **조건부 렌더링으로 차이 처리**
   - 개인: HR 관련 섹션 숨김
   - 법인: 전체 섹션 표시

3. **점진적 마이그레이션**
   - 기존 라우트 유지하며 리다이렉트
   - 새 통합 템플릿으로 단계적 전환

### 7.2 예상 효과
- 코드 중복 50% 이상 감소
- 일관된 사용자 경험 제공
- 유지보수 효율성 향상
- 새 기능 추가시 양쪽 적용 용이

### 7.3 주의사항
- 기존 사용자 경험 급격한 변화 방지
- 개인계정의 단순함 유지 필요
- 반응형 디자인 고려
