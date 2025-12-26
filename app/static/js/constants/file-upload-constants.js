/**
 * 파일 업로드 관련 상수 (SSOT)
 * 모든 파일 업로드 기능에서 이 상수들을 사용해야 합니다.
 */

/**
 * 최대 파일 크기 (10MB)
 * @type {number}
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024;

/**
 * 최대 파일 크기 (MB 단위)
 * @type {number}
 */
export const MAX_FILE_SIZE_MB = 10;

/**
 * 허용되는 이미지 확장자
 * @type {string[]}
 */
export const ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp'];

/**
 * 허용되는 문서 확장자
 * @type {string[]}
 */
export const ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'];

/**
 * 허용되는 모든 파일 확장자
 * @type {string[]}
 */
export const ALLOWED_FILE_EXTENSIONS = [
    ...ALLOWED_IMAGE_EXTENSIONS,
    ...ALLOWED_DOCUMENT_EXTENSIONS
];

/**
 * 확장자 검사 함수
 * @param {string} filename - 파일명
 * @param {string[]} [allowedExtensions] - 허용할 확장자 배열 (기본: 모든 허용 확장자)
 * @returns {boolean}
 */
export function isAllowedExtension(filename, allowedExtensions = ALLOWED_FILE_EXTENSIONS) {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext ? allowedExtensions.includes(ext) : false;
}

/**
 * 파일 크기 검사 함수
 * @param {number} size - 파일 크기 (bytes)
 * @param {number} [maxSize] - 최대 크기 (bytes, 기본: MAX_FILE_SIZE)
 * @returns {boolean}
 */
export function isAllowedFileSize(size, maxSize = MAX_FILE_SIZE) {
    return size <= maxSize;
}

/**
 * 파일 크기를 읽기 쉬운 형식으로 변환
 * @param {number} bytes - 바이트 단위 크기
 * @returns {string}
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 파일 업로드 에러 메시지
 * @type {Object}
 */
export const FILE_UPLOAD_MESSAGES = {
    SIZE_EXCEEDED: `파일 크기는 ${MAX_FILE_SIZE_MB}MB를 초과할 수 없습니다`,
    INVALID_TYPE: '허용되지 않는 파일 형식입니다',
    UPLOAD_SUCCESS: '파일이 업로드되었습니다',
    UPLOAD_FAILED: '파일 업로드에 실패했습니다',
    NO_FILE_SELECTED: '파일을 선택해주세요'
};
