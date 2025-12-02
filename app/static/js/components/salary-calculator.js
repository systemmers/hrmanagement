/**
 * 포괄임금제 급여 계산기 컴포넌트
 *
 * 기능:
 * - 연봉 기반 기본급 역산
 * - 연장/야간/휴일 근로수당 자동 계산
 * - 최저임금 및 연장근로 한도 검증
 * - 모달 UI 연동
 * - 수당 관리 (통상임금 포함/미포함 구분)
 *
 * 2025년 기준 적용
 */

import { showToast } from './toast.js';

/**
 * 급여 계산 상수
 */
const SALARY_CONSTANTS = {
    // 2025년 기준
    MINIMUM_WAGE: 10030,           // 원/시간
    MONTHLY_WORK_HOURS: 209,       // 월 소정근로시간 (주 40시간 기준)
    MAX_OVERTIME_HOURS: 52,        // 월 최대 연장근로시간
    DEFAULT_MEAL_ALLOWANCE: 200000, // 비과세 식대 한도

    // 수당 배율
    OVERTIME_RATE: 1.5,            // 연장근로 가산율
    NIGHT_RATE: 0.5,               // 야간근로 가산율 (추가분만)
    HOLIDAY_RATE: 1.5,             // 휴일근로 가산율
    HOLIDAY_HOURS_PER_DAY: 8       // 휴일 1일 = 8시간
};

/**
 * 검증 오류 유형
 */
const VALIDATION_ERROR_TYPES = {
    MINIMUM_WAGE_VIOLATION: 'MINIMUM_WAGE_VIOLATION',
    OVERTIME_LIMIT_EXCEEDED: 'OVERTIME_LIMIT_EXCEEDED',
    OVERTIME_NEAR_LIMIT: 'OVERTIME_NEAR_LIMIT'
};

/**
 * 기본 수당 템플릿
 */
const DEFAULT_ALLOWANCES = [
    { id: 'meal', name: '식대', amount: 200000, includedInOrdinaryWage: false, taxable: false, removable: false },
    { id: 'position', name: '직책수당', amount: 0, includedInOrdinaryWage: true, taxable: true, removable: true },
    { id: 'technical', name: '기술수당', amount: 0, includedInOrdinaryWage: true, taxable: true, removable: true }
];

/**
 * AllowanceManager 클래스
 * 수당 목록 관리 (통상임금 포함/미포함 구분)
 */
export class AllowanceManager {
    constructor(initialAllowances = null) {
        this.allowances = initialAllowances
            ? initialAllowances.map(a => ({ ...a }))
            : DEFAULT_ALLOWANCES.map(a => ({ ...a }));
        this.idCounter = 100;
        this.onChange = null;
    }

    /**
     * 수당 추가
     * @param {Object} allowance - 수당 정보
     * @returns {Object} 추가된 수당
     */
    addAllowance(allowance) {
        const newAllowance = {
            id: `custom_${this.idCounter++}`,
            name: allowance.name,
            amount: allowance.amount || 0,
            includedInOrdinaryWage: allowance.includedInOrdinaryWage !== false,
            taxable: allowance.taxable !== false,
            removable: true
        };
        this.allowances.push(newAllowance);
        this._triggerChange();
        return newAllowance;
    }

    /**
     * 수당 삭제
     * @param {string} id - 수당 ID
     * @returns {boolean} 삭제 성공 여부
     */
    removeAllowance(id) {
        const index = this.allowances.findIndex(a => a.id === id);
        if (index === -1) return false;

        const allowance = this.allowances[index];
        if (!allowance.removable) return false;

        this.allowances.splice(index, 1);
        this._triggerChange();
        return true;
    }

    /**
     * 수당 업데이트
     * @param {string} id - 수당 ID
     * @param {Object} updates - 업데이트할 필드
     * @returns {Object|null} 업데이트된 수당
     */
    updateAllowance(id, updates) {
        const allowance = this.allowances.find(a => a.id === id);
        if (!allowance) return null;

        if (updates.amount !== undefined) allowance.amount = updates.amount;
        if (updates.includedInOrdinaryWage !== undefined) {
            allowance.includedInOrdinaryWage = updates.includedInOrdinaryWage;
        }
        if (updates.name !== undefined) allowance.name = updates.name;
        if (updates.taxable !== undefined) allowance.taxable = updates.taxable;

        this._triggerChange();
        return allowance;
    }

