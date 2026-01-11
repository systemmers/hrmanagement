/**
 * 조직유형 설정 모듈
 *
 * 법인 설정 페이지의 조직유형 설정 기능
 */

import { showToast } from '../../../../../shared/components/toast.js';
import { ICON_PICKER_OPTIONS } from '../shared/constants.js';

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
 * 조직유형 설정 렌더링
 * @param {Array} types - 조직유형 목록
 */
export function renderOrgTypeSettings(types) {
    const container = document.getElementById('orgTypeList');
    if (!container) return;

    if (!types || types.length === 0) {
        container.innerHTML = '<p class="text-muted">조직유형이 없습니다.</p>';
        return;
    }

    container.innerHTML = `
        <div class="org-type-table" id="orgTypeTable">
            <div class="org-type-header">
                <span class="org-type-col org-type-col--drag" aria-label="순서 변경"></span>
                <span class="org-type-col org-type-col--order">순번</span>
                <span class="org-type-col org-type-col--icon">아이콘</span>
                <span class="org-type-col org-type-col--label-ko">한글명</span>
                <span class="org-type-col org-type-col--label-en">영문명</span>
                <span class="org-type-col org-type-col--delete"></span>
            </div>
            ${types.map((type, index) => renderOrgTypeRow(type, index)).join('')}
        </div>
        <div class="org-type-add-row">
            <button type="button" class="btn btn--sm btn--secondary" data-action="add-org-type">
                <i class="fas fa-plus"></i>
                <span>조직유형 추가</span>
            </button>
        </div>
    `;

    // 드래그 앤 드롭 초기화
    initOrgTypeSortable();
}

/**
 * 조직유형 행 렌더링
 * @param {Object} type - 조직유형 데이터
 * @param {number} index - 인덱스
 * @returns {string} HTML 문자열
 */
export function renderOrgTypeRow(type, index) {
    return `
        <div class="org-type-row" data-id="${type.id}" data-sort-order="${type.sort_order}" draggable="true">
            <span class="org-type-col org-type-col--drag">
                <i class="fas fa-grip-vertical drag-handle" title="드래그하여 순서 변경"></i>
            </span>
            <span class="org-type-col org-type-col--order">${index + 1}</span>
            <span class="org-type-col org-type-col--icon">
                <button type="button" class="btn btn--icon btn--sm" data-action="select-icon" data-id="${type.id}" title="아이콘 선택">
                    <i class="fas ${type.icon || 'fa-folder'}"></i>
                </button>
            </span>
            <span class="org-type-col org-type-col--label-ko">
                <input type="text" class="form__input form__input--sm org-type-label-input"
                       value="${escapeHtml(type.type_label_ko || type.type_label || '')}"
                       data-id="${type.id}"
                       data-field="type_label_ko"
                       data-original="${escapeHtml(type.type_label_ko || type.type_label || '')}"
                       placeholder="한글명">
            </span>
            <span class="org-type-col org-type-col--label-en">
                <input type="text" class="form__input form__input--sm org-type-label-input"
                       value="${escapeHtml(type.type_label_en || '')}"
                       data-id="${type.id}"
                       data-field="type_label_en"
                       data-original="${escapeHtml(type.type_label_en || '')}"
                       placeholder="English">
            </span>
            <span class="org-type-col org-type-col--delete">
                <button type="button" class="btn btn--icon btn--sm btn--ghost"
                        data-action="delete-org-type" data-id="${type.id}"
                        data-type-code="${escapeHtml(type.type_code)}" title="삭제">
                    <i class="fas fa-trash"></i>
                </button>
            </span>
        </div>
    `;
}

/**
 * 조직유형 순서 드래그 앤 드롭 초기화
 */
export function initOrgTypeSortable() {
    const table = document.getElementById('orgTypeTable');
    if (!table) return;

    let draggedItem = null;

    table.addEventListener('dragstart', (e) => {
        const row = e.target.closest('.org-type-row');
        if (row) {
            draggedItem = row;
            row.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        }
    });

    table.addEventListener('dragend', (e) => {
        const row = e.target.closest('.org-type-row');
        if (row) {
            row.classList.remove('dragging');
            draggedItem = null;
            // 순서 저장
            saveOrgTypeOrder();
        }
    });

    table.addEventListener('dragover', (e) => {
        e.preventDefault();
        const row = e.target.closest('.org-type-row');
        if (row && row !== draggedItem) {
            const rect = row.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            if (e.clientY < midY) {
                row.parentNode.insertBefore(draggedItem, row);
            } else {
                row.parentNode.insertBefore(draggedItem, row.nextSibling);
            }
        }
    });
}

/**
 * 조직유형 순서 저장
 */
