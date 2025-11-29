/**
 * Employee Detail Page JavaScript
 * - 섹션 네비게이션 (SectionNav 컴포넌트 사용)
 * - 파일 업로드 UI
 */

import { SectionNav } from '../components/section-nav.js';

document.addEventListener('DOMContentLoaded', () => {
    initSectionNavigation();
    initFileUpload();
});

/**
 * 섹션 네비게이션 초기화
 */
function initSectionNavigation() {
    const sectionNav = new SectionNav({
        sectionSelector: '.content-section',
        navItemSelector: '.section-nav-item',
        scrollContainerSelector: '.detail-main-content',
        navId: 'sectionNav',
        overlayId: 'sectionNavOverlay',
        toggleBtnId: 'mobileNavToggle',
        scrollOffset: 80,
        rootMargin: '-100px 0px -50% 0px'
    });

    sectionNav.init();
}

/**
 * 파일 업로드 UI
 */
function initFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');

    if (!uploadArea) return;

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files);
        }
    });

    uploadArea.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png';

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files);
            }
        });

        input.click();
    });
}

/**
 * 파일 업로드 처리
 * @param {FileList} files - 업로드할 파일 목록
 */
function handleFileUpload(files) {
    console.log('Files to upload:', files);
    alert(`${files.length}개의 파일이 선택되었습니다.\n파일 업로드 기능은 향후 구현 예정입니다.`);
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
