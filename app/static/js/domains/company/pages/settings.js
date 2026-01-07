/**
 * 법인 설정 페이지 컨트롤러
 */

import { ClassificationApi, SettingsApi, VisibilityApi, DocumentsApi } from '../services/corporate-settings-api.js';
import { Accordion } from '../../shared/components/accordion.js';
import { MAX_FILE_SIZE, MAX_FILE_SIZE_MB, FILE_UPLOAD_MESSAGES } from '../../shared/constants/file-upload-constants.js';

const state = {
    activeTab: 'basic',
    loadedTabs: new Set(['basic'])
};

const TOAST_COLORS = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6'
};

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

function initTabs() {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(`tab-${hash}`)) {
        state.activeTab = hash;
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    switchTab(state.activeTab);
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        const isActive = btn.dataset.tab === tabId;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-selected', isActive);
    });

    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `tab-${tabId}`);
    });

    state.activeTab = tabId;
    window.location.hash = tabId;

    if (!state.loadedTabs.has(tabId)) {
        loadTabData(tabId);
    }
}

/**
 * 탭 데이터 로드
 * @param {string} tabId - 탭 ID
 */
async function loadTabData(tabId) {
    switch (tabId) {
        case 'organization':
            await loadOrganizationData();
            break;
        case 'patterns':
            await loadPatternsData();
            break;
        case 'employment':
            await loadEmploymentData();
            break;
        case 'documents':
            await loadDocumentsData();
            break;
        case 'visibility':
            await loadVisibilityData();
            break;
    }
    state.loadedTabs.add(tabId);
}

async function loadOrganizationData() {
    const content = document.getElementById('organization-content');

    try {
        const response = await ClassificationApi.getOrganization();
        Object.entries(response.data).forEach(([category, options]) => {
            renderCategoryList(`#tab-organization [data-category="${category}"]`, category, options);
        });
    } catch (error) {
        console.error('조직 구조 데이터 로드 실패:', error);
        showContentError(content);
    }
}

async function loadEmploymentData() {
    const content = document.getElementById('employment-content');

    try {
        const response = await ClassificationApi.getEmployment();
        Object.entries(response.data).forEach(([category, options]) => {
            renderCategoryList(`#tab-employment [data-category="${category}"]`, category, options);
        });
    } catch (error) {
        console.error('고용 정책 데이터 로드 실패:', error);
        showContentError(content);
    }
}

