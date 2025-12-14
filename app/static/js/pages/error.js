/**
 * Error Page JavaScript
 * 에러 페이지 이벤트 핸들러
 *
 * Used by:
 * - base_error.html (errors/*.html)
 */

document.addEventListener('DOMContentLoaded', function() {
    initErrorPageActions();
});

/**
 * Initialize error page action handlers
 */
function initErrorPageActions() {
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'reload-page':
                window.location.reload();
                break;
            case 'go-back':
                window.history.back();
                break;
        }
    });
}
