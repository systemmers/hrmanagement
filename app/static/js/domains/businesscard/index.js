/**
 * BusinessCard Domain Module
 * 명함 도메인 외부 인터페이스
 *
 * Usage:
 *   import {
 *       BusinessCard,
 *       businessCard,
 *       QRGenerator,
 *       qrGenerator,
 *       businesscardApi,
 *       initBusinessCards
 *   } from './domains/businesscard/index.js';
 *
 *   // 초기화
 *   initBusinessCards();
 *
 *   // 또는 개별 사용
 *   businessCard.initAll();
 *   qrGenerator.initAll();
 */

// Components - 로컬 import 후 re-export
import { BusinessCard, businessCard } from './components/BusinessCard.js';
import { QRGenerator, qrGenerator, initBusinessCardQRCodes } from './components/QRGenerator.js';

export { BusinessCard, businessCard };
export { QRGenerator, qrGenerator, initBusinessCardQRCodes };

// Services
export { businesscardApi, legacyBusinesscardApi } from './services/businesscard-api.js';

/**
 * 명함 뷰 초기화
 * 페이지 로드 시 호출
 */
export function initBusinessCards() {
    // BusinessCard 컴포넌트에서 QR도 자동 초기화됨
    businessCard.initAll();
}

/**
 * 명함 뷰 표시 시 초기화
 * 뷰 토글로 명함 뷰가 표시될 때 호출
 * @param {HTMLElement} container - 명함 뷰 컨테이너 (선택적)
 */
export function initBusinessCardView(container = null) {
    if (container) {
        // 특정 컨테이너 내 초기화
        const wrappers = container.querySelectorAll('.bc-wrapper');
        wrappers.forEach((wrapper, index) => {
            businessCard.initCard(wrapper, index);
        });
        qrGenerator.initWithin(container);
    } else {
        // 전체 초기화
        businessCard.initAll();
    }
}

/**
 * QR 코드만 초기화 (레거시 호환)
 */
export function initQRCodes() {
    return qrGenerator.initAll();
}
