더 세부적으로 검토 중입니다. 실제 구현 상태를 확인합니다.


[10 tools called]


템플릿과 JavaScript에서 실제 사용 패턴을 확인 중입니다.


[6 tools called]


## 세부 분석 결과

### 1. Foundation (기초 요소) - 추가 필요

#### 1.1 아이콘 시스템
- 현재: Font Awesome 사용 중, 문서화 없음
- 추가 필요:
  - 아이콘 크기 변형 (xs, sm, md, lg, xl)
  - 아이콘 색상 변형 (primary, secondary, success, warning, error, info, muted)
  - 아이콘 배경 원형/사각형 변형
  - 아이콘 애니메이션 (spin, pulse, bounce)
  - 아이콘 버튼 조합 가이드
  - 아이콘 텍스트 정렬 가이드

#### 1.2 간격 토큰 확장
- 현재: 기본 간격만 정의
- 추가 필요:
  - 간격 유틸리티 클래스 (margin, padding, gap)
  - 반응형 간격 변형
  - 음수 마진 가이드

#### 1.3 그림자/반경 확장
- 현재: 기본만 문서화
- 추가 필요:
  - 그림자 변형 (hover, focus, active)
  - 반경 변형 (sm, md, lg, xl, full)
  - 그림자 애니메이션

### 2. 기본 UI 컴포넌트 - 추가/수정 필요

#### 2.1 아코디언 (Accordion) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 기본 아코디언 (`.accordion-section`)
  - 헤더/본문 구조
  - 토글 아이콘 (쉐브론)
  - 액션 버튼 영역 (`.accordion-actions`)
  - 카운트 표시 (`.accordion-count`)
  - 항목 추가 폼 (`.add-item-form`)
  - 카테고리 리스트 변형 (`.accordion-section--category`)
- 추가 문서화 필요:
  - 다중 열림 아코디언
  - 중첩 아코디언
  - 아이콘 아코디언
  - 접근성 (ARIA 속성)
  - 애니메이션 가이드

#### 2.2 탭 (Tabs) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 기본 탭 (`.tabs-nav`, `.tab-btn`)
  - 활성 상태 (`.active`)
  - 아이콘 탭
  - 스크롤 가능 탭 (모바일)
  - 탭 패널 (`.tab-panel`)
  - 페이드 인 애니메이션
  - 로딩 상태 (`.tab-loading`, `.tab-loading-spinner`)
  - 탭 액션 영역 (`.tab-actions`)
- 추가 문서화 필요:
  - 수직 탭
  - 닫기 가능 탭
  - 탭 전환 애니메이션
  - 접근성 (키보드 네비게이션)

#### 2.3 드롭다운 (Dropdown) - 추가 필요
- 현재: JavaScript 구현, CSS 미정의, 스타일가이드 없음
- 구현된 기능:
  - 기본 드롭다운 (`.dropdown`, `.dropdown-menu`)
  - 토글 버튼 (`[data-toggle="dropdown"]`)
  - 메뉴 아이템 (`.dropdown-item`)
  - 구분선 (`.dropdown-divider`)
  - 우측 정렬 (`.dropdown-menu-right`)
- 추가 필요:
  - 드롭다운 CSS 스타일 정의
  - 화살표 표시
  - 위치 변형 (top, bottom, left, right)
  - 접근성 (포커스 트랩, 키보드 네비게이션)

#### 2.4 페이지네이션 (Pagination) - 추가 필요
- 현재: 템플릿에서 사용, 스타일가이드 없음
- 구현된 기능:
  - 기본 페이지네이션 (`.pagination`)
  - 페이지 링크 (`.page-link`)
  - 활성 상태 (`.active`)
- 추가 필요:
  - 이전/다음 버튼
  - 첫/마지막 페이지 버튼
  - 점프 페이지네이션
  - 간단 페이지네이션
  - 반응형 페이지네이션

#### 2.5 브레드크럼 (Breadcrumb) - 추가 필요
- 현재: 없음
- 추가 필요:
  - 기본 브레드크럼
  - 아이콘 브레드크럼
  - 구분자 커스터마이징
  - 반응형 브레드크럼

