/**
 * 조직 트리 컴포넌트
 *
 * 조직 트리 렌더링 및 드래그앤드롭 기능
 */

import { showToast } from '../../../../../shared/components/toast.js';
import { getOrgTypeIcon } from '../shared/constants.js';

// 트리 드래그 상태
let treeDraggedNode = null;
let treeDraggedParentId = null;
let treeExpanded = false;

// 콜백 함수
let onDataReloadCallback = null;
let onSelectOrgCallback = null;

/**
 * 콜백 설정
 * @param {Object} callbacks - 콜백 함수들
 */
export function setTreeCallbacks(callbacks) {
    if (callbacks.onDataReload) onDataReloadCallback = callbacks.onDataReload;
    if (callbacks.onSelectOrg) onSelectOrgCallback = callbacks.onSelectOrg;
}

/**
 * HTML 이스케이프
 */
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * 조직 트리 렌더링
 */
export function renderOrgTree(tree) {
    const treeContainer = document.getElementById('orgTree');
    if (!treeContainer) return;

    if (!tree || tree.length === 0) {
        treeContainer.innerHTML = `
            <div class="empty-tree">
                <i class="fas fa-folder-open"></i>
                <p>등록된 조직이 없습니다.</p>
                <button class="btn btn-primary" data-action="add-org">
                    첫 번째 조직 추가
                </button>
            </div>
        `;
        return;
    }

    treeContainer.innerHTML = tree.map(org => renderTreeNode(org, null)).join('');

    // 첫 번째 레벨 펼치기
    document.querySelectorAll('#orgTree > .tree-node > .tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('#orgTree > .tree-node > .tree-node-content .tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });

    // 드래그앤드롭 초기화
    initOrgTreeDragDrop();
}

/**
 * 트리 노드 렌더링
 */
function renderTreeNode(org, parentId = null) {
    const icon = getOrgTypeIcon(org.org_type);
    const hasChildren = org.children && org.children.length > 0;
    const isRoot = org.org_type === 'company';

    return `
        <div class="tree-node" data-id="${org.id}" data-type="${org.org_type}" data-parent-id="${parentId || ''}" draggable="${!isRoot}">
            <div class="tree-node-content" data-action="select-org" data-org-id="${org.id}">
                ${!isRoot ? `
                    <span class="tree-drag-handle" title="드래그하여 순서 변경">
                        <i class="fas fa-grip-vertical"></i>
                    </span>
                ` : ''}
                ${hasChildren ? `
                    <span class="tree-toggle" data-action="toggle-node">
                        <i class="fas fa-chevron-right"></i>
                    </span>
                ` : '<span class="tree-toggle-placeholder"></span>'}
                <span class="tree-icon">
                    <i class="fas ${icon}"></i>
                </span>
                <span class="tree-label">${escapeHtml(org.name)}</span>
                ${org.total_member_count > 0 ? `<span class="tree-member-count">(${org.total_member_count}명)</span>` : ''}
                ${org.code ? `<span class="tree-code">${escapeHtml(org.code)}</span>` : ''}
            </div>
            ${hasChildren ? `
                <div class="tree-children collapsed">
                    ${org.children.map(child => renderTreeNode(child, org.id)).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * 조직 트리 드래그앤드롭 초기화
 */
function initOrgTreeDragDrop() {
    const treeContainer = document.getElementById('orgTree');
    if (!treeContainer || treeContainer.dataset.dragInitialized) return;

    // 드래그 시작
    treeContainer.addEventListener('dragstart', (e) => {
        const node = e.target.closest('.tree-node[draggable="true"]');
        if (!node) return;

        const handle = e.target.closest('.tree-drag-handle');
        if (!handle) {
            e.preventDefault();
            return;
        }

        treeDraggedNode = node;
        treeDraggedParentId = node.dataset.parentId || '';
        node.classList.add('dragging');

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', node.dataset.id);
    });

    // 드래그 종료
    treeContainer.addEventListener('dragend', (e) => {
        if (treeDraggedNode) {
            treeDraggedNode.classList.remove('dragging');
        }
        treeContainer.querySelectorAll('.tree-node.drag-over, .tree-node.drag-over-above, .tree-node.drag-over-below').forEach(el => {
            el.classList.remove('drag-over', 'drag-over-above', 'drag-over-below');
        });
        treeDraggedNode = null;
        treeDraggedParentId = null;
    });

    // 드래그 오버
    treeContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!treeDraggedNode) return;

        const targetNode = e.target.closest('.tree-node[draggable="true"]');
        if (!targetNode || targetNode === treeDraggedNode) return;

        const targetParentId = targetNode.dataset.parentId || '';
        if (targetParentId !== treeDraggedParentId) {
            e.dataTransfer.dropEffect = 'none';
            return;
        }

        e.dataTransfer.dropEffect = 'move';

        const rect = targetNode.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;

        treeContainer.querySelectorAll('.tree-node.drag-over-above, .tree-node.drag-over-below').forEach(el => {
            el.classList.remove('drag-over-above', 'drag-over-below');
        });

        if (e.clientY < midY) {
            targetNode.classList.add('drag-over-above');
        } else {
            targetNode.classList.add('drag-over-below');
        }
    });

    // 드래그 리브
    treeContainer.addEventListener('dragleave', (e) => {
        const targetNode = e.target.closest('.tree-node');
        if (targetNode) {
            targetNode.classList.remove('drag-over', 'drag-over-above', 'drag-over-below');
        }
    });

    // 드롭
    treeContainer.addEventListener('drop', async (e) => {
        e.preventDefault();
        if (!treeDraggedNode) return;

        const targetNode = e.target.closest('.tree-node[draggable="true"]');
        if (!targetNode || targetNode === treeDraggedNode) return;

        const targetParentId = targetNode.dataset.parentId || '';
        if (targetParentId !== treeDraggedParentId) return;

        const rect = targetNode.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        const insertBefore = e.clientY < midY;

        const parent = targetNode.parentNode;
        if (insertBefore) {
            parent.insertBefore(treeDraggedNode, targetNode);
        } else {
            parent.insertBefore(treeDraggedNode, targetNode.nextSibling);
        }

        targetNode.classList.remove('drag-over-above', 'drag-over-below');

        if (treeDraggedParentId) {
            await saveOrgTreeOrder(treeDraggedParentId);
        }
    });

    treeContainer.dataset.dragInitialized = 'true';
}

