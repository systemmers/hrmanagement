/**
 * Classification Options Page JavaScript
 * 분류 옵션(부서, 직급, 상태) 관리 페이지
 */

import { showToast } from '../components/toast.js';

/**
 * ClassificationManager
 * 분류 옵션 CRUD 관리 클래스
 */
class ClassificationManager {
    constructor() {
        this.currentEditType = null;
        this.currentEditValue = null;
    }

    /**
     * 모달 열기 공통 함수
     * @param {string} modalId - 모달 요소 ID
     * @param {string} titleId - 타이틀 요소 ID
     * @param {string} title - 표시할 타이틀
     * @param {Array<{id: string, value: string}>} inputs - 입력 필드 배열
     * @param {string} editType - 'add' 또는 'edit'
     * @param {string|null} editValue - 수정 시 기존 값
     */
    openModal(modalId, titleId, title, inputs, editType, editValue = null) {
        this.currentEditType = editType;
        this.currentEditValue = editValue;

        document.getElementById(titleId).textContent = title;
        inputs.forEach(input => {
            document.getElementById(input.id).value = input.value;
        });
        document.getElementById(modalId).style.display = 'flex';
    }

    /**
     * 모달 닫기 공통 함수
     * @param {string} modalId - 모달 요소 ID
     */
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
        this.currentEditType = null;
        this.currentEditValue = null;
    }

    /**
     * API 호출 공통 함수
     * @param {string} url - API URL
     * @param {string} method - HTTP 메서드
     * @param {Object} data - 요청 데이터
     * @param {Function} onSuccess - 성공 콜백
     */
    async apiCall(url, method, data, onSuccess) {
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.error) {
                showToast(result.error, 'error');
            } else {
                showToast(result.message, 'success');
                if (onSuccess) onSuccess();
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            }
        } catch (error) {
            showToast('오류가 발생했습니다.', 'error');
            console.error('Error:', error);
        }
    }

    /**
     * 삭제 공통 함수
     * @param {string} url - API URL
     * @param {string} confirmMessage - 확인 메시지
     */
    async deleteItem(url, confirmMessage) {
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            const response = await fetch(url, { method: 'DELETE' });
            const result = await response.json();

            if (result.error) {
                showToast(result.error, 'error');
            } else {
                showToast(result.message, 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            }
        } catch (error) {
            showToast('오류가 발생했습니다.', 'error');
            console.error('Error:', error);
        }
    }
}

// 전역 인스턴스
const manager = new ClassificationManager();

// 부서 관리 함수
function showAddDepartmentModal() {
    manager.openModal(
        'department-modal',
        'department-modal-title',
        '부서 추가',
        [{ id: 'department-input', value: '' }],
        'add'
    );
}

function editDepartment(department) {
    manager.openModal(
        'department-modal',
        'department-modal-title',
        '부서 수정',
        [{ id: 'department-input', value: department }],
        'edit',
        department
    );
}

function closeDepartmentModal() {
    manager.closeModal('department-modal');
}

function saveDepartment() {
    const department = document.getElementById('department-input').value.trim();

    if (!department) {
        showToast('부서명을 입력해주세요.', 'error');
        return;
    }

    const url = manager.currentEditType === 'add'
        ? '/api/classification-options/departments'
        : `/api/classification-options/departments/${encodeURIComponent(manager.currentEditValue)}`;

    const method = manager.currentEditType === 'add' ? 'POST' : 'PUT';

    manager.apiCall(url, method, { department }, closeDepartmentModal);
}

function deleteDepartment(department) {
    manager.deleteItem(
        `/api/classification-options/departments/${encodeURIComponent(department)}`,
        `"${department}" 부서를 삭제하시겠습니까?`
    );
}

// 직급 관리 함수
function showAddPositionModal() {
    manager.openModal(
        'position-modal',
        'position-modal-title',
        '직급 추가',
        [{ id: 'position-input', value: '' }],
        'add'
    );
}

function editPosition(position) {
    manager.openModal(
        'position-modal',
        'position-modal-title',
        '직급 수정',
        [{ id: 'position-input', value: position }],
        'edit',
        position
    );
}

function closePositionModal() {
    manager.closeModal('position-modal');
}

function savePosition() {
    const position = document.getElementById('position-input').value.trim();

    if (!position) {
        showToast('직급명을 입력해주세요.', 'error');
        return;
    }

    const url = manager.currentEditType === 'add'
        ? '/api/classification-options/positions'
        : `/api/classification-options/positions/${encodeURIComponent(manager.currentEditValue)}`;

    const method = manager.currentEditType === 'add' ? 'POST' : 'PUT';

    manager.apiCall(url, method, { position }, closePositionModal);
}

function deletePosition(position) {
    manager.deleteItem(
        `/api/classification-options/positions/${encodeURIComponent(position)}`,
        `"${position}" 직급을 삭제하시겠습니까?`
    );
}

// 상태 관리 함수
function showAddStatusModal() {
    manager.openModal(
        'status-modal',
        'status-modal-title',
        '상태 추가',
        [
            { id: 'status-value-input', value: '' },
            { id: 'status-label-input', value: '' }
        ],
        'add'
    );
}

function editStatus(value, label) {
    manager.openModal(
        'status-modal',
        'status-modal-title',
        '상태 수정',
        [
            { id: 'status-value-input', value },
            { id: 'status-label-input', value: label }
        ],
        'edit',
        value
    );
}

function closeStatusModal() {
    manager.closeModal('status-modal');
}

function saveStatus() {
    const value = document.getElementById('status-value-input').value.trim();
    const label = document.getElementById('status-label-input').value.trim();

    if (!value || !label) {
        showToast('상태 값과 라벨을 모두 입력해주세요.', 'error');
        return;
    }

    const url = manager.currentEditType === 'add'
        ? '/api/classification-options/statuses'
        : `/api/classification-options/statuses/${encodeURIComponent(manager.currentEditValue)}`;

    const method = manager.currentEditType === 'add' ? 'POST' : 'PUT';

    manager.apiCall(url, method, { value, label }, closeStatusModal);
}

function deleteStatus(value) {
    manager.deleteItem(
        `/api/classification-options/statuses/${encodeURIComponent(value)}`,
        '이 상태를 삭제하시겠습니까?'
    );
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// window에 함수 노출 (inline onclick 호환성)
window.showAddDepartmentModal = showAddDepartmentModal;
window.editDepartment = editDepartment;
window.closeDepartmentModal = closeDepartmentModal;
window.saveDepartment = saveDepartment;
window.deleteDepartment = deleteDepartment;

window.showAddPositionModal = showAddPositionModal;
window.editPosition = editPosition;
window.closePositionModal = closePositionModal;
window.savePosition = savePosition;
window.deletePosition = deletePosition;

window.showAddStatusModal = showAddStatusModal;
window.editStatus = editStatus;
window.closeStatusModal = closeStatusModal;
window.saveStatus = saveStatus;
window.deleteStatus = deleteStatus;

// export for module usage
export {
    showAddDepartmentModal,
    editDepartment,
    closeDepartmentModal,
    saveDepartment,
    deleteDepartment,
    showAddPositionModal,
    editPosition,
    closePositionModal,
    savePosition,
    deletePosition,
    showAddStatusModal,
    editStatus,
    closeStatusModal,
    saveStatus,
    deleteStatus
};