#### 2.6 툴팁 (Tooltip) - 추가 필요
- 현재: 없음
- 추가 필요:
  - 기본 툴팁
  - 위치 변형 (top, bottom, left, right, auto)
  - 리치 툴팁 (HTML 콘텐츠)
  - 인터랙티브 툴팁
  - 접근성 (ARIA)

#### 2.7 프로그레스 (Progress) - 추가 필요
- 현재: 없음
- 추가 필요:
  - 선형 프로그레스 바
  - 원형 프로그레스
  - 단계별 프로그레스
  - 애니메이션 프로그레스
  - 색상 변형 (success, warning, error, info)

#### 2.8 스피너 (Spinner/Loader) - 추가 필요
- 현재: Font Awesome `fa-spinner fa-spin` 사용, 스타일가이드 없음
- 구현된 패턴:
  - 기본 스피너 (`.tab-loading-spinner`)
  - CSS 애니메이션 스피너
- 추가 필요:
  - 크기 변형 (sm, md, lg)
  - 색상 변형
  - 오버레이 스피너
  - 인라인 스피너
  - 버튼 내 스피너

### 3. 데이터 표시 컴포넌트 - 추가/수정 필요

#### 3.1 아바타 (Avatar) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 크기 변형 (xs: 32px, sm: 48px, md: 80px, lg: 120px, xl: 150px)
  - 이미지 아바타
  - 플레이스홀더 (이니셜, 아이콘)
  - 테마별 배경 (personal, corporate, employee, default)
  - 테두리 변형 (`.avatar--bordered`, `.avatar--bordered-white`)
  - 그룹 아바타 (`.avatar-group`)
  - 이미지 폴백 처리
- 추가 문서화 필요:
  - 상태 표시 (온라인/오프라인)
  - 배지 포함 아바타
  - 클릭 가능 아바타

#### 3.2 빈 상태 (Empty State) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 기본 빈 상태 (`.empty-state`)
  - 큰 빈 상태 (`.empty-state-large`)
  - 인라인 빈 상태 (`.empty-state-inline`, `.empty-cell`)
  - 테이블 빈 행 (`.empty-row`)
  - 아이콘, 제목, 설명, 액션 버튼
- 추가 문서화 필요:
  - 변형별 사용 가이드
  - 액션 버튼 조합
  - 반응형 동작

#### 3.3 상세 정보 (Details) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 상세 컨테이너 (`.detail-container`)
  - 상세 헤더 (`.detail-header`)
  - 상세 본문 (`.detail-body`)
  - 프로필 사진 (`.detail-photo`)
- 추가 문서화 필요:
  - 접이식 상세 정보
  - 테이블형 상세 정보
  - 반응형 레이아웃

#### 3.4 고급 데이터 테이블 (Data Table Advanced) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 테이블 컨테이너 및 툴바
  - 검색 기능 (`.data-table-search`)
  - 정렬 가능 헤더 (`.sort-btn`)
  - 컬럼 드래그 앤 드롭 (`.draggable`, `.drag-over`)
  - 행 선택 (`.selected`)
  - 체크박스 컬럼
  - 고정 헤더/푸터 (sticky)
  - 페이지네이션 (`.data-table-pagination`)
  - 컬럼 설정 팝오버 (`.column-settings-popover`)
  - 빈 상태 (`.data-table-empty`)
  - 로딩 상태 (`.data-table-loading`)
- 추가 문서화 필요:
  - 필터 기능 가이드
  - 확장 가능 행
  - 편집 가능 셀
  - 반응형 동작

#### 3.5 정보 그리드 (Info Grid) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 기본 2열 그리드 (`.info-grid`)
  - 자동 맞춤 그리드 (`.info-grid--auto`)
  - 계약 정보 그리드 (`.contract-info-grid`)
  - 정보 아이템 (`.info-item`, `.info-group`)
  - 전체 너비 아이템 (`.info-group--full`)
  - 라벨/값 스타일
  - 값 변형 (`.info-value--highlight`, `.info-value--empty`)
- 추가 문서화 필요:
  - 3열/4열 그리드
  - 반응형 동작
  - 사용 가이드

