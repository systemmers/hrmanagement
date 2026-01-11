/**
 * settings 모듈 공유 상수
 *
 * SSOT: 아이콘, 라벨 등 공유 상수 정의
 */

/**
 * 조직 유형별 아이콘 매핑
 */
export const ORG_TYPE_ICONS = {
    'company': 'fa-building',
    'division': 'fa-layer-group',
    'department': 'fa-users',
    'team': 'fa-user-friends',
    'headquarters': 'fa-building',
    'section': 'fa-user-friends',
    'office': 'fa-door-open',
    'part': 'fa-puzzle-piece'
};

/**
 * 아이콘 선택기에서 사용할 아이콘 목록
 */
export const ICON_PICKER_OPTIONS = [
    'fa-building', 'fa-layer-group', 'fa-users', 'fa-user-friends',
    'fa-sitemap', 'fa-door-open', 'fa-puzzle-piece', 'fa-folder',
    'fa-briefcase', 'fa-cog', 'fa-chart-line', 'fa-code-branch',
    'fa-cube', 'fa-cubes', 'fa-database', 'fa-globe',
    'fa-landmark', 'fa-network-wired', 'fa-project-diagram', 'fa-server'
];

/**
 * 감사 로그 액션 라벨
 */
export const AUDIT_ACTION_LABELS = {
    'view': '조회',
    'create': '생성',
    'update': '수정',
    'delete': '삭제',
    'export': '내보내기',
    'sync': '동기화',
    'login': '로그인',
    'logout': '로그아웃',
    'access_denied': '접근 거부'
};

/**
 * 감사 로그 상태 라벨
 */
export const AUDIT_STATUS_LABELS = {
    'success': '성공',
    'failure': '실패',
    'denied': '거부'
};

/**
 * 조직 유형 아이콘 반환
 * @param {string} orgType - 조직 유형
 * @returns {string} FontAwesome 아이콘 클래스
 */
export function getOrgTypeIcon(orgType) {
    return ORG_TYPE_ICONS[orgType] || 'fa-folder';
}
