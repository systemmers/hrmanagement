/**
 * ==========================================================
 * FilterBar Component (SSOT)
 * ==========================================================
 *
 * 통합 필터 바 컴포넌트
 * - 3가지 모드 지원: url, client, form
 * - data-* 속성 기반 자동 초기화
 * - 이벤트 시스템 제공
 * - 전역 함수 호환성 (기존 filter.js 대체)
 *
 * 사용처:
 * - employees/list.html (URL 모드)
 * - contracts/company_list.html (클라이언트 모드)
 * - platform/users/list.html (폼 모드)
 * - platform/companies/list.html (폼 모드)
 *
 * Last Updated: 2026-01-03
 * ==========================================================
 */

/**
 * FilterBar 클래스
 * @class
 */
export class FilterBar {
    /**
     * @param {HTMLElement} container - 필터 바 컨테이너 요소
     * @param {Object} options - 설정 옵션
     * @param {string} options.mode - 필터 모드 ('url' | 'client' | 'form')
     * @param {string} options.action - 폼 제출 URL (form 모드)
     * @param {string} options.targetSelector - 필터링 대상 선택자 (client 모드)
     * @param {Function} options.onFilter - 필터 적용 콜백
     * @param {Function} options.onReset - 필터 초기화 콜백
     */
    constructor(container, options = {}) {
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        if (!this.container) {
            console.warn('FilterBar: Container not found');
            return;
        }

        // 옵션 설정 (data-* 속성 우선)
        this.options = {
            mode: this.container.dataset.mode || options.mode || 'url',
            action: this.container.dataset.action || options.action || '',
            targetSelector: options.targetSelector || '[data-filter-target]',
            debounceDelay: options.debounceDelay || 300,
            ...options
        };

        // 상태
        this.filters = {};
        this.listeners = {};
        this.debounceTimer = null;

        // 요소 캐싱
        this.elements = {
            searchInput: this.container.querySelector('.filter-search__input'),
            selects: this.container.querySelectorAll('.filter-select'),
            checkboxes: this.container.querySelectorAll('.filter-checkbox'),
            resetBtn: this.container.querySelector('[data-action="reset"]'),
            submitBtn: this.container.querySelector('[data-action="submit"]'),
            activeFilters: document.querySelector('.active-filters')
        };

        this.init();
    }

