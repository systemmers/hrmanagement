/**
 * Section Navigation Initialization Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 섹션 네비게이션 초기화
 */

import { SectionNav } from '../../../shared/components/section-nav.js';

/**
 * 섹션 네비게이션 초기화
 */
export function initSectionNavigation() {
    const sectionNav = new SectionNav({
        sectionSelector: '.form-section',
        navItemSelector: '.section-nav-item',
        scrollContainerSelector: '.form-main-content',
        navId: 'sectionNav',
        overlayId: 'sectionNavOverlay',
        toggleBtnId: 'mobileNavToggle',
        scrollOffset: 80,
        rootMargin: '-100px 0px -50% 0px'
    });

    sectionNav.init();
}

export default {
    initSectionNavigation
};
