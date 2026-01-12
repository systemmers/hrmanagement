/**
 * File Upload Initialization Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 첨부파일 업로드 초기화
 * - 템플릿의 data-owner-type/data-owner-id 속성 우선 사용
 * - Fallback: URL 패턴에서 추출
 */

import { FileUpload } from '../../../shared/components/file-upload.js';

/**
 * 파일 업로드 초기화
 */
export function initFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');
    if (!uploadArea) return;

    // 1. 템플릿에서 설정한 owner_type/owner_id 속성 확인 (SSOT)
    let ownerType = uploadArea.dataset.ownerType;
    let ownerId = uploadArea.dataset.ownerId;

    // 2. Fallback: 폼 액션 URL 또는 data-employee-id에서 추출
    if (!ownerId) {
        // 폼에서 ID 추출 시도
        const form = document.getElementById('employeeForm') || document.getElementById('profileEditForm');
        if (form) {
            const actionUrl = form.getAttribute('action');
            // /employees/123/update 형식에서 ID 추출
            const employeeMatch = actionUrl.match(/\/employees\/(\d+)\/update/);
            if (employeeMatch) {
                ownerId = employeeMatch[1];
                ownerType = ownerType || 'employee';
            }
        }

        // data-employee-id 속성에서 추출
        if (!ownerId) {
            const employeeIdEl = document.querySelector('[data-employee-id]');
            ownerId = employeeIdEl?.dataset.employeeId;
            if (ownerId) {
                ownerType = ownerType || 'employee';
            }
        }
    }

    if (!ownerId) {
        // 신규 등록 모드에서는 파일 업로드 비활성화
        disableFileUpload(uploadArea);
        return;
    }

    new FileUpload({
        uploadAreaId: 'fileUploadArea',
        fileListId: 'fileList',
        ownerType: ownerType || 'employee',
        ownerId: parseInt(ownerId, 10),
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