    /**
     * 초기화
     */
    init() {
        this.bindEvents();
        this.loadFiltersFromUrl();
        this.emit('init', { filters: this.getFilters() });
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 검색 입력
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('input', () => {
                this.debounce(() => this.handleFilterChange());
            });

            this.elements.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.apply();
                }
            });
        }

        // 셀렉트 변경 - URL 모드에서 즉시 적용
        this.elements.selects.forEach(select => {
            select.addEventListener('change', () => {
                this.handleFilterChange();
                // URL 모드에서 셀렉트는 즉시 적용
                if (this.options.mode === 'url') {
                    this.apply();
                }
            });
        });

        // 체크박스 변경
        this.elements.checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.handleFilterChange();
            });
        });

        // 초기화 버튼
        if (this.elements.resetBtn) {
            this.elements.resetBtn.addEventListener('click', () => {
                this.reset();
            });
        }

        // 제출 버튼 (form 모드)
        if (this.elements.submitBtn) {
            this.elements.submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.apply();
            });
        }

        // 활성 필터 태그 제거
        if (this.elements.activeFilters) {
            this.elements.activeFilters.addEventListener('click', (e) => {
                const removeBtn = e.target.closest('[data-action="remove-filter"]');
                if (removeBtn) {
                    const tag = removeBtn.closest('.filter-tag');
                    if (tag) {
                        this.removeFilter(tag.dataset.type, tag.dataset.value);
                    }
                }

                const clearAllBtn = e.target.closest('[data-action="clear-all"]');
                if (clearAllBtn) {
                    this.reset();
                }
            });
        }
    }

    /**
     * 필터 변경 핸들러
     */
    handleFilterChange() {
        this.emit('change', { filters: this.getFilters() });

        // 클라이언트 모드: 즉시 적용
        if (this.options.mode === 'client') {
            this.applyClientFilter();
        }
    }

    /**
     * 현재 필터 값 가져오기
     * @returns {Object} 필터 객체
     */
    getFilters() {
        const filters = {};

        // 검색어
        if (this.elements.searchInput) {
            const value = this.elements.searchInput.value.trim();
            if (value) {
                filters.search = value;
            }
        }

        // 셀렉트
        this.elements.selects.forEach(select => {
            const name = select.dataset.filter || select.name;
            if (select.multiple) {
                const values = Array.from(select.selectedOptions)
                    .map(opt => opt.value)
                    .filter(v => v !== '');
                if (values.length > 0) {
                    filters[name] = values;
                }
            } else {
                const value = select.value;
                if (value) {
                    filters[name] = value;
                }
            }
        });

        // 체크박스
        const checkboxGroups = {};
        this.elements.checkboxes.forEach(checkbox => {
            const name = checkbox.dataset.filter || checkbox.name;
            if (checkbox.checked) {
                if (!checkboxGroups[name]) {
                    checkboxGroups[name] = [];
                }
                checkboxGroups[name].push(checkbox.value);
            }
        });
        Object.assign(filters, checkboxGroups);

        return filters;
    }

    /**
     * 필터 값 설정
     * @param {Object} filters - 설정할 필터 객체
     */
    setFilters(filters) {
        // 검색어
        if (this.elements.searchInput && filters.search !== undefined) {
            this.elements.searchInput.value = filters.search;
        }

        // 셀렉트
        this.elements.selects.forEach(select => {
            const name = select.dataset.filter || select.name;
            if (filters[name] !== undefined) {
                if (select.multiple) {
                    const values = Array.isArray(filters[name]) ? filters[name] : [filters[name]];
                    Array.from(select.options).forEach(opt => {
                        opt.selected = values.includes(opt.value);
                    });
                } else {
                    select.value = filters[name];
                }
            }
        });

        // 체크박스
        this.elements.checkboxes.forEach(checkbox => {
            const name = checkbox.dataset.filter || checkbox.name;
            if (filters[name] !== undefined) {
                const values = Array.isArray(filters[name]) ? filters[name] : [filters[name]];
                checkbox.checked = values.includes(checkbox.value);
            }
        });
    }

    /**
     * 필터 적용
     */
    apply() {
        const filters = this.getFilters();
        const event = this.emit('beforeApply', { filters });

        if (event.defaultPrevented) {
            return;
        }

        switch (this.options.mode) {
            case 'url':
                this.applyUrlFilter(filters);
                break;
            case 'client':
                this.applyClientFilter();
                break;
            case 'form':
                this.applyFormFilter(filters);
                break;
        }

        this.emit('filter', { filters });
    }

    /**
     * URL 모드 필터 적용
     * @param {Object} filters - 필터 객체
     */
    applyUrlFilter(filters) {
        const params = new URLSearchParams();

        Object.entries(filters).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                value.forEach(v => params.append(key, v));
            } else {
                params.set(key, value);
            }
        });

        const queryString = params.toString();
        const newUrl = queryString
            ? `${window.location.pathname}?${queryString}`
            : window.location.pathname;

        window.location.href = newUrl;
    }

    /**
     * 클라이언트 모드 필터 적용
     */
    applyClientFilter() {
        const filters = this.getFilters();
        const targets = document.querySelectorAll(this.options.targetSelector);

        targets.forEach(target => {
            const shouldShow = this.matchesFilters(target, filters);
            target.style.display = shouldShow ? '' : 'none';
            target.setAttribute('aria-hidden', !shouldShow);
        });

        // 결과 카운트 업데이트
        this.updateResultCount();
    }

    /**
     * 요소가 필터와 일치하는지 확인
     * @param {HTMLElement} element - 대상 요소
     * @param {Object} filters - 필터 객체
     * @returns {boolean}
     */
    matchesFilters(element, filters) {
        // 검색어 필터
        if (filters.search) {
            const text = element.textContent.toLowerCase();
            if (!text.includes(filters.search.toLowerCase())) {
                return false;
            }
        }

        // 다른 필터들
        for (const [key, value] of Object.entries(filters)) {
            if (key === 'search') continue;

            const elementValue = element.dataset[key];
            if (!elementValue) continue;

            const values = Array.isArray(value) ? value : [value];
            if (!values.includes(elementValue)) {
                return false;
            }
        }

        return true;
    }

    /**
     * 폼 모드 필터 적용
     * @param {Object} filters - 필터 객체
     */
    applyFormFilter(filters) {
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = this.options.action || window.location.pathname;

        Object.entries(filters).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                value.forEach(v => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = key;
                    input.value = v;
                    form.appendChild(input);
                });
            } else {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = key;
                input.value = value;
                form.appendChild(input);
            }
        });

        document.body.appendChild(form);
        form.submit();
    }

    /**
     * 필터 초기화
     */
    reset() {
        // 검색어 초기화
        if (this.elements.searchInput) {
            this.elements.searchInput.value = '';
        }

        // 셀렉트 초기화
        this.elements.selects.forEach(select => {
            if (select.multiple) {
                Array.from(select.options).forEach(opt => {
                    opt.selected = false;
                });
            } else {
                select.selectedIndex = 0;
            }
        });

        // 체크박스 초기화
        this.elements.checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        this.emit('reset', {});

        // 모드별 처리
        switch (this.options.mode) {
            case 'url':
                window.location.href = window.location.pathname;
                break;
            case 'client':
                this.applyClientFilter();
                break;
            case 'form':
                // 폼 모드는 초기화 후 재로드
                window.location.href = this.options.action || window.location.pathname;
                break;
        }
    }

    /**
     * 특정 필터 제거
     * @param {string} type - 필터 타입
     * @param {string} value - 필터 값
     */
    removeFilter(type, value) {
        // 셀렉트에서 제거
        this.elements.selects.forEach(select => {
            const name = select.dataset.filter || select.name;
            if (name === type) {
                if (select.multiple) {
                    Array.from(select.options).forEach(opt => {
                        if (opt.value === value) {
                            opt.selected = false;
                        }
                    });
                } else if (select.value === value) {
                    select.selectedIndex = 0;
                }
            }
        });

        // 체크박스에서 제거
        this.elements.checkboxes.forEach(checkbox => {
            const name = checkbox.dataset.filter || checkbox.name;
            if (name === type && checkbox.value === value) {
                checkbox.checked = false;
            }
        });

        // 검색어 제거
        if (type === 'search' && this.elements.searchInput) {
            this.elements.searchInput.value = '';
        }

        this.apply();
    }

    /**
     * URL에서 필터 로드
     */
    loadFiltersFromUrl() {
        const params = new URLSearchParams(window.location.search);
        const filters = {};

        params.forEach((value, key) => {
            if (filters[key]) {
                if (Array.isArray(filters[key])) {
                    filters[key].push(value);
                } else {
                    filters[key] = [filters[key], value];
                }
            } else {
                filters[key] = value;
            }
        });

        if (Object.keys(filters).length > 0) {
            this.setFilters(filters);
        }
    }

    /**
     * 결과 카운트 업데이트
     */
    updateResultCount() {
        const countEl = document.querySelector('.filter-result-count__number');
        if (countEl) {
            const targets = document.querySelectorAll(this.options.targetSelector);
            const visibleCount = Array.from(targets).filter(t => t.style.display !== 'none').length;
            countEl.textContent = visibleCount;
        }
    }

    /**
     * 디바운스 유틸리티
     * @param {Function} callback - 콜백 함수
     */
    debounce(callback) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(callback, this.options.debounceDelay);
    }

    /**
     * 이벤트 리스너 등록
     * @param {string} event - 이벤트 이름
     * @param {Function} callback - 콜백 함수
     */
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
        return this;
    }

    /**
     * 이벤트 리스너 제거
     * @param {string} event - 이벤트 이름
     * @param {Function} callback - 콜백 함수
     */
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
        return this;
    }

    /**
     * 이벤트 발생
     * @param {string} eventName - 이벤트 이름
     * @param {Object} detail - 이벤트 상세 데이터
     * @returns {CustomEvent}
     */
    emit(eventName, detail = {}) {
        // 커스텀 리스너 호출
        if (this.listeners[eventName]) {
            this.listeners[eventName].forEach(callback => {
                callback(detail);
            });
        }

        // DOM 이벤트 발생
        const event = new CustomEvent(`filterbar:${eventName}`, {
            bubbles: true,
            cancelable: true,
            detail
        });
        this.container.dispatchEvent(event);
        return event;
    }

    /**
     * 인스턴스 정리
     */
    destroy() {
        this.listeners = {};
        clearTimeout(this.debounceTimer);
        this.emit('destroy', {});
    }
}

