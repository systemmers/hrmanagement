/**
 * Employee List Page JavaScript
 * - 뷰 토글 (목록형/카드형)
 * - 필터링
 * - 정렬
 */

document.addEventListener('DOMContentLoaded', () => {
    initViewToggle();
    initFilterReset();
    initFilterRemove();
    initSorting();
    initEmployeeCardClick();
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
 * 필터 초기화 버튼 설정
 */
function initFilterReset() {
    const resetBtn = document.querySelector('.filter-reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }
}

/**
 * 필터 초기화
 */
function resetFilters() {
    window.location.href = window.location.pathname;
}

/**
 * 필터 제거 버튼 설정
 */
function initFilterRemove() {
    const activeFilters = document.getElementById('active-filters');
    if (!activeFilters) return;

    activeFilters.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        const tag = btn.closest('.filter-tag');
        if (!tag) return;

        // 버튼의 onclick에서 파라미터 추출
        const onclickAttr = btn.getAttribute('onclick');
        if (onclickAttr) {
            const match = onclickAttr.match(/removeFilter\('([^']+)',\s*'([^']+)'\)/);
            if (match) {
                removeFilter(match[1], match[2]);
            }
        }
    });
}

/**
 * 특정 필터 제거
 * @param {string} filterType - 필터 종류 (department, position, status)
 * @param {string} value - 제거할 값
 */
function removeFilter(filterType, value) {
    const url = new URL(window.location.href);
    const params = url.searchParams;
    const values = params.getAll(filterType);

    params.delete(filterType);
    values.filter(v => v !== value).forEach(v => params.append(filterType, v));

    window.location.href = url.toString();
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

// 전역 함수로 노출 (기존 onclick 호환성 유지)
window.toggleEmployeeView = toggleEmployeeView;
window.resetFilters = resetFilters;
window.removeFilter = removeFilter;
window.applySorting = applySorting;
