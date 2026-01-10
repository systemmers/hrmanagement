/**
 * 페이지네이션 유틸리티
 * - 기존 URL 파라미터 유지
 * - per_page 변경 시 page=1로 초기화
 */

/**
 * 페이지당 표시 수 변경 시 URL 업데이트
 * @param {number|string} value - 새로운 per_page 값
 */
function updatePerPage(value) {
    const url = new URL(window.location.href);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1'); // 페이지 초기화
    window.location.href = url.toString();
}

// 전역 스코프에 등록 (인라인 이벤트 핸들러용)
window.updatePerPage = updatePerPage;
