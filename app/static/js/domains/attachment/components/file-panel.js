/**
 * FilePanel Component
 *
 * 첨부파일 패널 컴포넌트
 * 파일 목록 표시, 업로드, 삭제, 드래그 앤 드롭 순서 변경 기능을 제공합니다.
 */
class FilePanel {
    /**
     * @param {HTMLElement} panelElement - 패널 DOM 요소
     * @param {Object} options - 설정 옵션
     * @param {string} options.ownerType - 소유자 타입 (employee, profile, company)
     * @param {number} options.ownerId - 소유자 ID
     * @param {string} [options.category] - 카테고리 필터 (선택)
     * @param {boolean} [options.readOnly] - 읽기 전용 모드 (기본값: false)
     * @param {Function} [options.onUpload] - 업로드 완료 콜백
     * @param {Function} [options.onDelete] - 삭제 완료 콜백
     * @param {Function} [options.onOrderChange] - 순서 변경 콜백
     */
    constructor(panelElement, options) {
        this.panel = panelElement;
        this.ownerType = options.ownerType;
        this.ownerId = options.ownerId;
        this.category = options.category || null;
        this.readOnly = options.readOnly || false;
        this.onUpload = options.onUpload || (() => {});
        this.onDelete = options.onDelete || (() => {});
        this.onOrderChange = options.onOrderChange || (() => {});

        this.files = [];
        this.init();
    }

    /**
     * 초기화
     */
    async init() {
        await this.loadFiles();
        this.setupEventListeners();
        if (!this.readOnly) {
            this.setupDragAndDrop();
        }
    }

    /**
     * 파일 목록 로드
     */
    async loadFiles() {
        try {
            const result = await AttachmentAPI.getByOwner(this.ownerType, this.ownerId);
            if (result.success) {
                this.files = result.data.attachments || [];
                if (this.category) {
                    this.files = this.files.filter(f => f.category === this.category);
                }
                this.renderFiles();
            }
        } catch (error) {
            console.error('파일 목록 로드 실패:', error);
        }
    }

    /**
     * 파일 목록 렌더링
     */
    renderFiles() {
        const listContainer = this.panel.querySelector('.file-list') ||
                              this.panel.querySelector('[data-file-list]');

        if (!listContainer) {
            console.warn('파일 목록 컨테이너를 찾을 수 없습니다.');
            return;
        }

        if (this.files.length === 0) {
            listContainer.innerHTML = '<div class="empty-state">첨부된 파일이 없습니다.</div>';
            return;
        }

        listContainer.innerHTML = this.files.map((file, index) => `
            <div class="file-item" data-id="${file.id}" data-index="${index}" draggable="${!this.readOnly}">
                <div class="file-icon">
                    ${this.getFileIcon(file.file_type)}
                </div>
                <div class="file-info">
                    <a href="${file.file_path}" target="_blank" class="file-name">${file.file_name}</a>
                    <span class="file-meta">${this.formatFileSize(file.file_size)} | ${file.upload_date}</span>
                </div>
                ${!this.readOnly ? `
                    <button type="button" class="btn-delete" data-id="${file.id}" title="삭제">
                        <i class="icon-trash"></i>
                    </button>
                ` : ''}
            </div>
        `).join('');
    }

    /**
     * 파일 아이콘 반환
     * @param {string} fileType - 파일 확장자
     * @returns {string} - 아이콘 HTML
     */
    getFileIcon(fileType) {
        const iconMap = {
            'pdf': '<i class="icon-file-pdf"></i>',
            'doc': '<i class="icon-file-word"></i>',
            'docx': '<i class="icon-file-word"></i>',
            'xls': '<i class="icon-file-excel"></i>',
            'xlsx': '<i class="icon-file-excel"></i>',
            'ppt': '<i class="icon-file-powerpoint"></i>',
            'pptx': '<i class="icon-file-powerpoint"></i>',
            'jpg': '<i class="icon-file-image"></i>',
            'jpeg': '<i class="icon-file-image"></i>',
            'png': '<i class="icon-file-image"></i>',
            'gif': '<i class="icon-file-image"></i>',
            'zip': '<i class="icon-file-archive"></i>',
            'hwp': '<i class="icon-file-text"></i>'
        };
        return iconMap[fileType?.toLowerCase()] || '<i class="icon-file"></i>';
    }

