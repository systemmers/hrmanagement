/**
 * Employee Form Page JavaScript
 * - 섹션 네비게이션 (SectionNav 컴포넌트 사용)
 * - 동적 필드 추가/삭제
 * - 사진 미리보기
 * - 폼 유효성 검사
 * - 주소 검색 (다음 주소 API)
 * - 파일 업로드
 */

import { SectionNav } from '../components/section-nav.js';
import { FileUpload } from '../components/file-upload.js';

document.addEventListener('DOMContentLoaded', () => {
    initSectionNavigation();
    initDynamicFields();
    initPhotoPreview();
    initFormValidation();
    initAddressSearch();
    initFileUpload();
});

/**
 * 섹션 네비게이션 초기화
 */
function initSectionNavigation() {
    const sectionNav = new SectionNav({
        sectionSelector: '.form-section',
        navItemSelector: '.section-nav-item',
        scrollContainerSelector: '.form-main-content',
        navId: 'sectionNav',
        overlayId: 'sectionNavOverlay',
        toggleBtnId: 'mobileNavToggle',
        scrollOffset: 80,
        rootMargin: '-100px 0px -50% 0px'
    });

    sectionNav.init();
}

/**
 * 동적 필드 추가/삭제 (학력, 경력, 자격증, 언어, 프로젝트, 가족)
 */
