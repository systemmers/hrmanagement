/**
 * Accordion Component
 * 재사용 가능한 아코디언 모듈
 * @module components/accordion
 */

/**
 * 아코디언 컴포넌트 옵션
 * @typedef {Object} AccordionOptions
 * @property {string} [toggleSelector='.accordion-toggle'] - 토글 버튼 선택자
 * @property {string} [sectionSelector='.accordion-section'] - 섹션 컨테이너 선택자
 * @property {string} [collapsedClass='collapsed'] - 접힘 상태 클래스명
 * @property {boolean} [autoExpand=true] - 추가 버튼 클릭 시 자동 펼침 여부
 */

/**
 * 아코디언 UI 컴포넌트
 * @class
 * @example
 * const accordion = new Accordion('#my-accordion', { autoExpand: true });
 * accordion.expandAll();
 */
export class Accordion {
    /**
     * Accordion 인스턴스 생성
     * @param {string|HTMLElement} container - 아코디언 컨테이너 요소 또는 선택자
     * @param {AccordionOptions} [options={}] - 아코디언 옵션
     */
    constructor(container, options = {}) {
        /** @type {HTMLElement|null} */
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        /** @type {AccordionOptions} */
        this.options = {
            toggleSelector: '.accordion-toggle',
            sectionSelector: '.accordion-section',
            collapsedClass: 'collapsed',
            autoExpand: true,
            ...options
        };

        /** @type {Function|null} 토글 콜백 */
        this.onToggle = null;

        this.init();
    }

    /**
     * 아코디언 초기화
     * @private
     */
    init() {
        if (!this.container) return;
        this.bindEvents();
    }

    /**
     * 이벤트 바인딩
     * @private
     */
    bindEvents() {
        this.container.querySelectorAll(this.options.toggleSelector).forEach(toggle => {
            toggle.addEventListener('click', (e) => this.handleToggle(e));
        });

        this.container.querySelectorAll('[data-action="add"]').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleAdd(e));
        });
    }

    /**
     * 토글 이벤트 핸들러
     * @private
     * @param {MouseEvent} e - 클릭 이벤트
     */
    handleToggle(e) {
        const section = e.target.closest(this.options.sectionSelector);
        if (section) {
            section.classList.toggle(this.options.collapsedClass);
            this.onToggle?.(section);
        }
    }

    /**
     * 추가 버튼 클릭 핸들러 (자동 펼침)
     * @private
     * @param {MouseEvent} e - 클릭 이벤트
     */
    handleAdd(e) {
        e.stopPropagation();

        if (this.options.autoExpand) {
            const section = e.target.closest(this.options.sectionSelector);
            section?.classList.remove(this.options.collapsedClass);
        }
    }

    /**
     * 특정 섹션 펼치기
     * @param {HTMLElement} section - 펼칠 섹션 요소
     */
    expand(section) {
        section.classList.remove(this.options.collapsedClass);
    }

    /**
     * 특정 섹션 접기
     * @param {HTMLElement} section - 접을 섹션 요소
     */
    collapse(section) {
        section.classList.add(this.options.collapsedClass);
    }

    /**
     * 특정 섹션 토글
     * @param {HTMLElement} section - 토글할 섹션 요소
     */
    toggle(section) {
        section.classList.toggle(this.options.collapsedClass);
    }

    /**
     * 모든 섹션 펼치기
     */
    expandAll() {
        this.container.querySelectorAll(this.options.sectionSelector).forEach(s =>
            s.classList.remove(this.options.collapsedClass)
        );
    }

    /**
     * 모든 섹션 접기
     */
    collapseAll() {
        this.container.querySelectorAll(this.options.sectionSelector).forEach(s =>
            s.classList.add(this.options.collapsedClass)
        );
    }
}

/**
 * 페이지 내 모든 아코디언 자동 초기화
 * data-accordion 속성이 있는 요소를 대상으로 함
 * @returns {void}
 */
export function initAccordions() {
    document.querySelectorAll('[data-accordion]').forEach(container => {
        new Accordion(container);
    });
}

export default Accordion;