#### 3.6 통계 카드 (Stats Cards) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 통계 행 (`.stats-row`)
  - 통계 그리드 (`.stats-grid`)
  - 통계 카드 (`.stat-card`)
  - 통계 아이템 (`.stat-item`)
  - 아이콘 변형 (색상별)
  - 값/라벨 스타일
- 추가 문서화 필요:
  - 트렌드 표시
  - 변화율 표시
  - 링크 포함 카드
  - 반응형 동작

#### 3.7 빠른 링크 (Quick Links) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 빠른 링크 그리드 (`.quick-links`)
  - 빠른 링크 아이템 (`.quick-link`)
  - 테마별 호버 효과 (corporate, personal)
  - 아이콘/텍스트 조합
- 추가 문서화 필요:
  - 3열/4열 그리드
  - 아이콘 변형
  - 반응형 동작

#### 3.8 필터 (Filter) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 필터 바 (`.filter-bar`)
  - 변형 (inline, compact, simple)
  - 검색 박스 (`.filter-search`)
  - 필터 셀렉트 (`.filter-select`)
  - 다중 선택 (`.filter-select--multi`)
  - 정렬 셀렉트 (`.filter-sort`)
  - 필터 버튼 (`.filter-submit`)
  - 필터 토글 (모바일, `.filter-toggle`)
  - 결과 카운트 (`.filter-result-count`)
  - 반응형 동작
  - 접근성 (고대비, 감소된 모션)
- 추가 문서화 필요:
  - 태그 필터
  - 날짜 범위 필터
  - 고급 필터 패널
  - 사용 가이드

#### 3.9 트리 셀렉터 (Tree Selector) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 모달 오버레이 (`.tree-selector-modal`)
  - 모달 컨텐츠 (`.tree-selector-content`)
  - 검색 기능 (`.tree-selector-search`)
  - 트리 구조 (`.tree-list`, `.tree-item`)
  - 토글 버튼 (`.tree-toggle`)
  - 타입별 아이콘 색상
  - 선택 상태 (`.selected`)
  - 조직 선택 입력 필드 (`.org-selector-input`)
- 추가 문서화 필요:
  - 체크박스 트리
  - 다중 선택 트리
  - 접근성

#### 3.10 알림 (Notification) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 알림 드롭다운 (`.notification-dropdown`)
  - 알림 버튼 (`.notification-btn`)
  - 알림 배지 (`.notification-badge`)
  - 알림 패널 (`.notification-panel`)
  - 알림 아이템 (`.notification-item`)
  - 읽지 않음 상태 (`.unread`)
  - 타입별 아이콘 색상
  - 빈 상태 (`.notification-empty`)
- 추가 문서화 필요:
  - 토스트 알림
  - 배너 알림
  - 실시간 업데이트
  - 접근성

### 4. 폼 컴포넌트 확장 - 추가/수정 필요

#### 4.1 이미지 업로드 (Image Upload) - 추가 필요
- 현재: CSS 구현 완료, 스타일가이드 없음
- 구현된 기능:
  - 이미지 미리보기 (`.image-preview`)
  - 크기 변형 (sm, md, lg)
  - 이미지 플레이스홀더 (`.image-placeholder`)
  - 업로드 섹션 레이아웃 (`.image-upload-section`)
  - 업로드 컨트롤 (`.image-upload-controls`)
  - 명함 미리보기 (`.card-preview`)
  - 가로형 명함 (`.card-preview--landscape`)
- 추가 문서화 필요:
  - 드래그 앤 드롭 업로드
  - 다중 이미지 업로드
  - 업로드 진행률
  - 이미지 편집 기능

#### 4.2 폼 요소 확장 - 수정 필요
- 현재: 기본 입력 필드만 문서화
- 추가 필요:
  - 체크박스 그룹 (인라인, 수직)
  - 라디오 버튼 그룹 (인라인, 수직, 버튼형, 카드형)
  - 스위치/토글 컴포넌트
  - 날짜 선택기 (Date Picker)
  - 시간 선택기 (Time Picker)
  - 슬라이더 (Range Slider)
  - 파일 업로드 (드래그 앤 드롭)
  - 리치 텍스트 에디터
  - 폼 검증 메시지 스타일
  - 필드 에러 상태
  - 도움말 텍스트
  - 필수 필드 표시

