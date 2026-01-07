/**
 * Avatar Fallback Module
 * 이미지 로드 실패 시 폴백 표시 (SSOT)
 *
 * 매크로 _avatar.html과 연동하여 동작:
 * - data-fallback-type: 'icon' | 'initial'
 * - data-fallback-theme: 'default' | 'personal' | 'corporate' | 'employee'
 * - data-fallback-initial: 이니셜 문자
 */

/**
 * 아바타 폴백 초기화
 * 이미지 로드 실패 시 폴백 요소를 표시
 */
export function initAvatarFallback() {
    // 이벤트 위임으로 이미지 에러 캡처 (버블링되지 않으므로 capture 사용)
    document.addEventListener('error', handleImageError, true);

    // 이미 로드 완료된 이미지 중 실패한 것 처리
    document.querySelectorAll('.avatar__image').forEach(img => {
        if (img.complete && img.naturalWidth === 0) {
            showFallback(img);
        }
    });
}

/**
 * 이미지 에러 핸들러
 * @param {Event} e - 에러 이벤트
 */
function handleImageError(e) {
    if (!e.target.matches('.avatar__image')) return;
    showFallback(e.target);
}

/**
 * 폴백 표시
 * @param {HTMLImageElement} img - 실패한 이미지 요소
 */
function showFallback(img) {
    // 이미지 숨기기
    img.classList.add('avatar__image--error');

    // 폴백 요소 찾기
    const avatar = img.closest('.avatar');
    if (!avatar) return;

    const fallback = avatar.querySelector('.avatar-fallback');
    if (!fallback) return;

    // 폴백 표시
    fallback.classList.remove('avatar-fallback--hidden');
    fallback.classList.add('avatar-fallback--visible');
}

export default {
    initAvatarFallback
};
