/**
 * @deprecated 2026-01-09
 * 명함 컴포넌트는 BusinessCard 도메인으로 이동되었습니다.
 * 새로운 위치: js/domains/businesscard/components/BusinessCard.js
 *
 * 명함 업로드/삭제 컴포넌트 (레거시)
 * - 앞면/뒷면 이미지 업로드
 * - 드래그앤드롭 지원
 * - 미리보기 기능
 *
 * Migration:
 * - js/domains/businesscard/index.js를 import하여 사용
 * - import { businessCard, BusinessCard } from '../businesscard/index.js';
 */

// 업로드할 파일 임시 저장
let businessCardFiles = {
    front: null,
    back: null
};

/**
 * 명함 업로드 모달 열기
 */
function openBusinessCardModal() {
    const modal = document.getElementById('businessCardModal');
    if (modal) {
        modal.classList.add('active');
        resetUploadForm();
        initDropzones();
    }
}

/**
 * 명함 업로드 모달 닫기
 */
function closeBusinessCardModal() {
    const modal = document.getElementById('businessCardModal');
    if (modal) {
        modal.classList.remove('active');
        resetUploadForm();
    }
}

/**
 * 업로드 폼 초기화
 */
function resetUploadForm() {
    businessCardFiles = { front: null, back: null };

    // 파일 입력 초기화
    const frontInput = document.getElementById('cardFrontInput');
    const backInput = document.getElementById('cardBackInput');
    if (frontInput) frontInput.value = '';
    if (backInput) backInput.value = '';

    // 미리보기 초기화
    const previewFront = document.getElementById('previewFront');
    const previewBack = document.getElementById('previewBack');
    if (previewFront) {
        previewFront.style.display = 'none';
        previewFront.src = '';
    }
    if (previewBack) {
        previewBack.style.display = 'none';
        previewBack.src = '';
    }

    // 드롭존 상태 초기화
    document.querySelectorAll('.upload-dropzone').forEach(zone => {
        zone.classList.remove('has-file', 'dragover');
    });
}

/**
 * 드롭존 초기화 (드래그앤드롭 이벤트)
 */
function initDropzones() {
    const dropzones = document.querySelectorAll('.upload-dropzone');

    dropzones.forEach(zone => {
        const side = zone.dataset.side;

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {
                handleFile(files[0], side);
            }
        });
    });
}

/**
 * 파일 선택 핸들러
 */
function handleFileSelect(input, side) {
    const file = input.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file, side);
    }
}

/**
 * 파일 처리 (미리보기 생성)
 */
function handleFile(file, side) {
    businessCardFiles[side] = file;

    const previewId = side === 'front' ? 'previewFront' : 'previewBack';
    const dropzoneId = side === 'front' ? 'dropzoneFront' : 'dropzoneBack';

    const preview = document.getElementById(previewId);
    const dropzone = document.getElementById(dropzoneId);

    if (preview && dropzone) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
            dropzone.classList.add('has-file');
        };
        reader.readAsDataURL(file);
    }
}

/**
 * 명함 이미지 업로드
 */
async function uploadBusinessCards() {
    // profile-header v3.3 또는 레거시 employee-header에서 employeeId 찾기
    const container = document.querySelector(
        '.profile-header__column--card[data-employee-id], ' +  // v3.3 신규
        '.employee-header-card[data-employee-id], ' +          // 레거시 (하위 호환)
        '.business-card-container[data-employee-id]'           // 레거시 (하위 호환)
    );
    const employeeId = container ? container.dataset.employeeId : null;

    if (!employeeId) {
        showToast('직원 정보를 찾을 수 없습니다.', 'error');
        return;
    }

    if (!businessCardFiles.front && !businessCardFiles.back) {
        showToast('업로드할 이미지를 선택해주세요.', 'warning');
        return;
    }

    try {
        const uploadPromises = [];

        // 앞면 업로드
        if (businessCardFiles.front) {
            uploadPromises.push(uploadSingleCard(employeeId, 'front', businessCardFiles.front));
        }

        // 뒷면 업로드
        if (businessCardFiles.back) {
            uploadPromises.push(uploadSingleCard(employeeId, 'back', businessCardFiles.back));
        }

        await Promise.all(uploadPromises);

        showToast('명함 이미지가 업로드되었습니다.', 'success');
        closeBusinessCardModal();

        // 페이지 새로고침으로 변경사항 반영
        setTimeout(() => {
            location.reload();
        }, 500);

    } catch (error) {
        console.error('명함 업로드 오류:', error);
        showToast('명함 업로드 중 오류가 발생했습니다.', 'error');
    }
}