/**
 * 자동 초기화 함수
 * @param {string} selector - 필터 바 선택자
 * @returns {FilterBar[]} 초기화된 FilterBar 인스턴스 배열
 */
export function initFilterBars(selector = '[data-filter-bar]') {
    const containers = document.querySelectorAll(selector);
    return Array.from(containers).map(container => new FilterBar(container));
}

// ========================================
// 전역 함수 호환성 (기존 filter.js 대체)
// ========================================

let defaultFilterBar = null;

/**
 * 필터 적용 (전역 함수)
 * @param {string} context - 컨텍스트 ('list' | 'dashboard')
 */
export function applyFilters(context = 'list') {
    const filterBar = getDefaultFilterBar();
    if (filterBar) {
        filterBar.apply();
    }
}

/**
 * 필터 초기화 (전역 함수)
 * @param {string} context - 컨텍스트
 */
export function resetFilters(context = 'list') {
    const filterBar = getDefaultFilterBar();
    if (filterBar) {
        filterBar.reset();
    }
}

/**
 * 필터 제거 (전역 함수)
 * @param {string} filterType - 필터 타입
 * @param {string} filterValue - 필터 값
 */
export function removeFilter(filterType, filterValue) {
    const filterBar = getDefaultFilterBar();
    if (filterBar) {
        filterBar.removeFilter(filterType, filterValue);
    }
}