async function loadPatternsData() {
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

async function loadVisibilityData() {
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
 * 법인 서류 데이터 로드
 */
async function loadDocumentsData() {
    const content = document.getElementById('documents-content');

    try {
        const [documentsResponse, statisticsResponse] = await Promise.all([
            DocumentsApi.getAll(),
            DocumentsApi.getStatistics()
        ]);

        // API 응답 구조: { success: true, data: { documents: [...], statistics: {...} } }
        const responseData = documentsResponse.data || documentsResponse;
        const documents = Array.isArray(responseData) ? responseData : (responseData.documents || []);
        const statistics = statisticsResponse.data || statisticsResponse;

        // 통계 업데이트
        updateDocumentStatistics(statistics);

        // 카테고리별 문서 렌더링 (템플릿과 일치)
        const categories = ['required', 'payroll', 'welfare', 'security', 'contract', 'other'];
        categories.forEach(category => {
            // benefits와 welfare 매핑 (DB에서 benefits로 저장된 경우 대응)
            const categoryDocs = documents.filter(d =>
                d.category === category ||
                (category === 'welfare' && d.category === 'benefits')
            );
            renderDocumentList(category, categoryDocs);
        });
    } catch (error) {
        console.error('법인 서류 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 문서 통계 업데이트
 * @param {Object} statistics - 통계 데이터
 */
function updateDocumentStatistics(statistics) {
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        const label = item.querySelector('.stat-label')?.textContent;
        const valueEl = item.querySelector('.stat-value');
        if (!valueEl) return;

        if (label?.includes('전체')) {
            valueEl.textContent = statistics.total || 0;
        } else if (label?.includes('필수')) {
            valueEl.textContent = statistics.required || 0;
        } else if (label?.includes('만료')) {
            valueEl.textContent = statistics.expiringSoon || 0;
        }
    });
}

/**
 * 문서 리스트 렌더링
 * @param {string} category - 카테고리
 * @param {Array} documents - 문서 목록
 */
function renderDocumentList(category, documents) {
    const listContainer = document.querySelector(`.document-list[data-category="${category}"]`);
    if (!listContainer) return;

    if (documents.length === 0) {
        listContainer.innerHTML = `
            <div class="document-empty">
                <i class="fas fa-folder-open"></i>
                <p>등록된 서류가 없습니다</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = documents.map(doc => {
        const expiresText = doc.expiresAt ? formatDate(doc.expiresAt) : '';
        const isExpiring = doc.expiresAt && isExpiringSoon(doc.expiresAt);

        return `
            <div class="document-item ${isExpiring ? 'is-expiring' : ''}" data-id="${doc.id}">
                <div class="document-icon">
                    <i class="fas ${getFileIcon(doc.fileType)}"></i>
                </div>
                <div class="document-info">
                    <span class="document-title">${escapeHtml(doc.title)}</span>
                    <span class="document-meta">
                        ${doc.version ? `v${doc.version}` : ''}
                        ${expiresText ? `<span class="document-expires ${isExpiring ? 'text-danger' : ''}">${expiresText} 만료</span>` : ''}
                    </span>
                </div>
                <div class="document-actions">
                    <button class="btn-icon" data-action="download" title="다운로드">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn-icon" data-action="edit" title="수정">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" data-action="delete" title="삭제">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 파일 타입에 따른 아이콘 반환
 * @param {string} fileType - 파일 타입
 * @returns {string} 아이콘 클래스
 */
function getFileIcon(fileType) {
    const iconMap = {
        'application/pdf': 'fa-file-pdf',
        'image/jpeg': 'fa-file-image',
        'image/png': 'fa-file-image',
        'application/msword': 'fa-file-word',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fa-file-word',
        'application/vnd.ms-excel': 'fa-file-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'fa-file-excel'
    };
    return iconMap[fileType] || 'fa-file';
}

/**
 * 날짜 포맷팅
 * @param {string} dateStr - 날짜 문자열
 * @returns {string} 포맷된 날짜
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
}

/**
 * 만료 임박 여부 확인
 * @param {string} dateStr - 만료일
 * @returns {boolean} 30일 이내 만료 여부
 */
function isExpiringSoon(dateStr) {
    const expires = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil((expires - now) / (1000 * 60 * 60 * 24));
    return diffDays > 0 && diffDays <= 30;
}

/**
 * 카테고리 리스트 렌더링
 * @param {string} selector - 섹션 셀렉터
 * @param {string} category - 카테고리 코드
 * @param {Array} options - 옵션 목록
 */
function renderCategoryList(selector, category, options) {
    const section = document.querySelector(selector);
    if (!section) return;

    const listContainer = section.querySelector('.category-list');
    const countEl = section.querySelector('.category-count');

    // 옵션 개수 표시
    countEl.textContent = `(${options.length}개)`;

    if (options.length === 0) {
        listContainer.innerHTML = `
            <div class="category-empty">
                <i class="fas fa-inbox"></i>
                <p>등록된 항목이 없습니다</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = options.map(option => {
        return `
            <div class="category-item" data-id="${option.id}" data-value="${option.value}">
                <div class="category-item-content">
                    <span class="category-item-value">${escapeHtml(option.label || option.value)}</span>
                </div>
                <div class="category-item-actions">
                    <button class="btn-icon" data-action="edit" title="수정">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" data-action="delete" title="삭제">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
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
function updatePreviews() {
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
 * 카테고리 이벤트 핸들러 초기화
 */
function initCategoryHandlers() {
    // 추가 버튼
    document.querySelectorAll('.category-section [data-action="add"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const section = e.target.closest('.category-section');
            const form = section.querySelector('.add-item-form');
            form.classList.remove('d-none');
            form.querySelector('input').focus();
        });
    });

    // 저장/취소 버튼
    document.querySelectorAll('.add-item-form [data-action="save"]').forEach(btn => {
        btn.addEventListener('click', (e) => handleAddItem(e));
    });

    document.querySelectorAll('.add-item-form [data-action="cancel"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const form = e.target.closest('.add-item-form');
            form.classList.add('d-none');
            form.querySelector('input').value = '';
        });
    });

    // 리스트 아이템 이벤트 위임
    document.querySelectorAll('.category-list').forEach(list => {
        list.addEventListener('click', handleListItemAction);
        list.addEventListener('change', handleListItemToggle);
    });
}

/**
 * 항목 추가 핸들러
 * @param {Event} e - 클릭 이벤트
 */
async function handleAddItem(e) {
    const form = e.target.closest('.add-item-form');
    const section = form.closest('.category-section');
    const category = section.dataset.category;
    const input = form.querySelector('input[data-field="value"]');
    const value = input.value.trim();

    if (!value) {
        showToast('값을 입력해주세요', 'warning');
        return;
    }

    try {
        const result = await ClassificationApi.add(category, { value });
        showToast('항목이 추가되었습니다', 'success');

        // 폼 리셋
        input.value = '';
        form.classList.add('d-none');

        // 리스트 갱신
        await refreshCategory(section.closest('.tab-panel').id.replace('tab-', ''), category);
    } catch (error) {
        showToast(error.message || '추가에 실패했습니다', 'error');
    }
}

/**
 * 리스트 아이템 액션 핸들러
 * @param {Event} e - 클릭 이벤트
 */
async function handleListItemAction(e) {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;
    const item = btn.closest('.category-item');
    const section = btn.closest('.category-section');
    const category = section.dataset.category;
    const optionId = item?.dataset.id;

    switch (action) {
        case 'edit':
            startInlineEdit(item, category, optionId);
            break;
        case 'delete':
            await handleDeleteItem(category, optionId, section);
            break;
    }
}

/**
 * 시스템 옵션 토글 핸들러
 * @param {Event} e - change 이벤트
 */
async function handleListItemToggle(e) {
    if (!e.target.matches('[data-action="toggle"]')) return;

    const input = e.target;
    const category = input.dataset.category;
    const value = input.dataset.value;
    const isActive = input.checked;

    try {
        await ClassificationApi.toggleSystemOption(category, { value, isActive });
        showToast(isActive ? '활성화되었습니다' : '비활성화되었습니다', 'success');

        // 아이템 스타일 업데이트
        const item = input.closest('.category-item');
        item.classList.toggle('is-disabled', !isActive);
    } catch (error) {
        // 롤백
        input.checked = !isActive;
        showToast(error.message || '변경에 실패했습니다', 'error');
    }
}

/**
 * 항목 삭제 핸들러
 * @param {string} category - 카테고리
 * @param {number} optionId - 옵션 ID
 * @param {Element} section - 섹션 엘리먼트
 */
async function handleDeleteItem(category, optionId, section) {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
        await ClassificationApi.delete(category, optionId);
        showToast('항목이 삭제되었습니다', 'success');

        // 리스트 갱신
        const tabId = section.closest('.tab-panel').id.replace('tab-', '');
        await refreshCategory(tabId, category);
    } catch (error) {
        showToast(error.message || '삭제에 실패했습니다', 'error');
    }
}

/**
 * 인라인 편집 시작
 * @param {Element} item - 아이템 엘리먼트
 * @param {string} category - 카테고리
 * @param {number} optionId - 옵션 ID
 */
function startInlineEdit(item, category, optionId) {
    const content = item.querySelector('.category-item-content');
    const value = item.querySelector('.category-item-value').textContent;

    // 현재 내용 저장
    const originalHtml = content.innerHTML;

    content.innerHTML = `
        <div class="inline-edit">
            <input type="text" class="inline-edit-input" value="${escapeHtml(value)}">
            <div class="inline-edit-actions">
                <button class="btn-icon btn-save" title="저장">
                    <i class="fas fa-check"></i>
                </button>
                <button class="btn-icon btn-cancel" title="취소">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;

    const input = content.querySelector('.inline-edit-input');
    input.focus();
    input.select();

    // 저장
    content.querySelector('.btn-save').addEventListener('click', async () => {
        const newValue = input.value.trim();
        if (!newValue) {
            showToast('값을 입력해주세요', 'warning');
            return;
        }

        try {
            await ClassificationApi.update(category, optionId, {
                value: newValue,
                label: newValue
            });
            showToast('수정되었습니다', 'success');

            // 리스트 갱신
            const section = item.closest('.category-section');
            const tabId = section.closest('.tab-panel').id.replace('tab-', '');
            await refreshCategory(tabId, category);
        } catch (error) {
            showToast(error.message || '수정에 실패했습니다', 'error');
            content.innerHTML = originalHtml;
        }
    });

    // 취소
    content.querySelector('.btn-cancel').addEventListener('click', () => {
        content.innerHTML = originalHtml;
    });

    // Enter/Escape 키 처리
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            content.querySelector('.btn-save').click();
        } else if (e.key === 'Escape') {
            content.querySelector('.btn-cancel').click();
        }
    });
}

async function refreshCategory(tabId, category) {
    try {
        const response = await ClassificationApi.getByCategory(category);
        // API returns {data: {category: [options]}} format
        const options = response.data?.[category] || response.data?.options || response.options || [];
        renderCategoryList(`#tab-${tabId} [data-category="${category}"]`, category, options);
    } catch (error) {
        console.error(`카테고리 갱신 실패: ${category}`, error);
        showToast(`${category} 목록 갱신에 실패했습니다`, 'error');
    }
}

