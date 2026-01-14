/**
 * Template Generator - FieldRegistry 기반 HTML 템플릿 생성기
 *
 * FieldRegistry 섹션 정의를 기반으로 동적 폼 HTML을 생성합니다.
 * 기존 하드코딩된 templates.js 함수들을 대체합니다.
 *
 * Usage:
 *   import { TemplateGenerator, generateFormRow, generateDynamicTemplate } from '/static/js/core/template-generator.js';
 *
 *   // 단일 필드 생성
 *   const fieldHtml = generateFormRow(field, { prefix: 'education_' });
 *
 *   // 동적 섹션 템플릿 생성
 *   const section = FieldRegistry.getSection('education');
 *   const template = generateDynamicTemplate(section);
 */

/**
 * 단일 폼 필드 HTML 생성
 *
 * @param {Object} field - FieldDefinition 객체 (JS 형태)
 * @param {Object} options - 생성 옵션
 * @param {string} options.prefix - 필드명 접두사 (예: 'education_')
 * @param {string} options.value - 기본값
 * @param {boolean} options.showRequired - 필수 마크 표시 여부
 * @returns {string} HTML 문자열
 */
export function generateFormRow(field, options = {}) {
    const {
        prefix = '',
        value = '',
        showRequired = true,
    } = options;

    const fieldName = `${prefix}${field.name}[]`;
    const requiredMark = showRequired && field.required ? '<span class="required">*</span>' : '';
    const cssClass = field.cssClass || '';
    const fullWidth = cssClass.includes('full') ? ' form-group-full' : '';

    const label = `<label class="form-label">${field.label}${requiredMark}</label>`;
    const input = generateInputElement(field, fieldName, value);

    return `
        <div class="form-group${fullWidth}">
            ${label}
            ${input}
        </div>
    `.trim();
}

/**
 * 입력 요소 HTML 생성
 *
 * @param {Object} field - FieldDefinition 객체
 * @param {string} name - 입력 요소 name 속성
 * @param {string} value - 기본값
 * @returns {string} input/select/textarea HTML
 */
function generateInputElement(field, name, value = '') {
    const placeholder = field.placeholder || '';
    const readonly = field.readonly ? ' readonly' : '';
    const maxLength = field.maxLength ? ` maxlength="${field.maxLength}"` : '';
    const minLength = field.minLength ? ` minlength="${field.minLength}"` : '';
    const pattern = field.pattern ? ` pattern="${escapeHtml(field.pattern)}"` : '';
    const required = field.required ? ' required' : '';

    // 추가 HTML 속성
    const extraAttrs = field.attributes
        ? Object.entries(field.attributes)
            .map(([k, v]) => `${k}="${escapeHtml(String(v))}"`)
            .join(' ')
        : '';

    const baseAttrs = `name="${name}" class="form-input"${readonly}${required}`;

    switch (field.type) {
        case 'textarea':
            return `<textarea ${baseAttrs}${maxLength}${minLength} rows="2" placeholder="${escapeHtml(placeholder)}" ${extraAttrs}>${escapeHtml(value)}</textarea>`;

        case 'select':
            return generateSelectElement(field, name, value, readonly);

        case 'date':
            return `<input type="date" ${baseAttrs} value="${escapeHtml(value)}" ${extraAttrs}>`;

        case 'number':
            return `<input type="number" ${baseAttrs}${maxLength}${minLength} value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" ${extraAttrs}>`;

        case 'tel':
            return `<input type="tel" ${baseAttrs}${pattern} value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" ${extraAttrs}>`;

        case 'email':
            return `<input type="email" ${baseAttrs} value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" ${extraAttrs}>`;

        case 'checkbox':
            const checked = value ? ' checked' : '';
            return `<input type="checkbox" ${baseAttrs}${checked} ${extraAttrs}>`;

        case 'hidden':
            return `<input type="hidden" ${baseAttrs} value="${escapeHtml(value)}" ${extraAttrs}>`;

        case 'text':
        default:
            return `<input type="text" ${baseAttrs}${maxLength}${minLength}${pattern} value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" ${extraAttrs}>`;
    }
}

/**
 * Select 요소 HTML 생성
 *
 * @param {Object} field - FieldDefinition 객체
 * @param {string} name - 입력 요소 name 속성
 * @param {string} selectedValue - 선택된 값
 * @param {string} readonly - readonly 속성 문자열
 * @returns {string} select HTML
 */
function generateSelectElement(field, name, selectedValue = '', readonly = '') {
    const options = field.options || [];
    const required = field.required ? ' required' : '';

    // 옵션 HTML 생성
    let optionsHtml = '<option value="">선택하세요</option>';
    for (const opt of options) {
        const selected = String(opt.value) === String(selectedValue) ? ' selected' : '';
        const disabled = opt.disabled ? ' disabled' : '';
        optionsHtml += `<option value="${escapeHtml(opt.value)}"${selected}${disabled}>${escapeHtml(opt.label)}</option>`;
    }

    return `<select name="${name}" class="form-input"${readonly}${required}>${optionsHtml}</select>`;
}

