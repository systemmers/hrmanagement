/**
 * 모바일 햄버거 메뉴 기능
 * 인사카드 프로토타입
 */

class MobileMenu {
    constructor() {
        this.hamburger = document.querySelector('.hamburger-menu');
        this.sidebar = document.querySelector('.sidebar-container');
        this.overlay = document.querySelector('.sidebar-overlay');
        this.body = document.body;
        this.isOpen = false;

        this.init();
    }

    init() {
        if (!this.hamburger || !this.sidebar) {
            console.warn('MobileMenu: Required elements not found');
            return;
        }

        // 오버레이가 없으면 생성
        if (!this.overlay) {
            this.createOverlay();
        }

        // 이벤트 리스너 등록
        this.setupEventListeners();

        // 윈도우 리사이즈 이벤트
        window.addEventListener('resize', () => this.handleResize());
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'sidebar-overlay';
        this.overlay.style.display = 'none';
        document.body.appendChild(this.overlay);
    }

    setupEventListeners() {
        // 햄버거 버튼 클릭
        this.hamburger.addEventListener('click', () => this.toggle());

        // 오버레이 클릭
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.close());
        }

        // ESC 키로 닫기
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // 네비게이션 링크 클릭 시 메뉴 닫기 (모바일에서만)
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    this.close();
                }
            });
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;

        // 사이드바 열기
        this.sidebar.classList.add('mobile-open');

        // body에 스크롤 방지
        this.body.classList.add('sidebar-open');

        // 오버레이 표시
        if (this.overlay) {
            this.overlay.style.display = 'block';
            // 애니메이션을 위한 약간의 지연
            setTimeout(() => {
                this.overlay.style.opacity = '1';
            }, 10);
        }

        // 접근성: aria-expanded 속성 업데이트
        this.hamburger.setAttribute('aria-expanded', 'true');

        // 햄버거 아이콘 변경
        this.updateHamburgerIcon(true);
    }

    close() {
        this.isOpen = false;

        // 사이드바 닫기
        this.sidebar.classList.remove('mobile-open');

        // body 스크롤 복원
        this.body.classList.remove('sidebar-open');

        // 오버레이 숨기기
        if (this.overlay) {
            this.overlay.style.opacity = '0';
            setTimeout(() => {
                this.overlay.style.display = 'none';
            }, 200); // transition 시간과 맞춤
        }

        // 접근성: aria-expanded 속성 업데이트
        this.hamburger.setAttribute('aria-expanded', 'false');

        // 햄버거 아이콘 변경
        this.updateHamburgerIcon(false);
    }

    updateHamburgerIcon(isOpen) {
        const icon = this.hamburger.querySelector('i');
        if (icon) {
            icon.className = isOpen ? 'fas fa-times' : 'fas fa-bars';
        }
    }

    handleResize() {
        // 데스크톱 크기로 변경되면 메뉴 자동 닫기
        if (window.innerWidth > 768 && this.isOpen) {
            this.close();
        }
    }

    // 공개 API
    isMenuOpen() {
        return this.isOpen;
    }

    forceClose() {
        if (this.isOpen) {
            this.close();
        }
    }
}

// 전역 인스턴스 생성
let mobileMenuInstance = null;

// DOM 로드 완료 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        mobileMenuInstance = new MobileMenu();
    });
} else {
    mobileMenuInstance = new MobileMenu();
}

// 모듈 export (필요한 경우)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileMenu;
}
