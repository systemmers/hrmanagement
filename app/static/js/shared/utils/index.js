/**
 * 유틸리티 모듈 인덱스
 * Phase 7: 프론트엔드 리팩토링
 *
 * 모든 유틸리티 함수를 하나의 진입점에서 내보냅니다.
 */

// 포맷팅 유틸리티
export {
    formatNumber,
    parseNumber,
    formatCurrency,
    formatPercent,
    formatDate,
    formatDateKorean,
    formatPhone,
    formatBusinessNumber,
    formatFileSize
} from './formatting.js';

// DOM 유틸리티
export {
    $,
    $$,
    createElement,
    toggleVisibility,
    show,
    hide,
    toggleClass,
    setDisabled,
    setDisabledAll,
    setValue,
    getValue,
    empty,
    isVisible,
    scrollIntoView,
    getFormData,
    focus
} from './dom.js';

// 이벤트 유틸리티
export {
    EventDelegator,
    debounce,
    throttle,
    once,
    onReady,
    emit,
    createKeyboardHandler,
    onClickOutside,
    EventManager
} from './events.js';

// 유효성 검증 유틸리티
export {
    isRequired,
    isEmail,
    isPhone,
    isNumber,
    isInteger,
    isPositive,
    isInRange,
    isLength,
    isDate,
    isBusinessNumber,
    isBirthDate,
    isAllowedExtension,
    isAllowedFileSize,
    isUrl,
    ValidationResult,
    validateForm,
    validators
} from './validation.js';

// API 유틸리티
export {
    ApiError,
    request,
    get,
    post,
    put,
    patch,
    del,
    postForm,
    uploadFile,
    downloadFile,
    retry,
    cancellableRequest
} from './api.js';
