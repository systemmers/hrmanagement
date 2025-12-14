/**
 * contracts.js - 계약 페이지 공통 스크립트
 * 
 * 포함 기능:
 * - filterTable: 테이블 필터링 기능
 * - initContractFilters: 계약 필터 초기화
 * - initContractActions: 계약 액션 버튼 초기화
 */

import { approveContract, rejectContract, terminateContract } from '../utils/contract-api.js';

/**
 * 테이블 필터링 기능
 * @param {object} config - 필터 설정
 */
export function filterTable(config = {}) {
    const searchInput = document.getElementById(config.searchInputId || 'searchInput');
    const statusFilter = document.getElementById(config.statusFilterId || 'statusFilter');
    const typeFilter = document.getElementById(config.typeFilterId || 'typeFilter');
    const tableBody = document.getElementById(config.tableBodyId || 'contractsTableBody');
    
    if (\!tableBody) return;
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const statusValue = statusFilter ? statusFilter.value : '';
    const typeValue = typeFilter ? typeFilter.value : '';
    
    const rows = tableBody.querySelectorAll('tr[data-status]');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const status = row.dataset.status || '';
        const type = row.dataset.type || '';
        
        const matchesSearch = \!searchTerm || text.includes(searchTerm);
        const matchesStatus = \!statusValue || status === statusValue;
        const matchesType = \!typeValue || type === typeValue;
        
        row.style.display = matchesSearch && matchesStatus && matchesType ? '' : 'none';
    });
}

/**
 * 계약 필터 초기화
 * @param {object} config - 필터 설정
 */
export function initContractFilters(config = {}) {
    const searchInput = document.getElementById(config.searchInputId || 'searchInput');
    const statusFilter = document.getElementById(config.statusFilterId || 'statusFilter');
    const typeFilter = document.getElementById(config.typeFilterId || 'typeFilter');
    
    const doFilter = () => filterTable(config);
    
    if (searchInput) {
        searchInput.addEventListener('input', doFilter);
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', doFilter);
    }
    if (typeFilter) {
        typeFilter.addEventListener('change', doFilter);
    }
}

/**
 * 계약 액션 버튼 초기화 (이벤트 위임)
 * @param {string} containerSelector - 컨테이너 셀렉터
 */
export function initContractActions(containerSelector = '.contracts-list, .contracts-table-wrapper') {
    const containers = document.querySelectorAll(containerSelector);

    containers.forEach(container => {
        container.addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-action]');
            if (!btn) return;

            const action = btn.dataset.action;
            const contractId = btn.dataset.contractId;

            if (!contractId) return;

            switch (action) {
                case 'approve':
                case 'approve-contract':
                    await approveContract(contractId);
                    break;
                case 'reject':
                case 'reject-contract':
                    await rejectContract(contractId);
                    break;
                case 'terminate':
                case 'terminate-contract':
                    await terminateContract(contractId);
                    break;
            }
        });
    });
}

/**
 * 계약 상태 레이블 반환
 * @param {string} status - 상태 코드
 * @returns {string} 상태 레이블
 */
export function getContractStatusLabel(status) {
    const labels = {
        'approved': '활성',
        'requested': '대기 중',
        'rejected': '거절됨',
        'terminated': '종료됨',
        'expired': '만료됨'
    };
    return labels[status] || status;
}

/**
 * 계약 유형 레이블 반환
 * @param {string} type - 유형 코드
 * @returns {string} 유형 레이블
 */
export function getContractTypeLabel(type) {
    const labels = {
        'employment': '정규직',
        'contract': '계약직',
        'freelance': '프리랜서',
        'intern': '인턴'
    };
    return labels[type] || type;
}

// 전역 함수로 노출 (비모듈 환경 호환)
if (typeof window \!== 'undefined') {
    window.HRContracts = {
        filterTable,
        initContractFilters,
        initContractActions,
        getContractStatusLabel,
        getContractTypeLabel
    };
    
    // 기존 전역 함수 호환성 유지
    window.filterTable = filterTable;
}

// 페이지 로드 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 필터가 있으면 자동 초기화
    if (document.getElementById('searchInput') || document.getElementById('statusFilter')) {
        initContractFilters();
    }
});
