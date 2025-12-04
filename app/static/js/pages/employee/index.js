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

// 템플릿 re-export
export {
    getEducationTemplate,
    getCareerTemplate,
    getCertificateTemplate,
    getFamilyTemplate,
    getLanguageTemplate,
    getProjectTemplate
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
    validateImageFile
};

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
    validateImageFile
};
