/**
 * Sidebar Search Component
 * 사이드바 직원 검색 기능
 *
 * Phase 04: HR Card Migration - Sidebar Search
 *
 * 검색 결과 처리 로직:
 * - 결과 0개: 토스트 메시지 표시
 * - 결과 1개: 바로 상세페이지 이동
 * - 결과 2개 이상: 모달로 선택 UI 표시
 */

import { debounce } from '../../../shared/utils/events.js';
import { showToast } from '../../../shared/components/toast.js';

/**
 * SidebarSearch 클래스
 */
export class SidebarSearch {
    /**
     * @param {Object} options - 설정 옵션
     */
    constructor(options = {}) {
        this.options = {
            containerSelector: options.containerSelector || '.sidebar-search',
            inputSelector: options.inputSelector || '.sidebar-search__input',
            clearBtnSelector: options.clearBtnSelector || '.sidebar-search__clear',
            searchBtnSelector: options.searchBtnSelector || '.sidebar-search__btn',
            modalId: options.modalId || 'searchResultModal',
            debounceDelay: options.debounceDelay || 300,
            minChars: options.minChars || 2,
            maxResults: options.maxResults || 10,
            apiUrl: options.apiUrl || '/api/employees',
            ...options
        };

        this.container = null;
        this.elements = {
            input: null,
            clearBtn: null,
            searchBtn: null,
            modal: null,
            modalBody: null
        };

        this.state = {
            query: '',
            results: [],
            isLoading: false
        };

        this.controller = null; // AbortController for fetch
        this.debouncedSearch = null;
    }

    /**
     * 초기화
     * @returns {SidebarSearch} 체이닝
     */
    init() {
        this.setupElements();

        if (!this.container) {
            console.warn('SidebarSearch: Container not found');
            return this;
        }

        this.setupModal();
        this.bindEvents();
        this.debouncedSearch = debounce(() => this.search(), this.options.debounceDelay);

        return this;
    }

    /**
     * DOM 요소 설정
     */
    setupElements() {
        this.container = document.querySelector(this.options.containerSelector);
        if (!this.container) return;

        this.elements.input = this.container.querySelector(this.options.inputSelector);
        this.elements.clearBtn = this.container.querySelector(this.options.clearBtnSelector);
        this.elements.searchBtn = this.container.querySelector(this.options.searchBtnSelector);
    }

    /**
     * 모달 설정
     */
    setupModal() {
        this.elements.modal = document.getElementById(this.options.modalId);

        if (!this.elements.modal) {
            this.createModal();
        }

        this.elements.modalBody = this.elements.modal?.querySelector('.modal__body');
    }

    /**
     * 모달 동적 생성
     */
    createModal() {
        const modal = document.createElement('div');
        modal.id = this.options.modalId;
        modal.className = 'modal';
        modal.setAttribute('aria-hidden', 'true');
        modal.innerHTML = `
            <div class="modal__backdrop"></div>
            <div class="modal__container modal__container--sm">
                <div class="modal__header">
                    <h3 class="modal__title">검색 결과</h3>
                    <button type="button" class="modal__close" data-modal-close>
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal__body">
                    <!-- 검색 결과가 여기에 렌더링됨 -->
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        this.elements.modal = modal;
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        if (!this.elements.input) return;

        // 입력 이벤트 (디바운스)
        this.elements.input.addEventListener('input', (e) => {
            this.state.query = e.target.value.trim();
            this.updateClearButton();

            if (this.state.query.length >= this.options.minChars) {
                this.debouncedSearch();
            }
        });

        // 엔터 키
        this.elements.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.search();
            } else if (e.key === 'Escape') {
                this.clear();
            }
        });

        // 검색 버튼 클릭
        if (this.elements.searchBtn) {
            this.elements.searchBtn.addEventListener('click', () => {
                this.search();
            });
        }

        // Clear 버튼 클릭
        if (this.elements.clearBtn) {
            this.elements.clearBtn.addEventListener('click', () => {
                this.clear();
            });
        }

        // 모달 이벤트
        if (this.elements.modal) {
            // 배경 클릭으로 닫기
            const backdrop = this.elements.modal.querySelector('.modal__backdrop');
            if (backdrop) {
                backdrop.addEventListener('click', () => this.closeModal());
            }

            // 닫기 버튼
            const closeBtn = this.elements.modal.querySelector('[data-modal-close]');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.closeModal());
            }

            // 결과 클릭 (이벤트 위임)
            this.elements.modal.addEventListener('click', (e) => {
                const item = e.target.closest('[data-employee-id]');
                if (item) {
                    this.handleResultClick(item);
                }
            });

            // ESC 키로 모달 닫기
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.elements.modal.classList.contains('show')) {
                    this.closeModal();
                }
            });
        }
    }

    /**
     * Clear 버튼 표시/숨김
     */
    updateClearButton() {
        if (this.state.query.length > 0) {
            this.container.classList.add('sidebar-search--has-value');
        } else {
            this.container.classList.remove('sidebar-search--has-value');
        }
    }

    /**
     * 검색 실행
     */
    async search() {
        const query = this.state.query;

        if (query.length < this.options.minChars) {
            showToast(`${this.options.minChars}글자 이상 입력해주세요`, 'info');
            return;
        }

        this.state.isLoading = true;

        // 이전 요청 취소
        if (this.controller) {
            this.controller.abort();
        }
        this.controller = new AbortController();

        try {
            const params = new URLSearchParams({
                search: query,
                limit: this.options.maxResults
            });

            const response = await fetch(`${this.options.apiUrl}?${params}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                signal: this.controller.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // API 응답: { success: true, data: { employees: [...] } }
            const responseData = data.data || data;
            const results = responseData.employees || responseData.results || responseData || [];

            this.handleSearchResult(results);

        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Search error:', error);
                showToast('검색 중 오류가 발생했습니다', 'error');
            }
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * 검색 결과 처리
     * @param {Array} results - 검색 결과 배열
     */
    handleSearchResult(results) {
        this.state.results = results;

        if (results.length === 0) {
            // 결과 없음
            showToast('검색 결과가 없습니다', 'info');
            return;
        }

        if (results.length === 1) {
            // 단일 결과: 바로 상세페이지 이동
            const employee = results[0];
            window.location.href = `/employees/${employee.id}`;
            return;
        }

        // 복수 결과: 모달로 선택 UI 표시
        this.renderResults(results);
        this.openModal();
    }

