/**
 * Photo Upload Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 프로필 사진 업로드/삭제 기능
 */

import { getEmployeeIdFromForm, showToast, validateImageFile } from './helpers.js';

/**
 * 사진 미리보기 초기화 (URL 입력용 - 신규 등록 모드)
 */
export function initPhotoPreview() {
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');

    if (!photoInput || !photoPreview) return;

    // URL 타입 input인 경우만 처리 (신규 등록 모드)
    if (photoInput.type !== 'url') return;

    photoInput.addEventListener('input', (e) => {
        const url = e.target.value.trim();

        if (url) {
            const img = new Image();
            img.onload = () => {
                photoPreview.innerHTML = `<img src="${url}" alt="프로필 사진" id="previewImage">`;
            };
            img.onerror = () => {
                photoPreview.innerHTML = `
                    <div class="image-placeholder">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>이미지 로드 실패</span>
                    </div>
                `;
            };
            img.src = url;
        } else {
            photoPreview.innerHTML = `
                <div class="image-placeholder">
                    <i class="fas fa-user"></i>
                    <span>사진 미등록</span>
                </div>
            `;
        }
    });
}

/**
 * 삭제 버튼 동적 추가
 * @param {number} employeeId - 직원 ID
 */
function addDeletePhotoButton(employeeId) {
    const buttonsContainer = document.querySelector('.photo-upload-buttons');
    if (!buttonsContainer) return;

    // 이미 삭제 버튼이 있으면 무시
    if (document.getElementById('deletePhotoBtn')) return;

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.id = 'deletePhotoBtn';
    deleteBtn.className = 'btn btn-outline-danger btn-sm';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i> 삭제';

    deleteBtn.addEventListener('click', () => handleDeletePhoto(employeeId, deleteBtn));
    buttonsContainer.appendChild(deleteBtn);
}

/**
 * 프로필 사진 삭제 처리
 * @param {number} employeeId - 직원 ID
 * @param {HTMLElement} deleteBtn - 삭제 버튼 요소
 */
async function handleDeletePhoto(employeeId, deleteBtn) {
    if (!confirm('프로필 사진을 삭제하시겠습니까?')) return;

    try {
        deleteBtn.disabled = true;

        const response = await fetch(`/api/employees/${employeeId}/profile-photo`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            const photoPreview = document.getElementById('photoPreview');
            const photoHiddenInput = document.getElementById('photo');

            photoPreview.innerHTML = `
                <div class="image-placeholder" id="photoPlaceholder">
                    <i class="fas fa-user"></i>
                    <span>사진 미등록</span>
                </div>
            `;
            if (photoHiddenInput) {
                photoHiddenInput.value = '';
            }
            deleteBtn.remove();
            showToast('프로필 사진이 삭제되었습니다.', 'success');
        } else {
            showToast(result.error || '삭제 실패', 'error');
        }
    } catch (error) {
        console.error('Profile photo delete error:', error);
        showToast('삭제 중 오류가 발생했습니다.', 'error');
    } finally {
        deleteBtn.disabled = false;
    }
}

/**
 * 프로필 사진 파일 미리보기 초기화 (신규 등록 모드)
 * 파일을 선택하면 미리보기만 표시하고, 실제 업로드는 폼 제출 시 서버에서 처리
 */