    /**
     * 통상임금 포함 수당 합계
     * @returns {number}
     */
    getOrdinaryWageIncludedSum() {
        return this.allowances
            .filter(a => a.includedInOrdinaryWage && a.amount > 0)
            .reduce((sum, a) => sum + a.amount, 0);
    }

    /**
     * 통상임금 미포함 수당 합계
     * @returns {number}
     */
    getOrdinaryWageExcludedSum() {
        return this.allowances
            .filter(a => !a.includedInOrdinaryWage && a.amount > 0)
            .reduce((sum, a) => sum + a.amount, 0);
    }

    /**
     * 전체 수당 합계
     * @returns {number}
     */
    getTotalSum() {
        return this.allowances
            .filter(a => a.amount > 0)
            .reduce((sum, a) => sum + a.amount, 0);
    }

    /**
     * 통상임금 포함 수당 목록
     * @returns {Array}
     */
    getOrdinaryWageIncludedAllowances() {
        return this.allowances.filter(a => a.includedInOrdinaryWage && a.amount > 0);
    }

    /**
     * 통상임금 미포함 수당 목록
     * @returns {Array}
     */
    getOrdinaryWageExcludedAllowances() {
        return this.allowances.filter(a => !a.includedInOrdinaryWage && a.amount > 0);
    }

    /**
     * 전체 수당 목록
     * @returns {Array}
     */
    getAllAllowances() {
        return [...this.allowances];
    }

    /**
     * 수당명 중복 체크
     * @param {string} name - 수당명
     * @param {string} excludeId - 제외할 ID (수정 시)
     * @returns {boolean}
     */
    isDuplicateName(name, excludeId = null) {
        return this.allowances.some(a =>
            a.name === name && a.id !== excludeId
        );
    }

    /**
     * 기본값으로 초기화
     */
    reset() {
        this.allowances = DEFAULT_ALLOWANCES.map(a => ({ ...a }));
        this._triggerChange();
    }

    /**
     * 변경 콜백 트리거
     */
    _triggerChange() {
        if (this.onChange) {
            this.onChange(this.allowances);
        }
    }

    /**
     * JSON 직렬화
     * @returns {Array}
     */
    toJSON() {
        return this.allowances.map(a => ({ ...a }));
    }

    /**
     * JSON에서 복원
     * @param {Array} data
     */
    fromJSON(data) {
        if (Array.isArray(data)) {
            this.allowances = data.map(a => ({ ...a }));
            this._triggerChange();
        }
    }
}

/**
 * SalaryCalculator 클래스
 * 포괄임금제 급여 구성 계산 담당
 */
export class SalaryCalculator {
    constructor(options = {}) {
        this.constants = { ...SALARY_CONSTANTS, ...options.constants };
        this.onCalculate = options.onCalculate || null;
        this.onValidationChange = options.onValidationChange || null;
        this.allowanceManager = options.allowanceManager || null;
    }

    /**
     * AllowanceManager 설정
     * @param {AllowanceManager} manager
     */
    setAllowanceManager(manager) {
        this.allowanceManager = manager;
    }

