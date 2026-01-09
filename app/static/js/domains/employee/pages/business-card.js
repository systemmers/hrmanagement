/**
 * @deprecated 2026-01-09
 * 명함 기능은 BusinessCard 도메인으로 이동되었습니다.
 * 새로운 위치: js/domains/businesscard/
 *
 * Business Card Upload Module (레거시)
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 명함 업로드/삭제 기능
 *
 * Migration:
 * - 명함 카드 렌더링: js/domains/businesscard/components/BusinessCard.js
 * - QR 코드 생성: js/domains/businesscard/components/QRGenerator.js
 * - API 통신: js/domains/businesscard/services/businesscard-api.js
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

    const actionsContainer = item.querySelector('.card__actions');
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
 * 명함 파일 미리보기 초기화 (신규 등록 모드)
 * 파일을 선택하면 미리보기만 표시하고, 실제 업로드는 폼 제출 시 서버에서 처리
 */
export function initBusinessCardPreviewForCreate() {
    const frontFileInput = document.getElementById('businessCardFrontFile');
    const backFileInput = document.getElementById('businessCardBackFile');

    if (!frontFileInput && !backFileInput) return;

    // 직원 ID가 있으면 수정 모드이므로 여기서 처리하지 않음
    const employeeId = getEmployeeIdFromForm();
    if (employeeId) return;

    // 파일 선택 시 미리보기 표시
    const handleFilePreview = (e, side) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 유효성 검사
        const validation = validateImageFile(file);
        if (!validation.valid) {
            showToast(validation.error, 'error');
            e.target.value = '';
            return;
        }

        const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
        const sideLabel = side === 'front' ? '앞면' : '뒷면';
        const preview = document.getElementById(previewId);

        if (preview) {
            // FileReader로 미리보기 생성
            const reader = new FileReader();
            reader.onload = (event) => {
                preview.innerHTML = `<img src="${event.target.result}" alt="명함 ${sideLabel} 미리보기">`;

                // 삭제 버튼 표시
                const item = document.querySelector(`.business-card-item[data-side="${side}"]`);
                if (item) {
                    const deleteBtn = item.querySelector('.delete-card-btn');
                    if (deleteBtn) {
                        deleteBtn.classList.remove('hidden');
                    }
                }
            };
            reader.readAsDataURL(file);
        }

        showToast(`명함 ${sideLabel}이 선택되었습니다. 등록 시 함께 저장됩니다.`, 'info');
    };

    // 삭제 버튼 클릭 시 초기화 (신규 등록 모드)
    const handleDeletePreview = (side) => {
        const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
        const fileInputId = side === 'front' ? 'businessCardFrontFile' : 'businessCardBackFile';
        const sideLabel = side === 'front' ? '앞면' : '뒷면';

        const preview = document.getElementById(previewId);
        const fileInput = document.getElementById(fileInputId);

        // 파일 입력 초기화
        if (fileInput) {
            fileInput.value = '';
        }

        // 미리보기를 기본 상태로 복원
        if (preview) {
            preview.innerHTML = `
                <div class="card-placeholder">
                    <i class="fas fa-id-card"></i>
                    <span>${sideLabel}</span>
                </div>
            `;
        }

        // 삭제 버튼 숨기기
        const item = document.querySelector(`.business-card-item[data-side="${side}"]`);
        if (item) {
            const deleteBtn = item.querySelector('.delete-card-btn');
            if (deleteBtn) {
                deleteBtn.classList.add('hidden');
            }
        }

        showToast(`명함 ${sideLabel} 선택이 취소되었습니다.`, 'info');
    };

    // 선택 버튼 클릭 이벤트
    const selectFrontBtn = document.getElementById('selectBusinessCardFrontBtn');
    const selectBackBtn = document.getElementById('selectBusinessCardBackBtn');

    if (selectFrontBtn && frontFileInput) {
        selectFrontBtn.addEventListener('click', () => frontFileInput.click());
    }
    if (selectBackBtn && backFileInput) {
        selectBackBtn.addEventListener('click', () => backFileInput.click());
    }

    // 앞면 미리보기
    if (frontFileInput) {
        frontFileInput.addEventListener('change', (e) => handleFilePreview(e, 'front'));
    }

    // 뒷면 미리보기
    if (backFileInput) {
        backFileInput.addEventListener('change', (e) => handleFilePreview(e, 'back'));
    }

    // 신규 등록 모드 삭제 버튼 이벤트
    document.querySelectorAll('.delete-card-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            handleDeletePreview(btn.dataset.side);
        });
    });
}

/**
 * 명함 업로드 초기화 (수정 모드)
 */
export function initBusinessCardUpload() {
    const frontFileInput = document.getElementById('businessCardFrontFile');
    const backFileInput = document.getElementById('businessCardBackFile');

    if (!frontFileInput && !backFileInput) return;

    const employeeId = getEmployeeIdFromForm();
    if (!employeeId) {
        // 신규 등록 모드면 미리보기 전용 초기화 실행
        initBusinessCardPreviewForCreate();
        return;
    }

    // 선택 버튼 클릭 이벤트
    const selectFrontBtn = document.getElementById('selectBusinessCardFrontBtn');
    const selectBackBtn = document.getElementById('selectBusinessCardBackBtn');

    if (selectFrontBtn && frontFileInput) {
        selectFrontBtn.addEventListener('click', () => frontFileInput.click());
    }
    if (selectBackBtn && backFileInput) {
        selectBackBtn.addEventListener('click', () => backFileInput.click());
    }

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
    initBusinessCardUpload,
    initBusinessCardPreviewForCreate
};
