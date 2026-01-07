/**
 * SalaryCalculatorModal 클래스
 * Phase 7: 프론트엔드 리팩토링 - salary-calculator.js 분할
 *
 * 급여 계산기 모달 UI 관리 (수당 관리 기능 포함)
 */

import { AllowanceManager } from './allowance-manager.js';
import { SalaryCalculator } from './calculator.js';
import { showToast } from '../toast.js';
import { formatNumber, parseNumber } from '../../../shared/utils/formatting.js';

/**
 * SalaryCalculatorModal 클래스
 * 급여 계산기 모달 UI 관리 (수당 관리 기능 포함)
 */
export class SalaryCalculatorModal {
    constructor(options = {}) {
        this.modalId = options.modalId || 'salaryCalculatorModal';

        // AllowanceManager 초기화
        this.allowanceManager = new AllowanceManager(options.initialAllowances);
        this.allowanceManager.onChange = () => this.onAllowanceChange();

        // SalaryCalculator 초기화 (AllowanceManager 연결)
        this.calculator = new SalaryCalculator({
            onCalculate: (result) => this.updateUI(result),
            onValidationChange: (validation) => this.updateValidationUI(validation),
            allowanceManager: this.allowanceManager
        });

        this.onApply = options.onApply || null;
        this.debounceTimer = null;
        this.debounceDelay = options.debounceDelay || 300;

        this.elements = {};
        this.isInitialized = false;
        this.showAddForm = false;
    }

    /**
     * 모달 초기화
     */
    init() {
        if (this.isInitialized) return;

        this.cacheElements();
        this.bindEvents();
        this.renderAllowanceTable();
        this.isInitialized = true;
    }

    /**
     * DOM 요소 캐싱
     */
    cacheElements() {
        const modal = document.getElementById(this.modalId);
        if (!modal) return;

        this.elements = {
            modal,
            // 입력 필드
            annualSalary: modal.querySelector('#calcAnnualSalary'),
            mealAllowance: modal.querySelector('#calcMealAllowance'),
            overtimeHours: modal.querySelector('#calcOvertimeHours'),
            nightHours: modal.querySelector('#calcNightHours'),
            holidayDays: modal.querySelector('#calcHolidayDays'),
            // 결과 표시
            hourlyWage: modal.querySelector('#calcHourlyWage'),
            baseSalary: modal.querySelector('#calcBaseSalary'),
            mealResult: modal.querySelector('#calcMealResult'),
            overtimeAllowance: modal.querySelector('#calcOvertimeAllowance'),
            nightAllowance: modal.querySelector('#calcNightAllowance'),
            holidayAllowance: modal.querySelector('#calcHolidayAllowance'),
            totalSalary: modal.querySelector('#calcTotalSalary'),
            // 검증 상태
            validationStatus: modal.querySelector('#calcValidationStatus'),
            minimumWageCompare: modal.querySelector('#calcMinimumWageCompare'),
            // 수식 표시
            overtimeFormula: modal.querySelector('#calcOvertimeFormula'),
            nightFormula: modal.querySelector('#calcNightFormula'),
            holidayFormula: modal.querySelector('#calcHolidayFormula'),
            // 버튼
            applyBtn: modal.querySelector('#calcApplyBtn'),
            closeBtn: modal.querySelector('#calcCloseBtn'),
            // 수당 관리 영역
            allowanceTable: modal.querySelector('#calcAllowanceTable'),
            allowanceTableBody: modal.querySelector('#calcAllowanceTableBody'),
            addAllowanceBtn: modal.querySelector('#calcAddAllowanceBtn'),
            allowanceAddForm: modal.querySelector('#calcAllowanceAddForm'),
            // 수당 합계 표시
            ordinaryIncludedSum: modal.querySelector('#calcOrdinaryIncludedSum'),
            ordinaryExcludedSum: modal.querySelector('#calcOrdinaryExcludedSum'),
            allowanceTotalSum: modal.querySelector('#calcAllowanceTotalSum'),
            // 결과 섹션 수당 표시
            ordinaryIncludedResult: modal.querySelector('#calcOrdinaryIncludedResult'),
            ordinaryExcludedResult: modal.querySelector('#calcOrdinaryExcludedResult'),
            ordinaryIncludedNames: modal.querySelector('#calcOrdinaryIncludedNames'),
            ordinaryExcludedNames: modal.querySelector('#calcOrdinaryExcludedNames')
        };
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 숫자 입력 필드 (콤마 포맷팅)
        ['annualSalary'].forEach(key => {
            const el = this.elements[key];
            if (!el) return;

            el.addEventListener('blur', () => this.formatInput(el));
            el.addEventListener('input', () => this.debouncedCalculate());
        });

        // 시간/일수 입력 필드
        ['overtimeHours', 'nightHours', 'holidayDays'].forEach(key => {
            const el = this.elements[key];
            if (!el) return;

            el.addEventListener('input', () => this.debouncedCalculate());
        });

        // 적용 버튼
        if (this.elements.applyBtn) {
            this.elements.applyBtn.addEventListener('click', () => this.apply());
        }

        // 닫기 버튼
        if (this.elements.closeBtn) {
            this.elements.closeBtn.addEventListener('click', () => this.close());
        }

        // 수당 추가 버튼
        if (this.elements.addAllowanceBtn) {
            this.elements.addAllowanceBtn.addEventListener('click', () => this.toggleAddForm());
        }

        // 모달 외부 클릭 시 닫기
        if (this.elements.modal) {
            this.elements.modal.addEventListener('click', (e) => {
                if (e.target === this.elements.modal) {
                    this.close();
                }
            });
        }

        // ESC 키로 닫기
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    }