    /**
     * 급여 구성 계산 (기본급 역산 방식)
     * AllowanceManager가 있으면 수당을 통상임금 포함/미포함으로 구분하여 계산
     *
     * @param {Object} params - 계산 파라미터
     * @param {number} params.annualSalary - 연봉
     * @param {number} params.mealAllowance - 식대 (비과세) - AllowanceManager 미사용 시
     * @param {number} params.overtimeHours - 월 연장근로시간
     * @param {number} params.nightHours - 월 야간근로시간
     * @param {number} params.holidayDays - 월 휴일근로일수
     * @returns {Object} 계산 결과
     */
    calculate(params) {
        const {
            annualSalary = 0,
            mealAllowance = 0,
            overtimeHours = 0,
            nightHours = 0,
            holidayDays = 0
        } = params;

        // 1. 월 급여 계산
        const monthlySalary = Math.floor(annualSalary / 12);

        // 2. 수당 분류 (AllowanceManager 사용 여부에 따라 분기)
        let ordinaryIncluded = 0;  // 통상임금 포함 수당
        let ordinaryExcluded = 0;  // 통상임금 미포함 수당
        let customAllowances = [];

        if (this.allowanceManager) {
            ordinaryIncluded = this.allowanceManager.getOrdinaryWageIncludedSum();
            ordinaryExcluded = this.allowanceManager.getOrdinaryWageExcludedSum();
            customAllowances = this.allowanceManager.getAllAllowances();
        } else {
            // 기존 방식: mealAllowance만 통상임금 미포함으로 처리
            ordinaryExcluded = mealAllowance;
        }

        // 3. 휴일근로시간 변환
        const holidayHours = holidayDays * this.constants.HOLIDAY_HOURS_PER_DAY;

        // 4. 수당 계수 계산
        const overtimeCoeff = (this.constants.OVERTIME_RATE * overtimeHours) / this.constants.MONTHLY_WORK_HOURS;
        const nightCoeff = (this.constants.NIGHT_RATE * nightHours) / this.constants.MONTHLY_WORK_HOURS;
        const holidayCoeff = (this.constants.HOLIDAY_RATE * holidayHours) / this.constants.MONTHLY_WORK_HOURS;
        const totalCoeff = 1 + overtimeCoeff + nightCoeff + holidayCoeff;

        // 5. 기본급 역산 (수정된 알고리즘: 통상임금 포함 수당 고려)
        // 월급여 - 통상임금 미포함 수당 = 과세 대상 급여
        // 과세 대상 급여 = (기본급 + 통상임금 포함 수당) * totalCoeff
        // 기본급 = (과세 대상 급여 / totalCoeff) - 통상임금 포함 수당
        const taxableSalary = monthlySalary - ordinaryExcluded;
        const baseSalary = Math.floor(taxableSalary / totalCoeff) - ordinaryIncluded;

        // 6. 통상임금 (시간당) = (기본급 + 통상임금 포함 수당) / 209시간
        const ordinaryWageBase = baseSalary + ordinaryIncluded;
        const hourlyWage = Math.floor(ordinaryWageBase / this.constants.MONTHLY_WORK_HOURS);

        // 7. 각 수당 계산
        const overtimeAllowance = Math.floor(hourlyWage * this.constants.OVERTIME_RATE * overtimeHours);
        const nightAllowance = Math.floor(hourlyWage * this.constants.NIGHT_RATE * nightHours);
        const holidayAllowance = Math.floor(hourlyWage * this.constants.HOLIDAY_RATE * holidayHours);
        const statutoryAllowances = overtimeAllowance + nightAllowance + holidayAllowance;

        // 8. 검증
        const validation = this.validate({ hourlyWage, overtimeHours });

        const result = {
            // 입력값
            input: {
                annualSalary,
                mealAllowance: this.allowanceManager ? ordinaryExcluded : mealAllowance,
                overtimeHours,
                nightHours,
                holidayDays,
                holidayHours
            },
            // 계산 결과
            monthlySalary,
            taxableSalary,
            baseSalary,
            hourlyWage,
            ordinaryWageBase,
            // 수당 상세
            allowances: {
                meal: this.allowanceManager ? ordinaryExcluded : mealAllowance,
                overtime: overtimeAllowance,
                night: nightAllowance,
                holiday: holidayAllowance,
                statutory: statutoryAllowances,
                ordinaryIncluded,
                ordinaryExcluded,
                total: ordinaryIncluded + ordinaryExcluded + statutoryAllowances
            },
            // 커스텀 수당 목록
            customAllowances,
            // 계수 정보 (투명성)
            coefficients: {
                overtime: overtimeCoeff,
                night: nightCoeff,
                holiday: holidayCoeff,
                total: totalCoeff
            },
            // 검증 결과
            validation,
            // 비교 정보
            comparison: {
                minimumWagePercent: ((hourlyWage / this.constants.MINIMUM_WAGE) * 100).toFixed(1),
                overtimeUtilization: ((overtimeHours / this.constants.MAX_OVERTIME_HOURS) * 100).toFixed(1)
            }
        };

        // 콜백 실행
        if (this.onCalculate) {
            this.onCalculate(result);
        }

        return result;
    }

