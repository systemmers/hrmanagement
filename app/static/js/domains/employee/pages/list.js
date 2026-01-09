/**
 * Employee List Page JavaScript
 * - 뷰 토글 (목록형/카드형/명함형)
 * - 정렬
 * - 계약 요청 (21번 원칙)
 *
 * 필터링: FilterBar (filter-bar.js) + URL 모드로 처리
 * 명함형 뷰: BusinessCard 도메인 모듈 사용
 * Last Updated: 2026-01-09 (BusinessCard 도메인 통합)
 */

// BusinessCard 도메인 모듈 import
import { initBusinessCardView, businessCard } from '../../businesscard/index.js';

document.addEventListener('DOMContentLoaded', () => {
    initViewToggle();
    initSorting();
    initEmployeeCardClick();
    initContractRequest();  // 21번 원칙: 계약 요청 기능
});

/**
 * 뷰 토글 초기화 (목록형/카드형)
 * - URL 파라미터 우선 (서버 측 렌더링과 동기화)
 * - URL 파라미터 없으면 localStorage 사용
 * - 서버 측 렌더링 신뢰: URL 파라미터 있으면 DOM 조작 건너뜀
 */
function initViewToggle() {
    const toggleButtons = document.querySelectorAll('.view-toggle-btn');

    // URL 파라미터에서 뷰모드 확인 (우선순위 1 - 서버 측과 동기화)
    const urlParams = new URLSearchParams(window.location.search);
    const urlView = urlParams.get('view');

    // URL 파라미터가 있으면 서버 측 렌더링을 신뢰하고 localStorage만 동기화
    if (urlView) {
        localStorage.setItem('employeeViewPreference', urlView);
        // 명함뷰인 경우 BusinessCard 초기화만 실행
        if (urlView === 'namecard') {
            initBusinessCards();
        }
    } else {
        // URL 파라미터 없으면 localStorage 기반으로 뷰 전환
        const savedView = localStorage.getItem('employeeViewPreference') || 'list';
        // 기본값(list)이 아닌 경우에만 뷰 전환 (서버 기본값과 다를 때)
        if (savedView !== 'list') {
            toggleEmployeeView(savedView, true);  // URL도 업데이트
        }
    }

    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            toggleEmployeeView(view, true);
        });
    });
}

/**
 * 뷰 전환 처리
 * @param {string} view - 'list', 'card', 또는 'namecard'
 * @param {boolean} updateUrl - URL 파라미터 업데이트 여부 (기본: true)
 */
function toggleEmployeeView(view, updateUrl = true) {
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    const namecardView = document.getElementById('namecard-view');
    const buttons = document.querySelectorAll('.view-toggle-btn');

    if (!listView || !cardView) return;

    buttons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });

    // 모든 뷰 숨기기
    listView.classList.add('d-none');
    cardView.classList.add('d-none');
    if (namecardView) namecardView.classList.add('d-none');

    // 선택된 뷰만 표시
    if (view === 'list') {
        listView.classList.remove('d-none');
    } else if (view === 'card') {
        cardView.classList.remove('d-none');
    } else if (view === 'namecard' && namecardView) {
        namecardView.classList.remove('d-none');
        // BusinessCard 도메인 모듈로 초기화 (최초 1회)
        initBusinessCards();
    }

    // 사용자 선호 저장
    localStorage.setItem('employeeViewPreference', view);

    // URL 파라미터 업데이트 (리로드 없이)
    if (updateUrl) {
        const url = new URL(window.location);
        url.searchParams.set('view', view);
        window.history.replaceState({}, '', url);
    }
}

/**
 * 명함형 뷰 초기화 (BusinessCard 도메인 모듈 사용)
 * - 명함 카드 컴포넌트 및 QR 코드 초기화
 */
let businessCardsInitialized = false;

function initBusinessCards() {
    // 이미 초기화된 경우 스킵
    if (businessCardsInitialized) return;

    // BusinessCard 도메인 모듈로 초기화
    const namecardView = document.getElementById('namecard-view');
    if (namecardView) {
        initBusinessCardView(namecardView);
    }

    businessCardsInitialized = true;
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
 * - 현재 뷰모드(view) 파라미터 유지
 */
function applySorting() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    const value = sortSelect.value;
    const url = new URL(window.location.href);

    // 현재 뷰모드 유지 (URL 또는 localStorage에서)
    const currentView = url.searchParams.get('view') || localStorage.getItem('employeeViewPreference');
    if (currentView) {
        url.searchParams.set('view', currentView);
    }

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