function initDynamicFields() {
    const addEducationBtn = document.getElementById('addEducation');
    if (addEducationBtn) {
        addEducationBtn.addEventListener('click', () => {
            addDynamicItem('educationList', getEducationTemplate());
        });
    }

    const addCareerBtn = document.getElementById('addCareer');
    if (addCareerBtn) {
        addCareerBtn.addEventListener('click', () => {
            addDynamicItem('careerList', getCareerTemplate());
        });
    }

    const addCertificateBtn = document.getElementById('addCertificate');
    if (addCertificateBtn) {
        addCertificateBtn.addEventListener('click', () => {
            addDynamicItem('certificateList', getCertificateTemplate());
        });
    }

    const addLanguageBtn = document.getElementById('addLanguage');
    if (addLanguageBtn) {
        addLanguageBtn.addEventListener('click', () => {
            addDynamicItem('languageList', getLanguageTemplate());
        });
    }

    const addProjectBtn = document.getElementById('addProject');
    if (addProjectBtn) {
        addProjectBtn.addEventListener('click', () => {
            addDynamicItem('projectList', getProjectTemplate());
        });
    }

    const addFamilyBtn = document.getElementById('addFamily');
    if (addFamilyBtn) {
        addFamilyBtn.addEventListener('click', () => {
            addDynamicItem('familyList', getFamilyTemplate());
        });
    }

    document.addEventListener('click', (e) => {
        if (e.target.closest('.btn-remove')) {
            const item = e.target.closest('.dynamic-item');
            if (item) {
                const list = item.parentElement;
                if (list.querySelectorAll('.dynamic-item').length > 1) {
                    item.remove();
                } else {
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
 * @param {string} listId - 목록 요소 ID
 * @param {string} template - HTML 템플릿
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
    newItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * 학력 템플릿
 * @returns {string} HTML 템플릿
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
 * @returns {string} HTML 템플릿
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
 * @returns {string} HTML 템플릿
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
 * @returns {string} HTML 템플릿
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
 * 언어능력 템플릿
 * @returns {string} HTML 템플릿
 */
function getLanguageTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">언어</label>
                    <select name="language_name[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="영어">영어</option>
                        <option value="일본어">일본어</option>
                        <option value="중국어">중국어</option>
                        <option value="스페인어">스페인어</option>
                        <option value="프랑스어">프랑스어</option>
                        <option value="독일어">독일어</option>
                        <option value="러시아어">러시아어</option>
                        <option value="베트남어">베트남어</option>
                        <option value="태국어">태국어</option>
                        <option value="기타">기타</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">수준</label>
                    <select name="language_level[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="native">원어민</option>
                        <option value="advanced">상</option>
                        <option value="intermediate">중</option>
                        <option value="basic">하</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">자격증/점수</label>
                    <input type="text" name="language_cert[]" class="form-input" placeholder="TOEIC 900, JLPT N1 등">
                </div>
                <div class="form-group">
                    <label class="form-label">취득일</label>
                    <input type="date" name="language_cert_date[]" class="form-input">
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * 프로젝트 템플릿
 * @returns {string} HTML 템플릿
 */
function getProjectTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">프로젝트명</label>
                    <input type="text" name="project_name[]" class="form-input" placeholder="프로젝트명">
                </div>
                <div class="form-group">
                    <label class="form-label">역할</label>
                    <input type="text" name="project_role[]" class="form-input" placeholder="PM, 개발자, 디자이너 등">
                </div>
                <div class="form-group">
                    <label class="form-label">시작일</label>
                    <input type="date" name="project_start[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">종료일</label>
                    <input type="date" name="project_end[]" class="form-input">
                </div>
                <div class="form-group form-group-full">
                    <label class="form-label">프로젝트 설명</label>
                    <textarea name="project_description[]" class="form-input" rows="2" placeholder="프로젝트 내용 및 성과"></textarea>
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

    form.addEventListener('input', (e) => {
        if (e.target.classList.contains('invalid') && e.target.value.trim()) {
            e.target.classList.remove('invalid');
        }
    });
}

/**
 * 주소 검색 (다음 주소 API)
 */
function initAddressSearch() {
    const searchBtn = document.getElementById('searchAddressBtn');
    const addressInput = document.getElementById('address');
    const detailedAddressInput = document.getElementById('detailed_address');

    if (!searchBtn || !addressInput) return;

    searchBtn.addEventListener('click', () => {
        // daum.Postcode는 전역으로 로드됨 (base.html)
        if (typeof daum === 'undefined' || !daum.Postcode) {
            alert('주소 검색 서비스를 불러오는 중입니다. 잠시 후 다시 시도해 주세요.');
            return;
        }

        new daum.Postcode({
            oncomplete: function(data) {
                // 도로명 주소 우선, 없으면 지번 주소
                const address = data.roadAddress || data.jibunAddress;
                addressInput.value = address;

                // 상세주소 입력란으로 포커스 이동
                if (detailedAddressInput) {
                    detailedAddressInput.focus();
                }
            },
            onclose: function(state) {
                // 사용자가 닫기 버튼을 눌렀을 때
                if (state === 'FORCE_CLOSE') {
                    // 아무 동작 없음
                }
            }
        }).open();
    });

    // 주소 입력란 클릭 시에도 검색 팝업
    addressInput.addEventListener('click', () => {
        searchBtn.click();
    });
}

/**
 * 파일 업로드 초기화
 */
function initFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');
    if (!uploadArea) return;

    // 직원 ID 추출 (수정 모드에서만 파일 업로드 가능)
    const form = document.getElementById('employeeForm');
    if (!form) return;

    const actionUrl = form.getAttribute('action');
    // /employees/123/update 형식에서 ID 추출
    const match = actionUrl.match(/\/employees\/(\d+)\/update/);
    if (!match) {
        // 신규 등록 모드에서는 파일 업로드 비활성화
        uploadArea.style.opacity = '0.5';
        uploadArea.style.pointerEvents = 'none';
        uploadArea.querySelector('.file-upload-text').textContent = '직원 등록 후 파일 업로드 가능';
        return;
    }

    const employeeId = parseInt(match[1], 10);

    new FileUpload({
        uploadAreaId: 'fileUploadArea',
        fileListId: 'fileList',
        employeeId: employeeId,
        onUploadComplete: (attachment) => {
            console.log('파일 업로드 완료:', attachment);
        }
    });
}
