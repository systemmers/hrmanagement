/**
 * 분류 옵션 관리 JavaScript
 */

let currentEditType = null;
let currentEditValue = null;

// 부서 관리
function showAddDepartmentModal() {
    currentEditType = 'add';
    currentEditValue = null;
    document.getElementById('department-modal-title').textContent = '부서 추가';
    document.getElementById('department-input').value = '';
    document.getElementById('department-modal').style.display = 'flex';
}

function editDepartment(department) {
    currentEditType = 'edit';
    currentEditValue = department;
    document.getElementById('department-modal-title').textContent = '부서 수정';
    document.getElementById('department-input').value = department;
    document.getElementById('department-modal').style.display = 'flex';
}

function closeDepartmentModal() {
    document.getElementById('department-modal').style.display = 'none';
    currentEditType = null;
    currentEditValue = null;
}

function saveDepartment() {
    const input = document.getElementById('department-input');
    const department = input.value.trim();
    
    if (!department) {
        showToast('부서명을 입력해주세요.', 'error');
        return;
    }
    
    const url = currentEditType === 'add' 
        ? '/api/classification-options/departments'
        : `/api/classification-options/departments/${encodeURIComponent(currentEditValue)}`;
    
    const method = currentEditType === 'add' ? 'POST' : 'PUT';
    const data = { department: department };
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(data.message, 'success');
            closeDepartmentModal();
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    })
    .catch(error => {
        showToast('오류가 발생했습니다.', 'error');
        console.error('Error:', error);
    });
}

function deleteDepartment(department) {
    if (!confirm(`"${department}" 부서를 삭제하시겠습니까?`)) {
        return;
    }
    
    fetch(`/api/classification-options/departments/${encodeURIComponent(department)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    })
    .catch(error => {
        showToast('오류가 발생했습니다.', 'error');
        console.error('Error:', error);
    });
}

// 직급 관리
function showAddPositionModal() {
    currentEditType = 'add';
    currentEditValue = null;
    document.getElementById('position-modal-title').textContent = '직급 추가';
    document.getElementById('position-input').value = '';
    document.getElementById('position-modal').style.display = 'flex';
}

function editPosition(position) {
    currentEditType = 'edit';
    currentEditValue = position;
    document.getElementById('position-modal-title').textContent = '직급 수정';
    document.getElementById('position-input').value = position;
    document.getElementById('position-modal').style.display = 'flex';
}

function closePositionModal() {
    document.getElementById('position-modal').style.display = 'none';
    currentEditType = null;
    currentEditValue = null;
}

function savePosition() {
    const input = document.getElementById('position-input');
    const position = input.value.trim();
    
    if (!position) {
        showToast('직급명을 입력해주세요.', 'error');
        return;
    }
    
    const url = currentEditType === 'add' 
        ? '/api/classification-options/positions'
        : `/api/classification-options/positions/${encodeURIComponent(currentEditValue)}`;
    
    const method = currentEditType === 'add' ? 'POST' : 'PUT';
    const data = { position: position };
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(data.message, 'success');
            closePositionModal();
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    })
    .catch(error => {
        showToast('오류가 발생했습니다.', 'error');
        console.error('Error:', error);
    });
}

function deletePosition(position) {
    if (!confirm(`"${position}" 직급을 삭제하시겠습니까?`)) {
        return;
    }
    
    fetch(`/api/classification-options/positions/${encodeURIComponent(position)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    })
    .catch(error => {
        showToast('오류가 발생했습니다.', 'error');
        console.error('Error:', error);
    });
}

// 상태 관리
function showAddStatusModal() {
    currentEditType = 'add';
    currentEditValue = null;
    document.getElementById('status-modal-title').textContent = '상태 추가';
    document.getElementById('status-value-input').value = '';
    document.getElementById('status-label-input').value = '';
    document.getElementById('status-modal').style.display = 'flex';
}

function editStatus(value, label) {
    currentEditType = 'edit';
    currentEditValue = value;
    document.getElementById('status-modal-title').textContent = '상태 수정';
    document.getElementById('status-value-input').value = value;
    document.getElementById('status-label-input').value = label;
    document.getElementById('status-modal').style.display = 'flex';
}

function closeStatusModal() {
    document.getElementById('status-modal').style.display = 'none';
    currentEditType = null;
    currentEditValue = null;
}

function saveStatus() {
    const valueInput = document.getElementById('status-value-input');
    const labelInput = document.getElementById('status-label-input');
    const value = valueInput.value.trim();
    const label = labelInput.value.trim();
    
    if (!value || !label) {
        showToast('상태 값과 라벨을 모두 입력해주세요.', 'error');
        return;
    }
    
    const url = currentEditType === 'add' 
        ? '/api/classification-options/statuses'
        : `/api/classification-options/statuses/${encodeURIComponent(currentEditValue)}`;
    
    const method = currentEditType === 'add' ? 'POST' : 'PUT';
    const data = { value: value, label: label };
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(data.message, 'success');
            closeStatusModal();
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    })
    .catch(error => {
        showToast('오류가 발생했습니다.', 'error');
        console.error('Error:', error);
    });
}

function deleteStatus(value) {
    if (!confirm('이 상태를 삭제하시겠습니까?')) {
        return;
    }
    
    fetch(`/api/classification-options/statuses/${encodeURIComponent(value)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    })
    .catch(error => {
        showToast('오류가 발생했습니다.', 'error');
        console.error('Error:', error);
    });
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

