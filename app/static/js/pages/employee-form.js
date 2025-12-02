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
    initProfilePhotoUpload();
    initBusinessCardUpload();
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
 * 사진 미리보기 (URL 입력용 - 신규 등록 모드)
 */
function initPhotoPreview() {
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');

    if (!photoInput || !photoPreview) return;

    // URL 타입 input인 경우만 처리 (신규 등록 모드)
    if (photoInput.type !== 'url') return;

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
 * 프로필 사진 파일 업로드 초기화 (수정 모드)
 */
function initProfilePhotoUpload() {
    const selectPhotoBtn = document.getElementById('selectPhotoBtn');
    const deletePhotoBtn = document.getElementById('deletePhotoBtn');
    const photoFileInput = document.getElementById('photoFile');
    const photoHiddenInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');

    if (!selectPhotoBtn || !photoFileInput) return;

    // 직원 ID 추출
    const employeeId = getEmployeeIdFromForm();
    if (!employeeId) return;

    // 사진 선택 버튼 클릭
    selectPhotoBtn.addEventListener('click', () => {
        photoFileInput.click();
    });

    // 파일 선택 시 업로드
    photoFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 유효성 검사
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            showToast('이미지 파일만 업로드 가능합니다. (JPG, PNG, GIF, WebP)', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            showToast('파일 크기가 5MB를 초과합니다.', 'error');
            return;
        }

        // 업로드 진행
        try {
            selectPhotoBtn.disabled = true;
            selectPhotoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 업로드 중...';

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`/api/employees/${employeeId}/profile-photo`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // 미리보기 업데이트
                photoPreview.innerHTML = `<img src="${result.file_path}" alt="프로필 사진" id="previewImage">`;
                if (photoHiddenInput) {
                    photoHiddenInput.value = result.file_path;
                }

                // 삭제 버튼 추가
                addDeletePhotoButton();

                showToast('프로필 사진이 업로드되었습니다.', 'success');
            } else {
                showToast(result.error || '업로드 실패', 'error');
            }
        } catch (error) {
            console.error('Profile photo upload error:', error);
            showToast('업로드 중 오류가 발생했습니다.', 'error');
        } finally {
            selectPhotoBtn.disabled = false;
            selectPhotoBtn.innerHTML = '<i class="fas fa-camera"></i> 사진 선택';
            photoFileInput.value = '';
        }
    });

    // 삭제 버튼 이벤트
    if (deletePhotoBtn) {
        deletePhotoBtn.addEventListener('click', async () => {
            if (!confirm('프로필 사진을 삭제하시겠습니까?')) return;

            try {
                deletePhotoBtn.disabled = true;

                const response = await fetch(`/api/employees/${employeeId}/profile-photo`, {
                    method: 'DELETE'
                });

                const result = await response.json();

                if (result.success) {
                    // 미리보기 초기화
                    photoPreview.innerHTML = `
                        <div class="photo-placeholder" id="photoPlaceholder">
                            <i class="fas fa-user"></i>
                            <span>사진 미등록</span>
                        </div>
                    `;
                    if (photoHiddenInput) {
                        photoHiddenInput.value = '';
                    }
                    deletePhotoBtn.remove();
                    showToast('프로필 사진이 삭제되었습니다.', 'success');
                } else {
                    showToast(result.error || '삭제 실패', 'error');
                }
            } catch (error) {
                console.error('Profile photo delete error:', error);
                showToast('삭제 중 오류가 발생했습니다.', 'error');
            } finally {
                deletePhotoBtn.disabled = false;
            }
        });
    }
}

/**
 * 삭제 버튼 동적 추가
 */
function addDeletePhotoButton() {
    const buttonsContainer = document.querySelector('.photo-upload-buttons');
    if (!buttonsContainer) return;

    // 이미 삭제 버튼이 있으면 무시
    if (document.getElementById('deletePhotoBtn')) return;

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.id = 'deletePhotoBtn';
    deleteBtn.className = 'btn btn-outline-danger btn-sm';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i> 삭제';

    const employeeId = getEmployeeIdFromForm();

    deleteBtn.addEventListener('click', async () => {
        if (!confirm('프로필 사진을 삭제하시겠습니까?')) return;

        try {
            deleteBtn.disabled = true;

            const response = await fetch(`/api/employees/${employeeId}/profile-photo`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                const photoPreview = document.getElementById('photoPreview');
                const photoHiddenInput = document.getElementById('photo');

                photoPreview.innerHTML = `
                    <div class="photo-placeholder" id="photoPlaceholder">
                        <i class="fas fa-user"></i>
                        <span>사진 미등록</span>
                    </div>
                `;
                if (photoHiddenInput) {
                    photoHiddenInput.value = '';
                }
                deleteBtn.remove();
                showToast('프로필 사진이 삭제되었습니다.', 'success');
            } else {
                showToast(result.error || '삭제 실패', 'error');
            }
        } catch (error) {
            console.error('Profile photo delete error:', error);
            showToast('삭제 중 오류가 발생했습니다.', 'error');
        } finally {
            deleteBtn.disabled = false;
        }
    });

    buttonsContainer.appendChild(deleteBtn);
}

/**
 * 명함 업로드 초기화
 */
