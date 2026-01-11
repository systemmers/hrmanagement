/**
 * 패턴 규칙 및 노출 설정 관리 모듈
 *
 * 법인 설정 페이지의 패턴 규칙(사번, 이메일, 내선번호 등) 및
 * 노출 설정 탭 기능
 */

import { showToast } from '../../../../../shared/components/toast.js';
import { SettingsApi, VisibilityApi } from '../../../services/settings-api.js';

/**
 * 패턴 규칙 데이터 로드
 */
export async function loadPatternsData() {
    const content = document.getElementById('patterns-content');

    try {
        const response = await SettingsApi.getAll();
        applySettingsToForm(response.data);
        updatePreviews();
    } catch (error) {
        console.error('패턴 규칙 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 노출 설정 데이터 로드
 */
export async function loadVisibilityData() {
    const content = document.getElementById('visibility-content');

    try {
        const response = await VisibilityApi.get();
        applyVisibilityToForm(response.data);
    } catch (error) {
        console.error('노출 설정 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 콘텐츠 영역에 에러 메시지 표시
 * @param {Element} contentEl - 콘텐츠 엘리먼트
 */
function showContentError(contentEl) {
    if (!contentEl) return;
    contentEl.innerHTML = `
        <div class="category-empty">
            <i class="fas fa-exclamation-circle"></i>
            <p>데이터를 불러오는데 실패했습니다</p>
            <button class="btn btn-sm btn-secondary" onclick="location.reload()">다시 시도</button>
        </div>
    `;
}

/**
 * 설정값을 폼에 적용
 * @param {Object} settings - 설정 데이터
 */
function applySettingsToForm(settings) {
    // 회사 코드
    const companyCode = document.getElementById('company_code');
    if (companyCode && settings.company_code) {
        companyCode.value = settings.company_code;
    }

    // 사번 접두어
    const prefix = document.getElementById('employee_number_prefix');
    if (prefix && settings['employee_number.prefix']) {
        prefix.value = settings['employee_number.prefix'];
    }

    // 사번 구분자
    const separator = document.getElementById('employee_number_separator');
    if (separator && settings['employee_number.separator']) {
        separator.value = settings['employee_number.separator'];
    }

    // 사번 자릿수
    const digits = document.getElementById('employee_number_digits');
    if (digits && settings['employee_number.digits']) {
        digits.value = settings['employee_number.digits'];
    }

    // 사번 연도 포함
    const includeYear = document.getElementById('employee_number_include_year');
    if (includeYear) {
        includeYear.checked = settings['employee_number.include_year'] === true;
    }

    // 이메일 도메인
    const emailDomain = document.getElementById('email_domain');
    if (emailDomain && settings['email.domain']) {
        emailDomain.value = settings['email.domain'];
    }

    // 이메일 자동 생성
    const autoEmail = document.getElementById('auto_generate_email');
    if (autoEmail) {
        autoEmail.checked = settings['email.auto_generate'] === true;
    }

    // 이메일 포맷
    const emailFormat = document.getElementById('email_format');
    if (emailFormat && settings['email.format']) {
        emailFormat.value = settings['email.format'];
    }

    // 내선번호 자릿수
    const phoneDigits = document.getElementById('internal_phone_digits');
    if (phoneDigits && settings['internal_phone.digits']) {
        phoneDigits.value = settings['internal_phone.digits'];
    }

    // 내선번호 범위
    const extStart = document.getElementById('extension_range_start');
    if (extStart && settings['internal_phone.range_start']) {
        extStart.value = settings['internal_phone.range_start'];
    }

    const extEnd = document.getElementById('extension_range_end');
    if (extEnd && settings['internal_phone.range_end']) {
        extEnd.value = settings['internal_phone.range_end'];
    }

    // 급여 지급일
    const paymentDay = document.getElementById('payment_day');
    if (paymentDay && settings['payroll.payment_day']) {
        paymentDay.value = settings['payroll.payment_day'];
    }

    // IP 설정
    const ipAutoAssign = document.getElementById('ip_auto_assign');
    if (ipAutoAssign) {
        ipAutoAssign.checked = settings['ip.auto_assign'] === true;
    }

    const ipRangeStart = document.getElementById('ip_range_start');
    if (ipRangeStart && settings['ip.range_start']) {
        ipRangeStart.value = settings['ip.range_start'];
    }

    const ipRangeEnd = document.getElementById('ip_range_end');
    if (ipRangeEnd && settings['ip.range_end']) {
        ipRangeEnd.value = settings['ip.range_end'];
    }

    // 자산번호 설정
    const assetPrefix = document.getElementById('asset_number_prefix');
    if (assetPrefix && settings['asset_number.prefix']) {
        assetPrefix.value = settings['asset_number.prefix'];
    }

    const assetSeparator = document.getElementById('asset_number_separator');
    if (assetSeparator && settings['asset_number.separator']) {
        assetSeparator.value = settings['asset_number.separator'];
    }

    const assetDigits = document.getElementById('asset_number_digits');
    if (assetDigits && settings['asset_number.digits']) {
        assetDigits.value = settings['asset_number.digits'];
    }
}

/**
 * 노출 설정값을 폼에 적용
 * @param {Object} data - 노출 설정 데이터
 */
function applyVisibilityToForm(data) {
    const fields = [
        'salary_visibility',
        'show_salary_to_managers',
        'evaluation_visibility',
        'show_evaluation_to_managers',
        'org_chart_visibility',
        'contact_visibility',
        'document_visibility'
    ];

    fields.forEach(field => {
        const el = document.getElementById(field);
        // camelCase로 변환
        const camelField = field.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
        if (el && data[camelField] !== undefined) {
            el.checked = data[camelField];
        }
    });
}

/**
 * 미리보기 업데이트
 */
export function updatePreviews() {
    // 사번 미리보기
    const companyCode = document.getElementById('company_code')?.value || 'ABC';
    const prefix = document.getElementById('employee_number_prefix')?.value || 'EMP';
    const separator = document.getElementById('employee_number_separator')?.value || '-';
    const digits = parseInt(document.getElementById('employee_number_digits')?.value) || 6;
    const includeYear = document.getElementById('employee_number_include_year')?.checked;

    const employeePreview = document.getElementById('employee_number_preview');
    if (employeePreview) {
        const seq = '1'.padStart(digits, '0');
        const year = new Date().getFullYear();
        let preview = companyCode;
        if (separator) preview += separator;
        if (includeYear) preview += year + (separator || '');
        preview += prefix;
        if (separator) preview += separator;
        preview += seq;
        employeePreview.textContent = preview;
    }

    // 이메일 미리보기
    const emailDomain = document.getElementById('email_domain')?.value || 'company.co.kr';
    const emailFormat = document.getElementById('email_format')?.value || 'first.last';
    const emailPreview = document.getElementById('email_preview');
    if (emailPreview) {
        const formatExamples = {
            'first.last': 'hong.gildong',
            'last.first': 'gildong.hong',
            'firstlast': 'honggildong',
            'first_last': 'hong_gildong',
            'flast': 'ghong',
            'first': 'gildong'
        };
        const username = formatExamples[emailFormat] || 'hong.gildong';
        emailPreview.textContent = `${username}@${emailDomain}`;
    }

    // 내선번호 범위 미리보기
    const extStart = document.getElementById('extension_range_start')?.value || '100';
    const extEnd = document.getElementById('extension_range_end')?.value || '999';
    const extRangePreview = document.getElementById('extension_range_preview');
    if (extRangePreview) {
        extRangePreview.textContent = `${extStart} ~ ${extEnd}`;
    }

    // IP 범위 미리보기
    const ipStart = document.getElementById('ip_range_start')?.value || '192.168.1.100';
    const ipEnd = document.getElementById('ip_range_end')?.value || '192.168.1.200';
    const ipRangePreview = document.getElementById('ip_range_preview');
    if (ipRangePreview) {
        ipRangePreview.textContent = `${ipStart} ~ ${ipEnd}`;
    }

    // 자산번호 미리보기
    const assetPrefix = document.getElementById('asset_number_prefix')?.value || 'ASSET';
    const assetSeparator = document.getElementById('asset_number_separator')?.value || '-';
    const assetDigits = parseInt(document.getElementById('asset_number_digits')?.value) || 4;
    const assetPreview = document.getElementById('asset_number_preview');
    if (assetPreview) {
        const seq = '1'.padStart(assetDigits, '0');
        assetPreview.textContent = `${assetPrefix}${assetSeparator}${seq}`;
    }
}

/**
 * 섹션별 설정 데이터 추출
 * @param {string} section - 섹션 이름
 * @returns {Object} 섹션별 설정 데이터
 */
function getSectionSettings(section) {
    const sectionSettingsMap = {
        'employee_number': {
            'company_code': document.getElementById('company_code')?.value || '',
            'employee_number.prefix': document.getElementById('employee_number_prefix')?.value || '',
            'employee_number.separator': document.getElementById('employee_number_separator')?.value || '-',
            'employee_number.digits': document.getElementById('employee_number_digits')?.value || '6',
            'employee_number.include_year': document.getElementById('employee_number_include_year')?.checked || false
        },
        'email': {
            'email.domain': document.getElementById('email_domain')?.value || '',
            'email.auto_generate': document.getElementById('auto_generate_email')?.checked || false,
            'email.format': document.getElementById('email_format')?.value || 'first.last'
        },
        'internal_phone': {
            'internal_phone.digits': document.getElementById('internal_phone_digits')?.value || '4',
            'internal_phone.range_start': document.getElementById('extension_range_start')?.value || '',
            'internal_phone.range_end': document.getElementById('extension_range_end')?.value || ''
        },
        'payroll': {
            'payroll.payment_day': document.getElementById('payment_day')?.value || '25'
        },
        'ip': {
            'ip.auto_assign': document.getElementById('ip_auto_assign')?.checked || false,
            'ip.range_start': document.getElementById('ip_range_start')?.value || '',
            'ip.range_end': document.getElementById('ip_range_end')?.value || ''
        },
        'asset_number': {
            'asset_number.prefix': document.getElementById('asset_number_prefix')?.value || '',
            'asset_number.separator': document.getElementById('asset_number_separator')?.value || '-',
            'asset_number.digits': document.getElementById('asset_number_digits')?.value || '4'
        }
    };

    return sectionSettingsMap[section] || {};
}

/**
 * 섹션 이름 한글 매핑
 */
const SECTION_LABELS = {
    'employee_number': '사번 규칙',
    'email': '이메일 설정',
    'internal_phone': '내선번호 설정',
    'payroll': '급여 설정',
    'ip': 'IP 주소 관리',
    'asset_number': '자산번호 설정'
};

/**
 * 섹션별 설정 저장
 * @param {string} section - 섹션 이름
 */
async function saveSectionSettings(section) {
    const btn = document.querySelector(`.section-save-btn[data-section="${section}"]`);
    const originalContent = btn?.innerHTML;

    try {
        // 버튼 로딩 상태
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>저장 중...</span>';
        }

        const settings = getSectionSettings(section);
        await SettingsApi.saveAll(settings);

        const label = SECTION_LABELS[section] || section;
        showToast(`${label}이(가) 저장되었습니다`, 'success');
    } catch (error) {
        showToast(error.message || '저장에 실패했습니다', 'error');
    } finally {
        // 버튼 복원
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    }
}

/**
 * 패턴 규칙 저장 핸들러 초기화
 */
export function initPatternsHandlers() {
    // 미리보기 업데이트를 트리거하는 모든 필드
    const previewFields = [
        'company_code', 'employee_number_prefix', 'employee_number_separator',
        'employee_number_digits', 'employee_number_include_year',
        'email_domain', 'email_format', 'auto_generate_email',
        'extension_range_start', 'extension_range_end',
        'ip_range_start', 'ip_range_end',
        'asset_number_prefix', 'asset_number_separator', 'asset_number_digits'
    ];

    previewFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', updatePreviews);
            el.addEventListener('change', updatePreviews);
        }
    });

    // 섹션별 저장 버튼 이벤트
    document.querySelectorAll('.section-save-btn[data-section]').forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            saveSectionSettings(section);
        });
    });
}

