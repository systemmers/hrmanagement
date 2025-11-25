/**
 * 사이드바 토글 기능
 * 인사카드 프로토타입
 */

class Sidebar {
    constructor() {
        this.sidebar = document.querySelector('.sidebar-container');
        this.toggleBtn = document.querySelector('.sidebar-toggle');
        this.mainContent = document.querySelector('.main-content-wrapper');
        this.storageKey = 'insacard_sidebar_collapsed';

        this.init();
    }

    init() {
        if (!this.sidebar || !this.toggleBtn) {
            console.warn('Sidebar: Required elements not found');
            return;
        }

        // localStorage에서 상태 복원
        this.restoreState();

        // 이벤트 리스너 등록
        this.toggleBtn.addEventListener('click', () => this.toggle());

        // 윈도우 리사이즈 이벤트
        window.addEventListener('resize', () => this.handleResize());
    }

    toggle() {
        const isCollapsed = this.sidebar.classList.toggle('collapsed');

        // localStorage에 상태 저장
        this.saveState(isCollapsed);

        // 아이콘 변경
        this.updateToggleIcon(isCollapsed);

        // 접근성: aria-expanded 속성 업데이트
        this.toggleBtn.setAttribute('aria-expanded', !isCollapsed);
    }

    collapse() {
        if (!this.sidebar.classList.contains('collapsed')) {
            this.sidebar.classList.add('collapsed');
            this.saveState(true);
            this.updateToggleIcon(true);
            this.toggleBtn.setAttribute('aria-expanded', 'false');
        }
    }

    expand() {
        if (this.sidebar.classList.contains('collapsed')) {
            this.sidebar.classList.remove('collapsed');
            this.saveState(false);
            this.updateToggleIcon(false);
            this.toggleBtn.setAttribute('aria-expanded', 'true');
        }
    }

    updateToggleIcon(isCollapsed) {
        const icon = this.toggleBtn.querySelector('i');
        if (icon) {
            icon.className = isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left';
        }
    }

    saveState(isCollapsed) {
        try {
            localStorage.setItem(this.storageKey, isCollapsed.toString());
        } catch (e) {
            console.warn('Sidebar: Failed to save state to localStorage', e);
        }
    }

    restoreState() {
        try {
            const savedState = localStorage.getItem(this.storageKey);
            if (savedState === 'true') {
                this.sidebar.classList.add('collapsed');
                this.updateToggleIcon(true);
                this.toggleBtn.setAttribute('aria-expanded', 'false');
            } else {
                this.updateToggleIcon(false);
                this.toggleBtn.setAttribute('aria-expanded', 'true');
            }
        } catch (e) {
            console.warn('Sidebar: Failed to restore state from localStorage', e);
        }
    }

    handleResize() {
        // 768px 이하에서는 자동으로 collapsed 상태로 변경
        if (window.innerWidth <= 768) {
            // 모바일에서는 collapsed 클래스 제거 (transform으로 처리)
            this.sidebar.classList.remove('collapsed');
        } else if (window.innerWidth > 768) {
            // 데스크톱으로 돌아왔을 때 저장된 상태 복원
            this.restoreState();
        }
    }

    // 공개 API
    isCollapsed() {
        return this.sidebar.classList.contains('collapsed');
    }

    getWidth() {
        return this.isCollapsed() ? 50 : 280;
    }
}

// 전역 인스턴스 생성
let sidebarInstance = null;

// DOM 로드 완료 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        sidebarInstance = new Sidebar();
    });
} else {
    sidebarInstance = new Sidebar();
}

// 모듈 export (필요한 경우)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Sidebar;
}
