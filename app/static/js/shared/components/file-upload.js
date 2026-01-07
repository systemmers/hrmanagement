/**
 * 파일 업로드 컴포넌트
 * - 드래그 앤 드롭 지원
 * - 파일 선택 지원
 * - 업로드 진행률 표시
 * - 파일 목록 관리
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
     * @param {number} options.employeeId - 직원 ID
     * @param {Function} options.onUploadComplete - 업로드 완료 콜백
     */
    constructor(options) {
        this.uploadArea = document.getElementById(options.uploadAreaId);
        this.fileList = document.getElementById(options.fileListId);
        this.employeeId = options.employeeId;
        this.onUploadComplete = options.onUploadComplete || (() => {});

        if (this.uploadArea) {
            this.init();
        }
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

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', this.detectCategory(file.name));

        // 업로드 상태 표시
        const uploadingCard = this.createUploadingCard(file.name);
        if (this.fileList) {
            const emptyState = this.fileList.querySelector('.empty-state-small');
            if (emptyState) {
                emptyState.remove();
            }
            this.fileList.prepend(uploadingCard);
        }

        try {
            const response = await fetch(`/api/employees/${this.employeeId}/attachments`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // 업로드 중 카드를 실제 파일 카드로 교체
                const fileCard = this.createFileCard(result.attachment);
                uploadingCard.replaceWith(fileCard);
                showToast(`${file.name} 업로드 완료`, 'success');
                this.onUploadComplete(result.attachment);
            } else {
                uploadingCard.remove();
                showToast(`업로드 실패: ${result.error}`, 'error');
            }
        } catch (error) {
            uploadingCard.remove();
            showToast(`업로드 오류: ${error.message}`, 'error');
        }
    }

    async deleteFile(attachmentId) {
        if (!confirm('이 파일을 삭제하시겠습니까?')) {
            return;
        }

        try {
            const response = await fetch(`/api/attachments/${attachmentId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                const card = this.fileList.querySelector(`[data-attachment-id="${attachmentId}"]`);
                if (card) {
                    card.remove();
                }
                showToast('파일이 삭제되었습니다.', 'success');

                // 파일 목록이 비었는지 확인
                if (this.fileList && !this.fileList.querySelector('.file-card')) {
                    this.fileList.innerHTML = `
                        <div class="empty-state-small">
                            <i class="fas fa-folder-open"></i>
                            <p>등록된 첨부파일이 없습니다</p>
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

    createUploadingCard(fileName) {
        const card = document.createElement('div');
        card.className = 'file-card uploading';
        card.innerHTML = `
            <div class="file-icon">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${fileName}</div>
                <div class="file-meta">
                    <span class="file-status">업로드 중...</span>
                </div>
            </div>
        `;
        return card;
    }

    createFileCard(attachment) {
        const card = document.createElement('div');
        card.className = 'file-card';
        card.dataset.attachmentId = attachment.id;

        const iconClass = this.getFileIcon(attachment.file_type);
        const fileSizeKB = (attachment.file_size / 1024).toFixed(1);

        card.innerHTML = `
            <div class="file-icon">
                <i class="${iconClass}"></i>
            </div>
            <div class="file-info">
                <div class="file-name">${attachment.file_name}</div>
                <div class="file-meta">
                    <span class="file-category">${attachment.category || '기타'}</span>
                    <span class="file-size">${fileSizeKB}KB</span>
                </div>
            </div>
            <div class="file-actions">
                <a href="${attachment.file_path}" target="_blank" class="btn-icon" title="보기">
                    <i class="fas fa-eye"></i>
                </a>
                <a href="${attachment.file_path}" download class="btn-icon" title="다운로드">
                    <i class="fas fa-download"></i>
                </a>
                <button type="button" class="btn-icon btn-delete-attachment" data-id="${attachment.id}" title="삭제">
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
