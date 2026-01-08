/**
 * organization.js - 조직 관리 페이지 스크립트
 *
 * 포함 기능:
 * - 조직 트리 토글/펼치기/접기
 * - 조직 선택 및 상세 정보 표시
 * - 조직 추가/수정/삭제 모달
 * - 이벤트 위임 처리
 */

let selectedOrgId = null;
let deleteOrgId = null;

/**
 * 트리 노드 토글
 */
function toggleNode(el) {
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
function expandAll() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('.tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });
}

/**
 * 전체 접기
 */
function collapseAll() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.classList.add('collapsed');
    });
    document.querySelectorAll('.tree-toggle i').forEach(el => {
        el.classList.add('fa-chevron-right');
        el.classList.remove('fa-chevron-down');
    });
}

/**
 * 조직 선택
 */
async function selectOrganization(orgId) {
    selectedOrgId = orgId;

    // 기존 선택 해제
    document.querySelectorAll('.tree-node-content.selected').forEach(el => {
        el.classList.remove('selected');
    });

    // 새로운 선택
    const node = document.querySelector(`.tree-node[data-id="${orgId}"] > .tree-node-content`);
    if (node) {
        node.classList.add('selected');
    }

    // 상세 정보 로드
    try {
        const response = await fetch(`/admin/api/organizations/${orgId}`);
        const result = await response.json();

        if (result.success) {
            renderOrgDetail(result.data);
        }
    } catch (error) {
        console.error('Error loading organization:', error);
    }
}

/**
 * 조직 상세 정보 렌더링
 */
function renderOrgDetail(org) {
    const panel = document.getElementById('orgDetailPanel');
    const typeLabels = {
        'company': '회사',
        'division': '본부',
        'department': '부서',
        'team': '팀',
        'unit': '파트'
    };

    panel.querySelector('.panel-body').innerHTML = `
        <div class="org-detail">
            <div class="detail-header">
                <h4>${org.name}</h4>
                <span class="org-type-badge ${org.org_type}">${typeLabels[org.org_type] || org.org_type}</span>
            </div>

            <div class="detail-info">
                <div class="info-row">
                    <span class="info-label">조직 코드</span>
                    <span class="info-value">${org.code || '-'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">조직 경로</span>
                    <span class="info-value">${org.path || org.name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">설명</span>
                    <span class="info-value">${org.description || '-'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">등록일</span>
                    <span class="info-value">${org.created_at ? new Date(org.created_at).toLocaleDateString('ko-KR') : '-'}</span>
                </div>
            </div>

            <div class="detail-actions">
                <button class="btn btn-secondary" data-action="edit-org" data-org-id="${org.id}">
                    <i class="fas fa-edit"></i> 수정
                </button>
                <button class="btn btn-secondary" data-action="add-child" data-parent-id="${org.id}">
                    <i class="fas fa-plus"></i> 하위 조직 추가
                </button>
                <button class="btn btn-danger" data-action="delete-org" data-org-id="${org.id}" data-org-name="${org.name}">
                    <i class="fas fa-trash"></i> 삭제
                </button>
            </div>
        </div>
    `;
}

/**
 * 조직 추가 모달 표시
 */
function showAddOrgModal() {
    document.getElementById('orgModalTitle').textContent = '조직 추가';
    document.getElementById('orgForm').reset();
    document.getElementById('orgId').value = '';
    document.getElementById('orgModal').classList.add('show');
}

/**
 * 하위 조직 추가 모달
 */
function showAddChildModal(parentId) {
    showAddOrgModal();
    document.getElementById('orgParent').value = parentId;
}

/**
 * 조직 수정 모달
 */
async function showEditOrgModal(orgId) {
    try {
        const response = await fetch(`/admin/api/organizations/${orgId}`);
        const result = await response.json();

        if (result.success) {
            const org = result.data;
            document.getElementById('orgModalTitle').textContent = '조직 수정';
            document.getElementById('orgId').value = org.id;
            document.getElementById('orgName').value = org.name;
            document.getElementById('orgCode').value = org.code || '';
            document.getElementById('orgType').value = org.org_type;
            document.getElementById('orgParent').value = org.parent_id || '';
            document.getElementById('orgDescription').value = org.description || '';
            document.getElementById('orgModal').classList.add('show');
        }
    } catch (error) {
        console.error('Error loading organization:', error);
    }
}

/**
 * 조직 저장
 */
async function saveOrganization(event) {
    event.preventDefault();

    const orgId = document.getElementById('orgId').value;
    const parentIdValue = document.getElementById('orgParent').value;
    const data = {
        name: document.getElementById('orgName').value,
        code: document.getElementById('orgCode').value || null,
        org_type: document.getElementById('orgType').value,
        parent_id: parentIdValue ? parseInt(parentIdValue, 10) : null,
        description: document.getElementById('orgDescription').value || null
    };

    // CSRF 토큰 가져오기
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const url = orgId ? `/admin/api/organizations/${orgId}` : '/admin/api/organizations';
        const method = orgId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            closeOrgModal();
            location.reload();
        } else {
            alert(result.error || '저장에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error saving organization:', error);
        alert('저장 중 오류가 발생했습니다.');
    }
}

/**
 * 모달 닫기
 */
function closeOrgModal() {
    document.getElementById('orgModal').classList.remove('show');
}

/**
 * 삭제 모달 표시
 */
function showDeleteModal(orgId, orgName) {
    deleteOrgId = orgId;
    document.getElementById('deleteMessage').textContent = `'${orgName}' 조직을 삭제하시겠습니까?`;
    document.getElementById('cascadeDelete').checked = false;
    document.getElementById('deleteModal').classList.add('show');
}

/**
 * 삭제 모달 닫기
 */
function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('show');
    deleteOrgId = null;
}

/**
 * 삭제 확인
 */
async function confirmDelete() {
    if (!deleteOrgId) return;

    const cascade = document.getElementById('cascadeDelete').checked;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch(`/admin/api/organizations/${deleteOrgId}?cascade=${cascade}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (result.success) {
            closeDeleteModal();
            location.reload();
        } else {
            alert(result.error || '삭제에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error deleting organization:', error);
        alert('삭제 중 오류가 발생했습니다.');
    }
}

/**
 * 페이지 초기화
 */
function initOrganizationPage() {
    // 첫 번째 레벨 펼치기
    document.querySelectorAll('.tree-node[data-type="company"] > .tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('.tree-node[data-type="company"] > .tree-node-content .tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });

    // 이벤트 위임 - 클릭 이벤트
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'toggle-node':
                e.stopPropagation();
                toggleNode(target);
                break;
            case 'select-org':
                selectOrganization(parseInt(target.dataset.orgId));
                break;
            case 'add-org':
                showAddOrgModal();
                break;
            case 'expand-all':
                expandAll();
                break;
            case 'collapse-all':
                collapseAll();
                break;
            case 'close-org-modal':
                closeOrgModal();
                break;
            case 'close-delete-modal':
                closeDeleteModal();
                break;
            case 'confirm-delete':
                confirmDelete();
                break;
            case 'edit-org':
                showEditOrgModal(parseInt(target.dataset.orgId));
                break;
            case 'add-child':
                showAddChildModal(parseInt(target.dataset.parentId));
                break;
            case 'delete-org':
                showDeleteModal(parseInt(target.dataset.orgId), target.dataset.orgName);
                break;
        }
    });

    // 이벤트 위임 - 폼 제출
    document.addEventListener('submit', function(e) {
        const target = e.target.closest('[data-action="save-org"]');
        if (target) {
            e.preventDefault();
            saveOrganization(e);
        }
    });
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', initOrganizationPage);
