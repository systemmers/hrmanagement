/**
 * Business Card Upload Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 명함 업로드/삭제 기능
 */

import { getEmployeeIdFromForm, showToast, validateImageFile } from './helpers.js';

/**
 * 명함 삭제 버튼 동적 추가
 * @param {string} side - 앞면(front) 또는 뒷면(back)
 * @param {number} employeeId - 직원 ID
 */
function addBusinessCardDeleteButton(side, employeeId) {
    const item = document.querySelector(`.business-card-item[data-side="${side}"]`);
    if (!item) return;

    const actionsContainer = item.querySelector('.card-actions');
    if (!actionsContainer) return;

    // 이미 삭제 버튼이 있으면 무시
    if (actionsContainer.querySelector('.delete-card-btn')) return;

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn btn-outline-danger btn-sm delete-card-btn';
    deleteBtn.dataset.side = side;
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';

    deleteBtn.addEventListener('click', () => handleDeleteBusinessCard(side, employeeId, deleteBtn));
    actionsContainer.appendChild(deleteBtn);
}

/**
 * 명함 삭제 처리
 * @param {string} side - 앞면(front) 또는 뒷면(back)
 * @param {number} employeeId - 직원 ID
 * @param {HTMLElement} deleteBtn - 삭제 버튼 요소
 */
async function handleDeleteBusinessCard(side, employeeId, deleteBtn) {
    const sideLabel = side === 'front' ? '앞면' : '뒷면';

    if (!confirm(`명함 ${sideLabel}을 삭제하시겠습니까?`)) return;

    try {
        deleteBtn.disabled = true;

        const response = await fetch(`/api/employees/${employeeId}/business-card/${side}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.innerHTML = `
                    <div class="card-placeholder">
                        <i class="fas fa-id-card"></i>
                        <span>${sideLabel} 미등록</span>
                    </div>
                `;
            }
            deleteBtn.remove();
            showToast(`명함 ${sideLabel}이 삭제되었습니다.`, 'success');
        } else {
            showToast(result.error || '삭제 실패', 'error');
        }
    } catch (error) {
        console.error('Business card delete error:', error);
        showToast('삭제 중 오류가 발생했습니다.', 'error');
    } finally {
        deleteBtn.disabled = false;
    }
}

/**
 * 명함 업로드 처리
 * @param {Event} e - 변경 이벤트
 * @param {string} side - 앞면(front) 또는 뒷면(back)
 * @param {number} employeeId - 직원 ID
 */
async function handleBusinessCardUpload(e, side, employeeId) {
    const file = e.target.files[0];
    if (!file) return;

    // 파일 유효성 검사
    const validation = validateImageFile(file);
    if (!validation.valid) {
        showToast(validation.error, 'error');
        return;
    }

    const sideLabel = side === 'front' ? '앞면' : '뒷면';
    const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
    const preview = document.getElementById(previewId);

    try {
        if (preview) {
            preview.innerHTML = '<div class="card-loading"><i class="fas fa-spinner fa-spin"></i></div>';
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('side', side);

        const response = await fetch(`/api/employees/${employeeId}/business-card`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            if (preview) {
                preview.innerHTML = `<img src="${result.file_path}" alt="명함 ${sideLabel}">`;
            }

            // 삭제 버튼 추가
            addBusinessCardDeleteButton(side, employeeId);

            showToast(`명함 ${sideLabel}이 업로드되었습니다.`, 'success');
        } else {
            if (preview) {
                preview.innerHTML = `
                    <div class="card-placeholder">
                        <i class="fas fa-id-card"></i>
                        <span>${sideLabel} 미등록</span>
                    </div>
                `;
            }
            showToast(result.error || '업로드 실패', 'error');
        }
    } catch (error) {
        console.error('Business card upload error:', error);
        if (preview) {
            preview.innerHTML = `
                <div class="card-placeholder">
                    <i class="fas fa-id-card"></i>
                    <span>${sideLabel} 미등록</span>
                </div>
            `;
        }
        showToast('업로드 중 오류가 발생했습니다.', 'error');
    } finally {
        e.target.value = '';
    }
}

/**
 * 명함 업로드 초기화
 */
export function initBusinessCardUpload() {
    const frontFileInput = document.getElementById('businessCardFrontFile');
    const backFileInput = document.getElementById('businessCardBackFile');

    if (!frontFileInput && !backFileInput) return;

    const employeeId = getEmployeeIdFromForm();
    if (!employeeId) return;

    // 앞면 업로드
    if (frontFileInput) {
        frontFileInput.addEventListener('change', (e) => handleBusinessCardUpload(e, 'front', employeeId));
    }

    // 뒷면 업로드
    if (backFileInput) {
        backFileInput.addEventListener('change', (e) => handleBusinessCardUpload(e, 'back', employeeId));
    }

    // 기존 삭제 버튼 이벤트
    document.querySelectorAll('.delete-card-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            handleDeleteBusinessCard(btn.dataset.side, employeeId, btn);
        });
    });
}

export default {
    initBusinessCardUpload
};
