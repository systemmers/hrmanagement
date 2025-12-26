/**
 * Profile Sync Module
 *
 * 개인 프로필 데이터를 직원 정보로 동기화하는 기능
 * profile/detail.html에서 사용
 */

/**
 * 프로필 동기화 초기화
 * DOMContentLoaded 시 자동 실행
 */
function initProfileSync() {
    const syncBtn = document.getElementById('syncProfileBtn');
    if (!syncBtn) return;

    syncBtn.addEventListener('click', async function() {
        const contractId = this.dataset.contractId;
        if (!contractId) return;

        const confirmed = confirm('개인 프로필 데이터를 직원 정보로 동기화하시겠습니까?\n\n학력, 경력, 자격증, 어학, 병역, 가족 정보가 업데이트됩니다.');
        if (!confirmed) return;

        syncBtn.disabled = true;
        syncBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>동기화 중...</span>';

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            const response = await fetch(`/api/sync/full-sync/${contractId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''
                }
            });

            const result = await response.json();

            if (result.success) {
                alert(`동기화 완료!\n\n동기화된 항목: ${result.relations?.join(', ') || '없음'}`);
                location.reload();
            } else {
                alert(`동기화 실패: ${result.error || '알 수 없는 오류'}`);
            }
        } catch (error) {
            alert('동기화 중 오류가 발생했습니다: ' + error.message);
        } finally {
            syncBtn.disabled = false;
            syncBtn.innerHTML = '<i class="fas fa-sync"></i> <span>프로필 동기화</span>';
        }
    });
}

// DOMContentLoaded 시 자동 초기화
document.addEventListener('DOMContentLoaded', initProfileSync);