/**
 * 필터 바 토글 (전역 함수)
 */
export function toggleFilterBar() {
    const filterContent = document.getElementById('filter-content');
    if (filterContent) {
        const isHidden = filterContent.dataset.collapsed === 'true';
        filterContent.dataset.collapsed = !isHidden;
        filterContent.classList.toggle('filter-bar--mobile-visible', isHidden);

        // 토글 버튼 상태 업데이트
        const toggleBtn = document.querySelector('[data-toggle="filter"]');
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', isHidden);
        }
    }
}

/**
 * 기본 FilterBar 인스턴스 가져오기
 * @returns {FilterBar|null}
 */
function getDefaultFilterBar() {
    if (!defaultFilterBar) {
        const container = document.querySelector('[data-filter-bar]');
        if (container) {
            defaultFilterBar = new FilterBar(container);
        }
    }
    return defaultFilterBar;
}

// ========================================
// 자동 초기화 (DOMContentLoaded)
// ========================================

if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        initFilterBars();
    });
}

// 전역 노출 (레거시 호환성)
if (typeof window !== 'undefined') {
    window.FilterBar = FilterBar;
    window.applyFilters = applyFilters;
    window.resetFilters = resetFilters;
    window.removeFilter = removeFilter;
    window.toggleFilterBar = toggleFilterBar;
}
