/**
 * Admin Profile Form JavaScript
 * 법인 관리자 프로필 폼 스크립트
 *
 * 기능:
 * - 프로필 사진 업로드 및 미리보기
 * - 사진 삭제
 *
 * TODO: ES 모듈 전환 시 constants/file-upload-constants.js import 필요
 */

// 파일 업로드 상수 (SSOT: 5MB로 통일 - 템플릿과 일치)
const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024;

document.addEventListener('DOMContentLoaded', function() {
    initAdminProfileForm();
});

/**
 * 법인 관리자 프로필 폼 초기화
 */
function initAdminProfileForm() {
    initPhotoUpload();
    initPhotoDelete();
}

/**
 * Toast 메시지 표시 (helpers.js 의존성 제거 버전)
 */
function showToastMessage(message, type = 'info') {
    // Toast 컨테이너 생성 또는 재사용
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(container);
    }

    // Toast 요소 생성
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#3b82f6';
    toast.style.cssText = `
        background: ${bgColor}; color: white; padding: 12px 20px;
        border-radius: 8px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-size: 14px; animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    container.appendChild(toast);

    // 3초 후 제거
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * 사진 업로드 초기화
 */
function initPhotoUpload() {
    const selectPhotoBtn = document.getElementById('selectPhotoBtn');
    const photoFileInput = document.getElementById('photoFile');
    const photoPreview = document.getElementById('photoPreview');
    const deletePhotoBtn = document.getElementById('deletePhotoBtn');

    if (selectPhotoBtn && photoFileInput) {
        selectPhotoBtn.addEventListener('click', function() {
            photoFileInput.click();
        });

        photoFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // 파일 크기 체크
                if (file.size > MAX_FILE_SIZE) {
                    showToastMessage(`파일 크기는 ${MAX_FILE_SIZE_MB}MB 이하여야 합니다.`, 'error');
                    e.target.value = '';
                    return;
                }

                // 파일 형식 체크
                const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    showToastMessage('JPG, PNG, GIF, WebP 파일만 업로드 가능합니다.', 'error');
                    e.target.value = '';
                    return;
                }

                // 미리보기 표시
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (photoPreview) {
                        photoPreview.innerHTML = '<img src="' + e.target.result + '" alt="프로필 사진" id="previewImage">';
                    }
                    // 삭제 버튼 표시
                    if (deletePhotoBtn) {
                        deletePhotoBtn.classList.remove('hidden');
                    }
                };
                reader.readAsDataURL(file);

                showToastMessage('사진이 선택되었습니다. 저장 시 함께 업로드됩니다.', 'info');
            }
        });
    }
}

/**
 * 사진 삭제 초기화
 */
function initPhotoDelete() {
    const deletePhotoBtn = document.getElementById('deletePhotoBtn');
    const photoPreview = document.getElementById('photoPreview');
    const photoHiddenInput = document.getElementById('photo');
    const photoFileInput = document.getElementById('photoFile');

    if (deletePhotoBtn) {
        deletePhotoBtn.addEventListener('click', function() {
            if (confirm('프로필 사진을 삭제하시겠습니까?')) {
                if (photoPreview) {
                    photoPreview.innerHTML = '<div class="image-placeholder" id="photoPlaceholder"><i class="fas fa-user"></i><span>사진 미등록</span></div>';
                }
                if (photoHiddenInput) {
                    photoHiddenInput.value = '';
                }
                if (photoFileInput) {
                    photoFileInput.value = '';
                }
                deletePhotoBtn.classList.add('hidden');
            }
        });
    }
}
