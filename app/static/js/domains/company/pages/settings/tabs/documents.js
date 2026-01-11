/**
 * 법인 서류 관리 모듈
 *
 * 법인 설정 페이지의 서류 관리 탭 기능
 */

import { showToast } from '../../../../../shared/components/toast.js';
import { DocumentsApi } from '../../../services/settings-api.js';

// 파일 업로드 상수
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const FILE_UPLOAD_MESSAGES = {
    SIZE_EXCEEDED: '파일 크기는 10MB를 초과할 수 없습니다'
};

const ALLOWED_FILE_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
];

/**
 * HTML 이스케이프
 * @param {string} str - 문자열
 * @returns {string} 이스케이프된 문자열
 */
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
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
 * 법인 서류 데이터 로드
 */
export async function loadDocumentsData() {
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
        if (content) {
            content.innerHTML = `
                <div class="content-error">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>데이터를 불러오는데 실패했습니다</p>
                </div>
            `;
        }
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
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
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
 * 문서 핸들러 초기화
 */
export function initDocumentsHandlers() {
    const container = document.getElementById('tab-documents');
    if (!container || container.dataset.handlersInitialized) return;

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

    container.dataset.handlersInitialized = 'true';
}

/**
 * 문서 탭 초기화 엔트리 포인트
 */
export async function initDocumentsTab() {
    initDocumentsHandlers();
    await loadDocumentsData();
}
