/**
 * RRN (Resident Registration Number) 자동입력 모듈
 * Phase 28: 주민등록번호 입력 시 생년월일, 나이, 성별 자동 입력
 */
(function() {
    'use strict';

    /**
     * RRN 형식 검증 (13자리 숫자 + 하이픈)
     * @param {string} rrn - 주민등록번호
     * @returns {boolean}
     */
    function isValidFormat(rrn) {
        if (!rrn) return false;
        // 하이픈 제거
        const cleaned = rrn.replace(/-/g, '');
        return /^\d{13}$/.test(cleaned);
    }

    /**
     * 체크섬 검증 (Luhn 변형 알고리즘)
     * @param {string} rrn - 주민등록번호 (하이픈 제거된 13자리)
     * @returns {boolean}
     */
    function validateChecksum(rrn) {
        const cleaned = rrn.replace(/-/g, '');
        if (cleaned.length !== 13) return false;

        const weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5];
        let sum = 0;

        for (let i = 0; i < 12; i++) {
            sum += parseInt(cleaned[i], 10) * weights[i];
        }

        const checkDigit = (11 - (sum % 11)) % 10;
        return checkDigit === parseInt(cleaned[12], 10);
    }

    /**
     * 생년월일 추출
     * @param {string} rrn - 주민등록번호
     * @returns {string|null} YYYY-MM-DD 형식
     */
    function extractBirthDate(rrn) {
        const cleaned = rrn.replace(/-/g, '');
        if (cleaned.length < 7) return null;

        const yy = cleaned.substring(0, 2);
        const mm = cleaned.substring(2, 4);
        const dd = cleaned.substring(4, 6);
        const genderCode = parseInt(cleaned[6], 10);

        // 세기 판단: 1,2,5,6 -> 1900년대, 3,4,7,8 -> 2000년대
        let century;
        if (genderCode >= 1 && genderCode <= 2) {
            century = '19';
        } else if (genderCode >= 3 && genderCode <= 4) {
            century = '20';
        } else if (genderCode >= 5 && genderCode <= 6) {
            century = '19';  // 외국인 1900년대
        } else if (genderCode >= 7 && genderCode <= 8) {
            century = '20';  // 외국인 2000년대
        } else {
            return null;
        }

        const year = century + yy;

        // 날짜 유효성 검증
        const date = new Date(parseInt(year), parseInt(mm) - 1, parseInt(dd));
        if (date.getFullYear() !== parseInt(year) ||
            date.getMonth() !== parseInt(mm) - 1 ||
            date.getDate() !== parseInt(dd)) {
            return null;
        }

        return `${year}-${mm}-${dd}`;
    }

    /**
     * 만 나이 계산
     * @param {string} birthDate - YYYY-MM-DD 형식
     * @returns {number|null}
     */
    function calculateAge(birthDate) {
        if (!birthDate) return null;

        const birth = new Date(birthDate);
        const today = new Date();

        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        const dayDiff = today.getDate() - birth.getDate();

        // 생일이 지나지 않았으면 1살 감소
        if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
            age--;
        }

        return age;
    }

    /**
     * 성별 추출
     * @param {string} rrn - 주민등록번호
     * @returns {string|null} '남' 또는 '여'
     */
    function extractGender(rrn) {
        const cleaned = rrn.replace(/-/g, '');
        if (cleaned.length < 7) return null;

        const genderCode = parseInt(cleaned[6], 10);

        // 1,3,5,7 -> 남성, 2,4,6,8 -> 여성
        if ([1, 3, 5, 7].includes(genderCode)) {
            return '남';
        } else if ([2, 4, 6, 8].includes(genderCode)) {
            return '여';
        }
        return null;
    }

    /**
     * 자동입력 필드 업데이트
     * @param {string} rrn - 주민등록번호
     */
    function updateAutoFields(rrn) {
        const birthDateInput = document.getElementById('birth_date');
        const ageInput = document.getElementById('age');
        const genderSelect = document.getElementById('gender');
        const rrnInput = document.getElementById('resident_number');

        // 형식 검증
        if (!isValidFormat(rrn)) {
            clearValidationState(rrnInput);
            return;
        }

        // 체크섬 검증
        if (!validateChecksum(rrn)) {
            setInvalidState(rrnInput, '주민등록번호가 유효하지 않습니다');
            return;
        }

        // 생년월일 추출 및 설정
        const birthDate = extractBirthDate(rrn);
        if (birthDate && birthDateInput) {
            birthDateInput.value = birthDate;
        }

        // 나이 계산 및 설정
        const age = calculateAge(birthDate);
        if (age !== null && ageInput) {
            ageInput.value = age;
        }

        // 성별 설정
        const gender = extractGender(rrn);
        if (gender && genderSelect) {
            genderSelect.value = gender;
        }

        // 유효 상태 표시
        setValidState(rrnInput);
    }

    /**
     * 유효하지 않은 상태 표시
     */
    function setInvalidState(input, message) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');

        // 기존 에러 메시지 제거
        const existingError = input.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // 에러 메시지 추가
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        input.parentElement.appendChild(errorDiv);
    }

    /**
     * 유효 상태 표시
     */
    function setValidState(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');

        const existingError = input.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    /**
     * 검증 상태 초기화
     */
    function clearValidationState(input) {
        input.classList.remove('is-invalid', 'is-valid');

        const existingError = input.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    /**
     * RRN 자동입력 초기화
     */
    function initRRNAutofill() {
        const rrnInput = document.getElementById('resident_number');
        if (!rrnInput) return;

        // readonly가 아닌 경우에만 이벤트 연결
        if (!rrnInput.hasAttribute('readonly') && !rrnInput.disabled) {
            // 입력 이벤트
            rrnInput.addEventListener('input', function(e) {
                const value = e.target.value;

                // 하이픈 자동 추가 (6자리 입력 후)
                if (value.length === 6 && !value.includes('-')) {
                    e.target.value = value + '-';
                }

                // 13자리 완성 시 자동입력
                const cleaned = value.replace(/-/g, '');
                if (cleaned.length === 13) {
                    updateAutoFields(value);
                } else {
                    clearValidationState(rrnInput);
                }
            });

            // blur 이벤트 (포커스 해제 시 최종 검증)
            rrnInput.addEventListener('blur', function(e) {
                const value = e.target.value;
                const cleaned = value.replace(/-/g, '');

                if (cleaned.length === 13) {
                    updateAutoFields(value);
                } else if (cleaned.length > 0) {
                    setInvalidState(rrnInput, '주민등록번호는 13자리입니다');
                }
            });
        }

        // 국적 기본값 설정 (신규 등록 시)
        const nationalitySelect = document.getElementById('nationality');
        if (nationalitySelect && !nationalitySelect.value) {
            // 대한민국 옵션 찾아서 선택
            for (let i = 0; i < nationalitySelect.options.length; i++) {
                if (nationalitySelect.options[i].value === '대한민국') {
                    nationalitySelect.selectedIndex = i;
                    break;
                }
            }
        }
    }

    // DOM 로드 완료 시 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRRNAutofill);
    } else {
        initRRNAutofill();
    }

    // 전역 노출 (선택적)
    window.RRNAutofill = {
        init: initRRNAutofill,
        validate: validateChecksum,
        extractBirthDate: extractBirthDate,
        calculateAge: calculateAge,
        extractGender: extractGender
    };

})();