/**
 * 패턴 규칙 저장 핸들러 초기화
 */
function initPatternsHandlers() {
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

    // 저장 버튼
    const saveBtn = document.getElementById('save-patterns');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            try {
                const settings = {
                    // 사번 설정
                    'company_code': document.getElementById('company_code')?.value || '',
                    'employee_number.prefix': document.getElementById('employee_number_prefix')?.value || '',
                    'employee_number.separator': document.getElementById('employee_number_separator')?.value || '-',
                    'employee_number.digits': document.getElementById('employee_number_digits')?.value || '6',
                    'employee_number.include_year': document.getElementById('employee_number_include_year')?.checked || false,

                    // 이메일 설정
                    'email.domain': document.getElementById('email_domain')?.value || '',
                    'email.auto_generate': document.getElementById('auto_generate_email')?.checked || false,
                    'email.format': document.getElementById('email_format')?.value || 'first.last',

                    // 내선번호 설정
                    'internal_phone.digits': document.getElementById('internal_phone_digits')?.value || '4',
                    'internal_phone.range_start': document.getElementById('extension_range_start')?.value || '',
                    'internal_phone.range_end': document.getElementById('extension_range_end')?.value || '',

                    // 급여 설정
                    'payroll.payment_day': document.getElementById('payment_day')?.value || '25',

                    // IP 설정
                    'ip.auto_assign': document.getElementById('ip_auto_assign')?.checked || false,
                    'ip.range_start': document.getElementById('ip_range_start')?.value || '',
                    'ip.range_end': document.getElementById('ip_range_end')?.value || '',

                    // 자산번호 설정
                    'asset_number.prefix': document.getElementById('asset_number_prefix')?.value || '',
                    'asset_number.separator': document.getElementById('asset_number_separator')?.value || '-',
                    'asset_number.digits': document.getElementById('asset_number_digits')?.value || '4'
                };

                await SettingsApi.saveAll(settings);
                showToast('설정이 저장되었습니다', 'success');
            } catch (error) {
                showToast(error.message || '저장에 실패했습니다', 'error');
            }
        });
    }
}

