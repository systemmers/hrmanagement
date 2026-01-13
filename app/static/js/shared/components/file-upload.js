/**
 * 파일 업로드 컴포넌트
 * - 드래그 앤 드롭 지원
 * - 파일 선택 지원
 * - 업로드 진행률 표시
 * - 파일 목록 관리
 * - Phase 5.3: FileFilter - 파일 검색/필터링/정렬
 * - Phase 5.4: FilePreview - 이미지/PDF 미리보기 모달
 */

import { showToast } from './toast.js';
import {
    MAX_FILE_SIZE,
    ALLOWED_FILE_EXTENSIONS,
    FILE_UPLOAD_MESSAGES,
    isAllowedExtension
} from '../constants/file-upload-constants.js';

export class FileUpload {
    /**
     * @param {Object} options
     * @param {string} options.uploadAreaId - 업로드 영역 ID
     * @param {string} options.fileListId - 파일 목록 ID
     * @param {string} options.ownerType - 소유자 타입 (employee, profile, company)
     * @param {number} options.ownerId - 소유자 ID
     * @param {Function} options.onUploadComplete - 업로드 완료 콜백
     * @param {Function} options.onDeleteComplete - 삭제 완료 콜백
     */
    constructor(options) {
        this.uploadArea = document.getElementById(options.uploadAreaId);
        this.fileList = document.getElementById(options.fileListId);
        this.ownerType = options.ownerType || 'employee';
        this.ownerId = options.ownerId || options.employeeId; // 하위 호환
        this.onUploadComplete = options.onUploadComplete || (() => {});
        this.onDeleteComplete = options.onDeleteComplete || (() => {});

        if (this.uploadArea) {
            this.init();
        }
    }

