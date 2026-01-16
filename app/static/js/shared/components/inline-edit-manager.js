/**
 * InlineEditManager - 인라인 편집 상태 관리자
 *
 * Phase 0.1: 인라인 편집 시스템 인프라
 * Phase 2: CREATE 모드 지원 추가 (신규 직원 등록)
 *
 * 상태 머신: VIEW -> EDITING -> SAVING -> VIEW/ERROR
 * 패턴: 상태 머신, 옵저버, 이벤트 위임
 *
 * 모드:
 * - EDIT 모드: employeeId 있음, 섹션별 PATCH 저장
 * - CREATE 모드: employeeId 없음, 전체 POST 저장
 *
 * @example
 * // EDIT 모드 (기존)
 * const manager = new InlineEditManager({
 *     employeeId: 123,
 *     onSave: (sectionId, data) => console.log('saved'),
 *     onError: (sectionId, error) => console.log('error')
 * });
 *
 * // CREATE 모드 (신규)
 * const manager = new InlineEditManager({
 *     isCreateMode: true,
 *     requiredFields: ['name', 'account_username', 'account_email'],
 *     onCreateSuccess: (response) => window.location.href = `/employees/${response.employee_id}`
 * });
 * manager.init();
 */

import { patch, post, del } from '../utils/api.js';
import { Toast } from './toast.js';

// ========================================
// 상태 상수
// ========================================

export const EditState = {
    VIEW: 'VIEW',
    EDITING: 'EDITING',
    SAVING: 'SAVING',
    ERROR: 'ERROR'
};

// ========================================
// 섹션 설정 (detail.js SECTION_CONFIG 확장)
// ========================================

export const SECTION_CONFIG = {
    // 정적 섹션 (info-table) - Phase 1-7
    'personal': {
        name: '개인 기본정보',
        apiPath: 'personal',
        type: 'static'
    },
    'organization': {
        name: '소속정보',
        apiPath: 'organization',
        type: 'static'
    },
    'contract': {
        name: '계약정보',
        apiPath: 'contract',
        type: 'static',
        readonlyFields: ['contract_type', 'contract_start', 'contract_end']
    },
    'salary': {
        name: '급여정보',
        apiPath: 'salary',
        type: 'static'
    },
    'benefit': {
        name: '연차 및 복리후생',
        apiPath: 'benefit',
        type: 'static'
    },
    'military': {
        name: '병역정보',
        apiPath: 'military',
        type: 'static'
    },
    'attendance': {
        name: '근태현황',
        apiPath: 'attendance',
        type: 'static'
    },
    'account': {
        name: '계정정보',
        apiPath: 'account',
        type: 'static'
    }
};

// ========================================
// 동적 테이블 설정 (detail.js TABLE_CONFIG 확장)
// ========================================

export const TABLE_CONFIG = {
    // 이력 정보 - Phase 8-13
    'family': {
        name: '가족정보',
        apiPath: 'families',
        hasAttach: false,
        type: 'dynamic'
    },
    'education': {
        name: '학력정보',
        apiPath: 'educations',
        hasAttach: true,
        type: 'dynamic'
    },
    'career': {
        name: '경력정보',
        apiPath: 'careers',
        hasAttach: true,
        type: 'dynamic'
    },
    'certificate': {
        name: '자격증',
        apiPath: 'certificates',
        hasAttach: true,
        type: 'dynamic'
    },
    'language': {
        name: '언어능력',
        apiPath: 'languages',
        hasAttach: true,
        type: 'dynamic'
    },
    'award': {
        name: '수상내역',
        apiPath: 'awards',
        hasAttach: true,
        type: 'dynamic'
    },
    'project': {
        name: '프로젝트 참여',
        apiPath: 'projects',
        hasAttach: false,
        type: 'dynamic'
    },
    // HR 릴레이션 - Phase 14-21
    'employment-contract': {
        name: '근로계약 이력',
        apiPath: 'employment-contracts',
        hasAttach: true,
        type: 'dynamic'
    },
    'salary-history': {
        name: '연봉계약 이력',
        apiPath: 'salary-histories',
        hasAttach: true,
        type: 'dynamic'
    },
    'salary-payment': {
        name: '급여 지급 이력',
        apiPath: 'salary-payments',
        hasAttach: true,
        type: 'dynamic'
    },
    'promotion': {
        name: '인사이동/승진',
        apiPath: 'promotions',
        hasAttach: true,
        type: 'dynamic'
    },
    'evaluation': {
        name: '인사고과',
        apiPath: 'evaluations',
        hasAttach: false,
        type: 'dynamic'
    },
    'training': {
        name: '교육훈련',
        apiPath: 'trainings',
        hasAttach: true,
        type: 'dynamic'
    },
    'hr-project': {
        name: 'HR 프로젝트',
        apiPath: 'hr-projects',
        hasAttach: false,
        type: 'dynamic'
    },
    'asset': {
        name: '비품지급',
        apiPath: 'assets',
        hasAttach: false,
        type: 'dynamic'
    }
};

