/**
 * contract-api.js - 계약 API 유틸리티
 * 
 * 포함 기능:
 * - approveContract: 계약 승인 API
 * - rejectContract: 계약 거절 API
 * - terminateContract: 계약 종료 API
 * - checkBusinessNumber: 사업자등록번호 중복 확인 API
 */

const API_BASE = '/contracts/api';

/**
 * API 요청 래퍼 함수
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: { 'Content-Type': 'application/json' }
    };
    
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        return await response.json();
    } catch (error) {
        console.error('API 요청 오류:', error);
        return { success: false, message: '요청 처리 중 오류가 발생했습니다.' };
    }
}

/**
 * 계약 승인
 */
export async function approveContract(contractId, options = {}) {
    const confirmMsg = options.confirmMessage || '이 계약 요청을 승인하시겠습니까?';
    
    if (\!confirm(confirmMsg)) return false;
    
    const result = await apiRequest(
        API_BASE + '/' + contractId + '/approve',
        { method: 'POST' }
    );
    
    if (result.success) {
        alert(options.successMessage || '계약이 승인되었습니다.');
        if (options.reload \!== false) location.reload();
        return true;
    } else {
        alert(result.message || '오류가 발생했습니다.');
        return false;
    }
}

/**
 * 계약 거절
 */
export async function rejectContract(contractId, options = {}) {
    const reason = prompt(options.reasonPrompt || '거절 사유를 입력해주세요 (선택사항):');
    if (reason === null) return false;
    
    const result = await apiRequest(
        API_BASE + '/' + contractId + '/reject',
        {
            method: 'POST',
            body: JSON.stringify({ reason })
        }
    );
    
    if (result.success) {
        alert(options.successMessage || '계약 요청이 거절되었습니다.');
        if (options.reload \!== false) location.reload();
        return true;
    } else {
        alert(result.message || '오류가 발생했습니다.');
        return false;
    }
}

/**
 * 계약 종료
 */
export async function terminateContract(contractId, options = {}) {
    const reason = prompt(options.reasonPrompt || '계약 종료 사유를 입력해주세요 (선택사항):');
    if (reason === null) return false;
    
    const confirmMsg = options.confirmMessage || '정말 이 계약을 종료하시겠습니까?';
    if (\!confirm(confirmMsg)) return false;
    
    const result = await apiRequest(
        API_BASE + '/' + contractId + '/terminate',
        {
            method: 'POST',
            body: JSON.stringify({ reason })
        }
    );
    
    if (result.success) {
        alert(options.successMessage || '계약이 종료되었습니다.');
        if (options.reload \!== false) location.reload();
        return true;
    } else {
        alert(result.message || '오류가 발생했습니다.');
        return false;
    }
}

/**
 * 사업자등록번호 중복 확인
 */
export async function checkBusinessNumber(businessNumber) {
    if (\!businessNumber || \!businessNumber.trim()) {
        return { available: false, message: '사업자등록번호를 입력해주세요.' };
    }
    
    try {
        const response = await fetch(
            '/corporate/api/check-business-number?business_number=' + encodeURIComponent(businessNumber)
        );
        const data = await response.json();
        
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
if (typeof window \!== 'undefined') {
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
}
