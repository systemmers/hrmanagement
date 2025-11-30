/**
 * 포괄임금제 급여 계산기 컴포넌트
 *
 * 기능:
 * - 연봉 기반 기본급 역산
 * - 연장/야간/휴일 근로수당 자동 계산
 * - 최저임금 및 연장근로 한도 검증
 * - 모달 UI 연동
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
 * SalaryCalculator 클래스
 * 포괄임금제 급여 구성 계산 담당
 */
export class SalaryCalculator {
    constructor(options = {}) {
        this.constants = { ...SALARY_CONSTANTS, ...options.constants };
        this.onCalculate = options.onCalculate || null;
        this.onValidationChange = options.onValidationChange || null;
    }

    /**
     * 급여 구성 계산 (기본급 역산 방식)
     * @param {Object} params - 계산 파라미터
     * @param {number} params.annualSalary - 연봉
     * @param {number} params.mealAllowance - 식대 (비과세)
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

        // 2. 과세 대상 급여 (식대 제외)
        const taxableSalary = monthlySalary - mealAllowance;

        // 3. 휴일근로시간 변환
        const holidayHours = holidayDays * this.constants.HOLIDAY_HOURS_PER_DAY;

        // 4. 수당 계수 계산
        const overtimeCoeff = (this.constants.OVERTIME_RATE * overtimeHours) / this.constants.MONTHLY_WORK_HOURS;
        const nightCoeff = (this.constants.NIGHT_RATE * nightHours) / this.constants.MONTHLY_WORK_HOURS;
        const holidayCoeff = (this.constants.HOLIDAY_RATE * holidayHours) / this.constants.MONTHLY_WORK_HOURS;
        const totalCoeff = 1 + overtimeCoeff + nightCoeff + holidayCoeff;

        // 5. 기본급 역산
        const baseSalary = Math.floor(taxableSalary / totalCoeff);

        // 6. 통상임금 (시간당)
        const hourlyWage = Math.floor(baseSalary / this.constants.MONTHLY_WORK_HOURS);

        // 7. 각 수당 계산
        const overtimeAllowance = Math.floor(hourlyWage * this.constants.OVERTIME_RATE * overtimeHours);
        const nightAllowance = Math.floor(hourlyWage * this.constants.NIGHT_RATE * nightHours);
        const holidayAllowance = Math.floor(hourlyWage * this.constants.HOLIDAY_RATE * holidayHours);
        const totalAllowances = overtimeAllowance + nightAllowance + holidayAllowance;

        // 8. 검증
        const validation = this.validate({ hourlyWage, overtimeHours });

        const result = {
            // 입력값
            input: {
                annualSalary,
                mealAllowance,
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
            // 수당 상세
            allowances: {
                meal: mealAllowance,
                overtime: overtimeAllowance,
                night: nightAllowance,
                holiday: holidayAllowance,
                total: totalAllowances
            },
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
 * 급여 계산기 모달 UI 관리
 */
export class SalaryCalculatorModal {
    constructor(options = {}) {
        this.modalId = options.modalId || 'salaryCalculatorModal';
        this.calculator = new SalaryCalculator({
            onCalculate: (result) => this.updateUI(result),
            onValidationChange: (validation) => this.updateValidationUI(validation)
        });

        this.onApply = options.onApply || null;
        this.debounceTimer = null;
        this.debounceDelay = options.debounceDelay || 300;

        this.elements = {};
        this.isInitialized = false;
    }

    /**
     * 모달 초기화
     */
    init() {
        if (this.isInitialized) return;

        this.cacheElements();
        this.bindEvents();
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
            closeBtn: modal.querySelector('#calcCloseBtn')
        };
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 숫자 입력 필드 (콤마 포맷팅)
        ['annualSalary', 'mealAllowance'].forEach(key => {
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