    /**
     * 법적 요건 검증
     * @param {Object} params
     * @param {number} params.hourlyWage - 통상임금
     * @param {number} params.overtimeHours - 연장근로시간
     * @returns {Object} 검증 결과
     */
    validate(params) {
        const { hourlyWage, overtimeHours } = params;
        const result = {
            isValid: true,
            errors: [],
            warnings: []
        };

        // 최저임금 검증
        if (hourlyWage < this.constants.MINIMUM_WAGE) {
            result.isValid = false;
            result.errors.push({
                type: VALIDATION_ERROR_TYPES.MINIMUM_WAGE_VIOLATION,
                message: `통상임금(${this.formatNumber(hourlyWage)}원/시간)이 최저임금(${this.formatNumber(this.constants.MINIMUM_WAGE)}원/시간)보다 낮습니다.`,
                current: hourlyWage,
                required: this.constants.MINIMUM_WAGE,
                diff: this.constants.MINIMUM_WAGE - hourlyWage
            });
        }

        // 연장근로시간 한도 검증
        if (overtimeHours > this.constants.MAX_OVERTIME_HOURS) {
            result.isValid = false;
            result.errors.push({
                type: VALIDATION_ERROR_TYPES.OVERTIME_LIMIT_EXCEEDED,
                message: `월 연장근로시간(${overtimeHours}시간)이 법정 한도(${this.constants.MAX_OVERTIME_HOURS}시간)를 초과합니다.`,
                current: overtimeHours,
                limit: this.constants.MAX_OVERTIME_HOURS,
                excess: overtimeHours - this.constants.MAX_OVERTIME_HOURS
            });
        }

        // 경고: 연장근로시간이 한도에 근접 (80% 이상)
        const overtimeThreshold = this.constants.MAX_OVERTIME_HOURS * 0.8;
        if (overtimeHours > overtimeThreshold && overtimeHours <= this.constants.MAX_OVERTIME_HOURS) {
            result.warnings.push({
                type: VALIDATION_ERROR_TYPES.OVERTIME_NEAR_LIMIT,
                message: `월 연장근로시간이 법정 한도의 ${((overtimeHours / this.constants.MAX_OVERTIME_HOURS) * 100).toFixed(0)}%입니다.`,
                current: overtimeHours,
                limit: this.constants.MAX_OVERTIME_HOURS
            });
        }

        // 콜백 실행
        if (this.onValidationChange) {
            this.onValidationChange(result);
        }

        return result;
    }

    /**
     * 역계산: 원하는 기본급에서 연봉 추정
     * @param {Object} params
     * @param {number} params.targetBaseSalary - 목표 기본급
     * @param {number} params.mealAllowance - 식대
     * @param {number} params.overtimeHours - 연장근로시간
     * @param {number} params.nightHours - 야간근로시간
     * @param {number} params.holidayDays - 휴일근로일수
     * @returns {number} 예상 연봉
     */
    estimateAnnualSalary(params) {
        const {
            targetBaseSalary,
            mealAllowance = 0,
            overtimeHours = 0,
            nightHours = 0,
            holidayDays = 0
        } = params;

        const holidayHours = holidayDays * this.constants.HOLIDAY_HOURS_PER_DAY;
        const hourlyWage = Math.floor(targetBaseSalary / this.constants.MONTHLY_WORK_HOURS);

        const overtimeAllowance = Math.floor(hourlyWage * this.constants.OVERTIME_RATE * overtimeHours);
        const nightAllowance = Math.floor(hourlyWage * this.constants.NIGHT_RATE * nightHours);
        const holidayAllowance = Math.floor(hourlyWage * this.constants.HOLIDAY_RATE * holidayHours);

        const monthlySalary = targetBaseSalary + mealAllowance + overtimeAllowance + nightAllowance + holidayAllowance;
        const annualSalary = monthlySalary * 12;

        return annualSalary;
    }

    /**
     * 최저 연봉 계산 (최저임금 기준)
     * @param {Object} params - 근로시간 파라미터
     * @returns {number} 최저 연봉
     */
    calculateMinimumAnnualSalary(params = {}) {
        const {
            mealAllowance = this.constants.DEFAULT_MEAL_ALLOWANCE,
            overtimeHours = 0,
            nightHours = 0,
            holidayDays = 0
        } = params;

        const minimumBaseSalary = this.constants.MINIMUM_WAGE * this.constants.MONTHLY_WORK_HOURS;

        return this.estimateAnnualSalary({
            targetBaseSalary: minimumBaseSalary,
            mealAllowance,
            overtimeHours,
            nightHours,
            holidayDays
        });
    }