async function saveOrgTypeOrder() {
    const table = document.getElementById('orgTypeTable');
    if (!table) return;

    const rows = table.querySelectorAll('.org-type-row');
    const typeIds = Array.from(rows).map(row => parseInt(row.dataset.id));

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/api/corporate/organization-types/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ type_ids: typeIds })
        });

        const result = await response.json();

        if (result.success) {
            showToast('순서가 저장되었습니다', 'success');
            // 순번 UI 즉시 업데이트
            updateOrgTypeOrderNumbers();
        } else {
            showToast(result.error || '순서 저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 순서 저장 오류:', error);
        showToast('순서 저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 순번 UI 업데이트
 */
function updateOrgTypeOrderNumbers() {
    const table = document.getElementById('orgTypeTable');
    if (!table) return;

    const rows = table.querySelectorAll('.org-type-row');
    rows.forEach((row, index) => {
        const orderCol = row.querySelector('.org-type-col--order');
        if (orderCol) {
            orderCol.textContent = index + 1;
        }
    });
}

/**
 * 조직유형 라벨 저장 (한글명/영문명)
 * @param {number} configId - 설정 ID
 * @param {string} field - 필드명 (type_label_ko 또는 type_label_en)
 * @param {string} value - 새 값
 */
export async function saveOrgTypeLabel(configId, field, value) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    const data = {};
    data[field] = value;

    try {
        const response = await fetch(`/api/corporate/organization-types/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('저장되었습니다', 'success');
            // 입력 필드의 original 값 업데이트
            const input = document.querySelector(`.org-type-label-input[data-id="${configId}"][data-field="${field}"]`);
            if (input) {
                input.dataset.original = value;
            }
        } else {
            showToast(result.error || '저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 라벨 저장 오류:', error);
        showToast('저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 삭제
 * @param {number} configId - 설정 ID
 * @param {string} typeCode - 유형 코드
 */
export async function deleteOrgType(configId, typeCode) {
    const confirmed = confirm(`이 조직유형을 삭제하시겠습니까?\n\n사용 중인 조직이 있으면 삭제할 수 없습니다.`);
    if (!confirmed) return;

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch(`/api/corporate/organization-types/${configId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (result.success) {
            showToast('조직유형이 삭제되었습니다', 'success');
            // 해당 행 제거 및 순번 재정렬
            const row = document.querySelector(`.org-type-row[data-id="${configId}"]`);
            if (row) {
                row.remove();
                updateOrgTypeOrderNumbers();
            }
        } else {
            showToast(result.error || '삭제에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 삭제 오류:', error);
        showToast('삭제 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 추가
 */
export async function addOrgType() {
    const labelKo = prompt('새 조직유형의 한글명을 입력하세요:');
    if (!labelKo || !labelKo.trim()) return;

    const labelEn = prompt('영문명을 입력하세요 (선택사항):');

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/api/corporate/organization-types', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                type_label_ko: labelKo.trim(),
                type_label_en: labelEn ? labelEn.trim() : null,
                icon: 'fa-folder'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast('조직유형이 추가되었습니다', 'success');
            // 새 행 추가
            const table = document.getElementById('orgTypeTable');
            if (table && result.data) {
                const rowCount = table.querySelectorAll('.org-type-row').length;
                const newRowHtml = renderOrgTypeRow(result.data, rowCount);
                table.insertAdjacentHTML('beforeend', newRowHtml);
            }
        } else {
            showToast(result.error || '추가에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 추가 오류:', error);
        showToast('추가 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 아이콘 저장
 * @param {number} configId - 설정 ID
 * @param {string} icon - 아이콘 클래스
 */
async function saveOrgTypeIcon(configId, icon) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch(`/api/corporate/organization-types/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ icon: icon })
        });

        const result = await response.json();

        if (result.success) {
            showToast('아이콘이 저장되었습니다', 'success');
            // 아이콘 버튼 업데이트
            const btn = document.querySelector(`.org-type-row[data-id="${configId}"] [data-action="select-icon"] i`);
            if (btn) {
                btn.className = `fas ${icon}`;
            }
        } else {
            showToast(result.error || '저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 아이콘 저장 오류:', error);
        showToast('저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 아이콘 선택 모달 표시
 * @param {number} configId - 설정 ID
 */
export function showIconSelector(configId) {
    // 기존 모달 제거
    const existingModal = document.getElementById('iconSelectorModal');
    if (existingModal) {
        existingModal.remove();
    }

    const modalHtml = `
        <div class="modal show" id="iconSelectorModal">
            <div class="modal__content modal__content--sm">
                <div class="modal__header">
                    <h3 class="modal__title">아이콘 선택</h3>
                    <button class="modal__close" data-action="close-icon-modal">&times;</button>
                </div>
                <div class="modal__body">
                    <div class="icon-grid">
                        ${ICON_PICKER_OPTIONS.map(icon => `
                            <button type="button" class="icon-grid__item" data-icon="${icon}" data-config-id="${configId}">
                                <i class="fas ${icon}"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    const modal = document.getElementById('iconSelectorModal');

    // 이벤트 리스너
    modal.addEventListener('click', (e) => {
        const closeBtn = e.target.closest('[data-action="close-icon-modal"]');
        if (closeBtn || e.target === modal) {
            modal.remove();
            return;
        }

        const iconBtn = e.target.closest('.icon-grid__item');
        if (iconBtn) {
            const icon = iconBtn.dataset.icon;
            const cId = parseInt(iconBtn.dataset.configId);
            saveOrgTypeIcon(cId, icon);
            modal.remove();
        }
    });
}

/**
 * 조직유형 초기화
 * @param {Function} reloadCallback - 데이터 새로고침 콜백
 */
export async function resetOrgTypes(reloadCallback) {
    if (!confirm('조직유형 설정을 기본값으로 초기화하시겠습니까?')) {
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/api/corporate/organization-types/reset', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (result.success) {
            showToast('기본값으로 초기화되었습니다', 'success');
            // 콜백으로 데이터 새로고침
            if (typeof reloadCallback === 'function') {
                await reloadCallback();
            }
        } else {
            showToast(result.error || '초기화에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 초기화 오류:', error);
        showToast('초기화 중 오류가 발생했습니다', 'error');
    }
}
