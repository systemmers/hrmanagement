"""
Styleguide Configuration
네비게이션 구조 및 설정
"""

NAVIGATION = {
    'foundation': {
        'label': 'Foundation',
        'description': '디자인 시스템의 기초 요소',
        'items': [
            {'id': 'colors', 'label': '색상', 'icon': 'fa-palette', 'description': '색상 팔레트 및 시맨틱 색상'},
            {'id': 'typography', 'label': '타이포그래피', 'icon': 'fa-font', 'description': '폰트 크기 및 스타일'},
            {'id': 'spacing', 'label': '간격', 'icon': 'fa-arrows-alt', 'description': '간격 시스템'},
            {'id': 'shadows', 'label': '그림자/반경', 'icon': 'fa-clone', 'description': '그림자 및 모서리 반경'},
            {'id': 'icons', 'label': '아이콘', 'icon': 'fa-icons', 'description': 'FontAwesome 아이콘 시스템'},
        ]
    },
    'components': {
        'label': 'Components',
        'description': '재사용 가능한 UI 컴포넌트',
        'items': [
            # 기존 컴포넌트 (8개)
            {'id': 'buttons', 'label': '버튼', 'icon': 'fa-hand-pointer', 'description': '버튼 스타일 및 상태'},
            {'id': 'forms', 'label': '폼', 'icon': 'fa-edit', 'description': '입력 필드 및 폼 요소'},
            {'id': 'cards', 'label': '카드', 'icon': 'fa-id-card', 'description': '카드 레이아웃'},
            {'id': 'tables', 'label': '테이블', 'icon': 'fa-table', 'description': '데이터 테이블'},
            {'id': 'modals', 'label': '모달', 'icon': 'fa-window-maximize', 'description': '모달 대화상자'},
            {'id': 'badges', 'label': '배지/태그', 'icon': 'fa-tag', 'description': '상태 배지 및 태그'},
            {'id': 'alerts', 'label': '알림', 'icon': 'fa-bell', 'description': '알림 및 토스트'},
            {'id': 'layouts', 'label': '레이아웃', 'icon': 'fa-columns', 'description': '페이지 레이아웃 및 반응형'},
            # 1순위 - 핵심 UI (4개)
            {'id': 'avatar', 'label': '아바타', 'icon': 'fa-user-circle', 'description': '프로필 아바타'},
            {'id': 'empty-state', 'label': '빈 상태', 'icon': 'fa-inbox', 'description': '데이터 없음 표시'},
            {'id': 'page-header', 'label': '페이지 헤더', 'icon': 'fa-heading', 'description': '페이지 제목 영역'},
            {'id': 'info-grid', 'label': '정보 그리드', 'icon': 'fa-th', 'description': '정보 항목 그리드'},
            # 2순위 - 인터랙티브 (4개)
            {'id': 'accordion', 'label': '아코디언', 'icon': 'fa-bars', 'description': '접기/펼치기 섹션'},
            {'id': 'tabs', 'label': '탭', 'icon': 'fa-folder', 'description': '탭 네비게이션'},
            {'id': 'filter', 'label': '필터', 'icon': 'fa-filter', 'description': '검색 및 필터 바'},
            {'id': 'notification', 'label': '알림 드롭다운', 'icon': 'fa-bell-slash', 'description': '헤더 알림'},
            # 3순위 - 대시보드/복합 (5개)
            {'id': 'stats-cards', 'label': '통계 카드', 'icon': 'fa-chart-bar', 'description': '대시보드 통계'},
            {'id': 'quick-links', 'label': '바로가기', 'icon': 'fa-external-link-alt', 'description': '빠른 링크'},
            {'id': 'image-upload', 'label': '이미지 업로드', 'icon': 'fa-image', 'description': '사진 업로드'},
            {'id': 'tree-selector', 'label': '트리 선택', 'icon': 'fa-sitemap', 'description': '조직 트리 선택'},
            {'id': 'data-table-advanced', 'label': '고급 테이블', 'icon': 'fa-table', 'description': '고급 데이터 테이블'},
            # 4순위 - 도메인 특화 컴포넌트 (4개)
            {'id': 'profile-header', 'label': '프로필 헤더', 'icon': 'fa-user-tie', 'description': '계정별 통합 헤더 카드'},
            {'id': 'employee-card', 'label': '직원 카드', 'icon': 'fa-address-card', 'description': '직원 카드형 표시'},
            {'id': 'business-card', 'label': '명함', 'icon': 'fa-id-card-alt', 'description': '3D 플립 명함 카드'},
            {'id': 'attachment', 'label': '첨부서류', 'icon': 'fa-paperclip', 'description': '파일 업로드 및 목록'},
            # 5순위 - HR Card 마이그레이션 컴포넌트 (4개) - info-section, info-table은 cards.html로 병합
            {'id': 'inline-edit', 'label': '인라인 편집', 'icon': 'fa-pencil-alt', 'description': '인라인 편집 모드'},
            {'id': 'sub-nav', 'label': '서브 네비게이션', 'icon': 'fa-list-ul', 'description': '확장/축소 섹션 네비게이션'},
            {'id': 'sidebar-search', 'label': '사이드바 검색', 'icon': 'fa-search', 'description': '사이드바 내 검색'},
            {'id': 'mobile-nav', 'label': '모바일 네비게이션', 'icon': 'fa-mobile-alt', 'description': '모바일 하단 탭'},
        ]
    }
}

# 스타일가이드 메타데이터
STYLEGUIDE_META = {
    'title': 'HR Management 스타일가이드',
    'description': '인사카드 관리 시스템의 UI 컴포넌트 및 디자인 시스템 문서',
    'version': '1.0.0',
}