    /**
     * 숫자 포맷팅 (천단위 콤마)
     * @param {number} num - 숫자
     * @returns {string} 포맷팅된 문자열
     */
    formatNumber(num) {
        if (num === null || num === undefined || isNaN(num)) return '0';
        return Math.floor(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * 문자열에서 숫자 추출
     * @param {string} str - 콤마 포함 문자열
     * @returns {number} 숫자
     */
    parseNumber(str) {
        if (typeof str === 'number') return str;
        return parseInt(String(str).replace(/[^0-9]/g, ''), 10) || 0;
    }

    /**
     * 상수값 조회
     * @returns {Object} 상수 객체
     */
    getConstants() {
        return { ...this.constants };
    }
}

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
        // 숫자 입력 필드 (콤마 포맷팅) - mealAllowance는 AllowanceManager가 관리
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
        const fmt = (n) => this.calculator.formatNumber(n);

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
                           value="${fmt(allowance.amount)}"
                           data-allowance-id="${allowance.id}"
                           ${!allowance.removable && allowance.id === 'meal' ? '' : ''}>
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
                const amount = this.calculator.parseNumber(e.target.value);
                this.allowanceManager.updateAllowance(id, { amount });
                e.target.value = this.calculator.formatNumber(amount);
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
        const amount = this.calculator.parseNumber(formContainer.querySelector('.allowance-add-amount').value);
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
        const fmt = (n) => this.calculator.formatNumber(n);

        if (this.elements.ordinaryIncludedSum) {
            this.elements.ordinaryIncludedSum.textContent =
                fmt(this.allowanceManager.getOrdinaryWageIncludedSum()) + '원';
        }
        if (this.elements.ordinaryExcludedSum) {
            this.elements.ordinaryExcludedSum.textContent =
                fmt(this.allowanceManager.getOrdinaryWageExcludedSum()) + '원';
        }
        if (this.elements.allowanceTotalSum) {
            this.elements.allowanceTotalSum.textContent =
                fmt(this.allowanceManager.getTotalSum()) + '원';
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
            annualSalary: this.calculator.parseNumber(this.elements.annualSalary?.value || 0),
            mealAllowance: this.calculator.parseNumber(this.elements.mealAllowance?.value || 0),
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
        const fmt = (n) => this.calculator.formatNumber(n);

        // 결과값 업데이트
        if (this.elements.hourlyWage) {
            this.elements.hourlyWage.textContent = fmt(result.hourlyWage) + '원';
        }
        if (this.elements.baseSalary) {
            this.elements.baseSalary.textContent = fmt(result.baseSalary) + '원';
        }
        if (this.elements.mealResult) {
            this.elements.mealResult.textContent = fmt(result.allowances.meal) + '원';
        }
        if (this.elements.overtimeAllowance) {
            this.elements.overtimeAllowance.textContent = fmt(result.allowances.overtime) + '원';
        }
        if (this.elements.nightAllowance) {
            this.elements.nightAllowance.textContent = fmt(result.allowances.night) + '원';
        }
        if (this.elements.holidayAllowance) {
            this.elements.holidayAllowance.textContent = fmt(result.allowances.holiday) + '원';
        }
        if (this.elements.totalSalary) {
            this.elements.totalSalary.textContent = fmt(result.monthlySalary) + '원';
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
                `최저임금(${fmt(this.calculator.constants.MINIMUM_WAGE)}원) 대비 <strong>${result.comparison.minimumWagePercent}%</strong>`;
        }

        // 검증 상태 업데이트
        this.updateValidationUI(result.validation, result.hourlyWage);
    }

    /**
     * 수당 결과 UI 업데이트
     * @param {Object} result - 계산 결과
     */
    updateAllowanceResultUI(result) {
        const fmt = (n) => this.calculator.formatNumber(n);

        // 통상임금 포함 수당 결과
        if (this.elements.ordinaryIncludedResult) {
            this.elements.ordinaryIncludedResult.textContent =
                fmt(result.allowances.ordinaryIncluded) + '원';
        }

        // 통상임금 미포함 수당 결과
        if (this.elements.ordinaryExcludedResult) {
            this.elements.ordinaryExcludedResult.textContent =
                fmt(result.allowances.ordinaryExcluded) + '원';
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
        const value = this.calculator.parseNumber(input.value);
        if (value > 0) {
            input.value = this.calculator.formatNumber(value);
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
            this.elements.annualSalary.value = this.calculator.formatNumber(initialValues.annualSalary);
        }
        if (initialValues.mealAllowance && this.elements.mealAllowance) {
            this.elements.mealAllowance.value = this.calculator.formatNumber(initialValues.mealAllowance);
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

/**
 * 기본 내보내기
 */
export default SalaryCalculator;
