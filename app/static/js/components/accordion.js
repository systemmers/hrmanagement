/**
 * Accordion Component
 * 재사용 가능한 아코디언 모듈
 */

export class Accordion {
    constructor(container, options = {}) {
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        this.options = {
            toggleSelector: '.accordion-toggle',
            sectionSelector: '.accordion-section',
            collapsedClass: 'collapsed',
            autoExpand: true,  // 추가 버튼 클릭 시 자동 펼침
            ...options
        };

        this.init();
    }

    init() {
        if (!this.container) return;
        this.bindEvents();
    }

    bindEvents() {
        // 토글 이벤트
        this.container.querySelectorAll(this.options.toggleSelector).forEach(toggle => {
            toggle.addEventListener('click', (e) => this.handleToggle(e));
        });

        // 추가 버튼 이벤트 (자동 펼침)
        this.container.querySelectorAll('[data-action="add"]').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleAdd(e));
        });
    }

    handleToggle(e) {
        const section = e.target.closest(this.options.sectionSelector);
        if (section) {
            section.classList.toggle(this.options.collapsedClass);
            this.onToggle?.(section);
        }
    }

    handleAdd(e) {
        e.stopPropagation();

        if (this.options.autoExpand) {
            const section = e.target.closest(this.options.sectionSelector);
            section?.classList.remove(this.options.collapsedClass);
        }
    }

    // 프로그래밍 방식 제어
    expand(section) {
        section.classList.remove(this.options.collapsedClass);
    }

    collapse(section) {
        section.classList.add(this.options.collapsedClass);
    }

    toggle(section) {
        section.classList.toggle(this.options.collapsedClass);
    }

    expandAll() {
        this.container.querySelectorAll(this.options.sectionSelector).forEach(s =>
            s.classList.remove(this.options.collapsedClass)
        );
    }

    collapseAll() {
        this.container.querySelectorAll(this.options.sectionSelector).forEach(s =>
            s.classList.add(this.options.collapsedClass)
        );
    }
}

// 자동 초기화 (data-accordion 속성 사용 시)
export function initAccordions() {
    document.querySelectorAll('[data-accordion]').forEach(container => {
        new Accordion(container);
    });
}

export default Accordion;
