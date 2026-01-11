# HR Card Migration - 사이드바 영역

> 분할 계획 1/3: 사이드바 검색 및 섹션 네비게이션
> 생성일: 2026-01-11
> 우선순위: **2순위** (메인 영역 완료 후)

---

## 1. 개요

### 1.1 범위
- 직원 검색 기능 (사이드바 내)
- 섹션 네비게이션 (메인 → 사이드바 이동)

### 1.2 예상 기간
**총 1.1일** (잔여 작업)

### 1.3 진행률
**약 50%** (CSS 완료, JS 미완료)

---

## 2. Phase 목록

| Phase | 내용 | 기간 | 진행률 | 상태 |
|-------|------|------|--------|------|
| **04** | Sidebar Search - 검색 기능 | 0.6일 | 60% | 진행중 |
| **08** | Section Nav → Sidebar Migration | 0.5일 | 0% | 미완료 |

---

## 3. 상세 작업

### 3.1 Phase 04: Sidebar Search (0.6일)

**완료 항목**:
- [x] sidebar-search.css 작성 (`css/shared/components/`)
- [x] 검색 API 구현 (`GET /api/employees?search=`)
- [x] styleguide 템플릿 (`sidebar-search.html`)

**잔여 항목**:
- [ ] sidebar-search.js 컴포넌트 생성

**JavaScript 구현 사항**:
```javascript
// js/domains/employee/components/sidebar-search.js
class SidebarSearch {
    constructor(inputElement, options) {
        this.options = {
            debounceMs: 300,
            minChars: 2,
            maxResults: 10,
            apiUrl: '/api/employees'
        };
    }

    _search() { }           // API 검색
    _renderResults() { }    // 결과 렌더링
    _openModal() { }        // 모달 열기
    _closeModal() { }       // 모달 닫기
}

// 화면 연결
function selectEmployee(empId) {
    closeModal('search-result-modal');
    window.location.href = `/employees/${empId}`;
}
```

### 3.2 Phase 08: Section Nav Migration (0.5일)

**현재 상태**:
- `.section-nav` (250px)가 메인 콘텐츠 내부에 위치
- CSS: `css/shared/layouts/section-nav.css`

**목표 상태**:
- `.employee-card-nav` + `.sub-nav`가 메인 사이드바 내부에 위치

**작업 항목**:
- [ ] section-nav.css 확장 (employee-card-nav, sub-nav 스타일)
- [ ] sidebar-nav.js 생성 (확장/축소 토글, 섹션 스크롤)
- [ ] 사이드바 템플릿에 마크업 추가

**CSS 구현**:
```css
/* employee-card-nav 스타일 */
.employee-card-nav {
    margin: 8px 12px;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    overflow: hidden;
}

/* sub-nav 확장/축소 */
.sub-nav {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out;
}

.employee-card-nav.expanded .sub-nav {
    max-height: 800px;
}
```

**JavaScript 구현**:
```javascript
// js/shared/components/sidebar-nav.js
document.querySelectorAll('.employee-card-header').forEach(header => {
    header.addEventListener('click', () => {
        const card = header.closest('.employee-card-nav');
        card.classList.toggle('expanded');
    });
});

document.querySelectorAll('.sub-nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // active 상태 관리
        document.querySelectorAll('.sub-nav-item').forEach(i =>
            i.classList.remove('active'));
        item.classList.add('active');

        // 해당 섹션으로 스크롤
        const targetId = item.dataset.section;
        document.getElementById(targetId)?.scrollIntoView({
            behavior: 'smooth'
        });
    });
});
```

---

## 4. 의존성

| 항목 | 의존 대상 | 상태 |
|------|----------|------|
| Phase 04 | Phase 02 (Modal/Toast) | 진행중 |
| Phase 08 | Phase 01 (CSS Variables) | 완료 |

---

## 5. 실행 순서

```
Day 1:
  [sidebar-search.js] Phase 04 (0.6일)
  - 디바운스 검색 구현
  - 모달 결과 표시
  - selectEmployee() 화면 연결

Day 1.5:
  [section-nav → sidebar] Phase 08 (0.5일)
  - CSS 확장
  - sidebar-nav.js 생성
  - 템플릿 마크업 추가
```

---

## 6. 테스트 체크리스트

### 6.1 Sidebar Search
- [ ] 검색어 2글자 이상 입력 시 검색 실행
- [ ] 디바운스 300ms 동작 확인
- [ ] 검색 결과 모달 표시
- [ ] 결과 클릭 시 `/employees/<id>` 이동
- [ ] 검색 결과 없음 메시지 표시

### 6.2 Section Nav
- [ ] 프로필 카드 클릭 시 확장/축소
- [ ] 섹션 항목 클릭 시 스크롤 이동
- [ ] active 상태 시각적 표시
- [ ] 모바일 반응형 동작

---

## 7. 파일 목록

### 7.1 생성할 파일
| 파일 | 경로 |
|------|------|
| sidebar-search.js | `js/domains/employee/components/` |
| sidebar-nav.js | `js/shared/components/` |

### 7.2 수정할 파일
| 파일 | 수정 내용 |
|------|----------|
| section-nav.css | employee-card-nav, sub-nav 스타일 추가 |
| 사이드바 템플릿 | employee-card-nav 마크업 추가 |
