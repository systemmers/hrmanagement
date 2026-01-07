/**
 * CellRenderer - 셀 렌더링 유틸리티
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class CellRenderer {
    /**
     * 셀 값 렌더링
     * @param {Object} column - 컬럼 설정
     * @param {*} value - 셀 값
     * @param {Object} row - 행 데이터
     * @returns {string} 렌더링된 HTML
     */
    render(column, value, row) {
        // 커스텀 렌더러가 있으면 사용
        if (column.render) {
            return column.render(value, row);
        }

        // 기본 렌더러
        if (value === null || value === undefined) {
            return '<span class="text-muted">-</span>';
        }

        // 타입별 렌더링
        switch (column.type) {
            case 'status':
                return this._renderStatus(value);
            case 'number':
                return this._renderNumber(value);
            case 'currency':
                return this._renderCurrency(value, column);
            case 'date':
                return this._renderDate(value);
            case 'boolean':
                return this._renderBoolean(value);
            case 'link':
                return this._renderLink(value, column, row);
            case 'badge':
                return this._renderBadge(value, column);
            default:
                return this._escapeHtml(String(value));
        }
    }

    /**
     * 상태 배지 렌더링
     */
    _renderStatus(value) {
        const statusClass = String(value).toLowerCase().replace(/\s+/g, '-');
        return `<span class="status-badge ${statusClass}">${value}</span>`;
    }

    /**
     * 숫자 렌더링
     */
    _renderNumber(value) {
        return new Intl.NumberFormat('ko-KR').format(value);
    }

    /**
     * 통화 렌더링
     */
    _renderCurrency(value, column) {
        const formatted = new Intl.NumberFormat('ko-KR').format(value);
        const prefix = column.prefix || '';
        const suffix = column.suffix || '원';
        return `${prefix}${formatted}${suffix}`;
    }

    /**
     * 날짜 렌더링
     */
    _renderDate(value) {
        if (!value) return '-';
        const date = new Date(value);
        if (isNaN(date.getTime())) return value;
        return date.toLocaleDateString('ko-KR');
    }

    /**
     * 불린 렌더링
     */
    _renderBoolean(value) {
        if (value) {
            return '<i class="fas fa-check text-success"></i>';
        }
        return '<i class="fas fa-times text-muted"></i>';
    }

    /**
     * 링크 렌더링
     */
    _renderLink(value, column, row) {
        const href = column.hrefTemplate
            ? column.hrefTemplate.replace(/{(\w+)}/g, (_, key) => row[key] || '')
            : value;
        return `<a href="${href}" class="table-link">${this._escapeHtml(value)}</a>`;
    }

    /**
     * 배지 렌더링
     */
    _renderBadge(value, column) {
        const badgeClass = column.badgeMap?.[value] || 'default';
        return `<span class="badge badge-${badgeClass}">${value}</span>`;
    }

    /**
     * HTML 이스케이프
     */
    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * 합계 계산
     * @param {Array} data - 데이터 배열
     * @param {string} columnKey - 컬럼 키
     * @returns {number} 합계
     */
    calculateSum(data, columnKey) {
        return data.reduce((acc, row) => {
            return acc + (Number(row[columnKey]) || 0);
        }, 0);
    }
}

export default CellRenderer;
