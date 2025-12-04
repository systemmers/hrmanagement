/**
 * Dynamic Sections Manager
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 동적 필드 추가/삭제 로직 관리
 */

import {
    getEducationTemplate,
    getCareerTemplate,
    getCertificateTemplate,
    getFamilyTemplate,
    getLanguageTemplate,
    getProjectTemplate
} from './templates.js';

/**
 * 동적 항목 추가
 * @param {string} listId - 목록 요소 ID
 * @param {string} template - HTML 템플릿
 */
export function addDynamicItem(listId, template) {
    const list = document.getElementById(listId);
    if (!list) return;

    const items = list.querySelectorAll('.dynamic-item');
    const newIndex = items.length;

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
 * 버튼별 동적 필드 매핑
 */
const BUTTON_CONFIG = {
    addEducation: { listId: 'educationList', getTemplate: getEducationTemplate },
    addCareer: { listId: 'careerList', getTemplate: getCareerTemplate },
    addCertificate: { listId: 'certificateList', getTemplate: getCertificateTemplate },
    addLanguage: { listId: 'languageList', getTemplate: getLanguageTemplate },
    addProject: { listId: 'projectList', getTemplate: getProjectTemplate },
    addFamily: { listId: 'familyList', getTemplate: getFamilyTemplate }
};

/**
 * 동적 필드 추가/삭제 초기화
 */
export function initDynamicFields() {
    // 각 버튼에 이벤트 리스너 등록
    Object.entries(BUTTON_CONFIG).forEach(([buttonId, config]) => {
        const btn = document.getElementById(buttonId);
        if (btn) {
            btn.addEventListener('click', () => {
                addDynamicItem(config.listId, config.getTemplate());
            });
        }
    });

    // 삭제 버튼 이벤트 위임
    document.addEventListener('click', handleRemoveClick);
}

export default {
    initDynamicFields,
    addDynamicItem
};
