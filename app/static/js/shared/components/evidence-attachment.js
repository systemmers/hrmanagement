/**
 * Evidence Attachment Component
 * Phase 5.2: 항목별 증빙 서류 연동 UI
 *
 * 학력, 경력, 자격증 등의 항목에 증빙 파일을 연결하는 기능 제공
 */

import { showToast } from './toast.js';

/**
 * CSRF 토큰 가져오기
 * @returns {string} CSRF 토큰
 */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content
        || document.querySelector('input[name="csrf_token"]')?.value
        || '';
}

/**
 * Evidence Attachment Manager
 */
export class EvidenceAttachmentManager {
    constructor(options = {}) {
        this.ownerType = options.ownerType || 'employee';
        this.ownerId = options.ownerId;
        this.container = options.container;
        this.onUpdate = options.onUpdate || (() => {});

        if (this.container) {
            this.init();
        }
    }

    /**
     * 초기화
     */
    init() {
        this.bindEvents();
        this.loadAll();
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        if (!this.container) return;

        // 파일 추가 버튼
        this.container.addEventListener('click', async (e) => {
            const addBtn = e.target.closest('[data-action="add-evidence"]');
            if (addBtn) {
                const wrapper = addBtn.closest('.evidence-attachment');
                const input = wrapper?.querySelector('.evidence-attachment__input');
                if (input) {
                    input.click();
                }
                return;
            }

            // 파일 삭제 버튼
            const removeBtn = e.target.closest('[data-action="remove-evidence"]');
            if (removeBtn) {
                const fileItem = removeBtn.closest('.evidence-attachment__file');
                const fileId = fileItem?.dataset.fileId;
                if (fileId) {
                    await this.removeEvidence(fileId, fileItem);
                }
            }
        });

        // 파일 선택 이벤트
        this.container.addEventListener('change', async (e) => {
            if (e.target.matches('.evidence-attachment__input')) {
                const wrapper = e.target.closest('.evidence-attachment');
                if (e.target.files.length > 0) {
                    await this.uploadEvidence(e.target.files[0], wrapper);
                    e.target.value = ''; // 리셋
                }
            }
        });
    }

    /**
     * 모든 증빙 영역 로드
     */
    async loadAll() {
        if (!this.container) return;

        const wrappers = this.container.querySelectorAll('.evidence-attachment');
        for (const wrapper of wrappers) {
            await this.loadEvidence(wrapper);
        }
    }

    /**
     * 개별 증빙 영역 로드
     * @param {HTMLElement} wrapper - 증빙 영역 컨테이너
     */
    async loadEvidence(wrapper) {
        const linkedType = wrapper.dataset.linkedType;
        const linkedId = wrapper.dataset.linkedId;
        const ownerType = wrapper.dataset.ownerType || this.ownerType;
        const ownerId = wrapper.dataset.ownerId || this.ownerId;

        if (!linkedId || !ownerId) {
            // 아직 저장되지 않은 항목
            return;
        }

        try {
            const response = await fetch(
                `/api/attachments/${ownerType}/${ownerId}/linked/${linkedType}/${linkedId}`
            );
            const result = await response.json();

            if (result.success) {
                // API 응답: { data: { attachments: [...] } } 또는 { data: [...] }
                const files = result.data?.attachments || result.data || [];
                this.renderFiles(wrapper, files);
            }
        } catch (error) {
            console.error('증빙 파일 로드 실패:', error);
        }
    }

