/**
 * 급여 계산 상수 및 기본 데이터
 * Phase 7: 프론트엔드 리팩토링 - salary-calculator.js 분할
 *
 * 2025년 기준 적용
 */

/**
 * 급여 계산 상수
 */
export const SALARY_CONSTANTS = {
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
export const VALIDATION_ERROR_TYPES = {
    MINIMUM_WAGE_VIOLATION: 'MINIMUM_WAGE_VIOLATION',
    OVERTIME_LIMIT_EXCEEDED: 'OVERTIME_LIMIT_EXCEEDED',
    OVERTIME_NEAR_LIMIT: 'OVERTIME_NEAR_LIMIT'
};

/**
 * 기본 수당 템플릿
 */
export const DEFAULT_ALLOWANCES = [
    { id: 'meal', name: '식대', amount: 200000, includedInOrdinaryWage: false, taxable: false, removable: false },
    { id: 'position', name: '직책수당', amount: 0, includedInOrdinaryWage: true, taxable: true, removable: true },
    { id: 'technical', name: '기술수당', amount: 0, includedInOrdinaryWage: true, taxable: true, removable: true }
];
