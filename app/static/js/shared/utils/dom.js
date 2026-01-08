/**
 * DOM 조작 유틸리티
 * Phase 7: 프론트엔드 리팩토링
 *
 * DOM 요소 생성, 조회, 조작을 위한 헬퍼 함수를 제공합니다.
 */

/**
 * 요소 선택 (단일)
 * @param {string} selector - CSS 선택자
 * @param {Element} parent - 부모 요소 (기본: document)
 * @returns {Element|null} 찾은 요소
 */
export function $(selector, parent = document) {
    return parent.querySelector(selector);
}

/**
 * 요소 선택 (복수)
 * @param {string} selector - CSS 선택자
 * @param {Element} parent - 부모 요소 (기본: document)
 * @returns {Element[]} 찾은 요소 배열
 */
export function $$(selector, parent = document) {
    return Array.from(parent.querySelectorAll(selector));
}

/**
 * 요소 생성
 * @param {string} tag - 태그명
 * @param {Object} options - 옵션 (className, innerHTML, attributes, dataset, styles)
 * @returns {Element} 생성된 요소
 */
export function createElement(tag, options = {}) {
    const element = document.createElement(tag);

    if (options.className) {
        element.className = options.className;
    }

    if (options.innerHTML) {
        element.innerHTML = options.innerHTML;
    }

    if (options.textContent) {
        element.textContent = options.textContent;
    }

    if (options.attributes) {
        Object.entries(options.attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
    }

    if (options.dataset) {
        Object.entries(options.dataset).forEach(([key, value]) => {
            element.dataset[key] = value;
        });
    }

    if (options.styles) {
        Object.assign(element.style, options.styles);
    }

    if (options.children) {
        options.children.forEach(child => {
            if (child instanceof Element) {
                element.appendChild(child);
            } else if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            }
        });
    }

    return element;
}

/**
 * 요소 표시/숨김 토글
 * @param {Element|string} element - 요소 또는 선택자
 * @param {boolean} show - 표시 여부 (undefined면 토글)
 */
export function toggleVisibility(element, show) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;

    if (show === undefined) {
        el.classList.toggle('hidden');
    } else {
        el.classList.toggle('hidden', !show);
    }
}

/**
 * 요소 표시
 * @param {Element|string} element - 요소 또는 선택자
 */
export function show(element) {
    toggleVisibility(element, true);
}

/**
 * 요소 숨김
 * @param {Element|string} element - 요소 또는 선택자
 */
export function hide(element) {
    toggleVisibility(element, false);
}

/**
 * 클래스 토글
 * @param {Element|string} element - 요소 또는 선택자
 * @param {string} className - 클래스명
 * @param {boolean} force - 강제 추가/제거
 */
export function toggleClass(element, className, force) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;
    el.classList.toggle(className, force);
}

/**
 * 요소 비활성화/활성화
 * @param {Element|string} element - 요소 또는 선택자
 * @param {boolean} disabled - 비활성화 여부
 */
export function setDisabled(element, disabled) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;
    el.disabled = disabled;
    toggleClass(el, 'disabled', disabled);
}

/**
 * 여러 요소 비활성화/활성화
 * @param {string} selector - CSS 선택자
 * @param {boolean} disabled - 비활성화 여부
 */
export function setDisabledAll(selector, disabled) {
    $$(selector).forEach(el => setDisabled(el, disabled));
}

/**
 * 입력 필드 값 설정
 * @param {Element|string} element - 요소 또는 선택자
 * @param {*} value - 설정할 값
 */
export function setValue(element, value) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;

    if (el.type === 'checkbox') {
        el.checked = Boolean(value);
    } else if (el.type === 'radio') {
        el.checked = el.value === String(value);
    } else {
        el.value = value ?? '';
    }
}

/**
 * 입력 필드 값 가져오기
 * @param {Element|string} element - 요소 또는 선택자
 * @returns {*} 필드 값
 */
export function getValue(element) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return null;

    if (el.type === 'checkbox') {
        return el.checked;
    } else if (el.type === 'number') {
        return el.valueAsNumber || 0;
    }
    return el.value;
}

/**
 * 요소 내용 비우기
 * @param {Element|string} element - 요소 또는 선택자
 */
export function empty(element) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;
    el.innerHTML = '';
}

/**
 * 요소가 보이는지 확인
 * @param {Element} element - 확인할 요소
 * @returns {boolean} 보이는지 여부
 */
export function isVisible(element) {
    if (!element) return false;
    return !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length);
}

/**
 * 스크롤 위치로 이동
 * @param {Element|string} element - 요소 또는 선택자
 * @param {Object} options - 스크롤 옵션
 */
export function scrollIntoView(element, options = { behavior: 'smooth', block: 'center' }) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;
    el.scrollIntoView(options);
}

/**
 * 폼 데이터를 객체로 변환
 * @param {HTMLFormElement|string} form - 폼 요소 또는 선택자
 * @returns {Object} 폼 데이터 객체
 */
export function getFormData(form) {
    const formEl = typeof form === 'string' ? $(form) : form;
    if (!formEl) return {};

    const formData = new FormData(formEl);
    const data = {};

    formData.forEach((value, key) => {
        if (data[key]) {
            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    });

    return data;
}

/**
 * 요소에 포커스 설정 (지연 가능)
 * @param {Element|string} element - 요소 또는 선택자
 * @param {number} delay - 지연 시간 (ms)
 */
export function focus(element, delay = 0) {
    const el = typeof element === 'string' ? $(element) : element;
    if (!el) return;

    if (delay > 0) {
        setTimeout(() => el.focus(), delay);
    } else {
        el.focus();
    }
}
