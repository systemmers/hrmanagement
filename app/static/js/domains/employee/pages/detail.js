/**
 * Employee Detail Page JavaScript
 * - 섹션 네비게이션 (SectionNav 컴포넌트 사용)
 * - 파일 업로드 UI (FileUpload 컴포넌트 사용)
 * - Phase 5.3: 파일 필터링 (FileFilter 컴포넌트 사용)
 * - Phase 5.4: 파일 미리보기 (FilePreview 컴포넌트 사용)
 * - 명함 QR 코드 (BusinessCard 도메인)
 * - Phase 1: 인라인 편집 시스템 (InlineEditManager)
 */

import { SectionNav } from '../../../shared/components/section-nav.js';
import { FileUpload, FileFilter, FilePreview } from '../../../shared/components/file-upload.js';
import { initBusinessCards } from '../../businesscard/index.js';
import { initInlineEdit, SECTION_CONFIG as INLINE_SECTION_CONFIG } from '../../../shared/components/inline-edit-manager.js';
import { openAddressSearch } from './address-search.js';

// 전역 인스턴스 (업로드/삭제 후 새로고침용)
let fileFilter = null;
let filePreview = null;
let inlineEditManager = null;

document.addEventListener('DOMContentLoaded', () => {
    initSectionNavigation();
    initFileUpload();
    initFileFilter();
    initFilePreview();
    initBusinessCards();  // 명함 QR 코드 초기화
    initInlineEditSystem();  // Phase 1: 인라인 편집 시스템 초기화
});

/**
 * 인라인 편집 시스템 초기화
 * Phase 1: InlineEditManager 통합
 *
 * 지원 계정 타입:
 * - corporate (employee_sub): Employee 모델, /api/employees/{id}/ API 사용
 * - personal: PersonalProfile 모델, /api/profiles/{id}/ API 사용
 * - corporate_admin: CorporateAdminProfile 모델, /api/admin/profile API 사용
 */
