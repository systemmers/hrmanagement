/**
 * 토스트 알림 컴포넌트
 */

export class Toast {
    constructor(containerId = 'toastContainer') {
        this.container = document.getElementById(containerId);
    }

    show(message, type = 'success') {
        if (!this.container) {
            console.warn('Toast container not found');
            return;
        }

        const toast = document.createElement('div');
        toast.className = 'toast';

        const iconClass = type === 'success' ? 'fa-check-circle' :
                          type === 'error' ? 'fa-exclamation-circle' :
                          'fa-info-circle';

        toast.innerHTML = `
            <i class="fas ${iconClass} toast-icon"></i>
            <span class="toast-message">${message}</span>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    success(message) {
        this.show(message, 'success');
    }

    error(message) {
        this.show(message, 'error');
    }

    info(message) {
        this.show(message, 'info');
    }
}

// 전역 함수로도 사용 가능하도록 (기존 코드 호환성)
export function showToast(message, type = 'success') {
    const toast = new Toast();
    toast.show(message, type);
}
