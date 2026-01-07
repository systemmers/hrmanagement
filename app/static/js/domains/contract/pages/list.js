/**
 * contracts.js - 계약 페이지 공통 스크립트
 *
 * 포함 기능:
 * - initContractActions: 계약 액션 버튼 초기화
 * - getContractStatusLabel: 상태 레이블 반환
 * - getContractTypeLabel: 유형 레이블 반환
 *
 * 필터링은 filter-bar.js (SSOT)에서 처리
 */

import { approveContract, rejectContract, terminateContract } from '../services/contract-service.js';

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
if (typeof window !== 'undefined') {
    window.HRContracts = {
        initContractActions,
        getContractStatusLabel,
        getContractTypeLabel
    };
}

/**
 * 이벤트 전파 방지 버튼 초기화 (이벤트 위임)
 * CLAUDE.md 규칙: 인라인 onclick 금지 → addEventListener 사용
 */
function initPreventPropagationButtons() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-prevent-propagation');
        if (btn) {
            e.stopPropagation();
        }
    });
}

// 페이지 로드 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 계약 액션 버튼 초기화
    initContractActions();

    // 이벤트 전파 방지 버튼 초기화
    initPreventPropagationButtons();
});
