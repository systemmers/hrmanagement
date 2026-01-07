/**
 * AllowanceManager 클래스
 * Phase 7: 프론트엔드 리팩토링 - salary-calculator.js 분할
 *
 * 수당 목록 관리 (통상임금 포함/미포함 구분)
 */

import { DEFAULT_ALLOWANCES } from './constants.js';

/**
 * AllowanceManager 클래스
 * 수당 목록 관리 (통상임금 포함/미포함 구분)
 */
export class AllowanceManager {
    constructor(initialAllowances = null) {
        this.allowances = initialAllowances
            ? initialAllowances.map(a => ({ ...a }))
            : DEFAULT_ALLOWANCES.map(a => ({ ...a }));
        this.idCounter = 100;
        this.onChange = null;
    }

    /**
     * 수당 추가
     * @param {Object} allowance - 수당 정보
     * @returns {Object} 추가된 수당
     */
    addAllowance(allowance) {
        const newAllowance = {
            id: `custom_${this.idCounter++}`,
            name: allowance.name,
            amount: allowance.amount || 0,
            includedInOrdinaryWage: allowance.includedInOrdinaryWage !== false,
            taxable: allowance.taxable !== false,
            removable: true
        };
        this.allowances.push(newAllowance);
        this._triggerChange();
        return newAllowance;
    }

    /**
     * 수당 삭제
     * @param {string} id - 수당 ID
     * @returns {boolean} 삭제 성공 여부
     */
    removeAllowance(id) {
        const index = this.allowances.findIndex(a => a.id === id);
        if (index === -1) return false;

        const allowance = this.allowances[index];
        if (!allowance.removable) return false;

        this.allowances.splice(index, 1);
        this._triggerChange();
        return true;
    }

    /**
     * 수당 업데이트
     * @param {string} id - 수당 ID
     * @param {Object} updates - 업데이트할 필드
     * @returns {Object|null} 업데이트된 수당
     */
    updateAllowance(id, updates) {
        const allowance = this.allowances.find(a => a.id === id);
        if (!allowance) return null;

        if (updates.amount !== undefined) allowance.amount = updates.amount;
        if (updates.includedInOrdinaryWage !== undefined) {
            allowance.includedInOrdinaryWage = updates.includedInOrdinaryWage;
        }
        if (updates.name !== undefined) allowance.name = updates.name;
        if (updates.taxable !== undefined) allowance.taxable = updates.taxable;

        this._triggerChange();
        return allowance;
    }

    /**
     * 통상임금 포함 수당 합계
     * @returns {number}
     */
    getOrdinaryWageIncludedSum() {
        return this.allowances
            .filter(a => a.includedInOrdinaryWage && a.amount > 0)
            .reduce((sum, a) => sum + a.amount, 0);
    }

    /**
     * 통상임금 미포함 수당 합계
     * @returns {number}
     */
    getOrdinaryWageExcludedSum() {
        return this.allowances
            .filter(a => !a.includedInOrdinaryWage && a.amount > 0)
            .reduce((sum, a) => sum + a.amount, 0);
    }

    /**
     * 전체 수당 합계
     * @returns {number}
     */
    getTotalSum() {
        return this.allowances
            .filter(a => a.amount > 0)
            .reduce((sum, a) => sum + a.amount, 0);
    }

    /**
     * 통상임금 포함 수당 목록
     * @returns {Array}
     */
    getOrdinaryWageIncludedAllowances() {
        return this.allowances.filter(a => a.includedInOrdinaryWage && a.amount > 0);
    }

    /**
     * 통상임금 미포함 수당 목록
     * @returns {Array}
     */
    getOrdinaryWageExcludedAllowances() {
        return this.allowances.filter(a => !a.includedInOrdinaryWage && a.amount > 0);
    }

    /**
     * 전체 수당 목록
     * @returns {Array}
     */
    getAllAllowances() {
        return [...this.allowances];
    }

    /**
     * 수당명 중복 체크
     * @param {string} name - 수당명
     * @param {string} excludeId - 제외할 ID (수정 시)
     * @returns {boolean}
     */
    isDuplicateName(name, excludeId = null) {
        return this.allowances.some(a =>
            a.name === name && a.id !== excludeId
        );
    }

    /**
     * 기본값으로 초기화
     */
    reset() {
        this.allowances = DEFAULT_ALLOWANCES.map(a => ({ ...a }));
        this._triggerChange();
    }

    /**
     * 변경 콜백 트리거
     */
    _triggerChange() {
        if (this.onChange) {
            this.onChange(this.allowances);
        }
    }

    /**
     * JSON 직렬화
     * @returns {Array}
     */
    toJSON() {
        return this.allowances.map(a => ({ ...a }));
    }

    /**
     * JSON에서 복원
     * @param {Array} data
     */
    fromJSON(data) {
        if (Array.isArray(data)) {
            this.allowances = data.map(a => ({ ...a }));
            this._triggerChange();
        }
    }
}

export default AllowanceManager;
