# 인사카드 사이드바 레이아웃 프로토타입 문서

## 1. 개요

### 1.1 파일 정보
- **파일명**: `insacard_sidebar_layout.html`
- **위치**: `_dev_docs/prototype/`
- **크기**: 2,752줄
- **타입**: 프로토타입 HTML 파일 (단일 파일에 HTML, CSS, JavaScript 포함)
- **목적**: 인사카드 관리 시스템의 직원 상세 정보 페이지 레이아웃 프로토타입

### 1.2 프로토타입 상태
이 파일은 실제 Flask 애플리케이션 구현 전 디자인 및 레이아웃 검증을 위한 프로토타입입니다. 현재는 정적 HTML 파일로, 실제 데이터 연동 없이 하드코딩된 샘플 데이터를 사용합니다.

### 1.3 주요 특징
- **3컬럼 레이아웃**: 상단 헤더 + 좌측 사이드바 + 메인 콘텐츠 + 우측 사이드바
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **스크롤 스파이 네비게이션**: Intersection Observer API 활용
- **디자인 시스템**: CSS 변수 기반 일관된 스타일링
- **25명 데모 데이터베이스**: 샘플 직원 데이터 구조 포함

## 2. 파일 구조

### 2.1 전체 구조
```
insacard_sidebar_layout.html
├── <head>
│   ├── 메타 태그
│   ├── 외부 리소스 (Google Fonts, Font Awesome)
│   └── <style> (937줄)
│       ├── CSS 변수 정의 (디자인 시스템)
│       ├── 기본 스타일
│       ├── 헤더 스타일
│       ├── 사이드바 스타일
│       ├── 메인 콘텐츠 스타일
│       ├── 컴포넌트 스타일 (카드, 테이블, 배지 등)
│       └── 반응형 스타일
├── <body>
│   ├── 상단 헤더 (app-header)
│   ├── 메인 컨테이너 (app-container)
│   │   ├── 좌측 사이드바 (sidebar)
│   │   ├── 메인 콘텐츠 (main-content)
│   │   │   ├── 직원 헤더 (employee-header)
│   │   │   └── 정보 섹션들 (content-section)
│   │   └── 우측 사이드바 (right-sidebar)
│   ├── 모바일 메뉴 토글
│   ├── 사이드바 오버레이
│   └── 토스트 알림 컨테이너
└── <script> (125줄)
    ├── 네비게이션 스크롤 기능
    ├── Intersection Observer 섹션 감지
    ├── 모바일 메뉴 토글
    ├── 토스트 알림 시스템
    └── 헤더 검색 기능
```

### 2.2 HTML 구조 상세

#### 2.2.1 상단 헤더 (app-header)
```html
<header class="app-header">
  <div class="header-brand">로고 및 제목</div>
  <div class="header-search">검색 입력</div>
  <div class="header-actions">사용자 정보 및 로그아웃</div>
</header>
```

#### 2.2.2 좌측 사이드바 (sidebar)
```html
<aside class="sidebar">
  <div class="sidebar-header">사이드바 헤더</div>
  <nav class="sidebar-nav">
    <div class="nav-section">기본정보 메뉴</div>
    <div class="nav-section">이력 및 경력 메뉴</div>
    <div class="nav-section">인사기록 메뉴</div>
  </nav>
</aside>
```

#### 2.2.3 메인 콘텐츠 (main-content)
```html
<main class="main-content">
  <div class="employee-header">직원 헤더 정보</div>
  <section id="personal-info" class="content-section">개인 기본정보</section>
  <section id="organization-info" class="content-section">소속정보</section>
  <!-- ... 총 13개 섹션 -->
</main>
```

#### 2.2.4 우측 사이드바 (right-sidebar)
```html
<aside class="right-sidebar">
  <div class="right-sidebar-header">제목</div>
  <div class="right-sidebar-content">
    파일 업로드 버튼 및 파일 목록
  </div>
</aside>
```

## 3. 디자인 시스템

