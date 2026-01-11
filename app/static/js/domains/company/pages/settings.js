/**
 * 법인 설정 페이지 컨트롤러
 *
 * 모듈 구조:
 * - settings/tabs/org-management.js: 조직 관리 (트리, CRUD, 드래그앤드롭)
 * - settings/tabs/org-type-settings.js: 조직 유형 설정 (아이콘, 라벨)
 * - settings/tabs/classifications.js: 분류 옵션 (조직구조, 고용정책)
 * - settings/tabs/patterns-visibility.js: 패턴 규칙, 노출 설정
 * - settings/tabs/documents.js: 법인 서류 관리
 * - settings/tabs/audit-logs.js: 감사 로그
 * - settings/shared/constants.js: 공유 상수
 */

import { Accordion } from '../../../shared/components/accordion.js';
import { loadAuditData, initAuditHandlers } from './settings/tabs/audit-logs.js';
import { loadDocumentsData, initDocumentsHandlers } from './settings/tabs/documents.js';
import { loadOrganizationData, loadEmploymentData, initCategoryHandlers } from './settings/tabs/classifications.js';
import { loadPatternsData, loadVisibilityData, initPatternsHandlers, initVisibilityHandlers } from './settings/tabs/patterns-visibility.js';
import { loadOrgManagementData, initOrgManagementHandlers, setDataReloadCallback } from './settings/tabs/org-management.js';

const state = {
    activeTab: 'basic',
    loadedTabs: new Set(['basic'])
};

// org-management 모듈에 리로드 콜백 설정
setDataReloadCallback(async () => {
    state.loadedTabs.delete('org-management');
    await loadOrgManagementData();
});

function initTabs() {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(`tab-${hash}`)) {
        state.activeTab = hash;
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    switchTab(state.activeTab);
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        const isActive = btn.dataset.tab === tabId;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-selected', isActive);
    });

    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `tab-${tabId}`);
    });

    state.activeTab = tabId;
    window.location.hash = tabId;

    if (!state.loadedTabs.has(tabId)) {
        loadTabData(tabId);
    }
}

/**
 * 탭 데이터 로드
 * @param {string} tabId - 탭 ID
 */
async function loadTabData(tabId) {
    switch (tabId) {
        case 'org-management':
            await loadOrgManagementData();
            break;
        case 'organization':
            await loadOrganizationData();
            break;
        case 'patterns':
            await loadPatternsData();
            break;
        case 'employment':
            await loadEmploymentData();
            break;
        case 'documents':
            await loadDocumentsData();
            break;
        case 'visibility':
            await loadVisibilityData();
            break;
        case 'audit':
            await loadAuditData();
            break;
    }
    state.loadedTabs.add(tabId);
}

function initAccordions() {
    document.querySelectorAll('[data-accordion]').forEach(container => {
        new Accordion(container);
    });
}

function init() {
    initTabs();
    initAccordions();
    initCategoryHandlers();
    initPatternsHandlers();
    initDocumentsHandlers();
    initVisibilityHandlers();
    initAuditHandlers();
}

// DOM 로드 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