function initBusinessCardUpload() {
    const frontFileInput = document.getElementById('businessCardFrontFile');
    const backFileInput = document.getElementById('businessCardBackFile');

    if (!frontFileInput && !backFileInput) return;

    const employeeId = getEmployeeIdFromForm();
    if (!employeeId) return;

    // 앞면 업로드
    if (frontFileInput) {
        frontFileInput.addEventListener('change', (e) => handleBusinessCardUpload(e, 'front', employeeId));
    }

    // 뒷면 업로드
    if (backFileInput) {
        backFileInput.addEventListener('change', (e) => handleBusinessCardUpload(e, 'back', employeeId));
    }

    // 삭제 버튼 이벤트
    document.querySelectorAll('.delete-card-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const side = btn.dataset.side;
            if (!confirm(`명함 ${side === 'front' ? '앞면' : '뒷면'}을 삭제하시겠습니까?`)) return;

            try {
                btn.disabled = true;

                const response = await fetch(`/api/employees/${employeeId}/business-card/${side}`, {
                    method: 'DELETE'
                });

                const result = await response.json();

                if (result.success) {
                    const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
                    const preview = document.getElementById(previewId);
                    if (preview) {
                        preview.innerHTML = `
                            <div class="card-placeholder">
                                <i class="fas fa-id-card"></i>
                                <span>${side === 'front' ? '앞면' : '뒷면'} 미등록</span>
                            </div>
                        `;
                    }
                    btn.remove();
                    showToast(`명함 ${side === 'front' ? '앞면' : '뒷면'}이 삭제되었습니다.`, 'success');
                } else {
                    showToast(result.error || '삭제 실패', 'error');
                }
            } catch (error) {
                console.error('Business card delete error:', error);
                showToast('삭제 중 오류가 발생했습니다.', 'error');
            } finally {
                btn.disabled = false;
            }
        });
    });
}

/**
 * 명함 업로드 처리
 */
async function handleBusinessCardUpload(e, side, employeeId) {
    const file = e.target.files[0];
    if (!file) return;

    // 파일 유효성 검사
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('이미지 파일만 업로드 가능합니다. (JPG, PNG, GIF, WebP)', 'error');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('파일 크기가 5MB를 초과합니다.', 'error');
        return;
    }

    const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
    const preview = document.getElementById(previewId);

    try {
        if (preview) {
            preview.innerHTML = '<div class="card-loading"><i class="fas fa-spinner fa-spin"></i></div>';
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('side', side);

        const response = await fetch(`/api/employees/${employeeId}/business-card`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            if (preview) {
                preview.innerHTML = `<img src="${result.file_path}" alt="명함 ${side === 'front' ? '앞면' : '뒷면'}">`;
            }

            // 삭제 버튼 추가
            addBusinessCardDeleteButton(side, employeeId);

            showToast(`명함 ${side === 'front' ? '앞면' : '뒷면'}이 업로드되었습니다.`, 'success');
        } else {
            if (preview) {
                preview.innerHTML = `
                    <div class="card-placeholder">
                        <i class="fas fa-id-card"></i>
                        <span>${side === 'front' ? '앞면' : '뒷면'} 미등록</span>
                    </div>
                `;
            }
            showToast(result.error || '업로드 실패', 'error');
        }
    } catch (error) {
        console.error('Business card upload error:', error);
        if (preview) {
            preview.innerHTML = `
                <div class="card-placeholder">
                    <i class="fas fa-id-card"></i>
                    <span>${side === 'front' ? '앞면' : '뒷면'} 미등록</span>
                </div>
            `;
        }
        showToast('업로드 중 오류가 발생했습니다.', 'error');
    } finally {
        e.target.value = '';
    }
}

/**
 * 명함 삭제 버튼 동적 추가
 */
function addBusinessCardDeleteButton(side, employeeId) {
    const item = document.querySelector(`.business-card-item[data-side="${side}"]`);
    if (!item) return;

    const actionsContainer = item.querySelector('.card-actions');
    if (!actionsContainer) return;

    // 이미 삭제 버튼이 있으면 무시
    if (actionsContainer.querySelector('.delete-card-btn')) return;

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn btn-outline-danger btn-sm delete-card-btn';
    deleteBtn.dataset.side = side;
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';

    deleteBtn.addEventListener('click', async () => {
        if (!confirm(`명함 ${side === 'front' ? '앞면' : '뒷면'}을 삭제하시겠습니까?`)) return;

        try {
            deleteBtn.disabled = true;

            const response = await fetch(`/api/employees/${employeeId}/business-card/${side}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                const previewId = side === 'front' ? 'businessCardFrontPreview' : 'businessCardBackPreview';
                const preview = document.getElementById(previewId);
                if (preview) {
                    preview.innerHTML = `
                        <div class="card-placeholder">
                            <i class="fas fa-id-card"></i>
                            <span>${side === 'front' ? '앞면' : '뒷면'} 미등록</span>
                        </div>
                    `;
                }
                deleteBtn.remove();
                showToast(`명함 ${side === 'front' ? '앞면' : '뒷면'}이 삭제되었습니다.`, 'success');
            } else {
                showToast(result.error || '삭제 실패', 'error');
            }
        } catch (error) {
            console.error('Business card delete error:', error);
            showToast('삭제 중 오류가 발생했습니다.', 'error');
        } finally {
            deleteBtn.disabled = false;
        }
    });

    actionsContainer.appendChild(deleteBtn);
}

/**
 * 폼에서 직원 ID 추출
 */
function getEmployeeIdFromForm() {
    const form = document.getElementById('employeeForm');
    if (!form) return null;

    const actionUrl = form.getAttribute('action');
    const match = actionUrl.match(/\/employees\/(\d+)\/update/);
    return match ? parseInt(match[1], 10) : null;
}

/**
 * Toast 메시지 표시
 */
function showToast(message, type = 'info') {
    // Toast 컴포넌트가 있으면 사용
    if (typeof Toast !== 'undefined' && Toast.show) {
        Toast.show(message, type);
        return;
    }

    // 기본 alert 대체
    if (type === 'error') {
        alert('오류: ' + message);
    } else {
        alert(message);
    }
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
