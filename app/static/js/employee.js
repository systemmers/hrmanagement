/**
 * 직원 관리 JavaScript
 * XSS 방지를 위해 이벤트 리스너 분리
 */

document.addEventListener('DOMContentLoaded', function() {
    // 삭제 버튼 이벤트 리스너
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const employeeId = this.dataset.employeeId;
            const employeeName = this.dataset.employeeName;
            deleteEmployee(employeeId, employeeName);
        });
    });
});

/**
 * 직원 삭제 함수
 * @param {string|number} id - 직원 ID
 * @param {string} name - 직원 이름
 */
function deleteEmployee(id, name) {
    if (confirm(`정말로 ${name} 직원을 삭제하시겠습니까?`)) {
        fetch(`/employee/${id}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/employee';
            } else {
                return response.json().then(data => {
                    throw new Error(data.message || '삭제 중 오류가 발생했습니다.');
                });
            }
        })
        .catch(error => {
            alert(error.message);
        });
    }
}

/**
 * CSRF 토큰 가져오기
 * @returns {string} CSRF 토큰
 */
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}
