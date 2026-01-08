/**
 * AI Test Index Page JavaScript
 * AI 문서 분석 테스트 페이지
 *
 * Used by:
 * - ai_test/index.html
 */

document.addEventListener('DOMContentLoaded', function() {
    initFilePreview();
    initAnalyzeForm();
});

/**
 * Initialize file preview functionality
 */
function initFilePreview() {
    const fileInput = document.getElementById('fileInput');
    const sampleSelect = document.getElementById('sampleSelect');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (sampleSelect) sampleSelect.value = '';
                showFilePreview(file.name);
            }
        });
    }

    if (sampleSelect) {
        sampleSelect.addEventListener('change', function(e) {
            if (e.target.value) {
                if (fileInput) fileInput.value = '';
                showFilePreview(e.target.value);
            } else {
                hideFilePreview();
            }
        });
    }
}

/**
 * Show file preview
 * @param {string} filename - File name to display
 */
function showFilePreview(filename) {
    const previewEl = document.getElementById('filePreview');
    const nameEl = document.getElementById('selectedFileName');
    if (previewEl && nameEl) {
        nameEl.textContent = filename;
        previewEl.classList.remove('hidden');
    }
}

/**
 * Hide file preview
 */
function hideFilePreview() {
    const previewEl = document.getElementById('filePreview');
    if (previewEl) {
        previewEl.classList.add('hidden');
    }
}

/**
 * Initialize analyze form submission
 */
function initAnalyzeForm() {
    const form = document.getElementById('analyzeForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const btn = document.getElementById('analyzeBtn');
        const resultContainer = document.getElementById('resultContainer');

        const fileInput = document.getElementById('fileInput');
        const sampleSelect = document.getElementById('sampleSelect');
        const file = fileInput?.files[0];
        const sampleFile = sampleSelect?.value;

        if (!file && !sampleFile) {
            alert('파일을 선택해주세요');
            return;
        }

        // Loading state
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 분석 중...';
        resultContainer.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>AI가 문서를 분석하고 있습니다...</p>
            </div>
        `;

        try {
            // CSRF 토큰 가져오기
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

            const response = await fetch('/ai-test/analyze', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok && !result.error) {
                displayResult(result);
            } else {
                displayError(result.error || '분석 중 오류가 발생했습니다');
            }
        } catch (error) {
            displayError('서버 연결 오류: ' + error.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-search"></i> 분석 시작';
        }
    });
}

/**
 * Display analysis result
 * @param {Object} result - Analysis result object
 */
function displayResult(result) {
    const container = document.getElementById('resultContainer');
    const confidence = result.confidence || 0;
    const confidenceClass = confidence > 0.8 ? 'high' : confidence > 0.6 ? 'medium' : 'low';

    container.innerHTML = `
        <div class="result-meta">
            <div class="meta-item">
                <div class="label">문서 유형</div>
                <div class="value">${getDocumentTypeName(result.document_type)}</div>
            </div>
            <div class="meta-item">
                <div class="label">신뢰도</div>
                <div class="value">
                    <span class="confidence-badge confidence-${confidenceClass}">
                        ${(confidence * 100).toFixed(1)}%
                    </span>
                </div>
            </div>
            <div class="meta-item">
                <div class="label">처리 시간</div>
                <div class="value">${result.processing_time?.toFixed(2) || '-'}초</div>
            </div>
        </div>
        <div class="provider-wrapper">
            <span class="provider-tag">${result.provider || 'unknown'}</span>
        </div>
        <h4 class="raw-json-title">Raw JSON 응답:</h4>
        <pre class="result-json">${JSON.stringify(result.extracted_fields || result, null, 2)}</pre>
    `;

    // Display fields table
    if (result.extracted_fields) {
        displayFields(result.extracted_fields, result.field_confidences);
    }
}

/**
 * Display error message
 * @param {string} message - Error message
 */
function displayError(message) {
    const container = document.getElementById('resultContainer');
    container.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <div>
                <strong>오류 발생</strong>
                <p>${message}</p>
            </div>
        </div>
    `;
    const fieldsCard = document.getElementById('fieldsCard');
    if (fieldsCard) fieldsCard.classList.add('hidden');
}

/**
 * Display extracted fields in table format
 * @param {Object} fields - Extracted fields object
 * @param {Object} confidences - Field confidence values
 */
function displayFields(fields, confidences) {
    const card = document.getElementById('fieldsCard');
    const container = document.getElementById('extractedFields');
    if (!card || !container) return;

    card.classList.remove('hidden');

    const flatFields = flattenObject(fields);
    let html = `
        <table class="fields-table">
            <thead>
                <tr>
                    <th>필드명</th>
                    <th>추출된 값</th>
                    <th>신뢰도</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const [key, value] of Object.entries(flatFields)) {
        if (value === null || value === undefined || value === '') continue;

        const conf = confidences?.[key] || 0.5;
        const confClass = conf > 0.8 ? 'high' : conf > 0.6 ? 'medium' : 'low';

        html += `
            <tr>
                <td><strong>${key}</strong></td>
                <td>${formatValue(value)}</td>
                <td>
                    <span class="confidence-badge confidence-${confClass}">
                        ${(conf * 100).toFixed(0)}%
                    </span>
                </td>
            </tr>
        `;
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Flatten nested object
 * @param {Object} obj - Object to flatten
 * @param {string} prefix - Key prefix
 * @returns {Object} Flattened object
 */
function flattenObject(obj, prefix = '') {
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
        const newKey = prefix ? `${prefix}.${key}` : key;
        if (value && typeof value === 'object' && !Array.isArray(value)) {
            Object.assign(result, flattenObject(value, newKey));
        } else {
            result[newKey] = value;
        }
    }
    return result;
}

/**
 * Format value for display
 * @param {*} value - Value to format
 * @returns {string} Formatted string
 */
function formatValue(value) {
    if (Array.isArray(value)) {
        return value.length + '개 항목';
    }
    if (typeof value === 'boolean') {
        return value ? '예' : '아니오';
    }
    return String(value);
}

/**
 * Get document type display name
 * @param {string} type - Document type key
 * @returns {string} Display name
 */
function getDocumentTypeName(type) {
    const names = {
        'auto_detect': '자동 감지',
        'resume': '이력서',
        'career_certificate': '경력증명서',
        'graduation_certificate': '졸업증명서',
        'resident_registration': '주민등록등본/초본',
        'bank_account': '통장사본',
        'photo': '증명사진'
    };
    return names[type] || type;
}

// Expose functions for non-module environments
window.showFilePreview = showFilePreview;
window.hideFilePreview = hideFilePreview;
window.displayResult = displayResult;
window.displayError = displayError;
window.displayFields = displayFields;
window.getDocumentTypeName = getDocumentTypeName;
