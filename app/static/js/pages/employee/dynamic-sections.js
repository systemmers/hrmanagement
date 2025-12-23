/**
 * Dynamic Sections Manager
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 * Phase 8: FieldRegistry 통합 - 동적 설정 기반 전환
 *
 * 동적 필드 추가/삭제 로직 관리
 *
 * 마이그레이션 전략:
 * - FieldRegistry 로드됨: 동적으로 BUTTON_CONFIG 생성
 * - FieldRegistry 미로드: 기존 하드코딩 설정 사용 (fallback)
 */

import {
    getEducationTemplate,
    getCareerTemplate,
    getCertificateTemplate,
    getFamilyTemplate,
    getLanguageTemplate,
    getProjectTemplate,
    getAwardTemplate,
    getProjectParticipationTemplate
} from './templates.js';
import { TemplateGenerator } from '../../core/template-generator.js';

/**
 * 동적 항목 추가
 * @param {string} listId - 목록 요소 ID
 * @param {Function|string} templateOrGetter - HTML 템플릿 또는 템플릿 getter 함수
 */
export function addDynamicItem(listId, templateOrGetter) {
    const list = document.getElementById(listId);
    if (!list) return;

    const items = list.querySelectorAll('.dynamic-item');
    const newIndex = items.length;

    // 템플릿 가져오기 (함수면 호출, 문자열이면 그대로 사용)
    const template = typeof templateOrGetter === 'function'
        ? templateOrGetter(newIndex)
        : templateOrGetter;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = template.replace(/\[0\]/g, `[${newIndex}]`);

    const newItem = tempDiv.firstElementChild;
    newItem.setAttribute('data-index', newIndex);

    list.appendChild(newItem);
    newItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * 동적 항목 삭제 핸들러
 * @param {Event} e - 클릭 이벤트
 */
function handleRemoveClick(e) {
    if (!e.target.closest('.btn-remove')) return;

    const item = e.target.closest('.dynamic-item');
    if (!item) return;

    const list = item.parentElement;
    if (list.querySelectorAll('.dynamic-item').length > 1) {
        item.remove();
    } else {
        // 마지막 항목은 삭제하지 않고 입력값만 초기화
        const inputs = item.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            } else {
                input.value = '';
            }
        });
    }
}

/**
 * 버튼별 동적 필드 매핑 (Fallback)
 * FieldRegistry 미로드 시 사용
 */
const FALLBACK_BUTTON_CONFIG = {
    addEducation: { listId: 'educationList', getTemplate: getEducationTemplate },
    addCareer: { listId: 'careerList', getTemplate: getCareerTemplate },
    addCertificate: { listId: 'certificateList', getTemplate: getCertificateTemplate },
    addLanguage: { listId: 'languageList', getTemplate: getLanguageTemplate },
    addProject: { listId: 'projectList', getTemplate: getProjectTemplate },
    addFamily: { listId: 'familyList', getTemplate: getFamilyTemplate },
    addAward: { listId: 'awardList', getTemplate: getAwardTemplate },
    addProjectParticipation: { listId: 'projectParticipationList', getTemplate: getProjectParticipationTemplate }
};

/**
 * 섹션 ID → 버튼 ID 매핑
 */
const SECTION_TO_BUTTON = {
    education: 'addEducation',
    career: 'addCareer',
    certificate: 'addCertificate',
    language: 'addLanguage',
    project: 'addProject',
    family: 'addFamily',
    award: 'addAward',
    project_participation: 'addProjectParticipation'
};

/**
 * FieldRegistry에서 동적 버튼 설정 생성
 * @returns {Object} 버튼 설정 객체
 */
function buildButtonConfigFromRegistry() {
    const FieldRegistry = window.FieldRegistry;
    if (!FieldRegistry || !FieldRegistry.isLoaded()) {
        return null;
    }

    const config = {};
    const dynamicSections = FieldRegistry.getDynamicSections();

    for (const section of dynamicSections) {
        const buttonId = SECTION_TO_BUTTON[section.id] || `add${capitalize(section.id)}`;
        const listId = `${section.id}List`;

        config[buttonId] = {
            listId,
            sectionId: section.id,
            getTemplate: (index = 0) => {
                return TemplateGenerator.generateDynamicTemplate(section, { index });
            }
        };
    }

    return config;
}

/**
 * 버튼 설정 가져오기 (FieldRegistry 우선, Fallback 대비)
 * @returns {Object} 버튼 설정 객체
 */
function getButtonConfig() {
    const registryConfig = buildButtonConfigFromRegistry();
    if (registryConfig && Object.keys(registryConfig).length > 0) {
        return registryConfig;
    }
    return FALLBACK_BUTTON_CONFIG;
}

/**
 * 문자열 첫 글자 대문자화 (CamelCase)
 */
function capitalize(str) {
    if (!str) return '';
    return str.split('_')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join('');
}

/**
 * 동적 필드 추가/삭제 초기화
 * @param {Object} options - 초기화 옵션
 * @param {boolean} options.useRegistry - FieldRegistry 사용 여부 (기본: true)
 */
export function initDynamicFields(options = {}) {
    const { useRegistry = true } = options;

    // 버튼 설정 가져오기
    const buttonConfig = useRegistry ? getButtonConfig() : FALLBACK_BUTTON_CONFIG;

    // 각 버튼에 이벤트 리스너 등록
    Object.entries(buttonConfig).forEach(([buttonId, config]) => {
        const btn = document.getElementById(buttonId);
        if (btn) {
            btn.addEventListener('click', () => {
                addDynamicItem(config.listId, config.getTemplate);
            });
        }
    });

    // 삭제 버튼 이벤트 위임
    document.addEventListener('click', handleRemoveClick);
}

/**
 * FieldRegistry 로드 후 동적 필드 초기화
 * (페이지 로드 시 비동기로 호출)
 */
export async function initDynamicFieldsWithRegistry() {
    const FieldRegistry = window.FieldRegistry;

    if (FieldRegistry && !FieldRegistry.isLoaded()) {
        try {
            await FieldRegistry.loadFromServer();
        } catch (error) {
            console.warn('[dynamic-sections] FieldRegistry load failed, using fallback:', error);
        }
    }

    initDynamicFields({ useRegistry: true });
}

export default {
    initDynamicFields,
    initDynamicFieldsWithRegistry,
    addDynamicItem,
    getButtonConfig
};
