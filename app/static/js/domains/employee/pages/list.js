/**
 * Employee List Page JavaScript
 * - 뷰 토글 (목록형/카드형)
 * - 정렬
 * - 계약 요청 (21번 원칙)
 *
 * 필터링: FilterBar (filter-bar.js) + URL 모드로 처리
 * Last Updated: 2026-01-06 (Phase 31 필터 통합)
 */

document.addEventListener('DOMContentLoaded', () => {
    initViewToggle();
    initSorting();
    initEmployeeCardClick();
    initContractRequest();  // 21번 원칙: 계약 요청 기능
});

/**
 * 뷰 토글 초기화 (목록형/카드형)
 */
function initViewToggle() {
    const toggleButtons = document.querySelectorAll('.view-toggle-btn');

    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            toggleEmployeeView(view);
        });
    });
}

/**
 * 뷰 전환 처리
 * @param {string} view - 'list' 또는 'card'
 */
function toggleEmployeeView(view) {
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    const buttons = document.querySelectorAll('.view-toggle-btn');

    if (!listView || !cardView) return;

    buttons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });

    if (view === 'list') {
        listView.classList.remove('d-none');
        cardView.classList.add('d-none');
    } else {
        listView.classList.add('d-none');
        cardView.classList.remove('d-none');
    }

    // 사용자 선호 저장
    localStorage.setItem('employeeViewPreference', view);
}

/**
 * 정렬 초기화
 */
function initSorting() {
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', applySorting);
    }
}

/**
 * 정렬 적용
 */
function applySorting() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    const value = sortSelect.value;
    const url = new URL(window.location.href);

    if (!value) {
        url.searchParams.delete('sort');
        url.searchParams.delete('order');
    } else if (value.endsWith('-desc')) {
        url.searchParams.set('sort', value.replace('-desc', ''));
        url.searchParams.set('order', 'desc');
    } else {
        url.searchParams.set('sort', value);
        url.searchParams.delete('order');
    }

    window.location.href = url.toString();
}

/**
 * 직원 카드 클릭 이벤트 초기화
 */
function initEmployeeCardClick() {
    const cards = document.querySelectorAll('.employee-card[data-href]');

    cards.forEach(card => {
        card.addEventListener('click', (e) => {
            // 내부 액션 버튼 클릭 시 이벤트 전파 방지
            if (e.target.closest('.employee-actions')) return;

            const href = card.dataset.href;
            if (href) {
                window.location.href = href;
            }
        });
    });
}

/**
 * 21번 원칙: 계약 요청 버튼 초기화
 */
function initContractRequest() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-contract-request');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const userId = btn.dataset.userId;
        const employeeName = btn.dataset.employeeName;

        if (userId) {
            requestEmployeeContract(userId, employeeName, btn);
        }
    });
}

/**
 * 직원에게 계약 요청
 * @param {string} userId - 직원 User ID
 * @param {string} employeeName - 직원 이름
 * @param {HTMLElement} btn - 클릭된 버튼 요소
 */
async function requestEmployeeContract(userId, employeeName, btn) {
    const confirmMsg = employeeName
        ? `${employeeName} 직원에게 계약을 요청하시겠습니까?`
        : '해당 직원에게 계약을 요청하시겠습니까?';

    if (!confirm(confirmMsg)) {
        return;
    }

    // 버튼 비활성화 및 로딩 상태
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        // CSRF 토큰 가져오기
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

        const headers = {
            'Content-Type': 'application/json',
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        const response = await fetch(`/contracts/api/employee/${userId}/request`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                contract_type: 'employment'
            })
        });

        const data = await response.json();

        if (data.success) {
            showContractToast('계약 요청이 전송되었습니다.', 'success');
            // 버튼을 대기중 배지로 교체
            btn.outerHTML = '<span class="badge badge-warning">대기중</span>';
        } else {
            showContractToast(data.error || '계약 요청에 실패했습니다.', 'error');
            // 버튼 복원
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    } catch (error) {
        console.error('Contract request error:', error);
        showContractToast('계약 요청 중 오류가 발생했습니다.', 'error');
        // 버튼 복원
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
}

/**
 * 토스트 메시지 표시
 * @param {string} message - 메시지
 * @param {string} type - 'success' | 'error' | 'info'
 */
function showContractToast(message, type = 'info') {
    // 기존 토스트 함수가 있으면 사용
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
        return;
    }

    // 간단한 알림 fallback
    if (type === 'success') {
        alert(message);
    } else if (type === 'error') {
        alert('오류: ' + message);
    } else {
        alert(message);
    }
}

// 전역 함수로 노출 (기존 onclick 호환성 유지)
window.toggleEmployeeView = toggleEmployeeView;
window.applySorting = applySorting;
window.requestEmployeeContract = requestEmployeeContract;
