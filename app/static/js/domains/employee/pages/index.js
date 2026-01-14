/**
 * Employee Form Module Index
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 직원 폼 관련 모든 모듈을 하나의 진입점에서 초기화 및 내보냅니다.
 */

// 모듈 imports
import { initSectionNavigation } from './section-nav-init.js';
import { initDynamicFields, addDynamicItem } from './dynamic-sections.js';
import { initPhotoPreview, initProfilePhotoUpload } from './photo-upload.js';
import { initBusinessCardUpload } from './business-card.js';
import { initFormValidation, validateField, validateForm } from './validators.js';
import { initAddressSearch } from './address-search.js';
import { initFileUpload } from './file-upload-init.js';
import { getEmployeeIdFromForm, showToast, validateImageFile } from './helpers.js';
import { initAccountSection, validateAccountFields } from './account-section.js';
import { EvidenceAttachmentManager } from '../../../shared/components/evidence-attachment.js';

// 템플릿 re-export
export {
    getEducationTemplate,
    getCareerTemplate,
    getCertificateTemplate,
    getFamilyTemplate,
    getLanguageTemplate,
    getProjectTemplate,
    getAwardTemplate
} from './templates.js';

// 함수 re-export
export {
    initSectionNavigation,
    initDynamicFields,
    addDynamicItem,
    initPhotoPreview,
    initProfilePhotoUpload,
    initBusinessCardUpload,
    initFormValidation,
    validateField,
    validateForm,
    initAddressSearch,
    initFileUpload,
    getEmployeeIdFromForm,
    showToast,
    validateImageFile,
    initAccountSection,
    validateAccountFields
};

/**
 * 조직 트리 선택기 초기화
 * TreeSelector 컴포넌트를 사용하여 조직 선택 UI 구성
 */
export function initTreeSelector() {
    const organizationDisplay = document.getElementById('organization_display');
    if (!organizationDisplay || typeof window.TreeSelector === 'undefined') {
        return;
    }

    new window.TreeSelector({
        inputId: 'organization_display',
        hiddenInputId: 'organization_id',
        modalId: 'orgTreeSelectorModal',
        apiUrl: '/admin/api/organizations?format=tree',
        allowEmpty: true,
        onSelect: function(selected) {
            // 선택 완료 - 필요시 추가 처리 가능
        }
    });
}

/**
 * 직원 폼 전체 초기화
 * 모든 모듈을 순서대로 초기화합니다.
 */
export function initEmployeeForm() {
    initSectionNavigation();
    initDynamicFields();
    initPhotoPreview();
    initProfilePhotoUpload();
    initBusinessCardUpload();
    initFormValidation();
    initAddressSearch();
    initFileUpload();
    initTreeSelector();
    initAccountSection();  // 21번/22번 원칙: 계정 섹션 초기화
    initEvidenceAttachments();  // Phase 5.2: 증빙 서류 연동
}

/**
 * 증빙 서류 첨부 초기화
 * Phase 5.2: 항목별 증빙 서류 연동 UI
 */
export function initEvidenceAttachments() {
    const employeeForm = document.querySelector('form');
    const employeeIdInput = document.querySelector('[name="employee_id"]') ||
                            document.querySelector('[data-employee-id]');

    if (!employeeForm) return;

    const employeeId = employeeIdInput?.value ||
                       employeeIdInput?.dataset?.employeeId ||
                       getEmployeeIdFromForm();

    if (!employeeId) {
        // 신규 등록 모드 - 증빙 첨부는 저장 후 가능
        return;
    }

    // 증빙 첨부 영역이 있는 컨테이너 초기화
    new EvidenceAttachmentManager({
        ownerType: 'employee',
        ownerId: employeeId,
        container: employeeForm,
        onUpdate: () => {
            // 증빙 파일 업데이트 완료
        }
    });
}

// DOMContentLoaded에서 자동 초기화
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initEmployeeForm);
}

export default {
    initEmployeeForm,
    initSectionNavigation,
    initDynamicFields,
    addDynamicItem,
    initPhotoPreview,
    initProfilePhotoUpload,
    initBusinessCardUpload,
    initFormValidation,
    validateField,
    validateForm,
    initAddressSearch,
    initFileUpload,
    getEmployeeIdFromForm,
    showToast,
    validateImageFile,
    initAccountSection,
    validateAccountFields,
    initEvidenceAttachments
};
