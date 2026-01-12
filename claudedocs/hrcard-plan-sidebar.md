# HR Card Migration - 사이드바 영역

> 분할 계획 1/3: 사이드바 검색 및 섹션 네비게이션
> 생성일: 2026-01-11
> 업데이트: 2026-01-11 (Phase 04, 08 구현 완료)
> 우선순위: **2순위** (메인 영역 완료 후)

---

## 1. 개요

### 1.1 범위
- 직원 검색 기능 (사이드바 내)
- 섹션 네비게이션 (메인 → 사이드바 이동)

### 1.2 예상 기간
**총 1.1일** (잔여 작업)

### 1.3 진행률
**100%** (Phase 04, 08 완료)

---

## 2. Phase 목록

| Phase | 내용 | 기간 | 진행률 | 상태 |
|-------|------|------|--------|------|
| **04** | Sidebar Search - 검색 기능 | 0.6일 | 100% | 완료 |
| **08** | Section Nav → Sidebar Migration | 0.5일 | 100% | 완료 |

---

## 3. 상세 작업

### 3.1 Phase 04: Sidebar Search (0.6일) - 완료

**완료 항목**:
- [x] sidebar-search.css 작성 (`css/shared/components/`)
- [x] 검색 API 구현 (`GET /api/employees?search=`)
- [x] styleguide 템플릿 (`sidebar-search.html`)
- [x] sidebar-search.js 컴포넌트 생성
- [x] 검색 결과 CSS 추가 (`.search-results__*`)

**검색 결과 처리 로직**:
```
검색 실행 → API 응답
    │
    ├─ results.length === 0 → 토스트 메시지 "검색 결과가 없습니다"
    │
    ├─ results.length === 1 → 바로 `/employees/<id>` 이동
    │
    └─ results.length > 1  → 모달로 선택 UI 표시
```

**생성 파일**: `js/domains/employee/components/sidebar-search.js`

### 3.2 Phase 08: Section Nav Migration (0.5일) - 완료

**완료 항목**:
- [x] section-nav.css (이미 `.section-nav-card`, `.sub-nav` 스타일 포함)
- [x] sidebar-nav.js 생성 (확장/축소 토글, 섹션 스크롤, ScrollSpy)

**생성 파일**: `js/shared/components/sidebar-nav.js`

**기능**:
- section-nav-card 확장/축소 토글
- sub-nav 아이템 클릭 시 섹션 스크롤
- active 상태 관리
- ScrollSpy (IntersectionObserver)

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
