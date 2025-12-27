/**
 * 인사카드 관리 시스템 - 메인 애플리케이션
 * ES6 모듈 기반 진입점
 *
 * HRApp 네임스페이스 구조:
 * - HRApp.toast: 토스트 알림 기능
 * - HRApp.filter: 필터링 기능
 * - HRApp.employee: 직원 관련 기능
 * - HRApp.ui: UI 유틸리티 기능
 */

import { Toast, showToast } from './components/toast.js';
import { FormValidator } from './components/form-validator.js';
import { Filter, applyFilters, resetFilters, removeFilter, toggleFilterBar } from './components/filter.js';
import { searchEmployees } from './services/employee-service.js';
import { SalaryCalculator, SalaryCalculatorModal } from './components/salary-calculator.js';
import { initAvatarFallback } from './components/avatar-fallback.js';

/**
 * 정렬 적용 함수
 */
function applySorting() {
    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    const value = sortSelect.value;
    const url = new URL(window.location.href);

    if (value) {
        const parts = value.split('-');
        const sortField = parts[0];
        const sortOrder = parts[1] === 'desc' ? 'desc' : 'asc';

        url.searchParams.set('sort', sortField);
        url.searchParams.set('order', sortOrder);
    } else {
        url.searchParams.delete('sort');
        url.searchParams.delete('order');
    }

    window.location.href = url.toString();
}

/**
 * 로그아웃 처리 함수
 */
