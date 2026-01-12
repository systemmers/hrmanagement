/**
 * Sidebar Navigation Component
 * 사이드바 네비게이션 카드 확장/축소 및 섹션 스크롤
 *
 * Phase 08: HR Card Migration - Section Nav → Sidebar Migration
 *
 * 기능:
 * - section-nav-card 확장/축소 토글
 * - sub-nav 아이템 클릭 시 섹션 스크롤
 * - active 상태 관리
 * - ScrollSpy (IntersectionObserver)
 */

/**
 * SidebarNav 클래스
 */
export class SidebarNav {
    /**
     * @param {Object} options - 설정 옵션
     */
    constructor(options = {}) {
        this.options = {
            cardSelector: options.cardSelector || '.section-nav-card',
            headerSelector: options.headerSelector || '.section-nav-card__header',
            toggleSelector: options.toggleSelector || '.section-nav-card__toggle',
            subNavSelector: options.subNavSelector || '.sub-nav',
            itemSelector: options.itemSelector || '.sub-nav__item',
            sectionSelector: options.sectionSelector || '.form-section',
            expandedClass: options.expandedClass || 'expanded',
            activeClass: options.activeClass || 'active',
            scrollOffset: options.scrollOffset || 100,
            rootMargin: options.rootMargin || '-100px 0px -60% 0px',
            autoExpand: options.autoExpand !== false, // 기본값 true
            ...options
        };

        this.cards = [];
        this.navItems = [];
        this.sections = [];
        this.observer = null;
    }

    /**
     * 초기화
     * @returns {SidebarNav} 체이닝
     */
    init() {
        this.setupElements();

        if (this.cards.length === 0) {
            // section-nav-card가 없으면 조용히 종료
            return this;
        }

        this.bindEvents();
        this.initScrollSpy();

        // 첫 번째 카드 자동 확장
        if (this.options.autoExpand && this.cards.length > 0) {
            this.expandCard(this.cards[0]);
        }

        return this;
    }

    /**
     * DOM 요소 설정
     */
    setupElements() {
        this.cards = Array.from(document.querySelectorAll(this.options.cardSelector));
        this.navItems = Array.from(document.querySelectorAll(this.options.itemSelector));
        this.sections = Array.from(document.querySelectorAll(this.options.sectionSelector));
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 카드 헤더 클릭 → 토글
        this.cards.forEach(card => {
            const header = card.querySelector(this.options.headerSelector);
            if (header) {
                header.addEventListener('click', (e) => {
                    // 링크 클릭은 제외
                    if (e.target.closest('a')) return;
                    this.toggleCard(card);
                });
            }
        });

        // 서브 네비 아이템 클릭 → 섹션 스크롤
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleItemClick(item);
            });
        });
    }

    /**
     * 카드 토글
     * @param {Element} card - 카드 요소
     */
    toggleCard(card) {
        if (card.classList.contains(this.options.expandedClass)) {
            this.collapseCard(card);
        } else {
            this.expandCard(card);
        }
    }

    /**
     * 카드 확장
     * @param {Element} card - 카드 요소
     */
    expandCard(card) {
        card.classList.add(this.options.expandedClass);

        // 토글 아이콘 회전
        const toggle = card.querySelector(this.options.toggleSelector);
        if (toggle) {
            toggle.style.transform = 'rotate(180deg)';
        }
    }

    /**
     * 카드 축소
     * @param {Element} card - 카드 요소
     */
    collapseCard(card) {
        card.classList.remove(this.options.expandedClass);

        // 토글 아이콘 복원
        const toggle = card.querySelector(this.options.toggleSelector);
        if (toggle) {
            toggle.style.transform = '';
        }
    }

    /**
     * 모든 카드 축소
     */
    collapseAll() {
        this.cards.forEach(card => this.collapseCard(card));
    }

    /**
     * 아이템 클릭 처리
     * @param {Element} item - 클릭된 아이템
     */
    handleItemClick(item) {
        // 활성 상태 설정
        this.setActiveItem(item);

        // 섹션으로 스크롤
        const targetId = item.getAttribute('href') || item.dataset.section;
        if (targetId) {
            const sectionId = targetId.startsWith('#') ? targetId.slice(1) : targetId;
            const section = document.getElementById(sectionId);
            if (section) {
                this.scrollToSection(section);
            }
        }
    }

    /**
     * 활성 아이템 설정
     * @param {Element} item - 활성화할 아이템
     */
    setActiveItem(item) {
        // 모든 아이템 비활성화
        this.navItems.forEach(i => i.classList.remove(this.options.activeClass));

        // 선택된 아이템 활성화
        item.classList.add(this.options.activeClass);

        // 해당 카드 확장
        const card = item.closest(this.options.cardSelector);
        if (card && !card.classList.contains(this.options.expandedClass)) {
            this.expandCard(card);
        }
    }

    /**
     * 섹션으로 스크롤
     * @param {Element} section - 대상 섹션
     */
    scrollToSection(section) {
        const offsetTop = section.getBoundingClientRect().top + window.pageYOffset - this.options.scrollOffset;

        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }

    /**
     * ScrollSpy 초기화
     */
    initScrollSpy() {
        if (this.sections.length === 0 || this.navItems.length === 0) return;

        const observerOptions = {
            root: null,
            rootMargin: this.options.rootMargin,
            threshold: 0
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.id;
                    this.updateActiveBySection(sectionId);
                }
            });
        }, observerOptions);

        this.sections.forEach(section => {
            if (section.id) {
                this.observer.observe(section);
            }
        });
    }

    /**
     * 섹션 ID로 활성 아이템 업데이트
     * @param {string} sectionId - 섹션 ID
     */
    updateActiveBySection(sectionId) {
        // href 또는 data-section으로 매칭
        const matchingItem = this.navItems.find(item => {
            const href = item.getAttribute('href');
            const dataSection = item.dataset.section;
            return href === `#${sectionId}` || dataSection === sectionId;
        });

        if (matchingItem) {
            // 모든 아이템 비활성화
            this.navItems.forEach(i => i.classList.remove(this.options.activeClass));
            // 매칭 아이템 활성화
            matchingItem.classList.add(this.options.activeClass);
        }
    }

    /**
     * 정리
     */
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
    }
}

/**
 * 간편 초기화 함수
 * @param {Object} options - 설정 옵션
 * @returns {SidebarNav} 인스턴스
 */
export function initSidebarNav(options = {}) {
    const nav = new SidebarNav(options);
    return nav.init();
}

// 자동 초기화 (DOMContentLoaded)
document.addEventListener('DOMContentLoaded', () => {
    const card = document.querySelector('.section-nav-card');
    if (card) {
        initSidebarNav();
    }
});

export default SidebarNav;