/**
 * 노출 설정 핸들러 초기화
 */
export function initVisibilityHandlers() {
    // 저장 버튼
    const saveBtn = document.getElementById('save-visibility');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            try {
                const settings = {
                    salaryVisibility: document.getElementById('salary_visibility')?.checked,
                    showSalaryToManagers: document.getElementById('show_salary_to_managers')?.checked,
                    evaluationVisibility: document.getElementById('evaluation_visibility')?.checked,
                    showEvaluationToManagers: document.getElementById('show_evaluation_to_managers')?.checked,
                    orgChartVisibility: document.getElementById('org_chart_visibility')?.checked,
                    contactVisibility: document.getElementById('contact_visibility')?.checked,
                    documentVisibility: document.getElementById('document_visibility')?.checked
                };

                await VisibilityApi.save(settings);
                showToast('노출 설정이 저장되었습니다', 'success');
            } catch (error) {
                showToast(error.message || '저장에 실패했습니다', 'error');
            }
        });
    }

    // 초기화 버튼
    const resetBtn = document.getElementById('reset-visibility');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (!confirm('모든 노출 설정을 기본값으로 초기화하시겠습니까?')) return;

            try {
                const data = await VisibilityApi.reset();
                applyVisibilityToForm(data);
                showToast('기본값으로 초기화되었습니다', 'success');
            } catch (error) {
                showToast(error.message || '초기화에 실패했습니다', 'error');
            }
        });
    }
}

/**
 * 패턴 규칙 탭 초기화 엔트리 포인트
 */
export async function initPatternsTab() {
    initPatternsHandlers();
    await loadPatternsData();
}

/**
 * 노출 설정 탭 초기화 엔트리 포인트
 */
export async function initVisibilityTab() {
    initVisibilityHandlers();
    await loadVisibilityData();
}
