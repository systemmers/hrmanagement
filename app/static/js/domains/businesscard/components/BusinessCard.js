/**
 * BusinessCard Component
 * 명함 카드 컴포넌트 (플립 애니메이션, 이벤트 처리)
 *
 * Usage:
 *   import { BusinessCard } from './components/BusinessCard.js';
 *
 *   const bc = new BusinessCard();
 *   bc.initAll();
 */

import { qrGenerator } from './QRGenerator.js';

export class BusinessCard {
    /**
     * BusinessCard 컴포넌트 초기화
     * @param {Object} options - 설정 옵션
     */
    constructor(options = {}) {
        this.options = {
            wrapperSelector: options.wrapperSelector || '.bc-wrapper',
            cardSelector: options.cardSelector || '.bc-card',
            actionSelector: options.actionSelector || '.bc-actions',
            flipOnHover: options.flipOnHover !== false,
            flipOnClick: options.flipOnClick || false,
            enableKeyboard: options.enableKeyboard !== false
        };

        this.cards = new Map();
    }

    /**
     * 모든 명함 카드 초기화
     */
    initAll() {
        const wrappers = document.querySelectorAll(this.options.wrapperSelector);

        wrappers.forEach((wrapper, index) => {
            this.initCard(wrapper, index);
        });

        // QR 코드 초기화
        qrGenerator.initAll();

        // 키보드 이벤트 설정
        if (this.options.enableKeyboard) {
            this._setupKeyboardNavigation();
        }
    }

    /**
     * 단일 명함 카드 초기화
     * @param {HTMLElement} wrapper - 카드 래퍼 요소
     * @param {number} index - 카드 인덱스
     */
    initCard(wrapper, index = 0) {
        const card = wrapper.querySelector(this.options.cardSelector);
        if (!card) return;

        const cardId = `bc-card-${index}`;
        wrapper.setAttribute('data-card-id', cardId);

        // 카드 정보 저장
        this.cards.set(cardId, {
            wrapper,
            card,
            isFlipped: false,
            employeeId: wrapper.dataset.employeeId,
            href: wrapper.dataset.href
        });

        // 이벤트 바인딩
        this._bindCardEvents(wrapper, card, cardId);

        // QR 코드 초기화
        qrGenerator.initWithin(wrapper);
    }

    /**
     * 카드 이벤트 바인딩
     * @private
     */
    _bindCardEvents(wrapper, card, cardId) {
        // 클릭 이벤트 (상세 페이지 이동 또는 플립)
        wrapper.addEventListener('click', (e) => {
            // 액션 버튼 클릭 시 이벤트 전파 방지
            if (e.target.closest(this.options.actionSelector)) {
                return;
            }

            const cardData = this.cards.get(cardId);

            if (this.options.flipOnClick) {
                this.toggleFlip(cardId);
            } else if (cardData?.href) {
                window.location.href = cardData.href;
            }
        });

        // 터치 디바이스에서 플립 토글
        wrapper.addEventListener('touchstart', (e) => {
            if (e.target.closest(this.options.actionSelector)) {
                return;
            }

            // 터치 시 플립 토글
            if (!this.options.flipOnHover) {
                this.toggleFlip(cardId);
            }
        }, { passive: true });
    }

    /**
     * 키보드 네비게이션 설정
     * @private
     */
    _setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            const focusedWrapper = document.activeElement?.closest(this.options.wrapperSelector);

            if (!focusedWrapper) return;

            const cardId = focusedWrapper.getAttribute('data-card-id');

            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    const cardData = this.cards.get(cardId);
                    if (cardData?.href) {
                        window.location.href = cardData.href;
                    } else {
                        this.toggleFlip(cardId);
                    }
                    break;

                case 'Escape':
                    this.unflip(cardId);
                    break;
            }
        });
    }

    /**
     * 카드 플립 토글
     * @param {string} cardId - 카드 ID
     */
    toggleFlip(cardId) {
        const cardData = this.cards.get(cardId);
        if (!cardData) return;

        cardData.isFlipped = !cardData.isFlipped;
        cardData.card.classList.toggle('is-flipped', cardData.isFlipped);
    }

    /**
     * 카드 플립
     * @param {string} cardId - 카드 ID
     */
    flip(cardId) {
        const cardData = this.cards.get(cardId);
        if (!cardData || cardData.isFlipped) return;

        cardData.isFlipped = true;
        cardData.card.classList.add('is-flipped');
    }

    /**
     * 카드 플립 해제
     * @param {string} cardId - 카드 ID
     */
    unflip(cardId) {
        const cardData = this.cards.get(cardId);
        if (!cardData || !cardData.isFlipped) return;

        cardData.isFlipped = false;
        cardData.card.classList.remove('is-flipped');
    }

    /**
     * 모든 카드 플립 해제
     */
    unflipAll() {
        this.cards.forEach((cardData, cardId) => {
            this.unflip(cardId);
        });
    }

    /**
     * 호버 플립 비활성화 (터치 디바이스용)
     * @param {string} cardId - 카드 ID
     */
    disableHoverFlip(cardId) {
        const cardData = this.cards.get(cardId);
        if (!cardData) return;

        cardData.card.classList.add('no-flip');
    }

    /**
     * 호버 플립 활성화
     * @param {string} cardId - 카드 ID
     */
    enableHoverFlip(cardId) {
        const cardData = this.cards.get(cardId);
        if (!cardData) return;

        cardData.card.classList.remove('no-flip');
    }

    /**
     * 카드 정보 조회
     * @param {string} cardId - 카드 ID
     * @returns {Object|undefined}
     */
    getCard(cardId) {
        return this.cards.get(cardId);
    }

    /**
     * 모든 카드 정리
     */
    destroy() {
        this.cards.clear();
    }
}

// 기본 인스턴스 export
export const businessCard = new BusinessCard();