    /**
     * 결과 렌더링
     * @param {Array} results - 검색 결과 배열
     */
    renderResults(results) {
        if (!this.elements.modalBody) return;

        const html = `
            <div class="search-results">
                <p class="search-results__count">${results.length}명의 직원이 검색되었습니다</p>
                <ul class="search-results__list">
                    ${results.map(emp => this.renderResultItem(emp)).join('')}
                </ul>
            </div>
        `;

        this.elements.modalBody.innerHTML = html;
    }

    /**
     * 결과 아이템 렌더링
     * @param {Object} employee - 직원 데이터
     * @returns {string} HTML 문자열
     */
    renderResultItem(employee) {
        const photoUrl = employee.photo_url || '/static/images/default-avatar.png';
        const department = employee.department || employee.organization_name || '';
        const position = employee.position || employee.job_title || '';

        return `
            <li class="search-results__item" data-employee-id="${employee.id}">
                <div class="search-results__avatar">
                    <img src="${this.escapeHtml(photoUrl)}" alt="${this.escapeHtml(employee.name)}"
                         onerror="this.src='/static/images/default-avatar.png'">
                </div>
                <div class="search-results__info">
                    <div class="search-results__name">${this.escapeHtml(employee.name)}</div>
                    <div class="search-results__meta">
                        ${department ? `<span>${this.escapeHtml(department)}</span>` : ''}
                        ${position ? `<span>${this.escapeHtml(position)}</span>` : ''}
                    </div>
                </div>
                <div class="search-results__action">
                    <i class="fas fa-chevron-right"></i>
                </div>
            </li>
        `;
    }

    /**
     * 결과 클릭 처리
     * @param {Element} item - 클릭된 아이템 요소
     */
    handleResultClick(item) {
        const employeeId = item.dataset.employeeId;
        if (employeeId) {
            this.closeModal();
            window.location.href = `/employees/${employeeId}`;
        }
    }

    /**
     * 모달 열기
     */
    openModal() {
        if (!this.elements.modal) return;

        this.elements.modal.classList.add('show');
        this.elements.modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    /**
     * 모달 닫기
     */
    closeModal() {
        if (!this.elements.modal) return;

        this.elements.modal.classList.remove('show');
        this.elements.modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    /**
     * 검색 초기화
     */
    clear() {
        this.state.query = '';
        this.state.results = [];

        if (this.elements.input) {
            this.elements.input.value = '';
        }

        this.updateClearButton();

        // 이전 요청 취소
        if (this.controller) {
            this.controller.abort();
            this.controller = null;
        }
    }

    /**
     * HTML 이스케이프
     * @param {string} text - 원본 텍스트
     * @returns {string} 이스케이프된 텍스트
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 정리
     */
    destroy() {
        if (this.controller) {
            this.controller.abort();
        }

        // 동적 생성된 모달 제거
        if (this.elements.modal && this.elements.modal.id === this.options.modalId) {
            this.elements.modal.remove();
        }
    }
}

/**
 * 간편 초기화 함수
 * @param {Object} options - 설정 옵션
 * @returns {SidebarSearch} 인스턴스
 */
export function initSidebarSearch(options = {}) {
    const search = new SidebarSearch(options);
    return search.init();
}

// 자동 초기화 (DOMContentLoaded)
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.sidebar-search');
    if (container) {
        initSidebarSearch();
    }
});
