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

import { post, get } from '../utils/api.js';
import { showToast } from '../components/toast.js';

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
 * 계약 종료
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

    const confirmMsg = options.confirmMessage || '정말 이 계약을 종료하시겠습니까?';
    if (!confirm(confirmMsg)) return false;

    try {
        const result = await post(`${API_BASE}/${contractId}/terminate`, { reason });

        if (result.success) {
            showToast(options.successMessage || '계약이 종료되었습니다.', 'success');
            if (options.reload !== false) location.reload();
            return true;
        } else {
            showToast(result.message || '오류가 발생했습니다.', 'error');
            return false;
        }
    } catch (error) {
        console.error('계약 종료 오류:', error);
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
        checkBusinessNumber
    };

    // 기존 전역 함수 호환성 유지
    window.approveContract = function(id) { return approveContract(id); };
    window.rejectContract = function(id) { return rejectContract(id); };
    window.terminateContract = function(id) { return terminateContract(id); };

    // 이벤트 위임: data-action 기반 버튼 클릭 핸들러
    document.addEventListener('DOMContentLoaded', () => {
        document.addEventListener('click', async (e) => {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;
            const contractId = target.dataset.contractId;

            if (!contractId) return;

            e.preventDefault();

            if (action === 'approve-contract') {
                await approveContract(contractId);
            } else if (action === 'reject-contract') {
                await rejectContract(contractId);
            } else if (action === 'terminate-contract') {
                await terminateContract(contractId);
            }
        });
    });
}
