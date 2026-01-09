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
        ]
    },
    'components': {
        'label': 'Components',
        'description': '재사용 가능한 UI 컴포넌트',
        'items': [
            {'id': 'buttons', 'label': '버튼', 'icon': 'fa-hand-pointer', 'description': '버튼 스타일 및 상태'},
            {'id': 'forms', 'label': '폼', 'icon': 'fa-edit', 'description': '입력 필드 및 폼 요소'},
            {'id': 'cards', 'label': '카드', 'icon': 'fa-id-card', 'description': '카드 레이아웃'},
            {'id': 'tables', 'label': '테이블', 'icon': 'fa-table', 'description': '데이터 테이블'},
            {'id': 'modals', 'label': '모달', 'icon': 'fa-window-maximize', 'description': '모달 대화상자'},
            {'id': 'badges', 'label': '배지/태그', 'icon': 'fa-tag', 'description': '상태 배지 및 태그'},
            {'id': 'alerts', 'label': '알림', 'icon': 'fa-bell', 'description': '알림 및 토스트'},
            {'id': 'layouts', 'label': '레이아웃', 'icon': 'fa-columns', 'description': '페이지 레이아웃 및 반응형'},
        ]
    }
}

# 스타일가이드 메타데이터
STYLEGUIDE_META = {
    'title': 'HR Management 스타일가이드',
    'description': '인사카드 관리 시스템의 UI 컴포넌트 및 디자인 시스템 문서',
    'version': '1.0.0',
}