// ========================================
// InlineEditManager 클래스
// ========================================

export class InlineEditManager {
    /**
     * @param {Object} options - 설정 옵션
     * @param {number} [options.employeeId] - 직원 ID (EDIT 모드 필수)
     * @param {boolean} [options.isCreateMode=false] - CREATE 모드 여부
     * @param {string[]} [options.requiredFields] - 필수 필드 목록 (CREATE 모드)
     * @param {string} [options.apiBaseUrl='/api/employees'] - API 기본 URL
     * @param {string} [options.createApiUrl='/employees'] - 생성 API URL (CREATE 모드)
     * @param {Function} [options.onStateChange] - 상태 변경 콜백
     * @param {Function} [options.onSave] - 저장 성공 콜백
     * @param {Function} [options.onError] - 에러 콜백
     * @param {Function} [options.onCancel] - 취소 콜백
     * @param {Function} [options.onCreateSuccess] - 생성 성공 콜백 (CREATE 모드)
     */
    constructor(options = {}) {
        this.employeeId = options.employeeId;
        this.apiBaseUrl = options.apiBaseUrl || '/api/employees';

        // CREATE 모드 설정
        this.isCreateMode = options.isCreateMode || !this.employeeId;
        this.createApiUrl = options.createApiUrl || '/employees';
        this.requiredFields = options.requiredFields || ['name', 'account_username', 'account_email'];

        // 콜백 함수
        this.onStateChange = options.onStateChange || null;
        this.onSave = options.onSave || null;
        this.onError = options.onError || null;
        this.onCancel = options.onCancel || null;
        this.onCreateSuccess = options.onCreateSuccess || null;

        // 상태 관리
        this.sectionStates = new Map();  // sectionId -> EditState
        this.originalData = new Map();   // sectionId -> original data (롤백용)
        this.dirtyFields = new Map();    // sectionId -> Set of dirty field names

        // Toast 인스턴스
        this.toast = new Toast();

        // 이벤트 핸들러 바인딩
        this._handleEditClick = this._handleEditClick.bind(this);
        this._handleSaveClick = this._handleSaveClick.bind(this);
        this._handleCancelClick = this._handleCancelClick.bind(this);
        this._handleFieldChange = this._handleFieldChange.bind(this);
        this._handleKeydown = this._handleKeydown.bind(this);
        this._handleSubmitAllClick = this._handleSubmitAllClick.bind(this);
    }

    /**
     * 초기화 - 이벤트 리스너 등록
     */
    init() {
        // CREATE 모드는 employeeId 없이 동작
        if (!this.isCreateMode && !this.employeeId) {
            console.error('InlineEditManager: employeeId is required for EDIT mode');
            return;
        }

        // 이벤트 위임 등록
        document.addEventListener('click', this._handleEditClick);
        document.addEventListener('click', this._handleSaveClick);
        document.addEventListener('click', this._handleCancelClick);
        document.addEventListener('click', this._handleSubmitAllClick);
        document.addEventListener('input', this._handleFieldChange);
        document.addEventListener('change', this._handleFieldChange);
        document.addEventListener('keydown', this._handleKeydown);

        // CREATE 모드: 모든 섹션을 EDITING 상태로 초기화
        if (this.isCreateMode) {
            this._initCreateMode();
            console.log('InlineEditManager initialized in CREATE mode');
        } else {
            console.log('InlineEditManager initialized for employee:', this.employeeId);
        }
    }

    /**
     * CREATE 모드 초기화
     * - 모든 섹션을 EDITING 상태로 설정
     * - 섹션별 저장/취소 버튼 숨김
     * - 하단 최종 제출 버튼 활성화
     */
    _initCreateMode() {
        // CREATE 모드: VIEW 상태로 시작 (섹션별 수정 버튼 방식)
        const sections = document.querySelectorAll('[data-section]');
        sections.forEach(section => {
            const sectionId = section.dataset.section;
            // VIEW 상태로 초기화 (기존 EDIT 모드와 동일한 UX)
            this.setState(sectionId, EditState.VIEW);
            this.dirtyFields.set(sectionId, new Set());
        });

        // body에 create-mode 클래스 추가 (CSS 스타일링용)
        document.body.classList.add('create-mode');

        // 빈 값 플레이스홀더 표시
        this._showEmptyPlaceholders();
    }

    /**
     * 빈 값 필드에 플레이스홀더 표시 (CREATE 모드용)
     */
    _showEmptyPlaceholders() {
        const viewElements = document.querySelectorAll('.inline-edit__view');
        viewElements.forEach(view => {
            const text = view.textContent.trim();
            if (!text || text === '-' || text === '미입력') {
                view.classList.add('inline-edit__view--empty');
                if (!text) {
                    view.textContent = '(미입력)';
                }
            }
        });
    }

