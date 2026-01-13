/**
 * Employee Detail Page JavaScript
 * - 섹션 네비게이션 (SectionNav 컴포넌트 사용)
 * - 파일 업로드 UI (FileUpload 컴포넌트 사용)
 * - Phase 5.3: 파일 필터링 (FileFilter 컴포넌트 사용)
 * - Phase 5.4: 파일 미리보기 (FilePreview 컴포넌트 사용)
 */

import { SectionNav } from '../../../shared/components/section-nav.js';
import { FileUpload, FileFilter, FilePreview } from '../../../shared/components/file-upload.js';

// 전역 인스턴스 (업로드/삭제 후 새로고침용)
let fileFilter = null;
let filePreview = null;

document.addEventListener('DOMContentLoaded', () => {
    initSectionNavigation();
    initFileUpload();
    initFileFilter();
    initFilePreview();
});

/**
 * 섹션 네비게이션 초기화
 */
function initSectionNavigation() {
    // 사이드바 섹션 네비게이션 초기화 (hr_card 모드)
    const sidebarNav = document.querySelector('.sub-nav');
    if (sidebarNav) {
        const sectionNav = new SectionNav({
            sectionSelector: '.content-section',
            navItemSelector: '.sub-nav__item',  // 사이드바 네비 아이템
            scrollContainerSelector: '.detail-main-content',
            navId: 'sectionNav',
            overlayId: 'sectionNavOverlay',
            toggleBtnId: 'mobileNavToggle',
            scrollOffset: 80,
            rootMargin: '-100px 0px -50% 0px'
        });
        sectionNav.init();
        return;
    }

    // 내부 섹션 네비게이션 초기화 (프로필 모드)
    const internalNav = document.querySelector('.section-nav');
    if (internalNav) {
        const sectionNav = new SectionNav({
            sectionSelector: '.content-section',
            navItemSelector: '.section-nav-item',  // 내부 네비 아이템
            scrollContainerSelector: '.detail-main-content',
            navId: 'sectionNav',
            overlayId: 'sectionNavOverlay',
            toggleBtnId: 'mobileNavToggle',
            scrollOffset: 80,
            rootMargin: '-100px 0px -50% 0px'
        });
        sectionNav.init();
    }
}

/**
 * 파일 업로드 초기화 (FileUpload 컴포넌트 사용)
 * - 템플릿의 data-owner-type/data-owner-id 속성 우선 사용
 * - Fallback: URL 패턴 및 data-employee-id에서 추출
 */
function initFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');
    if (!uploadArea) return;

    // 1. 템플릿에서 설정한 owner_type/owner_id 속성 확인 (SSOT)
    let ownerType = uploadArea.dataset.ownerType;
    let ownerId = uploadArea.dataset.ownerId;

    // 2. Fallback: data-employee-id 속성 또는 URL에서 추출
    if (!ownerId) {
        const employeeIdEl = document.querySelector('[data-employee-id]');
        ownerId = employeeIdEl?.dataset.employeeId;

        if (!ownerId) {
            // URL에서 추출 시도: /employees/123 또는 /employees/123/...
            const match = window.location.pathname.match(/\/employees\/(\d+)/);
            ownerId = match?.[1];
        }

        // fallback인 경우 ownerType도 'employee'로 설정
        if (ownerId && !ownerType) {
            ownerType = 'employee';
        }
    }

    if (!ownerId) {
        console.warn('FileUpload: owner ID를 찾을 수 없습니다.');
        return;
    }

    // FileUpload 컴포넌트 초기화
    new FileUpload({
        uploadAreaId: 'fileUploadArea',
        fileListId: 'fileList',
        ownerType: ownerType || 'employee',
        ownerId: parseInt(ownerId, 10),
        onUploadComplete: (attachment) => {
            console.log('파일 업로드 완료:', attachment);
            // 필터/미리보기 새로고침
            if (fileFilter) fileFilter.refresh();
            if (filePreview) filePreview.refresh();
        },
        onDeleteComplete: (attachmentId) => {
            console.log('파일 삭제 완료:', attachmentId);
            // 필터/미리보기 새로고침
            if (fileFilter) fileFilter.refresh();
            if (filePreview) filePreview.refresh();
        }
    });
}

/**
 * 파일 필터 초기화 (Phase 5.3)
 */
function initFileFilter() {
    const filterBar = document.getElementById('fileFilterBar');
    const fileList = document.getElementById('fileList');

    if (!filterBar || !fileList) return;

    fileFilter = new FileFilter();
}

/**
 * 파일 미리보기 초기화 (Phase 5.4)
 */
function initFilePreview() {
    const modal = document.getElementById('filePreviewModal');
    const fileList = document.getElementById('fileList');

    if (!modal || !fileList) return;

    filePreview = new FilePreview();
}

/**
 * 파일 카드 렌더링
 * @param {File} file - 렌더링할 파일 객체
 * @returns {string} HTML 문자열
 */
function renderFileCard(file) {
    const extension = file.name.split('.').pop().toLowerCase();
    let iconClass = 'fas fa-file';
    let typeClass = '';

    switch (extension) {
        case 'pdf':
            iconClass = 'fas fa-file-pdf';
            typeClass = 'pdf';
            break;
        case 'doc':
        case 'docx':
            iconClass = 'fas fa-file-word';
            typeClass = 'doc';
            break;
        case 'xls':
        case 'xlsx':
            iconClass = 'fas fa-file-excel';
            typeClass = 'xls';
            break;
        case 'jpg':
        case 'jpeg':
        case 'png':
            iconClass = 'fas fa-file-image';
            typeClass = 'img';
            break;
    }

    return `
        <div class="file-card">
            <div class="file-icon ${typeClass}">
                <i class="${iconClass}"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${formatFileSize(file.size)}</div>
            </div>
            <div class="file-actions">
                <button class="file-action-btn" title="다운로드">
                    <i class="fas fa-download"></i>
                </button>
                <button class="file-action-btn" title="삭제">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

/**
 * 파일 크기 포맷
 * @param {number} bytes - 바이트 수
 * @returns {string} 포맷된 파일 크기 문자열
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 직원 삭제 확인 및 처리
 * @param {number} id - 직원 ID
 * @param {string} name - 직원 이름
 */
function deleteEmployee(id, name) {
    if (confirm(`"${name}" 직원을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/employees/${id}/delete`;
        document.body.appendChild(form);
        form.submit();
    }
}

/**
 * 이벤트 위임 - data-action 기반 클릭 핸들러
 */
document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-action]');
    if (!target) return;

    const action = target.dataset.action;

    switch (action) {
        case 'delete-employee':
            const employeeId = target.dataset.employeeId;
            const employeeName = target.dataset.employeeName;
            deleteEmployee(parseInt(employeeId), employeeName);
            break;
    }
});
