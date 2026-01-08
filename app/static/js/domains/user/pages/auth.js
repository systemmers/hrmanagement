/**
 * auth.js - 인증 페이지 공통 스크립트
 * - 비밀번호 토글 기능
 */

/**
 * 비밀번호 표시/숨김 토글
 * @param {HTMLElement} button - 토글 버튼 요소
 */
function togglePassword(button) {
    const wrapper = button.closest('.auth-form__password-wrapper');
    if (!wrapper) return;

    const passwordInput = wrapper.querySelector('input[type="password"], input[type="text"]');
    const toggleIcon = button.querySelector('i');

    if (!passwordInput || !toggleIcon) return;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// 이벤트 위임 - data-action 기반 클릭 핸들러
document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-action]');
    if (!target) return;

    const action = target.dataset.action;

    switch (action) {
        case 'toggle-password':
            togglePassword(target);
            break;
    }
});
