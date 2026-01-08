/**
 * Employee Form Page JavaScript
 * Phase 7: 프론트엔드 리팩토링 - 모듈 분할
 *
 * 기능:
 * - 섹션 네비게이션 (SectionNav 컴포넌트 사용)
 * - 동적 필드 추가/삭제
 * - 사진 미리보기
 * - 폼 유효성 검사
 * - 주소 검색 (다음 주소 API)
 * - 파일 업로드
 *
 * 이 파일은 하위 호환성을 위해 유지됩니다.
 * 개별 기능이 필요한 경우 './employee/index.js'에서 import하세요.
 *
 * 분할된 모듈 구조:
 * - templates.js: 동적 필드 HTML 템플릿
 * - dynamic-sections.js: 동적 필드 추가/삭제 로직
 * - helpers.js: 공통 헬퍼 함수
 * - photo-upload.js: 프로필 사진 업로드
 * - business-card.js: 명함 업로드
 * - validators.js: 폼 유효성 검사
 * - address-search.js: 다음 주소 API 연동
 * - file-upload-init.js: 첨부파일 업로드
 * - section-nav-init.js: 섹션 네비게이션
 * - index.js: 통합 진입점
 */

// 모듈화된 버전에서 모든 기능 re-export
export {
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
    initTreeSelector,
    getEmployeeIdFromForm,
    showToast,
    validateImageFile,
    getEducationTemplate,
    getCareerTemplate,
    getCertificateTemplate,
    getFamilyTemplate,
    getLanguageTemplate,
    getProjectTemplate,
    getAwardTemplate,
    initAccountSection,
    validateAccountFields
} from './index.js';

// 기본 export
export { default } from './index.js';

// 자동 초기화는 employee/index.js에서 수행됨
