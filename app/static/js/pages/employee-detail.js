/**
 * Employee Detail Page JavaScript
 * - 섹션 네비게이션 스크롤 스파이
 * - 스무스 스크롤 네비게이션
 * - 모바일 메뉴 토글
 * - 파일 업로드 UI
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollSpy();
    initSmoothScroll();
    initMobileNav();
    initFileUpload();
});

/**
 * 스크롤 스파이 - IntersectionObserver를 사용한 현재 섹션 감지
 */
function initScrollSpy() {
    const sections = document.querySelectorAll('.content-section');
    const navItems = document.querySelectorAll('.section-nav-item');

    if (sections.length === 0 || navItems.length === 0) return;

    const observerOptions = {
        root: document.querySelector('.detail-main-content'),
        rootMargin: '-100px 0px -50% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;

                // 모든 네비게이션 아이템에서 active 제거
                navItems.forEach(item => {
                    item.classList.remove('active');
                });

                // 현재 섹션에 해당하는 네비게이션 아이템에 active 추가
                const activeNavItem = document.querySelector(`.section-nav-item[href="#${sectionId}"]`);
                if (activeNavItem) {
                    activeNavItem.classList.add('active');
                }
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * 스무스 스크롤 - 네비게이션 클릭 시 부드러운 스크롤
 */
function initSmoothScroll() {
    const navItems = document.querySelectorAll('.section-nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            const targetId = item.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                // 메인 콘텐츠 영역 내에서 스크롤
                const mainContent = document.querySelector('.detail-main-content');

                if (mainContent) {
                    const offsetTop = targetSection.offsetTop - 80;
                    mainContent.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                } else {
                    targetSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }

                // 모바일에서 네비게이션 닫기
                closeMobileNav();
            }
        });
    });
}

/**
 * 모바일 네비게이션 토글
 */
function initMobileNav() {
    const toggleBtn = document.getElementById('mobileNavToggle');
    const sectionNav = document.getElementById('sectionNav');
    const overlay = document.getElementById('sectionNavOverlay');

    if (!toggleBtn || !sectionNav) return;

    toggleBtn.addEventListener('click', () => {
        sectionNav.classList.toggle('mobile-active');
        if (overlay) {
            overlay.classList.toggle('active');
        }

        // 버튼 아이콘 변경
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        }
    });

    // 오버레이 클릭 시 닫기
    if (overlay) {
        overlay.addEventListener('click', closeMobileNav);
    }
}

/**
 * 모바일 네비게이션 닫기
 */
function closeMobileNav() {
    const sectionNav = document.getElementById('sectionNav');
    const overlay = document.getElementById('sectionNavOverlay');
    const toggleBtn = document.getElementById('mobileNavToggle');

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
 * 파일 업로드 UI
 */
function initFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');

    if (!uploadArea) return;

    // 드래그 앤 드롭 이벤트
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files);
        }
    });

    // 클릭 업로드
    uploadArea.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png';

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files);
            }
        });

        input.click();
    });
}

/**
 * 파일 업로드 처리 (향후 구현 예정)
 */
function handleFileUpload(files) {
    console.log('Files to upload:', files);

    // 향후 구현: API 호출로 파일 업로드
    // 현재는 알림만 표시
    alert(`${files.length}개의 파일이 선택되었습니다.\n파일 업로드 기능은 향후 구현 예정입니다.`);
}

/**
 * 파일 카드 렌더링 (향후 구현 예정)
 */
function renderFileCard(file) {
    const extension = file.name.split('.').pop().toLowerCase();
    let iconClass = 'fas fa-file';
    let typeClass = '';

    switch (extension) {
        case 'pdf':
            iconClass = 'fas fa-file-pdf';
            typeClass = 'pdf';
            break;
        case 'doc':
        case 'docx':
            iconClass = 'fas fa-file-word';
            typeClass = 'doc';
            break;
        case 'xls':
        case 'xlsx':
            iconClass = 'fas fa-file-excel';
            typeClass = 'xls';
            break;
        case 'jpg':
        case 'jpeg':
        case 'png':
            iconClass = 'fas fa-file-image';
            typeClass = 'img';
            break;
    }

    return `
        <div class="file-card">
            <div class="file-icon ${typeClass}">
                <i class="${iconClass}"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${formatFileSize(file.size)}</div>
            </div>
            <div class="file-actions">
                <button class="file-action-btn" title="다운로드">
                    <i class="fas fa-download"></i>
                </button>
                <button class="file-action-btn" title="삭제">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

/**
 * 파일 크기 포맷
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