    /**
     * 수당 변경 시 콜백
     */
    onAllowanceChange() {
        this.renderAllowanceTable();
        this.updateAllowanceSummary();
        this.debouncedCalculate();
    }

    /**
     * 수당 테이블 렌더링
     */
    renderAllowanceTable() {
        const tbody = this.elements.allowanceTableBody;
        if (!tbody) return;

        const allowances = this.allowanceManager.getAllAllowances();

        tbody.innerHTML = allowances.map(allowance => `
            <tr data-allowance-id="${allowance.id}">
                <td class="allowance-name-cell">
                    <div class="allowance-name-wrapper">
                        <span class="allowance-name">${allowance.name}</span>
                        <span class="allowance-tax-badge ${allowance.taxable ? 'taxable' : 'non-taxable'}">
                            ${allowance.taxable ? '과세' : '비과세'}
                        </span>
                    </div>
                </td>
                <td class="allowance-amount-cell">
                    <input type="text"
                           class="allowance-amount-input"
                           value="${formatNumber(allowance.amount)}"
                           data-allowance-id="${allowance.id}">
                </td>
                <td class="allowance-toggle-cell">
                    <label class="toggle-switch">
                        <input type="checkbox"
                               class="allowance-ordinary-toggle"
                               data-allowance-id="${allowance.id}"
                               ${allowance.includedInOrdinaryWage ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">${allowance.includedInOrdinaryWage ? '포함' : '미포함'}</span>
                </td>
                <td class="allowance-action-cell">
                    <button type="button"
                            class="btn-allowance-delete"
                            data-allowance-id="${allowance.id}"
                            ${!allowance.removable ? 'disabled' : ''}>
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        // 이벤트 바인딩
        this.bindAllowanceTableEvents();
    }

    /**
     * 수당 테이블 이벤트 바인딩
     */
    bindAllowanceTableEvents() {
        const tbody = this.elements.allowanceTableBody;
        if (!tbody) return;

        // 금액 입력 이벤트
        tbody.querySelectorAll('.allowance-amount-input').forEach(input => {
            input.addEventListener('blur', (e) => {
                const id = e.target.dataset.allowanceId;
                const amount = parseNumber(e.target.value);
                this.allowanceManager.updateAllowance(id, { amount });
                e.target.value = formatNumber(amount);
            });
            input.addEventListener('input', () => this.debouncedCalculate());
        });

        // 통상임금 포함 토글 이벤트
        tbody.querySelectorAll('.allowance-ordinary-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const id = e.target.dataset.allowanceId;
                const includedInOrdinaryWage = e.target.checked;
                this.allowanceManager.updateAllowance(id, { includedInOrdinaryWage });

                // 라벨 업데이트
                const label = e.target.closest('td').querySelector('.toggle-label');
                if (label) {
                    label.textContent = includedInOrdinaryWage ? '포함' : '미포함';
                }

                // 통상임금 변경 시 재계산
                this.debouncedCalculate();
            });
        });

        // 삭제 버튼 이벤트
        tbody.querySelectorAll('.btn-allowance-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.allowanceId;
                this.allowanceManager.removeAllowance(id);
            });
        });
    }

    /**
     * 수당 추가 폼 토글
     */
    toggleAddForm() {
        this.showAddForm = !this.showAddForm;

        let formContainer = this.elements.modal.querySelector('.allowance-add-inline');

        if (this.showAddForm) {
            if (!formContainer) {
                formContainer = document.createElement('div');
                formContainer.className = 'allowance-add-inline';
                formContainer.innerHTML = `
                    <input type="text" class="allowance-add-name" placeholder="수당명">
                    <input type="text" class="allowance-add-amount" placeholder="금액">
                    <label class="toggle-switch">
                        <input type="checkbox" class="allowance-add-ordinary">
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label">미포함</span>
                    <select class="allowance-add-taxable">
                        <option value="true">과세</option>
                        <option value="false">비과세</option>
                    </select>
                    <button type="button" class="btn-allowance-add-confirm">
                        <i class="fas fa-plus"></i> 추가
                    </button>
                    <button type="button" class="btn-allowance-add-cancel">
                        <i class="fas fa-times"></i> 취소
                    </button>
                `;

                // 테이블 아래에 추가
                const tableContainer = this.elements.allowanceTable?.parentElement;
                if (tableContainer) {
                    tableContainer.appendChild(formContainer);
                }

                // 토글 이벤트
                const ordinaryToggle = formContainer.querySelector('.allowance-add-ordinary');
                const toggleLabel = formContainer.querySelector('.toggle-label');
                ordinaryToggle.addEventListener('change', () => {
                    toggleLabel.textContent = ordinaryToggle.checked ? '포함' : '미포함';
                });

                // 추가 버튼 이벤트
                formContainer.querySelector('.btn-allowance-add-confirm').addEventListener('click', () => {
                    this.addNewAllowance(formContainer);
                });

                // 취소 버튼 이벤트
                formContainer.querySelector('.btn-allowance-add-cancel').addEventListener('click', () => {
                    this.toggleAddForm();
                });
            }
            formContainer.style.display = 'flex';
            formContainer.querySelector('.allowance-add-name').focus();
        } else {
            if (formContainer) {
                formContainer.style.display = 'none';
            }
        }
    }

    /**
     * 새 수당 추가
     * @param {HTMLElement} formContainer - 폼 컨테이너
     */
    addNewAllowance(formContainer) {
        const name = formContainer.querySelector('.allowance-add-name').value.trim();
        const amount = parseNumber(formContainer.querySelector('.allowance-add-amount').value);
        const includedInOrdinaryWage = formContainer.querySelector('.allowance-add-ordinary').checked;
        const taxable = formContainer.querySelector('.allowance-add-taxable').value === 'true';

        if (!name) {
            showToast('수당명을 입력해주세요.', 'error');
            return;
        }

        if (this.allowanceManager.isDuplicateName(name)) {
            showToast('이미 존재하는 수당명입니다.', 'error');
            return;
        }

        this.allowanceManager.addAllowance({
            name,
            amount,
            includedInOrdinaryWage,
            taxable
        });

        // 폼 초기화 및 닫기
        formContainer.querySelector('.allowance-add-name').value = '';
        formContainer.querySelector('.allowance-add-amount').value = '';
        formContainer.querySelector('.allowance-add-ordinary').checked = false;
        formContainer.querySelector('.toggle-label').textContent = '미포함';
        this.toggleAddForm();

        showToast(`'${name}' 수당이 추가되었습니다.`, 'success');
    }

    /**
     * 수당 합계 요약 업데이트
     */
    updateAllowanceSummary() {
        if (this.elements.ordinaryIncludedSum) {
            this.elements.ordinaryIncludedSum.textContent =
                formatNumber(this.allowanceManager.getOrdinaryWageIncludedSum()) + '원';
        }
        if (this.elements.ordinaryExcludedSum) {
            this.elements.ordinaryExcludedSum.textContent =
                formatNumber(this.allowanceManager.getOrdinaryWageExcludedSum()) + '원';
        }
        if (this.elements.allowanceTotalSum) {
            this.elements.allowanceTotalSum.textContent =
                formatNumber(this.allowanceManager.getTotalSum()) + '원';
        }
    }

    /**
     * 디바운스 계산
     */
    debouncedCalculate() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.calculate(), this.debounceDelay);
    }

    /**
     * 계산 실행
     */
    calculate() {
        const params = this.getInputValues();
        return this.calculator.calculate(params);
    }

    /**
     * 입력값 가져오기
     * @returns {Object} 입력값 객체
     */
    getInputValues() {
        return {
            annualSalary: parseNumber(this.elements.annualSalary?.value || 0),
            mealAllowance: parseNumber(this.elements.mealAllowance?.value || 0),
            overtimeHours: parseInt(this.elements.overtimeHours?.value, 10) || 0,
            nightHours: parseInt(this.elements.nightHours?.value, 10) || 0,
            holidayDays: parseInt(this.elements.holidayDays?.value, 10) || 0
        };
    }

    /**
     * UI 업데이트
     * @param {Object} result - 계산 결과
     */
    updateUI(result) {
        // 결과값 업데이트
        if (this.elements.hourlyWage) {
            this.elements.hourlyWage.textContent = formatNumber(result.hourlyWage) + '원';
        }
        if (this.elements.baseSalary) {
            this.elements.baseSalary.textContent = formatNumber(result.baseSalary) + '원';
        }
        if (this.elements.mealResult) {
            this.elements.mealResult.textContent = formatNumber(result.allowances.meal) + '원';
        }
        if (this.elements.overtimeAllowance) {
            this.elements.overtimeAllowance.textContent = formatNumber(result.allowances.overtime) + '원';
        }
        if (this.elements.nightAllowance) {
            this.elements.nightAllowance.textContent = formatNumber(result.allowances.night) + '원';
        }
        if (this.elements.holidayAllowance) {
            this.elements.holidayAllowance.textContent = formatNumber(result.allowances.holiday) + '원';
        }
        if (this.elements.totalSalary) {
            this.elements.totalSalary.textContent = formatNumber(result.monthlySalary) + '원';
        }

        // 수당 합계 요약 업데이트
        this.updateAllowanceSummary();

        // 수당 결과 표시 업데이트 (결과 섹션)
        this.updateAllowanceResultUI(result);

        // 수식 업데이트
        this.updateFormulas(result);

        // 최저임금 비교 업데이트
        if (this.elements.minimumWageCompare) {
            this.elements.minimumWageCompare.innerHTML =
                `최저임금(${formatNumber(this.calculator.constants.MINIMUM_WAGE)}원) 대비 <strong>${result.comparison.minimumWagePercent}%</strong>`;
        }

        // 검증 상태 업데이트
        this.updateValidationUI(result.validation, result.hourlyWage);
    }

    /**
     * 수당 결과 UI 업데이트
     * @param {Object} result - 계산 결과
     */
    updateAllowanceResultUI(result) {
        // 통상임금 포함 수당 결과
        if (this.elements.ordinaryIncludedResult) {
            this.elements.ordinaryIncludedResult.textContent =
                formatNumber(result.allowances.ordinaryIncluded) + '원';
        }

        // 통상임금 미포함 수당 결과
        if (this.elements.ordinaryExcludedResult) {
            this.elements.ordinaryExcludedResult.textContent =
                formatNumber(result.allowances.ordinaryExcluded) + '원';
        }

        // 통상임금 포함 수당명 목록
        if (this.elements.ordinaryIncludedNames) {
            const includedAllowances = this.allowanceManager.getOrdinaryWageIncludedAllowances();
            const names = includedAllowances.map(a => a.name).join(' + ') || '-';
            this.elements.ordinaryIncludedNames.textContent = names;
        }

        // 통상임금 미포함 수당명 목록
        if (this.elements.ordinaryExcludedNames) {
            const excludedAllowances = this.allowanceManager.getOrdinaryWageExcludedAllowances();
            const names = excludedAllowances.map(a =>
                a.taxable ? a.name : `${a.name} (비과세)`
            ).join(' + ') || '-';
            this.elements.ordinaryExcludedNames.textContent = names;
        }
    }

    /**
     * 수식 표시 업데이트
     * @param {Object} result - 계산 결과
     */
    updateFormulas(result) {
        const input = result.input;

        if (this.elements.overtimeFormula) {
            this.elements.overtimeFormula.textContent =
                `통상임금 x 1.5 x ${input.overtimeHours}시간`;
        }
        if (this.elements.nightFormula) {
            this.elements.nightFormula.textContent =
                `통상임금 x 0.5 x ${input.nightHours}시간`;
        }
        if (this.elements.holidayFormula) {
            this.elements.holidayFormula.textContent =
                `통상임금 x 1.5 x ${input.holidayHours}시간`;
        }
    }

    /**
     * 검증 상태 UI 업데이트
     * @param {Object} validation - 검증 결과
     * @param {number} hourlyWage - 통상임금 (옵션)
     */
    updateValidationUI(validation, hourlyWage) {
        const statusEl = this.elements.validationStatus;
        if (!statusEl) return;

        if (!validation.isValid) {
            statusEl.className = 'validation-status error';
            statusEl.innerHTML = `
                <i class="fas fa-exclamation-circle validation-icon"></i>
                <div class="validation-text">
                    <strong>검증 실패</strong>
                    <span>${validation.errors.map(e => e.message).join(' ')}</span>
                </div>
            `;
        } else if (validation.warnings.length > 0) {
            statusEl.className = 'validation-status warning';
            statusEl.innerHTML = `
                <i class="fas fa-exclamation-triangle validation-icon"></i>
                <div class="validation-text">
                    <strong>주의</strong>
                    <span>${validation.warnings.map(w => w.message).join(' ')}</span>
                </div>
            `;
        } else {
            statusEl.className = 'validation-status success';
            statusEl.innerHTML = `
                <i class="fas fa-check-circle validation-icon"></i>
                <div class="validation-text">
                    <strong>검증 통과</strong>
                    <span>통상임금이 최저임금 기준을 충족합니다.</span>
                </div>
            `;
        }
    }

    /**
     * 입력 필드 포맷팅
     * @param {HTMLInputElement} input - 입력 요소
     */
    formatInput(input) {
        const value = parseNumber(input.value);
        if (value > 0) {
            input.value = formatNumber(value);
        }
    }

    /**
     * 모달 열기
     * @param {Object} initialValues - 초기값 (옵션)
     */
    open(initialValues = {}) {
        if (!this.isInitialized) {
            this.init();
        }

        // 초기값 설정
        if (initialValues.annualSalary && this.elements.annualSalary) {
            this.elements.annualSalary.value = formatNumber(initialValues.annualSalary);
        }
        if (initialValues.mealAllowance && this.elements.mealAllowance) {
            this.elements.mealAllowance.value = formatNumber(initialValues.mealAllowance);
        }
        if (initialValues.overtimeHours !== undefined && this.elements.overtimeHours) {
            this.elements.overtimeHours.value = initialValues.overtimeHours;
        }
        if (initialValues.nightHours !== undefined && this.elements.nightHours) {
            this.elements.nightHours.value = initialValues.nightHours;
        }
        if (initialValues.holidayDays !== undefined && this.elements.holidayDays) {
            this.elements.holidayDays.value = initialValues.holidayDays;
        }

        // 모달 표시
        if (this.elements.modal) {
            this.elements.modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }

        // 초기 계산 실행
        this.calculate();
    }

    /**
     * 모달 닫기
     */
    close() {
        if (this.elements.modal) {
            this.elements.modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    /**
     * 모달 열림 상태 확인
     * @returns {boolean}
     */
    isOpen() {
        return this.elements.modal?.style.display === 'flex';
    }

    /**
     * 계산 결과 적용
     */
    apply() {
        const result = this.calculate();

        if (!result.validation.isValid) {
            showToast('검증 오류가 있습니다. 수정 후 다시 시도해주세요.', 'error');
            return;
        }

        // 콜백 실행
        if (this.onApply) {
            this.onApply(result);
        }

        showToast('계산 결과가 적용되었습니다.', 'success');
        this.close();
    }

    /**
     * 계산 결과 가져오기
     * @returns {Object} 현재 계산 결과
     */
    getResult() {
        return this.calculate();
    }
}

export default SalaryCalculatorModal;
