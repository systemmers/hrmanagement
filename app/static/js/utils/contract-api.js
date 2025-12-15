/**
 * contract-api.js - 계약 API 유틸리티 (하위 호환성)
 *
 * DEPRECATED: services/contract-service.js를 직접 import하세요.
 * 이 파일은 하위 호환성을 위해 services/contract-service.js를 re-export합니다.
 */

// services/contract-service.js에서 re-export
export {
    approveContract,
    rejectContract,
    terminateContract,
    checkBusinessNumber
} from '../services/contract-service.js';