### 5. 기존 컴포넌트 수정 필요 사항

#### 5.1 버튼 (Buttons) - 수정 필요
- 현재: 기본 버튼만 문서화
- 추가 필요:
  - 로딩 버튼 상태 (스피너 포함)
  - 버튼 그룹 상세 가이드
  - Split 버튼
  - Floating Action Button (FAB)
  - 버튼 아이콘 위치 (left, right)
  - 버튼 비활성화 상태 상세화

#### 5.2 폼 (Forms) - 수정 필요
- 현재: 기본 입력 필드만 문서화
- 추가 필요:
  - 폼 검증 메시지 스타일
  - 필드 에러 상태 표시
  - 도움말 텍스트 스타일
  - 필수 필드 표시 가이드 보강
  - 폼 레이아웃 옵션 확장 (3열, 4열)
  - 인라인 폼
  - 수평 폼 레이아웃

#### 5.3 카드 (Cards) - 수정 필요
- 현재: 기본 카드만 문서화
- 추가 필요:
  - 카드 변형 (이미지 카드, 액션 카드, 호버 카드)
  - 카드 호버 효과 문서화
  - 카드 그리드 레이아웃 가이드
  - 카드 플레이스홀더 (`.placeholder-card`)
  - 카드 액션 영역 (`.card-actions`)

#### 5.4 테이블 (Tables) - 수정 필요
- 현재: 기본 테이블만 문서화
- 추가 필요:
  - 정렬 가능 테이블 헤더 스타일
  - 필터 가능 테이블 가이드
  - 확장 가능 행 (expandable rows)
  - 테이블 로딩 상태
  - 테이블 선택 (체크박스) 기능
  - 테이블 액션 (`.table-actions`)
  - 하이라이트 행 (`.highlight-row`)
  - 빈 테이블 상태 (`.table-empty`)

#### 5.5 모달 (Modals) - 수정 필요
- 현재: 기본 모달만 문서화
- 추가 필요:
  - 모달 크기 변형 상세화 (sm: 400px, md: 600px, lg: 800px, full: 90%)
  - 확인 모달 패턴 문서화
  - 폼 모달 패턴 추가
  - 중첩 모달 가이드 추가
  - 모달 애니메이션 가이드
  - 모달 오버레이 스타일
  - 모달 포커스 트랩

#### 5.6 배지/태그 (Badges) - 수정 필요
- 현재: 기본 배지만 문서화
- 추가 필요:
  - 배지 크기 변형 (sm, md, lg)
  - 배지 아이콘 포함 가이드
  - 배지 위치 (상단 우측 등) 가이드
  - 카운트 배지 (`.count-badge`)
  - 상태 배지 (`.status-badge`)
  - 태그 (`.tag`, `.tag-removable`)

#### 5.7 알림 (Alerts) - 수정 필요
- 현재: 기본 알림만 문서화
- 추가 필요:
  - 닫기 가능 알림
  - 액션 버튼 포함 알림
  - 배너 알림 스타일 추가
  - 인라인 알림 상세화 (`.inline-alert`)
  - 토스트 메시지 상세화
  - 알림 아이콘 스타일

#### 5.8 레이아웃 (Layouts) - 수정 필요
- 현재: 기본 레이아웃만 문서화
- 추가 필요:
  - 사이드바 상태 (접힘/펼침) 문서화
  - 반응형 동작 상세화
  - 그리드 시스템 유틸리티 클래스 문서화
  - 컨테이너 크기 변형 추가
  - 섹션 네비게이션 (`.section-nav`)
  - 우측 사이드바 (`.right-sidebar`)

### 6. 우선순위별 작업 계획 (세부)