/**
 * 조직 트리 순서 저장
 */
async function saveOrgTreeOrder(parentId) {
    if (!parentId) return;

    const parent = document.querySelector(`.tree-node[data-id="${parentId}"]`);
    if (!parent) return;

    const childrenContainer = parent.querySelector('.tree-children');
    if (!childrenContainer) return;

    const children = childrenContainer.querySelectorAll(':scope > .tree-node');
    const orgIds = Array.from(children).map(node => parseInt(node.dataset.id));

    if (orgIds.length === 0) return;

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/admin/api/organizations/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                parent_id: parseInt(parentId),
                org_ids: orgIds
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast('순서가 저장되었습니다', 'success');
        } else {
            showToast(result.error || '순서 저장에 실패했습니다', 'error');
            if (onDataReloadCallback) {
                await onDataReloadCallback();
            }
        }
    } catch (error) {
        console.error('순서 저장 오류:', error);
        showToast('순서 저장 중 오류가 발생했습니다', 'error');
        if (onDataReloadCallback) {
            await onDataReloadCallback();
        }
    }
}

/**
 * 트리 노드 토글
 */
export function toggleTreeNode(el) {
    const node = el.closest('.tree-node');
    const children = node.querySelector('.tree-children');
    const icon = el.querySelector('i');

    if (children) {
        children.classList.toggle('collapsed');
        icon.classList.toggle('fa-chevron-right');
        icon.classList.toggle('fa-chevron-down');
    }
}

/**
 * 전체 펼치기
 */
export function expandAllTree() {
    document.querySelectorAll('#orgTree .tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('#orgTree .tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });
}

/**
 * 전체 접기
 */
export function collapseAllTree() {
    document.querySelectorAll('#orgTree .tree-children').forEach(el => {
        el.classList.add('collapsed');
    });
    document.querySelectorAll('#orgTree .tree-toggle i').forEach(el => {
        el.classList.add('fa-chevron-right');
        el.classList.remove('fa-chevron-down');
    });
}

/**
 * 트리 펼치기/접기 토글
 */
export function toggleTreeExpand() {
    if (treeExpanded) {
        collapseAllTree();
        updateToggleButton(false);
    } else {
        expandAllTree();
        updateToggleButton(true);
    }
    treeExpanded = !treeExpanded;
}

/**
 * 토글 버튼 상태 업데이트
 */
function updateToggleButton(expanded) {
    const btn = document.getElementById('toggleTreeBtn');
    if (!btn) return;

    const icon = btn.querySelector('i');
    const srText = btn.querySelector('.sr-only');

    if (expanded) {
        icon.className = 'fas fa-compress-alt';
        btn.title = '전체 접기';
        if (srText) srText.textContent = '전체 접기';
    } else {
        icon.className = 'fas fa-expand-alt';
        btn.title = '전체 펼치기';
        if (srText) srText.textContent = '전체 펼치기';
    }
}

/**
 * 상위 조직 선택 옵션 업데이트
 */
export async function updateParentOrgOptions() {
    try {
        const response = await fetch('/admin/api/organizations?format=flat');
        const result = await response.json();

        if (result.success) {
            const select = document.getElementById('orgParent');
            if (!select) return;

            select.innerHTML = '<option value="">없음 (최상위)</option>' +
                result.data.map(org => `<option value="${org.id}">${escapeHtml(org.path || org.name)}</option>`).join('');
        }
    } catch (error) {
        console.error('상위 조직 옵션 로드 실패:', error);
    }
}
