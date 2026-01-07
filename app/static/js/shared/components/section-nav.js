/**
 * Section Navigation Component
 * 공통 섹션 네비게이션 모듈
 * - 스크롤 스파이 (IntersectionObserver)
 * - 스무스 스크롤 네비게이션
 * - 모바일 네비게이션 토글
 */

/**
 * SectionNav 클래스
 * 섹션 기반 네비게이션을 관리하는 재사용 가능한 컴포넌트
 */
export class SectionNav {
    /**
     * @param {Object} options - 설정 옵션
     * @param {string} options.sectionSelector - 섹션 요소 선택자 (기본: '.form-section')
     * @param {string} options.navItemSelector - 네비게이션 아이템 선택자 (기본: '.section-nav-item')
     * @param {string} options.scrollContainerSelector - 스크롤 컨테이너 선택자 (기본: null, 없으면 document)
     * @param {string} options.navId - 네비게이션 컨테이너 ID (기본: 'sectionNav')
     * @param {string} options.overlayId - 오버레이 요소 ID (기본: 'sectionNavOverlay')
     * @param {string} options.toggleBtnId - 모바일 토글 버튼 ID (기본: 'mobileNavToggle')
     * @param {number} options.scrollOffset - 스크롤 오프셋 (기본: 80)
     * @param {string} options.rootMargin - IntersectionObserver rootMargin (기본: '-100px 0px -50% 0px')
     */
    constructor(options = {}) {
        this.options = {
            sectionSelector: options.sectionSelector || '.form-section',
            navItemSelector: options.navItemSelector || '.section-nav-item',
            scrollContainerSelector: options.scrollContainerSelector || null,
            navId: options.navId || 'sectionNav',
            overlayId: options.overlayId || 'sectionNavOverlay',
            toggleBtnId: options.toggleBtnId || 'mobileNavToggle',
            scrollOffset: options.scrollOffset || 80,
            rootMargin: options.rootMargin || '-100px 0px -50% 0px'
        };

        this.sections = null;
        this.navItems = null;
        this.scrollContainer = null;
        this.observer = null;
    }

    /**
     * 네비게이션 초기화
     * @returns {SectionNav} 체이닝을 위한 this 반환
     */
    init() {
        this.sections = document.querySelectorAll(this.options.sectionSelector);
        this.navItems = document.querySelectorAll(this.options.navItemSelector);

        if (this.options.scrollContainerSelector) {
            this.scrollContainer = document.querySelector(this.options.scrollContainerSelector);
        }

        this.initScrollSpy();
        this.initSmoothScroll();
        this.initMobileNav();

        return this;
    }

    /**
     * 스크롤 스파이 초기화 - IntersectionObserver를 사용한 현재 섹션 감지
     */
    initScrollSpy() {
        if (this.sections.length === 0 || this.navItems.length === 0) return;

        const observerOptions = {
            root: this.scrollContainer,
            rootMargin: this.options.rootMargin,
            threshold: 0
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.id;
                    this.setActiveNavItem(sectionId);
                }
            });
        }, observerOptions);

        this.sections.forEach(section => {
            this.observer.observe(section);
        });
    }

    /**
     * 활성 네비게이션 아이템 설정
     * @param {string} sectionId - 활성화할 섹션 ID
     */
    setActiveNavItem(sectionId) {
        this.navItems.forEach(item => {
            item.classList.remove('active');
        });

        const activeNavItem = document.querySelector(
            `${this.options.navItemSelector}[href="#${sectionId}"]`
        );

        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
    }

    /**
     * 스무스 스크롤 초기화 - 네비게이션 클릭 시 부드러운 스크롤
     */
    initSmoothScroll() {
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();

                const targetId = item.getAttribute('href');
                const targetSection = document.querySelector(targetId);

                if (targetSection) {
                    this.scrollToSection(targetSection);
                    this.closeMobileNav();
                }
            });
        });
    }

    /**
     * 특정 섹션으로 스크롤
     * @param {HTMLElement} targetSection - 스크롤할 대상 섹션
     */
    scrollToSection(targetSection) {
        if (this.scrollContainer) {
            const offsetTop = targetSection.offsetTop - this.options.scrollOffset;
            this.scrollContainer.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        } else {
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    /**
     * 모바일 네비게이션 토글 초기화
     */
    initMobileNav() {
        const toggleBtn = document.getElementById(this.options.toggleBtnId);
        const sectionNav = document.getElementById(this.options.navId);
        const overlay = document.getElementById(this.options.overlayId);

        if (!toggleBtn || !sectionNav) return;

        toggleBtn.addEventListener('click', () => {
            this.toggleMobileNav();
        });

        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeMobileNav();
            });
        }
    }

    /**
     * 모바일 네비게이션 토글
     */
    toggleMobileNav() {
        const sectionNav = document.getElementById(this.options.navId);
        const overlay = document.getElementById(this.options.overlayId);
        const toggleBtn = document.getElementById(this.options.toggleBtnId);

        if (sectionNav) {
            sectionNav.classList.toggle('mobile-active');
        }

        if (overlay) {
            overlay.classList.toggle('active');
        }

        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        }
    }

    /**
     * 모바일 네비게이션 닫기
     */
    closeMobileNav() {
        const sectionNav = document.getElementById(this.options.navId);
        const overlay = document.getElementById(this.options.overlayId);
        const toggleBtn = document.getElementById(this.options.toggleBtnId);

        if (sectionNav) {
            sectionNav.classList.remove('mobile-active');
        }

        if (overlay) {
            overlay.classList.remove('active');
        }

        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        }
    }

    /**
     * 옵저버 정리 (컴포넌트 제거 시 호출)
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
 * @param {Object} options - SectionNav 옵션
 * @returns {SectionNav} 초기화된 SectionNav 인스턴스
 */
export function initSectionNav(options = {}) {
    const nav = new SectionNav(options);
    return nav.init();
}

export default SectionNav;