#### 높은 우선순위 (즉시 필요)
1. 아코디언 컴포넌트 문서화 (구현 완료, 문서화만 필요)
2. 탭 컴포넌트 문서화 (구현 완료, 문서화만 필요)
3. 드롭다운 컴포넌트 CSS 정의 및 문서화 (JS만 구현)
4. 페이지네이션 컴포넌트 문서화 (사용 중, 문서화 필요)
5. 아바타 컴포넌트 문서화 (구현 완료, 문서화만 필요)
6. 빈 상태 컴포넌트 문서화 (구현 완료, 문서화만 필요)
7. 이미지 업로드 컴포넌트 문서화 (구현 완료, 문서화만 필요)
8. 페이지 헤더 컴포넌트 문서화 (구현 완료, 문서화만 필요)
9. 정보 그리드 컴포넌트 문서화 (구현 완료, 문서화만 필요)
10. 통계 카드 컴포넌트 문서화 (구현 완료, 문서화만 필요)
11. 필터 컴포넌트 문서화 (구현 완료, 문서화만 필요)
12. 알림/토스트 컴포넌트 보강 (구현 완료, 문서화 필요)

#### 중간 우선순위 (단기 필요)
1. 고급 데이터 테이블 컴포넌트 문서화 (구현 완료, 문서화만 필요)
2. 트리 셀렉터 컴포넌트 문서화 (구현 완료, 문서화만 필요)
3. 빠른 링크 컴포넌트 문서화 (구현 완료, 문서화만 필요)
4. 상세 정보 컴포넌트 문서화 (구현 완료, 문서화만 필요)
5. 스피너 컴포넌트 문서화 (사용 중, 문서화 필요)
6. 아이콘 시스템 문서화 (사용 중, 문서화 필요)
7. 폼 요소 확장 (체크박스 그룹, 라디오 그룹, 스위치, 날짜 선택기)

#### 낮은 우선순위 (장기 개선)
1. 브레드크럼 컴포넌트 추가
2. 툴팁 컴포넌트 추가
3. 프로그레스 컴포넌트 추가
4. 기존 컴포넌트 변형/상태 확장
5. 접근성 가이드 추가
6. 애니메이션 가이드 추가
7. 반응형 패턴 가이드 추가




----


BEM 전환을 단계별로 진행하는 방법을 정리합니다.

## BEM 전환 로드맵

### Phase 1: 현재 상태 문서화 (1-2일)

#### 1.1 현재 스타일가이드 업데이트
- 현재 사용 중인 모든 컴포넌트 스타일을 스타일가이드에 반영
- 하이픈 기반 네이밍 패턴 문서화
- 실제 코드와 100% 일치 확인

작업 내용:
```
1. 모든 컴포넌트 템플릿 확인
2. 실제 CSS 클래스명 수집
3. 스타일가이드 문서 업데이트
4. 현재 네이밍 패턴 정리
```

#### 1.2 현재 네이밍 패턴 분석
- 컴포넌트별 클래스명 목록 작성
- 사용 빈도 분석
- 영향 범위 파악

### Phase 2: BEM 표준 확정 (2-3일)

#### 2.1 BEM 네이밍 규칙 정의
스타일가이드에 BEM 표준 문서 작성:

```markdown
## BEM 네이밍 컨벤션

### 규칙
- Block: 독립적인 컴포넌트 (예: `.btn`, `.card`)
- Element: 블록의 구성 요소 (예: `.btn__icon`, `.card__header`)
- Modifier: 상태나 변형 (예: `.btn--primary`, `.card--featured`)

### 네이밍 규칙
- Block: 단일 단어 또는 하이픈으로 구분된 단어
- Element: `Block__element` (언더바 2개)
- Modifier: `Block--modifier` 또는 `Block__element--modifier` (하이픈 2개)
```

#### 2.2 컴포넌트별 BEM 매핑표 작성

예시:

| 현재 클래스 | BEM 클래스 | 타입 | 설명 |
|------------|-----------|------|------|
| `.btn` | `.btn` | Block | 버튼 블록 |
| `.btn-primary` | `.btn--primary` | Modifier | Primary 변형 |
| `.btn-sm` | `.btn--sm` | Modifier | 작은 크기 |
| `.btn-icon` | `.btn__icon` | Element | 아이콘 요소 |
| `.card` | `.card` | Block | 카드 블록 |
| `.card-header` | `.card__header` | Element | 헤더 요소 |
| `.card-body` | `.card__body` | Element | 본문 요소 |
| `.card-title` | `.card__title` | Element | 제목 요소 |
| `.form-group` | `.form__group` | Element | 그룹 요소 |
| `.form-label` | `.form__label` | Element | 라벨 요소 |
| `.form-input` | `.form__input` | Element | 입력 요소 |