/**
 * 문서 핸들러 초기화
 */
function initDocumentsHandlers() {
    // 드래그 앤 드롭 영역
    const dropzone = document.getElementById('document-dropzone');
    const fileInput = document.getElementById('document-file-input');
    const uploadForm = document.getElementById('document-upload-form');

    if (dropzone && fileInput) {
        // 클릭으로 파일 선택
        dropzone.addEventListener('click', () => fileInput.click());

        // 드래그 앤 드롭 이벤트
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        // 파일 선택 이벤트
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    // 업로드 폼 제출
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleDocumentUpload);

        // 카테고리 변경 시 서류 유형 업데이트
        const categorySelect = uploadForm.querySelector('[name="category"]');
        if (categorySelect) {
            categorySelect.addEventListener('change', updateDocumentTypeOptions);
        }

        // 취소 버튼
        const cancelBtn = uploadForm.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                uploadForm.classList.add('d-none');
                uploadForm.reset();
                document.getElementById('selected-file-name').textContent = '';
            });
        }
    }

    // 문서 리스트 액션 이벤트 위임
    document.querySelectorAll('.document-list').forEach(list => {
        list.addEventListener('click', handleDocumentAction);
    });
}

/**
 * 파일 선택 처리
 * @param {File} file - 선택된 파일
 */