/**
 * 동적 섹션 템플릿 생성 (dynamic-item 컨테이너 포함)
 *
 * @param {Object} section - SectionDefinition 객체 (JS 형태)
 * @param {Object} options - 생성 옵션
 * @param {number} options.index - 항목 인덱스 (기본 0)
 * @param {Object} options.data - 초기 데이터
 * @returns {string} HTML 문자열
 */
export function generateDynamicTemplate(section, options = {}) {
    const {
        index = 0,
        data = {},
    } = options;

    // 섹션 ID에서 prefix 추출 (예: education -> education_)
    const prefix = `${section.id}_`;

    // 필드 HTML 생성
    const fields = section.fields || [];
    const fieldsHtml = fields
        .sort((a, b) => a.order - b.order)
        .map(field => {
            const value = data[field.name] || '';
            return generateFormRow(field, { prefix, value });
        })
        .join('\n                ');

    return `
        <div class="dynamic-item" data-index="${index}">
            <div class="form-grid">
                ${fieldsHtml}
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `.trim();
}

/**
 * 섹션 ID로 동적 템플릿 생성 함수 반환
 * (기존 getEducationTemplate() 등 함수 대체용)
 *
 * @param {string} sectionId - 섹션 ID
 * @returns {Function} 템플릿 생성 함수
 */
export function createTemplateGetter(sectionId) {
    return function(index = 0, data = {}) {
        // FieldRegistry에서 섹션 조회
        const FieldRegistry = window.FieldRegistry;
        if (!FieldRegistry) {
            console.error('[TemplateGenerator] FieldRegistry not loaded');
            return '';
        }

        const section = FieldRegistry.getSection(sectionId);
        if (!section) {
            console.error(`[TemplateGenerator] Section not found: ${sectionId}`);
            return '';
        }

        return generateDynamicTemplate(section, { index, data });
    };
}

/**
 * 모든 동적 섹션에 대한 템플릿 getter 함수 맵 생성
 *
 * @returns {Object} { sectionId: getTemplate() } 맵
 */
export function createAllTemplateGetters() {
    const FieldRegistry = window.FieldRegistry;
    if (!FieldRegistry) {
        console.error('[TemplateGenerator] FieldRegistry not loaded');
        return {};
    }

    const getters = {};
    const dynamicSections = FieldRegistry.getDynamicSections();

    for (const section of dynamicSections) {
        // 함수명 생성 (education -> getEducationTemplate)
        const funcName = `get${capitalize(section.id)}Template`;
        getters[funcName] = createTemplateGetter(section.id);

        // sectionId로도 접근 가능하게
        getters[section.id] = getters[funcName];
    }

    return getters;
}

/**
 * 정적 섹션 폼 HTML 생성 (동적이 아닌 일반 폼 섹션)
 *
 * @param {Object} section - SectionDefinition 객체
 * @param {Object} data - 폼 데이터
 * @param {Object} options - 생성 옵션
 * @returns {string} HTML 문자열
 */
export function generateStaticSection(section, data = {}, options = {}) {
    const prefix = options.prefix || '';

    const fields = section.fields || [];
    const fieldsHtml = fields
        .sort((a, b) => a.order - b.order)
        .map(field => {
            const value = data[field.name] || '';
            return generateFormRow(field, { prefix, value, showRequired: true });
        })
        .join('\n            ');

    return `
        <div class="form-grid">
            ${fieldsHtml}
        </div>
    `.trim();
}

// ===== Utility Functions =====

/**
 * HTML 특수문자 이스케이프
 *
 * @param {string} str - 원본 문자열
 * @returns {string} 이스케이프된 문자열
 */
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * 문자열 첫 글자 대문자화
 *
 * @param {string} str - 원본 문자열
 * @returns {string} 첫 글자 대문자 문자열
 */
function capitalize(str) {
    if (!str) return '';
    // snake_case를 CamelCase로 변환
    return str.split('_')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join('');
}

// ===== TemplateGenerator Class (Alternative Interface) =====

export class TemplateGenerator {
    /**
     * 단일 필드 HTML 생성
     */
    static generateFormRow = generateFormRow;

    /**
     * 동적 섹션 템플릿 생성
     */
    static generateDynamicTemplate = generateDynamicTemplate;

    /**
     * 정적 섹션 폼 생성
     */
    static generateStaticSection = generateStaticSection;

    /**
     * 템플릿 getter 함수 생성
     */
    static createTemplateGetter = createTemplateGetter;

    /**
     * 모든 템플릿 getter 맵 생성
     */
    static createAllTemplateGetters = createAllTemplateGetters;
}

// 전역 접근용 (기존 코드 호환성)
if (typeof window !== 'undefined') {
    window.TemplateGenerator = TemplateGenerator;

    // escapeHtml 전역 export (SSOT - DRY 원칙)
    window.HRFormatters = window.HRFormatters || {};
    window.HRFormatters.escapeHtml = escapeHtml;
}

// ES6 module export
export { escapeHtml };
