/**
 * button-loading.js - 버튼 로딩 상태 관리 컴포넌트
 * SSOT: 버튼 로딩/비활성화 패턴 중앙화
 *
 * 사용법:
 * import { setButtonLoading, setButtonDisabled } from '../components/button-loading.js';
 *
 * // 로딩 상태 설정
 * setButtonLoading(btn, true, '저장 중...', '저장', 'fa-save');
 *
 * // 완료 후 복원
 * setButtonLoading(btn, false, '저장 중...', '저장', 'fa-save');
 */

/**
 * 버튼 로딩 상태 설정
 * @param {HTMLButtonElement} btn - 대상 버튼 요소
 * @param {boolean} isLoading - 로딩 상태 여부
 * @param {string} loadingText - 로딩 중 표시할 텍스트
 * @param {string} defaultText - 기본 버튼 텍스트
 * @param {string} icon - 아이콘 클래스 (FontAwesome, fa- 접두사)
 */
export function setButtonLoading(btn, isLoading, loadingText = '처리 중...', defaultText = '버튼', icon = 'fa-download') {
    if (!btn) return;

    btn.disabled = isLoading;

    if (isLoading) {
        // 현재 상태 저장 (복원용)
        if (!btn.dataset.originalHtml) {
            btn.dataset.originalHtml = btn.innerHTML;
        }
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> <span>${loadingText}</span>`;
    } else {
        // 저장된 원본 HTML이 있으면 복원, 없으면 기본값 사용
        if (btn.dataset.originalHtml) {
            btn.innerHTML = btn.dataset.originalHtml;
            delete btn.dataset.originalHtml;
        } else {
            btn.innerHTML = `<i class="fas ${icon}"></i> <span>${defaultText}</span>`;
        }
    }
}

/**
 * 버튼 비활성화 상태만 설정 (HTML 변경 없음)
 * @param {HTMLButtonElement} btn - 대상 버튼 요소
 * @param {boolean} isDisabled - 비활성화 여부
 */
export function setButtonDisabled(btn, isDisabled) {
    if (!btn) return;
    btn.disabled = isDisabled;
}

/**
 * 여러 버튼의 로딩 상태 일괄 설정
 * @param {HTMLButtonElement[]} buttons - 버튼 요소 배열
 * @param {boolean} isLoading - 로딩 상태 여부
 */
export function setButtonsLoading(buttons, isLoading) {
    buttons.forEach(btn => {
        if (btn) {
            btn.disabled = isLoading;
        }
    });
}

// 전역 함수로 노출 (비모듈 환경 호환)
if (typeof window !== 'undefined') {
    window.HRButtonLoading = {
        setButtonLoading,
        setButtonDisabled,
        setButtonsLoading
    };

    // 기존 전역 함수 호환성 유지
    window.setButtonLoading = setButtonLoading;
}
