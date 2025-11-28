/**
 * 필터 컴포넌트
 */

export class Filter {
    constructor(context = 'list') {
        this.context = context;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 부서/직급 다중 선택 필터
        const filterSelects = document.querySelectorAll('.filter-select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.apply();
            });
        });

        // 상태 체크박스 필터
        const filterCheckboxes = document.querySelectorAll('.filter-checkbox');
        filterCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.apply();
            });
        });
    }

    apply() {
        const params = new URLSearchParams();

        // 부서 필터
        const deptSelect = document.getElementById(
            this.context === 'dashboard' ? 'filter-department-dashboard' : 'filter-department'
        );
        if (deptSelect) {
            const selectedDepts = Array.from(deptSelect.selectedOptions)
                .map(opt => opt.value)
                .filter(val => val !== '');
            selectedDepts.forEach(dept => {
                params.append('department', dept);
            });
        }

        // 직급 필터 (목록 페이지에만)
        if (this.context === 'list') {
            const posSelect = document.getElementById('filter-position');
            if (posSelect) {
                const selectedPositions = Array.from(posSelect.selectedOptions)
                    .map(opt => opt.value)
                    .filter(val => val !== '');
                selectedPositions.forEach(pos => {
                    params.append('position', pos);
                });
            }
        }

        // 상태 필터
        const statusCheckboxes = document.querySelectorAll('.filter-checkbox:checked');
        statusCheckboxes.forEach(checkbox => {
            params.append('status', checkbox.value);
        });

        // URL 업데이트
        const baseUrl = this.context === 'dashboard' ? '/' : '/employees';
        const queryString = params.toString();
        const newUrl = queryString ? `${baseUrl}?${queryString}` : baseUrl;

        window.location.href = newUrl;
    }

    reset() {
        const baseUrl = this.context === 'dashboard' ? '/' : '/employees';
        window.location.href = baseUrl;
    }

    remove(filterType, filterValue) {
        const url = new URL(window.location.href);
        const params = url.searchParams;

        // 해당 필터 값 제거
        const values = params.getAll(filterType);
        params.delete(filterType);
        values.forEach(val => {
            if (val !== filterValue) {
                params.append(filterType, val);
            }
        });

        // URL 업데이트
        const queryString = params.toString();
        const newUrl = queryString ? `${url.pathname}?${queryString}` : url.pathname;
        window.location.href = newUrl;
    }

    toggleFilterBar() {
        const filterContent = document.getElementById('filter-content');
        if (filterContent) {
            filterContent.style.display = filterContent.style.display === 'none' ? 'flex' : 'none';
        }
    }
}

// 전역 함수로도 사용 가능하도록 (기존 코드 호환성)
export function applyFilters(context = 'list') {
    const filter = new Filter(context);
    filter.apply();
}

export function resetFilters(context = 'list') {
    const filter = new Filter(context);
    filter.reset();
}

export function removeFilter(filterType, filterValue) {
    const filter = new Filter();
    filter.remove(filterType, filterValue);
}

export function toggleFilterBar() {
    const filter = new Filter();
    filter.toggleFilterBar();
}