function initInlineEditSystem() {
    // 계정 타입 확인
    const layoutEl = document.querySelector('[data-account-type]');
    const accountType = layoutEl?.dataset.accountType;

    let entityId = null;
    let apiBaseUrl = '/api/employees';

    // 계정 타입별 ID 및 API 경로 설정
    if (accountType === 'corporate_admin') {
        // 법인 관리자: admin_profile_id 사용, /api/admin/profile API (섹션 API 없음)
        const adminProfileIdEl = document.querySelector('[data-admin-profile-id]');
        entityId = adminProfileIdEl?.dataset.adminProfileId;

        if (!entityId) {
            console.warn('InlineEditSystem: admin profile ID를 찾을 수 없습니다.');
            return;
        }

        // corporate_admin은 단일 프로필 API 사용 (섹션별 API 없음)
        apiBaseUrl = '/api/admin/profile';
        console.log('InlineEditSystem: corporate_admin 계정 - admin profile API 사용');

    } else if (accountType === 'personal') {
        // 개인 계정: profile_id 사용, /api/profiles API
        const profileIdEl = document.querySelector('[data-profile-id]');
        entityId = profileIdEl?.dataset.profileId;

        if (!entityId) {
            console.warn('InlineEditSystem: profile ID를 찾을 수 없습니다.');
            return;
        }

        apiBaseUrl = '/api/profiles';
        console.log('InlineEditSystem: personal 계정 - profile API 사용');

    } else {
        // 법인 직원: employee_id 사용, /api/employees API
        const employeeIdEl = document.querySelector('[data-employee-id]');
        entityId = employeeIdEl?.dataset.employeeId;

        if (!entityId) {
            const match = window.location.pathname.match(/\/employees\/(\d+)/);
            entityId = match?.[1];
        }

        if (!entityId) {
            console.warn('InlineEditSystem: employee ID를 찾을 수 없습니다.');
            return;
        }

        console.log('InlineEditSystem: corporate 계정 - employee API 사용');
    }

    // InlineEditManager 초기화
    inlineEditManager = initInlineEdit(parseInt(entityId, 10), {
        apiBaseUrl: apiBaseUrl,
        onSave: (sectionId, data) => {
            console.log(`Section ${sectionId} saved:`, data);
            // 필요시 UI 갱신 로직 추가
        },
        onError: (sectionId, error) => {
            console.error(`Section ${sectionId} error:`, error);
        },
        onCancel: (sectionId) => {
            console.log(`Section ${sectionId} cancelled`);
        },
        onStateChange: (sectionId, state, prevState) => {
            console.log(`Section ${sectionId}: ${prevState} -> ${state}`);
        }
    });
}

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
// tableId -> InlineEditManager tableId 매핑 (family-table -> family)
const TABLE_CONFIG = {
    'family-table': { name: '가족정보', hasAttach: false, managerKey: 'family' },
    'education-table': { name: '학력정보', hasAttach: true, managerKey: 'education' },
    'career-table': { name: '경력정보', hasAttach: true, managerKey: 'career' },
    'certificate-table': { name: '자격증', hasAttach: true, managerKey: 'certificate' },
    'language-table': { name: '언어능력', hasAttach: true, managerKey: 'language' },
    'award-table': { name: '수상내역', hasAttach: true, managerKey: 'award' },
    'project-table': { name: '프로젝트 참여', hasAttach: false, managerKey: 'project' },
    'employment-contract-table': { name: '근로계약', hasAttach: true, managerKey: 'employment-contract' },
    'salary-history-table': { name: '연봉계약', hasAttach: true, managerKey: 'salary-history' },
    'salary-payment-table': { name: '급여지급', hasAttach: true, managerKey: 'salary-payment' },
    'promotion-table': { name: '인사이동', hasAttach: true, managerKey: 'promotion' },
    'evaluation-table': { name: '인사고과', hasAttach: false, managerKey: 'evaluation' },
    'training-table': { name: '교육훈련', hasAttach: true, managerKey: 'training' },
    'hr-project-table': { name: '프로젝트', hasAttach: false, managerKey: 'hr-project' },
    'asset-table': { name: '비품지급', hasAttach: false, managerKey: 'asset' }
};