    /**
     * 파일 크기 포맷팅
     * @param {number} bytes - 바이트 크기
     * @returns {string} - 포맷팅된 크기
     */
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    }

    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 삭제 버튼
        this.panel.addEventListener('click', async (e) => {
            const deleteBtn = e.target.closest('.btn-delete');
            if (deleteBtn) {
                const attachmentId = parseInt(deleteBtn.dataset.id);
                await this.deleteFile(attachmentId);
            }
        });

        // 파일 업로드
        const uploadInput = this.panel.querySelector('input[type="file"]');
        if (uploadInput) {
            uploadInput.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (file) {
                    await this.uploadFile(file);
                    uploadInput.value = '';
                }
            });
        }
    }

    /**
     * 드래그 앤 드롭 설정
     */
    setupDragAndDrop() {
        const listContainer = this.panel.querySelector('.file-list') ||
                              this.panel.querySelector('[data-file-list]');

        if (!listContainer) return;

        let draggedItem = null;

        listContainer.addEventListener('dragstart', (e) => {
            const item = e.target.closest('.file-item');
            if (!item) return;
            draggedItem = item;
            item.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });

        listContainer.addEventListener('dragend', (e) => {
            const item = e.target.closest('.file-item');
            if (item) {
                item.classList.remove('dragging');
            }
            draggedItem = null;
        });

        listContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';

            const afterElement = this.getDragAfterElement(listContainer, e.clientY);
            if (draggedItem) {
                if (afterElement) {
                    listContainer.insertBefore(draggedItem, afterElement);
                } else {
                    listContainer.appendChild(draggedItem);
                }
            }
        });

        listContainer.addEventListener('drop', async (e) => {
            e.preventDefault();
            // 새 순서 추출
            const items = [...listContainer.querySelectorAll('.file-item')];
            const order = items.map(item => parseInt(item.dataset.id));
            await this.updateOrder(order);
        });
    }

    /**
     * 드래그 위치 계산
     * @param {HTMLElement} container - 컨테이너 요소
     * @param {number} y - Y 좌표
     * @returns {HTMLElement|null} - 삽입 위치 요소
     */
    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.file-item:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;

            if (offset < 0 && offset > closest.offset) {
                return { offset, element: child };
            }
            return closest;
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    /**
     * 파일 업로드
     * @param {File} file - 업로드할 파일
     */
    async uploadFile(file) {
        try {
            const category = this.category || 'document';
            const result = await AttachmentAPI.upload(this.ownerType, this.ownerId, file, category);

            if (result.success) {
                if (typeof Toast !== 'undefined') {
                    Toast.success('파일이 업로드되었습니다.');
                }
                await this.loadFiles();
                this.onUpload(result.data.attachment);
            } else {
                if (typeof Toast !== 'undefined') {
                    Toast.error(result.error || '파일 업로드에 실패했습니다.');
                }
            }
        } catch (error) {
            console.error('파일 업로드 실패:', error);
            if (typeof Toast !== 'undefined') {
                Toast.error('파일 업로드 중 오류가 발생했습니다.');
            }
        }
    }

    /**
     * 파일 삭제
     * @param {number} attachmentId - 첨부파일 ID
     */
    async deleteFile(attachmentId) {
        if (!confirm('파일을 삭제하시겠습니까?')) return;

        try {
            const result = await AttachmentAPI.delete(attachmentId);

            if (result.success) {
                if (typeof Toast !== 'undefined') {
                    Toast.success('파일이 삭제되었습니다.');
                }
                await this.loadFiles();
                this.onDelete(attachmentId);
            } else {
                if (typeof Toast !== 'undefined') {
                    Toast.error(result.error || '파일 삭제에 실패했습니다.');
                }
            }
        } catch (error) {
            console.error('파일 삭제 실패:', error);
            if (typeof Toast !== 'undefined') {
                Toast.error('파일 삭제 중 오류가 발생했습니다.');
            }
        }
    }

    /**
     * 순서 변경
     * @param {number[]} order - 첨부파일 ID 순서 배열
     */
    async updateOrder(order) {
        try {
            const result = await AttachmentAPI.updateOrder(this.ownerType, this.ownerId, order);

            if (result.success) {
                this.onOrderChange(order);
            } else {
                // 실패 시 원래 순서로 복원
                await this.loadFiles();
                if (typeof Toast !== 'undefined') {
                    Toast.error(result.error || '순서 변경에 실패했습니다.');
                }
            }
        } catch (error) {
            console.error('순서 변경 실패:', error);
            await this.loadFiles();
        }
    }
}


// 전역 export
window.FilePanel = FilePanel;