### 3.1 CSS 변수 정의

#### 3.1.1 색상 팔레트
```css
--color-pure-white: #ffffff;
--color-gray-25: #fcfcfc;
--color-gray-50: #f9f9f9;
--color-gray-75: #f6f6f6;
--color-gray-100: #f1f1f1;
--color-gray-200: #e4e4e4;
--color-gray-300: #d1d1d1;
--color-gray-400: #b4b4b4;
--color-gray-500: #888888;
--color-gray-600: #6b6b6b;
--color-gray-700: #515151;
--color-gray-800: #343434;
--color-gray-900: #1a1a1a;
```

#### 3.1.2 브랜드 색상
```css
--color-primary: #2563eb;        /* 파란색 */
--color-primary-hover: #1d4ed8;
--color-success: #10b981;        /* 초록색 */
--color-warning: #f59e0b;        /* 주황색 */
--color-danger: #ef4444;         /* 빨간색 */
--color-info: #3b82f6;           /* 정보 파란색 */
```

#### 3.1.3 타이포그래피
```css
--font-family: 'Inter', system-ui, -apple-system, sans-serif;
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.8125rem;    /* 13px */
--text-base: 0.875rem;   /* 14px */
--text-md: 0.9375rem;    /* 15px */
--text-lg: 1rem;         /* 16px */
--text-xl: 1.125rem;     /* 18px */
--text-2xl: 1.25rem;     /* 20px */
--text-3xl: 1.5rem;      /* 24px */
```

#### 3.1.4 간격 시스템
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;       /* 16px */
--space-5: 1.25rem;    /* 20px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */
```

#### 3.1.5 둥근 모서리
```css
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.375rem;  /* 6px */
--radius-lg: 0.5rem;    /* 8px */
--radius-xl: 0.75rem;   /* 12px */
--radius-2xl: 1rem;     /* 16px */
```

#### 3.1.6 그림자
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

#### 3.1.7 전환 효과
```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

#### 3.1.8 레이아웃 변수
```css
--sidebar-width: 250px;
--scroll-offset: 80px;
```

### 3.2 컴포넌트 스타일

#### 3.2.1 카드 컴포넌트
- `.card`: 기본 카드 컨테이너
- `.card-header`: 카드 헤더 영역
- `.card-title`: 카드 제목
- `.card-body`: 카드 본문 영역

#### 3.2.2 테이블 컴포넌트
- `.table-container`: 테이블 래퍼 (스크롤 지원)
- `table`: 기본 테이블 스타일
- `thead`: 테이블 헤더
- `tbody`: 테이블 본문

#### 3.2.3 배지 컴포넌트
- `.badge`: 기본 배지
- `.badge-success`: 성공 상태 (초록색)
- `.badge-warning`: 경고 상태 (주황색)
- `.badge-info`: 정보 상태 (파란색)
- `.badge-gray`: 회색 배지

#### 3.2.4 버튼 컴포넌트
- `.btn`: 기본 버튼
- `.btn-secondary`: 보조 버튼
- `.btn-logout`: 로그아웃 버튼

### 3.3 반응형 디자인

#### 3.3.1 모바일 (max-width: 767px)
- 사이드바: 고정 위치에서 슬라이드 인/아웃
- 헤더: 일부 요소 숨김 (제목, 사용자 이름)
- 메인 콘텐츠: 패딩 축소
- 직원 헤더: 세로 배치

#### 3.3.2 태블릿 (768px ~ 1023px)
- 사이드바: 240px 너비
- 우측 사이드바: 280px 너비
- 메인 콘텐츠: 패딩 조정

#### 3.3.3 데스크톱 (1024px 이상)
- 기본 스타일 유지
- 3컬럼 레이아웃 최적화

## 4. 컴포넌트 상세

### 4.1 상단 헤더 (app-header)

#### 4.1.1 구조
- **위치**: 고정 위치 (position: fixed, top: 0)
- **높이**: 64px
- **z-index**: 100

