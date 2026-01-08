/**
 * Contract Request Page JavaScript
 * 계약 요청 페이지 스크립트
 *
 * 기능:
 * - 탭 전환 (직원 계정 / 개인 계정)
 * - 대상 선택 및 폼 자동 입력
 * - 폼 제출 검증
 */

document.addEventListener('DOMContentLoaded', function() {
    initContractRequestForm();
});

/**
 * 계약 요청 폼 초기화
 */
function initContractRequestForm() {
    initTabNavigation();
    initTargetSelection();
    initFormValidation();
}

/**
 * 탭 네비게이션 초기화
 */
function initTabNavigation() {
    const tabs = document.querySelectorAll('.tab-btn[data-tab]');
    const panels = document.querySelectorAll('.tab-panel[id^="panel-"]');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetPanel = this.dataset.tab;

            // 탭 활성화
            tabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');

            // 패널 전환
            panels.forEach(p => p.classList.remove('active'));
            const panel = document.getElementById('panel-' + targetPanel);
            if (panel) {
                panel.classList.add('active');
            }
        });
    });
}

/**
 * 대상 선택 초기화
 */
function initTargetSelection() {
    const radios = document.querySelectorAll('input[name="target_selection"]');
    const targetUserIdInput = document.getElementById('target_user_id');
    const departmentInput = document.getElementById('department');
    const positionInput = document.getElementById('position');

    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            // hidden input 업데이트
            if (targetUserIdInput) {
                targetUserIdInput.value = this.value;
            }

            // 선택 스타일 업데이트
            document.querySelectorAll('.target-item').forEach(item => {
                item.classList.remove('selected');
            });
            this.closest('.target-item').classList.add('selected');

            // 직원 정보로 부서/직위 자동 입력 (비어있는 경우만)
            const dept = this.dataset.department;
            const pos = this.dataset.position;
            if (dept && departmentInput && !departmentInput.value) {
                departmentInput.value = dept;
            }
            if (pos && positionInput && !positionInput.value) {
                positionInput.value = pos;
            }
        });
    });
}

/**
 * 폼 제출 검증 초기화
 */
function initFormValidation() {
    const form = document.getElementById('contractForm');
    const targetUserIdInput = document.getElementById('target_user_id');

    if (form) {
        form.addEventListener('submit', function(e) {
            if (!targetUserIdInput || !targetUserIdInput.value) {
                e.preventDefault();
                alert('계약 대상을 선택해주세요.');
                return false;
            }
        });
    }
}
