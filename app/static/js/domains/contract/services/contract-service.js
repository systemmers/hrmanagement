/**
 * contract-service.js - 계약 API 서비스
 * Phase 7: utils/contract-api.js에서 services/로 이동
 *
 * 포함 기능:
 * - approveContract: 계약 승인 API
 * - rejectContract: 계약 거절 API
 * - terminateContract: 계약 종료 API
 * - checkBusinessNumber: 사업자등록번호 중복 확인 API
 */

import { post, get } from '../../../shared/utils/api.js';
import { showToast } from '../../../shared/components/toast.js';

const API_BASE = '/contracts/api';

/**
 * 계약 승인
 * @param {number|string} contractId - 계약 ID
 * @param {Object} options - 옵션
 * @param {string} options.confirmMessage - 확인 메시지
 * @param {string} options.successMessage - 성공 메시지
 * @param {boolean} options.reload - 성공 후 페이지 새로고침 (기본: true)
 * @returns {Promise<boolean>} 성공 여부
 */
export async function approveContract(contractId, options = {}) {
    const confirmMsg = options.confirmMessage || '이 계약 요청을 승인하시겠습니까?';

    if (!confirm(confirmMsg)) return false;

    try {
        const result = await post(`${API_BASE}/${contractId}/approve`);

        if (result.success) {
            showToast(options.successMessage || '계약이 승인되었습니다.', 'success');
            if (options.reload !== false) location.reload();
            return true;
        } else {
            showToast(result.message || '오류가 발생했습니다.', 'error');
            return false;
        }
    } catch (error) {
        console.error('계약 승인 오류:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
        return false;
    }
}

/**
 * 계약 거절
 * @param {number|string} contractId - 계약 ID
 * @param {Object} options - 옵션
 * @param {string} options.reasonPrompt - 사유 입력 프롬프트
 * @param {string} options.successMessage - 성공 메시지
 * @param {boolean} options.reload - 성공 후 페이지 새로고침 (기본: true)
 * @returns {Promise<boolean>} 성공 여부
 */
export async function rejectContract(contractId, options = {}) {
    const reason = prompt(options.reasonPrompt || '거절 사유를 입력해주세요 (선택사항):');
    if (reason === null) return false;

    try {
        const result = await post(`${API_BASE}/${contractId}/reject`, { reason });

        if (result.success) {
            showToast(options.successMessage || '계약 요청이 거절되었습니다.', 'success');
            if (options.reload !== false) location.reload();
            return true;
        } else {
            showToast(result.message || '오류가 발생했습니다.', 'error');
            return false;
        }
    } catch (error) {
        console.error('계약 거절 오류:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
        return false;
    }
}

/**
 * 계약 종료 요청 (양측 동의 방식)
 * 상대방이 승인해야 최종 종료됨
 * @param {number|string} contractId - 계약 ID
 * @param {Object} options - 옵션
 * @param {string} options.reasonPrompt - 사유 입력 프롬프트
 * @param {string} options.confirmMessage - 확인 메시지
 * @param {string} options.successMessage - 성공 메시지
 * @param {boolean} options.reload - 성공 후 페이지 새로고침 (기본: true)
 * @returns {Promise<boolean>} 성공 여부
 */
export async function terminateContract(contractId, options = {}) {
    const reason = prompt(options.reasonPrompt || '계약 종료 사유를 입력해주세요 (선택사항):');
    if (reason === null) return false;

    const confirmMsg = options.confirmMessage || '계약 종료를 요청하시겠습니까?\n상대방이 승인해야 최종 종료됩니다.';
    if (!confirm(confirmMsg)) return false;

    try {
        // 양측 동의 API 호출
        const result = await post(`/api/sync/contracts/${contractId}/request-termination`, { reason });

        if (result.success) {
            showToast(options.successMessage || '계약 종료가 요청되었습니다. 상대방의 승인을 기다려주세요.', 'success');
            if (options.reload !== false) location.reload();
            return true;
        } else {
            showToast(result.message || result.error || '오류가 발생했습니다.', 'error');
            return false;
        }
    } catch (error) {
        console.error('계약 종료 요청 오류:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
        return false;
    }
}

/**
 * 계약 종료 승인 (양측 동의 방식)
 * 상대방의 종료 요청을 승인하여 최종 종료
 * @param {number|string} contractId - 계약 ID
 * @param {Object} options - 옵션
 * @returns {Promise<boolean>} 성공 여부
 */
export async function approveTermination(contractId, options = {}) {
    const confirmMsg = options.confirmMessage || '계약 종료를 승인하시겠습니까?\n승인 시 계약이 최종 종료됩니다.';
    if (!confirm(confirmMsg)) return false;

    try {
        const result = await post(`/api/sync/contracts/${contractId}/approve-termination`);

        if (result.success) {
            showToast(options.successMessage || '계약이 종료되었습니다.', 'success');
            if (options.reload !== false) location.reload();
            return true;
        } else {
            showToast(result.message || result.error || '오류가 발생했습니다.', 'error');
            return false;
        }
    } catch (error) {
        console.error('계약 종료 승인 오류:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
        return false;
    }
}

/**
 * 계약 종료 거절 (양측 동의 방식)
 * 상대방의 종료 요청을 거절하여 계약 유지
 * @param {number|string} contractId - 계약 ID
 * @param {Object} options - 옵션
 * @returns {Promise<boolean>} 성공 여부
 */
export async function rejectTermination(contractId, options = {}) {
    const reason = prompt(options.reasonPrompt || '종료 거절 사유를 입력해주세요 (선택사항):');
    if (reason === null) return false;

    try {
        const result = await post(`/api/sync/contracts/${contractId}/reject-termination`, { reason });

        if (result.success) {
            showToast(options.successMessage || '계약 종료 요청이 거절되었습니다.', 'success');
            if (options.reload !== false) location.reload();
            return true;
        } else {
            showToast(result.message || result.error || '오류가 발생했습니다.', 'error');
            return false;
        }
    } catch (error) {
        console.error('계약 종료 거절 오류:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
        return false;
    }
}

/**
 * 사업자등록번호 중복 확인
 * @param {string} businessNumber - 사업자등록번호
 * @returns {Promise<{available: boolean, message: string}>} 확인 결과
 */
export async function checkBusinessNumber(businessNumber) {
    if (!businessNumber || !businessNumber.trim()) {
        return { available: false, message: '사업자등록번호를 입력해주세요.' };
    }

    try {
        const data = await get('/corporate/api/check-business-number', {
            business_number: businessNumber
        });

        return {
            available: data.available,
            message: data.available
                ? '사용 가능한 사업자등록번호입니다.'
                : '이미 등록된 사업자등록번호입니다.'
        };
    } catch (error) {
        console.error('사업자등록번호 확인 오류:', error);
        return { available: false, message: '확인 중 오류가 발생했습니다.' };
    }
}

// 전역 함수로 노출 (비모듈 환경 호환)
if (typeof window !== 'undefined') {
    window.HRContractAPI = {
        approveContract,
        rejectContract,
        terminateContract,
        approveTermination,
        rejectTermination,
        checkBusinessNumber
    };

    // 기존 전역 함수 호환성 유지
    window.approveContract = function(id) { return approveContract(id); };
    window.rejectContract = function(id) { return rejectContract(id); };
    window.terminateContract = function(id) { return terminateContract(id); };
    window.approveTermination = function(id) { return approveTermination(id); };
    window.rejectTermination = function(id) { return rejectTermination(id); };

    // 이벤트 위임: data-action 기반 버튼 클릭 핸들러
    document.addEventListener('DOMContentLoaded', () => {
        document.addEventListener('click', async (e) => {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;
            const contractId = target.dataset.contractId;

            if (!contractId) return;

            e.preventDefault();

            switch (action) {
                case 'approve-contract':
                    await approveContract(contractId);
                    break;
                case 'reject-contract':
                    await rejectContract(contractId);
                    break;
                case 'terminate-contract':
                    await terminateContract(contractId);
                    break;
                case 'approve-termination':
                    await approveTermination(contractId);
                    break;
                case 'reject-termination':
                    await rejectTermination(contractId);
                    break;
            }
        });
    });
}
