/**
 * 프로필 페이지 섹션 네비게이션
 *
 * 기능:
 * - updateActiveNav: 스크롤 시 활성 섹션 업데이트
 * - smoothScrollToSection: 네비게이션 클릭 시 부드러운 스크롤
 * - initProfileNavigation: 전체 초기화
 */

/**
 * 활성 네비게이션 항목 업데이트
 * @param {NodeList} navItems - 네비게이션 항목 목록
 * @param {NodeList} sections - 섹션 목록
 * @param {number} offset - 스크롤 오프셋 (기본: 100)
 */
export function updateActiveNav(navItems, sections, offset = 100) {
    let currentSection = '';
    const scrollPosition = window.scrollY + offset;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;

        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });

    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === '#' + currentSection) {
            item.classList.add('active');
        }
    });
}

/**
 * 섹션으로 부드러운 스크롤
 * @param {Event} e - 클릭 이벤트
 */
export function smoothScrollToSection(e) {
    e.preventDefault();
    const targetId = this.getAttribute('href').substring(1);
    const targetSection = document.getElementById(targetId);

    if (targetSection) {
        targetSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * 프로필 네비게이션 초기화
 * @param {Object} options - 초기화 옵션
 * @param {string} options.navSelector - 네비게이션 항목 선택자 (기본: '.section-nav-item')
 * @param {string} options.sectionSelector - 섹션 선택자 (기본: '.profile-section')
 * @param {number} options.scrollOffset - 스크롤 오프셋 (기본: 100)
 */
export function initProfileNavigation(options = {}) {
    const {
        navSelector = '.section-nav-item',
        sectionSelector = '.profile-section',
        scrollOffset = 100
    } = options;

    const navItems = document.querySelectorAll(navSelector);
    const sections = document.querySelectorAll(sectionSelector);

    if (navItems.length === 0 || sections.length === 0) {
        return;
    }

    // 스크롤 시 활성 섹션 업데이트
    window.addEventListener('scroll', function() {
        updateActiveNav(navItems, sections, scrollOffset);
    });

    // 네비게이션 클릭 시 부드러운 스크롤
    navItems.forEach(item => {
        item.addEventListener('click', smoothScrollToSection);
    });

    // 초기 활성 상태 설정
    updateActiveNav(navItems, sections, scrollOffset);
}

// 전역 노출 (레거시 호환)
if (typeof window !== 'undefined') {
    window.ProfileNavigation = {
        updateActiveNav,
        smoothScrollToSection,
        initProfileNavigation
    };
}