    /**
     * 첫 번째 필수 필드에 포커스
     */
    _focusFirstRequiredField() {
        if (this.requiredFields.length === 0) return;

        const firstRequiredField = this.requiredFields[0];
        const field = document.querySelector(`[data-field="${firstRequiredField}"]`);
        if (field) {
            const input = field.querySelector('input, select, textarea');
            if (input) {
                setTimeout(() => input.focus(), 100);
            }
        }
    }

    /**
     * 정리 - 이벤트 리스너 제거
     */
    destroy() {
        document.removeEventListener('click', this._handleEditClick);
        document.removeEventListener('click', this._handleSaveClick);
        document.removeEventListener('click', this._handleCancelClick);
        document.removeEventListener('click', this._handleSubmitAllClick);
        document.removeEventListener('input', this._handleFieldChange);
        document.removeEventListener('change', this._handleFieldChange);
        document.removeEventListener('keydown', this._handleKeydown);

        this.sectionStates.clear();
        this.originalData.clear();
        this.dirtyFields.clear();

        // CREATE 모드 클래스 제거
        document.body.classList.remove('create-mode');
    }

    // ========================================
    // CREATE 모드 전용 메서드
    // ========================================

    /**
     * 전체 폼 데이터 수집 (CREATE 모드용)
     * @returns {Object} 전체 폼 데이터
     */
    _collectAllFormData() {
        const data = {};
        const sections = document.querySelectorAll('[data-section]');

        sections.forEach(section => {
            const sectionId = section.dataset.section;
            const sectionData = this._collectFormData(sectionId);

            // 섹션 데이터를 플랫하게 병합 (빈 값으로 기존 값 덮어쓰기 방지)
            Object.entries(sectionData).forEach(([key, value]) => {
                // 기존 값이 있고 새 값이 비어있으면 덮어쓰지 않음
                if (data[key] && !value) {
                    return;
                }
                data[key] = value;
            });
        });

        return data;
    }

    /**
     * 필수 필드 검증 (CREATE 모드용)
     * @param {Object} data - 폼 데이터
     * @returns {Object} 필드별 에러 메시지 (빈 객체면 검증 통과)
     */
    _validateRequiredFields(data) {
        const errors = {};

        this.requiredFields.forEach(fieldName => {
            const value = data[fieldName];
            if (!value || (typeof value === 'string' && !value.trim())) {
                errors[fieldName] = this._getFieldLabel(fieldName) + '은(는) 필수 입력 항목입니다.';
            }
        });

        // 이메일 형식 검증
        if (data.account_email && !this._isValidEmail(data.account_email)) {
            errors.account_email = '올바른 이메일 형식이 아닙니다.';
        }

        // 계정 ID 형식 검증 (영문, 숫자, _ 만 허용, 4~50자)
        if (data.account_username) {
            if (!/^[a-zA-Z0-9_]+$/.test(data.account_username)) {
                errors.account_username = '계정 ID는 영문, 숫자, 밑줄(_)만 사용 가능합니다.';
            } else if (data.account_username.length < 4 || data.account_username.length > 50) {
                errors.account_username = '계정 ID는 4~50자 사이여야 합니다.';
            }
        }

        return errors;
    }

    /**
     * 이메일 형식 검증
     */
    _isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * 필드 라벨 조회
     */
    _getFieldLabel(fieldName) {
        const labelMap = {
            'name': '이름',
            'account_username': '계정 ID',
            'account_email': '이메일',
            'english_name': '영문명',
            'birth_date': '생년월일',
            'gender': '성별',
            'phone': '전화번호',
            'email': '이메일'
        };
        return labelMap[fieldName] || fieldName;
    }

