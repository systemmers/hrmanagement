/**
 * SalaryCalculator 클래스
 * Phase 7: 프론트엔드 리팩토링 - salary-calculator.js 분할
 *
 * 포괄임금제 급여 구성 계산 담당
 */

import { SALARY_CONSTANTS, VALIDATION_ERROR_TYPES } from './constants.js';
import { formatNumber, parseNumber } from '../../../../shared/utils/formatting.js';

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
                message: `통상임금(${formatNumber(hourlyWage)}원/시간)이 최저임금(${formatNumber(this.constants.MINIMUM_WAGE)}원/시간)보다 낮습니다.`,
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
     * 숫자 포맷팅 (천단위 콤마) - 유틸리티 래퍼
     * @param {number} num - 숫자
     * @returns {string} 포맷팅된 문자열
     */
    formatNumber(num) {
        return formatNumber(num);
    }

    /**
     * 문자열에서 숫자 추출 - 유틸리티 래퍼
     * @param {string} str - 콤마 포함 문자열
     * @returns {number} 숫자
     */
    parseNumber(str) {
        return parseNumber(str);
    }

    /**
     * 상수값 조회
     * @returns {Object} 상수 객체
     */
    getConstants() {
        return { ...this.constants };
    }
}

export default SalaryCalculator;
