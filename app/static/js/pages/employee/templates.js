/**
 * Employee Form Templates
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 동적 필드 추가를 위한 HTML 템플릿 함수 모음
 */

/**
 * 학력 템플릿
 * @returns {string} HTML 템플릿
 */
export function getEducationTemplate() {
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
export function getCareerTemplate() {
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
export function getCertificateTemplate() {
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
export function getFamilyTemplate() {
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
export function getLanguageTemplate() {
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
export function getProjectTemplate() {
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
 * 수상내역 템플릿
 * @returns {string} HTML 템플릿
 */
export function getAwardTemplate() {
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">수상일</label>
                    <input type="date" name="award_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">수상명</label>
                    <input type="text" name="award_name[]" class="form-input" placeholder="수상명">
                </div>
                <div class="form-group">
                    <label class="form-label">수여기관</label>
                    <input type="text" name="award_issuer[]" class="form-input" placeholder="수여기관">
                </div>
                <div class="form-group">
                    <label class="form-label">비고</label>
                    <input type="text" name="award_note[]" class="form-input" placeholder="비고">
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

export default {
    getEducationTemplate,
    getCareerTemplate,
    getCertificateTemplate,
    getFamilyTemplate,
    getLanguageTemplate,
    getProjectTemplate,
    getAwardTemplate
};