function handleLogout() {
    if (confirm('로그아웃 하시겠습니까?')) {
        showToast('로그아웃되었습니다.');
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
}

/**
 * 직원 목록 뷰 전환 함수
 * @param {string} viewType - 'list' 또는 'card'
 */
function toggleEmployeeView(viewType) {
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    const listBtn = document.querySelector('.view-toggle-btn[data-view="list"]');
    const cardBtn = document.querySelector('.view-toggle-btn[data-view="card"]');

    if (!listView || !cardView || !listBtn || !cardBtn) {
        return;
    }

    if (viewType === 'list') {
        listView.style.display = 'block';
        cardView.style.display = 'none';
        listBtn.classList.add('active');
        cardBtn.classList.remove('active');
    } else if (viewType === 'card') {
        listView.style.display = 'none';
        cardView.style.display = 'grid';
        listBtn.classList.remove('active');
        cardBtn.classList.add('active');
    }
}

/**
 * HRApp 네임스페이스 - 전역 API
 */
window.HRApp = {
    version: '1.0.0',

    toast: {
        show: showToast
    },

    filter: {
        apply: applyFilters,
        reset: resetFilters,
        remove: removeFilter,
        toggle: toggleFilterBar
    },

    employee: {
        search: searchEmployees
    },

    ui: {
        applySorting: applySorting,
        handleLogout: handleLogout,
        toggleView: toggleEmployeeView
    }
};

/**
 * 기존 코드 호환성을 위한 전역 함수 (deprecated)
 * 2025-03 이후 제거 예정, HRApp 네임스페이스 사용 권장
 *
 * 마이그레이션 가이드:
 * - window.showToast() → HRApp.toast.show()
 * - window.applyFilters() → HRApp.filter.apply()
 * - window.resetFilters() → HRApp.filter.reset()
 * - window.removeFilter() → HRApp.filter.remove()
 * - window.toggleFilterBar() → HRApp.filter.toggle()
 * - window.searchEmployees() → HRApp.employee.search()
 * - window.applySorting() → HRApp.ui.applySorting()
 * - window.handleLogout() → HRApp.ui.handleLogout()
 * - window.toggleEmployeeView() → HRApp.ui.toggleView()
 */
window.showToast = (...args) => {
    console.warn('DEPRECATED: window.showToast() → HRApp.toast.show()');
    return showToast(...args);
};
window.applyFilters = (...args) => {
    console.warn('DEPRECATED: window.applyFilters() → HRApp.filter.apply()');
    return applyFilters(...args);
};
window.resetFilters = (...args) => {
    console.warn('DEPRECATED: window.resetFilters() → HRApp.filter.reset()');
    return resetFilters(...args);
};
window.removeFilter = (...args) => {
    console.warn('DEPRECATED: window.removeFilter() → HRApp.filter.remove()');
    return removeFilter(...args);
};
window.toggleFilterBar = (...args) => {
    console.warn('DEPRECATED: window.toggleFilterBar() → HRApp.filter.toggle()');
    return toggleFilterBar(...args);
};
window.searchEmployees = (...args) => {
    console.warn('DEPRECATED: window.searchEmployees() → HRApp.employee.search()');
    return searchEmployees(...args);
};
window.applySorting = (...args) => {
    console.warn('DEPRECATED: window.applySorting() → HRApp.ui.applySorting()');
    return applySorting(...args);
};
window.handleLogout = (...args) => {
    console.warn('DEPRECATED: window.handleLogout() → HRApp.ui.handleLogout()');
    return handleLogout(...args);
};
window.toggleEmployeeView = (...args) => {
    console.warn('DEPRECATED: window.toggleEmployeeView() → HRApp.ui.toggleView()');
    return toggleEmployeeView(...args);
};

// 페이지 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 아바타 폴백 초기화 (이미지 로드 실패 처리)
    initAvatarFallback();

    // Flash 메시지 닫기 버튼 처리
    document.addEventListener('click', (e) => {
        const closeBtn = e.target.closest('[data-action="close-alert"]');
        if (closeBtn) {
            const alert = closeBtn.closest('.alert');
            if (alert) {
                alert.remove();
            }
        }
    });

    // 헤더 검색 폼 제출 방지 (엔터 키 처리)
    const searchForm = document.querySelector('.header-search form');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            const input = searchForm.querySelector('input[name="q"]');
            if (!input.value.trim()) {
                e.preventDefault();
            }
        });
    }

    // 폼 유효성 검사 초기화
    new FormValidator();

    // 직원 목록 뷰 초기화
    const listView = document.getElementById('list-view');
    const cardView = document.getElementById('card-view');
    if (listView && cardView) {
        window.toggleEmployeeView('list');
    }

    // 필터 초기화
    const filterContext = document.body.dataset.pageContext || 'list';
    new Filter(filterContext);

    // 카드 클릭 이벤트 처리
    document.addEventListener('click', (e) => {
        const card = e.target.closest('.employee-card');
        if (card && !e.target.closest('.employee-actions')) {
            const employeeId = card.getAttribute('data-id');
            if (employeeId) {
                window.location.href = `/employees/${employeeId}`;
            }
        }
    });

    // 급여 계산기 초기화
    initializeSalaryCalculator();

    // Flash 메시지를 Toast로 변환 (레이아웃 시프트 방지)
    document.querySelectorAll('.flash-messages .alert').forEach(alert => {
        const messageSpan = alert.querySelector('span');
        const message = messageSpan ? messageSpan.textContent : '';

        let type = 'info';
        if (alert.classList.contains('alert-success')) type = 'success';
        else if (alert.classList.contains('alert-error')) type = 'error';
        else if (alert.classList.contains('alert-warning')) type = 'warning';

        if (message) {
            showToast(message, type);
        }
        alert.remove();
    });

    // 빈 Flash 컨테이너 정리
    const flashContainer = document.querySelector('.flash-messages');
    if (flashContainer && flashContainer.children.length === 0) {
        flashContainer.remove();
    }
});

/**
 * 급여 계산기 초기화
 */
