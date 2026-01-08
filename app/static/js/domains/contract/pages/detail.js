/**
 * contract-detail.js - 계약 상세 페이지 스크립트
 *
 * 포함 기능:
 * - 계약 승인/거절/종료 이벤트 위임
 * - 공유 설정 폼 제출
 */

// 이벤트 위임 초기화
document.addEventListener('DOMContentLoaded', function() {
    initContractDetailActions();
    initSharingSettingsForm();
});

/**
 * 계약 상세 액션 버튼 이벤트 위임
 */
function initContractDetailActions() {
    document.addEventListener('click', async function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;
        const contractId = target.dataset.contractId;

        if (!contractId) return;

        switch (action) {
            case 'approve-contract':
                if (typeof approveContract === 'function') {
                    await approveContract(contractId);
                }
                break;
            case 'reject-contract':
                if (typeof rejectContract === 'function') {
                    await rejectContract(contractId);
                }
                break;
            case 'terminate-contract':
                if (typeof terminateContract === 'function') {
                    await terminateContract(contractId);
                }
                break;
        }
    });
}

/**
 * 공유 설정 폼 초기화
 */
function initSharingSettingsForm() {
    const form = document.getElementById('sharingSettingsForm');
    if (!form) return;

    // contract_id를 폼의 data 속성에서 가져오거나 URL에서 추출
    const contractId = form.dataset.contractId || getContractIdFromUrl();

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const settings = {
            share_basic_info: formData.has('share_basic_info'),
            share_contact: formData.has('share_contact'),
            share_education: formData.has('share_education'),
            share_career: formData.has('share_career'),
            share_certificates: formData.has('share_certificates'),
            share_languages: formData.has('share_languages'),
            share_military: formData.has('share_military'),
            is_realtime_sync: formData.has('is_realtime_sync')
        };

        try {
            const response = await fetch(`/contracts/api/${contractId}/sharing-settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });

            const result = await response.json();

            if (result.success) {
                alert('공유 설정이 저장되었습니다.');
            } else {
                alert(result.message || '오류가 발생했습니다.');
            }
        } catch (error) {
            alert('요청 처리 중 오류가 발생했습니다.');
        }
    });
}

/**
 * URL에서 계약 ID 추출
 */
function getContractIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    // /contracts/{id} 형식 가정
    const contractIndex = pathParts.indexOf('contracts');
    if (contractIndex !== -1 && pathParts[contractIndex + 1]) {
        return pathParts[contractIndex + 1];
    }
    return null;
}
