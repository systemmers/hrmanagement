/**
 * 스크롤 감지 및 네비게이션 활성화
 * Intersection Observer API 사용
 * 인사카드 프로토타입
 */

class ScrollSpy {
    constructor() {
        this.sections = [];
        this.navLinks = [];
        this.observer = null;
        this.observerOptions = {
            root: null, // viewport 기준
            rootMargin: '-20% 0px -70% 0px', // 상단 20%, 하단 70% 여백
            threshold: 0
        };

        this.init();
    }

    init() {
        // 섹션과 네비게이션 링크 수집
        this.collectElements();

        if (this.sections.length === 0) {
            console.warn('ScrollSpy: No sections found');
            return;
        }

        // Intersection Observer 설정
        this.setupObserver();

        // 네비게이션 링크 클릭 이벤트
        this.setupNavigation();

        // 초기 활성화 상태 설정
        this.setInitialActive();
    }

    collectElements() {
        // data-section 속성을 가진 모든 섹션 수집
        this.sections = Array.from(document.querySelectorAll('[data-section]'));

        // 네비게이션 링크 수집
        this.navLinks = Array.from(document.querySelectorAll('.nav-link[href^="#"]'));
    }

    setupObserver() {
        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersection(entries),
            this.observerOptions
        );

        // 각 섹션 관찰 시작
        this.sections.forEach(section => {
            this.observer.observe(section);
        });
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                this.setActiveLink(sectionId);
            }
        });
    }

    setActiveLink(sectionId) {
        // 모든 링크에서 active 클래스 제거
        this.navLinks.forEach(link => {
            link.classList.remove('active');
        });

        // 해당 섹션의 링크에 active 클래스 추가
        const activeLink = this.navLinks.find(link => {
            const href = link.getAttribute('href');
            return href === `#${sectionId}`;
        });

        if (activeLink) {
            activeLink.classList.add('active');

            // 접근성: aria-current 속성 업데이트
            this.navLinks.forEach(link => {
                link.removeAttribute('aria-current');
            });
            activeLink.setAttribute('aria-current', 'location');
        }
    }

    setupNavigation() {
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();

                const targetId = link.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);

                if (targetSection) {
                    // 부드러운 스크롤
                    this.smoothScrollTo(targetSection);

                    // 모바일에서 메뉴 닫기
                    if (window.innerWidth <= 768) {
                        this.closeMobileMenu();
                    }
                }
            });
        });
    }

    smoothScrollTo(element) {
        const headerOffset = 20; // 여유 공간
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    closeMobileMenu() {
        const sidebar = document.querySelector('.sidebar-container');
        const overlay = document.querySelector('.sidebar-overlay');
        const body = document.body;

        if (sidebar) {
            sidebar.classList.remove('mobile-open');
        }
        if (body) {
            body.classList.remove('sidebar-open');
        }
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    setInitialActive() {
        // 페이지 로드 시 첫 번째 섹션 활성화
        if (this.sections.length > 0) {
            const firstSectionId = this.sections[0].id;
            if (firstSectionId) {
                this.setActiveLink(firstSectionId);
            }
        }

        // URL 해시가 있으면 해당 섹션으로 스크롤
        const hash = window.location.hash;
        if (hash) {
            const targetSection = document.querySelector(hash);
            if (targetSection) {
                setTimeout(() => {
                    this.smoothScrollTo(targetSection);
                }, 100);
            }
        }
    }

    // 공개 API
    refresh() {
        // 섹션과 링크 다시 수집 (동적 콘텐츠용)
        this.collectElements();

        // Observer 다시 설정
        if (this.observer) {
            this.observer.disconnect();
            this.setupObserver();
        }
    }

    destroy() {
        // Observer 해제
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }

        // 이벤트 리스너 제거는 여기서 필요 시 구현
    }
}

// 전역 인스턴스 생성
let scrollSpyInstance = null;

// DOM 로드 완료 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        scrollSpyInstance = new ScrollSpy();
    });
} else {
    scrollSpyInstance = new ScrollSpy();
}

// 모듈 export (필요한 경우)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScrollSpy;
}