function initializeSalaryCalculator() {
    const openBtn = document.getElementById('openSalaryCalculatorBtn');
    const modal = document.getElementById('salaryCalculatorModal');

    if (!openBtn || !modal) return;

    // 모달 인스턴스 생성
    const salaryCalcModal = new SalaryCalculatorModal({
        modalId: 'salaryCalculatorModal',
        onApply: (result) => {
            // 폼에 계산 결과 적용
            applySalaryCalculationToForm(result);
        }
    });

    // 계산기 열기 버튼 이벤트
    openBtn.addEventListener('click', () => {
        // 현재 폼 값으로 초기값 설정
        const initialValues = {
            annualSalary: parseInt(document.getElementById('annual_salary')?.value) || 52000000,
            mealAllowance: parseInt(document.getElementById('meal_allowance')?.value) || 200000,
            overtimeHours: parseInt(document.getElementById('overtime_hours')?.value) || 24,
            nightHours: parseInt(document.getElementById('night_hours')?.value) || 8,
            holidayDays: parseInt(document.getElementById('holiday_days')?.value) || 1
        };

        salaryCalcModal.open(initialValues);
    });

    // 취소 버튼 이벤트
    const cancelBtn = document.getElementById('calcCancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            salaryCalcModal.close();
        });
    }

    // HRApp에 급여 계산기 추가
    window.HRApp.salary = {
        calculator: new SalaryCalculator(),
        modal: salaryCalcModal
    };
}

/**
 * 급여 계산 결과를 폼에 적용
 * @param {Object} result - 계산 결과
 */
function applySalaryCalculationToForm(result) {
    const formatter = (num) => Math.floor(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');

    // 기본급 적용
    const baseSalaryField = document.getElementById('base_salary');
    if (baseSalaryField) {
        baseSalaryField.value = result.baseSalary;
    }

    // 식대 적용
    const mealField = document.getElementById('meal_allowance');
    if (mealField) {
        mealField.value = result.allowances.meal;
    }

    // 포괄임금제 필드 적용
    const annualSalaryField = document.getElementById('annual_salary');
    if (annualSalaryField) {
        annualSalaryField.value = result.input.annualSalary;
    }

    const hourlyWageField = document.getElementById('hourly_wage');
    if (hourlyWageField) {
        hourlyWageField.value = result.hourlyWage;
    }

    const overtimeHoursField = document.getElementById('overtime_hours');
    if (overtimeHoursField) {
        overtimeHoursField.value = result.input.overtimeHours;
    }

    const overtimeAllowanceField = document.getElementById('overtime_allowance');
    if (overtimeAllowanceField) {
        overtimeAllowanceField.value = result.allowances.overtime;
    }

    const nightHoursField = document.getElementById('night_hours');
    if (nightHoursField) {
        nightHoursField.value = result.input.nightHours;
    }

    const nightAllowanceField = document.getElementById('night_allowance');
    if (nightAllowanceField) {
        nightAllowanceField.value = result.allowances.night;
    }

    const holidayDaysField = document.getElementById('holiday_days');
    if (holidayDaysField) {
        holidayDaysField.value = result.input.holidayDays;
    }

    const holidayAllowanceField = document.getElementById('holiday_allowance');
    if (holidayAllowanceField) {
        holidayAllowanceField.value = result.allowances.holiday;
    }

    // 요약 섹션 표시 및 업데이트
    const summarySection = document.getElementById('comprehensiveSalarySummary');
    if (summarySection) {
        summarySection.style.display = 'block';

        const summaryAnnual = document.getElementById('summaryAnnualSalary');
        if (summaryAnnual) {
            summaryAnnual.textContent = formatter(result.input.annualSalary) + '원';
        }

        const summaryHourly = document.getElementById('summaryHourlyWage');
        if (summaryHourly) {
            summaryHourly.textContent = formatter(result.hourlyWage) + '원/시간';
        }

        const summaryOvertime = document.getElementById('summaryOvertimeHours');
        if (summaryOvertime) {
            summaryOvertime.textContent = result.input.overtimeHours + '시간/월';
        }
    }

    // 상세 필드 섹션 표시
    const detailsSection = document.getElementById('comprehensiveSalaryDetails');
    if (detailsSection) {
        detailsSection.style.display = 'block';
    }
}
