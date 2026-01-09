/**
 * Contract Request Modal JavaScript
 * 계약 요청 모달 스크립트
 *
 * 3-Step Modal:
 * - Step 1: 대상 선택 (직원/개인 계정)
 * - Step 2: 계약 정보 입력
 * - Step 3: 확인 및 제출
 */

import { get, post } from '../../../shared/utils/api.js';
import { showToast } from '../../../shared/components/toast.js';

// State
let currentStep = 1;
let selectedTarget = null;
let targetsData = null;

// DOM Elements
let modal, form;
let employeeList, personalList;
let employeeCount, personalCount;

document.addEventListener('DOMContentLoaded', function() {
    initContractRequestModal();
});

/**
 * Initialize contract request modal
 */
function initContractRequestModal() {
    modal = document.getElementById('contractRequestModal');
    form = document.getElementById('contractRequestForm');

    if (!modal || !form) return;

    employeeList = document.getElementById('employeeTargetList');
    personalList = document.getElementById('personalTargetList');
    employeeCount = document.getElementById('employeeCount');
    personalCount = document.getElementById('personalCount');

    // Open modal button
    const openBtn = document.getElementById('openContractRequestModal');
    if (openBtn) {
        openBtn.addEventListener('click', openModal);
    }

    // Filter pending button
    const filterPendingBtn = document.getElementById('filterPendingBtn');
    if (filterPendingBtn) {
        filterPendingBtn.addEventListener('click', filterPendingContracts);
    }

    // Close modal buttons
    modal.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    // Backdrop click
    modal.querySelector('.modal__backdrop').addEventListener('click', closeModal);

    // Tab navigation
    initTabNavigation();

    // Step navigation
    initStepNavigation();

    // Form submission
    form.addEventListener('submit', handleFormSubmit);
}

/**
 * Open modal and load data
 */
async function openModal() {
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Reset state
    currentStep = 1;
    selectedTarget = null;
    form.reset();
    updateStepUI();

    // Load targets
    await loadEligibleTargets();
}

/**
 * Close modal
 */
