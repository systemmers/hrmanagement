/**
 * Employee Form Page JavaScript
 * - 섹션 네비게이션 스크롤 스파이
 * - 스무스 스크롤 네비게이션
 * - 모바일 메뉴 토글
 * - 동적 필드 추가/삭제
 * - 사진 미리보기
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollSpy();
    initSmoothScroll();
    initMobileNav();
    initDynamicFields();
    initPhotoPreview();
    initFormValidation();
});

/**
 * 스크롤 스파이 - IntersectionObserver를 사용한 현재 섹션 감지
 */
function initScrollSpy() {
    const sections = document.querySelectorAll('.form-section');
    const navItems = document.querySelectorAll('.section-nav-item');

    if (sections.length === 0 || navItems.length === 0) return;

    const observerOptions = {
        root: document.querySelector('.form-main-content'),
        rootMargin: '-100px 0px -50% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;

                navItems.forEach(item => {
                    item.classList.remove('active');
                });

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
                const mainContent = document.querySelector('.form-main-content');

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

        const icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        }
    });

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
 * 동적 필드 추가/삭제 (학력, 경력, 자격증, 가족)
 */
function initDynamicFields() {
    // 학력 추가
    const addEducationBtn = document.getElementById('addEducation');
    if (addEducationBtn) {
        addEducationBtn.addEventListener('click', () => {
            addDynamicItem('educationList', getEducationTemplate());
        });
    }

    // 경력 추가
    const addCareerBtn = document.getElementById('addCareer');
    if (addCareerBtn) {
        addCareerBtn.addEventListener('click', () => {
            addDynamicItem('careerList', getCareerTemplate());
        });
    }

    // 자격증 추가
    const addCertificateBtn = document.getElementById('addCertificate');
    if (addCertificateBtn) {
        addCertificateBtn.addEventListener('click', () => {
            addDynamicItem('certificateList', getCertificateTemplate());
        });
    }

    // 가족 추가
    const addFamilyBtn = document.getElementById('addFamily');
    if (addFamilyBtn) {
        addFamilyBtn.addEventListener('click', () => {
            addDynamicItem('familyList', getFamilyTemplate());
        });
    }

    // 삭제 버튼 이벤트 (이벤트 위임)
    document.addEventListener('click', (e) => {
        if (e.target.closest('.btn-remove')) {
            const item = e.target.closest('.dynamic-item');
            if (item) {
                const list = item.parentElement;
                if (list.querySelectorAll('.dynamic-item').length > 1) {
                    item.remove();
                } else {
                    // 마지막 항목은 삭제하지 않고 값만 초기화
                    const inputs = item.querySelectorAll('input, select');
                    inputs.forEach(input => {
                        if (input.tagName === 'SELECT') {
                            input.selectedIndex = 0;
                        } else {
                            input.value = '';
                        }
                    });
                }
            }
        }
    });
}

/**
 * 동적 항목 추가
 */
function addDynamicItem(listId, template) {
    const list = document.getElementById(listId);
    if (!list) return;

    const items = list.querySelectorAll('.dynamic-item');
    const newIndex = items.length;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = template.replace(/\[0\]/g, `[${newIndex}]`);

    const newItem = tempDiv.firstElementChild;
    newItem.setAttribute('data-index', newIndex);

    list.appendChild(newItem);

    // 새 항목으로 스크롤
    newItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * 학력 템플릿
 */
function getEducationTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">학교명</label>
                    <input type="text" name="education_school[]" class="form-input" placeholder="대학교명">
                </div>
                <div class="form-group">
                    <label class="form-label">학위</label>
                    <select name="education_degree[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="highschool">고등학교 졸업</option>
                        <option value="associate">전문학사</option>
                        <option value="bachelor">학사</option>
                        <option value="master">석사</option>
                        <option value="doctor">박사</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">전공</label>
                    <input type="text" name="education_major[]" class="form-input" placeholder="전공명">
                </div>
                <div class="form-group">
                    <label class="form-label">졸업년도</label>
                    <input type="text" name="education_year[]" class="form-input" placeholder="2020">
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * 경력 템플릿
 */
function getCareerTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">회사명</label>
                    <input type="text" name="career_company[]" class="form-input" placeholder="회사명">
                </div>
                <div class="form-group">
                    <label class="form-label">직급/직책</label>
                    <input type="text" name="career_position[]" class="form-input" placeholder="대리">
                </div>
                <div class="form-group">
                    <label class="form-label">담당업무</label>
                    <input type="text" name="career_duty[]" class="form-input" placeholder="웹 개발">
                </div>
                <div class="form-group">
                    <label class="form-label">재직기간</label>
                    <input type="text" name="career_period[]" class="form-input" placeholder="2020.01 ~ 2023.12">
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * 자격증 템플릿
 */
function getCertificateTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">자격증명</label>
                    <input type="text" name="cert_name[]" class="form-input" placeholder="정보처리기사">
                </div>
                <div class="form-group">
                    <label class="form-label">발급기관</label>
                    <input type="text" name="cert_issuer[]" class="form-input" placeholder="한국산업인력공단">
                </div>
                <div class="form-group">
                    <label class="form-label">취득일</label>
                    <input type="date" name="cert_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">자격번호</label>
                    <input type="text" name="cert_number[]" class="form-input" placeholder="자격번호">
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * 가족 템플릿
 */
function getFamilyTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">관계</label>
                    <select name="family_relation[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="spouse">배우자</option>
                        <option value="child">자녀</option>
                        <option value="parent">부모</option>
                        <option value="sibling">형제/자매</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">성명</label>
                    <input type="text" name="family_name[]" class="form-input" placeholder="이름">
                </div>
                <div class="form-group">
                    <label class="form-label">생년월일</label>
                    <input type="date" name="family_birth[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">직업</label>
                    <input type="text" name="family_job[]" class="form-input" placeholder="직업">
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * 사진 미리보기
 */
function initPhotoPreview() {
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');

    if (!photoInput || !photoPreview) return;

    photoInput.addEventListener('input', (e) => {
        const url = e.target.value.trim();

        if (url) {
            // URL 유효성 검사 (간단한 검사)
            const img = new Image();
            img.onload = () => {
                photoPreview.innerHTML = `<img src="${url}" alt="프로필 사진" id="previewImage">`;
            };
            img.onerror = () => {
                photoPreview.innerHTML = `
                    <div class="photo-placeholder">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>이미지 로드 실패</span>
                    </div>
                `;
            };
            img.src = url;
        } else {
            photoPreview.innerHTML = `
                <div class="photo-placeholder">
                    <i class="fas fa-user"></i>
                    <span>사진 미등록</span>
                </div>
            `;
        }
    });
}

/**
 * 폼 유효성 검사
 */
function initFormValidation() {
    const form = document.getElementById('employeeForm');

    if (!form) return;

    form.addEventListener('submit', (e) => {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        let firstInvalidField = null;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('invalid');
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
            } else {
                field.classList.remove('invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();

            if (firstInvalidField) {
                firstInvalidField.focus();
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            alert('필수 입력 항목을 모두 입력해 주세요.');
        }
    });

    // 입력 시 invalid 클래스 제거
    form.addEventListener('input', (e) => {
        if (e.target.classList.contains('invalid') && e.target.value.trim()) {
            e.target.classList.remove('invalid');
        }
    });
}
