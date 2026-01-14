/**
 * 분류 옵션 관리 모듈
 *
 * 법인 설정 페이지의 조직 구조/고용 정책 분류 옵션 관리 기능
 */

import { showToast } from '../../../../../shared/components/toast.js';
import { ClassificationApi } from '../../../services/settings-api.js';

/**
 * HTML 이스케이프 (SSOT: window.HRFormatters.escapeHtml)
 */
function escapeHtml(str) {
    return window.HRFormatters?.escapeHtml?.(str) || '';
}

/**
 * 조직 구조 데이터 로드
 */
export async function loadOrganizationData() {
    const content = document.getElementById('organization-content');

    try {
        const response = await ClassificationApi.getOrganization();
        Object.entries(response.data).forEach(([category, options]) => {
            renderCategoryList(`#tab-organization [data-category="${category}"]`, category, options);
        });
    } catch (error) {
        console.error('조직 구조 데이터 로드 실패:', error);
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
 * 고용 정책 데이터 로드
 */
export async function loadEmploymentData() {
    const content = document.getElementById('employment-content');

    try {
        const response = await ClassificationApi.getEmployment();
        Object.entries(response.data).forEach(([category, options]) => {
            renderCategoryList(`#tab-employment [data-category="${category}"]`, category, options);
        });
    } catch (error) {
        console.error('고용 정책 데이터 로드 실패:', error);
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
 * 카테고리 리스트 렌더링
 * @param {string} selector - 섹션 셀렉터
 * @param {string} category - 카테고리 코드
 * @param {Array} options - 옵션 목록
 */
export function renderCategoryList(selector, category, options) {
    const section = document.querySelector(selector);
    if (!section) return;

    const listContainer = section.querySelector('.category-list');
    const countEl = section.querySelector('.category-count');

    // 옵션 개수 표시
    if (countEl) {
        countEl.textContent = `(${options.length}개)`;
    }

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
 * 카테고리 이벤트 핸들러 초기화
 */
export function initCategoryHandlers() {
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
        await ClassificationApi.add(category, { value });
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

/**
 * 카테고리 새로고침
 * @param {string} tabId - 탭 ID
 * @param {string} category - 카테고리
 */
export async function refreshCategory(tabId, category) {
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
 * 조직 구조 탭 초기화 엔트리 포인트
 */
export async function initOrganizationTab() {
    initCategoryHandlers();
    await loadOrganizationData();
}

/**
 * 고용 정책 탭 초기화 엔트리 포인트
 */
export async function initEmploymentTab() {
    initCategoryHandlers();
    await loadEmploymentData();
}
