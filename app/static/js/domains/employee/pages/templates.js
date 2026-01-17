/**
 * Employee Form Templates
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 * Phase 8: FieldRegistry 통합 - 하드코딩 → 중앙 관리 전환
 *
 * 동적 필드 추가를 위한 HTML 템플릿 함수 모음
 *
 * 마이그레이션 전략:
 * - FieldRegistry 로드됨: TemplateGenerator로 동적 생성
 * - FieldRegistry 미로드: 기존 하드코딩 함수 사용 (fallback)
 */

import { TemplateGenerator } from '../../../shared/core/template-generator.js';

/**
 * FieldRegistry 기반 템플릿 생성 (우선)
 * @param {string} sectionId - 섹션 ID
 * @param {number} index - 항목 인덱스
 * @returns {string|null} HTML 템플릿 또는 null (fallback 필요)
 */
function getRegistryTemplate(sectionId, index = 0) {
    const FieldRegistry = window.FieldRegistry;
    if (!FieldRegistry || !FieldRegistry.isLoaded()) {
        return null; // fallback 필요
    }

    const section = FieldRegistry.getSection(sectionId);
    if (!section) {
        console.warn(`[templates] Section not found in registry: ${sectionId}`);
        return null;
    }

    return TemplateGenerator.generateDynamicTemplate(section, { index });
}

