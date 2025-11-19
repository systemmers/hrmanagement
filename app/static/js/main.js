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

// Flask 메시지 표시
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('[data-flash-message]');
    flashMessages.forEach(msg => {
        const category = msg.dataset.flashCategory || 'info';
        const message = msg.dataset.flashMessage;
        showToast(message, category);
    });
});

// 실시간 검색 (대시보드)
function initEmployeeSearch() {
    const searchInputs = document.querySelectorAll('[data-search="employee"]');

    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(async (e) => {
            const searchTerm = e.target.value;

            try {
                const response = await fetch(`/api/employees?q=${encodeURIComponent(searchTerm)}`);
                const data = await response.json();

                if (data.success) {
                    renderEmployeeGrid(data.employees);
                }
            } catch (error) {
                console.error('검색 오류:', error);
            }
        }, 300));
    });
}

// 직원 카드 그리드 렌더링
function renderEmployeeGrid(employees) {
    const grid = document.getElementById('employeeGrid');
    if (!grid) return;

    grid.innerHTML = '';

    employees.forEach(employee => {
        const card = createEmployeeCard(employee);
        grid.appendChild(card);
    });
}

// 직원 카드 생성
function createEmployeeCard(employee) {
    const card = document.createElement('div');
    card.className = 'employee-card';
    card.setAttribute('data-id', employee.id);

    const photoUrl = employee.photo ?
        `/static/uploads/${employee.photo}` :
        'https://i.pravatar.cc/150?img=' + (employee.id % 70);

    card.innerHTML = `
        <div class="employee-status ${employee.status}"></div>
        <img src="${photoUrl}" alt="${employee.name}" class="employee-photo" onerror="this.src='https://i.pravatar.cc/150'">
        <h3 class="employee-name">${employee.name}</h3>
        <p class="employee-position">${employee.department || '미배정'} · ${employee.position || '미정'}</p>
        <div class="employee-meta">
            <div class="employee-meta-item">
                <i class="fas fa-calendar"></i>
                <span>입사일: ${employee.hire_date || '미정'}</span>
            </div>
            <div class="employee-meta-item">
                <i class="fas fa-phone"></i>
                <span>${employee.phone || '연락처 없음'}</span>
            </div>
        </div>
        <div class="employee-actions">
            <button class="btn btn-secondary btn-small" onclick="viewEmployee(${employee.id})">
                <i class="fas fa-eye"></i>
                <span>보기</span>
            </button>
            <button class="btn btn-secondary btn-small" onclick="editEmployee(${employee.id})">
                <i class="fas fa-edit"></i>
                <span>수정</span>
            </button>
        </div>
    `;

    // 카드 전체 클릭 이벤트
    card.addEventListener('click', (e) => {
        if (!e.target.closest('button')) {
            viewEmployee(employee.id);
        }
    });

    return card;
}

// 직원 상세 보기
function viewEmployee(id) {
    window.location.href = `/employee/${id}`;
}

// 직원 수정
function editEmployee(id) {
    window.location.href = `/employee/${id}/edit`;
}

// 직원 삭제
function deleteEmployee(id, name) {
    if (confirm(`${name} 직원을 삭제하시겠습니까?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/employee/${id}/delete`;

        // CSRF 토큰 추가
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = csrfToken;
            form.appendChild(input);
        }

        document.body.appendChild(form);
        form.submit();
    }
}

// 디바운스 유틸리티
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 폼 검증
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });

    return isValid;
}

// 사진 미리보기
function previewPhoto(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const preview = document.getElementById('photoPreview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// 전화번호 자동 포맷
function formatPhone(input) {
    let value = input.value.replace(/\D/g, '');

    if (value.length <= 3) {
        input.value = value;
    } else if (value.length <= 7) {
        input.value = value.slice(0, 3) + '-' + value.slice(3);
    } else {
        input.value = value.slice(0, 3) + '-' + value.slice(3, 7) + '-' + value.slice(7, 11);
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 검색 기능 초기화
    initEmployeeSearch();

    // 전화번호 입력 포맷팅
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', () => formatPhone(input));
    });

    // 사진 업로드 미리보기
    const photoInput = document.getElementById('photo');
    if (photoInput) {
        photoInput.addEventListener('change', function() {
            previewPhoto(this);
        });
    }
});
