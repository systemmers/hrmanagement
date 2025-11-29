/**
 * 인사카드 관리 시스템 - 메인 애플리케이션
 * ES6 모듈 기반 진입점
 */

import { Toast, showToast } from './components/toast.js';
import { FormValidator } from './components/form-validator.js';
import { Filter, applyFilters, resetFilters, removeFilter, toggleFilterBar } from './components/filter.js';
import { searchEmployees } from './services/employee-service.js';

// 전역 함수로 노출 (기존 코드 호환성)
window.showToast = showToast;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.removeFilter = removeFilter;
window.toggleFilterBar = toggleFilterBar;
window.searchEmployees = searchEmployees;

// 정렬 함수
window.applySorting = function() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    const value = sortSelect.value;
    const url = new URL(window.location.href);

    if (value) {
        // value 형식: "name" 또는 "name-desc"
        const parts = value.split('-');
        const sortField = parts[0];
        const sortOrder = parts[1] === 'desc' ? 'desc' : 'asc';

        url.searchParams.set('sort', sortField);
        url.searchParams.set('order', sortOrder);
    } else {
        url.searchParams.delete('sort');
        url.searchParams.delete('order');
    }

    window.location.href = url.toString();
};

// 로그아웃 함수
window.handleLogout = function() {
    if (confirm('로그아웃 하시겠습니까?')) {
        showToast('로그아웃되었습니다.');
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
};

// 직원 목록 뷰 전환 함수
window.toggleEmployeeView = function(viewType) {
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    const listBtn = document.querySelector('.view-toggle-btn[data-view="list"]');
    const cardBtn = document.querySelector('.view-toggle-btn[data-view="card"]');

    if (!listView || !cardView || !listBtn || !cardBtn) {
        return;
    }

    if (viewType === 'list') {
        listView.style.display = 'block';
        cardView.style.display = 'none';
        listBtn.classList.add('active');
        cardBtn.classList.remove('active');
    } else if (viewType === 'card') {
        listView.style.display = 'none';
        cardView.style.display = 'grid';
        listBtn.classList.remove('active');
        cardBtn.classList.add('active');
    }
};

// 페이지 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 헤더 검색 폼 제출 방지 (엔터 키 처리)
    const searchForm = document.querySelector('.header-search form');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            const input = searchForm.querySelector('input[name="q"]');
            if (!input.value.trim()) {
                e.preventDefault();
            }
        });
    }

    // 폼 유효성 검사 초기화
    new FormValidator();

    // 직원 목록 뷰 초기화
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    if (listView && cardView) {
        window.toggleEmployeeView('list');
    }

    // 필터 초기화
    const filterContext = document.body.dataset.pageContext || 'list';
    new Filter(filterContext);

    // 카드 클릭 이벤트 처리
    document.addEventListener('click', (e) => {
        const card = e.target.closest('.employee-card');
        if (card && !e.target.closest('.employee-actions')) {
            const employeeId = card.getAttribute('data-id');
            if (employeeId) {
                window.location.href = `/employees/${employeeId}`;
            }
        }
    });
});