function handleFileSelect(file) {
    const uploadForm = document.getElementById('document-upload-form');
    const fileNameEl = document.getElementById('selected-file-name');

    if (!uploadForm) return;

    // 파일 크기 체크
    if (file.size > MAX_FILE_SIZE) {
        showToast(FILE_UPLOAD_MESSAGES.SIZE_EXCEEDED, 'error');
        return;
    }

    // 허용된 파일 형식 체크
    const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    if (!allowedTypes.includes(file.type)) {
        showToast('허용되지 않은 파일 형식입니다', 'error');
        return;
    }

    // 파일 정보 저장
    uploadForm.dataset.selectedFile = file.name;
    uploadForm._selectedFile = file;

    // 파일명 표시
    if (fileNameEl) {
        fileNameEl.textContent = file.name;
    }

    // 폼 표시
    uploadForm.classList.remove('d-none');
}

/**
 * 문서 업로드 처리
 * @param {Event} e - submit 이벤트
 */
async function handleDocumentUpload(e) {
    e.preventDefault();

    const form = e.target;
    const file = form._selectedFile;

    if (!file) {
        showToast('파일을 선택해주세요', 'warning');
        return;
    }

    const title = form.querySelector('[name="title"]')?.value.trim();
    if (!title) {
        showToast('서류명을 입력해주세요', 'warning');
        return;
    }

    const category = form.querySelector('[name="category"]')?.value;
    const documentType = form.querySelector('[name="documentType"]')?.value;
    const description = form.querySelector('[name="description"]')?.value?.trim() || '';
    const expiresAt = form.querySelector('[name="expiresAt"]')?.value || '';
    const isRequired = form.querySelector('[name="isRequired"]')?.checked || false;

    try {
        // FormData로 파일과 메타데이터 함께 전송
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        formData.append('category', category);
        formData.append('documentType', documentType);
        formData.append('description', description);
        formData.append('expiresAt', expiresAt);
        formData.append('isRequired', isRequired);

        await DocumentsApi.upload(formData);

        showToast('서류가 등록되었습니다', 'success');

        // 폼 리셋
        form.classList.add('d-none');
        form.reset();
        form._selectedFile = null;
        document.getElementById('selected-file-name').textContent = '';

        // 리스트 갱신
        await loadDocumentsData();

    } catch (error) {
        showToast(error.message || '서류 등록에 실패했습니다', 'error');
    }
}

