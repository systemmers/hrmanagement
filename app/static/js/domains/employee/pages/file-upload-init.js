/**
 * File Upload Initialization Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 첨부파일 업로드 초기화
 */

import { FileUpload } from '../../../shared/components/file-upload.js';

/**
 * 파일 업로드 초기화
 */
export function initFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');
    if (!uploadArea) return;

    // 직원 ID 추출 (수정 모드에서만 파일 업로드 가능)
    const form = document.getElementById('employeeForm');
    if (!form) return;

    const actionUrl = form.getAttribute('action');
    // /employees/123/update 형식에서 ID 추출
    const match = actionUrl.match(/\/employees\/(\d+)\/update/);

    if (!match) {
        // 신규 등록 모드에서는 파일 업로드 비활성화
        disableFileUpload(uploadArea);
        return;
    }

    const employeeId = parseInt(match[1], 10);

    new FileUpload({
        uploadAreaId: 'fileUploadArea',
        fileListId: 'fileList',
        employeeId: employeeId,
        onUploadComplete: (attachment) => {
            // 업로드 완료 후 추가 처리가 필요하면 여기에 구현
        }
    });
}

/**
 * 파일 업로드 비활성화 (신규 등록 모드)
 * @param {HTMLElement} uploadArea - 업로드 영역 요소
 */
function disableFileUpload(uploadArea) {
    uploadArea.style.opacity = '0.5';
    uploadArea.style.pointerEvents = 'none';

    const textElement = uploadArea.querySelector('.file-upload-text');
    if (textElement) {
        textElement.textContent = '직원 등록 후 파일 업로드 가능';
    }
}

export default {
    initFileUpload
};