#### 4.1.2 구성 요소
1. **브랜드 영역** (header-brand)
   - 로고 (header-logo): "HR" 텍스트
   - 제목 (header-title): "인사카드 관리 시스템"

2. **검색 영역** (header-search)
   - 검색 입력 필드 (header-search-input)
   - 검색 아이콘 (header-search-icon)

3. **액션 영역** (header-actions)
   - 사용자 정보 (header-user)
     - 아바타 (header-user-avatar)
     - 사용자 이름 (header-user-name)
   - 로그아웃 버튼 (btn-logout)

### 4.2 좌측 사이드바 (sidebar)

#### 4.2.1 구조
- **너비**: 250px (--sidebar-width)
- **배경**: 흰색
- **스크롤**: 세로 스크롤 지원

#### 4.2.2 구성 요소
1. **사이드바 헤더** (sidebar-header)
   - 그라데이션 배경 (파란색)
   - 제목: "인사카드"
   - 부제목: 직원 이름 및 직급

2. **네비게이션 메뉴** (sidebar-nav)
   - **기본정보 섹션**
     - 개인 기본정보 (#personal-info)
     - 소속정보 (#organization-info)
     - 계약정보 (#contract-info)
     - 급여정보 (#salary-info)
     - 연차 및 복리후생 (#benefit-info)
     - 4대보험 (#insurance-info)
   
   - **이력 및 경력 섹션**
     - 학력정보 (#education-info)
     - 경력정보 (#career-info)
     - 자격증 및 면허 (#certificate-info)
     - 언어능력 (#language-info)
     - 병역/프로젝트/수상 (#military-info)
   
   - **인사기록 섹션**
     - 근로계약 및 연봉 (#employment-contract)
     - 인사이동 및 고과 (#personnel-movement)
     - 근태 및 비품 (#attendance-assets)

#### 4.2.3 네비게이션 아이템 스타일
- 기본: 회색 텍스트
- 호버: 배경색 변경, 파란색 텍스트
- 활성: 파란색 배경, 왼쪽 테두리 강조

### 4.3 메인 콘텐츠 영역 (main-content)

#### 4.3.1 직원 헤더 (employee-header)
- **배경**: 파란색 그라데이션
- **구성 요소**:
  - 프로필 사진 (120x120px, 원형)
  - 직원 이름 (한글/영문)
  - 메타 정보 (부서, 직급, 직무, 재직상태)
  - 통계 정보 (입사일, 재직기간, 연차 잔여, 사번)

#### 4.3.2 정보 섹션들 (content-section)
각 섹션은 `id` 속성을 가지며, 사이드바 네비게이션과 연결됩니다.

### 4.4 우측 사이드바 (right-sidebar)

#### 4.4.1 구조
- **너비**: 320px
- **용도**: 파일 첨부 관리

#### 4.4.2 구성 요소
1. **헤더**: "개인 첨부서류"
2. **파일 업로드 버튼**
3. **파일 목록** (fileList)
   - 파일 카드 (file-card)
   - 파일 아이콘 (file-icon)
   - 파일 정보 (file-info)
     - 파일명 (file-name)
     - 파일 메타데이터 (file-meta)
4. **파일 뷰어** (file-viewer)

## 5. 섹션별 정보 구조

### 5.1 개인 기본정보 (personal-info)
- 성명 (한글/영문)
- 주민등록번호
- 생년월일
- 나이
- 결혼여부
- 휴대전화
- 전화번호
- 개인 이메일
- 회사 이메일
- 비상연락처
- 주민등록상 주소

### 5.2 소속정보 (organization-info)
- 소속
- 부서
- 직급
- 직책
- 직무
- 근무형태
- 근무지
- 재직상태
- 입사일
- 재직기간

### 5.3 계약정보 (contract-info)
- 계약형태
- 계약기간
- 계약시작일
- 시용기간
- 근로시간
- 근무시간
- 휴게시간

### 5.4 급여정보 (salary-info)
- 급여형태
- 기본급
- 직책수당
- 식대
- 교통비
- 총 급여
- 급여지급일
- 급여지급방법
- 급여계좌

### 5.5 연차 및 복리후생 (benefit-info)
- 연차 발생일수
- 연차 사용일수
- 연차 잔여일수
- 퇴직금
- 퇴직금 적립방법

### 5.6 4대보험 (insurance-info)
- 4대보험 가입 여부
- 건강보험
- 국민연금
- 고용보험
- 산재보험

### 5.7 학력정보 (education-info)
**테이블 형식**:
- 학력구분
- 학교명
- 졸업년월
- 학부/학과
- 전공
- 학점
- 졸업유무
- 비고

### 5.8 경력정보 (career-info)
**테이블 형식** (입사 전 경력):
- 직장명
- 입사일
- 퇴사일
- 경력
- 부서
- 직급
- 담당업무
- 연봉

### 5.9 자격증 및 면허 (certificate-info)
**테이블 형식**:
- 구분 (자격증/면허)
- 종류
- 등급/점수
- 발행처
- 취득일
- 비고

### 5.10 언어능력 (language-info)
**테이블 형식**:
- 언어
- 수준
- 영작
- 스피킹
- 비고

### 5.11 병역/프로젝트/수상 (military-info)
**3개 하위 카드**:
1. **병역정보**
   - 병역구분
   - 군별
   - 복무기간
   - 계급
   - 보직
   - 병과

2. **유사사업 참여경력**
   - 사업명
   - 참여기간
   - 기간
   - 담당업무
   - 역할/직책
   - 발주처

3. **수상내역**
   - 수상일
   - 수상명
   - 수여기관
   - 비고

### 5.12 근로계약 및 연봉 (employment-contract)
**2개 하위 카드**:
1. **근로계약 이력**
   - 계약일
   - 계약구분
   - 계약기간 시작/종료
   - 계약기간
   - 직원구분
   - 근무형태
   - 비고

2. **연봉계약 이력**
   - 계약연도
   - 연봉
   - 상여금
   - 총액
   - 계약기간
   - 비고

### 5.13 인사이동 및 고과 (personnel-movement)
**5개 하위 카드**:
1. **인사이동 및 승진**
   - 발령일
   - 발령구분
   - 발령전/후
   - 발령전/후 직급
   - 직무
   - 발령사유

2. **인사고과 - 정기평가**
   - 연차
   - 1/2/3/4분기 평가
   - 종합평가
   - 연봉협상
   - 비고

3. **교육훈련**
   - 연차
   - 오리엔테이션
   - 직무교육
   - 법정교육
   - 상/하반기 워크샵
   - 자격증
   - 기타

4. **연봉 및 상여**
   - 연차
   - 연봉
   - 상여
   - 기타
   - 포상
   - 청구
   - 합계
   - 대출
   - 비고

5. **프로젝트 참여 이력**
   - 프로젝트명
   - 참여기간
   - 기간
   - 직책
   - 담당업무
   - 기여도
   - 발주처
   - 성공여부

6. **상벌**
   - 날짜
   - 성과
   - 혁신
   - 근속
   - 우수사원
   - 발명보상
   - 사유서
   - 시말서
   - 징계

### 5.14 근태 및 비품 관리 (attendance-assets)
**3개 하위 카드**:
1. **근태 및 연차관리**
   - 연차
   - 출근/결근/지각/조퇴/무단
   - 병가
   - 연장근무/야간근무/휴일근무
   - 출장
   - 연차발생/사용/잔여

2. **소모품 및 비품 지급관리**
   - 지급일
   - 품목
   - 수량
   - 단가
   - 금액
   - 지급구분 (대여/영구지급)
   - 반납일
   - 상태
   - 비고

3. **입퇴사 관리**
   - 구분 (면접/입사/퇴사예정)
   - 일자
   - 사유
   - 비고

## 6. JavaScript 기능

### 6.1 네비게이션 스크롤 기능

#### 6.1.1 구현 방식
```javascript
navItems.forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetId);
        
        if (targetSection) {
            const targetPosition = targetSection.offsetTop - scrollOffset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});
```

#### 6.1.2 기능 설명
- 네비게이션 아이템 클릭 시 해당 섹션으로 부드럽게 스크롤
- 스크롤 오프셋(80px)을 고려하여 정확한 위치로 이동
- 모바일에서 메뉴 클릭 시 사이드바 자동 닫기

### 6.2 Intersection Observer 섹션 감지

#### 6.2.1 구현 방식
```javascript
const observerOptions = {
    root: null,
    rootMargin: `-${scrollOffset}px 0px -50% 0px`,
    threshold: 0
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            navItems.forEach(item => item.classList.remove('active'));
            const activeNavItem = document.querySelector(`.nav-item[href="#${id}"]`);
            if (activeNavItem) {
                activeNavItem.classList.add('active');
            }
        }
    });
}, observerOptions);
```

#### 6.2.2 기능 설명
- 현재 화면에 보이는 섹션을 자동 감지
- 해당 섹션의 네비게이션 아이템에 `active` 클래스 추가
- 스크롤 시 실시간으로 활성 메뉴 업데이트

### 6.3 모바일 메뉴 토글

#### 6.3.1 구현 방식
```javascript
mobileMenuToggle.addEventListener('click', function() {
    sidebar.classList.toggle('active');
    sidebarOverlay.classList.toggle('active');
});

sidebarOverlay.addEventListener('click', function() {
    sidebar.classList.remove('active');
    sidebarOverlay.classList.remove('active');
});
```

#### 6.3.2 기능 설명
- 모바일 메뉴 버튼 클릭 시 사이드바 열기/닫기
- 오버레이 클릭 시 사이드바 닫기
- CSS transition을 통한 부드러운 애니메이션

### 6.4 토스트 알림 시스템

#### 6.4.1 구현 방식
```javascript
function showToast(message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <i class="fas fa-check-circle toast-icon"></i>
        <span class="toast-message">${message}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
```

#### 6.4.2 기능 설명
- 동적으로 토스트 알림 생성
- 3초 후 자동으로 사라짐
- 페이드 아웃 애니메이션

### 6.5 헤더 검색 기능

#### 6.5.1 구현 방식
```javascript
headerSearchInput.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    // 검색 로직 구현 (현재는 미구현)
});
```

#### 6.5.2 기능 설명
- 현재는 입력 이벤트만 처리
- 실제 검색 로직은 백엔드 연동 후 구현 예정
- 직원 목록 필터링 등의 기능 추가 가능

## 7. 25명 데모 데이터베이스

### 7.1 데이터 구조 개요

프로토타입 파일은 25명의 샘플 직원 데이터를 참조합니다. 실제 데이터는 `data/employees.json` 파일에 저장되어 있으며, 프로필 이미지는 `_dev_docs/ref/members/` 디렉토리에 있습니다.

### 7.2 프로필 이미지 경로

#### 7.2.1 members/A 디렉토리
- 경로: `_dev_docs/ref/members/A/`
- 파일명 형식: `profile_01_m.png` ~ `profile_25_f.png`
- 형식: `profile_{번호}_{성별}.png`
  - 번호: 01~25
  - 성별: m (남성), f (여성)

#### 7.2.2 members/B 디렉토리
- 경로: `_dev_docs/ref/members/B/`
- 파일명 형식: `Avatar_01_M.jpg` ~ `Avatar_25_F.jpg`
- 형식: `Avatar_{번호}_{성별}.jpg`
  - 번호: 01~25
  - 성별: M (남성), F (여성)

### 7.3 데이터 필드 매핑

#### 7.3.1 기본 필드 (employees.json)
```json
{
  "id": 1,
  "name": "김철수",
  "photo": "/static/images/face/face_01_m.png",
  "department": "개발팀",
  "position": "과장",
  "status": "active",
  "hireDate": "2020-03-15",
  "phone": "010-1234-5678",
  "email": "chulsoo.kim@company.com"
}
```

#### 7.3.2 프로토타입에서 사용하는 확장 필드
프로토타입 파일에서는 다음 추가 필드들을 하드코딩된 값으로 사용합니다:

- **영문명**: `employee-name-en` (예: "KIM SANG JIN")
- **소속**: 기술본부
- **직책**: 팀장
- **직무**: 백엔드 개발
- **사번**: EMP-001
- **재직기간**: 계산된 값 (예: "10년 8개월")
- **연차 잔여**: 계산된 값 (예: "15일")

### 7.4 실제 시스템과의 연동 방법

#### 7.4.1 데이터 소스
1. **직원 기본 정보**: `data/employees.json`
2. **프로필 이미지**: `static/images/face/` 또는 `_dev_docs/ref/members/`
3. **추가 정보**: 추후 데이터베이스 스키마 확장 필요

#### 7.4.2 템플릿 변환 시 고려사항
- Jinja2 템플릿 문법으로 변환 필요
- 하드코딩된 값들을 Flask에서 전달하는 변수로 교체
- 이미지 경로를 `url_for('static', filename='...')` 형식으로 변경
- 반복되는 섹션은 Jinja2 매크로나 include로 모듈화

## 8. 사용 가이드

### 8.1 파일 실행 방법

#### 8.1.1 직접 브라우저에서 열기
1. 파일 탐색기에서 `insacard_sidebar_layout.html` 파일 찾기
2. 브라우저로 드래그 앤 드롭 또는 더블 클릭
3. 브라우저에서 파일 열기

#### 8.1.2 로컬 서버에서 실행 (권장)
```bash
# Python 3
python -m http.server 8000

# 또는 Node.js http-server
npx http-server -p 8000
```
브라우저에서 `http://localhost:8000/_dev_docs/prototype/insacard_sidebar_layout.html` 접속

### 8.2 커스터마이징 가이드

#### 8.2.1 색상 변경
CSS 변수 섹션에서 색상 값 수정:
```css
:root {
    --color-primary: #2563eb;  /* 원하는 색상으로 변경 */
}
```

#### 8.2.2 레이아웃 크기 조정
```css
:root {
    --sidebar-width: 250px;    /* 사이드바 너비 변경 */
    --scroll-offset: 80px;     /* 스크롤 오프셋 변경 */
}
```

#### 8.2.3 폰트 변경
```css
:root {
    --font-family: '원하는 폰트', system-ui, sans-serif;
}
```

### 8.3 Flask 템플릿으로 변환 시 고려사항

#### 8.3.1 파일 분리
1. **CSS 분리**: `<style>` 태그 내용을 `static/css/` 디렉토리로 이동
2. **JavaScript 분리**: `<script>` 태그 내용을 `static/js/` 디렉토리로 이동
3. **템플릿 분리**: 섹션별로 별도 템플릿 파일 생성 또는 매크로 사용

#### 8.3.2 템플릿 구조 제안
```
templates/
├── base.html                    # 기본 레이아웃
├── employee_detail.html         # 직원 상세 페이지
└── components/
    ├── employee_header.html     # 직원 헤더 컴포넌트
    ├── info_section.html        # 정보 섹션 컴포넌트
    └── file_sidebar.html        # 파일 사이드바 컴포넌트
```

#### 8.3.3 데이터 바인딩
하드코딩된 값들을 Jinja2 변수로 교체:
```jinja2
<!-- 변경 전 -->
<div class="employee-name">김상진</div>

<!-- 변경 후 -->
<div class="employee-name">{{ employee.name }}</div>
```

## 9. 통합 가이드

### 9.1 현재 Flask 애플리케이션과의 연동

#### 9.1.1 기존 템플릿 구조
현재 Flask 애플리케이션은 다음과 같은 템플릿 구조를 사용합니다:
- `templates/base.html`: 기본 레이아웃
- `templates/employee_detail.html`: 직원 상세 페이지 (간단한 버전)

#### 9.1.2 통합 방안
1. **점진적 통합**: 기존 `employee_detail.html`을 확장하여 프로토타입 기능 추가
2. **새 템플릿 생성**: 프로토타입을 기반으로 새로운 상세 템플릿 생성
3. **컴포넌트화**: 공통 컴포넌트를 별도 파일로 분리하여 재사용

### 9.2 템플릿 분리 전략

#### 9.2.1 레이아웃 분리
```jinja2
<!-- base_detail.html -->
{% extends "base.html" %}

{% block content %}
<div class="app-container">
    {% include "components/sidebar.html" %}
    <main class="main-content">
        {% block detail_content %}{% endblock %}
    </main>
    {% include "components/right_sidebar.html" %}
</div>
{% endblock %}
```

#### 9.2.2 섹션 모듈화
```jinja2
<!-- macros/info_sections.html -->
{% macro personal_info_section(employee) %}
<section id="personal-info" class="content-section">
    <!-- 섹션 내용 -->
</section>
{% endmacro %}
```

### 9.3 CSS 모듈화 방안

#### 9.3.1 파일 구조 제안
```
static/css/
├── core/
│   ├── variables.css      # CSS 변수
│   ├── reset.css          # 리셋 스타일
│   └── responsive.css     # 반응형 미디어 쿼리
├── layouts/
│   ├── header.css         # 헤더 스타일
│   ├── sidebar.css        # 사이드바 스타일
│   └── main-content.css   # 메인 콘텐츠 스타일
├── components/
│   ├── cards.css          # 카드 컴포넌트
│   ├── tables.css         # 테이블 컴포넌트
│   └── badges.css         # 배지 컴포넌트
└── pages/
    └── employee_detail.css # 직원 상세 페이지 전용
```

#### 9.3.2 CSS 변수 통합
기존 `static/css/core/variables.css`와 프로토타입의 CSS 변수를 통합하여 일관성 유지

### 9.4 JavaScript 모듈화 방안

#### 9.4.1 파일 구조 제안
```
static/js/
├── core/
│   └── navigation.js      # 네비게이션 스크롤 기능
├── components/
│   ├── sidebar.js         # 사이드바 토글 기능
│   └── toast.js           # 토스트 알림 시스템
└── pages/
    └── employee_detail.js # 직원 상세 페이지 전용
```

#### 9.4.2 모듈화 예시
```javascript
// static/js/components/sidebar.js
export function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('mobileMenuToggle');
    
    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}
```

## 10. 참고 자료

### 10.1 관련 파일
- `templates/employee_detail.html`: 현재 구현된 간단한 직원 상세 페이지
- `data/employees.json`: 직원 데이터 파일
- `static/css/layouts/main-content.css`: 메인 콘텐츠 스타일
- `_dev_docs/README.md`: 프로젝트 개요 문서

### 10.2 외부 리소스
- **Google Fonts**: Inter 폰트
- **Font Awesome 6.4**: 아이콘 라이브러리
- **Intersection Observer API**: 섹션 감지 기능

### 10.3 브라우저 호환성
- Chrome/Edge: 완전 지원
- Firefox: 완전 지원
- Safari: 완전 지원
- 모바일 브라우저: 반응형 디자인 지원

### 10.4 성능 고려사항
- **이미지 최적화**: 프로필 이미지는 적절한 크기로 최적화 필요
- **CSS 최적화**: 프로덕션 환경에서는 CSS 압축 및 미니파이 권장
- **JavaScript 최적화**: 이벤트 리스너 최적화 및 디바운싱 고려

## 11. 변경 이력

### 11.1 버전 정보
- **버전**: 1.0.0
- **작성일**: 2025-01-26
- **작성자**: 문서화 시스템

### 11.2 주요 변경사항
- 초기 문서화 완료
- 프로토타입 구조 분석 완료
- 25명 데모 데이터베이스 정보 포함

---

**문서 끝**