// 테이블별 필드 정의 (모달 폼 생성용)
const TABLE_FIELDS = {
    'family': [
        { name: 'relation', label: '관계', type: 'select', options: [
            { value: '배우자', label: '배우자' },
            { value: '자녀', label: '자녀' },
            { value: '부', label: '부' },
            { value: '모', label: '모' },
            { value: '형제자매', label: '형제자매' }
        ], required: true },
        { name: 'name', label: '성명', type: 'text', required: true },
        { name: 'birth_date', label: '생년월일', type: 'date' },
        { name: 'occupation', label: '직업', type: 'text' },
        { name: 'company', label: '직장명', type: 'text' },
        { name: 'contact', label: '연락처', type: 'text' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'education': [
        { name: 'degree', label: '학력구분', type: 'select', options: [
            { value: '고등학교', label: '고등학교' },
            { value: '전문학사', label: '전문학사' },
            { value: '학사', label: '학사' },
            { value: '석사', label: '석사' },
            { value: '박사', label: '박사' }
        ], required: true },
        { name: 'school_name', label: '학교명', type: 'text', required: true },
        { name: 'major', label: '전공', type: 'text' },
        { name: 'graduation_date', label: '졸업년월', type: 'month' },
        { name: 'gpa', label: '학점', type: 'text' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'career': [
        { name: 'company_name', label: '회사명', type: 'text', required: true },
        { name: 'department', label: '부서', type: 'text' },
        { name: 'position', label: '직위', type: 'text' },
        { name: 'job_grade', label: '직급', type: 'text' },
        { name: 'job_title', label: '직책', type: 'text' },
        { name: 'job_role', label: '직무', type: 'text' },
        { name: 'start_date', label: '입사일', type: 'date', required: true },
        { name: 'end_date', label: '퇴사일', type: 'date' },
        { name: 'salary_type', label: '급여유형', type: 'select', options: [
            { value: '연봉제', label: '연봉제' },
            { value: '월급제', label: '월급제' },
            { value: '시급제', label: '시급제' }
        ]},
        { name: 'salary', label: '연봉', type: 'number' },
        { name: 'job_description', label: '담당업무', type: 'textarea' }
    ],
    'certificate': [
        { name: 'certificate_name', label: '자격증명', type: 'text', required: true },
        { name: 'grade', label: '등급/점수', type: 'text' },
        { name: 'issuing_organization', label: '발행처', type: 'text' },
        { name: 'acquisition_date', label: '취득일', type: 'date' },
        { name: 'expiry_date', label: '만료일', type: 'date' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'language': [
        { name: 'language_name', label: '언어', type: 'text', required: true },
        { name: 'level', label: '수준', type: 'select', options: [
            { value: '원어민', label: '원어민' },
            { value: '상', label: '상' },
            { value: '중', label: '중' },
            { value: '하', label: '하' }
        ]},
        { name: 'exam_name', label: '시험명', type: 'text' },
        { name: 'score', label: '점수', type: 'text' },
        { name: 'acquisition_date', label: '취득일', type: 'date' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'award': [
        { name: 'award_name', label: '수상명', type: 'text', required: true },
        { name: 'institution', label: '수여기관', type: 'text' },
        { name: 'award_date', label: '수상일', type: 'date' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'project': [
        { name: 'project_name', label: '프로젝트명', type: 'text', required: true },
        { name: 'client', label: '고객사', type: 'text' },
        { name: 'start_date', label: '시작일', type: 'date' },
        { name: 'end_date', label: '종료일', type: 'date' },
        { name: 'role', label: '담당역할', type: 'text' },
        { name: 'duty', label: '수행업무', type: 'textarea' }
    ],
    'employment-contract': [
        { name: 'contract_date', label: '계약일', type: 'date', required: true },
        { name: 'contract_type', label: '계약구분', type: 'select', options: [
            { value: '정규직', label: '정규직' },
            { value: '계약직', label: '계약직' },
            { value: '파견직', label: '파견직' },
            { value: '인턴', label: '인턴' }
        ]},
        { name: 'start_date', label: '계약기간 시작', type: 'date' },
        { name: 'end_date', label: '계약기간 종료', type: 'date' },
        { name: 'employee_type', label: '직원구분', type: 'text' },
        { name: 'work_type', label: '근무형태', type: 'select', options: [
            { value: '전일제', label: '전일제' },
            { value: '시간제', label: '시간제' },
            { value: '교대제', label: '교대제' }
        ]},
        { name: 'note', label: '비고', type: 'text' }
    ],
    'salary-history': [
        { name: 'contract_year', label: '계약년도', type: 'text', required: true },
        { name: 'annual_salary', label: '연봉', type: 'number' },
        { name: 'bonus', label: '상여', type: 'number' },
        { name: 'total_amount', label: '총액', type: 'number' },
        { name: 'contract_period', label: '계약기간', type: 'text' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'salary-payment': [
        { name: 'payment_date', label: '지급일', type: 'date', required: true },
        { name: 'payment_period', label: '지급기간', type: 'text' },
        { name: 'base_salary', label: '기본급', type: 'number' },
        { name: 'allowances', label: '수당', type: 'number' },
        { name: 'gross_pay', label: '총지급액', type: 'number' },
        { name: 'insurance', label: '4대보험', type: 'number' },
        { name: 'income_tax', label: '소득세', type: 'number' },
        { name: 'total_deduction', label: '공제합계', type: 'number' },
        { name: 'net_pay', label: '실지급액', type: 'number' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'promotion': [
        { name: 'effective_date', label: '발령일', type: 'date', required: true },
        { name: 'promotion_type', label: '발령유형', type: 'select', options: [
            { value: '승진', label: '승진' },
            { value: '전보', label: '전보' },
            { value: '전출', label: '전출' },
            { value: '전입', label: '전입' }
        ]},
        { name: 'from_department', label: '이전부서', type: 'text' },
        { name: 'to_department', label: '발령부서', type: 'text' },
        { name: 'from_position', label: '이전직위', type: 'text' },
        { name: 'to_position', label: '발령직위', type: 'text' },
        { name: 'reason', label: '발령사유', type: 'text' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'evaluation': [
        { name: 'year', label: '평가년도', type: 'text', required: true },
        { name: 'q1_grade', label: '1분기', type: 'text' },
        { name: 'q2_grade', label: '2분기', type: 'text' },
        { name: 'q3_grade', label: '3분기', type: 'text' },
        { name: 'q4_grade', label: '4분기', type: 'text' },
        { name: 'overall_grade', label: '종합', type: 'text' },
        { name: 'note', label: '비고', type: 'text' }
    ],
    'training': [
        { name: 'training_name', label: '교육명', type: 'text', required: true },
        { name: 'institution', label: '교육기관', type: 'text' },
        { name: 'training_date', label: '교육일', type: 'date' },
        { name: 'hours', label: '교육시간', type: 'number' },
        { name: 'completion_status', label: '이수상태', type: 'select', options: [
            { value: '이수', label: '이수' },
            { value: '미이수', label: '미이수' },
            { value: '진행중', label: '진행중' }
        ]},
        { name: 'note', label: '비고', type: 'text' }
    ],
    'hr-project': [
        { name: 'project_name', label: '프로젝트명', type: 'text', required: true },
        { name: 'start_date', label: '시작일', type: 'date' },
        { name: 'end_date', label: '종료일', type: 'date' },
        { name: 'duration', label: '기간', type: 'text' },
        { name: 'duty', label: '담당업무', type: 'text' },
        { name: 'role', label: '역할', type: 'text' },
        { name: 'client', label: '고객사', type: 'text' }
    ],
    'asset': [
        { name: 'item_name', label: '품목명', type: 'text', required: true },
        { name: 'model', label: '모델', type: 'text' },
        { name: 'serial_number', label: '시리얼번호', type: 'text' },
        { name: 'issue_date', label: '지급일', type: 'date' },
        { name: 'status', label: '상태', type: 'select', options: [
            { value: '사용중', label: '사용중' },
            { value: '반납', label: '반납' },
            { value: '분실', label: '분실' }
        ]},
        { name: 'note', label: '비고', type: 'text' }
    ]
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
        const row = btn.closest('tr');
        const table = btn.closest('[data-draggable]');
        const config = TABLE_CONFIG[table?.id];

        if (!config) return;

        switch (action) {
            case 'edit':
                handleRowEdit(id, config, row, table);
                break;
            case 'attach':
                handleRowAttach(id, config);
                break;
            case 'delete':
                handleRowDelete(id, config, row, table);
                break;
        }
    });
}

/**
 * 섹션 수정 핸들러
 * Phase 1: InlineEditManager를 통한 인라인 편집
 */
function handleSectionEdit(btnId, config) {
    // btnId에서 section 이름 추출 (btn-edit-personal -> personal)
    const sectionId = btnId.replace('btn-edit-', '');

    // InlineEditManager가 지원하는 섹션인지 확인
    if (inlineEditManager && INLINE_SECTION_CONFIG[sectionId]) {
        inlineEditManager.editSection(sectionId);
    } else {
        showToast(`${config.name} 수정 기능 준비 중`, 'info');
    }
}

/**
 * 섹션 추가 핸들러
 * Phase 8: 모달을 통한 새 항목 추가
 * @param {string} btnId - 버튼 ID
 * @param {Object} config - 섹션 설정
 */
function handleSectionAdd(btnId, config) {
    if (!inlineEditManager) {
        showToast('편집 시스템이 초기화되지 않았습니다.', 'error');
        return;
    }

    // btnId에서 managerKey 추출 (btn-add-education -> education)
    const managerKey = btnId.replace('btn-add-', '');
    const fields = TABLE_FIELDS[managerKey];

    if (!fields) {
        showToast(`${config.name} 필드 정의가 없습니다.`, 'warning');
        return;
    }

    // 모달 열기
    openRowEditModal({
        title: `${config.name} 추가`,
        fields: fields,
        data: {},  // 빈 데이터
        onSave: async (formData) => {
            const result = await inlineEditManager.addRow(managerKey, formData);
            if (result) {
                // 성공 시 페이지 새로고침 (DOM 구조 일관성 유지)
                closeRowEditModal();
                window.location.reload();
            }
        }
    });
}


/**
 * 행 수정 핸들러
 * Phase 8: 모달을 통한 인라인 편집
 * @param {string} id - 항목 ID
 * @param {Object} config - 테이블 설정
 * @param {HTMLElement} row - 테이블 행 요소
 * @param {HTMLElement} table - 테이블 요소
 */
async function handleRowEdit(id, config, row, table) {
    if (!inlineEditManager) {
        showToast('편집 시스템이 초기화되지 않았습니다.', 'error');
        return;
    }

    const fields = TABLE_FIELDS[config.managerKey];
    if (!fields) {
        showToast(`${config.name} 필드 정의가 없습니다.`, 'warning');
        return;
    }

    // API에서 기존 데이터 조회
    showToast('데이터를 불러오는 중...', 'info');
    const existingData = await fetchRowData(config.managerKey, parseInt(id, 10));

    if (!existingData) {
        showToast('데이터를 불러오는 데 실패했습니다.', 'error');
        return;
    }

    // 모달 열기
    openRowEditModal({
        title: `${config.name} 수정`,
        fields: fields,
        data: existingData,
        onSave: async (formData) => {
            const result = await inlineEditManager.updateRow(config.managerKey, parseInt(id, 10), formData);
            if (result) {
                // 성공 시 페이지 새로고침 (간단한 방법)
                // 추후 DOM 직접 업데이트로 개선 가능
                closeRowEditModal();
                window.location.reload();
            }
        }
    });
}

/**
 * API에서 행 데이터 조회
 * @param {string} tableKey - 테이블 키 (family, education 등)
 * @param {number} itemId - 항목 ID
 * @returns {Promise<Object|null>} 데이터 또는 null
 */
async function fetchRowData(tableKey, itemId) {
    try {
        // tableKey -> apiPath 매핑 (TABLE_FIELDS 키와 동일한 패턴)
        const apiPathMap = {
            'family': 'families',
            'education': 'educations',
            'career': 'careers',
            'certificate': 'certificates',
            'language': 'languages',
            'award': 'awards',
            'project': 'projects',
            'employment-contract': 'employment-contracts',
            'salary-history': 'salary-histories',
            'salary-payment': 'salary-payments',
            'promotion': 'promotions',
            'evaluation': 'evaluations',
            'training': 'trainings',
            'hr-project': 'hr-projects',
            'asset': 'assets'
        };

        const apiPath = apiPathMap[tableKey];
        if (!apiPath) return null;

        const employeeId = getEmployeeId();
        if (!employeeId) return null;

        const response = await fetch(`/api/employees/${employeeId}/${apiPath}/${itemId}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) return null;

        const result = await response.json();
        return result.success ? result.data : null;

    } catch (error) {
        console.error('fetchRowData error:', error);
        return null;
    }
}

/**
 * 현재 직원 ID 조회
 * @returns {number|null}
 */
function getEmployeeId() {
    const el = document.querySelector('[data-employee-id]');
    if (el) return parseInt(el.dataset.employeeId, 10);

    const match = window.location.pathname.match(/\/employees\/(\d+)/);
    return match ? parseInt(match[1], 10) : null;
}


/**
 * 행 첨부파일 핸들러
 */
function handleRowAttach(id, config) {
    showToast(`${config.name} 첨부파일 기능 준비 중`, 'info');
}

/**
 * 행 삭제 핸들러
 * Phase 8: InlineEditManager를 통한 API 삭제
 * @param {string} id - 항목 ID
 * @param {Object} config - 테이블 설정
 * @param {HTMLElement} row - 테이블 행 요소
 * @param {HTMLElement} table - 테이블 요소
 */
async function handleRowDelete(id, config, row, table) {
    if (!inlineEditManager) {
        showToast('편집 시스템이 초기화되지 않았습니다.', 'error');
        return;
    }

    // InlineEditManager의 deleteRow 호출 (confirm 포함)
    const success = await inlineEditManager.deleteRow(config.managerKey, parseInt(id, 10));

    if (success && row) {
        // DOM에서 행 제거 (fade out 애니메이션)
        row.style.transition = 'opacity 0.3s ease';
        row.style.opacity = '0';
        setTimeout(() => {
            row.remove();
            // 빈 테이블 체크 및 empty state 표시
            updateEmptyState(table);
        }, 300);
    }
}

/**
 * 테이블 빈 상태 업데이트
 * @param {HTMLElement} table - 테이블 요소
 */
function updateEmptyState(table) {
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const rows = tbody?.querySelectorAll('tr:not(.data-table__empty-row)');

    if (!rows || rows.length === 0) {
        // 기존 empty row가 없으면 추가
        const existingEmpty = tbody?.querySelector('.data-table__empty-row');
        if (!existingEmpty) {
            const colCount = table.querySelectorAll('thead th').length || 5;
            const emptyRow = document.createElement('tr');
            emptyRow.className = 'data-table__empty-row';
            emptyRow.innerHTML = `<td colspan="${colCount}" class="data-table__empty">등록된 정보가 없습니다.</td>`;
            tbody?.appendChild(emptyRow);
        }
    }
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

// ========================================
// 행 편집 모달 시스템
// ========================================

let currentModal = null;
let currentModalCallback = null;

/**
 * 행 편집 모달 열기
 * @param {Object} options - 모달 옵션
 * @param {string} options.title - 모달 제목
 * @param {Array} options.fields - 필드 정의
 * @param {Object} options.data - 기존 데이터
 * @param {Function} options.onSave - 저장 콜백
 */
function openRowEditModal(options) {
    const { title, fields, data, onSave } = options;

    // 기존 모달 제거
    closeRowEditModal();

    // 모달 HTML 생성
    const modalHtml = createRowEditModalHtml(title, fields, data);

    // 모달 삽입
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    currentModal = document.getElementById('rowEditModal');
    currentModalCallback = onSave;

    // 모달 표시 (애니메이션용 딜레이)
    setTimeout(() => {
        currentModal.classList.add('show');
    }, 10);

    // 이벤트 바인딩
    bindModalEvents();

    // 첫 번째 입력 필드에 포커스
    const firstInput = currentModal.querySelector('input, select, textarea');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }
}

/**
 * 행 편집 모달 닫기
 */
function closeRowEditModal() {
    if (currentModal) {
        currentModal.classList.remove('show');
        setTimeout(() => {
            currentModal.remove();
            currentModal = null;
            currentModalCallback = null;
        }, 300);
    }
}

/**
 * 모달 HTML 생성
 * @param {string} title - 모달 제목
 * @param {Array} fields - 필드 정의
 * @param {Object} data - 기존 데이터
 * @returns {string} HTML 문자열
 */
function createRowEditModalHtml(title, fields, data) {
    const fieldsHtml = fields.map(field => createFieldHtml(field, data[field.name])).join('');

    return `
        <div id="rowEditModal" class="modal">
            <div class="modal__backdrop" data-action="close-modal"></div>
            <div class="modal__container modal__container--md">
                <div class="modal__header">
                    <h3 class="modal__title">${title}</h3>
                    <button type="button" class="modal__close" data-action="close-modal">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form id="rowEditForm" class="modal__body">
                    <div class="form-grid">
                        ${fieldsHtml}
                    </div>
                </form>
                <div class="modal__footer">
                    <button type="button" class="btn btn--outline" data-action="close-modal">취소</button>
                    <button type="button" class="btn btn--primary" data-action="save-modal">저장</button>
                </div>
            </div>
        </div>
    `;
}

/**
 * 필드 HTML 생성
 * @param {Object} field - 필드 정의
 * @param {*} value - 현재 값
 * @returns {string} HTML 문자열
 */
function createFieldHtml(field, value) {
    const required = field.required ? 'required' : '';
    const requiredMark = field.required ? '<span class="form-required">*</span>' : '';
    const valueAttr = value || '';

    let inputHtml = '';

    switch (field.type) {
        case 'select':
            const optionsHtml = (field.options || []).map(opt =>
                `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
            ).join('');
            inputHtml = `
                <select name="${field.name}" class="form-input" ${required}>
                    <option value="">선택하세요</option>
                    ${optionsHtml}
                </select>
            `;
            break;

        case 'textarea':
            inputHtml = `
                <textarea name="${field.name}" class="form-input form-textarea" rows="3" ${required}>${valueAttr}</textarea>
            `;
            break;

        case 'date':
            inputHtml = `
                <input type="date" name="${field.name}" class="form-input" value="${valueAttr}" ${required}>
            `;
            break;

        case 'month':
            inputHtml = `
                <input type="month" name="${field.name}" class="form-input" value="${valueAttr}" ${required}>
            `;
            break;

        case 'number':
            inputHtml = `
                <input type="number" name="${field.name}" class="form-input" value="${valueAttr}" ${required}>
            `;
            break;

        default:
            inputHtml = `
                <input type="text" name="${field.name}" class="form-input" value="${valueAttr}" ${required}>
            `;
    }

    return `
        <div class="form-group">
            <label class="form-label">${field.label}${requiredMark}</label>
            ${inputHtml}
        </div>
    `;
}

/**
 * 모달 이벤트 바인딩
 */
function bindModalEvents() {
    if (!currentModal) return;

    // 닫기 버튼 및 배경 클릭
    currentModal.addEventListener('click', (e) => {
        if (e.target.closest('[data-action="close-modal"]')) {
            closeRowEditModal();
        }
    });

    // 저장 버튼
    currentModal.addEventListener('click', async (e) => {
        if (e.target.closest('[data-action="save-modal"]')) {
            await handleModalSave();
        }
    });

    // ESC 키로 닫기
    document.addEventListener('keydown', handleModalKeydown);

    // 폼 제출 (Enter 키)
    const form = currentModal.querySelector('#rowEditForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleModalSave();
        });
    }
}

/**
 * 모달 저장 처리
 */
async function handleModalSave() {
    if (!currentModal || !currentModalCallback) return;

    const form = currentModal.querySelector('#rowEditForm');
    if (!form) return;

    // 유효성 검사
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // 폼 데이터 수집
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    // 저장 버튼 비활성화
    const saveBtn = currentModal.querySelector('[data-action="save-modal"]');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 저장 중...';
    }

    try {
        await currentModalCallback(data);
    } finally {
        // 버튼 복원
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '저장';
        }
    }
}

/**
 * 모달 키보드 이벤트 핸들러
 */
function handleModalKeydown(e) {
    if (e.key === 'Escape' && currentModal) {
        closeRowEditModal();
        document.removeEventListener('keydown', handleModalKeydown);
    }
}

// HR Card 액션 버튼 초기화
document.addEventListener('DOMContentLoaded', () => {
    initHeaderActions();
    initTableActions();
    initAddressSearchInline();
    initOrganizationSelectorInline();
});

/**
 * 인라인 편집 - 주소 검색 버튼 초기화
 * 기존 address-search.js의 openAddressSearch 재사용
 */
function initAddressSearchInline() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-address-search]');
        if (!btn) return;

        const fieldName = btn.dataset.addressSearch;
        const container = btn.closest('.inline-edit--address');
        if (!container) return;

        const addressInput = container.querySelector(`input[name="${fieldName}"]`);
        const detailInput = container.querySelector('.inline-edit__detail-input');

        // 우편번호 필드 찾기 (같은 섹션 내)
        const section = btn.closest('[data-section]');
        const postalCodeInput = section?.querySelector('input[name="postal_code"]');

        // 기존 모듈의 openAddressSearch 재사용
        openAddressSearch(addressInput, detailInput, postalCodeInput);
    });
}

/**
 * 인라인 편집 - 조직 트리 선택기 초기화
 */
function initOrganizationSelectorInline() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-org-selector]');
        if (!btn) return;

        const fieldName = btn.dataset.orgSelector;
        const container = btn.closest('.inline-edit--organization');
        if (!container) return;

        const displayInput = container.querySelector('.inline-edit__org-display');
        const hiddenInput = container.querySelector('.inline-edit__org-id');

        openOrganizationSelector(displayInput, hiddenInput);
    });

    // 조직 표시 필드 클릭 시에도 선택기 열기
    document.addEventListener('click', (e) => {
        const input = e.target.closest('.inline-edit__org-display');
        if (!input) return;

        const container = input.closest('.inline-edit--organization');
        if (!container) return;

        // 편집 모드일 때만 작동
        const section = container.closest('.info-section--editing');
        if (!section) return;

        const btn = container.querySelector('[data-org-selector]');
        if (btn) btn.click();
    });
}

// TreeSelector 인스턴스 캐시 (비동기 초기화 처리)
let orgTreeSelectorInstance = null;

/**
 * 조직 선택기 모달 열기
 * 기존 index.js의 window.TreeSelector 패턴 재사용
 */
function openOrganizationSelector(displayInput, hiddenInput) {
    if (typeof window.TreeSelector === 'undefined') {
        showToast('조직 선택기를 불러오는 중입니다. 잠시 후 다시 시도해 주세요.', 'info');
        return;
    }

    const displayId = displayInput?.id;
    const hiddenId = hiddenInput?.id;

    if (!displayId || !hiddenId) {
        console.error('Organization selector: Missing input IDs', { displayId, hiddenId });
        showToast('조직 선택기 설정 오류', 'error');
        return;
    }

    // TreeSelector 인스턴스가 없거나 다른 필드용이면 새로 생성
    if (!orgTreeSelectorInstance || orgTreeSelectorInstance.inputId !== displayId) {
        orgTreeSelectorInstance = new window.TreeSelector({
            inputId: displayId,
            hiddenInputId: hiddenId,
            modalId: 'inlineOrgTreeSelectorModal',
            apiUrl: '/admin/api/organizations?format=tree',
            allowEmpty: true,
            onSelect: (selected) => {
                if (displayInput && selected) {
                    displayInput.value = selected.name || selected.text;
                    displayInput.classList.add('inline-edit__input--dirty');
                }
                if (hiddenInput && selected) {
                    hiddenInput.value = selected.id;
                    hiddenInput.classList.add('inline-edit__input--dirty');
                }
            }
        });

        // TreeSelector의 비동기 init() 완료 후 모달 열기
        // 모달이 생성될 때까지 폴링 (최대 2초)
        const waitForModal = (retries = 20) => {
            if (orgTreeSelectorInstance?.modal) {
                orgTreeSelectorInstance.open();
            } else if (retries > 0) {
                setTimeout(() => waitForModal(retries - 1), 100);
            } else {
                console.warn('TreeSelector modal not created in time');
                showToast('조직 정보를 불러오는 중입니다. 다시 시도해 주세요.', 'info');
            }
        };
        waitForModal();
    } else {
        // 기존 인스턴스 재사용 - 바로 열기
        orgTreeSelectorInstance.open();
    }
}