    /**
     * 전체 폼 제출 (CREATE 모드 전용)
     * @returns {Promise<boolean>} 성공 여부
     */
    async submitAll() {
        if (!this.isCreateMode) {
            console.error('submitAll() is only available in CREATE mode');
            return false;
        }

        // 전체 데이터 수집
        const data = this._collectAllFormData();

        // 필수 필드 검증
        const errors = this._validateRequiredFields(data);
        if (Object.keys(errors).length > 0) {
            this._showAllFieldErrors(errors);
            this.toast.error('필수 항목을 입력해주세요.');
            return false;
        }

        // 제출 버튼 비활성화
        const submitBtn = document.querySelector('[data-action="submit-all"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>등록 중...</span>';
        }

        try {
            // POST /employees API 호출
            const response = await post(this.createApiUrl, data);

            this.toast.success(response.message || '직원이 등록되었습니다.');

            // 성공 콜백 또는 기본 동작 (상세 페이지로 이동)
            if (this.onCreateSuccess) {
                this.onCreateSuccess(response.data);
            } else if (response.data && response.data.employee_id) {
                window.location.href = `/employees/${response.data.employee_id}`;
            } else {
                window.location.href = '/employees';
            }

            return true;

        } catch (error) {
            // 에러 처리
            const message = error.data?.error || error.message || '등록 중 오류가 발생했습니다.';
            this.toast.error(message);

            // 필드별 에러 표시
            if (error.data?.errors) {
                this._showAllFieldErrors(error.data.errors);
            }

            // 콜백 호출
            if (this.onError) {
                this.onError(null, error);
            }

            return false;

        } finally {
            // 제출 버튼 복원
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-save"></i> <span>직원 등록</span>';
            }
        }
    }

    /**
     * 전체 필드 에러 표시 (CREATE 모드용)
     */
    _showAllFieldErrors(errors) {
        // 기존 에러 제거
        document.querySelectorAll('.inline-edit__input--invalid').forEach(el => {
            el.classList.remove('inline-edit__input--invalid');
        });
        document.querySelectorAll('.inline-edit__error').forEach(el => {
            el.remove();
        });

        // 새 에러 표시
        Object.entries(errors).forEach(([fieldName, message]) => {
            const field = document.querySelector(`[data-field="${fieldName}"]`);
            if (field) {
                field.classList.add('inline-edit__input--invalid');

                // 에러 메시지 표시
                let errorEl = field.querySelector('.inline-edit__error');
                if (!errorEl) {
                    errorEl = document.createElement('span');
                    errorEl.className = 'inline-edit__error';
                    field.appendChild(errorEl);
                }
                errorEl.textContent = message;

                // 첫 번째 에러 필드에 포커스
                const input = field.querySelector('input, select, textarea');
                if (input && Object.keys(errors)[0] === fieldName) {
                    input.focus();
                }
            }
        });
    }

    /**
     * 제출 버튼 클릭 핸들러 (CREATE 모드용)
     */
    _handleSubmitAllClick(e) {
        const btn = e.target.closest('[data-action="submit-all"]');
        if (!btn) return;

        e.preventDefault();
        this.submitAll();
    }

    // ========================================
    // 상태 관리
    // ========================================

    /**
     * 섹션 상태 조회
     * @param {string} sectionId - 섹션 ID
     * @returns {string} EditState
     */
    getState(sectionId) {
        return this.sectionStates.get(sectionId) || EditState.VIEW;
    }

    /**
     * 섹션 상태 설정
     * @param {string} sectionId - 섹션 ID
     * @param {string} state - EditState
     */
    setState(sectionId, state) {
        const prevState = this.getState(sectionId);
        this.sectionStates.set(sectionId, state);

        // CSS 클래스 업데이트
        this._updateSectionClasses(sectionId, state);

        // 콜백 호출
        if (this.onStateChange) {
            this.onStateChange(sectionId, state, prevState);
        }
    }

    /**
     * 편집 중인 섹션이 있는지 확인
     * @returns {boolean}
     */
    hasEditingSection() {
        for (const state of this.sectionStates.values()) {
            if (state === EditState.EDITING || state === EditState.SAVING) {
                return true;
            }
        }
        return false;
    }

    // ========================================
    // 편집 모드 전환
    // ========================================

    /**
     * 섹션 편집 모드 시작
     * @param {string} sectionId - 섹션 ID
     */
    editSection(sectionId) {
        const currentState = this.getState(sectionId);

        // 이미 편집 중이면 무시
        if (currentState !== EditState.VIEW) {
            return;
        }

        // 원본 데이터 저장 (롤백용)
        this._saveOriginalData(sectionId);

        // dirty 필드 초기화
        this.dirtyFields.set(sectionId, new Set());

        // 상태 전환
        this.setState(sectionId, EditState.EDITING);

        // 개인정보 섹션: 실제 거주지가 비어있으면 주민등록상 주소로 자동 복사
        if (sectionId === 'personal') {
            this._autoCopyAddressIfEmpty(sectionId);
        }

        // 첫 번째 입력 필드에 포커스
        this._focusFirstInput(sectionId);
    }

    /**
     * 섹션 저장
     * @param {string} sectionId - 섹션 ID
     * @returns {Promise<boolean>} 성공 여부
     */
    async saveSection(sectionId) {
        const currentState = this.getState(sectionId);

        if (currentState !== EditState.EDITING) {
            return false;
        }

        // 변경된 데이터 수집
        const data = this._collectFormData(sectionId);

        // CREATE 모드: API 호출 없이 로컬 상태만 업데이트
        if (this.isCreateMode) {
            return this._saveSectionLocal(sectionId, data);
        }

        // EDIT 모드: 기존 API 호출 로직
        // 상태 전환: SAVING
        this.setState(sectionId, EditState.SAVING);

        try {
            // 변경 사항 없으면 그냥 VIEW 모드로 복귀
            const dirtySet = this.dirtyFields.get(sectionId);
            if (!dirtySet || dirtySet.size === 0) {
                this.setState(sectionId, EditState.VIEW);
                this.toast.info('변경된 내용이 없습니다.');
                return true;
            }

            // API 호출
            const config = this._getSectionConfig(sectionId);
            const url = `${this.apiBaseUrl}/${this.employeeId}/sections/${config.apiPath}`;

            const response = await patch(url, data);

            // 성공
            this.setState(sectionId, EditState.VIEW);
            this._clearOriginalData(sectionId);
            this.dirtyFields.delete(sectionId);

            this.toast.success(response.message || `${config.name} 저장 완료`);

            // 콜백 호출
            if (this.onSave) {
                this.onSave(sectionId, response.data);
            }

            return true;

        } catch (error) {
            // 에러
            this.setState(sectionId, EditState.ERROR);

            const message = error.data?.error || error.message || '저장 중 오류가 발생했습니다.';
            this.toast.error(message);

            // 필드별 에러 표시
            if (error.data?.errors) {
                this._showFieldErrors(sectionId, error.data.errors);
            }

            // 콜백 호출
            if (this.onError) {
                this.onError(sectionId, error);
            }

            // 일정 시간 후 EDITING 상태로 복귀
            setTimeout(() => {
                if (this.getState(sectionId) === EditState.ERROR) {
                    this.setState(sectionId, EditState.EDITING);
                }
            }, 2000);

            return false;
        }
    }

    /**
     * 섹션 로컬 저장 (CREATE 모드용 - API 호출 없음)
     * @param {string} sectionId - 섹션 ID
     * @param {Object} data - 폼 데이터
     * @returns {boolean} 성공 여부
     */
    _saveSectionLocal(sectionId, data) {
        const config = this._getSectionConfig(sectionId);

        // VIEW 요소 업데이트 (입력한 값을 표시)
        this._updateViewElements(sectionId, data);

        // 상태 전환: VIEW
        this.setState(sectionId, EditState.VIEW);
        this.dirtyFields.delete(sectionId);

        this.toast.success(`${config.name} 입력 완료 (최종 등록 시 저장됩니다)`);
        return true;
    }

    /**
     * VIEW 요소 업데이트 (CREATE 모드용)
     * @param {string} sectionId - 섹션 ID
     * @param {Object} data - 폼 데이터
     */
    _updateViewElements(sectionId, data) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        const fields = section.querySelectorAll('[data-field]');
        fields.forEach(field => {
            const fieldName = field.dataset.field;
            const value = data[fieldName];
            const viewElement = field.querySelector('.inline-edit__view');

            if (viewElement) {
                // 값이 있으면 표시, 없으면 플레이스홀더
                if (value && String(value).trim()) {
                    viewElement.textContent = value;
                    viewElement.classList.remove('inline-edit__view--empty');
                } else {
                    viewElement.textContent = '(미입력)';
                    viewElement.classList.add('inline-edit__view--empty');
                }
            }
        });
    }

    /**
     * 편집 취소 (롤백)
     * @param {string} sectionId - 섹션 ID
     */
    cancelEdit(sectionId) {
        const currentState = this.getState(sectionId);

        if (currentState !== EditState.EDITING && currentState !== EditState.ERROR) {
            return;
        }

        // 원본 데이터로 롤백
        this._restoreOriginalData(sectionId);

        // 상태 복원
        this.setState(sectionId, EditState.VIEW);
        this._clearOriginalData(sectionId);
        this.dirtyFields.delete(sectionId);

        // 필드 에러 제거
        this._clearFieldErrors(sectionId);

        // 콜백 호출
        if (this.onCancel) {
            this.onCancel(sectionId);
        }
    }

    // ========================================
    // 동적 섹션 (테이블) CRUD
    // ========================================

    /**
     * 행 추가
     * @param {string} tableId - 테이블 ID
     * @param {Object} data - 새 행 데이터
     * @returns {Promise<Object|null>} 생성된 항목
     */
    async addRow(tableId, data) {
        const config = TABLE_CONFIG[tableId];
        if (!config) {
            console.error('Unknown table:', tableId);
            return null;
        }

        try {
            const url = `${this.apiBaseUrl}/${this.employeeId}/${config.apiPath}`;
            const response = await post(url, data);

            this.toast.success(response.message || `${config.name} 추가 완료`);
            return response.data;

        } catch (error) {
            const message = error.data?.error || error.message || '추가 중 오류가 발생했습니다.';
            this.toast.error(message);
            return null;
        }
    }

    /**
     * 행 수정
     * @param {string} tableId - 테이블 ID
     * @param {number} itemId - 항목 ID
     * @param {Object} data - 수정 데이터
     * @returns {Promise<Object|null>} 수정된 항목
     */
    async updateRow(tableId, itemId, data) {
        const config = TABLE_CONFIG[tableId];
        if (!config) {
            console.error('Unknown table:', tableId);
            return null;
        }

        try {
            const url = `${this.apiBaseUrl}/${this.employeeId}/${config.apiPath}/${itemId}`;
            const response = await patch(url, data);

            this.toast.success(response.message || `${config.name} 수정 완료`);
            return response.data;

        } catch (error) {
            const message = error.data?.error || error.message || '수정 중 오류가 발생했습니다.';
            this.toast.error(message);
            return null;
        }
    }

    /**
     * 행 삭제
     * @param {string} tableId - 테이블 ID
     * @param {number} itemId - 항목 ID
     * @returns {Promise<boolean>} 성공 여부
     */
    async deleteRow(tableId, itemId) {
        const config = TABLE_CONFIG[tableId];
        if (!config) {
            console.error('Unknown table:', tableId);
            return false;
        }

        if (!confirm(`${config.name} 항목을 삭제하시겠습니까?`)) {
            return false;
        }

        try {
            const url = `${this.apiBaseUrl}/${this.employeeId}/${config.apiPath}/${itemId}`;
            const response = await del(url);

            this.toast.success(response.message || `${config.name} 삭제 완료`);
            return true;

        } catch (error) {
            const message = error.data?.error || error.message || '삭제 중 오류가 발생했습니다.';
            this.toast.error(message);
            return false;
        }
    }

    // ========================================
    // 이벤트 핸들러 (이벤트 위임)
    // ========================================

    /**
     * 수정 버튼 클릭 핸들러
     */
    _handleEditClick(e) {
        const btn = e.target.closest('[data-inline-action="edit"]');
        if (!btn) return;

        const sectionId = btn.dataset.section;
        if (sectionId) {
            e.preventDefault();
            this.editSection(sectionId);
        }
    }

    /**
     * 저장 버튼 클릭 핸들러
     */
    _handleSaveClick(e) {
        const btn = e.target.closest('[data-inline-action="save"]');
        if (!btn) return;

        const sectionId = btn.dataset.section;
        if (sectionId) {
            e.preventDefault();
            this.saveSection(sectionId);
        }
    }

    /**
     * 취소 버튼 클릭 핸들러
     */
    _handleCancelClick(e) {
        const btn = e.target.closest('[data-inline-action="cancel"]');
        if (!btn) return;

        const sectionId = btn.dataset.section;
        if (sectionId) {
            e.preventDefault();
            this.cancelEdit(sectionId);
        }
    }

    /**
     * 필드 변경 핸들러 (dirty 추적)
     */
    _handleFieldChange(e) {
        const field = e.target.closest('[data-field]');
        if (!field) return;

        const section = field.closest('[data-section]');
        if (!section) return;

        const sectionId = section.dataset.section;
        const fieldName = field.dataset.field;

        // 주민번호 자동입력 처리
        if (fieldName === 'resident_number' && sectionId === 'personal') {
            this._handleRRNAutofill(section, e.target.value);
        }

        // dirty 필드 추가
        const dirtySet = this.dirtyFields.get(sectionId);
        if (dirtySet) {
            const original = this.originalData.get(sectionId)?.[fieldName];
            const current = this._getFieldValue(field);

            if (original !== current) {
                dirtySet.add(fieldName);
                field.classList.add('inline-edit__input--dirty');
            } else {
                dirtySet.delete(fieldName);
                field.classList.remove('inline-edit__input--dirty');
            }
        }
    }

    /**
     * 주민번호 자동입력 처리
     * 생년월일, 나이, 성별 자동 설정
     */
    _handleRRNAutofill(section, rrn) {
        // 하이픈 제거
        const cleaned = rrn.replace(/-/g, '');

        // 13자리 미만이면 무시
        if (cleaned.length < 13) return;

        // 형식 검증
        if (!/^\d{13}$/.test(cleaned)) return;

        // 생년월일 추출
        const yy = cleaned.substring(0, 2);
        const mm = cleaned.substring(2, 4);
        const dd = cleaned.substring(4, 6);
        const genderCode = parseInt(cleaned[6], 10);

        // 세기 판단: 1,2,5,6 -> 1900년대, 3,4,7,8 -> 2000년대
        let century;
        if ([1, 2, 5, 6].includes(genderCode)) {
            century = '19';
        } else if ([3, 4, 7, 8].includes(genderCode)) {
            century = '20';
        } else {
            return;
        }

        const year = century + yy;
        const birthDate = `${year}-${mm}-${dd}`;

        // 날짜 유효성 검증
        const date = new Date(parseInt(year), parseInt(mm) - 1, parseInt(dd));
        if (date.getFullYear() !== parseInt(year) ||
            date.getMonth() !== parseInt(mm) - 1 ||
            date.getDate() !== parseInt(dd)) {
            return;
        }

        // 만 나이 계산
        const today = new Date();
        let age = today.getFullYear() - parseInt(year);
        const monthDiff = today.getMonth() - (parseInt(mm) - 1);
        const dayDiff = today.getDate() - parseInt(dd);
        if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
            age--;
        }

        // 성별 추출 (1,3,5,7 -> 남, 2,4,6,8 -> 여)
        const gender = [1, 3, 5, 7].includes(genderCode) ? '남' : '여';

        // 필드 업데이트
        this._setInlineFieldValue(section, 'birth_date', birthDate);
        this._setInlineFieldValue(section, 'age', age + '세', true); // readonly
        this._setInlineFieldValue(section, 'gender', gender);

        // dirty 표시 추가
        const dirtySet = this.dirtyFields.get('personal');
        if (dirtySet) {
            dirtySet.add('birth_date');
            dirtySet.add('gender');
        }
    }

    /**
     * 인라인 필드 값 설정
     */
    _setInlineFieldValue(section, fieldName, value, isReadonly = false) {
        const field = section.querySelector(`[data-field="${fieldName}"]`);
        if (!field) return;

        // 읽기전용 필드는 view 텍스트만 업데이트
        if (isReadonly) {
            const viewEl = field.querySelector('.inline-edit__view');
            if (viewEl) {
                viewEl.textContent = value || '-';
            }
            return;
        }

        // input 필드 업데이트
        const input = field.querySelector('input, select');
        if (input) {
            input.value = value || '';
            input.classList.add('inline-edit__input--dirty');
        }

        // view 텍스트 업데이트
        const viewEl = field.querySelector('.inline-edit__view');
        if (viewEl) {
            // select의 경우 라벨 표시
            if (input && input.tagName === 'SELECT') {
                const selectedOption = input.options[input.selectedIndex];
                viewEl.textContent = selectedOption?.text || value || '-';
            } else {
                viewEl.textContent = value || '-';
            }
        }
    }

    /**
     * 실제 거주지가 비어있으면 주민등록상 주소로 자동 복사
     * 편집 모드 진입 시 호출됨
     */
    _autoCopyAddressIfEmpty(sectionId) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        // 실제 거주지 필드 확인
        const actualAddressField = section.querySelector('[data-field="actual_address"]');
        if (!actualAddressField) return;

        const actualAddressInput = actualAddressField.querySelector('input[name="actual_address"]');
        const actualDetailInput = actualAddressField.querySelector('input[name="actual_address_detail"]');

        // 실제 거주지가 이미 입력되어 있으면 복사하지 않음
        if (actualAddressInput?.value?.trim()) {
            return;
        }

        // 주민등록상 주소 값 가져오기
        const addressField = section.querySelector('[data-field="address"]');
        if (!addressField) return;

        const address = addressField.querySelector('input[name="address"]')?.value || '';
        const addressDetail = addressField.querySelector('input[name="address_detail"]')?.value || '';

        // 주민등록상 주소가 없으면 복사하지 않음
        if (!address.trim()) {
            return;
        }

        // 실제 거주지에 주민등록상 주소 복사
        if (actualAddressInput) {
            actualAddressInput.value = address;
        }
        if (actualDetailInput) {
            actualDetailInput.value = addressDetail;
        }

        console.log('실제 거주지가 비어있어 주민등록상 주소로 자동 복사됨');
    }

    /**
     * 키보드 핸들러 (Escape: 취소, Enter: 저장)
     */
    _handleKeydown(e) {
        const section = e.target.closest('[data-section]');
        if (!section) return;

        const sectionId = section.dataset.section;
        const state = this.getState(sectionId);

        if (state !== EditState.EDITING) return;

        if (e.key === 'Escape') {
            e.preventDefault();
            this.cancelEdit(sectionId);
        } else if (e.key === 'Enter' && !e.shiftKey && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            this.saveSection(sectionId);
        }
    }

    // ========================================
    // 내부 헬퍼 메서드
    // ========================================

    /**
     * 섹션 설정 조회
     */
    _getSectionConfig(sectionId) {
        return SECTION_CONFIG[sectionId] || TABLE_CONFIG[sectionId] || {
            name: sectionId,
            apiPath: sectionId,
            type: 'unknown'
        };
    }

    /**
     * 섹션 CSS 클래스 업데이트
     */
    _updateSectionClasses(sectionId, state) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        // 모든 상태 클래스 제거
        section.classList.remove(
            'info-section--editing',
            'info-section--saving',
            'info-section--error'
        );

        // 새 상태 클래스 추가
        switch (state) {
            case EditState.EDITING:
                section.classList.add('info-section--editing');
                break;
            case EditState.SAVING:
                section.classList.add('info-section--saving');
                break;
            case EditState.ERROR:
                section.classList.add('info-section--error');
                break;
        }
    }

    /**
     * 원본 데이터 저장
     */
    _saveOriginalData(sectionId) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        const data = {};
        const fields = section.querySelectorAll('[data-field]');

        fields.forEach(field => {
            const fieldName = field.dataset.field;
            data[fieldName] = this._getFieldValue(field);
        });

        this.originalData.set(sectionId, data);
    }

    /**
     * 원본 데이터로 복원
     */
    _restoreOriginalData(sectionId) {
        const original = this.originalData.get(sectionId);
        if (!original) return;

        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        Object.entries(original).forEach(([fieldName, value]) => {
            const field = section.querySelector(`[data-field="${fieldName}"]`);
            if (field) {
                this._setFieldValue(field, value);
            }
        });
    }

    /**
     * 원본 데이터 삭제
     */
    _clearOriginalData(sectionId) {
        this.originalData.delete(sectionId);
    }

    /**
     * 폼 데이터 수집
     */
    _collectFormData(sectionId) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return {};

        const data = {};
        const fields = section.querySelectorAll('[data-field]');

        fields.forEach(field => {
            const fieldName = field.dataset.field;
            const value = this._getFieldValue(field);

            // readonly 필드는 제외
            if (!field.hasAttribute('readonly') && !field.disabled) {
                data[fieldName] = value;
            }
        });

        return data;
    }

    /**
     * 필드 값 조회
     * hidden input이 있으면 그 값을 우선 사용 (organization_id 등 복합 필드 대응)
     */
    _getFieldValue(field) {
        // hidden input 우선 확인 (organization_id 등)
        const hiddenInput = field.querySelector('input[type="hidden"]');
        if (hiddenInput) {
            return hiddenInput.value || '';
        }

        const input = field.querySelector('input, select, textarea') || field;

        if (input.type === 'checkbox') {
            return input.checked;
        }

        return input.value || '';
    }

    /**
     * 필드 값 설정
     */
    _setFieldValue(field, value) {
        const input = field.querySelector('input, select, textarea') || field;

        if (input.type === 'checkbox') {
            input.checked = Boolean(value);
        } else {
            input.value = value || '';
        }
    }

    /**
     * 첫 번째 입력 필드에 포커스
     */
    _focusFirstInput(sectionId) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        const firstInput = section.querySelector(
            'input:not([readonly]):not([disabled]), ' +
            'select:not([disabled]), ' +
            'textarea:not([readonly]):not([disabled])'
        );

        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    /**
     * 필드별 에러 표시
     */
    _showFieldErrors(sectionId, errors) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        Object.entries(errors).forEach(([fieldName, message]) => {
            const field = section.querySelector(`[data-field="${fieldName}"]`);
            if (field) {
                field.classList.add('inline-edit__input--invalid');

                // 에러 메시지 표시 (기존 에러 제거 후)
                let errorEl = field.parentElement.querySelector('.inline-edit__error');
                if (!errorEl) {
                    errorEl = document.createElement('span');
                    errorEl.className = 'inline-edit__error';
                    field.parentElement.appendChild(errorEl);
                }
                errorEl.textContent = message;
            }
        });
    }

    /**
     * 필드 에러 제거
     */
    _clearFieldErrors(sectionId) {
        const section = document.querySelector(`[data-section="${sectionId}"]`);
        if (!section) return;

        // invalid 클래스 제거
        section.querySelectorAll('.inline-edit__input--invalid').forEach(el => {
            el.classList.remove('inline-edit__input--invalid');
        });

        // dirty 클래스 제거
        section.querySelectorAll('.inline-edit__input--dirty').forEach(el => {
            el.classList.remove('inline-edit__input--dirty');
        });

        // 에러 메시지 제거
        section.querySelectorAll('.inline-edit__error').forEach(el => {
            el.remove();
        });
    }
}

