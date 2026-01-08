/**
 * 이벤트 처리 유틸리티
 * Phase 7: 프론트엔드 리팩토링
 *
 * 이벤트 위임, 디바운스, 스로틀 등의 이벤트 관련 헬퍼를 제공합니다.
 */

/**
 * 이벤트 위임 관리자
 * 컨테이너에 이벤트를 등록하고 자식 요소에 위임합니다.
 */
export class EventDelegator {
    /**
     * @param {Element|string} container - 컨테이너 요소 또는 선택자
     */
    constructor(container) {
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;
        this.handlers = new Map();
    }

    /**
     * 이벤트 위임 등록
     * @param {string} eventType - 이벤트 타입 (click, change 등)
     * @param {string} selector - 대상 요소 선택자
     * @param {Function} handler - 이벤트 핸들러
     * @returns {EventDelegator} 체이닝을 위한 this
     */
    on(eventType, selector, handler) {
        if (!this.container) return this;

        const key = `${eventType}:${selector}`;

        const delegatedHandler = (event) => {
            const target = event.target.closest(selector);
            if (target && this.container.contains(target)) {
                handler.call(target, event, target);
            }
        };

        this.handlers.set(key, delegatedHandler);
        this.container.addEventListener(eventType, delegatedHandler);

        return this;
    }

    /**
     * 이벤트 위임 해제
     * @param {string} eventType - 이벤트 타입
     * @param {string} selector - 대상 요소 선택자
     * @returns {EventDelegator} 체이닝을 위한 this
     */
    off(eventType, selector) {
        if (!this.container) return this;

        const key = `${eventType}:${selector}`;
        const handler = this.handlers.get(key);

        if (handler) {
            this.container.removeEventListener(eventType, handler);
            this.handlers.delete(key);
        }

        return this;
    }

    /**
     * 모든 이벤트 해제
     */
    destroy() {
        this.handlers.forEach((handler, key) => {
            const [eventType] = key.split(':');
            this.container.removeEventListener(eventType, handler);
        });
        this.handlers.clear();
    }
}

/**
 * 디바운스 함수
 * 연속 호출 시 마지막 호출만 실행
 * @param {Function} func - 실행할 함수
 * @param {number} wait - 대기 시간 (ms)
 * @param {boolean} immediate - 즉시 실행 여부
 * @returns {Function} 디바운스된 함수
 */
export function debounce(func, wait, immediate = false) {
    let timeout;

    return function executedFunction(...args) {
        const context = this;

        const later = () => {
            timeout = null;
            if (!immediate) {
                func.apply(context, args);
            }
        };

        const callNow = immediate && !timeout;

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);

        if (callNow) {
            func.apply(context, args);
        }
    };
}

/**
 * 스로틀 함수
 * 일정 시간마다 최대 한 번만 실행
 * @param {Function} func - 실행할 함수
 * @param {number} limit - 제한 시간 (ms)
 * @returns {Function} 스로틀된 함수
 */
export function throttle(func, limit) {
    let inThrottle;
    let lastFunc;
    let lastRan;

    return function executedFunction(...args) {
        const context = this;

        if (!inThrottle) {
            func.apply(context, args);
            lastRan = Date.now();
            inThrottle = true;
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(() => {
                if (Date.now() - lastRan >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
}

/**
 * 한 번만 실행되는 함수
 * @param {Function} func - 실행할 함수
 * @returns {Function} 래핑된 함수
 */
export function once(func) {
    let called = false;
    let result;

    return function executedFunction(...args) {
        if (!called) {
            called = true;
            result = func.apply(this, args);
        }
        return result;
    };
}

/**
 * DOM Ready 이벤트
 * @param {Function} callback - 실행할 콜백
 */
export function onReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

/**
 * 커스텀 이벤트 발생
 * @param {Element|string} element - 요소 또는 선택자
 * @param {string} eventName - 이벤트 이름
 * @param {Object} detail - 이벤트 데이터
 */
export function emit(element, eventName, detail = {}) {
    const el = typeof element === 'string'
        ? document.querySelector(element)
        : element;

    if (!el) return;

    const event = new CustomEvent(eventName, {
        bubbles: true,
        cancelable: true,
        detail
    });

    el.dispatchEvent(event);
}

/**
 * 키보드 단축키 핸들러
 * @param {Object} shortcuts - 단축키 맵 ({ 'ctrl+s': handler })
 * @returns {Function} 이벤트 핸들러
 */
export function createKeyboardHandler(shortcuts) {
    return function(event) {
        const keys = [];

        if (event.ctrlKey || event.metaKey) keys.push('ctrl');
        if (event.altKey) keys.push('alt');
        if (event.shiftKey) keys.push('shift');

        const key = event.key.toLowerCase();
        if (!['control', 'alt', 'shift', 'meta'].includes(key)) {
            keys.push(key);
        }

        const combo = keys.join('+');
        const handler = shortcuts[combo];

        if (handler) {
            event.preventDefault();
            handler(event);
        }
    };
}

/**
 * 요소 외부 클릭 감지
 * @param {Element|string} element - 요소 또는 선택자
 * @param {Function} callback - 외부 클릭 시 콜백
 * @returns {Function} 이벤트 제거 함수
 */
export function onClickOutside(element, callback) {
    const el = typeof element === 'string'
        ? document.querySelector(element)
        : element;

    if (!el) return () => {};

    const handler = (event) => {
        if (!el.contains(event.target)) {
            callback(event);
        }
    };

    document.addEventListener('click', handler);

    return () => {
        document.removeEventListener('click', handler);
    };
}

/**
 * 이벤트 리스너 일괄 등록/해제 관리자
 */
export class EventManager {
    constructor() {
        this.listeners = [];
    }

    /**
     * 이벤트 등록
     * @param {Element} element - 대상 요소
     * @param {string} type - 이벤트 타입
     * @param {Function} handler - 핸들러
     * @param {Object} options - 이벤트 옵션
     */
    add(element, type, handler, options = {}) {
        element.addEventListener(type, handler, options);
        this.listeners.push({ element, type, handler, options });
    }

    /**
     * 모든 이벤트 해제
     */
    removeAll() {
        this.listeners.forEach(({ element, type, handler, options }) => {
            element.removeEventListener(type, handler, options);
        });
        this.listeners = [];
    }
}