    /**
     * CSRF 토큰 가져오기
     */
    getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content
            || document.querySelector('input[name="csrf_token"]')?.value
            || '';
    }

    init() {
        // 파일 input 생성
        this.fileInput = document.createElement('input');
        this.fileInput.type = 'file';
        this.fileInput.multiple = true;
        this.fileInput.accept = '.pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.xls,.xlsx';
        this.fileInput.style.display = 'none';
        this.uploadArea.appendChild(this.fileInput);

        // 이벤트 바인딩
        this.bindEvents();
    }

    bindEvents() {
        // 클릭하여 파일 선택
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // 파일 선택 시
        this.fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFiles(files);
            this.fileInput.value = ''; // 초기화
        });

        // 드래그 앤 드롭 이벤트
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.add('drag-over');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('drag-over');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('drag-over');

            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });

        // 파일 삭제 이벤트 (이벤트 위임)
        if (this.fileList) {
            this.fileList.addEventListener('click', (e) => {
                const deleteBtn = e.target.closest('.btn-delete-attachment');
                if (deleteBtn) {
                    const attachmentId = deleteBtn.dataset.id;
                    if (attachmentId) {
                        this.deleteFile(attachmentId);
                    }
                }
            });
        }
    }

    async handleFiles(files) {
        for (const file of files) {
            // 파일 크기 검사
            if (file.size > MAX_FILE_SIZE) {
                showToast(`${file.name}: ${FILE_UPLOAD_MESSAGES.SIZE_EXCEEDED}`, 'error');
                continue;
            }

            // 파일 확장자 검사
            if (!isAllowedExtension(file.name, ALLOWED_FILE_EXTENSIONS)) {
                showToast(`${file.name}: ${FILE_UPLOAD_MESSAGES.INVALID_TYPE}`, 'error');
                continue;
            }

            await this.uploadFile(file);
        }
    }

    /**
     * 파일 업로드 (XHR 사용 - 진행률 표시)
     * @param {File} file - 업로드할 파일
     */
    uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('owner_type', this.ownerType);
        formData.append('owner_id', this.ownerId);
        formData.append('category', this.detectCategory(file.name));

        // 업로드 상태 표시
        const uploadingCard = this.createUploadingCard(file.name);
        if (this.fileList) {
            const emptyState = this.fileList.querySelector('.file-empty-state, .empty-state-small');
            if (emptyState) {
                emptyState.remove();
            }
            this.fileList.prepend(uploadingCard);
        }

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // 진행률 이벤트
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    this.updateUploadProgress(uploadingCard, percent);
                }
            });

            // 완료 이벤트
            xhr.addEventListener('load', () => {
                try {
                    const result = JSON.parse(xhr.responseText);

                    if (xhr.status >= 200 && xhr.status < 300 && result.success && result.data?.attachment) {
                        // 성공 상태로 변경
                        this.setUploadSuccess(uploadingCard);

                        // 잠시 후 실제 파일 카드로 교체
                        setTimeout(() => {
                            const fileCard = this.createFileCard(result.data.attachment);
                            uploadingCard.replaceWith(fileCard);
                        }, 500);

                        showToast(`${file.name} 업로드 완료`, 'success');
                        this.onUploadComplete(result.data.attachment);
                        resolve(result.data.attachment);
                    } else {
                        this.setUploadError(uploadingCard, result.error || '업로드 실패');
                        setTimeout(() => uploadingCard.remove(), 2000);
                        showToast(`업로드 실패: ${result.error || '알 수 없는 오류'}`, 'error');
                        reject(new Error(result.error || '업로드 실패'));
                    }
                } catch (parseError) {
                    this.setUploadError(uploadingCard, '응답 처리 실패');
                    setTimeout(() => uploadingCard.remove(), 2000);
                    showToast('응답 처리 중 오류 발생', 'error');
                    reject(parseError);
                }
            });

            // 에러 이벤트
            xhr.addEventListener('error', () => {
                this.setUploadError(uploadingCard, '네트워크 오류');
                setTimeout(() => uploadingCard.remove(), 2000);
                showToast('네트워크 오류가 발생했습니다', 'error');
                reject(new Error('네트워크 오류'));
            });

            // 취소 이벤트
            xhr.addEventListener('abort', () => {
                uploadingCard.remove();
                reject(new Error('업로드 취소'));
            });

            // 요청 설정
            xhr.open('POST', '/api/attachments');

            // CSRF 토큰 추가
            const csrfToken = this.getCsrfToken();
            if (csrfToken) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            }

            // 전송
            xhr.send(formData);
        });
    }

    async deleteFile(attachmentId) {
        if (!confirm('이 파일을 삭제하시겠습니까?')) {
            return;
        }

        try {
            const csrfToken = this.getCsrfToken();
            const headers = {
                'Content-Type': 'application/json'
            };
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }

            const response = await fetch(`/api/attachments/${attachmentId}`, {
                method: 'DELETE',
                headers: headers
            });

            const result = await response.json();

            if (result.success) {
                const card = this.fileList.querySelector(`[data-attachment-id="${attachmentId}"]`);
                if (card) {
                    card.remove();
                }
                showToast('파일이 삭제되었습니다.', 'success');
                this.onDeleteComplete(attachmentId);

                // 파일 목록이 비었는지 확인
                if (this.fileList && !this.fileList.querySelector('.file-card')) {
                    this.fileList.innerHTML = `
                        <div class="file-empty-state">
                            <i class="file-empty-state__icon fas fa-folder-open"></i>
                            <p class="file-empty-state__text">등록된 첨부파일이 없습니다</p>
                        </div>
                    `;
                }
            } else {
                showToast(`삭제 실패: ${result.error}`, 'error');
            }
        } catch (error) {
            showToast(`삭제 오류: ${error.message}`, 'error');
        }
    }

    detectCategory(filename) {
        const lower = filename.toLowerCase();
        if (lower.includes('이력서') || lower.includes('resume') || lower.includes('cv')) {
            return '이력서';
        }
        if (lower.includes('계약서') || lower.includes('contract')) {
            return '계약서';
        }
        if (lower.includes('증명서') || lower.includes('certificate')) {
            return '증명서';
        }
        if (lower.includes('주민') || lower.includes('신분')) {
            return '신분증';
        }
        if (lower.includes('사진') || lower.includes('photo')) {
            return '사진';
        }
        return '기타';
    }

    /**
     * 진행률이 포함된 업로드 카드 생성
     * @param {string} fileName - 파일명
     * @returns {HTMLElement} 업로드 카드 엘리먼트
     */
    createUploadingCard(fileName) {
        const card = document.createElement('div');
        card.className = 'file-card file-card--vertical file-card--compact file-card--uploading';
        card.innerHTML = `
            <div class="file-card__icon">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div class="file-card__info">
                <div class="file-card__name">${this.escapeHtml(fileName)}</div>
                <div class="upload-progress">
                    <div class="upload-progress__header">
                        <span class="upload-progress__status">업로드 중...</span>
                        <span class="upload-progress__percentage">0%</span>
                    </div>
                    <div class="upload-progress__bar">
                        <div class="upload-progress__fill" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `;
        return card;
    }

    /**
     * 업로드 카드의 진행률 업데이트
     * @param {HTMLElement} card - 업로드 카드 엘리먼트
     * @param {number} percent - 진행률 (0-100)
     */
    updateUploadProgress(card, percent) {
        const fill = card.querySelector('.upload-progress__fill');
        const percentage = card.querySelector('.upload-progress__percentage');
        const status = card.querySelector('.upload-progress__status');

        if (fill) fill.style.width = `${percent}%`;
        if (percentage) percentage.textContent = `${Math.round(percent)}%`;
        if (status) {
            if (percent < 100) {
                status.textContent = '업로드 중...';
            } else {
                status.textContent = '처리 중...';
            }
        }
    }

    /**
     * 업로드 카드를 성공 상태로 변경
     * @param {HTMLElement} card - 업로드 카드 엘리먼트
     */
    setUploadSuccess(card) {
        const progress = card.querySelector('.upload-progress');
        if (progress) {
            progress.classList.add('upload-progress--success');
            const status = progress.querySelector('.upload-progress__status');
            if (status) status.textContent = '완료';
        }
    }

    /**
     * 업로드 카드를 에러 상태로 변경
     * @param {HTMLElement} card - 업로드 카드 엘리먼트
     * @param {string} message - 에러 메시지
     */
    setUploadError(card, message) {
        const progress = card.querySelector('.upload-progress');
        if (progress) {
            progress.classList.add('upload-progress--error');
            const status = progress.querySelector('.upload-progress__status');
            if (status) status.textContent = message || '실패';
        }
    }

    /**
     * HTML 이스케이프
     * @param {string} str - 문자열
     * @returns {string} 이스케이프된 문자열
     */
    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    createFileCard(attachment) {
        const card = document.createElement('div');
        card.className = 'file-card file-card--vertical file-card--compact file-card--uploaded';
        card.dataset.attachmentId = attachment.id;

        const iconClass = this.getFileIcon(attachment.file_type);
        const fileSizeKB = (attachment.file_size / 1024).toFixed(1);
        const fileUrl = attachment.file_path?.startsWith('/static/')
            ? attachment.file_path
            : `/static/uploads/${attachment.file_path}`;
        const uploadDate = attachment.upload_date?.substring(0, 10) || '';
        const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(attachment.file_type);

        card.innerHTML = `
            <div class="file-card__icon ${isImage ? 'file-card__icon--thumbnail' : ''}">
                ${isImage
                    ? `<img src="${fileUrl}" alt="${attachment.file_name}" loading="lazy">`
                    : `<i class="${iconClass}"></i>`
                }
            </div>
            <div class="file-card__info">
                <div class="file-card__label">${attachment.category || '기타'}</div>
                <div class="file-card__name">${attachment.file_name}</div>
                <div class="file-card__meta">
                    <span class="file-card__date">${uploadDate}</span>
                    <span class="file-card__size">${fileSizeKB}KB</span>
                </div>
            </div>
            <div class="file-card__actions file-card__actions--bottom">
                <a href="${fileUrl}" target="_blank" class="file-card__btn" title="보기">
                    <i class="fas fa-eye"></i>
                </a>
                <a href="${fileUrl}" download class="file-card__btn" title="다운로드">
                    <i class="fas fa-download"></i>
                </a>
                <button type="button" class="file-card__btn file-card__btn--danger btn-delete-attachment" data-id="${attachment.id}" title="삭제">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        return card;
    }

    getFileIcon(fileType) {
        const iconMap = {
            'jpg': 'fas fa-file-image',
            'jpeg': 'fas fa-file-image',
            'png': 'fas fa-file-image',
            'gif': 'fas fa-file-image',
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'docx': 'fas fa-file-word',
            'xls': 'fas fa-file-excel',
            'xlsx': 'fas fa-file-excel'
        };
        return iconMap[fileType] || 'fas fa-file';
    }
}

/**
 * 파일 필터링 컴포넌트 (Phase 5.3)
 * - 파일명 검색
 * - 파일 유형 필터
 * - 정렬 기능
 */
export class FileFilter {
    /**
     * @param {Object} options
     * @param {string} options.fileListId - 파일 목록 컨테이너 ID
     * @param {string} options.searchInputId - 검색 입력 ID
     * @param {string} options.typeFilterId - 유형 필터 select ID
     * @param {string} options.sortSelectId - 정렬 select ID
     * @param {string} options.resultCountId - 결과 카운트 ID
     */
    constructor(options = {}) {
        this.fileList = document.getElementById(options.fileListId || 'fileList');
        this.searchInput = document.getElementById(options.searchInputId || 'fileSearchInput');
        this.typeFilter = document.getElementById(options.typeFilterId || 'fileTypeFilter');
        this.sortSelect = document.getElementById(options.sortSelectId || 'fileSortSelect');
        this.resultCount = document.getElementById(options.resultCountId || 'fileResultCount');

        // 필터 상태
        this.filters = {
            search: '',
            type: '',
            sort: 'date-desc'
        };

        // 원본 파일 카드 순서 저장
        this.originalOrder = [];

        if (this.fileList) {
            this.init();
        }
    }

    init() {
        // 원본 순서 저장
        this.saveOriginalOrder();

        // 이벤트 바인딩
        this.bindEvents();
    }

    saveOriginalOrder() {
        const cards = this.fileList.querySelectorAll('.file-card');
        this.originalOrder = Array.from(cards).map(card => ({
            element: card,
            id: card.dataset.attachmentId,
            name: card.querySelector('.file-card__name')?.textContent?.toLowerCase() || '',
            date: card.querySelector('.file-card__date')?.textContent || '',
            size: this.parseSize(card.querySelector('.file-card__size')?.textContent),
            type: this.detectFileType(card)
        }));
    }

    parseSize(sizeText) {
        if (!sizeText) return 0;
        const match = sizeText.match(/[\d.]+/);
        return match ? parseFloat(match[0]) : 0;
    }

    detectFileType(card) {
        const icon = card.querySelector('.file-card__icon i');
        const img = card.querySelector('.file-card__icon img');

        if (img) return 'image';
        if (!icon) return 'other';

        const classList = icon.className;
        if (classList.includes('fa-file-pdf')) return 'pdf';
        if (classList.includes('fa-file-image')) return 'image';
        if (classList.includes('fa-file-word') || classList.includes('fa-file-excel') || classList.includes('fa-file-powerpoint')) return 'document';
        return 'other';
    }

    bindEvents() {
        // 검색 입력 (debounced)
        if (this.searchInput) {
            let debounceTimer;
            this.searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.filters.search = e.target.value.toLowerCase().trim();
                    this.applyFilters();
                }, 300);
            });
        }

        // 유형 필터
        if (this.typeFilter) {
            this.typeFilter.addEventListener('change', (e) => {
                this.filters.type = e.target.value;
                this.applyFilters();
            });
        }

        // 정렬
        if (this.sortSelect) {
            this.sortSelect.addEventListener('change', (e) => {
                this.filters.sort = e.target.value;
                this.applyFilters();
            });
        }

    }

    applyFilters() {
        let filtered = [...this.originalOrder];

        // 1. 검색 필터
        if (this.filters.search) {
            filtered = filtered.filter(item =>
                item.name.includes(this.filters.search)
            );
        }

        // 2. 유형 필터
        if (this.filters.type) {
            filtered = filtered.filter(item =>
                item.type === this.filters.type
            );
        }

        // 3. 정렬
        filtered = this.sortItems(filtered);

        // 4. DOM 업데이트
        this.updateDOM(filtered);

        // 5. 결과 카운트 업데이트
        this.updateResultCount(filtered.length);
    }

    sortItems(items) {
        const [field, direction] = this.filters.sort.split('-');

        return items.sort((a, b) => {
            let comparison = 0;

            switch (field) {
                case 'date':
                    comparison = a.date.localeCompare(b.date);
                    break;
                case 'name':
                    comparison = a.name.localeCompare(b.name);
                    break;
                case 'size':
                    comparison = a.size - b.size;
                    break;
                default:
                    return 0;
            }

            return direction === 'desc' ? -comparison : comparison;
        });
    }

    updateDOM(filtered) {
        // 모든 카드 숨기기
        this.originalOrder.forEach(item => {
            item.element.style.display = 'none';
        });

        // 빈 상태 제거
        const emptyState = this.fileList.querySelector('.file-empty-state');
        if (emptyState) emptyState.style.display = 'none';

        // 필터링된 카드만 표시하고 순서 재배치
        if (filtered.length === 0) {
            // 필터 결과 없음 표시
            let noResult = this.fileList.querySelector('.filter-no-result');
            if (!noResult) {
                noResult = document.createElement('div');
                noResult.className = 'filter-no-result file-empty-state';
                noResult.innerHTML = `
                    <i class="file-empty-state__icon fas fa-search"></i>
                    <p class="file-empty-state__text">검색 결과가 없습니다</p>
                `;
                this.fileList.appendChild(noResult);
            }
            noResult.style.display = 'flex';
        } else {
            const noResult = this.fileList.querySelector('.filter-no-result');
            if (noResult) noResult.style.display = 'none';

            filtered.forEach(item => {
                item.element.style.display = '';
                this.fileList.appendChild(item.element); // 순서 재배치
            });
        }
    }

    updateResultCount(count) {
        if (this.resultCount) {
            const numberEl = this.resultCount.querySelector('.filter-result-count__number');
            if (numberEl) {
                numberEl.textContent = count;
            } else {
                this.resultCount.innerHTML = `<span class="filter-result-count__number">${count}</span>개 파일`;
            }
        }
    }

    resetAllFilters() {
        this.filters = {
            search: '',
            type: '',
            sort: 'date-desc'
        };
        if (this.searchInput) this.searchInput.value = '';
        if (this.typeFilter) this.typeFilter.value = '';
        if (this.sortSelect) this.sortSelect.value = 'date-desc';
        this.applyFilters();
    }

    /**
     * 새 파일이 추가된 후 원본 순서 재저장
     */
    refresh() {
        this.saveOriginalOrder();
        this.applyFilters();
    }
}

/**
 * 파일 미리보기 컴포넌트 (Phase 5.4)
 * - 이미지/PDF/미지원 파일 분기 렌더링
 * - 갤러리 네비게이션 (이전/다음)
 * - 모달 열기/닫기
 */
export class FilePreview {
    /**
     * @param {Object} options
     * @param {string} options.modalId - 모달 ID
     * @param {string} options.fileListId - 파일 목록 컨테이너 ID
     */
    constructor(options = {}) {
        this.modal = document.getElementById(options.modalId || 'filePreviewModal');
        this.fileList = document.getElementById(options.fileListId || 'fileList');

        // 모달 요소
        this.previewContent = document.getElementById('previewContent');
        this.previewFileName = document.getElementById('previewFileName');
        this.previewFileInfo = document.getElementById('previewFileInfo');
        this.downloadBtn = document.getElementById('previewDownloadBtn');
        this.newTabBtn = document.getElementById('previewNewTabBtn');
        this.prevBtn = document.getElementById('previewPrevBtn');
        this.nextBtn = document.getElementById('previewNextBtn');

        // 상태
        this.currentIndex = 0;
        this.previewableFiles = [];

        if (this.modal && this.fileList) {
            this.init();
        }
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // 미리보기 버튼 클릭 (이벤트 위임)
        this.fileList.addEventListener('click', (e) => {
            const previewBtn = e.target.closest('.btn-preview-attachment');
            if (previewBtn) {
                e.preventDefault();
                this.openPreview(previewBtn);
            }
        });

        // 모달 닫기 (X 버튼, 배경 클릭)
        if (this.modal) {
            const closeBtn = this.modal.querySelector('[data-modal-close]');
            const backdrop = this.modal.querySelector('.modal__backdrop');

            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.closePreview());
            }
            if (backdrop) {
                backdrop.addEventListener('click', () => this.closePreview());
            }

            // ESC 키로 닫기
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                    this.closePreview();
                }
            });
        }

        // 갤러리 네비게이션
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.navigatePrev());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.navigateNext());
        }

        // 키보드 네비게이션 (모달 열린 상태에서)
        document.addEventListener('keydown', (e) => {
            if (!this.modal.classList.contains('show')) return;

            if (e.key === 'ArrowLeft') {
                this.navigatePrev();
            } else if (e.key === 'ArrowRight') {
                this.navigateNext();
            }
        });
    }

    /**
     * 미리보기 열기
     * @param {HTMLElement} btn - 클릭된 미리보기 버튼
     */
    openPreview(btn) {
        // 미리보기 가능한 파일 목록 수집
        this.collectPreviewableFiles();

        // 현재 파일 인덱스 찾기
        const attachmentId = btn.dataset.attachmentId;
        this.currentIndex = this.previewableFiles.findIndex(f => f.id === attachmentId);

        if (this.currentIndex === -1) {
            this.currentIndex = 0;
        }

        // 미리보기 렌더링
        this.renderPreview();

        // 모달 열기
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    /**
     * 미리보기 닫기
     */
    closePreview() {
        this.modal.classList.remove('show');
        document.body.style.overflow = '';

        // 콘텐츠 초기화
        if (this.previewContent) {
            this.previewContent.innerHTML = '';
        }
    }

    /**
     * 미리보기 가능한 파일 목록 수집
     */
    collectPreviewableFiles() {
        const buttons = this.fileList.querySelectorAll('.btn-preview-attachment');
        this.previewableFiles = Array.from(buttons).map(btn => ({
            id: btn.dataset.attachmentId,
            url: btn.dataset.fileUrl,
            name: btn.dataset.fileName,
            type: btn.dataset.fileType,
            size: btn.dataset.fileSize
        }));
    }

    /**
     * 현재 파일 미리보기 렌더링
     */
    renderPreview() {
        const file = this.previewableFiles[this.currentIndex];
        if (!file) return;

        // 파일명 업데이트
        if (this.previewFileName) {
            this.previewFileName.textContent = file.name;
        }

        // 파일 정보 업데이트
        if (this.previewFileInfo) {
            this.previewFileInfo.textContent = `${file.size} KB | ${this.getTypeLabel(file.type)}`;
        }

        // 다운로드/새탭 버튼 업데이트
        if (this.downloadBtn) {
            this.downloadBtn.href = file.url;
        }
        if (this.newTabBtn) {
            this.newTabBtn.href = file.url;
        }

        // 콘텐츠 렌더링
        if (this.previewContent) {
            this.previewContent.innerHTML = this.renderContent(file);
        }

        // 네비게이션 버튼 상태 업데이트
        this.updateNavigation();
    }

    /**
     * 파일 유형에 따른 콘텐츠 렌더링
     * @param {Object} file - 파일 정보
     * @returns {string} HTML 문자열
     */
    renderContent(file) {
        const isImage = this.isImageType(file.type);
        const isPdf = this.isPdfType(file.type);

        if (isImage) {
            return `
                <div class="file-preview__image">
                    <img src="${file.url}" alt="${file.name}" loading="lazy">
                </div>
            `;
        }

        if (isPdf) {
            return `
                <div class="file-preview__pdf">
                    <iframe src="${file.url}" title="${file.name}"></iframe>
                </div>
            `;
        }

        // 미지원 파일
        return `
            <div class="file-preview__unsupported">
                <i class="fas fa-file fa-4x"></i>
                <p>이 파일 유형은 미리보기를 지원하지 않습니다.</p>
                <a href="${file.url}" download class="btn btn--primary btn--sm">
                    <i class="fas fa-download"></i> 다운로드
                </a>
            </div>
        `;
    }

    /**
     * 이미지 타입 여부 확인
     * @param {string} type - 파일 타입 (MIME 또는 확장자)
     * @returns {boolean}
     */
    isImageType(type) {
        if (!type) return false;
        const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
                           'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
        return imageTypes.includes(type.toLowerCase()) || type.toLowerCase().startsWith('image/');
    }

    /**
     * PDF 타입 여부 확인
     * @param {string} type - 파일 타입 (MIME 또는 확장자)
     * @returns {boolean}
     */
    isPdfType(type) {
        if (!type) return false;
        return type.toLowerCase() === 'application/pdf' || type.toLowerCase() === 'pdf';
    }

    /**
     * 파일 타입 레이블 반환
     * @param {string} type - 파일 타입
     * @returns {string}
     */
    getTypeLabel(type) {
        if (!type) return '파일';
        if (this.isImageType(type)) return '이미지';
        if (this.isPdfType(type)) return 'PDF';
        if (type.includes('word') || type === 'doc' || type === 'docx') return 'Word 문서';
        if (type.includes('excel') || type === 'xls' || type === 'xlsx') return 'Excel 문서';
        if (type.includes('powerpoint') || type === 'ppt' || type === 'pptx') return 'PowerPoint';
        return '파일';
    }

    /**
     * 이전 파일로 이동
     */
    navigatePrev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.renderPreview();
        }
    }

    /**
     * 다음 파일로 이동
     */
    navigateNext() {
        if (this.currentIndex < this.previewableFiles.length - 1) {
            this.currentIndex++;
            this.renderPreview();
        }
    }

    /**
     * 네비게이션 버튼 상태 업데이트
     */
    updateNavigation() {
        const hasPrev = this.currentIndex > 0;
        const hasNext = this.currentIndex < this.previewableFiles.length - 1;

        if (this.prevBtn) {
            this.prevBtn.style.display = hasPrev ? '' : 'none';
            this.prevBtn.disabled = !hasPrev;
        }
        if (this.nextBtn) {
            this.nextBtn.style.display = hasNext ? '' : 'none';
            this.nextBtn.disabled = !hasNext;
        }
    }

    /**
     * 파일 목록 변경 후 새로고침
     */
    refresh() {
        this.collectPreviewableFiles();
    }
}
