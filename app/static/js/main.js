/**
 * 인사카드 관리 시스템 - 메인 JavaScript
 */

// 토스트 알림 함수
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    const iconClass = type === 'success' ? 'fa-check-circle' : 
                      type === 'error' ? 'fa-exclamation-circle' : 
                      'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${iconClass} toast-icon"></i>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 로그아웃 함수
function handleLogout() {
    if (confirm('로그아웃 하시겠습니까?')) {
        showToast('로그아웃되었습니다.');
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
}

// 페이지 로드 시 초기화
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
    
    // 폼 유효성 검사
    const forms = document.querySelectorAll('form.employee-form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#ef4444';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('필수 항목을 모두 입력해주세요.', 'error');
            }
        });
    });
    
    // 입력 필드 포커스 시 에러 상태 제거
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.style.borderColor = '';
        });
    });
});

// AJAX 검색 (옵션)
function searchEmployees(query) {
    fetch(`/search?q=${encodeURIComponent(query)}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // 결과 처리
        console.log('Search results:', data);
    })
    .catch(error => {
        console.error('Search error:', error);
    });
}

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

// 직원 목록 뷰 전환 함수
function toggleEmployeeView(viewType) {
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
}

// 페이지 로드 시 뷰 전환 초기화
document.addEventListener('DOMContentLoaded', () => {
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    
    if (listView && cardView) {
        toggleEmployeeView('list');
    }
    
    // 필터 이벤트 리스너 설정
    setupFilterListeners();
});

// 필터 이벤트 리스너 설정
function setupFilterListeners() {
    // 부서/직급 다중 선택 필터
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', () => {
            applyFilters();
        });
    });
    
    // 상태 체크박스 필터
    const filterCheckboxes = document.querySelectorAll('.filter-checkbox');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            applyFilters();
        });
    });
}

// 필터 적용 함수
function applyFilters(context = 'list') {
    const params = new URLSearchParams();
    
    // 부서 필터
    const deptSelect = document.getElementById(context === 'dashboard' ? 'filter-department-dashboard' : 'filter-department');
    if (deptSelect) {
        const selectedDepts = Array.from(deptSelect.selectedOptions)
            .map(opt => opt.value)
            .filter(val => val !== '');
        selectedDepts.forEach(dept => {
            params.append('department', dept);
        });
    }
    
    // 직급 필터 (목록 페이지에만)
    if (context === 'list') {
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
    const baseUrl = context === 'dashboard' ? '/' : '/employees';
    const queryString = params.toString();
    const newUrl = queryString ? `${baseUrl}?${queryString}` : baseUrl;
    
    window.location.href = newUrl;
}

// 필터 초기화 함수
function resetFilters(context = 'list') {
    const baseUrl = context === 'dashboard' ? '/' : '/employees';
    window.location.href = baseUrl;
}

// 개별 필터 제거 함수
function removeFilter(filterType, filterValue) {
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

// 대시보드 필터 바 토글
function toggleFilterBar() {
    const filterContent = document.getElementById('filter-content');
    if (filterContent) {
        filterContent.style.display = filterContent.style.display === 'none' ? 'flex' : 'none';
    }
}