#### 2.3 스타일가이드에 BEM 예시 추가
각 컴포넌트 섹션에 BEM 버전 예시 추가:

```html
<!-- 현재 방식 (하이픈) -->
<button class="btn btn-primary">Primary</button>

<!-- BEM 방식 (표준) -->
<button class="btn btn--primary">Primary</button>
```

### Phase 3: 마이그레이션 전략 수립 (1-2일)

#### 3.1 전환 전략 선택

방안 A: 전체 일괄 전환 (권장하지 않음)
- 장점: 일관성 확보
- 단점: 대규모 변경, 리스크 큼, 테스트 부담

방안 B: 점진적 전환 (권장)
- 신규 컴포넌트: BEM 사용
- 기존 컴포넌트: 단계적 전환
- 우선순위별 전환

방안 C: 하이브리드 (현실적)
- 복잡한 컴포넌트: BEM 사용
- 단순한 컴포넌트: 하이픈 유지
- 명확한 가이드라인

#### 3.2 전환 우선순위 설정

높은 우선순위 (즉시 전환):
- 공유 컴포넌트 (버튼, 카드, 폼, 모달)
- 자주 사용되는 컴포넌트
- 스타일가이드에 문서화된 컴포넌트

중간 우선순위 (단계적 전환):
- 도메인별 컴포넌트
- 덜 자주 사용되는 컴포넌트

낮은 우선순위 (유지 또는 점진적 전환):
- 레거시 컴포넌트
- 곧 제거 예정인 컴포넌트

### Phase 4: 리팩토링 실행 (단계별)

#### 4.1 준비 작업

1. 마이그레이션 스크립트 작성
```javascript
// 마이그레이션 매핑 테이블
const BEM_MAPPING = {
  // 버튼
  'btn-primary': 'btn--primary',
  'btn-secondary': 'btn--secondary',
  'btn-sm': 'btn--sm',
  'btn-icon': 'btn__icon',
  
  // 카드
  'card-header': 'card__header',
  'card-body': 'card__body',
  'card-title': 'card__title',
  
  // 폼
  'form-group': 'form__group',
  'form-label': 'form__label',
  'form-input': 'form__input',
  
  // ... 모든 매핑
};
```

2. 검색/교체 도구 준비
- 정규식 패턴 작성
- 일괄 교체 스크립트
- 백업 계획

#### 4.2 단계별 전환 프로세스

Step 1: CSS 파일 전환
```bash
# 1. CSS 파일에서 클래스명 변경
# 예: button.css
.btn-primary { } → .btn--primary { }
.btn-icon { } → .btn__icon { }
```

Step 2: 템플릿 파일 전환
```bash
# 2. HTML 템플릿에서 클래스명 변경
# 예: templates/components/button.html
class="btn btn-primary" → class="btn btn--primary"
```

Step 3: JavaScript 파일 전환
```bash
# 3. JavaScript에서 클래스명 참조 변경
# 예: querySelector, classList 등
document.querySelector('.btn-primary') 
→ document.querySelector('.btn--primary')
```

Step 4: 테스트
- 각 단계마다 테스트 실행
- 시각적 회귀 테스트
- 기능 테스트

#### 4.3 컴포넌트별 전환 순서

1단계: 버튼 컴포넌트
```
1. CSS: button.css 수정
2. 템플릿: 모든 템플릿에서 btn-* 검색/교체
3. JavaScript: btn-* 참조 수정
4. 테스트: 버튼 기능 확인
```

2단계: 카드 컴포넌트
```
1. CSS: card.css 수정
2. 템플릿: card-* 검색/교체
3. JavaScript: card-* 참조 수정
4. 테스트: 카드 레이아웃 확인
```

3단계: 폼 컴포넌트
```
1. CSS: forms.css 수정
2. 템플릿: form-* 검색/교체
3. JavaScript: form-* 참조 수정
4. 테스트: 폼 기능 확인
```