function closeModal() {
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

/**
 * Load eligible targets from API
 */
async function loadEligibleTargets() {
    showLoading(employeeList);
    showLoading(personalList);

    try {
        const result = await get('/contracts/api/eligible-targets');

        if (result.success) {
            targetsData = result.data;
            renderTargetList(employeeList, targetsData.employee_accounts || [], 'employee');
            renderTargetList(personalList, targetsData.personal_accounts || [], 'personal');

            if (employeeCount) employeeCount.textContent = (targetsData.employee_accounts || []).length;
            if (personalCount) personalCount.textContent = (targetsData.personal_accounts || []).length;
        } else {
            showToast(result.message || '대상 목록을 불러오는데 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Failed to load targets:', error);
        showToast('대상 목록을 불러오는데 실패했습니다.', 'error');
    }
}

/**
 * Render target list
 */
function renderTargetList(container, targets, type) {
    if (!targets || targets.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>${type === 'employee' ? '계약 요청 가능한 직원이 없습니다.' : '계약 요청 가능한 개인 계정이 없습니다.'}</p>
            </div>
        `;
        return;
    }

    container.innerHTML = targets.map(target => `
        <label class="target-item" data-user-id="${target.user_id}">
            <input type="radio" name="target_selection" value="${target.user_id}"
                   data-name="${target.name || ''}"
                   data-email="${target.email || ''}"
                   data-department="${target.department || ''}"
                   data-position="${target.position || ''}"
                   data-type="${type}">
            <div class="target-info">
                <div class="target-name">${target.name || '이름 없음'}</div>
                <div class="target-email">${target.email || ''}</div>
                <div class="target-meta">
                    ${target.department ? target.department : ''}
                    ${target.department && target.position ? ' / ' : ''}
                    ${target.position ? target.position : ''}
                    ${type === 'employee' ?
                        `<span class="badge ${target.status === 'pending_info' ? 'badge-danger' : 'badge-warning'}">
                            ${target.status === 'pending_info' ? '프로필 미완성' : '계약 대기'}
                        </span>` :
                        '<span class="badge badge-info">개인 계정</span>'
                    }
                </div>
            </div>
        </label>
    `).join('');

    // Add selection handlers
    container.querySelectorAll('input[name="target_selection"]').forEach(radio => {
        radio.addEventListener('change', handleTargetSelection);
    });
}

/**
 * Handle target selection
 */
function handleTargetSelection(e) {
    const radio = e.target;

    selectedTarget = {
        userId: radio.value,
        name: radio.dataset.name,
        email: radio.dataset.email,
        department: radio.dataset.department,
        position: radio.dataset.position,
        type: radio.dataset.type
    };

    // Update hidden input
    document.getElementById('modalTargetUserId').value = selectedTarget.userId;

    // Update selection UI
    modal.querySelectorAll('.target-item').forEach(item => item.classList.remove('selected'));
    radio.closest('.target-item').classList.add('selected');

    // Auto-fill department/position if available
    const deptInput = document.getElementById('modalDepartment');
    const posInput = document.getElementById('modalPosition');

    if (deptInput && selectedTarget.department && !deptInput.value) {
        deptInput.value = selectedTarget.department;
    }
    if (posInput && selectedTarget.position && !posInput.value) {
        posInput.value = selectedTarget.position;
    }

    // Enable next button
    document.getElementById('step1NextBtn').disabled = false;
}

/**
 * Initialize tab navigation
 */
function initTabNavigation() {
    const tabs = modal.querySelectorAll('.tab-btn[data-tab]');
    const panels = modal.querySelectorAll('.tab-panel[id^="modal-panel-"]');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetPanel = this.dataset.tab;

            // Update tabs
            tabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');

            // Update panels
            panels.forEach(p => p.classList.remove('active'));
            const panel = document.getElementById('modal-panel-' + targetPanel);
            if (panel) panel.classList.add('active');
        });
    });
}

/**
 * Initialize step navigation
 */
function initStepNavigation() {
    // Next buttons
    modal.querySelectorAll('[data-step-next]').forEach(btn => {
        btn.addEventListener('click', function() {
            const nextStep = parseInt(this.dataset.stepNext);
            goToStep(nextStep);
        });
    });

    // Previous buttons
    modal.querySelectorAll('[data-step-prev]').forEach(btn => {
        btn.addEventListener('click', function() {
            const prevStep = parseInt(this.dataset.stepPrev);
            goToStep(prevStep);
        });
    });
}

/**
 * Go to specific step
 */
function goToStep(step) {
    // Validate before moving forward
    if (step > currentStep) {
        if (!validateCurrentStep()) return;
    }

    currentStep = step;
    updateStepUI();

    // Update confirm section for step 3
    if (step === 3) {
        updateConfirmSection();
    }

    // Update selected target info for step 2
    if (step === 2) {
        updateSelectedTargetInfo();
    }
}

/**
 * Validate current step
 */
function validateCurrentStep() {
    if (currentStep === 1) {
        if (!selectedTarget) {
            showToast('계약 대상을 선택해주세요.', 'warning');
            return false;
        }
    }

    if (currentStep === 2) {
        const contractType = document.getElementById('modalContractType').value;
        if (!contractType) {
            showToast('계약 유형을 선택해주세요.', 'warning');
            return false;
        }
    }

    return true;
}

/**
 * Update step UI
 */
function updateStepUI() {
    // Update step indicators
    modal.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');

        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });

    // Update step content
    modal.querySelectorAll('.modal-step-content').forEach(content => {
        const contentStep = parseInt(content.dataset.stepContent);
        content.classList.toggle('active', contentStep === currentStep);
    });
}

/**
 * Update selected target info in step 2
 */
function updateSelectedTargetInfo() {
    const container = document.getElementById('selectedTargetInfo');
    if (!container || !selectedTarget) return;

    container.innerHTML = `
        <div class="target-avatar">${selectedTarget.name ? selectedTarget.name.charAt(0) : '?'}</div>
        <div class="target-info">
            <div class="target-name">${selectedTarget.name || '이름 없음'}</div>
            <div class="target-email">${selectedTarget.email || ''}</div>
        </div>
    `;
}

/**
 * Update confirm section in step 3
 */
function updateConfirmSection() {
    const contractType = document.getElementById('modalContractType');
    const startDate = document.getElementById('modalStartDate').value;
    const endDate = document.getElementById('modalEndDate').value;
    const department = document.getElementById('modalDepartment').value;
    const position = document.getElementById('modalPosition').value;
    const notes = document.getElementById('modalNotes').value;

    const contractTypeLabels = {
        'employment': '정규직',
        'contract': '계약직',
        'freelance': '프리랜서',
        'intern': '인턴'
    };

    document.getElementById('confirmTarget').textContent = selectedTarget ? selectedTarget.name : '-';
    document.getElementById('confirmContractType').textContent = contractTypeLabels[contractType.value] || contractType.value || '-';
    document.getElementById('confirmDepartment').textContent = department || '-';
    document.getElementById('confirmPosition').textContent = position || '-';
    document.getElementById('confirmPeriod').textContent = startDate || endDate ?
        `${startDate || '미정'} ~ ${endDate || '미정'}` : '-';
    document.getElementById('confirmNotes').textContent = notes || '-';
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    if (!validateCurrentStep()) return;

    const submitBtn = document.getElementById('submitContractBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 처리 중...';

    const formData = {
        target_user_id: parseInt(document.getElementById('modalTargetUserId').value),
        contract_type: document.getElementById('modalContractType').value,
        contract_start_date: document.getElementById('modalStartDate').value || null,
        contract_end_date: document.getElementById('modalEndDate').value || null,
        department: document.getElementById('modalDepartment').value || null,
        position: document.getElementById('modalPosition').value || null,
        notes: document.getElementById('modalNotes').value || null
    };

    try {
        const result = await post('/contracts/api/create', formData);

        if (result.success) {
            showToast(result.message || '계약 요청이 전송되었습니다.', 'success');
            closeModal();
            location.reload();
        } else {
            showToast(result.message || '계약 요청에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Contract request error:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 계약 요청 전송';
    }
}

/**
 * Show loading state
 */
function showLoading(container) {
    container.innerHTML = `
        <div class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <span>대상 목록을 불러오는 중...</span>
        </div>
    `;
}

/**
 * Filter to show only pending contracts
 */
function filterPendingContracts() {
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.value = 'requested';
        statusFilter.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

// Export for testing
export { openModal, closeModal };
