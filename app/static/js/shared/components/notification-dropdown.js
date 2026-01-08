/**
 * notification-dropdown.js - 알림 드롭다운 컴포넌트 스크립트
 *
 * 포함 기능:
 * - 알림 드롭다운 토글
 * - 알림 로드 및 렌더링
 * - 읽음 처리
 * - 모두 읽음 처리
 */

// 알림 드롭다운 관리
(function() {
    let notificationPanel = null;
    let notificationBadge = null;
    let notificationList = null;

    document.addEventListener('DOMContentLoaded', function() {
        notificationPanel = document.getElementById('notificationPanel');
        notificationBadge = document.getElementById('notificationBadge');
        notificationList = document.getElementById('notificationList');

        if (!notificationPanel) return; // 알림 드롭다운이 없으면 초기화 안함

        // 초기 알림 로드
        loadNotifications();
        loadUnreadCount();

        // 주기적으로 알림 개수 업데이트 (30초마다)
        setInterval(loadUnreadCount, 30000);

        // 외부 클릭 시 닫기
        document.addEventListener('click', function(e) {
            const dropdown = document.getElementById('notificationDropdown');
            if (dropdown && !dropdown.contains(e.target)) {
                notificationPanel.classList.remove('show');
            }
        });

        // 이벤트 위임 설정
        initNotificationEventDelegation();
    });

    /**
     * 이벤트 위임 초기화
     */
    function initNotificationEventDelegation() {
        const dropdown = document.getElementById('notificationDropdown');
        if (!dropdown) return;

        dropdown.addEventListener('click', function(e) {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;

            switch (action) {
                case 'toggle-notification':
                    toggleNotificationDropdown();
                    break;
                case 'mark-all-read':
                    markAllAsRead();
                    break;
                case 'notification-click':
                    const notificationId = target.dataset.notificationId;
                    const actionUrl = target.dataset.actionUrl || '';
                    handleNotificationClick(notificationId, actionUrl);
                    break;
            }
        });
    }

    /**
     * 알림 드롭다운 토글
     */
    window.toggleNotificationDropdown = function() {
        if (!notificationPanel) return;
        notificationPanel.classList.toggle('show');
        if (notificationPanel.classList.contains('show')) {
            loadNotifications();
        }
    };

    /**
     * 알림 목록 로드
     */
    window.loadNotifications = async function() {
        if (!notificationList) return;

        try {
            const response = await fetch('/api/notifications?limit=10');
            const data = await response.json();

            if (data.success && data.notifications.length > 0) {
                renderNotifications(data.notifications);
            } else {
                notificationList.innerHTML = `
                    <div class="notification-empty">
                        <i class="fas fa-bell-slash"></i>
                        <p>알림이 없습니다</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('알림 로드 실패:', error);
        }
    };

    /**
     * 읽지 않은 알림 개수 로드
     */
    window.loadUnreadCount = async function() {
        if (!notificationBadge) return;

        try {
            const response = await fetch('/api/notifications/count');
            const data = await response.json();

            if (data.success) {
                if (data.count > 0) {
                    notificationBadge.textContent = data.count > 99 ? '99+' : data.count;
                    notificationBadge.style.display = 'flex';
                } else {
                    notificationBadge.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('알림 개수 로드 실패:', error);
        }
    };

    /**
     * 알림 목록 렌더링
     */
    function renderNotifications(notifications) {
        notificationList.innerHTML = notifications.map(n => `
            <div class="notification-item ${n.is_read ? '' : 'unread'}"
                 data-action="notification-click"
                 data-notification-id="${n.id}"
                 data-action-url="${n.action_url || ''}">
                <div class="notification-icon ${getIconClass(n.notification_type)}">
                    <i class="${getIcon(n.notification_type)}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${escapeHtml(n.title)}</div>
                    <div class="notification-message">${escapeHtml(n.message || '')}</div>
                    <div class="notification-time">${formatTime(n.created_at)}</div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 알림 클릭 처리
     */
    window.handleNotificationClick = async function(id, actionUrl) {
        // 읽음 처리
        try {
            await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
            loadUnreadCount();
        } catch (error) {
            console.error('읽음 처리 실패:', error);
        }

        // 액션 URL로 이동
        if (actionUrl) {
            window.location.href = actionUrl;
        }
    };

    /**
     * 모든 알림 읽음 처리
     */
    window.markAllAsRead = async function() {
        try {
            await fetch('/api/notifications/read-all', { method: 'POST' });
            loadNotifications();
            loadUnreadCount();
        } catch (error) {
            console.error('모두 읽음 처리 실패:', error);
        }
    };

    /**
     * 알림 유형별 아이콘 클래스
     */
    function getIconClass(type) {
        const classes = {
            'contract_request': 'contract',
            'contract_approved': 'contract',
            'contract_rejected': 'contract',
            'contract_terminated': 'contract',
            'sync_completed': 'sync',
            'sync_failed': 'warning',
            'termination_processed': 'termination',
            'system': 'system',
            'warning': 'warning'
        };
        return classes[type] || 'system';
    }

    /**
     * 알림 유형별 아이콘
     */
    function getIcon(type) {
        const icons = {
            'contract_request': 'fas fa-file-contract',
            'contract_approved': 'fas fa-check-circle',
            'contract_rejected': 'fas fa-times-circle',
            'contract_terminated': 'fas fa-file-times',
            'sync_completed': 'fas fa-sync',
            'sync_failed': 'fas fa-exclamation-triangle',
            'termination_processed': 'fas fa-user-times',
            'system': 'fas fa-cog',
            'warning': 'fas fa-exclamation-triangle'
        };
        return icons[type] || 'fas fa-bell';
    }

    /**
     * 시간 포맷팅
     */
    function formatTime(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return '방금 전';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}분 전`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}시간 전`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}일 전`;
        return date.toLocaleDateString('ko-KR');
    }

    /**
     * HTML 이스케이프
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();
