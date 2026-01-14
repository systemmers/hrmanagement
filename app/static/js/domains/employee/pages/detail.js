/**
 * Employee Detail Page JavaScript
 * - 섹션 네비게이션 (SectionNav 컴포넌트 사용)
 * - 파일 업로드 UI (FileUpload 컴포넌트 사용)
 * - Phase 5.3: 파일 필터링 (FileFilter 컴포넌트 사용)
 * - Phase 5.4: 파일 미리보기 (FilePreview 컴포넌트 사용)
 * - 명함 QR 코드 (BusinessCard 도메인)
 */

import { SectionNav } from '../../../shared/components/section-nav.js';
import { FileUpload, FileFilter, FilePreview } from '../../../shared/components/file-upload.js';
import { initBusinessCards } from '../../businesscard/index.js';

// 전역 인스턴스 (업로드/삭제 후 새로고침용)
let fileFilter = null;
let filePreview = null;

document.addEventListener('DOMContentLoaded', () => {
    initSectionNavigation();
    initFileUpload();
    initFileFilter();
    initFilePreview();
    initBusinessCards();  // 명함 QR 코드 초기화
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
            // 필터/미리보기 새로고침
            if (fileFilter) fileFilter.refresh();
            if (filePreview) filePreview.refresh();
        },
        onDeleteComplete: (attachmentId) => {
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
 * 파일 크기 포맷 (SSOT: window.HRFormatters.formatFileSize)
 */
function formatFileSize(bytes) {
    return window.HRFormatters?.formatFileSize?.(bytes) || '0 Bytes';
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

/**
 * HR Card 액션 버튼 이벤트 핸들러
 */

// 섹션 설정 (23개 섹션)
const SECTION_CONFIG = {
    // info-table 섹션 (수정 버튼)
    'btn-edit-personal': { name: '개인 기본정보', action: 'edit' },
    'btn-edit-organization': { name: '소속정보', action: 'edit' },
    'btn-edit-contract': { name: '계약정보', action: 'edit' },
    'btn-edit-salary': { name: '급여정보', action: 'edit' },
    'btn-edit-benefit': { name: '연차 및 복리후생', action: 'edit' },
    'btn-edit-military': { name: '병역정보', action: 'edit' },
    'btn-edit-attendance': { name: '근태현황', action: 'edit' },
    'btn-edit-account': { name: '계정정보', action: 'edit' },
    // data-table 섹션 (추가 버튼)
    'btn-add-family': { name: '가족정보', action: 'add' },
    'btn-add-education': { name: '학력정보', action: 'add' },
    'btn-add-career': { name: '경력정보', action: 'add' },
    'btn-add-certificate': { name: '자격증', action: 'add' },
    'btn-add-language': { name: '언어능력', action: 'add' },
    'btn-add-award': { name: '수상내역', action: 'add' },
    'btn-add-project': { name: '프로젝트 참여', action: 'add' },
    'btn-add-employment-contract': { name: '근로계약', action: 'add' },
    'btn-add-salary-history': { name: '연봉계약', action: 'add' },
    'btn-add-salary-payment': { name: '급여지급', action: 'add' },
    'btn-add-promotion': { name: '인사이동', action: 'add' },
    'btn-add-evaluation': { name: '인사고과', action: 'add' },
    'btn-add-training': { name: '교육훈련', action: 'add' },
    'btn-add-hr-project': { name: '프로젝트', action: 'add' },
    'btn-add-asset': { name: '비품지급', action: 'add' }
};

// 테이블 설정 (15개 테이블)
const TABLE_CONFIG = {
    'family-table': { name: '가족정보', hasAttach: false },
    'education-table': { name: '학력정보', hasAttach: true },
    'career-table': { name: '경력정보', hasAttach: true },
    'certificate-table': { name: '자격증', hasAttach: true },
    'language-table': { name: '언어능력', hasAttach: true },
    'award-table': { name: '수상내역', hasAttach: true },
    'project-table': { name: '프로젝트 참여', hasAttach: false },
    'employment-contract-table': { name: '근로계약', hasAttach: true },
    'salary-history-table': { name: '연봉계약', hasAttach: true },
    'salary-payment-table': { name: '급여지급', hasAttach: true },
    'promotion-table': { name: '인사이동', hasAttach: true },
    'evaluation-table': { name: '인사고과', hasAttach: false },
    'training-table': { name: '교육훈련', hasAttach: true },
    'hr-project-table': { name: '프로젝트', hasAttach: false },
    'asset-table': { name: '비품지급', hasAttach: false }
};

/**
 * 헤더 액션 버튼 초기화
 */
function initHeaderActions() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.info-section__add-btn');
        if (!btn) return;

        const config = SECTION_CONFIG[btn.id];
        if (!config) return;

        if (config.action === 'edit') {
            handleSectionEdit(btn.id, config);
        } else {
            handleSectionAdd(btn.id, config);
        }
    });
}

/**
 * 테이블 액션 버튼 초기화
 */
function initTableActions() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.data-table__btn-icon');
        if (!btn) return;

        const action = btn.dataset.action;
        const id = btn.dataset.id;
        const table = btn.closest('[data-draggable]');
        const config = TABLE_CONFIG[table?.id];

        if (!config) return;

        switch (action) {
            case 'edit':
                handleRowEdit(id, config);
                break;
            case 'attach':
                handleRowAttach(id, config);
                break;
            case 'delete':
                handleRowDelete(id, config);
                break;
        }
    });
}

/**
 * 섹션 수정 핸들러
 */
function handleSectionEdit(btnId, config) {
    showToast(`${config.name} 수정 기능 준비 중`, 'info');
}

/**
 * 섹션 추가 핸들러
 */
function handleSectionAdd(btnId, config) {
    showToast(`${config.name} 추가 기능 준비 중`, 'info');
}

/**
 * 행 수정 핸들러
 */
function handleRowEdit(id, config) {
    showToast(`${config.name} 항목 수정 준비 중`, 'info');
}

/**
 * 행 첨부파일 핸들러
 */
function handleRowAttach(id, config) {
    showToast(`${config.name} 첨부파일 기능 준비 중`, 'info');
}

/**
 * 행 삭제 핸들러
 */
function handleRowDelete(id, config) {
    if (!confirm(`${config.name} 항목을 삭제하시겠습니까?`)) return;
    showToast(`${config.name} 삭제 기능 준비 중`, 'info');
}

/**
 * 토스트 메시지 표시 헬퍼
 */
function showToast(message, type = 'info') {
    if (window.Toast) {
        window.Toast.show(message, type);
    } else if (window.HRApp?.toast?.show) {
        window.HRApp.toast.show(message, type);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// HR Card 액션 버튼 초기화
document.addEventListener('DOMContentLoaded', () => {
    initHeaderActions();
    initTableActions();
});
