/**
 * 폼 유효성 검사 컴포넌트
 */

import { showToast } from './toast.js';

export class FormValidator {
    constructor(formSelector = 'form.employee-form') {
        this.forms = document.querySelectorAll(formSelector);
        this.init();
    }

    init() {
        this.forms.forEach(form => {
            form.addEventListener('submit', (e) => this.validateForm(e, form));
        });

        // 입력 필드 포커스 시 에러 상태 제거
        const inputs = document.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.style.borderColor = '';
            });
        });
    }

    validateForm(event, form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#ef4444';
            } else {
                field.style.borderColor = '';
            }
        });

        if (!isValid) {
            event.preventDefault();
            showToast('필수 항목을 모두 입력해주세요.', 'error');
        }

        return isValid;
    }
}
