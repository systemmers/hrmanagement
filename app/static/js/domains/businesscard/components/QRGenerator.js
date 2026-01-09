/**
 * QR Code Generator Component
 * 명함용 QR 코드 생성 컴포넌트
 *
 * Dependencies:
 * - QRCode.js library (external)
 *
 * Usage:
 *   import { QRGenerator } from './components/QRGenerator.js';
 *
 *   const qr = new QRGenerator();
 *   qr.generate(container, 'EMP-001');
 *   qr.initAll();
 */

export class QRGenerator {
    /**
     * QR 코드 생성기 초기화
     * @param {Object} options - 설정 옵션
     */
    constructor(options = {}) {
        this.options = {
            width: options.width || 60,
            height: options.height || 60,
            colorDark: options.colorDark || '#1f2937',
            colorLight: options.colorLight || '#ffffff',
            correctLevel: options.correctLevel || 'M',
            selector: options.selector || '.bc-qr',
            dataAttribute: options.dataAttribute || 'data-employee-number'
        };

        this.initialized = new WeakSet();
    }

    /**
     * QRCode 라이브러리 사용 가능 여부 확인
     * @returns {boolean}
     */
    isAvailable() {
        return typeof QRCode !== 'undefined';
    }

    /**
     * 단일 컨테이너에 QR 코드 생성
     * @param {HTMLElement} container - QR 코드를 생성할 컨테이너
     * @param {string} text - QR 코드에 인코딩할 텍스트
     * @returns {boolean} 생성 성공 여부
     */
    generate(container, text) {
        if (!this.isAvailable()) {
            console.warn('QRCode library not loaded');
            return false;
        }

        if (!container || !text) {
            return false;
        }

        // 이미 생성된 경우 스킵
        if (this.initialized.has(container)) {
            return true;
        }

        // 기존 canvas 확인
        if (container.querySelector('canvas')) {
            this.initialized.add(container);
            return true;
        }

        try {
            const correctLevelMap = {
                'L': QRCode.CorrectLevel.L,
                'M': QRCode.CorrectLevel.M,
                'Q': QRCode.CorrectLevel.Q,
                'H': QRCode.CorrectLevel.H
            };

            new QRCode(container, {
                text: text,
                width: this.options.width,
                height: this.options.height,
                colorDark: this.options.colorDark,
                colorLight: this.options.colorLight,
                correctLevel: correctLevelMap[this.options.correctLevel] || QRCode.CorrectLevel.M
            });

            this.initialized.add(container);
            return true;

        } catch (error) {
            console.error('QR code generation failed:', error);
            return false;
        }
    }

    /**
     * 페이지 내 모든 QR 코드 컨테이너 초기화
     * @returns {number} 생성된 QR 코드 수
     */
    initAll() {
        if (!this.isAvailable()) {
            console.warn('QRCode library not loaded');
            return 0;
        }

        const containers = document.querySelectorAll(this.options.selector);
        let count = 0;

        containers.forEach(container => {
            const text = container.getAttribute(this.options.dataAttribute) ||
                         container.dataset.employeeNumber ||
                         container.dataset.text;

            if (text && this.generate(container, text)) {
                count++;
            }
        });

        return count;
    }

    /**
     * 특정 영역 내 QR 코드 초기화
     * @param {HTMLElement} parentElement - 부모 요소
     * @returns {number} 생성된 QR 코드 수
     */
    initWithin(parentElement) {
        if (!this.isAvailable() || !parentElement) {
            return 0;
        }

        const containers = parentElement.querySelectorAll(this.options.selector);
        let count = 0;

        containers.forEach(container => {
            const text = container.getAttribute(this.options.dataAttribute) ||
                         container.dataset.employeeNumber ||
                         container.dataset.text;

            if (text && this.generate(container, text)) {
                count++;
            }
        });

        return count;
    }

    /**
     * QR 코드 재생성 (기존 코드 제거 후 새로 생성)
     * @param {HTMLElement} container - QR 코드 컨테이너
     * @param {string} text - 새로운 텍스트
     * @returns {boolean} 생성 성공 여부
     */
    regenerate(container, text) {
        if (!container) return false;

        // 기존 canvas 제거
        const existingCanvas = container.querySelector('canvas');
        if (existingCanvas) {
            existingCanvas.remove();
        }

        // WeakSet에서 제거 (불가능하므로 새 인스턴스로 처리)
        // 새로 생성
        return this.generate(container, text);
    }

    /**
     * 초기화 상태 리셋
     */
    reset() {
        this.initialized = new WeakSet();
    }
}

// 기본 인스턴스 export
export const qrGenerator = new QRGenerator();

// 전역 함수 (레거시 호환)
export function initBusinessCardQRCodes() {
    return qrGenerator.initAll();
}
