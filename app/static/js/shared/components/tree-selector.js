/**
 * Tree Selector Component
 *
 * 조직 트리 선택기 컴포넌트
 * 모달 형태로 조직 트리를 표시하고 선택할 수 있습니다.
 */

class TreeSelector {
    constructor(options = {}) {
        this.inputId = options.inputId;
        this.hiddenInputId = options.hiddenInputId;
        this.modalId = options.modalId || 'treeSelectorModal';
        this.apiUrl = options.apiUrl || '/admin/api/organizations?format=tree';
        this.placeholder = options.placeholder || '조직을 선택하세요';
        this.allowEmpty = options.allowEmpty !== false;
        this.onSelect = options.onSelect || null;

        this.selectedId = null;
        this.selectedName = null;
        this.treeData = null;

        this.init();
    }

    async init() {
        await this.loadTreeData();
        this.createModal();
        this.bindEvents();
    }

    async loadTreeData() {
        try {
            const response = await fetch(this.apiUrl);
            const result = await response.json();
            if (result.success) {
                this.treeData = result.data;
            }
        } catch (error) {
            console.error('Failed to load organization tree:', error);
            this.treeData = [];
        }
    }

    createModal() {
        // 이미 모달이 있으면 제거
        const existingModal = document.getElementById(this.modalId);
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = this.modalId;
        modal.className = 'tree-selector-modal';
        modal.innerHTML = `
            <div class="tree-selector-content">
                <div class="tree-selector-header">
                    <h3>조직 선택</h3>
                    <button type="button" class="tree-selector-close">&times;</button>
                </div>
                <div class="tree-selector-search">
                    <input type="text" class="tree-selector-search-input" placeholder="조직명 검색...">
                </div>
                <div class="tree-selector-body">
                    <div class="tree-selector-tree">
                        ${this.renderTree(this.treeData)}
                    </div>
                </div>
                <div class="tree-selector-footer">
                    ${this.allowEmpty ? '<button type="button" class="btn btn-secondary tree-selector-clear">선택 해제</button>' : ''}
                    <button type="button" class="btn btn-secondary tree-selector-cancel">취소</button>
                    <button type="button" class="btn btn-primary tree-selector-confirm">확인</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.modal = modal;
    }

    renderTree(nodes, level = 0) {
        if (!nodes || nodes.length === 0) {
            return '<div class="tree-empty">등록된 조직이 없습니다.</div>';
        }

        let html = '<ul class="tree-list">';
        for (const node of nodes) {
            const hasChildren = node.children && node.children.length > 0;
            const typeIcon = this.getTypeIcon(node.org_type);

            html += `
                <li class="tree-item" data-id="${node.id}" data-name="${node.name}" data-type="${node.org_type}">
                    <div class="tree-item-content" style="padding-left: ${level * 20 + 8}px">
                        ${hasChildren ? '<span class="tree-toggle"><i class="fas fa-chevron-right"></i></span>' : '<span class="tree-toggle-placeholder"></span>'}
                        <span class="tree-icon">${typeIcon}</span>
                        <span class="tree-label">${node.name}</span>
                        ${node.code ? `<span class="tree-code">${node.code}</span>` : ''}
                    </div>
                    ${hasChildren ? this.renderTree(node.children, level + 1) : ''}
                </li>
            `;
        }
        html += '</ul>';
        return html;
    }

    getTypeIcon(type) {
        const icons = {
            'company': '<i class="fas fa-building"></i>',
            'division': '<i class="fas fa-layer-group"></i>',
            'department': '<i class="fas fa-users"></i>',
            'team': '<i class="fas fa-user-friends"></i>',
            'unit': '<i class="fas fa-folder"></i>'
        };
        return icons[type] || '<i class="fas fa-folder"></i>';
    }

    bindEvents() {
        const input = document.getElementById(this.inputId);
        if (input) {
            input.addEventListener('click', () => this.open());
            input.setAttribute('readonly', 'true');
            input.style.cursor = 'pointer';
        }

        // 모달 이벤트
        this.modal.querySelector('.tree-selector-close').addEventListener('click', () => this.close());
        this.modal.querySelector('.tree-selector-cancel').addEventListener('click', () => this.close());
        this.modal.querySelector('.tree-selector-confirm').addEventListener('click', () => this.confirm());

        const clearBtn = this.modal.querySelector('.tree-selector-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clear());
        }

        // 배경 클릭 시 닫기
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // 트리 아이템 클릭
        this.modal.querySelectorAll('.tree-item-content').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();

                // 토글 클릭 시 펼치기/접기
                if (e.target.closest('.tree-toggle')) {
                    this.toggleNode(e.target.closest('.tree-item'));
                    return;
                }

                // 선택
                this.selectNode(e.target.closest('.tree-item'));
            });
        });

        // 검색
        const searchInput = this.modal.querySelector('.tree-selector-search-input');
        searchInput.addEventListener('input', (e) => this.filterTree(e.target.value));
    }

    toggleNode(item) {
        const toggle = item.querySelector(':scope > .tree-item-content .tree-toggle');
        const childList = item.querySelector(':scope > .tree-list');

        if (toggle && childList) {
            toggle.classList.toggle('expanded');
            childList.classList.toggle('collapsed');
        }
    }

    selectNode(item) {
        // 기존 선택 해제
        this.modal.querySelectorAll('.tree-item-content.selected').forEach(el => {
            el.classList.remove('selected');
        });

        // 새로운 선택
        const content = item.querySelector(':scope > .tree-item-content');
        content.classList.add('selected');

        this.selectedId = item.dataset.id;
        this.selectedName = item.dataset.name;
    }

    filterTree(query) {
        const items = this.modal.querySelectorAll('.tree-item');
        const lowerQuery = query.toLowerCase();

        items.forEach(item => {
            const name = item.dataset.name.toLowerCase();
            const matches = name.includes(lowerQuery);

            if (matches) {
                item.style.display = '';
                // 부모도 표시
                let parent = item.parentElement.closest('.tree-item');
                while (parent) {
                    parent.style.display = '';
                    parent.querySelector(':scope > .tree-list')?.classList.remove('collapsed');
                    parent = parent.parentElement.closest('.tree-item');
                }
            } else if (query) {
                item.style.display = 'none';
            } else {
                item.style.display = '';
            }
        });
    }

    open() {
        this.modal.classList.add('show');
        this.modal.querySelector('.tree-selector-search-input').focus();

        // 현재 선택된 값이 있으면 표시
        const hiddenInput = document.getElementById(this.hiddenInputId);
        if (hiddenInput && hiddenInput.value) {
            const item = this.modal.querySelector(`.tree-item[data-id="${hiddenInput.value}"]`);
            if (item) {
                this.selectNode(item);
                // 부모 노드들 펼치기
                let parent = item.parentElement.closest('.tree-item');
                while (parent) {
                    parent.querySelector(':scope > .tree-list')?.classList.remove('collapsed');
                    parent.querySelector(':scope > .tree-item-content .tree-toggle')?.classList.add('expanded');
                    parent = parent.parentElement.closest('.tree-item');
                }
            }
        }
    }

    close() {
        this.modal.classList.remove('show');
        this.selectedId = null;
        this.selectedName = null;

        // 선택 초기화
        this.modal.querySelectorAll('.tree-item-content.selected').forEach(el => {
            el.classList.remove('selected');
        });
    }

    confirm() {
        if (this.selectedId) {
            const input = document.getElementById(this.inputId);
            const hiddenInput = document.getElementById(this.hiddenInputId);

            if (input) input.value = this.selectedName;
            if (hiddenInput) hiddenInput.value = this.selectedId;

            if (this.onSelect) {
                this.onSelect({
                    id: this.selectedId,
                    name: this.selectedName
                });
            }
        }
        this.close();
    }

    clear() {
        const input = document.getElementById(this.inputId);
        const hiddenInput = document.getElementById(this.hiddenInputId);

        if (input) input.value = '';
        if (hiddenInput) hiddenInput.value = '';

        this.selectedId = null;
        this.selectedName = null;

        if (this.onSelect) {
            this.onSelect(null);
        }

        this.close();
    }

    // 외부에서 값 설정
    setValue(id, name) {
        const input = document.getElementById(this.inputId);
        const hiddenInput = document.getElementById(this.hiddenInputId);

        if (input) input.value = name || '';
        if (hiddenInput) hiddenInput.value = id || '';

        this.selectedId = id;
        this.selectedName = name;
    }
}

// 전역으로 내보내기
window.TreeSelector = TreeSelector;