/**
 * 단일 명함 이미지 업로드
 */
async function uploadSingleCard(employeeId, side, file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('side', side);

    const response = await fetch(`/api/businesscard/employee/${employeeId}`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '업로드 실패');
    }

    return response.json();
}

/**
 * 모든 명함 이미지 삭제
 */
async function deleteAllBusinessCards() {
    if (!confirm('명함 이미지를 삭제하시겠습니까?')) {
        return;
    }

    // profile-header v3.3 또는 레거시 employee-header에서 employeeId 찾기
    const container = document.querySelector(
        '.profile-header__column--card[data-employee-id], ' +  // v3.3 신규
        '.employee-header-card[data-employee-id], ' +          // 레거시 (하위 호환)
        '.business-card-container[data-employee-id]'           // 레거시 (하위 호환)
    );
    const employeeId = container ? container.dataset.employeeId : null;

    if (!employeeId) {
        showToast('직원 정보를 찾을 수 없습니다.', 'error');
        return;
    }

    try {
        // 앞면, 뒷면 모두 삭제
        await Promise.all([
            deleteBusinessCard(employeeId, 'front'),
            deleteBusinessCard(employeeId, 'back')
        ]);

        showToast('명함 이미지가 삭제되었습니다.', 'success');

        // 페이지 새로고침으로 변경사항 반영
        setTimeout(() => {
            location.reload();
        }, 500);

    } catch (error) {
        console.error('명함 삭제 오류:', error);
        showToast('명함 삭제 중 오류가 발생했습니다.', 'error');
    }
}

/**
 * 단일 명함 이미지 삭제
 */
async function deleteBusinessCard(employeeId, side) {
    const response = await fetch(`/api/businesscard/employee/${employeeId}/${side}`, {
        method: 'DELETE'
    });

    // 404는 이미 삭제된 경우이므로 무시
    if (!response.ok && response.status !== 404) {
        const errorData = await response.json();
        throw new Error(errorData.error || '삭제 실패');
    }

    return response.json();
}

/**
 * 토스트 메시지 표시 (기존 showToast 함수 사용, 없으면 alert)
 */
function showToast(message, type) {
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
    } else if (typeof window.Toast !== 'undefined') {
        window.Toast.show(message, type);
    } else {
        alert(message);
    }
}

// 이벤트 위임 - data-action 기반 클릭 핸들러
document.addEventListener('click', (e) => {
    // 모달 외부 클릭 시 닫기
    const modal = document.getElementById('businessCardModal');
    if (modal && e.target === modal) {
        closeBusinessCardModal();
        return;
    }

    // data-action 기반 이벤트 처리
    const target = e.target.closest('[data-action]');
    if (!target) return;

    const action = target.dataset.action;

    switch (action) {
        case 'open-business-card-modal':
            openBusinessCardModal();
            break;
        case 'close-business-card-modal':
            closeBusinessCardModal();
            break;
        case 'upload-business-cards':
            uploadBusinessCards();
            break;
        case 'delete-all-business-cards':
            deleteAllBusinessCards();
            break;
    }
});

// 파일 선택 이벤트 위임
document.addEventListener('change', (e) => {
    const target = e.target.closest('[data-action="file-select"]');
    if (!target) return;

    const side = target.dataset.side;
    handleFileSelect(target, side);
});

// ESC 키로 모달 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeBusinessCardModal();
    }
});
