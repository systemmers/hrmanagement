/**
 * Employee Domain - Public Interface
 *
 * 직원 도메인의 외부 인터페이스
 * 다른 도메인에서 employee 기능 사용 시 이 파일을 통해 import
 */

// Services
export { EmployeeService, searchEmployees } from './services/employee-service.js';

// Components
export { SalaryCalculator } from './components/salary/calculator.js';
export { SalaryModal } from './components/salary/modal.js';
export { BusinessCard } from './components/business-card.js';

// Page modules (if needed externally)
// export * from './pages/list.js';
// export * from './pages/form.js';
// export * from './pages/detail.js';