// ========================================
// 팩토리 함수 (싱글톤 패턴)
// ========================================

let _instance = null;

/**
 * InlineEditManager 싱글톤 인스턴스 가져오기
 * @param {Object} options - 설정 옵션
 * @returns {InlineEditManager}
 */
export function getInlineEditManager(options = {}) {
    if (!_instance) {
        _instance = new InlineEditManager(options);
    } else if (options.employeeId && options.employeeId !== _instance.employeeId) {
        // employeeId가 변경되면 새 인스턴스 생성
        _instance.destroy();
        _instance = new InlineEditManager(options);
    }
    return _instance;
}

/**
 * InlineEditManager 인스턴스 초기화 (페이지 로드 시)
 * @param {number|null} employeeId - 직원 ID (CREATE 모드에서는 null)
 * @param {Object} options - 추가 옵션
 * @returns {InlineEditManager}
 */
export function initInlineEdit(employeeId, options = {}) {
    const manager = getInlineEditManager({ employeeId, ...options });
    manager.init();
    return manager;
}

/**
 * CREATE 모드로 InlineEditManager 초기화
 * @param {Object} options - 추가 옵션
 * @returns {InlineEditManager}
 */
export function initInlineEditCreate(options = {}) {
    const manager = getInlineEditManager({
        isCreateMode: true,
        ...options
    });
    manager.init();
    return manager;
}

export default InlineEditManager;