    /**
     * 파일 목록 렌더링
     * @param {HTMLElement} wrapper - 증빙 영역 컨테이너
     * @param {Array} files - 파일 목록
     */
    renderFiles(wrapper, files) {
        const filesContainer = wrapper.querySelector('.evidence-attachment__files');
        if (!filesContainer) return;

        if (files.length === 0) {
            filesContainer.innerHTML = '';
            return;
        }

        filesContainer.innerHTML = files.map(file => `
            <div class="evidence-attachment__file" data-file-id="${file.id}">
                <i class="fas fa-file evidence-attachment__file-icon"></i>
                <span class="evidence-attachment__file-name">${this.escapeHtml(file.originalFilename || file.fileName || '파일')}</span>
                <button type="button" class="evidence-attachment__file-remove" data-action="remove-evidence" title="삭제">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    /**
     * 증빙 파일 업로드 (XHR 사용 - 진행률 표시)
     * @param {File} file - 업로드할 파일
     * @param {HTMLElement} wrapper - 증빙 영역 컨테이너
     */
    uploadEvidence(file, wrapper) {
        const linkedType = wrapper.dataset.linkedType;
        const linkedId = wrapper.dataset.linkedId;
        const ownerType = wrapper.dataset.ownerType || this.ownerType;
        const ownerId = wrapper.dataset.ownerId || this.ownerId;

        if (!linkedId) {
            showToast('먼저 항목을 저장해주세요', 'warning');
            return Promise.resolve();
        }

        if (!ownerId) {
            showToast('소유자 정보가 없습니다', 'error');
            return Promise.resolve();
        }

        // 파일 크기 체크 (10MB)
        if (file.size > 10 * 1024 * 1024) {
            showToast('파일 크기는 10MB를 초과할 수 없습니다', 'error');
            return Promise.resolve();
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('owner_type', ownerType);
        formData.append('owner_id', ownerId);
        formData.append('category', 'evidence');
        formData.append('linked_entity_type', linkedType);
        formData.append('linked_entity_id', linkedId);

        // 업로드 중 UI 표시
        const filesContainer = wrapper.querySelector('.evidence-attachment__files');
        const progressItem = this.createProgressItem(file.name);
        if (filesContainer) {
            filesContainer.appendChild(progressItem);
        }

        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();

            // 진행률 이벤트
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    this.updateProgressItem(progressItem, percent);
                }
            });

            // 완료 이벤트
            xhr.addEventListener('load', async () => {
                try {
                    const result = JSON.parse(xhr.responseText);

                    if (xhr.status >= 200 && xhr.status < 300 && result.success) {
                        this.setProgressSuccess(progressItem);
                        showToast('증빙 파일이 첨부되었습니다', 'success');

                        // 잠시 후 목록 새로고침
                        setTimeout(async () => {
                            await this.loadEvidence(wrapper);
                            this.onUpdate();
                        }, 500);
                    } else {
                        this.setProgressError(progressItem, result.error || '업로드 실패');
                        setTimeout(() => progressItem.remove(), 2000);
                        showToast(result.error || '업로드에 실패했습니다', 'error');
                    }
                } catch (parseError) {
                    this.setProgressError(progressItem, '응답 처리 실패');
                    setTimeout(() => progressItem.remove(), 2000);
                    showToast('응답 처리 중 오류 발생', 'error');
                }
                resolve();
            });

            // 에러 이벤트
            xhr.addEventListener('error', () => {
                this.setProgressError(progressItem, '네트워크 오류');
                setTimeout(() => progressItem.remove(), 2000);
                showToast('네트워크 오류가 발생했습니다', 'error');
                resolve();
            });

            // 취소 이벤트
            xhr.addEventListener('abort', () => {
                progressItem.remove();
                resolve();
            });

            // 요청 설정
            xhr.open('POST', '/api/attachments');
            xhr.setRequestHeader('X-CSRFToken', getCsrfToken());
            xhr.send(formData);
        });
    }

    /**
     * 진행률 표시 아이템 생성
     * @param {string} fileName - 파일명
     * @returns {HTMLElement}
     */
    createProgressItem(fileName) {
        const item = document.createElement('div');
        item.className = 'evidence-attachment__file evidence-attachment__file--uploading';
        item.innerHTML = `
            <i class="fas fa-spinner fa-spin evidence-attachment__file-icon"></i>
            <span class="evidence-attachment__file-name">${this.escapeHtml(fileName)}</span>
            <span class="evidence-attachment__progress">
                <span class="evidence-attachment__progress-bar" style="width: 0%"></span>
            </span>
            <span class="evidence-attachment__percentage">0%</span>
        `;
        return item;
    }

    /**
     * 진행률 업데이트
     * @param {HTMLElement} item - 진행률 아이템
     * @param {number} percent - 진행률 (0-100)
     */
    updateProgressItem(item, percent) {
        const bar = item.querySelector('.evidence-attachment__progress-bar');
        const percentage = item.querySelector('.evidence-attachment__percentage');
        if (bar) bar.style.width = `${percent}%`;
        if (percentage) percentage.textContent = `${Math.round(percent)}%`;
    }

    /**
     * 진행률 아이템 성공 상태로 변경
     * @param {HTMLElement} item - 진행률 아이템
     */
    setProgressSuccess(item) {
        item.classList.remove('evidence-attachment__file--uploading');
        item.classList.add('evidence-attachment__file--success');
        const icon = item.querySelector('.evidence-attachment__file-icon');
        if (icon) {
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-check');
        }
        const percentage = item.querySelector('.evidence-attachment__percentage');
        if (percentage) percentage.textContent = '완료';
    }

    /**
     * 진행률 아이템 에러 상태로 변경
     * @param {HTMLElement} item - 진행률 아이템
     * @param {string} message - 에러 메시지
     */
    setProgressError(item, message) {
        item.classList.remove('evidence-attachment__file--uploading');
        item.classList.add('evidence-attachment__file--error');
        const icon = item.querySelector('.evidence-attachment__file-icon');
        if (icon) {
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-exclamation-circle');
        }
        const percentage = item.querySelector('.evidence-attachment__percentage');
        if (percentage) percentage.textContent = message || '실패';
    }

    /**
     * 증빙 파일 삭제
     * @param {number|string} fileId - 파일 ID
     * @param {HTMLElement} fileItem - 파일 아이템 엘리먼트
     */
    async removeEvidence(fileId, fileItem) {
        if (!confirm('증빙 파일을 삭제하시겠습니까?')) return;

        try {
            const response = await fetch(`/api/attachments/${fileId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                showToast('증빙 파일이 삭제되었습니다', 'success');
                fileItem.remove();
                this.onUpdate();
            } else {
                throw new Error(result.error || '삭제 실패');
            }
        } catch (error) {
            console.error('증빙 파일 삭제 실패:', error);
            showToast(error.message || '파일 삭제에 실패했습니다', 'error');
        }
    }

    /**
     * 증빙 상태 조회
     * @param {string} linkedEntityType - 연결 엔티티 타입
     * @returns {Promise<Object>} 증빙 상태
     */
    async getEvidenceStatus(linkedEntityType) {
        if (!this.ownerId) return { entityIdsWithEvidence: [], totalCount: 0 };

        try {
            const response = await fetch(
                `/api/attachments/${this.ownerType}/${this.ownerId}/evidence-status/${linkedEntityType}`
            );
            const result = await response.json();

            if (result.success) {
                return result.data;
            }
        } catch (error) {
            console.error('증빙 상태 조회 실패:', error);
        }

        return { entityIdsWithEvidence: [], totalCount: 0 };
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
}

/**
 * 자동 초기화 (document ready)
 */
export function initEvidenceAttachments(containerSelector, options = {}) {
    const container = document.querySelector(containerSelector);
    if (!container) return null;

    return new EvidenceAttachmentManager({
        ...options,
        container
    });
}

export default EvidenceAttachmentManager;
