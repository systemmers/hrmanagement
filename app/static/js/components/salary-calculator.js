/**
 * 포괄임금제 급여 계산기 컴포넌트
 * Phase 7: 프론트엔드 리팩토링 - 모듈 분할 후 re-export
 *
 * @deprecated 2025-03 이후 제거 예정
 * 이 파일은 하위 호환성을 위해 유지됩니다.
 * 새 코드에서는 './salary/index.js'에서 직접 import하세요.
 *
 * 마이그레이션:
 * - 변경 전: import { SalaryCalculator } from './salary-calculator.js';
 * - 변경 후: import { SalaryCalculator } from './salary/index.js';
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

console.warn('DEPRECATED: salary-calculator.js → salary/index.js (2025-03 이후 제거 예정)');

// 분할된 모듈에서 re-export
export {
    SALARY_CONSTANTS,
    VALIDATION_ERROR_TYPES,
    DEFAULT_ALLOWANCES,
    AllowanceManager,
    SalaryCalculator,
    SalaryCalculatorModal
} from './salary/index.js';

// 기존 코드 호환을 위한 기본 내보내기
export { SalaryCalculator as default } from './salary/index.js';