/**
 * 카테고리별 서류 유형 옵션 업데이트
 * @param {Event} e - change 이벤트
 */
function updateDocumentTypeOptions(e) {
    const category = e.target.value;
    const typeSelect = document.querySelector('#document-upload-form [name="documentType"]');

    if (!typeSelect) return;

    const typeOptions = {
        required: ['business_registration', 'corporate_seal', 'certificate_of_incorporation'],
        payroll: ['salary_regulations', 'tax_withholding', 'insurance_certificate'],
        welfare: ['welfare_policy', 'insurance_policy', 'retirement_plan'],
        benefits: ['welfare_policy', 'insurance_policy', 'retirement_plan'],
        security: ['security_policy', 'privacy_policy', 'access_control'],
        contract: ['employment_contract', 'nda', 'service_agreement'],
        other: ['other']
    };

    const typeLabels = {
        business_registration: '사업자등록증',
        corporate_seal: '법인인감증명',
        certificate_of_incorporation: '법인등기부등본',
        salary_regulations: '급여규정',
        tax_withholding: '원천징수영수증',
        insurance_certificate: '4대보험 가입증명',
        welfare_policy: '복리후생규정',
        insurance_policy: '단체보험증권',
        retirement_plan: '퇴직연금규약',
        security_policy: '보안정책',
        privacy_policy: '개인정보처리방침',
        access_control: '출입관리규정',
        employment_contract: '근로계약서',
        nda: '비밀유지계약서',
        service_agreement: '용역계약서',
        other: '기타'
    };

    const options = typeOptions[category] || ['other'];
    typeSelect.innerHTML = options.map(opt =>
        `<option value="${opt}">${typeLabels[opt] || opt}</option>`
    ).join('');
}

/**
 * 문서 액션 핸들러
 * @param {Event} e - 클릭 이벤트
 */
async function handleDocumentAction(e) {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;
    const item = btn.closest('.document-item');
    const documentId = item?.dataset.id;

    switch (action) {
        case 'download':
            handleDocumentDownload(documentId);
            break;
        case 'edit':
            handleDocumentEdit(documentId);
            break;
        case 'delete':
            await handleDocumentDelete(documentId);
            break;
    }
}

/**
 * 문서 다운로드
 * @param {number} documentId - 문서 ID
 */
function handleDocumentDownload(documentId) {
    if (!documentId) {
        showToast('문서 ID가 없습니다', 'warning');
        return;
    }
    DocumentsApi.download(documentId);
}

/**
 * 문서 수정
 * @param {number} documentId - 문서 ID
 */
function handleDocumentEdit(documentId) {
    // TODO: 수정 모달 또는 인라인 편집 구현
    showToast('수정 기능은 준비 중입니다', 'info');
}

/**
 * 문서 삭제
 * @param {number} documentId - 문서 ID
 */
async function handleDocumentDelete(documentId) {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
        await DocumentsApi.delete(documentId);
        showToast('서류가 삭제되었습니다', 'success');
        await loadDocumentsData();
    } catch (error) {
        showToast(error.message || '삭제에 실패했습니다', 'error');
    }
}

/**
 * 노출 설정 핸들러 초기화
 */
function initVisibilityHandlers() {
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

function showToast(message, type = 'info') {
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-size: 14px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        background: ${TOAST_COLORS[type] || TOAST_COLORS.info};
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * HTML 이스케이프
 * @param {string} str - 문자열
 * @returns {string} 이스케이프된 문자열
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * 아코디언 초기화
 */
function initAccordions() {
    // data-accordion 속성이 있는 모든 컨테이너에 아코디언 적용
    document.querySelectorAll('[data-accordion]').forEach(container => {
        new Accordion(container);
    });
}

/**
 * 페이지 초기화
 */
function init() {
    initTabs();
    initAccordions();
    initCategoryHandlers();
    initPatternsHandlers();
    initDocumentsHandlers();
    initVisibilityHandlers();
}

// DOM 로드 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// 토스트 애니메이션 스타일 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
