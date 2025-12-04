/**
 * 급여 계산기 모듈 인덱스
 * Phase 7: 프론트엔드 리팩토링 - salary-calculator.js 분할
 *
 * 모든 급여 관련 컴포넌트를 하나의 진입점에서 내보냅니다.
 */

// 상수
export {
    SALARY_CONSTANTS,
    VALIDATION_ERROR_TYPES,
    DEFAULT_ALLOWANCES
} from './constants.js';

// 수당 관리자
export { AllowanceManager } from './allowance-manager.js';

// 급여 계산기
export { SalaryCalculator } from './calculator.js';

// 모달 UI
export { SalaryCalculatorModal } from './modal.js';

// 기본 내보내기
export { SalaryCalculator as default } from './calculator.js';
