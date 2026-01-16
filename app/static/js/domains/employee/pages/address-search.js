/**
 * Address Search Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 다음 주소 API 연동
 * - 주민등록상 주소 검색
 * - 실제 거주 주소 검색
 */

/**
 * 주소 검색 초기화 (다음 주소 API)
 * 주민등록상 주소와 실제 거주 주소 모두 초기화
 */
export function initAddressSearch() {
    // 주민등록상 주소 검색 초기화
    initRegisteredAddressSearch();

    // 실제 거주 주소 검색 초기화
    initActualAddressSearch();
}

/**
 * 주민등록상 주소 검색 초기화
 */
function initRegisteredAddressSearch() {
    const searchBtn = document.getElementById('searchAddressBtn');
    const addressInput = document.getElementById('address');
    const postalCodeInput = document.getElementById('postal_code');
    const detailedAddressInput = document.getElementById('detailed_address');

    if (!searchBtn || !addressInput) return;

    // 검색 버튼 클릭
    searchBtn.addEventListener('click', () => openAddressSearch(addressInput, detailedAddressInput, postalCodeInput));

    // 주소 입력란 클릭 시에도 검색 팝업
    addressInput.addEventListener('click', () => {
        searchBtn.click();
    });
}

/**
 * 실제 거주 주소 검색 초기화
 */
function initActualAddressSearch() {
    const searchBtn = document.getElementById('searchActualAddressBtn');
    const addressInput = document.getElementById('actual_address');
    const postalCodeInput = document.getElementById('actual_postal_code');
    const detailedAddressInput = document.getElementById('actual_detailed_address');

    if (!searchBtn || !addressInput) return;

    // 검색 버튼 클릭
    searchBtn.addEventListener('click', () => openAddressSearch(addressInput, detailedAddressInput, postalCodeInput));

    // 주소 입력란 클릭 시에도 검색 팝업
    addressInput.addEventListener('click', () => {
        searchBtn.click();
    });
}

/**
 * 다음 주소 검색 팝업 열기
 * @param {HTMLElement} addressInput - 주소 입력 필드
 * @param {HTMLElement} detailedAddressInput - 상세주소 입력 필드
 * @param {HTMLElement} postalCodeInput - 우편번호 입력 필드 (선택적)
 */
function openAddressSearch(addressInput, detailedAddressInput, postalCodeInput = null) {
    // daum.Postcode는 전역으로 로드됨 (base.html)
    if (typeof daum === 'undefined' || !daum.Postcode) {
        alert('주소 검색 서비스를 불러오는 중입니다. 잠시 후 다시 시도해 주세요.');
        return;
    }

    new daum.Postcode({
        oncomplete: function(data) {
            // 도로명 주소 우선, 없으면 지번 주소
            const address = data.roadAddress || data.jibunAddress;
            addressInput.value = address;

            // 우편번호 입력
            if (postalCodeInput) {
                postalCodeInput.value = data.zonecode;
            }

            // 상세주소 입력란으로 포커스 이동
            if (detailedAddressInput) {
                detailedAddressInput.focus();
            }
        },
        onclose: function(state) {
            // 사용자가 닫기 버튼을 눌렀을 때
            if (state === 'FORCE_CLOSE') {
                // 아무 동작 없음
            }
        }
    }).open();
}

export { openAddressSearch };

export default {
    initAddressSearch,
    openAddressSearch
};
