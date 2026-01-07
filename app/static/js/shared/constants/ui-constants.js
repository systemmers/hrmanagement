/**
 * UI 관련 상수 (SSOT)
 * 레이블, 상태 텍스트 등 UI에 표시되는 텍스트 상수
 */

/**
 * 감사 로그 액션 레이블
 * @type {Object}
 */
export const AUDIT_ACTION_LABELS = {
    'view': '조회',
    'create': '생성',
    'update': '수정',
    'delete': '삭제',
    'login': '로그인',
    'logout': '로그아웃',
    'export': '내보내기',
    'import': '가져오기',
    'approve': '승인',
    'reject': '반려'
};

/**
 * 감사 로그 상태 레이블
 * @type {Object}
 */
export const AUDIT_STATUS_LABELS = {
    'success': '성공',
    'failed': '실패',
    'pending': '대기'
};

/**
 * 조직 유형 레이블
 * @type {Object}
 */
export const ORG_TYPE_LABELS = {
    'company': '회사',
    'division': '본부',
    'department': '부서',
    'team': '팀'
};

/**
 * 법인 문서 유형 레이블
 * @type {Object}
 */
export const CORPORATE_DOCUMENT_TYPE_LABELS = {
    'business_registration': '사업자등록증',
    'corporate_seal': '법인인감증명',
    'certificate_of_incorporation': '법인등기부등본',
    'financial_statement': '재무제표',
    'tax_payment': '납세증명',
    'other': '기타'
};

/**
 * 계약 상태 레이블
 * @type {Object}
 */
export const CONTRACT_STATUS_LABELS = {
    'active': '활성',
    'approved': '승인됨',
    'pending': '대기중',
    'terminated': '종료',
    'expired': '만료',
    'draft': '초안'
};

/**
 * 계약 유형 레이블
 * @type {Object}
 */
export const CONTRACT_TYPE_LABELS = {
    'employment': '정규직',
    'contract': '계약직',
    'part_time': '파트타임',
    'internship': '인턴',
    'freelance': '프리랜서'
};

/**
 * 레이블 조회 헬퍼 함수
 * @param {Object} labels - 레이블 객체
 * @param {string} key - 조회할 키
 * @param {string} [fallback] - 키가 없을 경우 반환할 값 (기본: key 자체)
 * @returns {string}
 */
export function getLabel(labels, key, fallback = null) {
    return labels[key] || fallback || key;
}
