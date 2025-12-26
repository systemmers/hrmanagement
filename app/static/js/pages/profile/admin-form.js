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

// 파일 업로드 상수 (SSOT: constants/file-upload-constants.js와 동일 값)
const MAX_FILE_SIZE_MB = 10;
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
 * 사진 업로드 초기화
 */
function initPhotoUpload() {
    const selectPhotoBtn = document.getElementById('selectPhotoBtn');
    const photoFileInput = document.getElementById('photoFile');
    const photoPreview = document.getElementById('photoPreview');

    if (selectPhotoBtn && photoFileInput) {
        selectPhotoBtn.addEventListener('click', function() {
            photoFileInput.click();
        });

        photoFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // 파일 크기 체크
                if (file.size > MAX_FILE_SIZE) {
                    alert(`파일 크기는 ${MAX_FILE_SIZE_MB}MB 이하여야 합니다.`);
                    return;
                }

                // 미리보기 표시
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (photoPreview) {
                        photoPreview.innerHTML = '<img src="' + e.target.result + '" alt="프로필 사진" id="previewImage">';
                    }
                };
                reader.readAsDataURL(file);
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
                    photoPreview.innerHTML = '<div class="admin-profile-form__photo-placeholder" id="photoPlaceholder"><i class="fas fa-user"></i><span>사진 미등록</span></div>';
                }
                if (photoHiddenInput) {
                    photoHiddenInput.value = '';
                }
                if (photoFileInput) {
                    photoFileInput.value = '';
                }
                deletePhotoBtn.style.display = 'none';
            }
        });
    }
}