/**
 * 학력 템플릿
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getEducationTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('education', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">학교명</label>
                    <input type="text" name="education_school_name[]" class="form-input" placeholder="대학교명">
                </div>
                <div class="form-group">
                    <label class="form-label">학위</label>
                    <select name="education_degree[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="고졸">고등학교 졸업</option>
                        <option value="전문학사">전문학사</option>
                        <option value="학사">학사</option>
                        <option value="석사">석사</option>
                        <option value="박사">박사</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">전공</label>
                    <input type="text" name="education_major[]" class="form-input" placeholder="전공명">
                </div>
                <div class="form-group">
                    <label class="form-label">졸업년도</label>
                    <input type="text" name="education_graduation_year[]" class="form-input" placeholder="2020">
                </div>
                <div class="form-group">
                    <label class="form-label">학점</label>
                    <input type="text" name="education_gpa[]" class="form-input" placeholder="4.0/4.5">
                </div>
                <div class="form-group">
                    <label class="form-label">졸업유무</label>
                    <select name="education_graduation_status[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="졸업">졸업</option>
                        <option value="재학">재학</option>
                        <option value="휴학">휴학</option>
                        <option value="중퇴">중퇴</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">비고</label>
                    <input type="text" name="education_note[]" class="form-input" placeholder="비고">
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
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getCareerTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('career', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">회사명</label>
                    <input type="text" name="career_company_name[]" class="form-input" placeholder="회사명">
                </div>
                <div class="form-group">
                    <label class="form-label">부서</label>
                    <input type="text" name="career_department[]" class="form-input" placeholder="개발팀">
                </div>
                <div class="form-group">
                    <label class="form-label">직위</label>
                    <input type="text" name="career_position[]" class="form-input" placeholder="사원, 대리, 과장">
                </div>
                <div class="form-group">
                    <label class="form-label">직급</label>
                    <input type="text" name="career_job_grade[]" class="form-input" placeholder="L3, Senior">
                </div>
                <div class="form-group">
                    <label class="form-label">직책</label>
                    <input type="text" name="career_job_title[]" class="form-input" placeholder="팀장, 본부장">
                </div>
                <div class="form-group">
                    <label class="form-label">직무</label>
                    <input type="text" name="career_job_role[]" class="form-input" placeholder="인사기획, 회계관리">
                </div>
                <div class="form-group">
                    <label class="form-label">담당업무</label>
                    <input type="text" name="career_job_description[]" class="form-input" placeholder="웹 개발, API 설계">
                </div>
                <div class="form-group">
                    <label class="form-label">급여유형</label>
                    <select name="career_salary_type[]" class="form-input">
                        <option value="">선택</option>
                        <option value="연봉제">연봉제</option>
                        <option value="월급제">월급제</option>
                        <option value="시급제">시급제</option>
                        <option value="호봉제">호봉제</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">연봉</label>
                    <input type="number" name="career_salary[]" class="form-input" placeholder="연봉 (원)">
                </div>
                <div class="form-group">
                    <label class="form-label">월급</label>
                    <input type="number" name="career_monthly_salary[]" class="form-input" placeholder="월급 (원)">
                </div>
                <div class="form-group">
                    <label class="form-label">호봉</label>
                    <input type="number" name="career_pay_step[]" class="form-input" placeholder="1~50">
                </div>
                <div class="form-group">
                    <label class="form-label">입사일</label>
                    <input type="date" name="career_start_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">퇴사일</label>
                    <input type="date" name="career_end_date[]" class="form-input">
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
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getCertificateTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('certificate', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">자격증명</label>
                    <input type="text" name="certificate_certificate_name[]" class="form-input" placeholder="정보처리기사">
                </div>
                <div class="form-group">
                    <label class="form-label">발급기관</label>
                    <input type="text" name="certificate_issuing_organization[]" class="form-input" placeholder="한국산업인력공단">
                </div>
                <div class="form-group">
                    <label class="form-label">등급/점수</label>
                    <input type="text" name="certificate_grade[]" class="form-input" placeholder="1급, 900점">
                </div>
                <div class="form-group">
                    <label class="form-label">취득일</label>
                    <input type="date" name="certificate_acquisition_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">자격번호</label>
                    <input type="text" name="certificate_number[]" class="form-input" placeholder="자격번호">
                </div>
                <div class="form-group">
                    <label class="form-label">만료일</label>
                    <input type="date" name="certificate_expiry_date[]" class="form-input">
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
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getFamilyTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('family', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">관계</label>
                    <select name="family_relation[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="배우자">배우자</option>
                        <option value="자녀">자녀</option>
                        <option value="부">부</option>
                        <option value="모">모</option>
                        <option value="형제">형제</option>
                        <option value="자매">자매</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">성명</label>
                    <input type="text" name="family_name[]" class="form-input" placeholder="이름">
                </div>
                <div class="form-group">
                    <label class="form-label">생년월일</label>
                    <input type="date" name="family_birth_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">직업</label>
                    <input type="text" name="family_occupation[]" class="form-input" placeholder="직업">
                </div>
                <div class="form-group">
                    <label class="form-label">연락처</label>
                    <input type="tel" name="family_contact[]" class="form-input" placeholder="010-0000-0000">
                </div>
                <div class="form-group">
                    <label class="form-label">동거여부</label>
                    <select name="family_is_cohabitant[]" class="form-input">
                        <option value="">선택하세요</option>
                        <option value="동거">동거</option>
                        <option value="별거">별거</option>
                    </select>
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
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getLanguageTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('language', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">언어</label>
                    <select name="language_language_name[]" class="form-input">
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
                        <option value="원어민">원어민</option>
                        <option value="고급">상</option>
                        <option value="중급">중</option>
                        <option value="초급">하</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">시험명</label>
                    <input type="text" name="language_exam_name[]" class="form-input" placeholder="TOEIC, JLPT 등">
                </div>
                <div class="form-group">
                    <label class="form-label">점수/급수</label>
                    <input type="text" name="language_score[]" class="form-input" placeholder="900점, N1 등">
                </div>
                <div class="form-group">
                    <label class="form-label">취득일</label>
                    <input type="date" name="language_acquisition_date[]" class="form-input">
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
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getProjectTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('project', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
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
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getAwardTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('award', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">수상명 <span class="required">*</span></label>
                    <input type="text" name="award_name[]" class="form-input" placeholder="수상명">
                </div>
                <div class="form-group">
                    <label class="form-label">수상일</label>
                    <input type="date" name="award_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">수여기관</label>
                    <input type="text" name="award_institution[]" class="form-input" placeholder="수여기관">
                </div>
                <div class="form-group form-group-full">
                    <label class="form-label">비고</label>
                    <textarea name="award_note[]" class="form-input" rows="2" placeholder="수상 내용 및 비고"></textarea>
                </div>
            </div>
            <button type="button" class="btn-remove" title="삭제">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * 프로젝트 참여이력 템플릿
 * @param {number} index - 항목 인덱스 (FieldRegistry 사용 시)
 * @returns {string} HTML 템플릿
 */
export function getProjectParticipationTemplate(index = 0) {
    // FieldRegistry 우선 시도
    const registryTemplate = getRegistryTemplate('project_participation', index);
    if (registryTemplate) return registryTemplate;

    // Fallback: 하드코딩된 템플릿
    return `
        <div class="dynamic-item" data-index="0">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">사업명</label>
                    <input type="text" name="participation_project_name[]" class="form-input" placeholder="프로젝트/사업명">
                </div>
                <div class="form-group">
                    <label class="form-label">역할/직책</label>
                    <input type="text" name="participation_role[]" class="form-input" placeholder="PM, 개발자, 디자이너 등">
                </div>
                <div class="form-group">
                    <label class="form-label">시작일</label>
                    <input type="date" name="participation_start_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">종료일</label>
                    <input type="date" name="participation_end_date[]" class="form-input">
                </div>
                <div class="form-group">
                    <label class="form-label">담당업무</label>
                    <input type="text" name="participation_duty[]" class="form-input" placeholder="담당업무">
                </div>
                <div class="form-group">
                    <label class="form-label">발주처</label>
                    <input type="text" name="participation_client[]" class="form-input" placeholder="발주처/클라이언트">
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
    getAwardTemplate,
    getProjectParticipationTemplate
};