### Phase 5: 검증 및 문서화 (1-2일)

#### 5.1 검증 체크리스트
- [ ] 모든 CSS 클래스명 BEM 규칙 준수
- [ ] 템플릿에서 하이픈 기반 클래스 제거 확인
- [ ] JavaScript에서 하이픈 기반 클래스 참조 제거 확인
- [ ] 스타일가이드 문서 BEM 예시로 업데이트
- [ ] 모든 컴포넌트 시각적 테스트 통과
- [ ] 기능 테스트 통과

#### 5.2 문서화
- 마이그레이션 가이드 작성
- BEM 네이밍 규칙 문서화
- 개발자 가이드 업데이트

## 구체적인 실행 방법

### 방법 1: 수동 전환 (소규모 프로젝트)

1. 컴포넌트별로 순차 전환
2. 각 컴포넌트마다 CSS → 템플릿 → JS 순서
3. 단계별 커밋
4. 테스트 후 다음 컴포넌트 진행

### 방법 2: 자동화 스크립트 (대규모 프로젝트)

```python
# 마이그레이션 스크립트 예시
import re
import os
from pathlib import Path

# BEM 매핑 테이블
BEM_MAPPING = {
    'btn-primary': 'btn--primary',
    'btn-secondary': 'btn--secondary',
    'card-header': 'card__header',
    'card-body': 'card__body',
    # ... 모든 매핑
}

def migrate_file(file_path):
    """파일 내 클래스명을 BEM으로 변경"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 각 매핑에 대해 교체
    for old, new in BEM_MAPPING.items():
        # CSS 클래스 선택자
        content = re.sub(rf'\.{old}\b', f'.{new}', content)
        # HTML class 속성
        content = re.sub(rf'class="([^"]*\s)?{old}(\s[^"]*)?', 
                        lambda m: m.group(0).replace(old, new), content)
        # JavaScript 문자열
        content = re.sub(rf'[\'"]{old}[\'"]', f'"{new}"', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 실행
for file_path in Path('app').rglob('*.{css,html,js}'):
    migrate_file(file_path)
```

### 방법 3: 점진적 전환 (권장)

1. 신규 컴포넌트부터 BEM 적용
2. 기존 컴포넌트는 사용 빈도 순으로 전환
3. 각 전환마다 독립적으로 테스트
4. 레거시 컴포넌트는 유지 또는 제거 시 전환

## 실행 체크리스트

### 준비 단계
- [ ] 현재 스타일가이드 업데이트 (현재 상태 반영)
- [ ] BEM 표준 문서 작성
- [ ] 컴포넌트별 매핑표 작성
- [ ] 전환 전략 수립
- [ ] 우선순위 설정

### 실행 단계
- [ ] 마이그레이션 스크립트 작성 (선택)
- [ ] 버전 관리 브랜치 생성
- [ ] 첫 번째 컴포넌트 전환 (버튼)
- [ ] 테스트 및 검증
- [ ] 다음 컴포넌트 전환
- [ ] 반복

### 완료 단계
- [ ] 모든 컴포넌트 전환 완료
- [ ] 스타일가이드 BEM 예시로 업데이트
- [ ] 개발자 가이드 업데이트
- [ ] 코드 리뷰 및 검증
- [ ] 배포

## 주의사항

1. 백업 필수
   - 전환 전 전체 코드 백업
   - Git 브랜치로 작업

2. 단계별 커밋
   - 컴포넌트별로 커밋
   - 롤백 가능하도록

3. 테스트 강화
   - 각 단계마다 테스트
   - 시각적 회귀 테스트
   - 자동화 테스트 실행

4. 팀 협의
   - 전환 전 팀 논의
   - 일정 조율
   - 리뷰 프로세스 확정

## 권장 접근법

현실적인 접근:
1. 현재 스타일가이드 업데이트 (현재 상태 반영)
2. BEM 표준 문서화 (참고용)
3. 신규 컴포넌트만 BEM 사용
4. 기존 컴포넌트는 점진적 전환 또는 유지

이 방법이 리스크가 낮고 실용적입니다.