export function initPhotoPreviewForCreate() {
    const selectPhotoBtn = document.getElementById('selectPhotoBtn');
    const deletePhotoBtn = document.getElementById('deletePhotoBtn');
    const photoFileInput = document.getElementById('photoFile');
    const photoPreview = document.getElementById('photoPreview');
    const photoHiddenInput = document.getElementById('photo');

    if (!selectPhotoBtn || !photoFileInput) return;

    // 직원 ID가 있으면 수정 모드이므로 여기서 처리하지 않음
    const employeeId = getEmployeeIdFromForm();
    if (employeeId) return;

    // 기본 이미지 경로 저장
    const defaultPhotoPath = photoHiddenInput ? photoHiddenInput.value : '';

    // 사진 선택 버튼 클릭
    selectPhotoBtn.addEventListener('click', () => {
        photoFileInput.click();
    });

    // 파일 선택 시 미리보기만 표시
    photoFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 유효성 검사
        const validation = validateImageFile(file);
        if (!validation.valid) {
            showToast(validation.error, 'error');
            photoFileInput.value = '';
            return;
        }

        // FileReader로 미리보기 생성
        const reader = new FileReader();
        reader.onload = (event) => {
            photoPreview.innerHTML = `<img src="${event.target.result}" alt="프로필 사진 미리보기" id="previewImage">`;
            // 삭제 버튼 표시
            if (deletePhotoBtn) {
                deletePhotoBtn.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);

        showToast('사진이 선택되었습니다. 등록 시 함께 저장됩니다.', 'info');
    });

    // 삭제 버튼 클릭 시 초기화 (신규 등록 모드)
    if (deletePhotoBtn) {
        deletePhotoBtn.addEventListener('click', () => {
            // 파일 입력 초기화
            photoFileInput.value = '';

            // 미리보기를 기본 이미지로 복원
            photoPreview.innerHTML = `
                <div class="image-placeholder" id="photoPlaceholder">
                    <i class="fas fa-user"></i>
                    <span>사진 미등록</span>
                </div>
            `;

            // hidden input 초기화
            if (photoHiddenInput) {
                photoHiddenInput.value = defaultPhotoPath;
            }

            // 삭제 버튼 숨기기
            deletePhotoBtn.classList.add('hidden');

            showToast('사진 선택이 취소되었습니다.', 'info');
        });
    }
}

/**
 * 프로필 사진 파일 업로드 초기화 (수정 모드)
 */
export function initProfilePhotoUpload() {
    const selectPhotoBtn = document.getElementById('selectPhotoBtn');
    const deletePhotoBtn = document.getElementById('deletePhotoBtn');
    const photoFileInput = document.getElementById('photoFile');
    const photoHiddenInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');

    if (!selectPhotoBtn || !photoFileInput) return;

    // 직원 ID 추출
    const employeeId = getEmployeeIdFromForm();
    if (!employeeId) {
        // 신규 등록 모드면 미리보기 전용 초기화 실행
        initPhotoPreviewForCreate();
        return;
    }

    // 사진 선택 버튼 클릭
    selectPhotoBtn.addEventListener('click', () => {
        photoFileInput.click();
    });

    // 파일 선택 시 업로드
    photoFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 유효성 검사
        const validation = validateImageFile(file);
        if (!validation.valid) {
            showToast(validation.error, 'error');
            return;
        }

        // 업로드 진행
        try {
            selectPhotoBtn.disabled = true;
            selectPhotoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 업로드 중...';

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`/api/employees/${employeeId}/profile-photo`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // 미리보기 업데이트
                photoPreview.innerHTML = `<img src="${result.file_path}" alt="프로필 사진" id="previewImage">`;
                if (photoHiddenInput) {
                    photoHiddenInput.value = result.file_path;
                }

                // 삭제 버튼 추가
                addDeletePhotoButton(employeeId);

                showToast('프로필 사진이 업로드되었습니다.', 'success');
            } else {
                showToast(result.error || '업로드 실패', 'error');
            }
        } catch (error) {
            console.error('Profile photo upload error:', error);
            showToast('업로드 중 오류가 발생했습니다.', 'error');
        } finally {
            selectPhotoBtn.disabled = false;
            selectPhotoBtn.innerHTML = '<i class="fas fa-camera"></i> 사진 선택';
            photoFileInput.value = '';
        }
    });

    // 기존 삭제 버튼 이벤트
    if (deletePhotoBtn) {
        deletePhotoBtn.addEventListener('click', () => handleDeletePhoto(employeeId, deletePhotoBtn));
    }
}

export default {
    initPhotoPreview,
    initPhotoPreviewForCreate,
    initProfilePhotoUpload
};
