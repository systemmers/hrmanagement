/**
 * File Upload Initialization Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 * Phase 5.3: 파일 필터링 기능 추가
 * Phase 5.4: 파일 미리보기 기능 추가
 *
 * 첨부파일 업로드, 필터링, 미리보기 초기화
 * - 템플릿의 data-owner-type/data-owner-id 속성 우선 사용
 * - Fallback: URL 패턴에서 추출
 */

import { FileUpload, FileFilter, FilePreview } from '../../../shared/components/file-upload.js';

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

    // 파일 필터/미리보기 인스턴스 (업로드 완료 시 새로고침 용도)
    let fileFilter = null;
    let filePreview = null;

    // 필터 초기화 (파일이 있는 경우만)
    const filterBar = document.getElementById('fileFilterBar');
    if (filterBar) {
        fileFilter = new FileFilter();
    }

    // 미리보기 초기화 (Phase 5.4)
    const previewModal = document.getElementById('filePreviewModal');
    if (previewModal) {
        filePreview = new FilePreview();
    }

    new FileUpload({
        uploadAreaId: 'fileUploadArea',
        fileListId: 'fileList',
        ownerType: ownerType || 'employee',
        ownerId: parseInt(ownerId, 10),
        onUploadComplete: (attachment) => {
            // 업로드 완료 후 필터/미리보기 새로고침
            if (fileFilter) fileFilter.refresh();
            if (filePreview) filePreview.refresh();
        },
        onDeleteComplete: (attachmentId) => {
            // 삭제 완료 후 필터/미리보기 새로고침
            if (fileFilter) fileFilter.refresh();
            if (filePreview) filePreview.refresh();
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

/**
 * 파일 필터만 초기화 (이미 파일이 로드된 경우)
 * @returns {FileFilter|null}
 */
export function initFileFilter() {
    const filterBar = document.getElementById('fileFilterBar');
    const fileList = document.getElementById('fileList');

    if (!filterBar || !fileList) return null;

    return new FileFilter();
}

/**
 * 파일 미리보기만 초기화 (Phase 5.4)
 * @returns {FilePreview|null}
 */
export function initFilePreview() {
    const previewModal = document.getElementById('filePreviewModal');
    const fileList = document.getElementById('fileList');

    if (!previewModal || !fileList) return null;

    return new FilePreview();
}

export default {
    initFileUpload,
    initFileFilter,
    initFilePreview
};
